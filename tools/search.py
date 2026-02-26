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
    Combines search results from DuckDuckGo and Google (via SerpAPI).
    Requires SERPAPI_API_KEY environment variable for Google results.
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
        
    # 2. Google Search (via SerpAPI)
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if serpapi_key:
            from serpapi import GoogleSearch
            search = GoogleSearch({
                "q": query,
                "api_key": serpapi_key,
                "num": num_results
            })
            google_results = search.get_dict().get("organic_results", [])
            
            for res in google_results[:num_results]:
                # Avoid duplicates by checking links
                if not any(r["link"] == res.get("link") for r in results):
                    results.append({
                        "source": "Google",
                        "title": res.get("title", ""),
                        "link": res.get("link", ""),
                        "snippet": res.get("snippet", "")
                    })
        else:
            print("Notice: SERPAPI_API_KEY not found. Skipping Google search.")
    except Exception as e:
        print(f"Warning: Google Search failed: {e}")
        
    return results

if __name__ == "__main__":
    if not os.getenv("SERPAPI_API_KEY"):
        print("Note: Set SERPAPI_API_KEY in your .env file to enable Google search results.")
        
    print("Testing Combined Search...")
    test_res = combined_web_search.invoke({"query": "DNA origami nanoarrays", "num_results": 2})
    
    import json
    print(json.dumps(test_res, indent=2))
