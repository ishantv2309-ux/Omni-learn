import os
import re
import time
import datetime
import httpx
from typing import Dict, Any, List, Optional
from backend import config
from backend.database import SessionLocal
from backend.models import Note

class CrawlerService:
    @staticmethod
    def search_freeallnotes(query: str) -> Optional[str]:
        """Tries to search freeallnotes.com for the topic and extracts content."""
        try:
            search_url = f"https://freeallnotes.com/?s={query.replace(' ', '+')}"
            headers = {"User-Agent": "Mozilla/5.0 (OmniLearn Crawler; Student Hub)"}
            
            with httpx.Client(headers=headers, timeout=6.0, follow_redirects=True) as client:
                res = client.get(search_url)
                if res.status_code != 200:
                    return None
                    
                html = res.text
                
                # Regex patterns to find search result links inside WordPress standard markup
                links = re.findall(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"', html)
                if not links:
                    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>Read More', html)
                    
                if links:
                    first_link = links[0]
                    # Fetch the full article content
                    art_res = client.get(first_link)
                    if art_res.status_code == 200:
                        art_html = art_res.text
                        
                        # Extract text from paragraph blocks
                        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', art_html, re.DOTALL)
                        clean_paragraphs = []
                        for p in paragraphs:
                            # Strip nested HTML tags
                            clean_p = re.sub(r'<[^>]+>', '', p).strip()
                            # Filter out short fragments or metadata
                            if len(clean_p) > 30 and not any(w in clean_p.lower() for w in ["cookie", "privacy policy", "copyright"]):
                                clean_paragraphs.append(clean_p)
                        
                        if clean_paragraphs:
                            content = "\n\n".join(clean_paragraphs[:10]) # Limit length
                            return f"Source article: {first_link}\n\n{content}"
        except Exception as e:
            print(f"Crawler freeallnotes.com fetch notice: {e}")
        return None

    @staticmethod
    def search_google_notes(query: str) -> Optional[str]:
        """Searches Google Custom Search for reference snippets as a fallback."""
        try:
            if not config.is_search_mocked():
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "cx": config.GOOGLE_SEARCH_CX,
                    "key": config.GOOGLE_SEARCH_KEY,
                    "q": f"{query} tutorial notes study guide reference",
                    "num": 3
                }
                with httpx.Client(timeout=6.0) as client:
                    response = client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        snippets = []
                        for item in data.get("items", []):
                            snippets.append(f"Title: {item['title']}\nLink: {item['link']}\nExcerpt: {item.get('snippet', '')}")
                        if snippets:
                            return "\n\n---\n\n".join(snippets)
        except Exception as e:
            print(f"Crawler Google search notice: {e}")
        return None

    @staticmethod
    def generate_temporary_note(query: str, domain: str) -> Optional[Note]:
        """Scrapes freeallnotes.com or Google fallback, compiles the file, and stores it in database."""
        clean_q = query.strip()
        
        # 1. Search freeallnotes.com
        notes_text = CrawlerService.search_freeallnotes(clean_q)
        source_label = "freeallnotes.com"
        
        # 2. Search Google Custom Search fallback
        if not notes_text:
            notes_text = CrawlerService.search_google_notes(clean_q)
            source_label = "Google Search Engine"
            
        # 3. If offline or no results found, synthesize notes using LLM or local fallback templates
        if not notes_text:
            notes_text = CrawlerService._synthesize_local_notes(clean_q, domain)
            source_label = "AI Academic Study Notes"
            
        final_notes_text = (
            f"===================================================================\n"
            f" STUDY NOTES: {clean_q.upper()}\n"
            f" Source: {source_label}\n"
            f" Date Synthesized: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"===================================================================\n\n"
            f"{notes_text}"
        )
        
        # Write temporary text file to configured storage directory
        timestamp = int(time.time())
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', clean_q.lower())
        filename = f"temp_{slug}_{timestamp}.txt"
        target_path = config.STORAGE_DIR / filename
        
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(final_notes_text)
        except Exception as e:
            print(f"Crawler failed to write notes file: {e}")
            return None
            
        # Insert Note database record
        db = SessionLocal()
        try:
            db_note = Note(
                title=f"Study Notes: {clean_q.title()}",
                subject=domain or "Academic",
                file_path=filename,
                file_type="txt",
                ocr_text=final_notes_text,
                uploaded_by="OmniLearn Crawler"
            )
            db.add(db_note)
            db.commit()
            db.refresh(db_note)
            print(f"Successfully generated temporary notes for: '{clean_q}' -> {filename}")
            return db_note
        except Exception as e:
            print(f"Crawler failed to insert note to DB: {e}")
            db.rollback()
            if target_path.exists():
                os.remove(target_path)
            return None
        finally:
            db.close()

    @staticmethod
    def _synthesize_local_notes(query: str, domain: str) -> str:
        """Generates comprehensive notes locally (or via active Gemini if online)."""
        # Call Gemini if configured and online to synthesize rich notes
        if not config.is_gemini_mocked():
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=config.GEMINI_API_KEY)
                prompt = f"""
                You are a senior academic assistant. Generate highly comprehensive, structured, and detailed revision study notes for the academic topic: "{query}".
                Write about 300-500 words of thorough technical notes. Include definitions, key concepts, formulas or code structures (if applicable), and study references.
                Return clean text formatting suitable for notepad/terminal view.
                """
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                    ),
                )
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"Gemini crawler notes synthesis notice: {e}")
                
        # Template fallback notes
        return (
            f"### 1. Overview of {query}\n"
            f"This topic represents a central component of {domain or 'Higher Academic Study'}. "
            f"It covers the core architectural layouts, governing algorithms, and operational properties.\n\n"
            f"### 2. Key Concepts & Details\n"
            f"- Foundational Structure: The organizational structure defines the constraints and interactions.\n"
            f"- Methodical Execution: Transition sequences are performed incrementally, ensuring correctness.\n"
            f"- Operational Analysis: Running complex inputs exhibits clear asymptotic performance bounds.\n\n"
            f"### 3. Review Questions & Edge Cases\n"
            f"- How does {query} scale under extreme concurrency or data constraints?\n"
            f"- Identify two primary edge cases when evaluating {query} solutions."
        )

    @staticmethod
    def cleanup_unbookmarked_temp_notes(db):
        """Locates all temporary notes and purges them if their topics or note IDs are not bookmarked."""
        from backend.models import Bookmark
        
        try:
            # Gather bookmarks
            bookmarked_topics = {b.title.lower() for b in db.query(Bookmark).filter(Bookmark.item_type == "topic").all()}
            bookmarked_note_ids = {b.item_id for b in db.query(Bookmark).filter(Bookmark.item_type == "note").all()}
            
            # Find all notes generated by the crawler
            temp_notes = db.query(Note).filter(Note.uploaded_by == "OmniLearn Crawler").all()
            
            for note in temp_notes:
                # Extract clean topic title from format: "Study Notes: Topic Title"
                topic_name = ""
                match = re.search(r'Study Notes:\s+(.+)', note.title, re.IGNORECASE)
                if match:
                    topic_name = match.group(1).lower().strip()
                
                # Check if this temp note is NOT bookmarked directly, and its topic is NOT bookmarked
                is_bookmarked = (note.id in bookmarked_note_ids) or (topic_name and topic_name in bookmarked_topics)
                
                if not is_bookmarked:
                    # 1. Remove file
                    file_path = config.STORAGE_DIR / note.file_path
                    if file_path.exists():
                        try:
                            os.remove(file_path)
                            print(f"Cleaned up temporary notes file: {note.file_path}")
                        except Exception as file_err:
                            print(f"Error deleting temp notes file {note.file_path}: {file_err}")
                    # 2. Delete database record
                    db.delete(note)
            db.commit()
        except Exception as e:
            print(f"Error during crawler cache cleanup: {e}")
            db.rollback()
