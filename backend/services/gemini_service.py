import json
import re
import httpx
from typing import Dict, Any, List, Optional
from backend import config

_client = None

def get_gemini_client():
    """Returns the singleton server-side Gemini client initialized exclusively from backend environment."""
    global _client
    if _client is None and config.GEMINI_API_KEY and not config.is_gemini_mocked():
        try:
            from google import genai
            _client = genai.Client(api_key=config.GEMINI_API_KEY)
            print("[GeminiService] Initialized server-side Gemini client securely from environment.")
        except Exception as e:
            print(f"[GeminiService] Failed to initialize server-side Gemini client: {e}")
            _client = None
    return _client

def reset_gemini_client():
    global _client
    _client = None

class GeminiService:
    @staticmethod
    def get_client():
        return get_gemini_client()

    @staticmethod
    def clean_search_query(query: str) -> str:
        """Strips conversational noise and filler words to find the core academic search terms."""
        cleaned = query.strip()
        prefixes = [
            r'^(what is|what are|explain|how does|how do|how to|notes on|tutorial on|derivation of|overview of|define|introduction to|details about|information on|summary of|concept of)\s+',
            r'^(can you explain|tell me about|give me notes for|give me information on)\s+'
        ]
        for p in prefixes:
            cleaned = re.sub(p, '', cleaned, flags=re.IGNORECASE).strip()
            
        suffixes = [
            r'\s+(in detail|with examples|step by step|for beginners|exam prep|simplified|easily)$'
        ]
        for s in suffixes:
            cleaned = re.sub(s, '', cleaned, flags=re.IGNORECASE).strip()
            
        return cleaned if len(cleaned) >= 2 else query.strip()

    @staticmethod
    def sanitize_study_notes(text: str) -> str:
        """Strips unwanted ASCII symbols (e.g. ==== or ----) and redundant header blocks
        so the content starts cleanly with '# Executive Overview'.
        """
        if not text or not isinstance(text, str):
            return ""
            
        # 1. Strip raw ASCII decorative borders (===, ---, ___, ~~~, etc.)
        cleaned = re.sub(r'^[=\-~_#*]{4,}\s*$', '', text, flags=re.MULTILINE)
        cleaned = re.sub(r'[=\-]{10,}', '', cleaned)
        
        # 2. Strip redundant plaintext header blocks
        cleaned = re.sub(r'^(#+\s*)?(STUDY NOTES|HANDWRITTEN[A-Z\s]*NOTES|LECTURE\s+NOTES?)[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^>*\s*\*{0,2}(Academic\s+)?Subject\*{0,2}[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^>*\s*\*{0,2}(Date\s+)?Synthesized\*{0,2}[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^>*\s*\*{0,2}Author\*{0,2}[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^>*\s*\*{0,2}Source\*{0,2}[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        cleaned = re.sub(r'^>*\s*\*{0,2}Topic\*{0,2}[:\s].*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # 3. Ensure content starts cleanly with # Executive Overview
        cleaned = cleaned.strip()
        exec_match = re.search(r'(#+\s*Executive Overview[\s\S]*)', cleaned, flags=re.IGNORECASE)
        if exec_match:
            cleaned = exec_match.group(1)
            cleaned = re.sub(r'^#+\s*Executive Overview', '# Executive Overview', cleaned, count=1, flags=re.IGNORECASE)
        else:
            if not cleaned.startswith("#"):
                cleaned = f"# Executive Overview\n\n{cleaned}"
                
        # 4. Collapse consecutive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
        return cleaned

    @staticmethod
    def clean_context_boilerplate(text: str) -> str:
        """Removes annoying boilerplate openers like 'In the context of ...,' from topic overviews."""
        if not text:
            return ""
        pattern = r"^(?:In the (?:context|domain|realm|framework) of|From the (?:perspective|standpoint) of|Within the (?:context|framework|realm) of)\s+(?:(?:B\.Tech|Ph\.D|M\.Tech|[^\n,:;])+)(?:,\s*|:\s*|\s*-\s*)"
        cleaned = re.sub(pattern, "", text.strip(), flags=re.IGNORECASE).strip()
        if cleaned:
            if len(cleaned) > 1 and cleaned[0] in ('"', "'", '“', '‘'):
                cleaned = cleaned[0] + cleaned[1].upper() + cleaned[2:]
            elif cleaned[0].isalpha():
                cleaned = cleaned[0].upper() + cleaned[1:]
        return cleaned

    @staticmethod
    def clean_title_casing(text: str) -> str:
        """Formats title cleanly, repairing Python's .title() apostrophe bugs like Newton'S -> Newton's."""
        if not text:
            return ""
        t = text.strip()
        t = re.sub(r"'S\b", "'s", t)
        t = re.sub(r"’S\b", "’s", t)
        return t

    @staticmethod
    def _detect_academic_domain(query: str) -> str:
        """Categorizes any academic search query into its respective academic discipline."""
        q_low = query.lower()
        if any(w in q_low for w in ["damnum", "damnun", "injuria", "tort", "jurisprudence", "legal maxim", "law of torts", "ipc", "constitution", "ipr", "patent", "copyright", "contract law", "civil liability", "negligence", "defamation"]):
            return "Law, Ethics & Jurisprudence"
        elif any(w in q_low for w in ["fourier", "modulation", "antenna", "vlsi", "cmos", "semiconductor", "op-amp", "opamp", "filter", "dsp", "telecom", "signal", "communication", "sampling", "analog electronics", "digital electronics"]):
            return "Electronics & Communication Engineering"
        elif any(w in q_low for w in ["kcl", "kvl", "kirchhoff", "electrical", "transformer", "induction motor", "power system", "circuit theory", "ohms law", "electromagnetic", "transmission line", "synchronous", "dc machine", "ac machine"]):
            return "Electrical & Electronics Engineering"
        elif any(w in q_low for w in ["thermodynamics", "mechanical", "heat transfer", "fluid mechanics", "kinematics", "cad", "cam", "stress", "strain", "refrigeration", "entropy", "carnot", "bernoulli", "machining", "robotics", "dynamics"]):
            return "Mechanical Engineering"
        elif any(w in q_low for w in ["civil", "structural", "concrete", "rcc", "geotechnical", "soil mechanics", "hydrology", "surveying", "beam", "truss", "foundation", "transportation"]):
            return "Civil & Structural Engineering"
        elif any(w in q_low for w in ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "neural network", "transformer", "regression", "classification", "nlp", "computer vision", "llm", "reinforcement learning"]):
            return "Artificial Intelligence & Data Science"
        elif any(w in q_low for w in [
            "database", "normalization", "bcnf", "sql", "dbms", "dsa", "algorithm", "data structure",
            "array", "arrays", "vector", "linked list", "stack", "queue", "deque", "hash table", "hash map", "hashing",
            "binary search", "tree", "binary tree", "bst", "avl", "red-black", "b-tree", "trie", "heap", "priority queue",
            "graph", "dijkstra", "sorting", "bubble sort", "merge sort", "quicksort", "heap sort", "radix sort",
            "operating system", "os", "network", "python", "java", "c++", "c programming", "programming", "code",
            "compiler", "recursion", "dynamic programming", "greedy", "pointer", "memory management", "cache", "buffer",
            "concurrency", "thread", "process", "deadlock", "paging", "virtual memory"
        ]):
            return "Computer Science & Engineering"
        elif any(w in q_low for w in ["calculus", "integral", "derivative", "matrix", "algebra", "differential", "laplace", "eigen", "probability", "statistics", "vector space", "complex analysis", "number theory"]):
            return "Mathematics & Optimization"
        elif any(w in q_low for w in ["quantum", "newton", "force", "mechanics", "physics", "gravity", "wave", "optics", "relativity", "electrodynamics", "kinematics"]):
            return "Physics & Physical Sciences"
        elif any(w in q_low for w in ["chemistry", "reaction", "acid", "organic", "polymer", "corrosion", "electrochemistry", "biotechnology"]):
            return "Chemistry & Materials Science"
        elif any(w in q_low for w in ["economics", "microeconomics", "macroeconomics", "finance", "accounting", "gdp", "inflation", "market structure", "supply and demand", "monopoly", "business management"]):
            return "Economics & Management Studies"
        elif any(w in q_low for w in ["biology", "genetics", "dna", "rna", "organism", "cellular", "physiology", "biomedical"]):
            return "Biological & Life Sciences"
        else:
            return "Academic Curriculum & Higher Education"

    @staticmethod
    def map_topic_to_careers(query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        career_map = [
            {
                "role": "Legal Analyst & Compliance Consultant",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["damnum", "damnun", "injuria", "tort", "law", "legal", "jurisprudence", "ipr", "patent", "ethics", "contract", "liability"],
                "importance": "Essential for corporate legal compliance, tort liability assessment, intellectual property protection, and regulatory governance."
            },
            {
                "role": "Quantitative Analyst & Financial Modeling Specialist",
                "roadmap_url": "https://roadmap.sh/datascience",
                "keywords": ["economics", "finance", "accounting", "gdp", "market", "microeconomics", "macroeconomics", "inflation"],
                "importance": "Crucial for econometric modeling, valuation analysis, risk assessment, and market resource optimization."
            },
            {
                "role": "Frontend Developer",
                "roadmap_url": "https://roadmap.sh/frontend",
                "keywords": ["html", "css", "javascript", "js", "typescript", "ts", "react", "vue", "angular", "tailwind", "bootstrap", "sass", "webpack", "vite", "dom", "frontend", "web dev", "next.js", "nextjs", "nuxt", "svelte"],
                "importance": "Frontend developers design and implement user interfaces. This topic is fundamental for building, styling, or managing client-side applications."
            },
            {
                "role": "Backend Developer",
                "roadmap_url": "https://roadmap.sh/backend",
                "keywords": ["python", "node", "nodejs", "express", "django", "fastapi", "flask", "ruby", "rails", "php", "laravel", "java", "spring", "c#", "asp.net", "go", "golang", "api", "rest", "graphql", "backend", "server", "authentication", "jwt", "oauth"],
                "importance": "Backend developers focus on server logic, APIs, and scalable distributed architectures."
            },
            {
                "role": "Database Architect & Data Platform Engineer",
                "roadmap_url": "https://roadmap.sh/backend",
                "keywords": ["database", "normalization", "bcnf", "3nf", "2nf", "1nf", "sql", "nosql", "postgres", "mysql", "mongodb", "redis", "dbms", "indexing", "acid", "transaction", "concurrency"],
                "importance": "Critical for high-performance schema design, relational normalization, ACID compliance, and low-latency storage systems."
            },
            {
                "role": "Electronics & Communications Systems Engineer",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["fourier", "signal", "modulation", "antenna", "vlsi", "cmos", "semiconductor", "op-amp", "opamp", "filter", "dsp", "telecom", "ece", "sampling", "frequency domain"],
                "importance": "Core to DSP architectures, telecommunication networks, RF design, and next-generation VLSI chip manufacturing."
            },
            {
                "role": "Electrical & Power Systems Engineer",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["kcl", "kvl", "kirchhoff", "electrical", "transformer", "induction motor", "power system", "grid", "voltage", "current", "circuit theory", "transmission line", "synchronous"],
                "importance": "Central to grid infrastructure, electrical machinery, high-voltage transmission, and renewable power systems."
            },
            {
                "role": "Mechanical & Thermal Systems Engineer",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["thermodynamics", "mechanical", "heat transfer", "fluid mechanics", "kinematics", "cad", "cam", "stress", "strain", "refrigeration", "entropy", "carnot", "bernoulli", "machining", "robotics"],
                "importance": "Essential for energy conversion, HVAC design, aerodynamic modeling, and advanced mechanical systems."
            },
            {
                "role": "Civil & Structural Infrastructure Engineer",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["civil", "structural", "concrete", "rcc", "geotechnical", "soil mechanics", "hydrology", "surveying", "beam", "truss", "foundation", "transportation"],
                "importance": "Fundamental to infrastructure planning, structural stability under load dynamics, and urban geotechnical engineering."
            },
            {
                "role": "DevOps & Cloud Engineer",
                "roadmap_url": "https://roadmap.sh/devops",
                "keywords": ["docker", "kubernetes", "k8s", "linux", "bash", "shell", "git", "ci/cd", "cicd", "jenkins", "github actions", "aws", "azure", "gcp", "terraform", "ansible", "nginx", "apache", "prometheus", "grafana", "devops", "cloud", "monitoring"],
                "importance": "DevOps engineers manage automated delivery pipelines, container clusters, cloud platforms, and system reliability."
            },
            {
                "role": "Data Scientist & Analytics Architect",
                "roadmap_url": "https://roadmap.sh/datascience",
                "keywords": ["data science", "datascience", "machine learning", "ml", "pandas", "numpy", "scikit-learn", "statistics", "probability", "data visualization", "matplotlib", "seaborn", "scipy"],
                "importance": "Data Scientists extract actionable patterns from structured and unstructured data using statistical modeling and mathematical analysis."
            },
            {
                "role": "AI Research & Systems Engineer",
                "roadmap_url": "https://roadmap.sh/ai-engineer",
                "keywords": ["ai", "artificial intelligence", "deep learning", "neural network", "transformer", "llm", "gpt", "gemini", "prompt engineering", "openai", "nlp", "computer vision", "vector database", "chromadb", "langchain", "rag", "quantum computing", "qubit"],
                "importance": "AI Engineers build, fine-tune, and deploy state-of-the-art neural architectures and advanced foundation model pipelines."
            },
            {
                "role": "Computer Science & Systems Architect",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["data structures", "algorithms", "array", "arrays", "vector", "dijkstra", "sorting", "searching", "graph", "tree", "linked list", "binary search", "big o", "complexity", "operating system", "networks", "tcp", "udp", "cpu", "memory", "compile", "recursion", "stack", "queue", "hash table", "heap", "trie", "dynamic programming"],
                "importance": "Computer Science fundamentals form the basis of software systems, optimal algorithms, and distributed computing."
            }
        ]

        matched = []
        for item in career_map:
            for kw in item["keywords"]:
                if re.search(rf"\b{re.escape(kw)}\b", q):
                    matched.append({
                        "role": item["role"],
                        "roadmap_url": item["roadmap_url"],
                        "importance": item["importance"]
                    })
                    break
                
        if not matched:
            domain = GeminiService._detect_academic_domain(query)
            if "Engineering" in domain or "Curriculum" in domain:
                role_title = "Computer Science & Engineering Systems Specialist"
            else:
                role_title = f"{domain} Specialist & Systems Engineer"
            matched.append({
                "role": role_title,
                "roadmap_url": "https://roadmap.sh/computer-science",
                "importance": f"Mastering '{query}' builds systematic analytical problem-solving skills, quantitative mathematical intuition, and foundational principles applicable across {domain}."
            })
            
        return matched

    @staticmethod
    def _clean_and_parse_llm_json(raw_text: str) -> Dict[str, Any]:
        """Safely extracts and parses JSON returned by the LLM, handling markdown code fences
        and unescaped LaTeX backslashes without syntax errors.
        """
        if not raw_text or not isinstance(raw_text, str):
            return {}
        text = raw_text.strip()
        if text.startswith("```"):
            m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL | re.IGNORECASE)
            if m:
                text = m.group(1).strip()

        # 1. First attempt: standard strict parse
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2. Second attempt: escape LaTeX keywords and invalid JSON escape sequences
        try:
            latex_conflict_pattern = re.compile(r'\\(text|frac|theta|times|tau|to|tan|begin|nabla|bf|bar|beta|binom|bmod|bot|bullet|ne|nu|nabla)')
            text_fixed = latex_conflict_pattern.sub(r'\\\\\1', text)
            pattern = re.compile(r'\\(?![/u"bfnrt\\])')
            text_fixed = pattern.sub(r'\\\\', text_fixed)
            return json.loads(text_fixed)
        except Exception:
            pass

        # 3. Third attempt: aggressively double every single backslash that isn't already escaped
        try:
            aggressive = re.sub(r'\\(?!\\)', r'\\\\', text)
            return json.loads(aggressive)
        except Exception:
            pass

        # 4. Fourth attempt: robust regex key-value extraction for essential academic fields
        extracted = {}
        for key in ["topic", "category", "overview", "theoretical_foundations", "core_formulations", "ai_evaluation", "did_you_know", "study_notes", "difficulty_score", "difficulty_level"]:
            m_field = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
            if m_field:
                val = m_field.group(1)
                val = val.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                extracted[key] = val
            elif key in ["difficulty_score"]:
                m_num = re.search(r'"' + key + r'"\s*:\s*([0-9.]+)', text)
                if m_num:
                    extracted[key] = float(m_num.group(1))

        if extracted.get("overview") or extracted.get("topic"):
            return extracted

        return {}

    @staticmethod
    def ensure_math_delimiters(text: str) -> str:
        """Enforces clean LaTeX math delimiter wrapping and formatting on academic text.
        Guarantees:
        1. Literal '\\n' escaped sequences are converted to actual newlines.
        2. Any C/Python code snippets without markdown code fences are wrapped in ```...```.
        3. Standalone mathematical formulas with LaTeX commands (\\text, \\frac, \\times, etc.)
           are wrapped in $$ ... $$, and inline Big-O / variables are wrapped in $ ... $.
        """
        if not text or not isinstance(text, str):
            return ""
        
        # 1. Unescape literal \n
        clean = text.replace('\\n', '\n')
        
        # 2. Auto-fence code snippets if present
        if '```' not in clean and any(k in clean for k in ['malloc(', 'sizeof(', 'int main', 'def ', 'class ', '#include']):
            clean = re.sub(
                r'((?:(?:int|char|float|double|void|\*|struct)\s+[\w*]+\s*=|if\s*\([^)]+\)\s*\{|malloc\()[^`]+?(?:;\s*\}|;))',
                r'\n```c\n\1\n```\n',
                clean
            )
        
        # 3. Format standalone formulas and equations
        latex_cmds = [r'\\text\{', r'\\frac\{', r'\\mathcal\{', r'\\pmod', r'\\times', r'\\cdot', r'\\sum', r'\\int', r'\\sqrt', r'\\alpha', r'\\beta', r'\\theta', r'\\Theta', r'\\Omega']
        has_latex = any(re.search(cmd, clean) for cmd in latex_cmds)
        
        if has_latex:
            lines = clean.split('\n')
            res_lines = []
            in_code = False
            for line in lines:
                trimmed = line.strip()
                if trimmed.startswith('```'):
                    in_code = not in_code
                    res_lines.append(line)
                    continue
                if in_code or not trimmed:
                    res_lines.append(line)
                    continue
                
                # Check if already wrapped in $$ or $
                if (trimmed.startswith('$$') and trimmed.endswith('$$')) or (trimmed.startswith('$') and trimmed.endswith('$')):
                    res_lines.append(line)
                    continue
                
                # Check if line contains standalone LaTeX equation without dollar delimiters
                if any(re.search(cmd, trimmed) for cmd in latex_cmds):
                    if '$' not in trimmed:
                        colon_idx = trimmed.find(':')
                        if colon_idx != -1 and any(re.search(cmd, trimmed[colon_idx:]) for cmd in latex_cmds):
                            prefix = trimmed[:colon_idx+1]
                            eq = trimmed[colon_idx+1:].strip()
                            res_lines.append(prefix)
                            res_lines.append(f"$${eq}$$")
                            continue
                        elif '=' in trimmed or '\\\\' in trimmed or trimmed.startswith('\\text') or trimmed.startswith('A['):
                            if '\\\\' in trimmed:
                                for sub in trimmed.split('\\\\'):
                                    sub = sub.strip()
                                    if sub:
                                        res_lines.append(f"$${sub}$$")
                                continue
                            else:
                                res_lines.append(f"$${trimmed}$$")
                                continue
                    else:
                        # Wrap un-delimited \mathcal{O}(...) with $\mathcal{O}(...)$
                        line = re.sub(r'(?<!\$)\\mathcal\{[A-Za-z]\}\([a-zA-Z0-9+\-* /]+\)(?!\$)', r'$\g<0>$', line)
                res_lines.append(line)
            clean = '\n'.join(res_lines)

        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
        return clean


    @staticmethod
    def build_quick_example(topic: str, category: str, core_formulations: str = "", overview: str = "", llm_example: Optional[Dict[str, Any]] = None, lang: str = "english") -> Dict[str, Any]:
        """Generates a clean, friendly, and intuitive everyday real-life analogy or walkthrough.
        Strictly NOT formatted as code or dense jargon. Easy for any student to understand.
        Supports both English and natural Hinglish.
        """
        clean_topic = GeminiService.clean_title_casing((topic or "Academic Topic").strip().title())
        t_lower = clean_topic.lower()
        cat_lower = (category or "").lower()
        is_hinglish = (lang or "").strip().lower() == "hinglish"

        def _clean_str(val: Any) -> str:
            if not val or not isinstance(val, str):
                return ""
            cleaned = re.sub(r'```[a-zA-Z0-9_-]*\n([\s\S]*?)```', r'\1', val).strip()
            return GeminiService.ensure_math_delimiters(cleaned)

        def _normalize_use_cases(raw_cases: Any) -> List[Dict[str, str]]:
            cases = []
            if isinstance(raw_cases, list):
                for item in raw_cases:
                    if isinstance(item, dict):
                        t = (item.get("title") or item.get("name") or "").strip()
                        imp = (item.get("impact") or item.get("system") or item.get("role") or "Everyday Application").strip()
                        desc = (item.get("description") or item.get("details") or item.get("desc") or "").strip()
                        if t or desc:
                            cases.append({
                                "title": _clean_str(t or "Real-World Application"),
                                "impact": _clean_str(imp),
                                "description": _clean_str(desc)
                            })
                    elif isinstance(item, str) and item.strip():
                        parts = item.split(":", 1)
                        if len(parts) == 2:
                            cases.append({
                                "title": _clean_str(parts[0].strip()),
                                "impact": "Real-World Use",
                                "description": _clean_str(parts[1].strip())
                            })
                        else:
                            cases.append({
                                "title": "Practical Application",
                                "impact": "Everyday Tech",
                                "description": _clean_str(item.strip())
                            })
            return cases[:4]

        # Check if LLM example exists and is NOT a generic placeholder
        is_generic_placeholder = False
        if llm_example and isinstance(llm_example, dict):
            scen = (llm_example.get("scenario") or "").lower()
            if any(k in scen for k in ["multidisciplinary team must systematically evaluate", "foundational variables, operational constraints"]):
                is_generic_placeholder = True

        if llm_example and isinstance(llm_example, dict) and not is_generic_placeholder:
            scenario = _clean_str(llm_example.get("scenario"))
            breakdown = _clean_str(llm_example.get("breakdown"))
            takeaway = _clean_str(llm_example.get("takeaway") or llm_example.get("key_takeaway"))
            title = _clean_str(llm_example.get("title") or f"{clean_topic} Real-World Analogy")
            badge = _clean_str(llm_example.get("badge") or "Everyday Real-Life Example")
            
            raw_cases = llm_example.get("use_cases") or llm_example.get("applications")
            use_cases = _normalize_use_cases(raw_cases)

            raw_tradeoffs = llm_example.get("tradeoffs") or {}
            tradeoffs = {}
            if isinstance(raw_tradeoffs, dict):
                adv = _clean_str(raw_tradeoffs.get("advantages") or raw_tradeoffs.get("pros"))
                dis = _clean_str(raw_tradeoffs.get("disadvantages") or raw_tradeoffs.get("cons") or raw_tradeoffs.get("limitations"))
                if adv or dis:
                    tradeoffs = {"advantages": adv, "disadvantages": dis}

            if scenario or breakdown:
                if not use_cases:
                    use_cases = GeminiService._synthesize_domain_use_cases(clean_topic, category, lang=lang)
                return {
                    "title": title,
                    "badge": badge,
                    "scenario": scenario,
                    "breakdown": breakdown,
                    "use_cases": use_cases,
                    "takeaway": takeaway or f"Shows how {clean_topic} operates simply and effectively in everyday scenarios.",
                    "tradeoffs": tradeoffs,
                    "example_text": f"{scenario}\n\n{breakdown}\n\nKey Takeaway: {takeaway}".strip()
                }

        # 2. Topic-specific crystal-clear, clean, and friendly real-world analogies
        # Array & Vector
        if any(w in t_lower for w in ["array", "arrays", "vector", "dynamic array", "contiguous"]):
            if is_hinglish:
                return {
                    "title": "Apartment Building ke Numbered Mailboxes",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Imagine karo ek apartment building ka lobby jisme 100 mailboxes ek seedhi row me lage hain, numbered 1 se 100. Har mailbox ka size exactly same hai aur sab ek ke baad ek continuous sequence me physically chipke hue hain.",
                    "breakdown": """1. **Instant Direct Access ($O(1)$)**: Agar postman ke pass Flat 42 ka letter hai, to use box 1, 2, 3 check karne ki zarurat nahi hai. Wo directly box 42 pe jaata hai aur letter daal deta hai. Kisi bhi mailbox ko access karna split-second leta hai.
2. **Contiguous (Side-by-Side) Order**: Kyunki saare boxes continuous line me hain, aapko agle box ki exact location pehle se pata hoti hai.
3. **The Limitation (Fixed Size & Shifting)**: Agar flat 10 aur 11 ke beech naya flat ban jaye, to beech me naya box nahi ghusa sakte. 11 se 100 tak ke saare boxes ko ek space aage shift karna padega!""",
                    "use_cases": [
                        {
                            "title": "Smartphone Photo Gallery",
                            "impact": "Direct Index Navigation",
                            "description": "Jab aap photo album me thumbnail #20 pe tap karte hain, phone pehle 19 photos scan kiye bina directly photo #20 open kar deta hai."
                        },
                        {
                            "title": "Cinema & Flight Seat Booking",
                            "impact": "Row & Seat Direct Lookup",
                            "description": "Booking engine 'Row 4, Seat 12' ko instant time me locate karta hai kyunki cinema seats 2D array grid me arranged hote hain."
                        }
                    ],
                    "takeaway": "Array bilkul numbered lockers ya mailboxes ki tarah kaam karta hai: index pata ho to zero time me direct jump milta hai.",
                    "tradeoffs": {
                        "advantages": "Index number se instant O(1) random access; simple aur fast memory layout.",
                        "disadvantages": "Middle me insertion/deletion pe O(n) element shifting karni padti hai."
                    },
                    "example_text": "Numbered Mailboxes: Index number se O(1) instant access milta hai, par middle insertion ke liye elements shift karne padte hain."
                }
            return {
                "title": "Numbered Apartment Mailboxes in a Lobby",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "Imagine an apartment building lobby with a neat wall of 100 mailboxes arranged in a single row, numbered 1 to 100. Every mailbox is identical in size and sits directly next to its neighbor.",
                "breakdown": """1. **Instant Direct Access ($O(1)$)**: If the postman has a letter for Apartment 42, he doesn't check box 1, then box 2, then box 3. He walks straight to box 42 and drops the letter in. Finding any mailbox takes the exact same split-second, whether it is #2 or #99.
2. **Side-by-Side (Contiguous) Order**: Because all mailboxes sit in one continuous line, you always know where the next box is without checking a map or following clues.
3. **The Limitation (Fixed Size & Shifting)**: If a new apartment is built between 10 and 11, the landlord cannot just squeeze a mailbox into the middle. Every mailbox from 11 to 100 must be pushed over by one space, or the landlord must build a completely new, larger wall of mailboxes!""",
                "use_cases": [
                    {
                        "title": "Smartphone Photo Gallery",
                        "impact": "Direct Numbered Navigation",
                        "description": "When you tap thumbnail #20 in your photo album, your phone jumps straight to photo #20 instantly without needing to scan through the first 19 photos."
                    },
                    {
                        "title": "Cinema & Flight Seat Booking",
                        "impact": "Row & Seat Direct Lookup",
                        "description": "Booking systems locate 'Row 4, Seat 12' in a split-second because movie theater and airplane seats are arranged in a fixed grid like a 2D array."
                    },
                    {
                        "title": "Video Game Top 10 High Scores",
                        "impact": "Ordered Leaderboard Slots",
                        "description": "Games store top player scores in fixed positions from rank 1 to 10, making it effortless to display or update the leaderboard."
                    },
                    {
                        "title": "Music & Video Streaming Buffers",
                        "impact": "Smooth Playback Queue",
                        "description": "Apps like Spotify and YouTube load the next 30 seconds of audio into a sequential row of sound chunks so your music never stutters."
                    }
                ],
                "takeaway": "An array works just like numbered lockers or mailboxes: if you know the number, you can jump straight to it in zero time.",
                "tradeoffs": {
                    "advantages": "Instant access to any item using its index number; simple and organized memory layout.",
                    "disadvantages": "Adding or removing an item in the middle requires shifting everything behind it; resizing requires creating a bigger array."
                },
                "example_text": "Numbered Apartment Mailboxes: Knowing the box number allows instant O(1) access to any mailbox, but adding a new box in the middle requires shifting all subsequent boxes."
            }

        # Linked List
        if any(w in t_lower for w in ["linked list", "inversion", "reverse linked list", "doubly linked"]):
            if is_hinglish:
                return {
                    "title": "Treasure Hunt ke Chhupe Hue Clue Cards",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Imagine karo ek exciting campus treasure hunt. Aap Location A se start karte ho. Aapke paas saari locations ka pehle se koi map nahi hai. Jab aap Location A pahunchte ho, to wahan ek clue card milta hai: 'Agla clue library bench ke neeche chhupa hai (Location B).' Location B par note aapko cafeteria bhej deta hai.",
                    "breakdown": """1. **Clues Kahin Bhi Ho Sakte Hain (Flexible Memory)**: Mailboxes ki tarah clues ko ek row me chipkaane ki zarurat nahi hoti. Har clue card ke paas apna message hota hai aur agle spot ka address (Pointer) hota hai.
2. **Kahin Bhi Insert ya Delete Karna Super Easy**: Agar organizer library aur cafeteria ke beech ek naya clue add karna chahe, to poora campus dobara nahi banana padta. Bas library wale note ko naye spot par point kar do aur naye spot ko cafeteria par ($O(1)$ Pointer update).
3. **The Limitation (Direct Jump Nahi Milta)**: Agar koi pooche ki 'Clue #4 kahan hai?', to aap directly jump nahi kar sakte. Aapko Clue 1 se start karke chain link-by-link follow karni padegi ($O(n)$ traversal).""",
                    "use_cases": [
                        {
                            "title": "Music Playlist 'Play Next'",
                            "impact": "Seamless Track Queuing",
                            "description": "Har song agle song ko point karta hai. Jab aap 'Play Next' me song add karte ho, to Spotify music files move kiye bina bas Pointer arrows re-link kar deta hai."
                        },
                        {
                            "title": "Web Browser History (Back / Forward)",
                            "impact": "Page Link Navigation",
                            "description": "Aap jo bhi web page visit karte ho wo pichhle page se link hota hai, jisse aap aage-peeche smoothly navigate kar sakte ho."
                        },
                        {
                            "title": "Undo / Redo in Text Editors",
                            "impact": "Chain of Actions",
                            "description": "Word processors har sentence edit ko pichhle edit se link karte hain taaki Ctrl+Z dabane par ek-ek karke pichhli state wapas aa sake."
                        },
                        {
                            "title": "Operating System Memory Allocation",
                            "impact": "Reusing Scattered RAM",
                            "description": "Computer RAM ke scattered free chunks ko aapas me link karke apps ko run karta hai jab memory fragmented hoti hai."
                        }
                    ],
                    "takeaway": "Linked List ek treasure hunt chain ki tarah hai: kahin bhi naye links aasani se add ya remove kar sakte hain, lekin kisi element ko dhoondhne ke liye poori chain walk karni padti hai.",
                    "tradeoffs": {
                        "advantages": "Bina doosre elements ko shift kiye O(1) insertion aur deletion; size pehle se fix karne ki zarurat nahi hoti.",
                        "disadvantages": "Index number se direct jump nahi kar sakte; search karne ke liye head se shuru karke O(n) walk karna padta hai."
                    },
                    "example_text": "Treasure Hunt Clues: Har clue agle location ko point karta hai, jisse flexible additions possible hain par link-by-link follow karna padta hai."
                }
            return {
                "title": "A Treasure Hunt with Hidden Clue Cards",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "Imagine an exciting treasure hunt across a campus. You start at Location A. You don't have a map of all locations in advance. Instead, when you arrive at Location A, you open a clue card that says: 'The next clue is hidden under the library bench (Location B).' At Location B, the note sends you to the cafeteria.",
                "breakdown": """1. **Clues Can Be Anywhere (Flexible Memory)**: Unlike mailboxes that must be glued together in a row, treasure hunt clues can be placed anywhere in town. Each clue card stores its own message plus the address of where to go next (a pointer).
2. **Super Easy to Insert or Remove**: If the organizer wants to add a surprise clue between the library and cafeteria, they don't rebuild the campus. They simply rewrite the note at the library to point to the new spot, and have the new spot point to the cafeteria.
3. **The Limitation (No Direct Jumping)**: If someone asks, 'What is clue #4?', you cannot jump straight to it. You must start at Clue 1, follow the note to Clue 2, then Clue 3, until you reach Clue 4.""",
                "use_cases": [
                    {
                        "title": "Music Playlist 'Play Next'",
                        "impact": "Seamless Track Queuing",
                        "description": "Each song points to the next track. When you add a song to 'Play Next', Spotify just re-links the arrows without moving the music files."
                    },
                    {
                        "title": "Web Browser History (Back / Forward)",
                        "impact": "Page Link Navigation",
                        "description": "Each web page you visit links back to the previous page you came from, letting you navigate backward and forward smoothly."
                    },
                    {
                        "title": "Undo / Redo in Text Editors",
                        "impact": "Chain of Actions",
                        "description": "Word processors link each sentence edit to the previous edit so pressing Ctrl+Z steps backward through your edits one-by-one."
                    },
                    {
                        "title": "Operating System Memory Allocation",
                        "impact": "Reusing Scattered RAM",
                        "description": "Your computer links together scattered empty chunks of memory so apps can open even when free memory is broken into pieces."
                    }
                ],
                "takeaway": "A linked list is like a chain of treasure clues: you can easily add or remove links anywhere, but you have to walk the chain link-by-link to find anything.",
                "tradeoffs": {
                    "advantages": "Effortless insertion and deletion without moving other items; grows as much as you need without pre-allocated limits.",
                    "disadvantages": "You cannot jump directly to an item by number; finding something requires walking from the very beginning."
                },
                "example_text": "Treasure Hunt Clues: Each clue points to the next location, allowing flexible additions anywhere, but requiring you to follow clues step-by-step."
            }

        # Stack
        if any(w in t_lower for w in ["stack", "lifo", "call stack"]):
            if is_hinglish:
                return {
                    "title": "Cafeteria me Clean Plates Ka Stack",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Cafeteria me dinner plates ke dher ke baare me socho. Jab dishwasher se saaf plates aati hain, to staff unhe dher ke sabse upar (top) par rakh deta hai. Jab students khana lene aate hain, to wo sabse upar wali plate uthate hain.",
                    "breakdown": """1. **Last-In, First-Out (LIFO)**: Jo plate sabse aakhir me top par rakhi gayi thi, wahi plate sabse pehle uthayi jaati hai. Sabse neeche wali plate tabhi use hogi jab upar ki saari plates khatam ho jayein.
2. **Push aur Pop Ek Second Me ($O(1)$)**: Plate ko top par rakhna **Push** kehlata hai. Top se plate uthana **Pop** kehlata hai. Dono operations instant $O(1)$ time me hote hain.
3. **Middle Se Pull Karna Allowed Nahi**: Aap stack ke beech ya neeche se plate nahi kheench sakte, warna poora stack girne ka risk hota hai!""",
                    "use_cases": [
                        {
                            "title": "Web Browser 'Back' Button",
                            "impact": "History Reversal",
                            "description": "Har visited page history stack ke top par push hota hai. Back button dabane par current page pop ho jata hai aur pichhla page samne aata hai."
                        },
                        {
                            "title": "Word Processor Undo (Ctrl + Z)",
                            "impact": "Action Rollback",
                            "description": "Har keystroke ya formatting change undo stack me push hoti hai. Ctrl+Z dabane par most recent action pop hokar revert ho jata hai."
                        },
                        {
                            "title": "Math Parentheses Matching",
                            "impact": "Syntax Validation",
                            "description": "Compilers open brackets `(` ko stack me push karte hain aur closing bracket `)` aane par pop karke check karte hain ki pairing sahi hai ya nahi."
                        },
                        {
                            "title": "Function Call Stack in Programming",
                            "impact": "Call Stack Execution",
                            "description": "Jab ek function doosre function ko call karta hai, to OS unhe stack par push karta hai aur innermost function khatam hone ke baad return karta hai."
                        }
                    ],
                    "takeaway": "Stack 'jo aakhir me aaya, wo sabse pehle jayega' (LIFO) rule par kaam karta hai—hamesha top element hi access hota hai.",
                    "tradeoffs": {
                        "advantages": "Push aur Pop operations extremely fast O(1) hote hain; undo aur backtracking ke liye perfect structure hai.",
                        "disadvantages": "Sirf top element dekh aur access kar sakte hain; neeche dabee puraani values par directly jump nahi kiya ja sakta."
                    },
                    "example_text": "Cafeteria Plate Stack: Last added plate sabse pehle nikali jaati hai (LIFO), jisse instant O(1) push aur pop milta hai."
                }
            return {
                "title": "A Stack of Clean Plates in a Cafeteria",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "Think of a tall pile of dinner plates in a cafeteria. When clean plates come out of the dishwasher, the staff places them on top of the pile. When students arrive to eat, they take the plate from the very top.",
                "breakdown": """1. **Last-In, First-Out (LIFO)**: The very last plate placed on top is the first plate taken by a student. The plate at the very bottom will only be used once all the plates above it are taken.
2. **Push and Pop in One Second**: Adding a plate to the top is called **Push**. Taking the top plate off is called **Pop**. Both actions take just one quick second ($O(1)$).
3. **No Pulling from the Middle**: You cannot safely pull out a plate from the middle or bottom of the pile without risking the whole stack crashing down!""",
                "use_cases": [
                    {
                        "title": "Web Browser 'Back' Button",
                        "impact": "History Reversal",
                        "description": "Every page you visit is placed on top of a history stack. Clicking 'Back' pops the current page off and reveals the page right beneath it."
                    },
                    {
                        "title": "Word Processor Undo (Ctrl + Z)",
                        "impact": "Action Rollback",
                        "description": "Every keystroke or formatting change is pushed onto an undo stack. Pressing Ctrl+Z pops the most recent action off to restore the previous state."
                    },
                    {
                        "title": "Math Formula Parentheses Checker",
                        "impact": "Syntax Validation",
                        "description": "Compilers push open brackets `(` onto a stack and pop them when a closing bracket `)` appears to make sure brackets match correctly."
                    },
                    {
                        "title": "Computer Program Function Calls",
                        "impact": "Call Stack Execution",
                        "description": "When a computer program runs a function inside another function, it stacks them up and finishes the innermost function first before returning."
                    }
                ],
                "takeaway": "A stack operates on 'last come, first served'—the last item you place on top is always the first item you get back.",
                "tradeoffs": {
                    "advantages": "Extremely fast push and pop operations; perfect for backtracking and reversing steps.",
                    "disadvantages": "You can only see and touch the top item; you cannot jump directly to older items buried underneath."
                },
                "example_text": "Cafeteria Plate Stack: Plates are pushed onto the top and popped from the top, ensuring the last plate added is always the first one taken."
            }

        # Queue
        if any(w in t_lower for w in ["queue", "fifo", "message broker"]):
            if is_hinglish:
                return {
                    "title": "Ice Cream Counter par Khade Customers ki Line",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Ek ice cream parlor ki picture imagine karo. Customers counter ke aage ek seedhi line me khade hote hain. Jo customer pehle aata hai use pehle ice cream milti hai, aur naye log line ke end me lagte hain.",
                    "breakdown": """1. **First-In, First-Out (FIFO)**: Jis customer ne sabse zyada wait kiya hai use pehle service milti hai. Line tod kar aage aana strictly allowed nahi hai!
2. **Enqueue aur Dequeue ($O(1)$)**: Line ke end me judna **Enqueue** kehlata hai. Ice cream lekar counter se nikalna **Dequeue** kehlata hai.
3. **Fairness aur System Protection**: Agar 50 log ek saath aa jayein, to line system me discipline banaye rakhti hai taaki server bina crash hue steady speed par order process kare.""",
                    "use_cases": [
                        {
                            "title": "Office Shared Printer",
                            "impact": "Fair Document Printing",
                            "description": "Jab kayi log ek saath 'Print' dabate hain, to printer Document 1 pehle aur Document 2 baad me print karta hai, exact arrival order ke mutabiq."
                        },
                        {
                            "title": "Customer Support Call Waiting",
                            "impact": "Orderly Phone Routing",
                            "description": "'Aap line me caller number 3 hain; kripya hold karein.' Call centers phone calls ko FIFO queue ke mutabiq answer karte hain."
                        },
                        {
                            "title": "Food Delivery Apps (Swiggy / Zomato)",
                            "impact": "Kitchen Order Queue",
                            "description": "Restaurant kitchen me orders ek queue me aate hain taaki chef pehle aaye order ko pehle prepare kare."
                        },
                        {
                            "title": "Concert Ticket Booking (BookMyShow)",
                            "impact": "Traffic Surge Buffer",
                            "description": "High-traffic ticket sales ke waqt website users ko virtual queue me daal deti hai taaki server overload se crash na ho."
                        }
                    ],
                    "takeaway": "Queue ek fair waiting line hai jo ensure karti hai ki kaam usi order me handle hon jisme wo arrive hue the (First-In, First-Out).",
                    "tradeoffs": {
                        "advantages": "Completely fair FIFO order; traffic spike aane par system ko shock absorber ki tarah crash hone se bachata hai.",
                        "disadvantages": "Line me aage khade tasks complete hone tak wait karna padta hai; pehla task slow ho to pichhle sabhi delay ho jaate hain."
                    },
                    "example_text": "Ice Cream Line: Customers line ke end me judte hain aur front se serve hote hain, ensuring strict FIFO order."
                }
            return {
                "title": "A Line of Customers at an Ice Cream Counter",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "Picture an ice cream shop on a warm summer evening. Customers form a single line in front of the counter. The person who arrives first is served first, while newcomers join the back of the line.",
                "breakdown": """1. **First-In, First-Out (FIFO)**: The customer who has waited the longest is served first. Cutting into the front of the line is strictly forbidden!
2. **Enqueue and Dequeue**: Joining the back of the line is called **Enqueue**. Leaving the counter after receiving your ice cream is called **Dequeue**.
3. **Fairness & Preventing Chaos**: If 50 people show up all at once, the line keeps order and lets the ice cream scooper serve customers steadily without getting overwhelmed.""",
                "use_cases": [
                    {
                        "title": "Shared Office Printer",
                        "impact": "Fair Document Printing",
                        "description": "When multiple people click 'Print' at the same time, the printer prints Document 1 first, then Document 2, in the exact order they were sent."
                    },
                    {
                        "title": "Customer Support Call Waiting",
                        "impact": "Orderly Phone Routing",
                        "description": "'You are caller number 3 in line; please hold.' Call centers answer phone calls in the exact order customers dialed in."
                    },
                    {
                        "title": "Food Delivery Apps (Swiggy / Zomato)",
                        "impact": "Kitchen Order Queue",
                        "description": "Orders arrive in a queue at the restaurant kitchen so chefs prepare the oldest ticket first before moving to newly placed orders."
                    },
                    {
                        "title": "Concert Ticket Sales (BookMyShow)",
                        "impact": "Traffic Surge Buffer",
                        "description": "During massive ticket sales, websites place fans into a digital waiting queue to protect servers from crashing under sudden traffic."
                    }
                ],
                "takeaway": "A queue is a fair waiting line that ensures things are handled in the exact order they arrived (first-come, first-served).",
                "tradeoffs": {
                    "advantages": "Completely fair and orderly; acts as a shock absorber preventing systems from crashing when traffic spikes.",
                    "disadvantages": "You must wait for everyone ahead of you to finish; if the first task takes a long time, everything behind is delayed."
                },
                "example_text": "Ice Cream Shop Line: Customers join at the back and are served from the front, ensuring strict first-come, first-served order."
            }

        # Tree & Binary Search Tree & B-Tree
        if any(w in t_lower for w in ["tree", "binary tree", "bst", "b-tree", "avl", "red-black"]):
            if is_hinglish:
                return {
                    "title": "Cookbook ka Table of Contents aur File Folders",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Maan lo aap 1,000 pages ki recipe book me 'Chocolate Chip Cookies' dhoondh rahe ho. Aap saare 1,000 pages ek-ek karke nahi palatoge! Aap Table of Contents khologe: Desserts $\\to$ Baked Goods $\\to$ Cookies $\\to$ Chocolate Chip.",
                    "breakdown": """1. **Hierarchical Branching**: Ek lambi flat list ke bajay information branches me failti hai: Root $\\to$ Categories $\\to$ Subcategories $\\to$ Specific Items.
2. **Search Half Ho Jaata Hai (Logarithmic $O(\\log n)$)**: Binary Search Tree me har left ya right decision aadhe options ko eliminate kar deta hai. Sirf 10 steps me aap 1,000 me se 1 exact item dhoondh sakte ho!
3. **Natural Organization**: Related items apne common parent ke under grouped rehte hain, jisse navigation fast aur structured ho jata hai.""",
                    "use_cases": [
                        {
                            "title": "Computer File Explorer Folders",
                            "impact": "Clean Directory Hierarchy",
                            "description": "Operating system aapki files ko nested folders me organize karta hai: Documents -> University -> Semester 2 -> Chemistry.pdf."
                        },
                        {
                            "title": "E-Commerce Shopping Categories (Amazon)",
                            "impact": "Guided Product Navigation",
                            "description": "Shoppers category branches browse karte hain: Electronics -> Audio -> Headphones, jisse lakho products seconds me filter ho jate hain."
                        },
                        {
                            "title": "Search Engine Autocomplete (Google)",
                            "impact": "Letter-by-Letter Trie Trees",
                            "description": "Jaise hi aap search box me letter type karte ho, Google Trie tree ke branches follow karke suggestions predict karta hai."
                        },
                        {
                            "title": "Database Fast Search Indexing",
                            "impact": "Sub-Millisecond Record Lookup",
                            "description": "Databases B-Trees use karte hain taaki 5 crore records me se 1 customer account sirf 3-4 disk checks me mil sake."
                        }
                    ],
                    "takeaway": "Tree data ko branches me organize karta hai taaki poori list scan kiye bina kuch hi steps me targeted item tak pahuncha ja sake.",
                    "tradeoffs": {
                        "advantages": "Super fast O(log n) search speeds; data ko naturally structured hierarchy me maintain karta hai.",
                        "disadvantages": "Tree ko balanced rakhne ke liye extra rotations karni padti hain; flat array se zyada memory overhead hota hai."
                    },
                    "example_text": "Cookbook Table of Contents: Desserts se Cookies tak branch follow karke 1,000 pages me se recipe 3 steps me mil jaati hai."
                }
            return {
                "title": "A Book's Table of Contents & File Folders",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "Imagine searching for a recipe for 'Chocolate Chip Cookies' in a huge 1,000-page cookbook. You don't flip through all 1,000 pages one by one! You open the Table of Contents: Desserts $\\to$ Baked Goods $\\to$ Cookies $\\to$ Chocolate Chip.",
                "breakdown": """1. **Hierarchical Branching**: Instead of one giant flat list, information branches outward like a tree: Root $\\to$ Categories $\\to$ Subcategories $\\to$ Specific Items.
2. **Cutting the Search in Half (Logarithmic)**: In a Binary Search Tree, every left-or-right choice eliminates half of all remaining options. In just 10 quick choices, you can pinpoint 1 item out of 1,000 items!
3. **Natural Organization**: Related items stay grouped neatly under common parents, making exploration fast and organized.""",
                "use_cases": [
                    {
                        "title": "Computer File Explorer Folders",
                        "impact": "Clean Directory Hierarchy",
                        "description": "Operating systems organize your files into nested folders: `Documents -> University -> Semester 2 -> Chemistry.pdf`."
                    },
                    {
                        "title": "E-Commerce Shopping Categories (Amazon)",
                        "impact": "Guided Product Navigation",
                        "description": "Shoppers browse through branches: Electronics $\\to$ Audio $\\to$ Wireless Headphones, narrowing down millions of items in seconds."
                    },
                    {
                        "title": "Search Engine Autocomplete Suggestions",
                        "impact": "Letter-by-Letter Trie Trees",
                        "description": "Google predicts what word you are typing by following a letter-branch tree as you press each key."
                    },
                    {
                        "title": "Database Fast Search Indexing",
                        "impact": "Sub-Millisecond Record Lookup",
                        "description": "Databases use B-Trees to find 1 customer account out of 50 million records in just 3 or 4 quick disk checks."
                    }
                ],
                "takeaway": "A tree organizes information into branches so you can zoom in on what you need in just a few quick choices instead of searching everything.",
                "tradeoffs": {
                    "advantages": "Blazing fast search speeds; groups related information naturally into clean hierarchies.",
                    "disadvantages": "Takes more effort to keep branches balanced; slightly more complicated to set up than a flat list."
                },
                "example_text": "Cookbook Table of Contents: Branching from Desserts to Cookies lets you find a recipe among 1,000 pages in just three quick steps."
            }

        # Hash Table & Hash Map
        if any(w in t_lower for w in ["hash", "hash table", "hash map", "hashing"]):
            if is_hinglish:
                return {
                    "title": "Theatre Coat Check Room aur Numbered Token",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Jab aap kisi theatre me jaate ho, to aap apna heavy coat attendant ko dete ho. Attendant use hook #47 par taang deta hai aur aapko #47 number ka claim token pakda deta hai.",
                    "breakdown": """1. **The Hash Shortcut**: Attendant ko ye yaad rakhne ki zarurat nahi hoti ki aapka coat kaisa dikhta hai (color, size, brand). System coat ko ek direct number (#47) me convert kar deta hai (Hashing).
2. **Instant 2-Second Pickup ($O(1)$)**: Show khatam hone par aap token #47 dikhate ho. Attendant saare 300 coats scan nahi karta! Wo seedhe hook #47 par jata hai aur 2 second me coat aapko de deta hai.
3. **Collision Handling**: Agar do doston ko same slot mil jaye, to attendant dusra coat pehle ke peeche taang deta hai (Chaining/Collision Resolution).""",
                    "use_cases": [
                        {
                            "title": "Phone Contacts Search",
                            "impact": "Instant Name-to-Number Lookup",
                            "description": "'Mom' type karte hi split-second me phone number nikal aata hai kyunki name directly memory slot se map hota hai."
                        },
                        {
                            "title": "Website Login & Username Check",
                            "impact": "Instant Account Verification",
                            "description": "Sign in karte waqt website 10 crore accounts me se check kar leti hai ki username exists karta hai ya nahi, 1 millisecond se bhi kam me."
                        },
                        {
                            "title": "Online Shopping Cart",
                            "impact": "Cart Items Retrieval",
                            "description": "E-commerce sites aapke unique Session ID ko hash key ki tarah use karke instantly aapka cart load karti hain."
                        },
                        {
                            "title": "Dictionary Word Definitions",
                            "impact": "Direct Word Meaning Search",
                            "description": "Online dictionary me koi word type karte hi bina baaki words scan kiye exact definition open hoti hai."
                        }
                    ],
                    "takeaway": "Hash table kisi bhi item ka name ya key ek exact locker number me convert karke instant O(1) shortcut deta hai.",
                    "tradeoffs": {
                        "advantages": "Data collection chahe kitna bhi bada ho, search, insert, aur delete hamesha instant O(1) time me hote hain.",
                        "disadvantages": "Collisions avoid karne ke liye extra empty space chahiye hoti hai; elements sorted order me nahi rehte."
                    },
                    "example_text": "Coat Check Token: Coat ko token #47 me map karke instant O(1) retrieval milta hai bina doosre coats scan kiye."
                }
            return {
                "title": "A Theatre Coat Check Room with Claim Tickets",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "When you arrive at a theatre, you hand your heavy winter coat to the attendant. The attendant hangs it on hook #47 and hands you a claim ticket with number #47 on it.",
                "breakdown": """1. **The Hash Shortcut**: Instead of remembering what your coat looks like (color, size, brand), the system converts your coat into a simple direct number (#47).
2. **Instant 2-Second Pickup ($O(1)$)**: When the show ends, you hand back ticket #47. The attendant doesn't examine all 300 coats! They walk straight to hook #47 and hand you your coat in two seconds flat.
3. **Sharing a Hook (Collision)**: If two friends check their jackets at the same time, the attendant hangs the second jacket behind the first on the same hook. When you return, they just check the label.""",
                "use_cases": [
                    {
                        "title": "Smartphone Contacts Search",
                        "impact": "Instant Name-to-Number Lookup",
                        "description": "Typing 'Mom' immediately reveals her phone number in a fraction of a millisecond because her name maps directly to her contact info."
                    },
                    {
                        "title": "Website Login & Username Check",
                        "impact": "Instant Account Verification",
                        "description": "When you sign in, the website checks if your username exists in a database of 100 million accounts in less than a millisecond."
                    },
                    {
                        "title": "Online Shopping Cart",
                        "impact": "Remembering Your Cart Items",
                        "description": "E-commerce stores use your unique Session ID as a hash key to instantly pull up the items in your cart as you browse."
                    },
                    {
                        "title": "Dictionary Word Definitions",
                        "impact": "Direct Word Meaning Search",
                        "description": "Typing any word in an online dictionary retrieves its definition directly without scanning through all other words."
                    }
                ],
                "takeaway": "A hash table gives you an instant shortcut to any item by turning its name into an exact locker or hook number.",
                "tradeoffs": {
                    "advantages": "Instant search, insert, and delete no matter how big the collection gets.",
                    "disadvantages": "Requires extra empty space to prevent crowding on the same hook; items are not stored in alphabetical order."
                },
                "example_text": "Coat Check Claim Tickets: Turning a coat into ticket #47 allows instant retrieval from hook #47 without inspecting other coats."
            }

        # Graph & Dijkstra
        if any(w in t_lower for w in ["dijkstra", "shortest path", "graph"]):
            if is_hinglish:
                return {
                    "title": "Metro Subway Map Par Sabse Fast Route Dhoondhna",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Aap ek busy metro station par khade ho jahan 40 interconnected lines hain. Aapko minimum time aur sabse kam interchange ke sath airport pahunchna hai.",
                    "breakdown": """1. **Stations aur Tracks (Nodes & Edges)**: Stations checkpoints hain (Nodes), aur unke beech railway tracks ka known travel time hota hai (jaise Station A se B tak 3 minutes).
2. **Step-by-Step Smart Exploration**: Blindly guess karne ke bajay route finder sabse pehle padosi stations inspect karta hai aur har station tak ka fastest time continuously record karta hai.
3. **Guaranteed Fastest Path**: Hamesha sabse shortest known segment ko extend karke Dijkstra algorithm mathematically guarantee karta hai ki aap least possible time me airport pahuncho.""",
                    "use_cases": [
                        {
                            "title": "Google Maps Live Traffic Navigation",
                            "impact": "Real-Time Driving Route",
                            "description": "GPS apps live traffic aur accidents ke mutabiq real-time me fastest route calculate karte hain."
                        },
                        {
                            "title": "Social Media 'People You May Know'",
                            "impact": "Friendship Network Connections",
                            "description": "Instagram aur LinkedIn mutual friends ke connections ko trace karke new network suggestions dete hain."
                        },
                        {
                            "title": "Delivery Package Routing (Amazon / Flipkart)",
                            "impact": "Optimal Delivery Path",
                            "description": "Delivery vans 100 packages drop karne ke liye smartest street-by-street path calculate karti hain taaki backtracking na ho."
                        },
                        {
                            "title": "Airline Flight Connections",
                            "impact": "Fastest Multi-City Layovers",
                            "description": "Flight booking engines connected flights ko analyse karke lowest travel time wala connecting flight schedule nikaalte hain."
                        }
                    ],
                    "takeaway": "Graph real world ke interconnected networks ko model karta hai, aur shortest path algorithm zero time waste kiye best route nikaalta hai.",
                    "tradeoffs": {
                        "advantages": "Complex networks me mathematically guaranteed fastest route dhoondhta hai; live traffic changes ko adapt karta hai.",
                        "disadvantages": "Saare connections map karne padte hain; millions of roads wale massive map par zyada CPU computation lagti hai."
                    },
                    "example_text": "Metro Route: Padosi stations ko step-by-step explore karke Dijkstra airport ka fastest path guarantee karta hai."
                }
            return {
                "title": "Finding the Quickest Route on a Metro Subway Map",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "You are standing at a busy subway station with 40 connected lines. You need to reach the airport with the minimum travel time and fewest station changes.",
                "breakdown": """1. **Stations and Tracks (Nodes & Connections)**: Stations are checkpoints, and the railway tracks between them have known travel times (e.g., 3 minutes between Station A and B).
2. **Smart Step-by-Step Exploration**: Instead of guessing blindly, the route finder inspects neighboring stations first, constantly recording the fastest travel time to each station.
3. **Guaranteed Fastest Path**: By always extending the shortest known leg, it mathematically guarantees you arrive at the airport in the least possible time.""",
                "use_cases": [
                    {
                        "title": "Google Maps / Apple Maps Navigation",
                        "impact": "Live Traffic Driving Route",
                        "description": "GPS apps calculate the quickest driving route to work in real time while steering you around accidents and traffic jams."
                    },
                    {
                        "title": "Social Media 'People You May Know'",
                        "impact": "Friendship Network Connections",
                        "description": "Platforms like Instagram and LinkedIn suggest connections by tracing mutual friendships across social network webs."
                    },
                    {
                        "title": "Package Delivery Routing (Amazon / FedEx)",
                        "impact": "Optimal Delivery Sequence",
                        "description": "Delivery vans calculate the smartest street-by-street path to drop off 120 packages without backtracking."
                    },
                    {
                        "title": "Airline Flight Connections",
                        "impact": "Fastest Multi-City Layovers",
                        "description": "Flight booking sites connect international flights across hub airports to find you the quickest route with the shortest layovers."
                    }
                ],
                "takeaway": "A graph models how things connect in the real world, and shortest-path algorithms guide you through the quickest route with zero wasted time.",
                "tradeoffs": {
                    "advantages": "Finds the mathematically fastest route across complex webs; adapts easily to real-time traffic updates.",
                    "disadvantages": "Requires mapping every connection; takes more computer processing on massive maps with millions of roads."
                },
                "example_text": "Metro Subway Route: Inspecting adjacent stations step-by-step guarantees discovering the fastest path to the airport."
            }

        # Sorting Algorithms
        if any(w in t_lower for w in ["sorting", "quicksort", "merge sort", "bubble sort", "heap sort"]):
            if is_hinglish:
                return {
                    "title": "Exam Papers ko Alphabetically Arrange Karna",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Ek teacher 150 students ke exam papers collect karta hai jo mixed order me hain. Report card me marks enter karne ke liye teacher ko papers A-se-Z alphabetical order me arrange karne hain.",
                    "breakdown": """1. **Order Hone Se Ghanton Ka Time Bachta Hai**: Agar papers mixed hon, to 150 grades enter karne ke liye poore pile ko 150 baar palatna padega ($150 \\times 150 = 22{,}500$ paper flips!).
2. **Divide and Conquer (Merge/Quick Sort)**: Teacher papers ko do chhote bundles me baant deta hai (A–M aur N–Z), dono ko alag sort karke aapas me smoothly merge kar deta hai.
3. **One-Pass Grading**: Ek baar alphabetically sort hone ke baad, teacher shuru se aakhir tak single smooth pass me saare marks enter kar deta hai.""",
                    "use_cases": [
                        {
                            "title": "E-Commerce 'Sort by Price: Low to High'",
                            "impact": "Instant Budget Filtering",
                            "description": "Amazon aur Flipkart hazaron products ko price ke mutabiq sort karke sabse affordable items pehle display karte hain."
                        },
                        {
                            "title": "Spotify Playlist Organization",
                            "impact": "Custom Music Browsing",
                            "description": "Users ek tap me apni music library ko song title, artist, ya date added ke hisaab se sort kar sakte hain."
                        },
                        {
                            "title": "Cricket Tournament Points Table",
                            "impact": "Leaderboard Rankings",
                            "description": "IPL aur World Cup me teams ko points aur net run rate ke according sort karke standings show ki jaati hain."
                        },
                        {
                            "title": "Smartphone Contact List",
                            "impact": "A-to-Z Fast Scrolling",
                            "description": "Phone contacts alphabetically sort hote hain taaki aap direct scroll karke required name par jump kar sako."
                        }
                    ],
                    "takeaway": "Sorting unorganized data ko order me laakar search aur retrieval time ko drastically reduce kar deti hai.",
                    "tradeoffs": {
                        "advantages": "Searching aur filtering ko effortless banata hai; top items aur price comparison fast karta hai.",
                        "disadvantages": "Initial sorting me processing time lagta hai; massive datasets me temporary extra memory chahiye hoti hai."
                    },
                    "example_text": "Exam Papers Sorting: Papers ko A-Z sort karke 150 grades single pass me enter ho jaate hain bina baar baar dhoondhe."
                }
            return {
                "title": "Arranging Exam Papers Alphabetically by Student Name",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "A teacher collects 150 student exam papers stacked in random order. To record grades into the school gradebook, the teacher needs the papers arranged alphabetically from A to Z.",
                "breakdown": """1. **Why Order Saves Hours**: If the papers are jumbled, entering 150 grades requires flipping through the pile 150 times ($150 \\times 150 = 22{,}500$ paper flips!).
2. **Divide and Conquer**: The teacher splits the stack into two smaller piles (A–M and N–Z), sorts each half, and neatly combines them together.
3. **One-Pass Grading**: Once sorted alphabetically, the teacher enters all 150 grades in a single smooth pass from start to finish.""",
                "use_cases": [
                    {
                        "title": "Online Shopping 'Sort by Price: Low to High'",
                        "impact": "Instant Budget Filtering",
                        "description": "Amazon and Flipkart sort thousands of products so you see the most affordable options first."
                    },
                    {
                        "title": "Spotify Playlist Organization",
                        "impact": "Custom Music Browsing",
                        "description": "Listeners sort their music library by song title, artist name, or date added with a single tap."
                    },
                    {
                        "title": "Sports League Tournament Standings",
                        "impact": "Leaderboard Rankings",
                        "description": "Football and cricket leagues sort teams by points, wins, and run-rates so fans immediately see who is in 1st place."
                    },
                    {
                        "title": "Smartphone Contact List",
                        "impact": "A-to-Z Fast Scrolling",
                        "description": "Your phone automatically sorts contact names alphabetically so you can jump straight to names starting with 'S'."
                    }
                ],
                "takeaway": "Sorting brings order to chaos, transforming endless searching into a quick and effortless lookup.",
                "tradeoffs": {
                    "advantages": "Enables instant lookups; makes comparing prices and finding top items effortless.",
                    "disadvantages": "Sorting requires initial time and effort; rearranging huge datasets requires extra temporary memory."
                },
                "example_text": "Alphabetical Exam Papers: Sorting papers into A-Z order allows entering 150 grades in a single smooth pass instead of flipping through papers thousands of times."
            }

        # Law: Damnum Sine Injuria
        if any(w in t_lower for w in ["damnum", "damnun", "injuria", "tort", "sine"]):
            if is_hinglish:
                return {
                    "title": "Ek Hi Sadak Par Do Competing Coffee Shops",
                    "badge": "Everyday Real-Life Legal Dispute (Hinglish)",
                    "scenario": "Rohan Main Street par ek coffee shop chalata hai jahan $5 me coffee milti hai. Priya uske bilkul bagal me ek naya coffee shop kholti hai jahan wahi coffee $3 me milti hai. Do mahine me Rohan ke kayi customers Priya ke shop par chale jaate hain jisse Rohan ko $4,000 ka monthly loss hota hai. Rohan gusse me Priya par court me lawsuit file karta hai aur compensation mangta hai.",
                    "breakdown": """1. **Financial Loss Hua (*Damnum*)**: Rohan ko financial nuksaan hua aur uska business kam ho gaya.
2. **Koi Legal Right Violate Nahi Hua (*Sine Injuria*)**: Priya ne koi illegal kaam nahi kiya. Na trespassing ki, na jhooth bola, na recipe chori ki. Usne lawful business khola aur fair price offer ki. Customers ke paas choice hai ki wo apna paisa kahan spend karein.
3. **Court Ka Faisla**: Judge Rohan ka case dismiss kar deta hai. Law me, sirf financial loss (*Damnum*) bina legal right violation (*Sine Injuria*) ke compensation ka claim nahi banata.""",
                    "use_cases": [
                        {
                            "title": "Supermarket Price Rivalry",
                            "impact": "Fair Market Competition",
                            "description": "Ek discount grocery store purane store ke bagal me khulkar budget-conscious customers ko lawfully attract karta hai."
                        },
                        {
                            "title": "Smartphone Market Rivalry",
                            "impact": "Consumer Innovation",
                            "description": "Ek company behtar aur sasta phone launch karti hai jisse rival brands ka market share kam ho jata hai."
                        },
                        {
                            "title": "Honest Restaurant Food Reviews",
                            "impact": "Freedom of Fair Review",
                            "description": "Food critic honest negative review likhta hai jisse restaurant ke customers kam hote hain, par ye defamation nahi hai."
                        },
                        {
                            "title": "New Metro Line Launch",
                            "impact": "Civic Infrastructure",
                            "description": "Nayi metro line shuru hone se local auto-rickshaws ki daily earnings kam ho jaati hain, par ye actionable wrong nahi hai."
                        }
                    ],
                    "takeaway": "Sirf paison ka nuksaan hone par aap court nahi ja sakte; lawsuit tabhi banta hai jab aapka koi legal right violate hua ho.",
                    "tradeoffs": {
                        "advantages": "Fair competition aur innovation ko protect karta hai; consumers ko affordable prices milti hain.",
                        "disadvantages": "Honest market competition se nuksaan uthane wale business owners ko koi legal remedy nahi milti."
                    },
                    "example_text": "Two Coffee Shops: Lawful price competition se hua financial loss bina legal right violation ke actionable nahi hai."
                }
            return {
                "title": "Two Competing Coffee Shops on the Same Street",
                "badge": "Everyday Real-Life Legal Dispute",
                "scenario": "Rohan runs a popular coffee shop on Main Street selling lattes for $5. Priya opens a bright coffee shop right next door selling equally good coffee for $3. Within two months, many of Rohan's customers switch to Priya's shop, causing Rohan's monthly profit to drop by $4,000. Rohan angrily sues Priya in court, demanding she pay for his lost earnings.",
                "breakdown": """1. **Real Money Was Lost (*Damnum*)**: Rohan suffered genuine financial loss and lost customer revenue.
2. **No Law Was Broken (*Sine Injuria*)**: Priya did nothing illegal. She didn't trespass, didn't spread false lies, and didn't steal recipes. She simply opened a legal business and offered lower prices. Customers have the freedom to spend their money wherever they like.
3. **The Court's Ruling**: The judge dismisses Rohan's lawsuit with zero compensation. In law, financial loss alone (*Damnum*) without a violation of a legal right (*Sine Injuria*) gives no right to sue.""",
                "use_cases": [
                    {
                        "title": "Supermarket Price Competition",
                        "impact": "Fair Market Rivalry",
                        "description": "A discount grocery store opening near an existing store and attracting price-conscious shoppers lawfully."
                    },
                    {
                        "title": "Smartphone Market Competition",
                        "impact": "Consumer Innovation",
                        "description": "A tech company launching a better, more affordable smartphone that causes rival brands to lose market share."
                    },
                    {
                        "title": "Honest Restaurant Product Reviews",
                        "impact": "Freedom of Fair Review",
                        "description": "A food critic writing a sincere negative review that causes a restaurant to lose customers without committing defamation."
                    },
                    {
                        "title": "New Public Transport Lines",
                        "impact": "Civic Infrastructure",
                        "description": "A city opening a new metro line that reduces daily passenger earnings for local auto-rickshaw drivers."
                    }
                ],
                "takeaway": "You cannot sue someone simply because you lost money; you can only sue if they actually violated your legal rights.",
                "tradeoffs": {
                    "advantages": "Protects fair competition, rewards innovation, and keeps prices affordable for everyday consumers.",
                    "disadvantages": "Business owners have no legal protection when honest market competition causes them financial hardship."
                },
                "example_text": "Two Competing Coffee Shops: Financial loss caused by lawful price competition without violating any legal right is not actionable in court."
            }

        # Physics: Newton's Laws
        if any(w in t_lower for w in ["newton", "law of motion", "force", "inertia", "dynamics"]):
            if is_hinglish:
                return {
                    "title": "Halki Bicycle vs Bhaari Khadi Hui Car ko Push Karna",
                    "badge": "Everyday Physical Experience (Hinglish)",
                    "scenario": "Imagine karo aap ek 10 kg ki halki bicycle ko sadak par dhakka de rahe ho, aur doosri taraf ek 2,000 kg ki bhaari car ko jo band pad gayi hai.",
                    "breakdown": """1. **Bhaari Cheezein Move Hone Se Rokti Hain (Inertia & $F = ma$)**: Ek halka sa dhakka bicycle ko turant aage badha deta hai. Lekin heavy car ko hilane ke liye teen logon ko apni poori Force lagani padti hai tab jaakar wo thoda sa crawl karti hai.
2. **Rokne Ke Liye Force Chahiye**: Halki cycle ko rokne ke liye handbrake ka halka press kaafi hai. Lekin aage badhti bhaari car ko rokne ke liye powerful brakes chahiye; agar haath se rokne ki koshish karoge to Inertia ki wajah se car aapko kheench legi!
3. **Equal & Opposite Push (Third Law)**: Jab aap car ko aage dhakelte ho, to sadak aapke joote ke neeche backwards direction me exact same Friction aur reaction Force lagati hai.""",
                    "use_cases": [
                        {
                            "title": "Car Seatbelts & Airbags",
                            "impact": "Passenger Crash Safety",
                            "description": "Sudden braking ke waqt seatbelts aur airbags aapki body ko smoothly slow karte hain taaki Inertia ki wajah se aap windshield se na takrayein."
                        },
                        {
                            "title": "Space Rocket Launches",
                            "impact": "Action & Reaction Propulsion",
                            "description": "Rocket engines hot exhaust gas ko tezi se downward shoot karte hain, jo reaction Force se heavy rocket ko outer space me push karta hai."
                        },
                        {
                            "title": "Bicycle & Motorcycle Brakes",
                            "impact": "Controlled Stopping Power",
                            "description": "Brake pads ghoomte wheels par Friction force lagate hain taaki moving vehicle safe distance par ruk sake."
                        },
                        {
                            "title": "Elevators & Counterweights",
                            "impact": "Mechanical Balance",
                            "description": "Bhaari counterweights elevator cab ke weight ko balance karte hain taaki electric motor ko kam Force lagani pade."
                        }
                    ],
                    "takeaway": "Bhaari objects (greater Mass) ko move ya stop karne ke liye zyada Force chahiye, aur nature me har action Force ka ek equal aur opposite reaction Force hota hai.",
                    "tradeoffs": {
                        "advantages": "Vehicles, machines, aur structures me motion aur safety calculate karne ke liye 100% reliable aur accurate rules deta hai.",
                        "disadvantages": "Ye everyday speeds aur objects par perfect apply hota hai, lekin speed of light ya atomic scale par Quantum Mechanics chahiye hoti hai."
                    },
                    "example_text": "Pushing a Bike vs Car: Heavy mass changes in motion ko resist karta hai (Inertia), jisse acceleration ke liye zyada Force lagti hai ($F = ma$)."
                }
            return {
                "title": "Pushing a Light Bicycle vs. a Heavy Stalled Car",
                "badge": "Everyday Physical Experience",
                "scenario": "Imagine you try pushing a lightweight 10 kg bicycle down a road, and then you try pushing a heavy 2,000 kg car that ran out of fuel.",
                "breakdown": """1. **Heavy Things Resist Moving (Inertia & $F = ma$)**: One gentle hand push rolls the light bicycle instantly. But moving the heavy car requires three adults pushing with all their strength just to get it rolling at a crawl.
2. **Stopping Takes Force**: Stopping the light bicycle takes a soft squeeze on the handbrake. Stopping the heavy rolling car requires powerful foot brakes; if you tried stopping it with your hands, it would drag you along!
3. **Equal & Opposite Push**: When you plant your sneakers on the asphalt to shove the car forward, the road pushes backward against your feet with the exact same force.""",
                "use_cases": [
                    {
                        "title": "Car Seatbelts & Airbags",
                        "impact": "Passenger Crash Safety",
                        "description": "Seatbelts and airbags slow down your body smoothly during sudden braking so you don't keep flying forward into the windshield."
                    },
                    {
                        "title": "Space Rocket Launches",
                        "impact": "Action & Reaction Propulsion",
                        "description": "Rocket engines shoot hot exhaust gas furiously downward, which pushes the heavy rocket upward into outer space."
                    },
                    {
                        "title": "Bicycle & Motorcycle Brakes",
                        "impact": "Controlled Stopping Power",
                        "description": "Brake pads squeeze against rotating wheels, creating friction force to bring moving vehicles to a safe halt."
                    },
                    {
                        "title": "Elevators & Counterweights",
                        "impact": "Mechanical Balance",
                        "description": "Heavy counterweights balance the weight of elevator cabs so electric motors only need a small push to move people between floors."
                    }
                ],
                "takeaway": "Heavy objects take much more force to move and stop, and every push in nature produces an equal push back.",
                "tradeoffs": {
                    "advantages": "Provides clear and reliable rules to calculate motion, speed, and safety in vehicles and machinery.",
                    "disadvantages": "Only applies to everyday speeds and objects; breaks down at near-light speeds or atomic scales."
                },
                "example_text": "Pushing a Bike vs Car: Heavy mass resists changes in motion, meaning greater mass requires greater force to accelerate or stop."
            }

        # Mathematics: Calculus & Integration
        if any(w in t_lower for w in ["calculus", "integral", "integration", "derivative"]):
            if is_hinglish:
                return {
                    "title": "Tapakhte Hue Nall Ke Neeche Bucket Ka Paani Napna",
                    "badge": "Everyday Real-Life Analogy (Hinglish)",
                    "scenario": "Aap ek leak hote tap ke neeche khali bucket rakhte ho. Pehle paani dheere tapakta hai (3 second me 1 drop). Fir upstairs koi flush karta hai to paani tez dhaar ban jata hai, fir dobara slow ho jata hai.",
                    "breakdown": """1. **Normal Multiplication Kyun Fail Hota Hai**: Agar paani constant speed se girta, to aap direct multiply karte: Speed $\\times$ Time = Total Water. Lekin yahan tapakne ki speed har second badal rahi hai!
2. **Chhote Chhote Drops Ka Total Sum (Integration)**: Integration poore ghante ko hazaron tiny 1-second snapshots me divide karta hai, har second ka paani calculate karta hai, aur sabko jod kar bucket ka exact total volume de deta hai.
3. **Speedometer vs Odometer**: Derivative aapki car ke speedometer jaisa hai (is exact second speed kya hai). Integral aapke odometer jaisa hai (poori trip me total kitna distance travel hua).""",
                    "use_cases": [
                        {
                            "title": "Phone Battery Life Percentage",
                            "impact": "Accumulated Power Usage",
                            "description": "Phone dynamic app consumption ko second-by-second integrate karke remaining battery life calculate karta hai."
                        },
                        {
                            "title": "Car Trip Distance Tracking",
                            "impact": "Variable Speed Distance",
                            "description": "Car computers variable driving speeds ko continuously integrate karke exact trip distance measure karte hain."
                        },
                        {
                            "title": "Medicine Bloodstream Absorption",
                            "impact": "Patient Dosing Tracking",
                            "description": "Doctors track karte hain ki 24 ghante me patient ki body me medicine kis rate par absorb ho rahi hai."
                        },
                        {
                            "title": "Dam Water Inflow in Monsoons",
                            "impact": "Rainfall Inflow Calculation",
                            "description": "Engineers changing rainfall speed ko integrate karke dam me gather hone wale total water volume ko predict karte hain."
                        }
                    ],
                    "takeaway": "Calculus continuously badalti hui speed aur rates ke dauraan bhi exact total calculation karne ki power deta hai.",
                    "tradeoffs": {
                        "advantages": "Conditions badal rahi hon tab bhi exact total amount aur instantaneous rate accurately calculate karta hai.",
                        "disadvantages": "Sudden jumps wale real-world scenarios me computer approximations ya complex mathematical formulas lagte hain."
                    },
                    "example_text": "Leaking Tap & Bucket: Variable drip speed ko second-by-second integrate karke bucket ka total water accurately calculate hota hai."
                }
            return {
                "title": "Measuring Water in a Bucket under a Leaking Tap",
                "badge": "Everyday Real-Life Analogy",
                "scenario": "You place an empty bucket under a leaking bathroom tap. At first, it drips slowly (1 drop every 3 seconds). Then someone flushes a toilet upstairs and the leak turns into a fast trickle, then slows down again.",
                "breakdown": """1. **Why Normal Multiplication Fails**: If water dripped at a constant, steady speed, you would simply multiply: Speed $\\times$ Time = Total Water. But here, the drip speed changes every single second!
2. **Adding Up Tiny Drops (Integration)**: Integration solves this by slicing the whole hour into thousands of tiny one-second snapshots, measuring how much dripped during each second, and adding them all together into the exact total bucket volume.
3. **Speedometer vs. Odometer**: The derivative is like your car's speedometer (how fast you are traveling right now this instant). The integral is like your car's odometer (the total miles you accumulated over the entire road trip).""",
                "use_cases": [
                    {
                        "title": "Smartphone Battery Remaining Indicator",
                        "impact": "Accumulated Power Usage",
                        "description": "Your phone calculates remaining battery life by adding up changing app power consumption second by second over the day."
                    },
                    {
                        "title": "Car Trip Mileage Tracking",
                        "impact": "Variable Speed Distance",
                        "description": "Computers calculate total distance driven even as you speed up on highways and stop at red traffic lights."
                    },
                    {
                        "title": "Medicine Absorption in Healthcare",
                        "impact": "Patient Dosing Tracking",
                        "description": "Doctors track total medicine absorbed into a patient's bloodstream over 24 hours as the body gradually processes it."
                    },
                    {
                        "title": "City Water Reservoir Management",
                        "impact": "Rainfall Inflow Calculation",
                        "description": "Engineers calculate total water gathered in a city dam during a rainstorm where rainfall intensity changes constantly."
                    }
                ],
                "takeaway": "Calculus lets you calculate total accumulation even when things are changing speed and rate every second.",
                "tradeoffs": {
                    "advantages": "Accurately calculates total amounts when rates, speeds, and conditions are constantly changing.",
                    "disadvantages": "Requires continuous mathematical formulas or computer approximations when real-world measurements have sudden jumps."
                },
                "example_text": "Leaking Tap & Water Bucket: Integration adds up variable drip speeds second-by-second to find the exact total water collected."
            }

        # 3. Clean, friendly domain-specific synthesized fallback for other topics
        domain_use_cases = GeminiService._synthesize_domain_use_cases(clean_topic, category, lang=lang)
        if is_hinglish:
            return {
                "title": f"Asli Duniya Ka Example: {clean_topic}",
                "badge": "Everyday Practical Example (Hinglish)",
                "scenario": f"{clean_topic} se judi ek practical situation ke baare me socho, jahan organized rules follow karne se mushkil task simple, predictable, aur error-free ho jata hai.",
                "breakdown": f"1. **Starting Problem**: Samajhna ki {clean_topic} me kya problem solve karni hai aur kaunse resources available hain.\n2. **How It Works (Step-by-Step)**: Core principle ko step-by-step follow karna taaki bina kisi confusion ke desired result mil sake.\n3. **Practical Result**: Verify karna ki outcome reliable hai aur har situation me consistently kaam karta hai.",
                "use_cases": domain_use_cases,
                "takeaway": f"{clean_topic} real-world problems ko efficiently aur systematically solve karne ka structured approach provide karta hai.",
                "tradeoffs": {
                    "advantages": f"{clean_topic} complex concepts ko structured, repeatable, aur reliable solution provide karta hai.",
                    "disadvantages": f"Best results paane ke liye core principles aur foundational details ka proper dhyan rakhna padta hai."
                },
                "example_text": f"Everyday practical walkthrough explaining how {clean_topic} works simply and reliably."
            }
        return {
            "title": f"Everyday Real-Life Analogy: {clean_topic}",
            "badge": "Everyday Practical Example",
            "scenario": f"Think of a practical everyday situation involving {clean_topic}, where following organized rules makes a complex task simple, predictable, and error-free.",
            "breakdown": f"1. **The Starting Problem**: Identifying what goal we need to achieve and what resources or inputs are available for {clean_topic}.\n2. **How It Works**: Following the core principle step-by-step to reach the desired result without confusion or wasted effort.\n3. **The Practical Result**: Verifying that the outcome is reliable, easy to understand, and works consistently every time.",
            "use_cases": domain_use_cases,
            "takeaway": f"{clean_topic} gives you a clear, structured way to solve real problems simply and reliably.",
            "tradeoffs": {
                "advantages": f"Provides a clear, repeatable, and organized solution for problems related to {clean_topic}.",
                "disadvantages": f"Requires learning the core rules and paying attention to small details to get the best results."
            },
            "example_text": f"Everyday practical walkthrough explaining how {clean_topic} works simply and reliably."
        }

    @staticmethod
    def _synthesize_domain_use_cases(topic: str, category: str = "", lang: str = "english") -> List[Dict[str, str]]:
        """Synthesizes three clean, realistic, everyday real-world use cases for any academic topic in English or Hinglish."""
        low_t = (topic or "").lower()
        low_c = (category or "").lower()
        is_h = (lang or "").strip().lower() == "hinglish"
        
        if any(k in low_t or k in low_c for k in ["os", "operating system", "process", "memory", "thread", "kernel", "scheduling", "deadlock"]):
            if is_h:
                return [
                    {
                        "title": "Smartphone Multitasking & App Switching",
                        "impact": "Smooth User Experience",
                        "description": "Phone me background music, chat notifications, aur live navigation ek saath bina crash ya freeze hue chalane me madad karta hai."
                    },
                    {
                        "title": "Cloud Server Virtualization",
                        "impact": "Maximum Resource Utilization",
                        "description": "Shared data center hardware pe thousands of isolated user workloads ko strict memory aur CPU isolation ke sath safely run karta hai."
                    },
                    {
                        "title": "Mission-Critical Aviation & Medical Devices",
                        "impact": "Deterministic Fault Tolerance",
                        "description": "Life-support controls aur flight sensor inputs ko microsecond deadlines me bina deadlock ke deterministic execute karta hai."
                    }
                ]
            return [
                {
                    "title": "Smartphone Multitasking & App Switching",
                    "impact": "Smooth User Experience",
                    "description": f"Enables modern phones to run background music, chat notifications, and navigation simultaneously without crashing or freezing."
                },
                {
                    "title": "Cloud Server Virtualization",
                    "impact": "Maximum Resource Utilization",
                    "description": f"Coordinates thousands of isolated user workloads on shared data center hardware safely with strict memory and CPU isolation."
                },
                {
                    "title": "Mission-Critical Aviation & Medical Devices",
                    "impact": "Deterministic Fault Tolerance",
                    "description": f"Guarantees that vital sensor inputs and life-support controls execute within strict microsecond deadlines without deadlock."
                }
            ]
        elif any(k in low_t or k in low_c for k in ["network", "tcp", "ip", "udp", "routing", "http", "socket"]):
            if is_h:
                return [
                    {
                        "title": "High-Definition Video Streaming",
                        "impact": "Buffer-Free Entertainment",
                        "description": "Live video stream ko lightweight data packets me segment karke global routers ke zariye smart TVs par bina buffer assemble karta hai."
                    },
                    {
                        "title": "Global Online Banking & Payments",
                        "impact": "Encrypted Transaction Delivery",
                        "description": "Jab users money transfer karte hain to transactions end-to-end encrypted packets ke roop me securely banks ke beech pahunchte hain."
                    },
                    {
                        "title": "Online Multiplayer Gaming",
                        "impact": "Ultra-Low Latency Sync",
                        "description": "Players ke live coordinates aur game actions sub-15ms bursts me distributed game servers globally par sync karta hai."
                    }
                ]
            return [
                {
                    "title": "High-Definition Video Streaming",
                    "impact": "Buffer-Free Entertainment",
                    "description": f"Segments live video into lightweight data packets that travel across global routers and reassemble seamlessly on smart TVs."
                },
                {
                    "title": "Global Online Banking & Payments",
                    "impact": "Encrypted Transaction Delivery",
                    "description": f"Guarantees secure, end-to-end encrypted packet delivery when users transfer money between banks worldwide."
                },
                {
                    "title": "Online Multiplayer Gaming",
                    "impact": "Ultra-Low Latency Sync",
                    "description": f"Transmits player coordinates and actions in sub-15ms bursts across distributed game servers globally."
                }
            ]
        elif any(k in low_t or k in low_c for k in ["database", "sql", "acid", "transaction", "storage", "index"]):
            if is_h:
                return [
                    {
                        "title": "E-Commerce Checkout & Inventory",
                        "impact": "Zero Overselling",
                        "description": "Jab flash sale me hazaron shoppers ek saath order karte hain, tab inventory counts 100% accurate aur consistent rehte hain."
                    },
                    {
                        "title": "Hospital Patient Records System",
                        "impact": "Instant & Reliable Medical Data",
                        "description": "Emergency rooms me doctors aur nurses ko real-time medical history instantly aur bina data corruption ke milti hai."
                    },
                    {
                        "title": "Airline Seat Reservation",
                        "impact": "Atomicity Under Concurrency",
                        "description": "Booking ke dauraan seats ko temporarily lock karta hai taaki do passengers ko same flight ticket issue na ho sake."
                    }
                ]
            return [
                {
                    "title": "E-Commerce Checkout & Inventory",
                    "impact": "Zero Overselling",
                    "description": f"Ensures that when thousands of shoppers buy the last clearance items, inventory counts remain 100% accurate and consistent."
                },
                {
                    "title": "Hospital Patient Records System",
                    "impact": "Instant & Reliable Medical Data",
                    "description": f"Allows doctors and nurses across emergency rooms to retrieve up-to-the-second medical histories without data corruption."
                },
                {
                    "title": "Airline Seat Reservation",
                    "impact": "Atomicity Under Concurrency",
                    "description": f"Locks seats temporarily during booking so two passengers can never accidentally purchase the exact same ticket."
                }
            ]
        elif any(k in low_t or k in low_c for k in ["physics", "force", "motion", "gravity", "thermodynamics", "optics"]):
            if is_h:
                return [
                    {
                        "title": "Automobile Crash Safety Systems",
                        "impact": "Passenger Life Protection",
                        "description": f"Engineers {topic} ke principles apply karke crumple zones design karte hain aur exact millisecond me airbags deploy karte hain."
                    },
                    {
                        "title": "Commercial Aircraft Aerodynamics",
                        "impact": "Fuel Efficiency & Flight Stability",
                        "description": f"Badalte weather me wing lift, drag reduction, aur safe flight dynamics ko govern karta hai."
                    },
                    {
                        "title": "Renewable Wind & Solar Energy Grids",
                        "impact": "Clean Power Generation",
                        "description": f"Natural energy flows ko city power lines ke liye stable alternating electricity me convert karta hai."
                    }
                ]
            return [
                {
                    "title": "Automobile Crash Safety Systems",
                    "impact": "Passenger Life Protection",
                    "description": f"Engineers apply principles of {topic} to design crumple zones and deploy airbags at the exact millisecond of impact."
                },
                {
                    "title": "Commercial Aircraft Aerodynamics",
                    "impact": "Fuel Efficiency & Flight Stability",
                    "description": f"Governs wing lift, drag minimization, and safe flight dynamics across changing weather conditions."
                },
                {
                    "title": "Renewable Wind & Solar Energy Grids",
                    "impact": "Clean Power Generation",
                    "description": f"Translates natural energy flows into stable alternating electrical currents for city power lines."
                }
            ]
        elif any(k in low_t or k in low_c for k in ["math", "calculus", "algebra", "geometry", "statistics", "probability"]):
            if is_h:
                return [
                    {
                        "title": "Financial Portfolio Risk Analysis",
                        "impact": "Capital Protection & Wealth Growth",
                        "description": f"Probability distributions aur market volatility calculate karke retirement funds me risk aur return balance karta hai."
                    },
                    {
                        "title": "Architectural Structural Engineering",
                        "impact": "Skyscraper Earthquake Resistance",
                        "description": f"Skyscrapers banate waqt exact load stresses, wind shear, aur bending moments calculate karta hai."
                    },
                    {
                        "title": "Computer Graphics & 3D Video Game Engines",
                        "impact": "Photorealistic Rendering",
                        "description": f"Modern GPU par 120 FPS par vector coordinates, lighting vectors, aur camera perspectives calculate karta hai."
                    }
                ]
            return [
                {
                    "title": "Financial Portfolio Risk Analysis",
                    "impact": "Capital Protection & Wealth Growth",
                    "description": f"Calculates probability distributions and market volatility to help retirement funds balance risk and growth."
                },
                {
                    "title": "Architectural Structural Engineering",
                    "impact": "Skyscraper Earthquake Resistance",
                    "description": f"Calculates precise load stresses, wind shears, and material bending moments before constructing tall buildings."
                },
                {
                    "title": "Computer Graphics & 3D Video Game Engines",
                    "impact": "Photorealistic Rendering",
                    "description": f"Transforms vector coordinates, lighting vectors, and camera angles at 120 frames per second on modern graphics cards."
                }
            ]
        elif any(k in low_t or k in low_c for k in ["law", "tort", "contract", "jurisprudence", "constitution"]):
            if is_h:
                return [
                    {
                        "title": "Commercial Business Contracts",
                        "impact": "Enforceable Agreements & Fair Trade",
                        "description": f"Clear obligations aur breach liabilities define karke business partners ke interests protect karta hai."
                    },
                    {
                        "title": "Consumer Product Safety Liability",
                        "impact": "Public Protection & Accountability",
                        "description": f"Manufacturers ko product defects ke liye accountable banata hai aur consumers ko legal remedies ensure karta hai."
                    },
                    {
                        "title": "Intellectual Property & Software Licensing",
                        "impact": "Innovation & Creator Safeguards",
                        "description": f"Creators aur software developers ke intellectual property rights protect karte hue clear usage guidelines deta hai."
                    }
                ]
            return [
                {
                    "title": "Commercial Business Contracts",
                    "impact": "Enforceable Agreements & Fair Trade",
                    "description": f"Protects business partners by defining clear obligations, default remedies, and breach liabilities."
                },
                {
                    "title": "Consumer Product Safety Liability",
                    "impact": "Public Protection & Accountability",
                    "description": f"Holds manufacturers accountable for defects and ensures fair financial remedies for injured consumers."
                },
                {
                    "title": "Intellectual Property & Software Licensing",
                    "impact": "Innovation & Creator Safeguards",
                    "description": f"Secures inventors and software creators against unauthorized copying while establishing clear commercial usage terms."
                }
            ]
        else:
            if is_h:
                return [
                    {
                        "title": f"Real-World Industry Deployment of {topic}",
                        "impact": "Operational Efficiency & Standardization",
                        "description": f"{topic} complex operations ko bina costly mistakes ya confusion ke execute karne ka reliable approach deta hai."
                    },
                    {
                        "title": "Quality Assurance & Error Prevention",
                        "impact": "System Reliability & Safety",
                        "description": f"Proven guidelines follow karke deployment se pehle system me defects aur flaws identify karta hai."
                    },
                    {
                        "title": "Scalable Resource Optimization",
                        "impact": "Cost Reduction & Performance",
                        "description": f"Wasted time aur computing resources minimize karke maximum throughput aur stable output ensure karta hai."
                    }
                ]
            return [
                {
                    "title": f"Real-World Industry Deployment of {topic}",
                    "impact": "Operational Efficiency & Standardization",
                    "description": f"Provides teams with a standardized, reliable method to execute complex operations without guesswork or costly mistakes."
                },
                {
                    "title": f"Quality Assurance & Error Prevention",
                    "impact": "System Reliability & Safety",
                    "description": f"Ensures that all stages of work conform to proven principles, catching defects early before deployment."
                },
                {
                    "title": f"Scalable Resource Optimization",
                    "impact": "Cost Reduction & Performance",
                    "description": f"Minimizes wasted time and material resources while maximizing throughput and predictable performance."
                }
            ]

    @staticmethod
    def build_topic_roadmap(topic: str, clean_q: str, category: str, lang: str = "english", llm_roadmap: Any = None) -> List[Dict[str, Any]]:
        """Constructs an authentic, topic-specific 5-step curriculum roadmap aligned with university exams & GATE.
        Supports both English and natural Hinglish. Eliminates generic template boilerplate and broken formatting.
        """
        clean_topic = GeminiService.clean_title_casing((topic or "Academic Topic").strip().title())
        q = (clean_q or topic or "").lower().strip()
        is_hinglish = (lang or "").strip().lower() == "hinglish"

        # 1. If LLM provided a valid 5-step roadmap without generic boilerplate, validate and return it
        if isinstance(llm_roadmap, list) and len(llm_roadmap) >= 4:
            valid = True
            cleaned_steps = []
            for i, step in enumerate(llm_roadmap[:5]):
                if not isinstance(step, dict):
                    valid = False
                    break
                c = (step.get("concept") or step.get("title") or "").strip()
                d = (step.get("description") or step.get("summary") or "").strip()
                t = (step.get("type") or "core").strip()
                est = (step.get("estimated_time") or step.get("time") or f"{i+1}-{i+2} hours").strip()
                if not c or not d or "coordinate framework" in d.lower() or d.endswith(":") or len(d) < 15:
                    valid = False
                    break
                cleaned_steps.append({
                    "step": i + 1,
                    "concept": c,
                    "description": d,
                    "type": t,
                    "estimated_time": est
                })
            if valid and len(cleaned_steps) >= 4:
                return cleaned_steps

        # 2. Topic-specific tailored curriculum roadmaps
        # Linked List
        if any(k in q for k in ["linked list", "singly linked", "doubly linked", "circular linked"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Pointers & Node Memory Layout (Basics)", "description": "Dynamic heap memory allocation, node struct jisme data payload aur next pointer address hota hai, aur head/null initialization samajhna.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Operations: Insertion, Deletion & Traversal", "description": "Constant-time O(1) head insertion/deletion, O(n) sequential traversal, aur pointer link reassignment ke invariants master karna.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Algorithmic Patterns: Two-Pointers & In-Place Reversal", "description": "Floyd's cycle detection (Tortoise & Hare), single-pass middle node dhoondna, aur iterative in-place list reversal techniques.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Practice Problems", "description": "High-frequency exam questions: cycle detect aur remove karna, do sorted lists ko O(1) auxiliary space me merge karna, aur palindrome check.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: LRU Cache & Kernel Free Lists", "description": "Doubly Linked List aur Hash Map se O(1) LRU Cache banana, OS kernel process scheduling tables, aur dynamic memory free lists.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Pointers & Node Memory Layout", "description": "Understanding dynamic heap allocation, struct/class node definitions (data payload + pointer address), and head/null pointer initialization.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Operations: Insertion, Deletion & Traversal", "description": "Mastering constant-time O(1) head insertion/deletion, O(n) middle updates, and pointer link reassignment invariants.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Algorithmic Patterns: Two-Pointers & In-Place Reversal", "description": "Floyd's cycle-finding (Tortoise & Hare), single-pass middle node discovery, and iterative vs recursive in-place reversal.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Problem Solving", "description": "Solving high-frequency exam problems: cycle detection and removal, merging two sorted lists in O(1) space, and palindrome verification.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: LRU Cache & Kernel Free Lists", "description": "Implementing O(1) LRU Caches with Doubly Linked Lists and Hash Maps, OS kernel process tables, and memory allocator free lists.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Array & Vector
        if any(k in q for k in ["array", "vector", "dynamic array"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Contiguous Memory & Index Offset Arithmetic (Basics)", "description": "Physical contiguous RAM allocation, Base + i * Size address calculation, aur CPU spatial cache locality ke fayde.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Array Invariants: O(1) Indexing vs O(n) Shifting", "description": "Constant-time O(1) direct index lookup aur insertion/deletion ke dauran element shifting ka O(n) time trade-off samajhna.", "type": "core", "estimated_time": "2-3 hours"},
                    {"step": 3, "concept": "Dynamic Arrays & Amortized Growth", "description": "Buffer capacity doubling strategy, memory re-allocation, aur amortized O(1) append time complexity ka mathematical proof.", "type": "deep_dive", "estimated_time": "3-4 hours"},
                    {"step": 4, "concept": "University & GATE Algorithmic Patterns", "description": "Two-pointer partitioning (Dutch National Flag), sliding window algorithms, binary search variants, aur prefix sum arrays solve karna.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems & Vectorized Buffers", "description": "Row-major vs column-major storage, SIMD parallel vector instructions, GPU tensors, aur low-latency audio/video buffers.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Contiguous Memory & Index Offset Arithmetic", "description": "Physical sequential memory layout, Base + i * Size address offset arithmetic, and CPU spatial cache locality.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Array Invariants: O(1) Indexing vs O(n) Insertion", "description": "Evaluating constant-time random memory addressing against linear-time element shifting required during insertions and deletions.", "type": "core", "estimated_time": "2-3 hours"},
                    {"step": 3, "concept": "Dynamic Arrays & Geometric Amortization", "description": "Buffer doubling growth strategy, memory reallocation overhead, and aggregate proof of amortized O(1) append operations.", "type": "deep_dive", "estimated_time": "3-4 hours"},
                    {"step": 4, "concept": "University & GATE Algorithmic Patterns", "description": "Two-pointer partitioning (Dutch National Flag), sliding window optimizations, binary search variants, and prefix sum arrays.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: SIMD Vectorization & Tensor Buffers", "description": "Row-major vs column-major layouts, SIMD vectorized instructions, GPU memory coalescing, and tensor buffers.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Stack & Queue
        if any(k in q for k in ["stack", "queue", "lifo", "fifo", "deque"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "LIFO vs FIFO Invariants & Buffer Allocation (Basics)", "description": "Stack (LIFO) aur Queue (FIFO) ke boundary conditions, array vs linked-list backing buffers, aur Top/Front pointers initialization.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Operations & Boundary Handling", "description": "Push, Pop, Peek, Enqueue, aur Dequeue operations me Overflow aur Underflow conditions ko deterministic O(1) time me handle karna.", "type": "core", "estimated_time": "2-3 hours"},
                    {"step": 3, "concept": "Circular Queues & Monotonic Stack Patterns", "description": "Modulo arithmetic (i + 1) % N se circular ring buffers banana aur Next Greater Element problems me monotonic stacks ka use.", "type": "deep_dive", "estimated_time": "3-4 hours"},
                    {"step": 4, "concept": "University & GATE Exam Practice Problems", "description": "Infix-to-Postfix conversion, expression evaluation, balanced parentheses parsing, aur queues using two stacks.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Operating Systems & Production Applications", "description": "CPU function call execution frames (Activation Records), browser history back-forward stacks, aur network packet queues.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "LIFO vs FIFO Invariants & Buffer Allocation", "description": "Understanding LIFO and FIFO invariants, backing store allocation (array vs linked list), and pointer boundary initialization.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Operations & Boundary Handling", "description": "Mastering Push/Pop and Enqueue/Dequeue mechanics with deterministic O(1) time and robust Underflow/Overflow validation.", "type": "core", "estimated_time": "2-3 hours"},
                    {"step": 3, "concept": "Circular Ring Buffers & Monotonic Stacks", "description": "Circular buffer index arithmetic via modulo indexing, and monotonic stack patterns for Next Greater Element problems.", "type": "deep_dive", "estimated_time": "3-4 hours"},
                    {"step": 4, "concept": "University & GATE Exam Problem Solving", "description": "Infix-to-postfix operator parsing, recursion stack depth bounds, balanced parentheses, and queue simulation using two stacks.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Operating Systems & Production Architectures", "description": "Call stack frames (Activation Records), browser history undo/redo stacks, and OS inter-process message queues.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Tree & BST
        if any(k in q for k in ["tree", "bst", "binary search tree", "avl", "red black", "b tree"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Hierarchical Nodes & Pointer Tree Topology (Basics)", "description": "Parent-child directed edges, root aur leaf node invariants, aur recursive binary subtrees ka mathematical structure samajhna.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "BST Ordering Property & Tree Traversals", "description": "BST key ordering invariant (Left < Node < Right) aur Pre-order, In-order, Post-order, Level-order (BFS) traversals execute karna.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Self-Balancing Trees & Rotations (AVL / Red-Black)", "description": "Tree skewing O(n) ko rokne ke liye AVL balance factor (-1, 0, +1) aur LL, RR, LR, RL tree rotations ka execution.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Tree Problems", "description": "Lowest Common Ancestor (LCA), tree diameter, binary tree reconstruction from Inorder+Preorder, aur balance height proofs.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: Database Indexes & ASTs", "description": "Database engines (PostgreSQL, MySQL) me B/B+ Tree indexes, compiler Abstract Syntax Trees, aur browser DOM hierarchies.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Hierarchical Nodes & Pointer Tree Topology", "description": "Understanding directed acyclic hierarchies, parent-child edges, root invariants, and structural recursion across subtrees.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "BST Ordering Property & Traversals", "description": "Enforcing BST key invariants (Left < Root < Right) and implementing recursive traversals (In-order, Pre-order, Post-order, Level-order).", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Self-Balancing Trees & Rotations (AVL / Red-Black)", "description": "Preventing O(n) degenerate skewing using AVL balance factors, height tracking, and LL, RR, LR, RL balancing rotations.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Problem Solving", "description": "Solving Lowest Common Ancestor (LCA), diameter calculation, unique tree construction from traversal pairs, and height bounds.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: Database Indexes & Compiler ASTs", "description": "Database B/B+ tree indexing engines (Postgres/MySQL), compiler Abstract Syntax Trees, and browser DOM node graphs.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Booth's Multiplication Algorithm
        if any(k in q for k in ["booth", "booths", "booth's"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Two's Complement Arithmetic & Register Setup (Basics)", "description": "Signed 2's complement binary representation, sign bit extension, aur hardware registers (AC, QR, BR, Qn+1, SC) ka initial setup.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Bit-Pair Decision Rules & Sequential Shifting", "description": "Bit pairs (01 -> Add & ASR, 10 -> Sub & ASR, 00/11 -> ASR) par operations aur Sequence Counter decrement karne ka process.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Hardware Datapath & Arithmetic Sign Extension", "description": "ALU parallel adder/subtractor logic, alternating bit patterns (01010101) ka worst-case analysis, aur ASR sign bit preservation.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "Numerical Trace Tables & Past GATE Problems", "description": "Signed numbers (jaise -5 * +7) ka cycle-by-cycle trace table banana, addition/subtraction counts calculate karna, aur GATE questions.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Modern High-Speed Multipliers: Radix-4 & Wallace Trees", "description": "Radix-4 Modified Booth Algorithm, bit-pair recoding, Wallace Tree reduction, aur modern 64-bit CPU multiplier hardware.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Two's Complement & Register Setup", "description": "Understanding signed 2's complement representation, sign extension, and hardware registers (AC, QR, BR, Qn+1, SC).", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Bit-Pair Decision Rules & Sequential Shifting", "description": "Executing conditional bit-pair transitions (01 -> Add & ASR, 10 -> Sub & ASR, 00/11 -> ASR) and sequence counter decrements.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Hardware Datapath & Arithmetic Sign Extension", "description": "Analyzing ALU parallel adder/subtractor control logic, worst-case alternating bit patterns (01010101), and ASR sign bit replication.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "Numerical Trace Tables & Past GATE Problems", "description": "Practicing full cycle-by-cycle numerical trace tables multiplying positive and negative integers (e.g. -5 * +7), and calculating transition counts.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Modern High-Speed Multipliers: Radix-4 & Wallace Trees", "description": "Exploring Radix-4 Modified Booth Algorithm, bit-pair recoding, Wallace Tree reduction, and modern 64-bit ALU multiplier hardware.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # LRU Page Replacement
        if any(k in q for k in ["lru", "page replacement", "paging", "virtual memory"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Virtual Memory & Frame Allocation (Basics)", "description": "MMU address translation, page tables, page faults ki mechanics, aur physical RAM frame allocation samajhna.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Page Eviction Logic & Recency Tracking", "description": "Cache hit/miss states pehchanna, sabse purane (LRU) page ko evict karna, aur dirty pages ka disk write-back.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Stack Algorithm Property & Belady's Immunity", "description": "Stack algorithm inclusion property M(m,t) ⊆ M(m+1,t) ka formal proof aur Belady's Anomaly se mathematical immunity.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "Reference String Tracing & Hit Ratio Calculations", "description": "Concrete reference strings par 3 aur 4 frames trace karna, Page Fault Frequency (PFF), Hit Ratio, aur EMAT calculate karna.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Kernel Page Management: Clock (Second-Chance) Algorithm", "description": "Real-world Linux kernel page reclamation, Clock (Second-Chance) algorithm with reference bits, aur kswapd daemon architecture.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Virtual Memory & Frame Allocation", "description": "Understanding MMU address translation, page tables, page faults, and physical RAM frame allocation.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Page Eviction Logic & Recency Tracking", "description": "Identifying hit/miss states, evicting the least recently referenced page, and handling dirty bit write-backs.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Stack Algorithm Property & Belady's Immunity", "description": "Formal proof of inclusion property M(m,t) ⊆ M(m+1,t), proving mathematical immunity to Belady's Anomaly unlike FIFO.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "Reference String Tracing & Hit Ratio Calculations", "description": "Tracing concrete reference strings across 3 and 4 frames, calculating Page Fault Frequency (PFF), Hit Ratio, and Effective Memory Access Time (EMAT).", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Kernel Page Management: Clock (Second-Chance) Algorithm", "description": "Analyzing practical Linux kernel page reclamation, Clock (Second-Chance) algorithm with reference bits, and page frame reclaim daemons (kswapd).", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Graph & Dijkstra
        if any(k in q for k in ["graph", "dijkstra", "bfs", "dfs", "shortest path"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Graph Representations & Priority Queues (Basics)", "description": "Adjacency List vs Adjacency Matrix, directed/undirected graphs, aur Min-Heap priority queue initialization.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Exploration: Edge Relaxation & Greedy Choice", "description": "Distance array initialization, edge relaxation invariant (dist[v] > dist[u] + w), aur greedy vertex selection.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Complexity Proofs & Negative Edge Limitations", "description": "O((V + E) log V) time complexity proof, Fibonacci heap bounds, aur negative edge cycles me failure reasons.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Graph Problems", "description": "Shortest path trace tables, Bellman-Ford vs Dijkstra comparison, Topological sorting, aur DAG shortest paths.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: Network Routing & GPS Navigation", "description": "OSPF internet gateway routing protocols, Google Maps road network routing, aur packet switching topologies.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Graph Representations & Priority Queues", "description": "Understanding Adjacency List vs Matrix storage, weighted directed graphs, and Min-Heap priority queue initialization.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Exploration: Edge Relaxation & Greedy Choice", "description": "Mastering edge relaxation invariants (dist[v] > dist[u] + w), distance array updates, and greedy vertex expansion.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Complexity Proofs & Negative Edge Limitations", "description": "Rigorous proof of O((V + E) log V) running time, Fibonacci heap optimizations, and failure cases on negative weight edges.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Graph Problems", "description": "Shortest path state tables, Bellman-Ford comparisons, cycle detection, and topological sorting problem sets.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: OSPF Routing & GPS Navigation", "description": "Internet routing protocols (OSPF, IS-IS), large-scale road network navigation (A* search), and network packet switching.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Sorting Algorithms
        if any(k in q for k in ["sorting", "quicksort", "merge sort", "heap sort", "bubble sort"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Comparison Models & Inversions (Basics)", "description": "Element comparisons, array inversion pairs, aur stability (stable vs unstable sorting) ke core definitions.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Sorting Mechanics: Partitioning & Merging", "description": "Pivot selection (Lomuto/Hoare partitioning) ya recursive divide-and-conquer two-way merge procedure master karna.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Asymptotic Lower Bounds & Complexity Proofs", "description": "Comparison sorting ka theoretical lower bound Omega(n log n) proof, recurrence relations T(n) = 2T(n/2) + O(n), aur worst-case bounds.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Sorting Problems", "description": "Tracing pass-by-pass iterations, recursion tree depth, in-place auxiliary space comparisons, aur past GATE questions.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: TimSort & Distributed Sort", "description": "Python aur Java me use hone wala hybrid TimSort algorithm, external disk sorting, aur distributed MapReduce pipelines.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Comparison Models & Inversions", "description": "Understanding decision tree bounds, array inversion pairs, and sorting stability guarantees.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Core Sorting Mechanics: Partitioning & Merging", "description": "Mastering pivot partitioning (Lomuto/Hoare) or recursive divide-and-conquer two-way merge procedures.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Asymptotic Lower Bounds & Complexity Proofs", "description": "Information-theoretic lower bound Omega(n log n) proof, recurrence tree analysis, and worst-case degeneracy proofs.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Problem Solving", "description": "Solving pass-by-pass tracing, recursion stack memory calculations, in-place stability trade-offs, and GATE MCQs.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Systems: TimSort & External Sorting", "description": "Modern hybrid algorithms (TimSort, IntroSort), multi-way external merge sorting for disk buffers, and distributed pipelines.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Database & Normalization
        if any(k in q for k in ["database", "normalization", "bcnf", "3nf", "sql", "dbms"]):
            if is_hinglish:
                return [
                    {"step": 1, "concept": "Relational Schema & Functional Dependencies (Basics)", "description": "Relational tables, functional dependencies (X -> Y), candidate keys, aur prime attributes ka identification.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Normal Forms Progression (1NF to BCNF)", "description": "Redundancy aur anomalies (Insertion, Deletion, Update) ko khatam karne ke liye 1NF, 2NF, 3NF, aur BCNF ke rules.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Decomposition: Lossless Join & Dependency Preservation", "description": "Lossless join decomposition test (R1 ∩ R2 -> R1 ya R2) aur dependency preservation guarantees ka formal verification.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Normalization Problems", "description": "Candidate keys dhoondna, canonical cover / minimal cover nikaalna, aur highest normal form identify karna.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Database Architecture & Indexing", "description": "PostgreSQL aur MySQL me normalized vs denormalized read-heavy architectures, B+ tree indexes, aur ACID transactions.", "type": "advanced", "estimated_time": "3 hours"}
                ]
            else:
                return [
                    {"step": 1, "concept": "Relational Schema & Functional Dependencies", "description": "Understanding relational schema definitions, functional dependency closures (X -> Y), and candidate key identification.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                    {"step": 2, "concept": "Normal Forms Progression (1NF to BCNF)", "description": "Systematic elimination of insertion, deletion, and update anomalies across 1NF, 2NF, 3NF, and Boyce-Codd Normal Form.", "type": "core", "estimated_time": "3-4 hours"},
                    {"step": 3, "concept": "Decomposition: Lossless Join & Preservation", "description": "Formal testing for lossless-join decomposition (R1 ∩ R2 -> R1 or R2) and functional dependency preservation.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                    {"step": 4, "concept": "University & GATE Exam Problem Solving", "description": "Computing attribute closures, finding minimal/canonical covers, and classifying relation schemas into highest normal forms.", "type": "practice", "estimated_time": "4 hours"},
                    {"step": 5, "concept": "Production Database Architecture & Indexing", "description": "Evaluating OLTP normalized designs vs OLAP denormalized read models, B+ tree index optimization, and ACID transactions.", "type": "advanced", "estimated_time": "3 hours"}
                ]

        # Generic Domain Fallback (Clean, authentic, topic-tailored, zero weird words)
        if is_hinglish:
            return [
                {"step": 1, "concept": f"Prerequisites & Foundations of {clean_topic}", "description": f"{clean_topic} ke basic definitions, prerequisite mathematical aur structural concepts ko samajhna.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                {"step": 2, "concept": f"Core Governing Principles of {clean_topic}", "description": f"{clean_topic} ke fundamental rules, state transitions, aur core governing mechanics ko master karna.", "type": "core", "estimated_time": "3-4 hours"},
                {"step": 3, "concept": f"Theoretical Deep Dive & Edge Cases", "description": f"Detailed mathematical analysis, boundary conditions, aur analytical edge cases ka rigorous study.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                {"step": 4, "concept": f"University & Exam Problem Solving", "description": f"Standard numerical derivations, theoretical proofs, aur past semester exam problems solve karna.", "type": "practice", "estimated_time": "4 hours"},
                {"step": 5, "concept": f"Modern Practical Applications & Scalability", "description": f"Real-world systems, industrial implementations, aur modern scalable engineering architectures.", "type": "advanced", "estimated_time": "3 hours"}
            ]
        else:
            return [
                {"step": 1, "concept": f"Prerequisites & Foundations of {clean_topic}", "description": f"Foundational definitions, prerequisite mathematics, and conceptual framing essential for {clean_topic}.", "type": "prerequisite", "estimated_time": "1-2 hours"},
                {"step": 2, "concept": f"Core Governing Principles of {clean_topic}", "description": f"Mastering fundamental mechanisms, operational invariants, and primary governing equations of {clean_topic}.", "type": "core", "estimated_time": "3-4 hours"},
                {"step": 3, "concept": f"Theoretical Deep Dive & Edge Cases", "description": f"Rigorous analytical derivation, boundary condition analysis, and systemic constraints of {clean_topic}.", "type": "deep_dive", "estimated_time": "3-5 hours"},
                {"step": 4, "concept": f"University & Competitive Exam Problem Solving", "description": f"Solving standard numerical derivations, state transition exercises, and past university examination problem sets.", "type": "practice", "estimated_time": "4 hours"},
                {"step": 5, "concept": f"Modern Practical Applications & Scalability", "description": f"Real-world production engineering, industrial implementations, and scalable system architectures.", "type": "advanced", "estimated_time": "3 hours"}
            ]

    @staticmethod
    def generate_topic_details(query: str, lang: str = "english") -> Dict[str, Any]:
        """Generates real-time, dynamic academic topic details using Google Gemini LLM SDK.
        Strictly enforces clean structured JSON with exact required keys.
        Supports both 'english' and 'hinglish' language modes.
        """
        clean_q = GeminiService.clean_search_query(query)
        if not clean_q:
            clean_q = query.strip()

        if not clean_q:
            raise ValueError("Query cannot be empty.")

        api_key = config.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError("Gemini API key is not configured. Real LLM generation requires GEMINI_API_KEY.")

        detected_domain = GeminiService._detect_academic_domain(clean_q)
        is_hinglish = (lang or "").strip().lower() == "hinglish"

        if is_hinglish:
            language_mandate = (
                "7. LANGUAGE MANDATE - FULL NATURAL HINGLISH EXPLANATION MODE:\n"
                "   - You MUST write ALL explanations, analysis, and walkthrough fields in NATURAL, CONVERSATIONAL HINGLISH (Hindi written in Roman/English script mixed with standard English Computer Science & Engineering terms):\n"
                "     * 'overview': Natural conversational Hinglish summary explaining the core concept, formal definitions, and invariants.\n"
                "     * 'ai_evaluation': Technical complexity evaluation, semester exam significance, and GATE focus in Hinglish.\n"
                "     * 'theoretical_foundations': Hardware / memory model, register architecture, and theoretical foundations in Hinglish.\n"
                "     * 'core_formulations': Step-by-step algorithm, state transitions, and complexity bounds in Hinglish.\n"
                "     * 'detailed_breakdown': Complete exam-ready breakdown with all 6 structured sections (Core Concept & Invariants, Hardware Registers & Architecture, Step-by-Step Procedure, Worked Numerical Trace Table with real numbers, Advantages/Comparisons, and University/GATE Exam Questions) written in natural conversational Hinglish!\n"
                "     * In 'quick_example':\n"
                "       - 'title': Relatable, catchy Hinglish title.\n"
                "       - 'badge': 'Worked Numerical Trace (Hinglish)'.\n"
                "       - 'scenario': Concrete problem statement or systems scenario written in conversational Hinglish.\n"
                "       - 'breakdown': Step-by-step trace walkthrough written in Hinglish (e.g., '1. **Pehla Step**: ...\\n2. **Dusra Step**: ...\\n3. **Result / Kaam Kaise Hua**: ...').\n"
                "       - 'use_cases': Every application's 'title', 'impact', and 'description' MUST be written in natural Hinglish.\n"
                "       - 'tradeoffs': BOTH 'advantages' (faayde) and 'disadvantages' (nuksaan / limitations) MUST be written in natural Hinglish.\n"
                "       - 'takeaway': The key takeaway ('Sabse Main Baat') MUST be written in natural Hinglish.\n"
                "     * 'did_you_know': Academic or historical trivia written in Hinglish.\n"
                "   - KEEP ALL CORE TECHNICAL TERMS, REGISTER NAMES, AND SYMBOLS STRICTLY IN ENGLISH: e.g., 'AC', 'QR', 'BR', 'Qn+1', 'SC', 'ALU', 'Multiplicand', 'Multiplier', 'Arithmetic Shift Right (ASR)', 'Two\\'s Complement', 'Array', 'Pointer', 'Memory Address', 'Time Complexity', 'Space Complexity', 'Big-O', 'Cache', 'Paging', 'Page Fault', 'LRU', 'Hit Ratio', 'Binary Tree', 'Stack', 'Queue', 'Linked List', 'Hash Table', 'Graph', 'CPU', 'Operating System', 'Thread', 'Algorithm', 'Base Address', 'Sizeof', 'Force', 'Inertia', 'Friction', 'Acceleration'. Do NOT translate technical terms into obscure pure Hindi (e.g. use 'Inertia', NOT 'Jadatva'; use 'Friction', NOT 'Gharshan'; use 'Array', NOT 'Krambaddh Suchi').\n"
                "   - Output format MUST be 100% valid JSON matching the exact schema below.\n\n"
            )
        else:
            language_mandate = (
                "7. LANGUAGE MANDATE: Provide all explanations, overviews, specifications, trace tables, trade-offs, and exam questions in standard, clear, authoritative academic English tailored for B.Tech CSE and GATE examinations.\n\n"
            )

        # STRICT LLM Prompt mandating university exam depth, genuine formulas, register models, trace tables
        prompt = (
            f"You are a distinguished University Professor and Senior Academic Evaluator for B.Tech Computer Science & Engineering and GATE examinations.\n"
            f"Evaluate and synthesize the syllabus topic: \"{clean_q}\" (Academic Discipline: \"{detected_domain}\").\n\n"
            f"GOAL: Deliver a complete, exhaustive, and exam-ready technical breakdown tailored for university semester finals and competitive exams (B.Tech CSE / GATE) instead of a generic summary.\n\n"
            f"CRITICAL SYSTEM DIRECTIVES:\n"
            f"1. TOPIC DEPTH & RIGOR (B.TECH CSE / GATE EXAM STANDARD):\n"
            f"   - Provide full technical specifications, exact formulas, recurrence relations, and asymptotic bounds (Big-O, Big-Omega, Big-Theta) in LaTeX math delimiters ($...$ for inline, $$...$$ for standalone block equations).\n"
            f"   - For Computer Organization & Architecture, Operating Systems, and Hardware topics (e.g., Booth's Algorithm, Cache Mapping, Paging, Virtual Memory, Pipeline Hazards, Interrupt Handling), explicitly document the HARDWARE / MEMORY MODEL: register setup (e.g., AC, QR, BR, Qn+1, SC), bit-width constraints, bus/datapath architecture, and exact step-by-step state transitions.\n"
            f"   - For Algorithms & Data Structures, specify structural invariants, pointer layouts, recurrence trees, and exact computational complexity bounds.\n"
            f"2. MANDATORY STRUCTURED SECTIONS:\n"
            f"   - 'overview': CORE CONCEPT & INVARIANTS — Formal definitions, mathematical/architectural foundations, fundamental invariants, and syllabus role. NO boilerplate intros like 'In the context of...'. Directly define {clean_q} with academic precision.\n"
            f"   - 'theoretical_foundations': HARDWARE / MEMORY MODEL & ARCHITECTURAL FOUNDATION — Register setup (e.g., AC, QR, BR, Qn+1, SC), bit-width constraints, memory layout, cache hierarchy, or mathematical invariant proofs with LaTeX formatting.\n"
            f"   - 'core_formulations': STEP-BY-STEP ALGORITHM / PROCEDURE & COMPLEXITY BOUNDS — Sequential execution steps with exact conditional transitions (e.g., bit pairs: 01 -> Add BR to AC & Arithmetic Shift Right, 10 -> Subtract BR from AC & Arithmetic Shift Right, 00/11 -> Arithmetic Shift Right only), recurrence relations, and exact Time and Space complexities ($O(n)$, $O(\\log n)$, etc.).\n"
            f"   - 'detailed_breakdown': COMPLETE EXAM-READY BREAKDOWN in GFM Markdown with clear sections:\n"
            f"     ### 1. Core Concept & Invariants\n"
            f"     ### 2. Hardware / Memory Model (Registers & Architecture)\n"
            f"     ### 3. Step-by-Step Algorithm & State Transitions\n"
            f"     ### 4. Worked Numerical Example & Complete Trace Table (MANDATORY: Must include a complete Markdown trace table with concrete numbers, e.g. multiplying -5 x +7 showing Step/Cycle, Operation, AC, QR, Qn+1, SC, and Explanation; or tracing page references for LRU; or tracing BST insertions step-by-step with state transitions)\n"
            f"     ### 5. Advantages, Trade-offs & Comparisons (What makes it fast/efficient vs traditional alternatives, e.g. Booth's vs standard shift-add multiplication)\n"
            f"     ### 6. Common University Exam / GATE / Interview Questions (Top 2-3 frequently asked exam/GATE questions with concise model answers and traps)\n"
            f"   - 'quick_example':\n"
            f"     * 'title': Concrete Numerical Problem or Real-Life Systems Application Title\n"
            f"     * 'badge': 'Worked Numerical Trace | B.Tech & GATE Exam Walkthrough'\n"
            f"     * 'scenario': Concrete problem statement (e.g., 'Multiply Multiplicand M = -5 (1011) and Multiplier Q = +7 (0111) using 4-bit Booth Multiplier') or practical operational setup\n"
            f"     * 'breakdown': 3-step sequential execution breakdown of the numerical trace or algorithm\n"
            f"     * 'use_cases': 3 realistic production/hardware/systems applications\n"
            f"     * 'tradeoffs': 'advantages' (performance gains) and 'disadvantages' (hardware overhead or corner cases)\n"
            f"     * 'takeaway': Golden rule or exam formula to remember\n"
            f"   - 'ai_evaluation': 2-3 sentence technical complexity evaluation, GATE exam weightage, and critical edge cases\n"
            f"   - 'did_you_know': Authentic historical discovery or architectural milestone\n"
            f"3. STRICT JSON OUTPUT MANDATE:\n"
            f"   - Return ONLY a raw valid JSON object. Do NOT wrap the JSON in markdown code fences (like ```json ... ```). Zero text before or after the JSON.\n"
            f"   - In JSON strings, ensure any LaTeX backslashes are double-escaped (e.g. \\\\alpha, \\\\frac, \\\\Theta, \\\\mathcal{{O}}).\n"
            f"   - All quotes inside string values must be escaped.\n\n"
            f"{language_mandate}"
            f"REQUIRED JSON SCHEMA:\n"
            f"{{\n"
            f"  \"topic\": \"{GeminiService.clean_title_casing(clean_q.title())}\",\n"
            f"  \"category\": \"{detected_domain}\",\n"
            f"  \"difficulty_score\": 7.5,\n"
            f"  \"difficulty_level\": \"Advanced\",\n"
            f"  \"ai_evaluation\": \"2-3 sentence technical evaluation, GATE weightage, and complexity traps...\",\n"
            f"  \"overview\": \"Formal academic definition, core concept, invariants, and syllabus importance without boilerplate...\",\n"
            f"  \"theoretical_foundations\": \"Hardware/memory model, register architecture (e.g. AC, QR, BR, Qn+1, SC), bit-widths, and architectural foundations...\",\n"
            f"  \"core_formulations\": \"Step-by-step sequential algorithm, state transitions (e.g. 01 -> Add & Shift, 10 -> Subtract & Shift), explicit formulas, and time/space complexity...\",\n"
            f"  \"detailed_breakdown\": \"Exhaustive Markdown lecture breakdown containing: ### 1. Core Concept & Invariants\\n\\n### 2. Hardware / Memory Model (Registers & Architecture)\\n\\n### 3. Step-by-Step Algorithm & State Transitions\\n\\n### 4. Worked Numerical Example & Complete Trace Table\\n| Step | Operation | AC | QR | Qn+1 | SC | Description |\\n|---|---|---|---|---|---|---|\\n...\\n\\n### 5. Advantages, Trade-offs & Comparisons\\n\\n### 6. Common University Exam / GATE / Interview Questions\\n...\",\n"
            f"  \"quick_example\": {{\n"
            f"    \"title\": \"Concrete Numerical Walkthrough or Real-Life Problem Title\",\n"
            f"    \"badge\": \"Worked Numerical Trace | B.Tech & GATE Exam Walkthrough\",\n"
            f"    \"scenario\": \"Concrete problem statement with specific numbers or real-life engineering setup...\",\n"
            f"    \"breakdown\": \"1. **Step 1**: ...\\n2. **Step 2**: ...\\n3. **Step 3**: ...\",\n"
            f"    \"use_cases\": [\n"
            f"      {{\"title\": \"System/App 1\", \"impact\": \"Hardware/System Role\", \"description\": \"2 clear sentences on usage...\"}},\n"
            f"      {{\"title\": \"System/App 2\", \"impact\": \"Hardware/System Role\", \"description\": \"2 clear sentences on usage...\"}},\n"
            f"      {{\"title\": \"System/App 3\", \"impact\": \"Hardware/System Role\", \"description\": \"2 clear sentences on usage...\"}}\n"
            f"    ],\n"
            f"    \"takeaway\": \"Golden rule or formula to remember for university and GATE exams.\",\n"
            f"    \"tradeoffs\": {{\n"
            f"      \"advantages\": \"Key performance advantages (e.g. skips shifts over sequences of 1s)...\",\n"
            f"      \"disadvantages\": \"Key limitations or hardware trade-offs...\"\n"
            f"    }}\n"
            f"  }},\n"
            f"  \"did_you_know\": \"Authentic historical or architectural trivia specifically about {clean_q}.\"\n"
            f"}}"
        )

        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
        raw_text = None
        last_err = None

        # 1. Primary: Use official modern google.genai client
        client = GeminiService.get_client()
        if client:
            try:
                from google.genai import types
                for m_name in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=m_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.1,
                                response_mime_type="application/json",
                                max_output_tokens=5000
                            )
                        )
                        if response and response.text and response.text.strip():
                            raw_text = response.text.strip()
                            break
                    except Exception as m_err:
                        last_err = m_err
                        continue
            except Exception as client_err:
                last_err = client_err

        # 2. Fallback: Try with new client instance if singleton had an issue
        if not raw_text:
            try:
                from google import genai
                from google.genai import types
                fresh_client = genai.Client(api_key=api_key)
                for m_name in candidate_models:
                    try:
                        response = fresh_client.models.generate_content(
                            model=m_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.1,
                                response_mime_type="application/json",
                                max_output_tokens=5000
                            )
                        )
                        if response and response.text and response.text.strip():
                            raw_text = response.text.strip()
                            break
                    except Exception as m_err:
                        last_err = m_err
                        continue
            except Exception as fresh_err:
                last_err = fresh_err

        parsed_data = {}
        if raw_text:
            try:
                parsed_data = GeminiService._clean_and_parse_llm_json(raw_text)
            except Exception as parse_err:
                print(f"[GeminiService] Failed to parse LLM JSON: {parse_err}. Generating synthetic fallback.")
                parsed_data = {}

        # If LLM was unavailable, quota-restricted, or returned incomplete data,
        # seamlessly synthesize authentic textbook-grade academic data so the platform runs anywhere.
        if not parsed_data or not (parsed_data.get("overview") and parsed_data.get("theoretical_foundations") and parsed_data.get("core_formulations")):
            print(f"[GeminiService] Live Gemini response unavailable or incomplete. Synthesizing authentic academic intelligence for: '{clean_q}' (lang={lang})")
            parsed_data = GeminiService._synthesize_academic_fallback(clean_q, detected_domain, lang=lang)

        # Enforce required fields
        topic = GeminiService.clean_title_casing(parsed_data.get("topic") or clean_q.title())
        category = parsed_data.get("category") or detected_domain
        overview = GeminiService.ensure_math_delimiters(GeminiService.clean_context_boilerplate((parsed_data.get("overview") or "").strip()))
        tf = GeminiService.ensure_math_delimiters((parsed_data.get("theoretical_foundations") or "").strip())
        cf = GeminiService.ensure_math_delimiters((parsed_data.get("core_formulations") or "").strip())
        ai_eval = GeminiService.ensure_math_delimiters((parsed_data.get("ai_evaluation") or "").strip())

        # Parse difficulty score and level
        diff_score = 7.3
        try:
            raw_score = parsed_data.get("difficulty_score")
            if raw_score is not None:
                diff_score = float(raw_score)
                if diff_score < 1.0 or diff_score > 10.0:
                    diff_score = 7.3
        except (ValueError, TypeError):
            diff_score = 7.3

        diff_level = parsed_data.get("difficulty_level")
        if not diff_level or diff_level not in ["Beginner", "Intermediate", "Advanced"]:
            diff_level = "Advanced" if diff_score > 7.0 else ("Intermediate" if diff_score > 4.5 else "Beginner")

        did_you_know = GeminiService.ensure_math_delimiters((parsed_data.get("did_you_know") or f"Historical and theoretical foundations of {topic}.").strip())
        raw_db = parsed_data.get("detailed_breakdown") or parsed_data.get("detailedBreakdown")
        if raw_db and len(raw_db.strip()) > 80:
            detailed_breakdown = GeminiService.ensure_math_delimiters(raw_db.strip())
        else:
            detailed_breakdown = f"### 1. Theoretical Foundations & Architecture\n\n{tf}\n\n### 2. Step-by-Step Algorithm & Formulations\n\n{cf}"

        raw_notes = parsed_data.get("study_notes")
        if not raw_notes or len(raw_notes.strip()) < 50:
            if detailed_breakdown and len(detailed_breakdown.strip()) > 200:
                raw_notes = (
                    f"# Complete University & GATE Study Notes: {topic}\n\n"
                    f"{overview}\n\n"
                    f"{detailed_breakdown}\n\n"
                    f"## Key Takeaway & Exam Insight\n\n"
                    f"> {did_you_know}"
                )
            else:
                try:
                    from backend.routes.topic_notes_engine import build_realistic_topic_notes
                    raw_notes = build_realistic_topic_notes(topic, category)
                except Exception:
                    raw_notes = (
                        f"# Executive Overview: {topic}\n\n"
                        f"{overview}\n\n"
                        f"## 1. Key Concepts & Theoretical Foundations\n\n"
                        f"{tf}\n\n"
                        f"## 2. Syntax & Implementation / Core Formulations\n\n"
                        f"{cf}\n\n"
                        f"## 3. Complexity Breakdown: Key Rules & Analysis\n\n"
                        f"{ai_eval}\n\n"
                        f"## 4. Common Pitfalls & Exam Edge Cases\n\n"
                        f"Ensure precise boundary checks, type matching, and valid initial conditions.\n\n"
                        f"## 5. University Exam: Practice Problems & Focus\n\n"
                        f"> **Academic Takeaway & Historical Insight:** {did_you_know}"
                    )
        study_notes = GeminiService.sanitize_study_notes(GeminiService.ensure_math_delimiters(raw_notes))
        # Topic-specific curriculum roadmap
        roadmap = GeminiService.build_topic_roadmap(topic, clean_q, category, lang=lang, llm_roadmap=parsed_data.get("roadmap"))

        raw_qe = parsed_data.get("quick_example") or parsed_data.get("quickExample")
        quick_example = GeminiService.build_quick_example(topic, category, cf, overview, llm_example=raw_qe, lang=lang)

        return {
            # Required exact schema fields
            "topic": topic,
            "category": category,
            "difficulty_score": diff_score,
            "difficulty_level": diff_level,
            "ai_evaluation": ai_eval,
            "overview": overview,
            "theoretical_foundations": tf,
            "core_formulations": cf,
            "quick_example": quick_example,
            "quickExample": quick_example,
            # Supporting fields for OmniLearn full-stack UI compatibility
            "title": topic,
            "query": clean_q,
            "summary": overview,
            "detailed_breakdown": detailed_breakdown,
            "detailedBreakdown": detailed_breakdown,
            "domain": category,
            "difficultyScore": diff_score,
            "difficultyLevel": diff_level,
            "difficulty_reasons": ai_eval,
            "aiEvaluation": ai_eval,
            "did_you_know": did_you_know,
            "didYouKnow": did_you_know,
            "fun_fact": did_you_know,
            "study_notes": study_notes,
            "notes_content": study_notes,
            "careers": GeminiService.map_topic_to_careers(clean_q),
            "careerRelevance": f"Applied across engineering systems and research specializations in {category} relevant to {topic}.",
            "exam_frequency": [10, 14, 18, 22, 25],
            "examFrequency": [10, 14, 18, 22, 25],
            "roadmap": roadmap,
            "diagram": GeminiService.build_topic_diagram(topic, clean_q, category)
        }


    @staticmethod
    def build_topic_diagram(topic_title: str, clean_q: str, detected_domain: str) -> dict:
        """Delegates to DiagramEngine to generate responsive vector diagrams."""
        from backend.services.diagram_engine import DiagramEngine
        return DiagramEngine.build_diagram(clean_q, topic_title, detected_domain)

    @staticmethod
    def build_topic_context(clean_q: str, detected_domain: str, lang: str = "english") -> dict:
        """Delegates to TopicContextEngine to generate rich, textbook-grade academic context."""
        from backend.services.topic_context_engine import TopicContextEngine
        return TopicContextEngine.build_topic_context(clean_q, detected_domain, lang=lang)

    @staticmethod
    def _synthesize_academic_fallback(clean_q: str, detected_domain: str, lang: str = "english") -> dict:
        """Synthesizes rich, textbook-grade academic intelligence for any topic across disciplines.
        Guarantees that OmniLearn runs anywhere reliably with rich context, use cases, and zero generic placeholders.
        """
        topic = GeminiService.clean_title_casing(clean_q.title())

        # 1. Generate clean, intuitive real-life analogies and everyday use cases
        quick_example = GeminiService.build_quick_example(topic, detected_domain, lang=lang)

        # 2. Generate comprehensive, multi-section academic context
        ctx = GeminiService.build_topic_context(clean_q, detected_domain, lang=lang)

        db_fallback = ctx.get("detailed_breakdown")
        if not db_fallback:
            tf_part = ctx.get("theoretical_foundations", "")
            cf_part = ctx.get("core_formulations", "")
            db_fallback = f"### 1. Theoretical Foundations & Architecture\n\n{tf_part}\n\n### 2. Step-by-Step Algorithm & Formulations\n\n{cf_part}"

        roadmap = GeminiService.build_topic_roadmap(topic, clean_q, detected_domain, lang=lang)

        return {
            "topic": ctx["topic"],
            "category": ctx["category"],
            "difficulty_score": ctx["difficulty_score"],
            "difficulty_level": ctx["difficulty_level"],
            "ai_evaluation": ctx["ai_evaluation"],
            "overview": ctx["overview"],
            "theoretical_foundations": ctx["theoretical_foundations"],
            "core_formulations": ctx["core_formulations"],
            "detailed_breakdown": db_fallback,
            "detailedBreakdown": db_fallback,
            "quick_example": quick_example,
            "quickExample": quick_example,
            "roadmap": roadmap,
            "did_you_know": ctx["did_you_know"],
            "diagram": ctx.get("diagram") or GeminiService.build_topic_diagram(topic, clean_q, detected_domain)
        }

    @staticmethod
    def generate_fallback_topic_details(query: str, lang: str = "english") -> dict:
        """Public method to safely produce complete topic details without throwing HTTP 500 errors."""
        clean_q = GeminiService.clean_search_query(query) or query.strip()
        return GeminiService.generate_topic_details(clean_q, lang=lang)

    @staticmethod
    def generate_detailed_notes(subject_title: str, chapters: str) -> str:
        """Generates comprehensive, multi-section study revision notes (800-1500+ words) using Gemini."""
        api_key = config.GEMINI_API_KEY
        if api_key:
            prompt = (
                f"Act as a distinguished senior academic professor and department chair.\n"
                f"Create comprehensive, highly detailed, multi-page university study revision notes for:\n"
                f"Subject/Unit Name: {subject_title}\n"
                f"Topics & Chapters to cover: {chapters}\n\n"
                f"Requirements:\n"
                f"1. Length & Depth: Exhaustive academic revision notes. Do NOT abbreviate or summarize.\n"
                f"2. LaTeX Mathematics: Format formulas using standard LaTeX ($...$ for inline, $$...$$ for display block equations). Include ONLY equations genuinely applicable to {subject_title}.\n"
                f"3. Structure: Use clean Markdown structure with these exact mandatory sections:\n\n"
                f"## Executive Overview: Core Definition & Intuition\n"
                f"Deep theoretical breakdown and real-world engineering applications of {subject_title}.\n\n"
                f"## Key Concepts & Theoretical Foundations: Fundamental Formulas & Derivations\n"
                f"Governing principles and rigorous mathematical derivations formatted in LaTeX display equations.\n\n"
                f"## Syntax & Implementation: Step-by-Step Worked Examples\n"
                f"Minimum 2-3 complete step-by-step solved academic problems with clean code snippets or detailed mathematical steps.\n\n"
                f"## Complexity Breakdown: Key Rules & Cheatsheet Mnemonics\n"
                f"Asymptotic Big-O breakdown table and cheatsheet rules/mnemonics.\n\n"
                f"## Common Mistakes & Exam Pitfalls\n"
                f"Critical edge cases and exam pitfalls where students lose marks.\n\n"
                f"## University Exam: Practice Problems with Answers & Focus Points\n"
                f"Top 3 practice exam questions with explicit final answers and key exam focus points.\n"
            )
            candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-flash-latest"]
            
            client = GeminiService.get_client()
            if not client:
                try:
                    from google import genai
                    client = genai.Client(api_key=api_key)
                except Exception:
                    client = None

            if client:
                try:
                    from google.genai import types
                    for m_name in candidate_models:
                        try:
                            response = client.models.generate_content(
                                model=m_name,
                                contents=prompt,
                                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=8192)
                            )
                            if response and response.text and response.text.strip():
                                return GeminiService.sanitize_study_notes(response.text.strip())
                        except Exception:
                            continue
                except Exception as e:
                    print(f"Failed to generate notes via Gemini: {e}")

        # Realistic domain-aware fallback using topic_notes_engine
        try:
            from backend.routes.topic_notes_engine import build_realistic_topic_notes
            return GeminiService.sanitize_study_notes(build_realistic_topic_notes(subject_title, chapters))
        except Exception as err:
            print(f"Topic notes engine fallback notice: {err}")

        # Static safety fallback
        fallback_notes = (
            f"# Executive Overview: Core Definition & Intuition\n"
            f"{subject_title} represents a core academic unit focusing on: {chapters}. "
            f"Mastering this domain requires systematic comprehension of its operational mechanics, algorithmic structures, and mathematical foundations.\n\n"
            f"## Key Concepts & Theoretical Foundations: Fundamental Formulas & Derivations\n"
            f"Core topics covered in this unit: {chapters}.\n"
            f"- Foundational Principles: System state transitions, asymptotic invariants, and analytical correctness.\n"
            f"- Theoretical Properties: Convergence criteria and boundary behaviors governing {subject_title}.\n\n"
            f"## Syntax & Implementation: Step-by-Step Worked Examples\n"
            f"### Worked Example 1: Core Algorithm Evaluation\n"
            f"```python\n"
            f"# Standard formulation for {subject_title}\n"
            f"def evaluate_algorithm(dataset):\n"
            f"    if not dataset:\n"
            f"        return None\n"
            f"    return [item for item in dataset if item is not None]\n"
            f"```\n\n"
            f"## Complexity Breakdown: Key Rules & Cheatsheet Mnemonics\n"
            f"| Operation / Stage | Time Complexity | Space Complexity |\n"
            f"| :--- | :--- | :--- |\n"
            f"| Primary Operation | $O(N)$ | $O(1)$ |\n"
            f"| Auxiliary Processing | $O(N \\log N)$ | $O(N)$ |\n\n"
            f"### Cheatsheet Mnemonics\n"
            fr"- **Master Theorem**: Compare $f(n)$ with $n^{{\\log_b a}}$ to immediately determine asymptotic growth.\n"
            fr"- **Invariant Verification**: Check base cases before recursive termination.\n\n"
            f"## Common Mistakes & Exam Pitfalls\n"
            f"- Forgetting boundary base cases ($N=0$) before loop termination.\n"
            f"- Confusing time complexity with auxiliary space complexity under recursive calls.\n\n"
            f"## University Exam: Practice Problems with Answers & Focus Points\n"
            f"1. **Problem 1**: Solve the recurrence $T(n) = 2T(n/2) + O(n)$.\n"
            f"   - *Answer*: By Master Theorem Case 2, $T(n) = \\Theta(n \\log n)$.\n\n"
            f"2. **Problem 2**: State the worst-case space complexity of recursive depth $d$.\n"
            f"   - *Answer*: $O(d)$ stack frames."
        )
        return GeminiService.sanitize_study_notes(fallback_notes)

