import pytest
from fastapi.testclient import TestClient
from backend.database import engine, Base, SessionLocal
from backend.models import SearchCache
from main import app

# Set up testing database/client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Make sure tables are created in the test sqlite database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(SearchCache).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield

def test_root_route():
    response = client.get("/")
    assert response.status_code == 200
    assert "OmniLearn" in response.text

def test_unified_search():
    # Search for Newton's laws (should fetch from seeded DB / mock generator)
    response = client.get("/api/search?query=Newton")
    assert response.status_code == 200
    data = response.json()
    
    assert "query" in data
    assert data["query"] == "Newton"
    assert "summary" in data
    assert "difficulty_score" in data
    assert "roadmap" in data
    assert "youtube_videos" in data
    assert "web_resources" in data
    assert len(data["youtube_videos"]) > 0
    assert len(data["web_resources"]) > 0

def test_notes_list_and_search():
    # Fetch all notes
    response = client.get("/api/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) > 0 # We seeded some notes
    
    # Deep search notes (OCR text search)
    # The note about Newton's laws contains the word "Inertia"
    response = client.get("/api/notes/search?query=Inertia")
    assert response.status_code == 200
    searched_notes = response.json()
    assert len(searched_notes) > 0
    assert "Newton" in searched_notes[0]["title"]

def test_bookmarks_flow():
    # 1. Fetch bookmarks (should be empty initially or have seeded ones)
    response = client.get("/api/bookmarks")
    assert response.status_code == 200
    initial_bookmarks = response.json()
    
    # 2. Add bookmark
    new_bookmark = {
        "item_type": "topic",
        "item_id": 0,
        "title": "Calculus Integration"
    }
    response = client.post("/api/bookmarks", json=new_bookmark)
    assert response.status_code == 201
    bookmark_data = response.json()
    assert bookmark_data["title"] == "Calculus Integration"
    bookmark_id = bookmark_data["id"]
    
    # 3. Check list again
    response = client.get("/api/bookmarks")
    assert response.status_code == 200
    bookmarks_list = response.json()
    assert len(bookmarks_list) > len(initial_bookmarks)
    
    # 4. Delete bookmark
    response = client.delete(f"/api/bookmarks/{bookmark_id}")
    assert response.status_code == 204
    
def test_real_time_search_and_no_rickroll():
    # Search for an algorithmic topic
    response = client.get("/api/search?query=Dijkstra+Algorithm")
    assert response.status_code == 200
    data = response.json()
    
    # 1. Summary verification
    assert "summary" in data and len(data["summary"]) > 50
    assert "Dijkstra" in data["summary"] or "graph" in data["summary"].lower() or "shortest" in data["summary"].lower()
    
    # 2. Difficulty verification
    assert 1.0 <= data["difficulty_score"] <= 10.0
    assert data["difficulty_reasons"] is not None and len(data["difficulty_reasons"]) > 10
    
    # 3. Roadmap verification
    assert "roadmap" in data and len(data["roadmap"]) >= 4
    for step in data["roadmap"]:
        assert "concept" in step
        assert "description" in step
        assert "type" in step
        assert "estimated_time" in step
        
    # 4. YouTube video verification (Ensure NO Rick Roll video dQw4w9WgXcQ and sorted by view count descending)
    assert len(data["youtube_videos"]) > 0
    from backend.services.youtube_service import YouTubeService
    last_views = float('inf')
    for video in data["youtube_videos"]:
        assert video["video_id"] != "dQw4w9WgXcQ"
        assert len(video["title"]) > 0
        assert len(video["video_id"]) > 0
        v_count = YouTubeService.parse_view_count(video["view_count"])
        assert v_count <= last_views
        last_views = v_count

def test_expandable_detailed_breakdown_and_query_optimizer():
    # Test conversational natural language query with prefixes
    response = client.get("/api/search?query=what+is+the+concept+of+Photosynthesis+in+detail")
    assert response.status_code == 200
    data = response.json()
    
    # 1. Verify concise summary
    assert "summary" in data and len(data["summary"]) > 40
    
    # 2. Verify long-format detailed breakdown
    assert "detailed_breakdown" in data and data["detailed_breakdown"] is not None
    assert len(data["detailed_breakdown"]) > 100
    assert "###" in data["detailed_breakdown"] or "Photosynthesis" in data["detailed_breakdown"] or "plant" in data["detailed_breakdown"].lower()
    
    # 3. Verify domain is identified
    assert "domain" in data and len(data["domain"]) > 0

def test_careers_mapping():
    # Search for React (should return Frontend Developer and perhaps others)
    response = client.get("/api/search?query=React")
    assert response.status_code == 200
    data = response.json()
    
    assert "careers" in data
    assert data["careers"] is not None
    assert len(data["careers"]) > 0
    
    # Verify career schema structure
    first_career = data["careers"][0]
    assert "role" in first_career
    assert "roadmap_url" in first_career
    assert "importance" in first_career
    
    # Check that it contains "Frontend Developer"
    roles = [c["role"] for c in data["careers"]]
    assert "Frontend Developer" in roles
    
    # Search for an unknown topic (should fallback to general CS/Developer path)
    response_fallback = client.get("/api/search?query=SomeUnknownArbitraryTopicHere")
    assert response_fallback.status_code == 200
    data_fallback = response_fallback.json()
    assert "careers" in data_fallback
    assert len(data_fallback["careers"]) == 1
    assert "Computer Science" in data_fallback["careers"][0]["role"]

def test_temporary_notes_crawler_and_cleanup():
    import os
    from backend.config import STORAGE_DIR
    from backend.database import SessionLocal
    from backend.models import Note, Bookmark
    
    # 1. Search for a new topic
    topic_query = "Quantum Physics"
    response = client.get(f"/api/search?query={topic_query}")
    assert response.status_code == 200
    data = response.json()
    
    # 2. Verify temporary note returned
    assert "notes" in data
    assert len(data["notes"]) > 0
    temp_note = None
    for n in data["notes"]:
        if n["uploaded_by"] == "OmniLearn Crawler":
            temp_note = n
            break
    assert temp_note is not None
    assert "Study Notes:" in temp_note["title"]
    
    # Verify file exists on disk
    file_path = STORAGE_DIR / temp_note["file_path"]
    assert file_path.exists()
    
    # 3. Create a bookmark for the topic
    bookmark_payload = {
        "item_type": "topic",
        "item_id": 0,
        "title": topic_query
    }
    bk_response = client.post("/api/bookmarks", json=bookmark_payload)
    assert bk_response.status_code == 201
    bk_data = bk_response.json()
    bookmark_id = bk_data["id"]
    
    # 4. Delete the bookmark (should trigger cascading note deletion)
    del_response = client.delete(f"/api/bookmarks/{bookmark_id}")
    assert del_response.status_code == 204
    
    # Verify file is deleted on disk
    assert not file_path.exists()
    
    # Verify note is deleted from database
    db = SessionLocal()
    db_note = db.query(Note).filter(Note.file_path == temp_note["file_path"]).first()
    assert db_note is None
    db.close()

def test_academic_context_resolution():
    # Search for python, should resolve to Python programming language / Computer Science instead of snakes
    response = client.get("/api/search?query=python")
    assert response.status_code == 200
    data = response.json()
    assert "Computer Science" in data["domain"]
    assert "fun_fact" in data
    assert data["fun_fact"] is not None
    assert "Monty Python" in data["fun_fact"]

def test_dynamic_aktu_note_compilation():
    # Attempt to download a missing aktu note file
    test_filename = "aktu_test_subject_maths_unit_1.html"
    from backend.services.storage_service import StorageService
    file_path = StorageService.get_file_path(test_filename)
    
    # Ensure it doesn't exist initially
    if file_path.exists():
        file_path.unlink()
        
    response = client.get(f"/api/notes/file/{test_filename}")
    assert response.status_code == 200
    assert "DR. A.P.J. ABDUL KALAM TECHNICAL UNIVERSITY" in response.text
    
    # Cleanup
    if file_path.exists():
        file_path.unlink()

def test_search_learn_topic_endpoint():
    response = client.post("/search-learn-topic/", json={"topic": "computer science"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["topic"] == "computer science"
    assert "result" in data

def test_prohibited_age_restricted_topics():
    # 1. Test POST /search-learn-topic/ endpoint block
    response_post = client.post("/search-learn-topic/", json={"topic": "nudity"})
    assert response_post.status_code == 200
    data_post = response_post.json()
    assert data_post["status"] == "blocked"
    assert "Warning" in data_post["result"]
    assert "not an academic topic to study" in data_post["result"]

    # 2. Test GET /api/search endpoint block
    response_get = client.get("/api/search?query=nudity")
    assert response_get.status_code == 200
    data_get = response_get.json()
    assert "Warning" in data_get["summary"]
    assert "Prohibited Content" in data_get["domain"]

def test_omni_learn_search_endpoint():
    # Test brief mode
    response_brief = client.post("/omni-learn-search/", json={"topic": "computer science", "depth": "brief"})
    assert response_brief.status_code == 200
    data_brief = response_brief.json()
    assert data_brief["status"] == "success"
    assert data_brief["depth"] == "brief"
    assert "MOCK GROUNDED SUMMARY" in data_brief["result"]

    # Test comprehensive mode
    response_comp = client.post("/omni-learn-search/", json={"topic": "computer science", "depth": "comprehensive"})
    assert response_comp.status_code == 200
    data_comp = response_comp.json()
    assert data_comp["status"] == "success"
    assert data_comp["depth"] == "comprehensive"
    assert "EXAM FREQUENCY & PYQ ANALYSIS" in data_comp["result"]

    # Test blocked / age-restricted topics
    response_blocked = client.post("/omni-learn-search/", json={"topic": "nudity"})
    assert response_blocked.status_code == 200
    data_blocked = response_blocked.json()
    assert data_blocked["status"] == "blocked"
    assert "Warning" in data_blocked["result"]

def test_api_key_configuration_endpoints():
    from backend import config
    original_key = config.GEMINI_API_KEY
    try:
        # 1. Fetch current status
        response_get = client.get("/api/config/get-status")
        assert response_get.status_code == 200
        data_get = response_get.json()
        assert data_get["status"] == "success"
        assert "has_key" in data_get

        # 2. Save a test API Key
        response_post = client.post("/api/config/save-key", json={"gemini_api_key": "TEST_GEMINI_KEY_123456"})
        assert response_post.status_code == 200
        data_post = response_post.json()
        assert data_post["status"] == "success"

        # 3. Verify status updated
        response_get_new = client.get("/api/config/get-status")
        assert response_get_new.status_code == 200
        data_get_new = response_get_new.json()
        assert data_get_new["has_key"] is True
        assert data_get_new["masked_key"] == "TEST...3456"
    finally:
        # Restore original key
        client.post("/api/config/save-key", json={"gemini_api_key": original_key})

def test_post_search_proxy_endpoint():
    """Verify POST /api/search handles query without client API key requirement."""
    response = client.post("/api/search", json={"query": "Dijkstra's Algorithm"})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Dijkstra's Algorithm"
    assert "summary" in data
    assert "difficulty_score" in data
    assert len(data["youtube_videos"]) > 0

def test_gemini_dedicated_endpoint():
    """Verify POST and GET /api/gemini proxy endpoints work server-side."""
    # POST
    response_post = client.post("/api/gemini", json={"query": "Newton's Laws"})
    assert response_post.status_code == 200
    data_post = response_post.json()
    assert "summary" in data_post
    assert "difficulty_score" in data_post

    # GET
    response_get = client.get("/api/gemini", params={"query": "Newton's Laws"})
    assert response_get.status_code == 200
    data_get = response_get.json()
    assert "summary" in data_get



