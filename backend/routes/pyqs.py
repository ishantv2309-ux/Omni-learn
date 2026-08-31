from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import PYQ
from backend.schemas import PYQResponse

router = APIRouter(prefix="/api/pyqs", tags=["PYQ Feed"])

@router.get("", response_model=List[PYQResponse])
def get_pyqs(
    subject: Optional[str] = None,
    board_univ: Optional[str] = None,
    exam: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve and filter Previous Year Questions (PYQs)."""
    db_query = db.query(PYQ)
    
    if subject:
        db_query = db_query.filter(PYQ.subject.ilike(f"%{subject}%"))
    if board_univ:
        db_query = db_query.filter(PYQ.board_university.ilike(f"%{board_univ}%"))
    if exam:
        db_query = db_query.filter(PYQ.exam_name.ilike(f"%{exam}%"))
    if query:
        # Search in question text or topic tags
        db_query = db_query.filter(
            (PYQ.question_text.ilike(f"%{query}%")) | 
            (PYQ.topic_tags.ilike(f"%{query}%"))
        )
        
    return db_query.order_by(PYQ.year.desc()).all()
