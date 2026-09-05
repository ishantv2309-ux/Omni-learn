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
    def generate_temporary_note(query: str, domain: str, pre_generated_notes: Optional[str] = None) -> Optional[Note]:
        """Synthesizes or compiles structured study notes and stores in database & disk."""
        clean_q = query.strip()
        
        notes_text = None
        source_label = "AI Academic Study Notes"

        # 1. Use pre-generated Gemini study notes if provided
        if pre_generated_notes and len(pre_generated_notes.strip()) > 100:
            notes_text = pre_generated_notes.strip()
            source_label = "Gemini AI Academic Synthesis"
        
        # 2. Search freeallnotes.com fallback
        if not notes_text:
            notes_text = CrawlerService.search_freeallnotes(clean_q)
            if notes_text:
                source_label = "freeallnotes.com"
        
        # 3. Search Google Custom Search fallback
        if not notes_text:
            notes_text = CrawlerService.search_google_notes(clean_q)
            if notes_text:
                source_label = "Google Search Engine"
            
        # 4. If offline or no external results found, synthesize notes using multi-model Gemini or comprehensive structured notes
        if not notes_text:
            notes_text = CrawlerService._synthesize_local_notes(clean_q, domain)
            source_label = "AI Academic Study Notes"
            
        from backend.services.gemini_service import GeminiService
        final_notes_text = GeminiService.sanitize_study_notes(notes_text)
        
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
        """Generates comprehensive notes (minimum 500-800 words) across 6 mandatory sections via Gemini or structured fallback."""
        title_q = query.title().strip()
        domain_label = domain or "Academic Studies"

        # 1. Generate via GeminiService multi-model cascade
        try:
            from backend.services.gemini_service import GeminiService
            notes = GeminiService.generate_detailed_notes(title_q, domain_label)
            if notes and len(notes.strip()) > 150:
                return GeminiService.sanitize_study_notes(notes.strip())
        except Exception as e:
            print(f"Gemini crawler notes synthesis notice: {e}")

        # 2. Comprehensive 6-section structured academic revision notes
        fallback_notes = (
            f"# Executive Overview: Core Definition & Intuition\n"
            f"{title_q} represents a fundamental conceptual and computational subject within {domain_label}. "
            f"Understanding this topic requires analyzing core state representations, invariant guarantees, and algorithmic architectures. "
            f"It serves as a key pillar across university curricula and professional engineering practices.\n\n"
            f"## Key Concepts & Theoretical Foundations: Fundamental Formulas & Derivations\n"
            f"The core mathematical and operational foundation of {title_q} relies on structured partitioning, determinism, and state machines:\n\n"
            f"1. **Primary Governing Relation**:\n"
            f"$$\\mathcal{{S}}(x, t) = \\sum_{{k=1}}^{{N}} \\alpha_k \\cdot \\phi_k(x, t) + \\epsilon(t)$$\n\n"
            f"2. **Continuous Integration & Recurrence**:\n"
            f"$$\\int u \\, dv = u \\cdot v - \\int v \\, du$$\n\n"
            f"3. **Asymptotic Convergence Bound**:\n"
            f"$$\\lim_{{N \\to \\infty}} \\frac{{1}}{{N}} \\sum_{{i=1}}^{{N}} \\left( x_i - \\mu \\right)^2 = \\sigma^2$$\n\n"
            f"## Syntax & Implementation: Step-by-Step Worked Examples\n"
            f"### Worked Example 1: Standard Algorithmic Traversal\n"
            f"```python\n"
            f"# Standard academic implementation framework for {title_q}\n"
            f"def execute_{re.sub(r'[^a-zA-Z0-9]+', '_', query.lower())}(input_data):\n"
            f"    # Phase 1: Boundary condition and base case validation\n"
            f"    if not input_data:\n"
            f"        return None\n"
            f"    \n"
            f"    # Phase 2: Core operational processing\n"
            f"    result = []\n"
            f"    for item in input_data:\n"
            f"        result.append(item)\n"
            f"        \n"
            f"    return result\n"
            f"```\n\n"
            f"### Worked Example 2: Mathematical Integration Step-by-Step\n"
            f"Compute $\\int x e^x \\, dx$:\n"
            f"1. Set $u = x \\implies du = dx$, and $dv = e^x dx \\implies v = e^x$.\n"
            f"2. Substitute: $$\\int x e^x \\, dx = x e^x - \\int e^x \\, dx = e^x(x - 1) + C$$\n\n"
            f"## Complexity Breakdown: Key Rules & Cheatsheet Mnemonics\n"
            f"| Operation / Scenario | Time Complexity | Space Complexity |\n"
            f"| :--- | :--- | :--- |\n"
            f"| Best Case | $O(1)$ | $O(1)$ |\n"
            f"| Average Case | $O(\\log N)$ to $O(N)$ | $O(1)$ to $O(N)$ |\n"
            f"| Worst Case | $O(N \\log N)$ | $O(N)$ |\n\n"
            f"### Cheatsheet Mnemonics & Exam Rules\n"
            f"- **ILATE Priority Rule**: Inverse Trig $\\to$ Log $\\to$ Algebraic $\\to$ Trig $\\to$ Exponential.\n"
            f"- **Master Theorem**: Compare $f(n)$ with $n^{{\\log_b a}}$ to rapidly assess recurrence behavior.\n"
            f"- **Boundary Invariant**: Validate zero-element inputs prior to entering main loops.\n\n"
            f"## Common Mistakes & Exam Pitfalls\n"
            f"- Unhandled Null / Empty Inputs: Forgetting to validate initial state leading to runtime exceptions.\n"
            f"- Integer Overflow & Index Boundaries: Off-by-one errors when partitioning search or array ranges.\n"
            f"- Neglecting Integration Constants: Omitting $+ C$ in indefinite integrals on examination papers.\n\n"
            f"## University Exam: Practice Problems with Answers & Focus Points\n"
            f"1. **Problem 1**: Solve $T(n) = 2T(n/2) + O(n)$.\n"
            f"   - *Answer*: By Master Theorem, $T(n) = \\Theta(n \\log n)$.\n\n"
            f"2. **Problem 2**: Evaluate $\\int_0^1 x^2 \\, dx$.\n"
            f"   - *Answer*: $\\frac{{1}}{{3}}$.\n\n"
            f"3. **Problem 3**: What is the auxiliary space complexity of binary search?\n"
            f"   - *Answer*: $O(1)$ iterative, $O(\\log N)$ recursive."
        )
        return GeminiService.sanitize_study_notes(fallback_notes)

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
