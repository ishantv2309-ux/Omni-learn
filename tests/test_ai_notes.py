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

def test_high_yield_revision_5_section_a_and_3_section_bc_solved():
    """Verify that Unit notes contain exactly 5 Section A 2-mark questions and 3 Section B/C 10-mark solved questions."""
    payload = {
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 1,
        "aktu_syllabus_topics": ["Arrays", "Row Major", "Column Major", "Recursion", "Complexity"]
    }
    response = client.post("/api/generate-unit-notes", json=payload)
    assert response.status_code == 200
    notes = response.json().get("unit_notes")
    
    # Verify Section A has 5 solved questions
    assert "Section A: 2-Mark Short Questions (5 Fully Solved with Solutions)" in notes
    for q_num in ["1. **Q1", "2. **Q2", "3. **Q3", "4. **Q4", "5. **Q5"]:
        assert q_num in notes
        
    # Verify Section B/C has 3 solved numericals/questions
    assert "Section B/C: 10-Mark Long Questions & Numericals (3 Fully Solved with Solutions)" in notes
    for q_num in ["1. **Q1", "2. **Q2", "3. **Q3"]:
        assert q_num in notes

    # Verify presence of LaTeX math and formulas
    assert "$" in notes
    assert "Row-Major" in notes or "Column-Major" in notes or "Base" in notes

import importlib.util
from pathlib import Path

def _get_backend_py_app():
    py_path = Path(__file__).resolve().parent.parent / "backend.py"
    spec = importlib.util.spec_from_file_location("standalone_backend", py_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app

def test_backend_academic_scope_guardrail_blocks_non_btech():
    """Verify that backend.py strictly rejects non-B.Tech topics (e.g., legal maxims, cooking) with 400."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)
    
    # Test legal maxim
    res_legal = b_client.get("/api/search?q=damnum+sine+injuria")
    assert res_legal.status_code == 400
    assert "This topic is outside your academic syllabus" in res_legal.json()["detail"]

    # Test cooking
    res_cook = b_client.get("/api/search?q=pasta+recipe")
    assert res_cook.status_code == 400
    assert "This topic is outside your academic syllabus" in res_cook.json()["detail"]

def test_backend_academic_scope_allows_engineering_topic():
    """Verify that backend.py accepts valid engineering topics."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)
    
    res = b_client.get("/api/search?q=Binary+Search+Tree")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "Binary Search Tree" in data["query"]
    assert len(data["content"]) > 50

def test_backend_generate_unit_notes_endpoint():
    """Verify that backend.py /api/generate-unit-notes returns structured AKTU revision notes."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)
    
    payload = {
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 2,
        "aktu_syllabus_topics": ["Stacks", "Queues", "Recursion"]
    }
    res = b_client.post("/api/generate-unit-notes", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["subject_code"] == "KCS301"
    assert data["unit"] == 2
    assert "unit_notes" in data
    assert len(data["unit_notes"]) > 100
    assert "Unit 2" in data["unit_notes"]

def test_kcs302_coa_does_not_inject_data_structures():
    """Verify that non-KCS301 subjects (e.g., KCS302 Computer Organization) strictly bind to their topics without injecting Data Structures."""
    payload = {
        "subject_code": "KCS302",
        "subject_name": "Computer Organization and Architecture",
        "unit_number": 3,
        "aktu_syllabus_topics": ["Memory Hierarchy", "Cache Memory Mapping", "Virtual Memory", "Paging"]
    }
    # Test primary app router
    res = client.post("/api/generate-unit-notes", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["subject_code"] == "KCS302"
    assert data["unit"] == 3
    notes = data.get("unit_notes") or data.get("notes")
    
    # Must contain COA subject and topic details
    assert "KCS302" in notes
    assert "Memory" in notes or "Cache" in notes
    
    # Absolute rule: Must NOT contain Data Structures topics
    assert "Linked List" not in notes
    assert "Doubly Linked" not in notes
    assert "Binary Search Tree" not in notes
    assert "Row-Major Order" not in notes

    # Test standalone backend.py
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)
    b_res = b_client.post("/api/generate-unit-notes", json=payload)
    assert b_res.status_code == 200
    b_notes = b_res.json().get("unit_notes") or b_res.json().get("notes")
    assert "KCS302" in b_notes
    assert "Linked List" not in b_notes
    assert "Binary Search Tree" not in b_notes

def test_zero_hallucination_negative_constraints():
    """Verify negative constraints: Unit 2 Linked Lists has NO Stacks/Queues/Hanoi, and Unit 3 Stacks/Queues has NO Trees/Graphs."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)

    # 1. Unit 2 (Linked Lists): DO NOT mention Stacks, Queues, Circular Queues, Infix/Postfix conversion, or Tower of Hanoi
    res_u2 = client.post("/api/generate-unit-notes", json={
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 2,
        "aktu_syllabus_topics": ["Linked Lists", "Singly Linked List", "Doubly Linked List", "Circular Linked List"]
    })
    assert res_u2.status_code == 200
    notes_u2 = res_u2.json().get("unit_notes") or res_u2.json().get("notes")
    assert "Linked List" in notes_u2
    assert "Stack" not in notes_u2
    assert "Queue" not in notes_u2
    assert "Circular Queue" not in notes_u2
    assert "Infix" not in notes_u2
    assert "Postfix" not in notes_u2
    assert "Tower of Hanoi" not in notes_u2
    assert "Hanoi" not in notes_u2

    # Verify same on backend.py
    b_res_u2 = b_client.post("/api/generate-unit-notes", json={
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 2,
        "aktu_syllabus_topics": ["Linked Lists", "Singly Linked List", "Doubly Linked List", "Circular Linked List"]
    })
    assert b_res_u2.status_code == 200
    b_notes_u2 = b_res_u2.json().get("unit_notes")
    assert "Linked List" in b_notes_u2
    assert "Stack" not in b_notes_u2
    assert "Queue" not in b_notes_u2
    assert "Hanoi" not in b_notes_u2

    # 2. Unit 3 (Stacks/Queues): DO NOT mention Trees or Graphs
    res_u3 = client.post("/api/generate-unit-notes", json={
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 3,
        "aktu_syllabus_topics": ["Stacks", "Queues", "Circular Queues", "Infix to Postfix", "Recursion"]
    })
    assert res_u3.status_code == 200
    notes_u3 = res_u3.json().get("unit_notes") or res_u3.json().get("notes")
    assert "Stack" in notes_u3
    assert "Queue" in notes_u3
    assert "Tree" not in notes_u3
    assert "Graph" not in notes_u3
    assert "Binary Search Tree" not in notes_u3
    assert "Dijkstra" not in notes_u3

    # Verify same on backend.py
    b_res_u3 = b_client.post("/api/generate-unit-notes", json={
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 3,
        "aktu_syllabus_topics": ["Stacks", "Queues", "Circular Queues", "Infix to Postfix", "Recursion"]
    })
    assert b_res_u3.status_code == 200
    b_notes_u3 = b_res_u3.json().get("unit_notes")
    assert "Stack" in b_notes_u3
    assert "Tree" not in b_notes_u3
    assert "Graph" not in b_notes_u3

def test_coa_unit_1_forbids_amdahls_law_and_template_bleed():
    """Verify absolute rejection rules: COA Unit 1 has NO Amdahl's Law, NO differential equations, NO generic filler, and valid RTL notation."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)

    payload = {
        "subject_code": "KCS302",
        "subject_name": "Computer Organization and Architecture",
        "unit_number": 1,
        "aktu_syllabus_topics": [
            "Register Transfer Language", 
            "Bus and Memory Transfers", 
            "Arithmetic Micro-operations", 
            "Logic Micro-operations", 
            "Shift Micro-operations"
        ]
    }

    for cl in [client, b_client]:
        res = cl.post("/api/generate-unit-notes", json=payload)
        assert res.status_code == 200
        notes = res.json().get("unit_notes") or res.json().get("notes")

        # 1. Must contain domain-accurate RTL and micro-operations
        assert "Register Transfer" in notes or "RTL" in notes
        assert "\\leftarrow" in notes or "<-" in notes or "Micro-operation" in notes
        assert "Bus" in notes

        # 2. ABSOLUTE REJECTION RULE 1: NO Amdahl's law or parallel speedup formulas
        assert "Amdahl" not in notes
        assert "T_\\text{serial}" not in notes
        assert "T_\\text{{serial}}" not in notes
        assert "T_{serial}" not in notes
        assert "\\frac{1}{(1-f)" not in notes
        assert "\\frac{1}{(1 - f)" not in notes
        assert "\\frac{{1}}{{(1 - f)" not in notes

        # 3. ABSOLUTE REJECTION RULE 2: NO differential equations / Laplacian
        assert "\\nabla" not in notes
        assert "differential equation" not in notes.lower()
        assert "\\mathcal{L}" not in notes

        # 4. ABSOLUTE REJECTION RULE 3: NO generic header intro filler
        assert "Key performance metrics, timing models" not in notes


def test_cache_busting_headers_and_timestamp():
    """Verify that /api/generate-unit-notes returns strict no-cache headers and dynamic timestamp."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)

    payload = {
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 1,
        "aktu_syllabus_topics": ["Arrays", "Searching and Sorting"]
    }

    for cl in [client, b_client]:
        res = cl.post("/api/generate-unit-notes", json=payload)
        assert res.status_code == 200
        # Check HTTP cache-busting headers
        assert "no-cache" in res.headers.get("cache-control", "").lower()
        assert "no-store" in res.headers.get("cache-control", "").lower()
        assert res.headers.get("pragma", "").lower() == "no-cache"
        assert res.headers.get("expires") == "0"
        
        # Check JSON response payload
        data = res.json()
        assert "timestamp" in data
        assert isinstance(data["timestamp"], (int, float))
        assert data["timestamp"] > 0


def test_exact_aktu_exam_specialist_output_structure():
    """Verify that notes follow the exact 4-section AKTU Specialist output structure."""
    backend_app = _get_backend_py_app()
    b_client = TestClient(backend_app)

    payload = {
        "subject_code": "KCS301",
        "subject_name": "Data Structures",
        "unit_number": 1,
        "aktu_syllabus_topics": ["Arrays", "Searching and Sorting", "Asymptotic Analysis"]
    }

    for cl in [client, b_client]:
        res = cl.post("/api/generate-unit-notes", json=payload)
        assert res.status_code == 200
        notes = res.json().get("unit_notes") or res.json().get("notes")

        # Check exact Title
        assert "KCS301" in notes and "Unit 1" in notes and "Revision & Exam Guide" in notes

        # Check 4 Exact Structure Headings
        assert ("## 1. Complete Unit Concept Breakdown" in notes or "## 1. Core Technical Concept Breakdown" in notes)
        assert ("## 2. AKTU Exam Scoring Strategy & Pitfalls" in notes or "## 2. Exam Scoring Strategy & Common Pitfalls" in notes)
        assert ("## 3. Section A: 2-Mark Short Answer Questions (10 Fully Solved Questions)" in notes or "## 3. Section A: 2-Mark Short Questions & Answers" in notes)
        assert ("## 4. Section B & C: 10-Mark Long Questions & Numericals (5 Fully Solved Questions)" in notes or "## 4. Section B & C: 10-Mark Long Questions & Answers" in notes)
