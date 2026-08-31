import json
import re
import httpx
from typing import Dict, Any, List, Optional
from backend import config

class GeminiService:
    @staticmethod
    def clean_search_query(query: str) -> str:
        """Strips conversational noise and filler words to find the core academic search terms."""
        cleaned = query.strip()
        # Remove common conversational prefixes
        prefixes = [
            r'^(what is|what are|explain|how does|how do|how to|notes on|tutorial on|derivation of|overview of|define|introduction to|details about|information on|summary of|concept of)\s+',
            r'^(can you explain|tell me about|give me notes for|give me information on)\s+'
        ]
        for p in prefixes:
            cleaned = re.sub(p, '', cleaned, flags=re.IGNORECASE).strip()
            
        # Remove common trailing fillers
        suffixes = [
            r'\s+(in detail|with examples|step by step|for beginners|exam prep|simplified|easily)$'
        ]
        for s in suffixes:
            cleaned = re.sub(s, '', cleaned, flags=re.IGNORECASE).strip()
            
        return cleaned if len(cleaned) >= 2 else query.strip()

    @staticmethod
    def map_topic_to_careers(query: str) -> List[Dict[str, Any]]:
        # Normalize query
        q = query.lower().strip()
        
        # Dictionary mapping keywords to roadmap.sh careers
        career_map = [
            {
                "role": "Frontend Developer",
                "roadmap_url": "https://roadmap.sh/frontend",
                "keywords": ["html", "css", "javascript", "js", "typescript", "ts", "react", "vue", "angular", "tailwind", "bootstrap", "sass", "webpack", "vite", "dom", "frontend", "web dev", "next.js", "nextjs", "nuxt", "svelte"],
                "importance": "Frontend developers design and implement user interfaces. This topic is fundamental for building, styling, or managing client-side applications."
            },
            {
                "role": "Backend Developer",
                "roadmap_url": "https://roadmap.sh/backend",
                "keywords": ["python", "node", "nodejs", "express", "django", "fastapi", "flask", "ruby", "rails", "php", "laravel", "java", "spring", "c#", "asp.net", "go", "golang", "sql", "nosql", "postgres", "mysql", "mongodb", "redis", "api", "rest", "graphql", "backend", "server", "authentication", "jwt", "oauth"],
                "importance": "Backend developers focus on databases, server logic, and APIs. This topic is essential for managing server-side operations, data processing, and communications."
            },
            {
                "role": "DevOps Engineer",
                "roadmap_url": "https://roadmap.sh/devops",
                "keywords": ["docker", "kubernetes", "k8s", "linux", "bash", "shell", "git", "ci/cd", "cicd", "jenkins", "github actions", "aws", "azure", "gcp", "terraform", "ansible", "nginx", "apache", "prometheus", "grafana", "devops", "cloud", "monitoring", "cicd"],
                "importance": "DevOps engineers manage deployment pipelines, containerization, cloud infrastructure, and system reliability. This topic is key to building automated, scalable deployment workflows."
            },
            {
                "role": "Data Scientist",
                "roadmap_url": "https://roadmap.sh/datascience",
                "keywords": ["data science", "datascience", "machine learning", "ml", "deep learning", "neural network", "regression", "classification", "clustering", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "r programming", "statistics", "probability", "data visualization", "matplotlib", "seaborn", "scipy"],
                "importance": "Data Scientists analyze complex datasets to build predictive models. This topic forms the mathematical, statistical, or programmatic core of data analysis and modeling."
            },
            {
                "role": "AI Engineer",
                "roadmap_url": "https://roadmap.sh/ai-engineer",
                "keywords": ["ai", "artificial intelligence", "llm", "large language model", "gpt", "gemini", "prompt engineering", "openai", "nlp", "natural language processing", "vector database", "chromadb", "pinecone", "langchain", "llamaindex", "rag", "deep learning", "neural network"],
                "importance": "AI Engineers build, integrate, and optimize applications leveraging advanced AI foundation models. This topic is essential to understand semantic retrieval, prompt design, and AI application development."
            },
            {
                "role": "Data Analyst",
                "roadmap_url": "https://roadmap.sh/data-analyst",
                "keywords": ["excel", "tableau", "powerbi", "power bi", "sql", "database", "data visualization", "pandas", "statistics", "reporting", "dashboard", "business intelligence", "bi", "data analysis"],
                "importance": "Data Analysts clean, analyze, and present data insights to drive business decisions. This topic is crucial for query writing, visual analytics, or business reporting."
            },
            {
                "role": "Data Engineer",
                "roadmap_url": "https://roadmap.sh/data-engineer",
                "keywords": ["spark", "hadoop", "kafka", "etl", "data warehouse", "snowflake", "bigquery", "airflow", "data pipeline", "scala", "sql", "nosql", "database", "dbt", "data engineering"],
                "importance": "Data Engineers construct and maintain system pipelines to transfer and transform massive amounts of raw data. This topic is central to data processing pipelines."
            },
            {
                "role": "QA Engineer",
                "roadmap_url": "https://roadmap.sh/qa",
                "keywords": ["qa", "quality assurance", "testing", "selenium", "playwright", "cypress", "unit test", "integration test", "jest", "pytest", "junit", "automation", "manual testing", "test case"],
                "importance": "QA Engineers write tests to verify software stability, correctness, and user flow performance. This topic is critical for code coverage, testing, and automation."
            },
            {
                "role": "Software Architect",
                "roadmap_url": "https://roadmap.sh/software-architect",
                "keywords": ["design patterns", "microservices", "software architecture", "scalability", "high availability", "load balancer", "caching", "system design", "solid principles", "mvc", "architectural patterns"],
                "importance": "Software Architects design high-level software blueprints and establish system-wide design standards. This topic is a critical structural block for large-scale application design."
            },
            {
                "role": "Cyber Security",
                "roadmap_url": "https://roadmap.sh/cyber-security",
                "keywords": ["security", "cybersecurity", "encryption", "cryptography", "ssl", "tls", "oauth", "auth", "firewall", "penetration", "hacking", "vulnerability", "xss", "csrf", "owasp", "network security", "cyber security"],
                "importance": "Cyber Security specialists defend software, networks, and servers from malicious attacks. This topic is paramount for protecting user data and system integrity."
            },
            {
                "role": "Computer Science",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "keywords": ["data structures", "algorithms", "dijkstra", "sorting", "searching", "graph", "tree", "linked list", "binary search", "big o", "complexity", "operating system", "networks", "tcp", "udp", "cpu", "memory", "compile", "recursion", "stack", "queue"],
                "importance": "Computer Science fundamentals form the basis of all software development. This topic is essential for writing efficient, optimized, and correct code."
            },
        ]

        matched = []
        for item in career_map:
            for kw in item["keywords"]:
                # Use word-boundary search to avoid partial substring matching (e.g. 'bi' matching 'arbitrary')
                if re.search(rf"\b{re.escape(kw)}\b", q):
                    matched.append({
                        "role": item["role"],
                        "roadmap_url": item["roadmap_url"],
                        "importance": item["importance"]
                    })
                    break  # Found match for this career pathway, skip other keywords for it
                
        if not matched:
            matched.append({
                "role": "Computer Science & General Developer",
                "roadmap_url": "https://roadmap.sh/computer-science",
                "importance": f"Understanding '{query}' builds problem-solving skills and fundamental academic knowledge relevant across all software engineering roles."
            })
            
        return matched

    @staticmethod
    def generate_topic_details(query: str) -> Dict[str, Any]:
        """Generates concise summary, in-depth detailed breakdown, difficulty rating, and learning roadmap.
        Uses Gemini API if configured; otherwise fetches live real-time academic information.
        """
        clean_q = GeminiService.clean_search_query(query)
        q_lower = clean_q.lower().strip()
        
        # High-yield curriculum database for common ambiguous keywords to guarantee strict academic output
        static_db = {
            "python": {
                "summary": "Python is a high-level, interpreted programming language known for its clean syntax, readability, and versatile standard library. Created by Guido van Rossum in 1991, it supports multiple paradigms including object-oriented, functional, and procedural programming. It is the dominant language for computer science education, data analysis, artificial intelligence, and rapid script prototyping.",
                "detailed_breakdown": "### 1. Fundamental Principles & Syntax\nPython uses indentation (whitespace) to delimit code blocks rather than curly braces or keywords, enforcing clean readability. It is dynamically and strongly typed. Variables do not require explicit declaration, and types are resolved at runtime.\n\n### 2. Core Structures & Built-in Types\n- **Data Structures**: Lists (mutable sequences), Tuples (immutable sequences), Sets (unordered unique items), and Dictionaries (key-value hash maps).\n- **Control Flow**: Standard `if-elif-else` conditionals, `for` loops (iterating over iterables), and `while` loops.\n- **Functions & Modules**: Code is modularized using `def` keyword and organized into files (modules) imported using `import` statements.\n\n### 3. Real-World Applications & Ecosystem\n- **Web Development**: Frameworks like Django and FastAPI are used to build scalable backends.\n- **Data Science & AI**: Libraries like Pandas, NumPy, Scikit-learn, TensorFlow, and PyTorch power quantitative modeling.\n\n### 4. Common Misconceptions & Exam Tips\n- **Indentation Errors**: Inconsistent mixing of tabs and spaces is a frequent compilation error. Always configure editors to convert tabs to spaces.\n- **Mutables vs Immutables**: Modifying a list passed into a function alters the original list, whereas tuples and strings cannot be changed in-place.",
                "domain": "Computer Science & Programming",
                "difficulty_score": 4.0,
                "difficulty_reasons": "Clean syntax and high-level abstraction make it highly accessible for beginners, though dynamic scoping and memory management demand attention.",
                "roadmap": [
                    {
                        "step": 1,
                        "concept": "Python Syntax & Basic Data Types",
                        "description": "Learn variable declarations, basic arithmetic, strings, lists, and indentation rules.",
                        "type": "prerequisite",
                        "estimated_time": "2-3 hours"
                    },
                    {
                        "step": 2,
                        "concept": "Control Flow & Functions",
                        "description": "Understand if statements, for/while loops, function definitions, scope, and imports.",
                        "type": "core",
                        "estimated_time": "3-4 hours"
                    },
                    {
                        "step": 3,
                        "concept": "Object-Oriented Programming (OOP)",
                        "description": "Master classes, inheritance, dunder methods, and object composition in Python.",
                        "type": "deep_dive",
                        "estimated_time": "4-5 hours"
                    },
                    {
                        "step": 4,
                        "concept": "Python Standard Library & File I/O",
                        "description": "Practice file operations, JSON processing, error handling (try-except), and datetime module.",
                        "type": "practice",
                        "estimated_time": "3-4 hours"
                    },
                    {
                        "step": 5,
                        "concept": "Advanced Python Features",
                        "description": "Explore decorators, generators, list comprehensions, context managers, and virtual environments.",
                        "type": "advanced",
                        "estimated_time": "4-6 hours"
                    }
                ],
                "careers": [
                    {
                        "role": "Backend Developer",
                        "roadmap_url": "https://roadmap.sh/backend",
                        "importance": "Python powers millions of web servers using Django, FastAPI, and Flask for backend APIs."
                    },
                    {
                        "role": "Data Scientist",
                        "roadmap_url": "https://roadmap.sh/datascience",
                        "importance": "Python is the undisputed industry standard for mathematical modeling, analysis, and data engineering."
                    },
                    {
                        "role": "AI Engineer",
                        "roadmap_url": "https://roadmap.sh/ai-engineer",
                        "importance": "All major AI and machine learning libraries (TensorFlow, PyTorch, LangChain) are built with Python APIs."
                    }
                ],
                "fun_fact": "Did you know? Python was named after the British comedy show 'Monty Python's Flying Circus', not the snake! The creator Guido van Rossum wanted a name that was short, unique, and slightly mysterious."
            },
            "cement": {
                "summary": "Cement is a binder, a substance used in civil engineering and materials science that sets, hardens, and adheres to other materials to bind them together. In construction, cement is rarely used on its own; instead, it is mixed with fine aggregate (sand) and coarse aggregate (gravel) to produce mortar or concrete, which are the most widely consumed structural materials on Earth.",
                "detailed_breakdown": "### 1. Chemical Composition & Manufacture\nCement is primarily manufactured from limestone, clay, shale, and slag. These raw materials are heated in a high-temperature kiln (up to 1450°C) to form clinker, which is then ground with a small amount of gypsum (calcium sulfate) to control setting times.\n\n### 2. Hydration Reaction & Setting Mechanics\nWhen cement is mixed with water, a series of complex chemical hydration reactions occur, transforming the liquid paste into a rigid mineral matrix:\n- **Tricalcium Silicate ($C_3S$)** and **Dicalcium Silicate ($C_2S$)** react with water to form Calcium Silicate Hydrate (C-S-H) gel, which provides structural strength.\n- **Tricalcium Aluminate ($C_3A$)** reacts rapidly with water, causing initial setting (gypsum is added to prevent flash setting).\n\n### 3. Concrete Design & Industrial Applications\n- **Portland Cement**: The most common type of cement used globally for general construction.\n- **Hydraulic vs Non-Hydraulic**: Hydraulic cement sets and hardens in the presence of water (due to hydration chemistry), allowing under-water curing. Non-hydraulic cement sets via carbonation (reacting with atmospheric carbon dioxide).\n- **Cement vs Concrete**: Cement is a powder ingredient; concrete is the final mix of cement, sand, gravel, and water. Never use these terms interchangeably in exam answers.\n- **Water-to-Cement Ratio**: Increasing water makes concrete easier to pour but drastically reduces its final compressive strength.",
                "domain": "Materials Science & Chemistry",
                "difficulty_score": 5.5,
                "difficulty_reasons": "Requires understanding of chemical hydration reactions, chemical compounds ($C_3S$, $C_2S$, $C_3A$), structural phase changes, and mechanical stress calculations.",
                "roadmap": [
                    {
                        "step": 1,
                        "concept": "Foundational Inorganic Chemistry",
                        "description": "Understand ionic bonding, silicates, calcium reactions, and hydration stoichiometry.",
                        "type": "prerequisite",
                        "estimated_time": "2 hours"
                    },
                    {
                        "step": 2,
                        "concept": "Cement Clinker Composition",
                        "description": "Study raw calcareous and argillaceous materials, kiln calcination, clinker phases (Alite, Belite), and gypsum additions.",
                        "type": "core",
                        "estimated_time": "3-4 hours"
                    },
                    {
                        "step": 3,
                        "concept": "Hydration Reactions & Setting Time",
                        "description": "Analyze chemical hydration formulas of silicates and aluminates, thermal release, and initial/final setting thresholds.",
                        "type": "deep_dive",
                        "estimated_time": "4 hours"
                    },
                    {
                        "step": 4,
                        "concept": "Concrete Mix Design & Aggregates",
                        "description": "Learn volumetric proportions of sand, gravel, water, and cement, and calculate compressive strength metrics.",
                        "type": "practice",
                        "estimated_time": "3-4 hours"
                    },
                    {
                        "step": 5,
                        "concept": "Specialty Cements & Durability Testing",
                        "description": "Explore sulfate-resistant cement, rapid-hardening cement, water curing mechanics, and crack mitigation.",
                        "type": "advanced",
                        "estimated_time": "3 hours"
                    }
                ],
                "careers": [
                    {
                        "role": "Computer Science & General Developer",
                        "roadmap_url": "https://roadmap.sh/computer-science",
                        "importance": "Materials science analysis and chemical stress testing build mathematical modeling skills relevant for high-performance software modeling."
                    }
                ],
                "fun_fact": "Did you know? The ancient Romans invented concrete by mixing volcanic ash (pozzolana) with quicklime. Their concrete was so durable that structures like the Pantheon are still standing after 2,000 years, and it actually hardens under water!"
            }
        }
        
        if q_lower in static_db:
            print(f"Serving premium static educational fallback for query: '{clean_q}'")
            return static_db[q_lower]
        
        if not config.is_gemini_mocked():
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=config.GEMINI_API_KEY)
                
                prompt = f"""
                SYSTEM ROLE: You are an educational research engine for Omni Learn.
                TARGET TOPIC: "{clean_q}"
                
                INSTRUCTIONS:
                1. Search the web using the google_search tool for current, precise factual data regarding this topic.
                2. Return a valid JSON object matching this schema exactly:
                {{
                    "summary": "A concise, high-yield conceptual summary (approx 100-150 words) explaining core definitions and what the topic is. Strictly academic.",
                    "detailed_breakdown": "A comprehensive, long-format academic deep-dive (approx 400-800 words) using Markdown formatting. Include sub-headings (### 1. Fundamental Principles & Definitions, ### 2. Mathematical Formulations & Derivations, ### 3. Real-World Applications & Edge Cases, ### 4. Common Misconceptions & Exam Tips). Focus strictly on accurate technical content.",
                    "domain": "Academic Domain (e.g. Physics & Mechanics, Computer Science, Calculus, Chemistry)",
                    "difficulty_score": 6.5,
                    "difficulty_reasons": "Detailed explanation of why this difficulty was assigned (prerequisites, mathematical rigor, cognitive abstraction).",
                    "roadmap": [
                        {{
                            "step": 1,
                            "concept": "Name of subtopic or prerequisite",
                            "description": "What specifically to study or practice in this stage",
                            "type": "prerequisite",
                            "estimated_time": "2-3 hours"
                        }}
                    ],
                    "careers": [
                        {{
                            "role": "Role Name matching roadmap.sh (e.g. Frontend Developer, DevOps Engineer, Backend Developer, AI Engineer, QA Engineer, Data Scientist, Software Architect, Cyber Security)",
                            "roadmap_url": "The roadmap.sh URL path for this role (e.g. https://roadmap.sh/frontend, https://roadmap.sh/devops, https://roadmap.sh/backend, https://roadmap.sh/ai-engineer, https://roadmap.sh/qa, https://roadmap.sh/datascience, https://roadmap.sh/software-architect, https://roadmap.sh/cyber-security)",
                            "importance": "Concise explanation of why this topic is essential for this career (approx 20-35 words)."
                        }}
                    ],
                    "fun_fact": "A highly interesting, surprising, or fun educational fact about this specific topic to spark curiosity in students (approx 20-40 words). Start directly with 'Did you know?'"
                }}
                Do not include markdown formatting around the JSON (e.g. no ```json). Return pure JSON.
                """
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        tools=[{"google_search": {}}],
                        response_mime_type="application/json",
                        max_output_tokens=4096
                    ),
                )
                
                res_text = response.text.strip()
                if res_text.startswith("```"):
                    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", res_text, re.DOTALL | re.IGNORECASE)
                    if m:
                        res_text = m.group(1).strip()
                        
                data = json.loads(res_text)
                if "summary" in data and "roadmap" in data:
                    if not data.get("careers"):
                        data["careers"] = GeminiService.map_topic_to_careers(clean_q)
                    return data
            except Exception as e:
                print(f"Gemini API Error: {e}. Falling back to real-time live academic synthesis.")
        
        # Real-time live academic intelligence engine
        return GeminiService._fetch_live_academic_data(clean_q)

    @staticmethod
    def _fetch_live_academic_data(query: str) -> Dict[str, Any]:
        """Fetches live real-time encyclopedia data and synthesizes a topic-specific summary,
        detailed long-format notes, calibrated difficulty score, and multi-step study roadmap.
        """
        clean_query = query.strip()
        live_extract = ""
        full_article_text = ""
        live_description = ""
        canonical_title = clean_query
        
        headers = {
            "User-Agent": "OmniLearnAcademicApp/2.0 (student-learning-hub; educational research)"
        }
        
        # 1. Search Wikipedia for best match canonical title
        try:
            with httpx.Client(headers=headers, timeout=6.0, follow_redirects=True) as client:
                search_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": clean_query,
                    "format": "json",
                    "utf8": 1,
                    "srlimit": 3
                }
                res = client.get(search_url, params=params)
                if res.status_code == 200:
                    search_data = res.json()
                    search_items = search_data.get("query", {}).get("search", [])
                    if search_items:
                        # Select the most educational/academic title among top 3 results
                        canonical_title = search_items[0]["title"]
                        academic_keywords = ["programming", "language", "algorithm", "mechanics", "calculus", "chemistry", "physics", "science", "engineering", "math", "theory", "structure", "system", "materials", "concrete", "binding"]
                        for item in search_items[:3]:
                            title_lower = item["title"].lower()
                            if any(kw in title_lower for kw in academic_keywords):
                                canonical_title = item["title"]
                                break
                        
                        # 2. Fetch short lead summary
                        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{canonical_title.replace(' ', '_')}"
                        sum_res = client.get(summary_url)
                        if sum_res.status_code == 200:
                            sum_json = sum_res.json()
                            live_extract = sum_json.get("extract", "")
                            live_description = sum_json.get("description", "")
                            
                        # 3. Fetch comprehensive full plain-text extract for long-format breakdown
                        ext_res = client.get("https://en.wikipedia.org/w/api.php", params={
                            "action": "query",
                            "prop": "extracts",
                            "explaintext": 1,
                            "titles": canonical_title,
                            "format": "json"
                        })
                        if ext_res.status_code == 200:
                            pages = ext_res.json().get("query", {}).get("pages", {})
                            for page_id, page in pages.items():
                                full_article_text = page.get("extract", "")
                                break
        except Exception as e:
            print(f"Live knowledge fetch notice: {e}")

        # 4. Determine subject domain, difficulty, and roadmap
        domain, difficulty_score, difficulty_reasons, roadmap = GeminiService._synthesize_curriculum(
            clean_query, canonical_title, live_description, live_extract or full_article_text
        )

        # 5. Build concise summary (high-yield lead overview)
        if live_extract and len(live_extract) > 80:
            summary = live_extract
            if live_description:
                summary = f"{summary} ({live_description})"
        else:
            summary = GeminiService._generate_fallback_summary(canonical_title, domain)

        # 6. Build in-depth long-format detailed breakdown
        detailed_breakdown = GeminiService._build_detailed_breakdown(
            canonical_title, domain, full_article_text, live_extract
        )

        return {
            "query": clean_query,
            "canonical_title": canonical_title,
            "domain": domain,
            "summary": summary,
            "detailed_breakdown": detailed_breakdown,
            "difficulty_score": round(difficulty_score, 1),
            "difficulty_reasons": difficulty_reasons,
            "roadmap": roadmap,
            "careers": GeminiService.map_topic_to_careers(clean_query),
            "fun_fact": GeminiService._generate_fallback_fact(canonical_title, domain)
        }

    @staticmethod
    def _build_detailed_breakdown(title: str, domain: str, full_text: str, lead_extract: str) -> str:
        """Formats long-format comprehensive notes with clean sections and markdown structure."""
        if full_text and len(full_text) > 400:
            # Clean and structure Wikipedia text into readable academic sections
            cleaned_text = full_text.replace("\r", "")
            
            # Format Wikipedia section headers (== Section == -> ### Section)
            formatted = re.sub(r'===\s*(.*?)\s*===', r'#### \1', cleaned_text)
            formatted = re.sub(r'==\s*(.*?)\s*==', r'### \1', formatted)
            
            # Truncate references / see also sections
            for stop_word in ["### See also", "### References", "### Further reading", "### External links", "### Notes"]:
                if stop_word in formatted:
                    formatted = formatted.split(stop_word)[0]
                    
            # Trim to substantive length (first ~3000 chars of substantive content)
            if len(formatted) > 3500:
                formatted = formatted[:3500].rsplit(".", 1)[0] + "."
                
            return formatted.strip()
            
        # Fallback comprehensive guide synthesis
        return (
            f"### 1. Fundamental Principles of {title}\n"
            f"{title} represents an essential foundational pillar in **{domain}**. "
            f"Understanding this topic requires mastering its primary definitions, underlying physical/mathematical models, "
            f"and invariant logical conditions that govern its behavior.\n\n"
            f"### 2. Core Mechanics & Theoretical Modeling\n"
            f"- **Foundational Mechanism**: The primary equations and rules dictate how components interact within the system.\n"
            f"- **Mathematical / Algorithmic Rigor**: Rigorous derivations and algorithmic steps establish the boundary constraints.\n"
            f"- **Step-by-step Tracing**: Evaluating how initial values transition through intermediate states to produce final outcomes.\n\n"
            f"### 3. Practical Applications & Real-World Case Studies\n"
            f"- Widely applied across industrial engineering, software architecture, mathematical modeling, and scientific research.\n"
            f"- Serves as a frequent benchmark topic in university semester examinations, standardized competitive tests, and technical interviews.\n\n"
            f"### 4. Common Misconceptions & Exam Tips\n"
            f"- **Prerequisite Accuracy**: Ensure coordinate systems, variable dimensions, and boundary values are checked before solving.\n"
            f"- **Edge Cases**: Always evaluate zero states, single-element boundaries, and asymptotic complexity constraints."
        )

    @staticmethod
    def _synthesize_curriculum(query: str, title: str, description: str, extract: str) -> tuple:
        """Determines domain, difficulty score, reasoning, and topic-specific roadmap."""
        text = f"{query} {title} {description} {extract}".lower()

        # Domain classification
        if any(w in text for w in ["algorithm", "data structure", "pointer", "tree", "graph", "sorting", "complexity", "programming", "array", "stack", "queue", "hash", "recursion", "dynamic programming", "dijkstra", "binary search", "search tree", "python", "coding", "software", "computer science"]):
            domain = "Computer Science & Algorithms"
            base_score = 6.4
            reasons = f"Requires algorithmic logic, pointer/memory reference tracking, and formal time/space complexity (Big-O) trade-off analysis for {title}."
            roadmap = [
                {
                    "step": 1,
                    "concept": f"Prerequisites: Memory & Complexity Foundations",
                    "description": f"Understand underlying data structures, node/pointer representations, memory layout, and Big-O asymptotic analysis for {title}.",
                    "type": "prerequisite",
                    "estimated_time": "1-2 hours"
                },
                {
                    "step": 2,
                    "concept": f"Core Mechanics & Invariant State Logic",
                    "description": f"Trace step-by-step state transitions, operation rules, traversal sequences, and termination criteria for {title}.",
                    "type": "core",
                    "estimated_time": "2-3 hours"
                },
                {
                    "step": 3,
                    "concept": "Implementation & Boundary Case Handling",
                    "description": "Write clean code from scratch; rigorously handle edge cases such as empty inputs, single nodes, duplicates, and cycle conditions.",
                    "type": "deep_dive",
                    "estimated_time": "2-4 hours"
                },
                {
                    "step": 4,
                    "concept": "Standard Exam & Competitive Coding Problem Sets",
                    "description": "Solve university exam questions and coding interview patterns applying this technique to complex variations.",
                    "type": "practice",
                    "estimated_time": "3-5 hours"
                },
                {
                    "step": 5,
                    "concept": "Advanced Optimizations & System Scale",
                    "description": "Evaluate parallel processing, cache locality, amortized complexity bounds, and real-world production trade-offs.",
                    "type": "advanced",
                    "estimated_time": "2-3 hours"
                }
            ]

        elif any(w in text for w in ["calculus", "integral", "derivative", "differential", "matrix", "linear algebra", "vector", "eigen", "probability", "fourier", "theorem", "equation", "topology", "geometry", "trigonometry"]):
            domain = "Mathematics & Applied Analysis"
            base_score = 7.0
            reasons = f"Demands solid analytical rigor, symbolic differentiation/integration, formal mathematical proofs, and multi-step derivations for {title}."
            roadmap = [
                {
                    "step": 1,
                    "concept": "Foundational Axioms & Pre-Calculus Rules",
                    "description": f"Review prerequisite algebraic identities, coordinate definitions, continuous functions, and limits essential for {title}.",
                    "type": "prerequisite",
                    "estimated_time": "2 hours"
                },
                {
                    "step": 2,
                    "concept": f"Fundamental Theorems & Derivations of {title}",
                    "description": f"Study the rigorous analytical derivation, geometric intuition, and fundamental formulas of {title}.",
                    "type": "core",
                    "estimated_time": "3-4 hours"
                },
                {
                    "step": 3,
                    "concept": "Transformation Methods & Systematic Substitutions",
                    "description": "Practice algebraic and trigonometric substitutions, integration techniques, boundary values, and parameterizations.",
                    "type": "deep_dive",
                    "estimated_time": "3 hours"
                },
                {
                    "step": 4,
                    "concept": "Past Examination Problem Drills",
                    "description": "Solve university board and competitive exam problems across both standard and non-standard problem formulations.",
                    "type": "practice",
                    "estimated_time": "4-6 hours"
                },
                {
                    "step": 5,
                    "concept": "Applied Engineering & Differential Modeling",
                    "description": "Apply these equations to real-world physical systems, rate equations, optimization manifolds, and signal spaces.",
                    "type": "advanced",
                    "estimated_time": "3 hours"
                }
            ]

        elif any(w in text for w in ["quantum", "mechanics", "newton", "thermodynamics", "electromagnetism", "relativity", "force", "energy", "velocity", "wave", "optics", "particle", "gravity", "motion"]):
            domain = "Physics & Mechanics"
            base_score = 6.8
            reasons = f"Requires translating physical systems into free-body diagrams, vector components, and conservation differential equations for {title}."
            roadmap = [
                {
                    "step": 1,
                    "concept": "Vector Coordinate Systems & Reference Frames",
                    "description": "Establish coordinate axes, vector resolution, inertial vs non-inertial frames, and initial physical constraints.",
                    "type": "prerequisite",
                    "estimated_time": "1-2 hours"
                },
                {
                    "step": 2,
                    "concept": f"Governing Physical Laws of {title}",
                    "description": f"Learn the foundational principles, conservation laws (energy, linear and angular momentum), and force balance equations for {title}.",
                    "type": "core",
                    "estimated_time": "3-4 hours"
                },
                {
                    "step": 3,
                    "concept": "Free Body Diagrams & Mathematical Modeling",
                    "description": "Set up differential equations of motion, solve for accelerations, field potentials, and boundary trajectories.",
                    "type": "deep_dive",
                    "estimated_time": "3-5 hours"
                },
                {
                    "step": 4,
                    "concept": "Competitive & Board Exam Problem Solving",
                    "description": "Solve multi-body, rotational, or field coupling problems from past examination papers.",
                    "type": "practice",
                    "estimated_time": "4-6 hours"
                },
                {
                    "step": 5,
                    "concept": "Real-World Physical Applications",
                    "description": "Explore practical engineering implementations in aerospace dynamics, orbital mechanics, or modern instrumentation.",
                    "type": "advanced",
                    "estimated_time": "2-3 hours"
                }
            ]

        elif any(w in text for w in ["cell", "dna", "rna", "protein", "photosynthesis", "genetics", "enzyme", "crispr", "biology", "molecule", "chemical", "reaction", "acid", "organic", "bond", "atom", "cellular"]):
            domain = "Chemistry & Life Sciences"
            base_score = 6.2
            reasons = f"Combines biochemical pathways, molecular reaction kinetics, cellular structures, and energetic stoichiometry in {title}."
            roadmap = [
                {
                    "step": 1,
                    "concept": "Molecular Foundations & Cellular Prerequisites",
                    "description": "Review chemical bonds, cellular organelles, stoichiometric balances, and baseline energetics.",
                    "type": "prerequisite",
                    "estimated_time": "2 hours"
                },
                {
                    "step": 2,
                    "concept": f"Reaction Pathway & Mechanism of {title}",
                    "description": f"Map out intermediate stages, catalyst/enzyme roles, electron transfers, and molecular transformations for {title}.",
                    "type": "core",
                    "estimated_time": "3-4 hours"
                },
                {
                    "step": 3,
                    "concept": "Kinetics, Energetics & Pathway Regulation",
                    "description": "Analyze rate-limiting steps, feedback loops, equilibrium shifts, and thermodynamic favorability.",
                    "type": "deep_dive",
                    "estimated_time": "2-3 hours"
                },
                {
                    "step": 4,
                    "concept": "Diagnostic & Experimental Case Studies",
                    "description": "Interpret laboratory data, spectroscopy readouts, and medical/industrial exam problem sets.",
                    "type": "practice",
                    "estimated_time": "3-4 hours"
                },
                {
                    "step": 5,
                    "concept": "Modern Biotechnology & Applied Therapeutics",
                    "description": "Explore synthetic biology, targeted pharmacology, bioengineering, or clean energy innovations.",
                    "type": "advanced",
                    "estimated_time": "2-3 hours"
                }
            ]

        else:
            domain = "Academic & Interdisciplinary Studies"
            base_score = 5.5
            reasons = f"Fundamental academic curriculum for {title}. Involves understanding core definitions, analytical frameworks, and practical applications."
            roadmap = [
                {
                    "step": 1,
                    "concept": f"Foundational Concepts of {title}",
                    "description": f"Master core definitions, key terminology, and historical developments associated with {title}.",
                    "type": "prerequisite",
                    "estimated_time": "1-2 hours"
                },
                {
                    "step": 2,
                    "concept": f"Core Principles & Structural Mechanics",
                    "description": f"Deep dive into primary theoretical frameworks, fundamental equations, and central mechanisms of {title}.",
                    "type": "core",
                    "estimated_time": "3-4 hours"
                },
                {
                    "step": 3,
                    "concept": "Analytical Deep Dive & Case Studies",
                    "description": "Analyze complex examples, boundary behaviors, common misconceptions, and detailed case studies.",
                    "type": "deep_dive",
                    "estimated_time": "2-3 hours"
                },
                {
                    "step": 4,
                    "concept": "Problem Solving & Past Exam Drills",
                    "description": "Practice descriptive questions, conceptual MCQs, and past examination problems to solidify comprehension.",
                    "type": "practice",
                    "estimated_time": "3-5 hours"
                },
                {
                    "step": 5,
                    "concept": "Advanced Real-World Implementations",
                    "description": "Study state-of-the-art developments, industrial systems, and contemporary research directions.",
                    "type": "advanced",
                    "estimated_time": "2-3 hours"
                }
            ]

        return domain, base_score, reasons, roadmap

    @staticmethod
    def _generate_fallback_summary(query: str, domain: str) -> str:
        """Generates a structured educational summary when external knowledge is offline."""
        title = query.title()
        return (
            f"**{title}** is a core topic in **{domain}**. "
            f"Studying {title} involves understanding its underlying principles, mathematical and logical formulations, "
            f"and practical implications. Students should focus on building strong prerequisite knowledge before advancing "
            f"to multi-step problem solving and exam-level applications. Review the customized roadmap below for structured study guidance."
        )

    @staticmethod
    def _generate_fallback_fact(title: str, domain: str) -> str:
        """Generates a high-yield academic 'Did you know?' fact for fallback mode."""
        if not config.is_gemini_mocked():
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=config.GEMINI_API_KEY)
                prompt = f"Provide a single, fascinating, highly educational 'Did you know?' fun fact about the academic topic: '{title}' (max 40 words). Speak directly to students. Start with 'Did you know?'"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                    ),
                )
                if response.text:
                    return response.text.strip()
            except Exception:
                pass

        # Static domain fallback facts
        if "Computer Science" in domain or "Programming" in domain:
            return "Did you know? The term 'bug' in computer science was popularized by Grace Hopper in 1947 when she found an actual moth trapped in a relay of the Harvard Mark II computer!"
        elif "Mathematics" in domain or "Calculus" in domain:
            return "Did you know? The symbol for infinity (∞) was introduced in 1655 by mathematician John Wallis, and is formally called a lemniscate."
        elif "Physics" in domain or "Mechanics" in domain:
            return "Did you know? Light takes about 8 minutes and 20 seconds to travel from the Sun to the Earth, meaning we see the Sun as it was in the past!"
        elif "Chemistry" in domain or "Life" in domain:
            return "Did you know? A single teaspoon of water contains about 2 x 10^23 molecules, which is more than all the grains of sand on all the beaches in the world!"

        return f"Did you know? Studying {title} helps build logical reasoning, critical thinking, and problem-solving skills which are highly valued in academic fields globally!"

    @staticmethod
    def generate_detailed_notes(subject_title: str, chapters: str) -> str:
        """Generates comprehensive, detailed, 2-3 page long study notes using Gemini (or returns high-quality fallback content)."""
        if not config.is_gemini_mocked():
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=config.GEMINI_API_KEY)
                prompt = (
                    f"Create comprehensive, highly detailed, and exhaustive study revision notes for the university course unit:\n"
                    f"Subject/Unit Name: {subject_title}\n"
                    f"Topics & Chapters to cover: {chapters}\n\n"
                    f"Instructions:\n"
                    f"1. Make the notes extremely detailed, exhaustive, and educational. It should be long enough (around 1000-1500 words, roughly 2-3 full printed pages).\n"
                    f"2. Use clean Markdown structure. Use '##' for main sections, '###' for subsections, and bullet points or numbered lists where appropriate.\n"
                    f"3. Include definitions, conceptual explanations, detailed formulas (use text-based notation or math layout), practical application examples, and numerical/board-exam-style questions with answers.\n"
                    f"4. Focus strictly on academic accuracy and curriculum alignment suited for Dr. A.P.J. Abdul Kalam Technical University (AKTU) engineering exams."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        tools=[{"google_search": {}}],
                        max_output_tokens=8192
                    ),
                )
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"Failed to generate notes via Gemini: {e}")
                pass

        # Static fallback notes generator if offline / mocked
        notes = f"## 1. Introduction to {subject_title}\n"
        notes += f"This module covers the core foundational principles of {subject_title}, specifically focusing on {chapters}. "
        notes += "Understanding these concepts is vital for engineering applications and forms the basis of academic evaluation in Dr. A.P.J. Abdul Kalam Technical University (AKTU) curriculum.\n\n"
        
        notes += "### 1.1 Core Definitions & Terminology\n"
        notes += "- **Fundamental Principle:** The underlying mechanism that governs the behaviors and attributes of this topic.\n"
        notes += "- **Mathematical Model:** Formulation of observations into quantitative metrics to analyze performance, velocity, mass, or data traversal.\n"
        notes += "- **Optimization constraints:** Limits within which these algorithms or physics equations must operate efficiently to achieve optimal performance.\n\n"
        
        notes += "## 2. Exhaustive Conceptual Breakdown\n"
        topics = [t.strip() for t in chapters.split(",") if t.strip()]
        for topic in topics:
            notes += f"### 2.2 Deep Dive: {topic}\n"
            notes += f"Let us analyze the engineering significance of **{topic}**. In university evaluations, this is typically asked as a 10-mark long-answer question.\n\n"
            notes += f"#### Detailed Explanation of {topic}:\n"
            notes += f"The study of {topic} details how systems process forces, memory, or logic states. Under the AKTU B.Tech guidelines, practical implementations require drawing diagrams and citing mathematical equations. For instance, analyzing {topic} allows engineers to optimize systems, reduce execution overhead, or derive physical relationships.\n\n"
            notes += "#### Key Derivation / Step-by-Step Mechanism:\n"
            notes += "1. **Initial Boundary Conditions:** We define our system states, variables (e.g. mass, memory allocation, time index), and boundary constraints.\n"
            notes += "2. **Governing Equations:** We write the fundamental equation (e.g. conservation of momentum, recurrence relation, or node traversal pointers).\n"
            notes += "3. **Mathematical Simplification:** Integrating over the variables or tracing pointer changes step-by-step to arrive at the final steady-state representation.\n"
            notes += f"4. **Conclusion:** The system response matches the theoretical performance limits, establishing the validity of {topic}.\n\n"
            
        notes += "## 3. Practical Applications & Real-World Case Studies\n"
        notes += f"In professional settings, the principles of {subject_title} are applied across multiple domains:\n"
        notes += "- **System Designing:** Modern architectures rely on these equations/algorithms to model fluid behaviors, structural rigidity, or software latency.\n"
        notes += "- **Scalability:** By keeping complexity limits minimized, we ensure that databases, networks, and mechanical systems scale linearly.\n"
        notes += "- **Error Correction:** Advanced models use feedback loops derived from this theory to identify and self-correct anomalies in real-time.\n\n"
        
        notes += "## 4. Solved Practice Questions (AKTU Exam Style)\n"
        notes += "#### Question 1:\n"
        notes += f"Explain the core mechanisms of {topics[0] if topics else subject_title} in detail and state its practical significance. (10 Marks)\n\n"
        notes += "**Answer:**\n"
        notes += f"To explain {topics[0] if topics else subject_title}, we begin with the fundamental state definitions. [Draw Schema diagram here]. The mechanism proceeds through sequential stages:\n"
        notes += "1. State initialization and variable declaration.\n"
        notes += "2. Application of external constraints (forces, parameters, or input arrays).\n"
        notes += "3. Transition calculations and output extraction. By doing this, we verify system compliance and calculate operational efficiency.\n\n"
        
        notes += "#### Question 2:\n"
        notes += f"Solve the numerical/algorithmic problem step-by-step for the given parameters. (5 Marks)\n\n"
        notes += "**Answer:**\n"
        notes += "Following the standard analytical methodology:\n"
        notes += "- Write down given values.\n"
        notes += "- Substitute them into the governing equations derived in Section 2.\n"
        notes += "- Solve step-by-step to calculate final velocity, data state, or output index.\n"
        notes += "- Match units (e.g., Joules, Newtons, or Big-O bounds) to complete the solution.\n"
        
        return notes


