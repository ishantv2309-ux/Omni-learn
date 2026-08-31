import httpx
from typing import List
from backend import config
from backend.schemas import WebResource

class SearchService:
    @staticmethod
    async def fetch_web_resources(query: str) -> List[WebResource]:
        """Fetches web resources (articles, documentation, references) from search APIs or live encyclopedia endpoints."""
        clean_query = query.strip()
        
        # 1. Try Google Custom Search if configured
        if not config.is_search_mocked():
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        "cx": config.GOOGLE_SEARCH_CX,
                        "key": config.GOOGLE_SEARCH_KEY,
                        "q": f"{clean_query} tutorial notes lecture",
                        "num": 5
                    }
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    resources = []
                    for item in data.get("items", []):
                        resources.append(WebResource(
                            title=item["title"],
                            url=item["link"],
                            snippet=item.get("snippet", "")
                        ))
                    if resources:
                        return resources
            except Exception as e:
                print(f"Google Search API notice: {e}. Falling back to live academic resources.")

        # 2. Live encyclopedia & open academic knowledge search
        try:
            live_resources = await SearchService._fetch_live_academic_links(clean_query)
            if live_resources:
                return live_resources
        except Exception as e:
            print(f"Live web search notice: {e}")

        # 3. Topic-tailored fallback resources
        return SearchService._get_mock_resources(clean_query)

    @staticmethod
    async def _fetch_live_academic_links(query: str) -> List[WebResource]:
        """Queries open educational and reference APIs for real academic links."""
        headers = {
            "User-Agent": "OmniLearnApp/2.0 (student-learning-hub; educational research)"
        }
        resources: List[WebResource] = []
        
        async with httpx.AsyncClient(headers=headers, timeout=6.0, follow_redirects=True) as client:
            # 1. Wikipedia search
            wiki_res = await client.get("https://en.wikipedia.org/w/api.php", params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": 3
            })
            if wiki_res.status_code == 200:
                wiki_data = wiki_res.json()
                for item in wiki_data.get("query", {}).get("search", []):
                    title = item["title"]
                    # Strip html tags from snippet
                    clean_snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
                    resources.append(WebResource(
                        title=f"Wikipedia: {title}",
                        url=f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                        snippet=clean_snippet or f"Comprehensive academic documentation, history, theorems, and definitions for {title}."
                    ))

        # Add curated academic hub links for the query
        resources.append(WebResource(
            title=f"LibreTexts Open Textbook: {query.title()}",
            url=f"https://query.libretexts.org/Search?q={query.replace(' ', '+')}",
            snippet=f"Open-access peer-reviewed textbook chapters, solved mathematical derivations, and exercise sets covering {query.title()}."
        ))
        resources.append(WebResource(
            title=f"MIT OpenCourseWare Search: {query.title()}",
            url=f"https://ocw.mit.edu/search/?q={query.replace(' ', '+')}",
            snippet=f"Syllabi, lecture slides, assignments, and exam archives from MIT undergraduate and graduate courses for {query.title()}."
        ))
        
        return resources

    @staticmethod
    def _get_mock_resources(query: str) -> List[WebResource]:
        """Provides mock web articles and documentation based on search terms."""
        return [
            WebResource(
                title=f"Wikipedia: {query.title()}",
                url=f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                snippet=f"General encyclopedia entry covering the historical development, foundational theory, definitions, applications, and mathematical formulations of {query.title()}."
            ),
            WebResource(
                title=f"LibreTexts: Introduction to {query.title()}",
                url=f"https://query.libretexts.org/Search?q={query}",
                snippet=f"Open-source textbook chapters covering core definitions, prerequisite concepts, solved examples, and practice problems for {query.title()}."
            ),
            WebResource(
                title=f"Khan Academy & MIT OpenCourseWare Guide: {query.title()}",
                url=f"https://www.khanacademy.org/search?page_search_query={query.replace(' ', '+')}",
                snippet=f"Structured online video courses, practice quizzes, and worked theoretical exercises for {query.title()}."
            )
        ]

        
