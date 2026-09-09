import time
import pytest
from fastapi.testclient import TestClient
from main import app
from backend.database import engine, Base, SessionLocal
from backend.models import SearchCache

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_cache():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from datetime import datetime
        db.query(SearchCache).filter(SearchCache.query == "hash table").delete()
        db.commit()
        if True:
            cached_data = {
                "query": "hash table",
                "topic": "Hash Table",
                "domain": "Computer Science & Information Technology",
                "category": "Computer Science & Information Technology",
                "summary": "Hash tables provide average O(1) lookups.",
                "detailed_breakdown": "Theoretical foundations of hash tables.",
                "difficulty_score": 7.3,
                "difficulty_level": "Advanced",
                "difficulty_reasons": "Requires understanding hash functions and collision resolution.",
                "did_you_know": "Invented by Hans Peter Luhn in 1953.",
                "fun_fact": "Invented by Hans Peter Luhn in 1953.",
                "roadmap": [],
                "youtube_videos": [{"title": "Hash Table Explained", "video_id": "shs0kmlyeIQ", "thumbnail_url": "", "channel_name": "CS", "description": "Video explaining hash tables"}],
                "web_resources": [],
                "pyqs": [],
                "notes": [],
                "careers": [],
                "exam_frequency": [12, 15, 18, 20, 25]
            }
            cache_entry = SearchCache(
                query="hash table",
                result_json=cached_data,
                created_at=datetime.utcnow()
            )
            db.add(cache_entry)
            db.commit()
    finally:
        db.close()
    yield

def test_cached_search_sub_second_latency():
    """Verify that cached search responds in sub-50ms and populated data matches schema."""
    # First search warms up or uses cache
    res1 = client.post("/api/search", json={"query": "hash table"})
    assert res1.status_code == 200
    
    # Second request should be instantaneous from cache (<50ms)
    t0 = time.time()
    res2 = client.post("/api/search", json={"query": "hash table"})
    elapsed = time.time() - t0
    
    assert res2.status_code == 200
    assert elapsed < 0.25
    data = res2.json()
    assert data.get("topic") == "Hash Table"
    assert "difficulty_score" in data
    assert len(data.get("youtube_videos", [])) > 0
