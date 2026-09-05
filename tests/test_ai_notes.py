import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_generate_topic_notes_endpoint():
    """Verify Mode 2: Topic-wise Deep Dive endpoint with LaTeX math."""
    payload = {
        "topic": "Quick Sort Algorithm",
        "subject": "Design and Analysis of Algorithms"
    }
    response = client.post("/api/generate-notes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Quick Sort Algorithm"
    assert data["subject"] == "Design and Analysis of Algorithms"
    assert "notes" in data
    assert len(data["notes"]) > 100
    assert "$" in data["notes"] or "##" in data["notes"]

def test_cs_domain_discrimination_array_linked_list_recursion():
    """Verify CS queries (array, linked list, recursion) do NOT hallucinate control systems or differential equations."""
    for cs_topic in ["array", "linked list", "recursion"]:
        response = client.post("/api/generate-notes", json={"topic": cs_topic})
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == cs_topic
        assert "Computer Science" in data["subject"]
        notes = data["notes"].lower()
        # Must NOT contain control systems or calculus equations
        assert "differential equation" not in notes
        assert "divergence theorem" not in notes
        assert "control system" not in notes
        assert "\\nabla" not in notes
        # Must contain CS specific content
        assert any(term in notes for term in ["time complexity", "big-o", "o(1)", "o(n)", "space complexity", "recurrence", "memory"])

def test_generate_aktu_unit_notes_structure_and_dynamic_binding():
    """Verify Mode 1: AKTU Unit-Wise endpoint strictly binds to unit and outputs required Q&A sections."""
    for test_unit in [1, 3, 5]:
        payload = {
            "subject_code": "KCS301",
            "subject_name": "Data Structures",
            "unit_number": test_unit,
            "aktu_syllabus_topics": [f"Topic A for Unit {test_unit}", f"Topic B for Unit {test_unit}"]
        }
        response = client.post("/api/generate-unit-notes", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["subject_code"] == "KCS301"
        assert data["unit"] == test_unit
        notes_text = data.get("unit_notes") or data.get("notes")
        assert len(notes_text) > 100
        
        # Enforce required section titles
        assert "AKTU End-Semester Examination Notes" in notes_text
        assert f"Unit: {test_unit}" in notes_text
        assert "AKTU Exam Scoring Strategy & Common Marking Pitfalls" in notes_text
        assert "Specific Notes on Important Topics" in notes_text
        assert "Section A: 2-Mark Short Questions" in notes_text
        assert "Section B/C: 10-Mark Long Questions" in notes_text

def test_unit_isolation_unit_3_never_returns_unit_1_or_2():
    """Verify that requesting Unit 3 returns Unit 3 content and never Unit 1 or Unit 2 content."""
    payload = {
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 3,
        "aktu_syllabus_topics": ["Linked Lists", "Singly Linked List", "Doubly Linked List", "Circular Linked List"]
    }
    response = client.post("/api/generate-unit-notes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["unit"] == 3
    notes = data["unit_notes"]
    assert "Unit: 3" in notes
    assert "Linked List" in notes
    # Must NOT have Unit 1 or Unit 2 themes as the overarching unit
    assert "Unit: 1" not in notes
    assert "Unit: 2" not in notes

