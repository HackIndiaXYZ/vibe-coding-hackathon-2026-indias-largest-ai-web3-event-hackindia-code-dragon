import json
import datetime
from duckduckgo_search import DDGS

# -----------------------------------------------------------------------------
# TOOLKIT & EXTERNAL CAPABILITIES
# -----------------------------------------------------------------------------
# This module provides external capabilities to the AI. Ren can leverage 
# these tools autonomously during inference.

def execute_web_search(query: str, max_results: int = 3) -> str:
    """
    Executes a web search utilizing the DuckDuckGo Search API.
    Returns a JSON string of the top results containing titles, snippets, and URLs.
    """
    print(f"[Tools] Initiating Web Search for query: '{query}'")
    try:
        results = DDGS().text(query, max_results=max_results)
        
        if not results:
            return json.dumps({"status": "no results found"})
            
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get('title', 'Unknown Title'),
                "snippet": r.get('body', 'No snippet available'),
                "url": r.get('href', '#')
            })
            
        print(f"[Tools] Search complete. Retrieved {len(formatted_results)} results.")
        return json.dumps(formatted_results)
        
    except Exception as e:
        print(f"[Tools] Web Search Exception: {e}")
        return json.dumps({"error": f"Search tool failed: {str(e)}"})

def get_current_datetime(_=None) -> str:
    """
    Returns the current server date and time.
    Useful for the AI to orient itself temporally.
    """
    now = datetime.datetime.now()
    return json.dumps({
        "current_date": now.strftime("%Y-%m-%d"),
        "current_time": now.strftime("%H:%M:%S"),
        "timezone": "Local Server Time"
    })

# -----------------------------------------------------------------------------
# GROQ TOOL DEFINITIONS
# -----------------------------------------------------------------------------
# These JSON schemas map Python functions to the Groq LLM tool calling format.

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute_web_search",
            "description": "Search the live internet for current information, news, programming documentation, or factual answers. Use this whenever the user asks for real-world or current data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The precise search query. Make it concise and keyword-focused."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Retrieves the current date and time. Use this when the user asks about today's date, the current time, or relative time questions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Mapping dictionary for the execution engine
TOOL_REGISTRY = {
    "execute_web_search": execute_web_search,
    "get_current_datetime": get_current_datetime
}
