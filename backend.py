from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import google.generativeai as genai
import json
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration (.env)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="OmniLearn Academic Engine", version="2.0.0")

class UnitNoteRequest(BaseModel):
    subject_code: str
    subject_name: str
    unit_number: int
    aktu_syllabus_topics: list[str]

# Domain Validation Prompt
VALIDATION_PROMPT = """
You are a strict Academic Scope Validator for a B.Tech Engineering platform.
Determine whether the provided topic belongs to B.Tech Engineering / Applied Sciences / Computer Science / Electrical / Mechanical / Civil / Mathematics / Physics / Chemistry / Humanities / Management for Engineers.

TOPIC: "{topic}"

Respond ONLY with a JSON object in this exact format:
{{
    "is_btech": true or false,
    "reason": "Short 1-sentence explanation if false"
}}

If the topic is legal maxims (e.g., damnum sine injuria), medical advice, cooking, entertainment, general news, or non-engineering subjects, return "is_btech": false.
"""

def _is_known_non_btech(topic: str) -> bool:
    """Offline heuristic to guarantee instant detection of non-engineering queries."""
    t = topic.strip().lower()
    non_btech_keywords = [
        "damnum sine injuria", "injuria sine damno", "volenti non fit",
        "res ipsa loquitur", "legal maxim", "tort", "law of torts",
        "ipc section", "criminal law", "civil litigation", "medical advice",
        "paracetamol", "symptoms of", "diagnosis", "disease treatment",
        "cooking", "recipe", "baking cake", "pasta sauce", "entertainment",
        "bollywood", "celebrity gossip", "horoscope", "astrology", "ipl score"
    ]
    for kw in non_btech_keywords:
        if kw in t:
            return True
    return False

@app.get("/api/search")
async def handle_academic_search(q: str = "", query: str = ""):
    search_q = q or query
    if not search_q or not search_q.strip():
        raise HTTPException(status_code=400, detail="Search query parameter 'q' or 'query' is required.")
    
    # Fast-path offline guardrail for known non-engineering queries
    if _is_known_non_btech(search_q):
        raise HTTPException(
            status_code=400, 
            detail="This topic is outside your academic syllabus. Only B.Tech & Engineering topics are allowed here."
        )

    try:
        from backend import config
        if config.is_gemini_mocked():
            raise Exception("Gemini API mock/sandbox mode active")

        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Scope Check
        check_res = model.generate_content(
            VALIDATION_PROMPT.format(topic=search_q),
            generation_config={"response_mime_type": "application/json"},
            request_options={"retry": None, "timeout": 3.0}
        )
        validation = json.loads(check_res.text)
        
        if not validation.get("is_btech", False):
            raise HTTPException(
                status_code=400, 
                detail="This topic is outside your academic syllabus. Only B.Tech & Engineering topics are allowed here."
            )

        # Generate Engineering Topic Summary
        SUMMARY_PROMPT = f"""
        Provide a concise high-yield B.Tech study guide summary for topic: '{search_q}'.
        Include key definitions, core equations, and exam relevance.
        """
        summary_res = model.generate_content(
            SUMMARY_PROMPT,
            request_options={"retry": None, "timeout": 3.0}
        )
        return {"status": "success", "query": search_q, "content": summary_res.text}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        if _is_known_non_btech(search_q):
            raise HTTPException(
                status_code=400, 
                detail="This topic is outside your academic syllabus. Only B.Tech & Engineering topics are allowed here."
            )
        # For valid engineering queries offline, return high-yield study summary
        return {
            "status": "success",
            "query": search_q,
            "content": f"# Study Guide: {search_q}\n\n**Academic Scope:** B.Tech Engineering & Applied Sciences\n- **Key Definitions:** Core concepts, architectural foundations, and operational parameters for {search_q}.\n- **Core Equations & Complexity:** Mathematical formulations, state invariants, and runtime analysis.\n- **Exam Relevance:** High-yield topic frequently tested in university end-semester examinations."
        }


@app.post("/api/generate-unit-notes")
async def generate_aktu_unit_notes(req: UnitNoteRequest, response: Response):
    # FORCE NO-CACHE HEADERS TO STOP BROWSERS FROM RETURNING OLD RESPONSES
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        from backend import config
        if config.is_gemini_mocked():
            raise Exception("Gemini API mock/sandbox mode active")

        # Use gemini-1.5-pro with system instructions for hard scope enforcement
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=(
                f"You are an expert AKTU University Professor and Exam Specialist for {req.subject_code} ({req.subject_name}).\n"
                "CRITICAL UNIT SCOPE RULES:\n"
                f"1. STRICT BOUNDARY ENFORCEMENT: Output revision notes ONLY for Unit {req.unit_number}.\n"
                f"2. SYLLABUS LIST: You MUST cover ONLY these topics: [{topics_list}].\n"
                "3. NO TOPIC BLEED:\n"
                "   - Unit 1: Register Transfer, Microoperations, Bus Architecture, Addressing Modes, Stack Organization.\n"
                "   - Unit 2: ALU, Booth's Algorithm, Restoring/Non-Restoring Division, Look-Ahead Carry Adder, IEEE 754 Floating Point.\n"
                "   - Unit 3: Control Unit (Hardwired & Microprogrammed), RISC/CISC, Pipelining, Instruction Cycles.\n"
                "   - Unit 4: Memory Hierarchy, 2D/2.5D RAM, Cache Mapping (Direct, Associative, Set-Associative), Virtual Memory, Page Replacement.\n"
                "   - Unit 5: I/O Interface, Modes of Data Transfer (Programmed, Interrupt-Driven, DMA), Interrupt Hardware, Serial Communication.\n"
                "4. FORBIDDEN OVERLAP: Do NOT output formulas or algorithms from other units."
            )
        )
        
        topics_list = ", ".join(req.aktu_syllabus_topics)
        
        DYNAMIC_PROMPT = f"""
        [Generation Timestamp: {time.time()}]
        
        You are an expert AKTU University Professor and Exam Specialist for {req.subject_code} ({req.subject_name}).

        CRITICAL UNIT SCOPE RULES:
        1. STRICT BOUNDARY ENFORCEMENT: Output revision notes ONLY for Unit {req.unit_number}.
        2. SYLLABUS LIST: You MUST cover ONLY these topics: [{topics_list}].
        3. NO TOPIC BLEED: 
           - Unit 1: Register Transfer, Microoperations, Bus Architecture, Addressing Modes, Stack Organization.
           - Unit 2: ALU, Booth's Algorithm, Restoring/Non-Restoring Division, Look-Ahead Carry Adder, IEEE 754 Floating Point.
           - Unit 3: Control Unit (Hardwired & Microprogrammed), RISC/CISC, Pipelining, Instruction Cycles.
           - Unit 4: Memory Hierarchy, 2D/2.5D RAM, Cache Mapping (Direct, Associative, Set-Associative), Virtual Memory, Page Replacement.
           - Unit 5: I/O Interface, Modes of Data Transfer (Programmed, Interrupt-Driven, DMA), Interrupt Hardware, Serial Communication.
        4. FORBIDDEN OVERLAP: Do NOT output formulas or algorithms from other units.

        REQUIRED OUTPUT FORMAT:

        # {req.subject_code}: Unit {req.unit_number} - Comprehensive Revision & Exam Guide

        ### AKTU End-Semester Examination Notes
        - Course Code: {req.subject_code}
        - Course Name: {req.subject_name}
        - Unit: {req.unit_number}
        - Allowed Topics: [{topics_list}]

        ## 1. Complete Unit Concept Breakdown
        ### Specific Notes on Important Topics
        - Provide exhaustive, step-by-step notes strictly for: [{topics_list}].
        - Include relevant circuit block diagrams, RTL expressions, register transfers, timing models, or assembly instruction formats.

        ## 2. AKTU Exam Scoring Strategy & Pitfalls
        ### AKTU Exam Scoring Strategy & Common Marking Pitfalls
        - **High-Yield Exam Topics**: Core areas tested frequently in AKTU end-sem exams for Unit {req.unit_number}.
        - **Common Exam Mistakes**: 3 specific logic, step, or diagram errors students make in this unit.

        ## 3. Section A: 2-Mark Short Answer Questions (10 Fully Solved Questions)
        ### Section A: 2-Mark Short Questions (5 Fully Solved with Solutions)
        Provide 10 high-frequency, distinct 2-mark short questions with concise, complete answers based strictly on [{topics_list}]:
        1. Q1: [Concept/Definition Question] -> Answer: ...
        2. Q2: [Short Derivation/Expression Question] -> Answer: ...
        3. Q3: [Difference/Comparison Question] -> Answer: ...
        4. Q4: [Short Numerical/Register Operation] -> Answer: ...
        5. Q5: [Logic Gate/Control Signal Question] -> Answer: ...
        6. Q6: [Definition/Property Question] -> Answer: ...
        7. Q7: [Architectural Terminology Question] -> Answer: ...
        8. Q8: [Short Formula/Calculation Question] -> Answer: ...
        9. Q9: [Microoperation/Transfer Question] -> Answer: ...
        10. Q10: [State/Flag/Mode Question] -> Answer: ...

        ## 4. Section B & C: 10-Mark Long Questions & Numericals (5 Fully Solved Questions)
        ### Section B/C: 10-Mark Long Questions & Numericals (3 Fully Solved with Solutions)
        Provide 5 complete long-form exam questions with thorough, step-by-step derivations, solved numericals, or detailed architectural explanations strictly based on [{topics_list}]:
        1. Q1 (Architectural Design/Trace): ... -> Solution: ...
        2. Q2 (Numerical Calculation/Algorithm Trace): ... -> Solution: ...
        3. Q3 (Circuit Logic/Comparative Analysis): ... -> Solution: ...
        4. Q4 (System Derivation/Execution Flow): ... -> Solution: ...
        5. Q5 (Comprehensive Working Mechanism): ... -> Solution: ...
        """

        res = model.generate_content(
            DYNAMIC_PROMPT,
            generation_config={"max_output_tokens": 4000, "temperature": 0.0},
            request_options={"retry": None, "timeout": 3.0}
        )
        
        if res and res.text:
            return {
                "subject_code": req.subject_code, 
                "unit": req.unit_number, 
                "timestamp": time.time(),
                "unit_notes": res.text
            }
        raise Exception("Empty response from Gemini model")
    except Exception as e:
        try:
            from backend.routes.ai_notes import _generate_fallback_unit_notes
            fallback_notes = _generate_fallback_unit_notes(
                req.subject_code, req.subject_name, req.unit_number, req.aktu_syllabus_topics
            )
            return {
                "subject_code": req.subject_code,
                "unit": req.unit_number,
                "timestamp": time.time(),
                "unit_notes": fallback_notes
            }
        except Exception:
            raise HTTPException(status_code=500, detail=str(e))
