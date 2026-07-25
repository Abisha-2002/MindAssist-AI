"""
Web Search Tool for Agent
Integrates Serper API with the agent system
"""
from utils.web_search import web_search

class SearchTool:
    """
    Tool for web search capability
    """
    
    def __init__(self):
        self.name = "web_search"
        self.description = "Search the internet for real-time information"
    
    def execute_task(self, task_message: dict) -> dict:
        """
        Execute web search based on task message
        """
        query = task_message.get("payload", {}).get("query", "")
        
        if not query:
            return {
                "status": "error",
                "worker": "SearchTool",
                "error": "No query provided"
            }
        
        results = web_search(query, num_results=5)
        
        if isinstance(results, dict) and "error" in results:
            return {
                "status": "error",
                "worker": "SearchTool",
                "error": results["error"]
            }
        
        if not results:
            return {
                "status": "error",
                "worker": "SearchTool",
                "error": "No search results found"
            }
        
        # Format results for Reflection Agent
        return {
            "status": "success",
            "worker": "SearchTool",
            "source": "web_search",
            "retrieved_chunks": [
                {
                    "title": r["title"],
                    "link": r["link"],
                    "snippet": r["snippet"],
                    "relevance_score": 0.95 - (i * 0.05)
                }
                for i, r in enumerate(results[:5])
            ],
            "total_chunks": len(results)
        }