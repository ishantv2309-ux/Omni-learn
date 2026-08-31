import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel

from backend.database import engine, Base
from backend.routes import search, notes, pyqs, bookmarks

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniLearn API",
    description="Unified single-search educational engine API",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(search.router)
app.include_router(notes.router)
app.include_router(pyqs.router)
app.include_router(bookmarks.router)

class SearchQuery(BaseModel):
    topic: str

@app.post("/search-learn-topic/")
async def search_learn_topic(query: SearchQuery):
    try:
        from backend.routes.search import is_inappropriate_topic
        if is_inappropriate_topic(query.topic):
            return {
                "status": "blocked",
                "topic": query.topic,
                "result": "⚠️ Warning: This is not an academic topic to study. Age-restricted or inappropriate content is prohibited on OmniLearn."
            }
            
        from backend import config
        if config.is_gemini_mocked():
            return {
                "status": "success",
                "topic": query.topic,
                "result": (
                    f"📊 **EXAM FREQUENCY & PYQ ANALYSIS**\n"
                    f"• **PYQ Importance Level:** High\n"
                    f"• **Recent Appearances:** AKTU 2024, GATE 2023, UPTU 2022\n"
                    f"• **Weightage Trend:** Typically carries 5-10 marks in theoretical and numerical sections.\n\n"
                    f"📚 **TOPIC CORE CONCEPTS**\n"
                    f"Core revision notes and formulas for '{query.topic}'. Focuses on fundamental principles, mathematical relationships, and applications."
                )
            }
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        prompt = (
            f"SYSTEM ROLE: You are an educational research and examination analysis engine for Omni Learn.\n"
            f"TARGET TOPIC: '{query.topic}'\n\n"
            "INSTRUCTIONS:\n"
            "1. Search live web data to analyze how frequently this topic has appeared in Previous Years' Questions (PYQs) and competitive exams.\n"
            "2. Determine its importance tier (High Frequency / Moderate / Rare) and recent exam trends.\n"
            "3. Return the response using the following structured format:\n\n"
            "📊 **EXAM FREQUENCY & PYQ ANALYSIS**\n"
            "• **PYQ Importance Level:** [High / Medium / Low]\n"
            "• **Recent Appearances:** [List specific years or exam types where this topic appeared recently]\n"
            "• **Weightage Trend:** [Brief summary of mark weightage or question types]\n\n"
            "📚 **TOPIC CORE CONCEPTS**\n"
            "[Provide concise, accurate core notes and formulas for this topic]"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                tools=[{"google_search": {}}],
            ),
        )

        return {
            "status": "success",
            "topic": query.topic,
            "result": response.text,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Search Engine Error: {str(e)}"
        )

class LearnQuery(BaseModel):
    topic: str
    depth: str = "comprehensive"  # Options: 'brief' or 'comprehensive'

@app.post("/omni-learn-search/")
async def omni_learn_search(query: LearnQuery):
    try:
        from backend.routes.search import is_inappropriate_topic
        if is_inappropriate_topic(query.topic):
            return {
                "status": "blocked",
                "topic": query.topic,
                "depth": query.depth,
                "result": "⚠️ Warning: This is not an academic topic to study. Age-restricted or inappropriate content is prohibited on OmniLearn."
            }

        from backend import config
        if config.is_gemini_mocked():
            if query.depth == "brief":
                result_text = f"MOCK GROUNDED SUMMARY: Core definition and key takeaway for '{query.topic}'. Simple, concise overview under 150 words."
            else:
                result_text = (
                    f"📊 **EXAM FREQUENCY & PYQ ANALYSIS**\n"
                    f"• **PYQ Importance Level:** High\n"
                    f"• **Recent Appearances:** AKTU 2024, GATE 2023, UPTU 2022\n"
                    f"• **Weightage Trend:** Typically carries 5-10 marks in theoretical and numerical sections.\n\n"
                    f"📚 **TOPIC CORE CONCEPTS**\n"
                    f"Definitional Overview & Context, Core Concepts / Formulas / Architecture, Real-world Applications for '{query.topic}'."
                )
            return {
                "status": "success",
                "topic": query.topic,
                "depth": query.depth,
                "result": result_text
            }
            
        from google import genai
        from google.genai import types
        
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        if query.depth == "brief":
            depth_instruction = (
                "Provide a concise, high-impact summary of the topic (under 150 words). "
                "Focus strictly on the core definition and key takeaway."
            )
        else:
            depth_instruction = (
                "Provide a deeply detailed, comprehensive breakdown including: "
                "1. Definitional Overview & Context\n"
                "2. Core Concepts / Formulas / Architecture\n"
                "3. Previous Years' Questions (PYQs) or Industry Frequency\n"
                "4. Real-world Applications"
            )

        prompt = (
            f"SYSTEM ROLE: You are the verified research engine for Omni Learn.\n"
            f"TARGET TOPIC: '{query.topic}'\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Search live web data to verify exact technical facts, academic definitions, and exam trends.\n"
            f"2. {depth_instruction}\n"
            f"3. Ensure 100% factual accuracy. Do not include introductory conversational fluff."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                tools=[{"google_search": {}}],
            ),
        )

        return {
            "status": "success",
            "topic": query.topic,
            "depth": query.depth,
            "result": response.text,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Omni Learn Processing Error: {str(e)}"
        )

class ApiKeyConfig(BaseModel):
    gemini_api_key: str

@app.post("/api/config/save-key")
async def save_config_key(config_data: ApiKeyConfig):
    try:
        env_path = BASE_DIR / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()
        lines = [line for line in lines if not line.strip().startswith("GEMINI_API_KEY=")]
        lines.append(f"GEMINI_API_KEY={config_data.gemini_api_key}\n")
        with open(env_path, "w") as f:
            f.writelines(lines)
            
        from backend import config
        config.GEMINI_API_KEY = config_data.gemini_api_key
        return {"status": "success", "message": "API key successfully updated and reloaded!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

@app.get("/api/config/get-status")
async def get_config_status():
    from backend import config
    has_key = bool(config.GEMINI_API_KEY)
    masked_key = ""
    if has_key:
        key = config.GEMINI_API_KEY
        if len(key) > 8:
            masked_key = key[:4] + "..." + key[-4:]
        else:
            masked_key = "..."
    return {
        "status": "success",
        "has_key": has_key,
        "masked_key": masked_key
    }

# Mount frontend files
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Serve index.html at root
@app.get("/")
def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        return {"message": "OmniLearn Frontend not build/found yet. Please create frontend/index.html"}
    return FileResponse(index_path)

# Serve app.js and other files directly from frontend/
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting OmniLearn Server on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
