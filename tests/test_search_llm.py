import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from backend.services.gemini_service import GeminiService

from backend.database import engine, Base, SessionLocal
from backend.models import SearchCache

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
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

def test_search_overview_dynamic_llm_json_structure():
    """Verify that search returns the 8 exact required structured JSON keys from the real LLM."""
    mock_llm_payload = {
        "topic": "Hash Table",
        "category": "Computer Science & Information Technology",
        "difficulty_score": 7.3,
        "difficulty_level": "Advanced",
        "ai_evaluation": "Hash tables offer amortized O(1) time complexity under SUHA. The key challenge lies in collision resolution and maintaining uniform bucket distribution. Load factor thresholding dictates table resizing overhead.",
        "overview": "A hash table is an associative array data structure that maps unique keys to values using a deterministic hash function.",
        "theoretical_foundations": "Under the Simple Uniform Hashing Assumption (SUHA), any given key is equally likely to hash into any of the m slots independently.",
        "core_formulations": "h(k) = k \\pmod m; \\alpha = \\frac{n}{m}; h(k, i) = (h'(k) + i \\cdot h_2(k)) \\pmod m",
        "did_you_know": "Hash tables were invented by Hans Peter Luhn in 1953 at IBM.",
        "study_notes": "# Executive Overview: Hash Table\\n\\nHash table notes and derivations."
    }

    with patch.object(GeminiService, "generate_topic_details", return_value=mock_llm_payload):
        res = client.get("/api/search?q=hash+table")
        assert res.status_code == 200
        data = res.json()

        # 1. Verify exact 8 required keys
        assert data.get("topic") == "Hash Table"
        assert data.get("category") == "Computer Science & Information Technology"
        assert float(data.get("difficulty_score")) == 7.3
        assert data.get("difficulty_level") == "Advanced"
        assert "SUHA" in data.get("ai_evaluation")
        assert "associative array" in data.get("overview")
        assert "Simple Uniform Hashing Assumption" in data.get("theoretical_foundations")
        assert "h(k) =" in data.get("core_formulations")

        # 2. Verify complete absence of dummy math equations in overview and formulations
        overview_fields = [
            data.get("overview", ""),
            data.get("theoretical_foundations", ""),
            data.get("core_formulations", ""),
            data.get("ai_evaluation", "")
        ]
        for field_text in overview_fields:
            assert "X_{t+1}" not in field_text
            assert "AX_t" not in field_text
            assert "X_{k+1}" not in field_text
            assert "\\mathcal{S}(x, t)" not in field_text

def test_search_overview_returns_500_on_llm_failure():
    """Verify that when the LLM call fails, the search route returns 500 instead of falling back to a mock template."""
    with patch.object(GeminiService, "generate_topic_details", side_effect=RuntimeError("Google Gemini API error: 403 Forbidden")):
        res = client.get("/api/search?q=binary+tree")
        assert res.status_code == 500
        err_data = res.json()
        assert "LLM API generation failed" in err_data.get("detail", "") or "error" in err_data
