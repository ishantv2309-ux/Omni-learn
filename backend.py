"""
OmniLearn Backend Interface & Route Module
Exports FastAPI app and Gemini / Search services with double-escaped LaTeX preservation.
"""
from main import app, search_endpoint, SearchQueryPayload
from backend.services.gemini_service import GeminiService
from backend.routes.search import perform_unified_search
from backend.routes.ai_notes import (
    router as ai_notes_router,
    generate_topic_notes,
    generate_aktu_unit_notes,
    TopicNoteRequest,
    UnitNoteRequest,
    TOPIC_SYSTEM_PROMPT,
    AKTU_UNIT_PROMPT
)

def call_gemini_service(query: str):
    """Executes Gemini topic details generation with double-escaped LaTeX sanitization."""
    return GeminiService.generate_topic_details(query)

@app.post("/api/generate-notes")
async def generate_notes_route(req: TopicNoteRequest):
    """
    Topic-wise endpoint bound strictly to req.topic.
    Runs with temperature=0.1 to eliminate drift/hallucinations and discriminates CS/IT from Core Engineering.
    """
    return await generate_topic_notes(req)

@app.post("/api/generate-unit-notes")
async def generate_unit_notes_route(req: UnitNoteRequest):
    """
    AKTU Unit-wise endpoint bound strictly to req.unit_number and req.subject_code.
    Runs with temperature=0.1 and enforces Q&A structure.
    """
    return await generate_aktu_unit_notes(req)



__all__ = [
    "app",
    "search_endpoint",
    "GeminiService",
    "call_gemini_service",
    "perform_unified_search",
    "ai_notes_router",
    "generate_topic_notes",
    "generate_aktu_unit_notes",
    "TopicNoteRequest",
    "UnitNoteRequest",
    "TOPIC_SYSTEM_PROMPT",
    "AKTU_UNIT_PROMPT"
]
