"""
OmniLearn Backend Package
Provides access to database, models, routes, services, schemas, and lazily resolves `app`.
"""

def __getattr__(name):
    if name == "app":
        from main import app
        return app
    if name == "search_learn_topic":
        from main import search_learn_topic
        return search_learn_topic
    if name == "sanitize_study_notes":
        from backend.services.gemini_service import GeminiService
        return GeminiService.sanitize_study_notes
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
