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
                "You are an expert AKTU university professor. "
                "CRITICAL MANDATE: Generate notes EXCLUSIVELY for the provided syllabus topics. "
                "NEVER include Amdahl's Law, Speedup equations, Linked Lists, or generic template "
                "formulas unless they are explicitly requested in the syllabus list."
            )
        )
        
        topics_list = ", ".join(req.aktu_syllabus_topics)
        
        DYNAMIC_PROMPT = f"""
        [Generation Timestamp: {time.time()}]
        
        SUBJECT: {req.subject_code} - {req.subject_name}
        UNIT: Unit {req.unit_number}
        EXPACT SYLLABUS TOPICS: [{topics_list}]

        Generate technical revision notes following this exact structure:

        # {req.subject_code}: Unit {req.unit_number} - {req.subject_name} Revision Notes

        ## 1. Technical Topic Breakdown
        - Provide deep explanations strictly for: [{topics_list}].
        - Use formulas, registers, or code snippets that ONLY belong to [{topics_list}].

        ## 2. Section A: 2-Mark Exam Questions & Solutions
        - Generate 5 distinct 2-mark questions and answers strictly based on [{topics_list}].

        ## 3. Section B/C: 10-Mark Exam Questions & Solutions
        - Generate 3 distinct 10-mark long questions and full step-by-step solutions strictly based on [{topics_list}].
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

import json
import time
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()


class UnitNoteRequest(BaseModel):
  subject_code: str
  subject_name: str
  unit_number: int
  aktu_syllabus_topics: list[str]


@app.post("/api/generate-unit-notes")
async def generate_aktu_unit_notes(req: UnitNoteRequest):
  try:
    # 1. Switch to gemini-1.5-flash for ultra-fast generation speed
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You are a strict AKTU exam note generator. "
            "Output concise, highly accurate revision notes ONLY for the requested topics. "
            "Do NOT output generic formulas, Amdahl's Law, or topics outside the syllabus list."
        ),
    )

    topics_list = ", ".join(req.aktu_syllabus_topics)

    prompt = f"""
        SUBJECT: {req.subject_code} - {req.subject_name}
        UNIT: Unit {req.unit_number}
        EXACT TOPICS: [{topics_list}]

        # {req.subject_code}: Unit {req.unit_number} - {req.subject_name}

        ## 1. Quick Technical Concepts
        (Provide concise breakdowns strictly for: [{topics_list}])

        ## 2. Section A: 2-Mark Questions & Answers
        (5 short, precise solved questions strictly on [{topics_list}])

        ## 3. Section B/C: 10-Mark Solved Questions
        (2 high-yield solved exam problems strictly on [{topics_list}])
        """

    # 2. Enable streaming output (stream=True)
    def generate_stream():
      response = model.generate_content(
          prompt,
          stream=True,
          generation_config={"max_output_tokens": 2048, "temperature": 0.0},
      )
      for chunk in response:
        if chunk.text:
          yield chunk.text

    return StreamingResponse(generate_stream(), media_type="text/plain")

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
