import asyncio
import datetime
import re
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import SearchCache, PYQ, Note
from backend.schemas import SearchResponse, YouTubeVideo, WebResource, PYQResponse, NoteResponse
from backend.services.gemini_service import GeminiService
from backend.services.youtube_service import YouTubeService
from backend.services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["Unified Search Engine"])

CACHE_EXPIRATION_HOURS = 24

def is_inappropriate_topic(topic: str) -> bool:
    """Returns True if the topic is classified as age-restricted or inappropriate."""
    prohibited_keywords = {
        "nudity", "naked", "sex", "porn", "xxx", "erotic", "adult content",
        "sensual", "orgasm", "masturbation", "intercourse", "clitoris", "penis", "vagina",
        "gore", "suicide", "murder", "weapons", "drugs", "cocaine", "heroin", "meth", "ecstasy",
        "violence", "hentai", "striptease", "playboy", "nsfw", "prostitution"
    }
    words = re.findall(r'\b\w+\b', topic.lower())
    for word in words:
        if word in prohibited_keywords:
            return True
    lowered_topic = topic.lower()
    for keyword in prohibited_keywords:
        if keyword in lowered_topic:
            return True
    return False

@router.get("", response_model=SearchResponse)
async def unified_search(query: str = Query(...), db: Session = Depends(get_db)):
    """Central entry point. Fetches AI details, videos, articles, local notes, and PYQs.
    Applies caching for high-speed queries.
    """
    clean_query = query.strip().lower()
    
    if is_inappropriate_topic(clean_query):
        return SearchResponse(
            query=query,
            summary="⚠️ Warning: This is not an academic topic to study. Age-restricted or inappropriate content is prohibited on OmniLearn.",
            detailed_breakdown="### Prohibited Content Warning\nYou searched for a topic that is classified as age-restricted or inappropriate for academic evaluation. Please search for educational subjects, coding languages, civil engineering materials, or other science topics.",
            domain="Prohibited Content",
            difficulty_score=0.0,
            difficulty_reasons="This query contains age-restricted or inappropriate keywords.",
            roadmap=[],
            youtube_videos=[],
            web_resources=[],
            pyqs=[],
            notes=[],
            careers=[],
            fun_fact="Keep your learning focused on academic coursework!"
        )
    
    # Clean up unbookmarked temporary notes to save database and disk space
    from backend.services.crawler_service import CrawlerService
    CrawlerService.cleanup_unbookmarked_temp_notes(db)
    
    # 1. Check Search Cache
    cache_record = db.query(SearchCache).filter(SearchCache.query == clean_query).first()
    if cache_record:
        # Check if cache is still fresh and contains rich detailed breakdown
        age = datetime.datetime.utcnow() - cache_record.created_at
        if age < datetime.timedelta(hours=CACHE_EXPIRATION_HOURS):
            cached_json = cache_record.result_json
            if isinstance(cached_json, dict) and cached_json.get("detailed_breakdown"):
                print(f"Serving cached search results for: '{clean_query}'")
                return cached_json

    print(f"Cache miss. Performing live aggregation for: '{clean_query}'")
    
    # 2. Run external API aggregations concurrently
    # Since gemini_service is synchronous, we run it in a threadpool to avoid blocking the event loop
    loop = asyncio.get_running_loop()
    
    async def get_gemini_data():
        return await loop.run_in_executor(None, GeminiService.generate_topic_details, query)

    # Gather external requests concurrently
    gemini_task = get_gemini_data()
    youtube_task = YouTubeService.search_videos(query)
    web_task = SearchService.fetch_web_resources(query)
    
    gemini_data, youtube_videos, web_resources = await asyncio.gather(
        gemini_task, youtube_task, web_task, return_exceptions=True
    )
    
    # Error fallbacks if any service fails
    if isinstance(gemini_data, Exception):
        print(f"Gemini aggregation error: {gemini_data}")
        gemini_data = GeminiService._fetch_live_academic_data(query)
        
    if isinstance(youtube_videos, Exception):
        print(f"YouTube aggregation error: {youtube_videos}")
        youtube_videos = YouTubeService._get_educational_fallback(query)
        
    if isinstance(web_resources, Exception):
        print(f"Web search aggregation error: {web_resources}")
        web_resources = SearchService._get_mock_resources(query)

    # 3. Query local database for matched PYQs and Notes with multi-token relevance
    academic_query = GeminiService.clean_search_query(query)
    search_terms = list(set([clean_query, academic_query.lower()] + [w.lower() for w in re.findall(r'\b\w{3,}\b', academic_query)]))
    
    # Query PYQs matching any key term
    pyq_query_filters = []
    for term in search_terms:
        pyq_query_filters.append(PYQ.topic_tags.ilike(f"%{term}%"))
        pyq_query_filters.append(PYQ.question_text.ilike(f"%{term}%"))
        pyq_query_filters.append(PYQ.subject.ilike(f"%{term}%"))
        
    matching_pyqs = db.query(PYQ).filter(or_(*pyq_query_filters)).distinct().all() if pyq_query_filters else []
    
    # Query Notes matching any key term
    note_query_filters = []
    for term in search_terms:
        note_query_filters.append(Note.ocr_text.ilike(f"%{term}%"))
        note_query_filters.append(Note.title.ilike(f"%{term}%"))
        note_query_filters.append(Note.subject.ilike(f"%{term}%"))
        
    matching_notes = db.query(Note).filter(or_(*note_query_filters)).distinct().all() if note_query_filters else []

    # If no crawled temporary note exists for this topic, trigger the CrawlerService
    has_temp_note = any(n.uploaded_by == "OmniLearn Crawler" for n in matching_notes)
    if not has_temp_note:
        from backend.services.crawler_service import CrawlerService
        temp_note = CrawlerService.generate_temporary_note(query, gemini_data.get("domain") or "Academic")
        if temp_note:
            matching_notes.append(temp_note)

    # Convert local db models to schema response shapes
    pyq_responses = [PYQResponse.model_validate(p) for p in matching_pyqs]
    note_responses = [NoteResponse.model_validate(n) for n in matching_notes]

    # 4. Formulate consolidated SearchResponse
    response_data = {
        "query": query,
        "summary": gemini_data.get("summary", ""),
        "detailed_breakdown": gemini_data.get("detailed_breakdown"),
        "domain": gemini_data.get("domain"),
        "difficulty_score": gemini_data.get("difficulty_score", 5.0),
        "difficulty_reasons": gemini_data.get("difficulty_reasons"),
        "roadmap": gemini_data.get("roadmap"),
        "youtube_videos": youtube_videos,
        "web_resources": web_resources,
        "pyqs": pyq_responses,
        "notes": note_responses,
        "careers": gemini_data.get("careers") or GeminiService.map_topic_to_careers(query),
        "fun_fact": gemini_data.get("fun_fact")
    }
    
    # Serialize to pydantic model for validation & formatting
    validated_response = SearchResponse(**response_data)
    
    # 5. Write to SearchCache (as dict/JSON representation)
    serialized_data = validated_response.model_dump(mode='json')
    if cache_record:
        cache_record.result_json = serialized_data
        cache_record.created_at = datetime.datetime.utcnow()
    else:
        new_cache = SearchCache(query=clean_query, result_json=serialized_data)
        db.add(new_cache)
        
    db.commit()
    
    return validated_response
