from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import Bookmark
from backend.schemas import BookmarkCreate, BookmarkResponse

router = APIRouter(prefix="/api/bookmarks", tags=["Bookmarks"])

@router.get("", response_model=List[BookmarkResponse])
def get_bookmarks(db: Session = Depends(get_db)):
    """Fetch all saved bookmarks."""
    return db.query(Bookmark).all()

@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
def create_bookmark(bookmark_in: BookmarkCreate, db: Session = Depends(get_db)):
    """Bookmark a topic or note. Prevents duplicates."""
    # Check if already bookmarked
    if bookmark_in.item_type == "topic":
        existing = db.query(Bookmark).filter(
            Bookmark.item_type == "topic",
            Bookmark.title == bookmark_in.title
        ).first()
    else:
        existing = db.query(Bookmark).filter(
            Bookmark.item_type == bookmark_in.item_type,
            Bookmark.item_id == bookmark_in.item_id
        ).first()
    
    if existing:
        return existing
        
    db_bookmark = Bookmark(
        item_type=bookmark_in.item_type,
        item_id=bookmark_in.item_id,
        title=bookmark_in.title
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """Remove a bookmarked item."""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    # If the bookmark was a topic, clean up all temporary crawler notes for this topic
    if bookmark.item_type == "topic":
        from backend.models import Note
        from backend.config import STORAGE_DIR
        import os
        
        temp_notes = db.query(Note).filter(
            Note.uploaded_by == "OmniLearn Crawler",
            Note.title.ilike(f"%{bookmark.title}%")
        ).all()
        
        for note in temp_notes:
            try:
                file_path = STORAGE_DIR / note.file_path
                if file_path.exists():
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing temp notes file on bookmark delete: {e}")
            db.delete(note)
            
    db.delete(bookmark)
    db.commit()
    return None
