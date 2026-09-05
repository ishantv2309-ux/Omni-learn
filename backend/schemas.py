from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- PYQ Schemas ---
class PYQBase(BaseModel):
    question_text: str
    year: int
    exam_name: str
    board_university: str
    subject: str
    difficulty: str
    topic_tags: str

class PYQResponse(PYQBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Note Schemas ---
class NoteBase(BaseModel):
    title: str
    subject: str
    file_path: str
    file_type: str
    uploaded_by: Optional[str] = "Anonymous"

class NoteResponse(NoteBase):
    id: int
    ocr_text: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Bookmark Schemas ---
class BookmarkCreate(BaseModel):
    item_type: str # 'note' or 'topic'
    item_id: int
    title: str

class BookmarkResponse(BaseModel):
    id: int
    item_type: str
    item_id: int
    title: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- External API result structures ---
class YouTubeVideo(BaseModel):
    title: str
    video_id: str
    thumbnail_url: str
    description: str
    view_count: Optional[str] = None
    channel_title: Optional[str] = None

class WebResource(BaseModel):
    title: str
    url: str
    snippet: str

class CareerRelevance(BaseModel):
    role: str
    roadmap_url: str
    importance: str

# --- Aggregated Search Schema ---
class SearchResponse(BaseModel):
    query: str
    title: Optional[str] = None
    category: Optional[str] = None
    summary: str
    detailed_breakdown: Optional[str] = None
    domain: Optional[str] = None
    difficulty_score: float
    difficulty_reasons: Optional[str] = None
    roadmap: Optional[List[Dict[str, Any]]] = None
    youtube_videos: List[YouTubeVideo]
    web_resources: List[WebResource]
    pyqs: Optional[List[PYQResponse]] = None
    notes: List[NoteResponse]
    careers: Optional[List[CareerRelevance]] = None
    fun_fact: Optional[str] = None
    did_you_know: Optional[str] = None
    exam_frequency: Optional[List[Dict[str, Any]]] = None

