from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.services.gemini_service import GeminiService

router = APIRouter(prefix="/api/gemini", tags=["Gemini AI Engine"])

class GeminiRequest(BaseModel):
    query: Optional[str] = None
    q: Optional[str] = None
    topic: Optional[str] = None

@router.post("")
async def gemini_generate_post(payload: GeminiRequest):
    """Server-side endpoint to query Gemini AI directly without client-side API keys."""
    target = payload.query or payload.q or payload.topic
    if not target or not target.strip():
        raise HTTPException(status_code=400, detail="Query parameter is required in JSON payload.")
    clean = GeminiService.clean_search_query(target.strip())
    return GeminiService.generate_topic_details(clean)

@router.get("")
async def gemini_generate_get(
    query: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    topic: Optional[str] = Query(None)
):
    """Server-side GET endpoint to query Gemini AI directly without client-side API keys."""
    target = query or q or topic
    if not target or not target.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'query' or 'q' is required.")
    clean = GeminiService.clean_search_query(target.strip())
    return GeminiService.generate_topic_details(clean)
