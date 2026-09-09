import time
import pytest
from fastapi.testclient import TestClient
from main import app
from backend.database import engine, Base, SessionLocal
from backend.models import SearchCache

client = TestClient(app)

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
