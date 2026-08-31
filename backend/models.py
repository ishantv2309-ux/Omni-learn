import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from backend.database import Base

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=False)
    difficulty_score = Column(Float, default=0.0)
    difficulty_reasons = Column(Text, nullable=True) # AI explanation of difficulty
    roadmap_json = Column(JSON, nullable=True) # AI step-by-step roadmap JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False) # 'pdf' or 'image'
    ocr_text = Column(Text, default="") # Extracted searchable text
    uploaded_by = Column(String, default="Anonymous")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class PYQ(Base):
    __tablename__ = "pyqs"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    year = Column(Integer, nullable=False)
    exam_name = Column(String, nullable=False) # e.g., JEE, CBSE, Mumbai Univ
    board_university = Column(String, nullable=False) # CBSE, ICSE, etc.
    subject = Column(String, nullable=False)
    difficulty = Column(String, default="Medium") # Easy, Medium, Hard
    topic_tags = Column(String, nullable=False) # Comma-separated search terms
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Bookmark(Base):
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String, nullable=False) # 'note' or 'topic'
    item_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SearchCache(Base):
    __tablename__ = "search_caches"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, unique=True, index=True, nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
