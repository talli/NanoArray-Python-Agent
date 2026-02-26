import os
from typing import List, Dict, Any
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Initialize standard DuckDuckGo search tool
ddg_search = DuckDuckGoSearchResults()

@tool
def combined_web_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Combines search results from DuckDuckGo and SearXNG.
    Requires SEARXNG_URL environment variable for SearXNG results (defaults to http://localhost:8080).
    """
    results = []
    
    # 1. DuckDuckGo Search
    try:
        ddg_results = ddg_search.run(query)
        # Parse the string output from DuckDuckGoSearchResults (format: [snippet: ..., title: ..., link: ...])
        # A simple parsing approach:
        import re
        snippets = re.findall(r"snippet: (.*?), title:", ddg_results)
        titles = re.findall(r"title: (.*?), link:", ddg_results)
        links = re.findall(r"link: (.*?)(?:\]|, snippet:)", ddg_results)
        
        for i in range(min(num_results, len(titles))):
            results.append({
                "source": "DuckDuckGo",
                "title": titles[i].strip(),
                "link": links[i].strip() if i < len(links) else "",
                "snippet": snippets[i].strip() if i < len(snippets) else ""
            })
    except Exception as e:
        print(f"Warning: DuckDuckGo search failed: {e}")
        
    # 2. SearXNG Search
    try:
        from langchain_community.utilities import SearxSearchWrapper
        searx_host = os.getenv("SEARXNG_URL", "http://localhost:8080")
        searx = SearxSearchWrapper(searx_host=searx_host)
        searx_results = searx.results(query, num_results=num_results)
        
        for res in searx_results:
            # Avoid duplicates by checking links
            if not any(r["link"] == res.get("link") for r in results):
                results.append({
                    "source": "SearXNG",
                    "title": res.get("title", ""),
                    "link": res.get("link", ""),
                    "snippet": res.get("snippet", "")
                })
    except Exception as e:
        print(f"Warning: SearXNG Search failed. Ensure SEARXNG_URL is set or a local instance is running on port 8080: {e}")
        
    return results

if __name__ == "__main__":
    if not os.getenv("SEARXNG_URL"):
        print("Note: Set SEARXNG_URL in your .env file to configure SearXNG (defaults to http://localhost:8080).")
        
    print("Testing Combined Search...")
    test_res = combined_web_search.invoke({"query": "DNA origami nanoarrays", "num_results": 2})
    
    import json
    print(json.dumps(test_res, indent=2))
