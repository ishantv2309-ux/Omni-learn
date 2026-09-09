import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Note
from backend.schemas import NoteResponse
import re
from backend.services.storage_service import StorageService
from backend.services.ocr_service import OCRService
from backend.services.gemini_service import GeminiService

router = APIRouter(prefix="/api/notes", tags=["Handwritten & Digital Notes"])

@router.get("", response_model=List[NoteResponse])
def get_notes(subject: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch all indexed notes, optionally filtered by subject."""
    q = db.query(Note)
    if subject:
        q = q.filter(Note.subject.ilike(f"%{subject}%"))
    return q.all()

@router.post("/upload", response_model=NoteResponse)
async def upload_note(
    title: str = Form(...),
    subject: str = Form(...),
    uploaded_by: Optional[str] = Form("Anonymous"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads a note file, runs OCR on it, and indexes the text in the database."""
    # Validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only PDF and image uploads (JPEG/PNG) are supported")
        
    file_type = "pdf" if ext == "pdf" else "image"
    
    # Save file
    filename = f"{int(os.path.getmtime(file.file.fileno()) if hasattr(file.file, 'fileno') else 0)}_{file.filename}"
    # Sanitizing filename
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    
    try:
        saved_path = StorageService.save_file(file, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    # Extract text using OCR (multimodal Gemini or mock depending on configuration)
    ocr_text = OCRService.extract_text(saved_path, filename)
    
    # Save to database
    db_note = Note(
        title=title,
        subject=subject,
        file_path=filename, # Store filename to query locally
        file_type=file_type,
        ocr_text=ocr_text,
        uploaded_by=uploaded_by
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.get("/search", response_model=List[NoteResponse])
def search_inside_notes(query: str = Query(...), db: Session = Depends(get_db)):
    """Performs full-text deep search inside notes by looking at indexed OCR text, titles, or subjects."""
    if not query.strip():
        return []
    return db.query(Note).filter(
        (Note.ocr_text.ilike(f"%{query}%")) |
        (Note.title.ilike(f"%{query}%")) |
        (Note.subject.ilike(f"%{query}%"))
    ).all()

@router.get("/file/{filename}")
def serve_note_file(filename: str, db: Session = Depends(get_db)):
    """Serves the actual file for display in the frontend viewer or download. Dynamically generates if missing."""
    try:
        file_path = StorageService.get_file_path(filename)
        lower_name = filename.lower()
        if not file_path.exists():
            db_note = db.query(Note).filter(Note.file_path == filename).first()
            if db_note and db_note.ocr_text:
                file_path.write_text(db_note.ocr_text, encoding="utf-8")
            elif lower_name.startswith("aktu_"):
                subject_title = filename.replace("_", " ").replace(".html", "").replace(".txt", "").replace("aktu", "").title().strip()
                html_content = f"""<!DOCTYPE html>
<html><head><title>{subject_title}</title></head>
<body>
    <h1>DR. A.P.J. ABDUL KALAM TECHNICAL UNIVERSITY</h1>
    <h2>{subject_title}</h2>
    <p>Official Academic Curricular Study Resource</p>
</body></html>"""
                file_path.write_text(html_content, encoding="utf-8")
            elif lower_name.startswith("temp_"):
                m = re.search(r'temp_(.+?)_\d+', lower_name)
                q_topic = m.group(1).replace("_", " ").title() if m else filename
                from backend.services.crawler_service import CrawlerService
                content = CrawlerService._synthesize_local_notes(q_topic, "Academic Curriculum")
                full_text = f"# Study Notes: {q_topic}\n\n{content}"
                file_path.write_text(full_text, encoding="utf-8")
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        # Set proper media type
        lower_filename = filename.lower()
        if lower_filename.endswith(".pdf"):
            media_type = "application/pdf"
        elif lower_filename.endswith(".html"):
            media_type = "text/html"
        elif lower_filename.endswith(".txt"):
            media_type = "text/plain"
        else:
            media_type = "image/jpeg"
            
        return FileResponse(path=file_path, media_type=media_type, filename=filename)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
