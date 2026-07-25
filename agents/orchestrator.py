"""
Agent Pattern 2: Orchestrator & Task Decomposition
Plans and coordinates tasks between agents
"""
import json
from typing import Dict, List, Any

class Orchestrator:
    """
    Orchestrator Agent - Plans tasks and manages agent-to-agent communication
    Pattern: Orchestrator-Worker & Task Decomposition
    """
    
    def __init__(self, user_query: str, intent: str):
        self.query = user_query
        self.intent = intent
        self.state = {
            "messages": [],
            "plan": [],
            "execution_results": {}
        }
        
    def create_plan(self) -> List[Dict]:
        """
        Decompose the task into smaller sub-tasks
        Pattern: Planning/Task Decomposition
        """
        # --- Literature Search ---
        if self.intent == "literature_search":
            self.state["plan"] = [
                {
                    "step": 1,
                    "worker": "ResearchAgent",
                    "task": "Retrieve relevant documents from RAG database",
                    "params": {"query": self.query, "k": 5}
                },
                {
                    "step": 2,
                    "worker": "ReflectionAgent",
                    "task": "Validate and synthesize retrieved information",
                    "params": {"query": self.query}
                }
            ]
        
        # --- Summarize Paper ---
        elif self.intent == "summarize_paper":
            self.state["plan"] = [
                {
                    "step": 1,
                    "worker": "ResearchAgent",
                    "task": "Find and retrieve the specific paper",
                    "params": {"query": self.query, "k": 3}
                },
                {
                    "step": 2,
                    "worker": "ReflectionAgent",
                    "task": "Create concise summary and validate accuracy",
                    "params": {"query": self.query}
                }
            ]
        
        # --- Gap Analysis ---
        elif self.intent == "gap_analysis":
            self.state["plan"] = [
                {
                    "step": 1,
                    "worker": "ResearchAgent",
                    "task": "Retrieve recent state-of-the-art research",
                    "params": {"query": self.query, "k": 5}
                },
                {
                    "step": 2,
                    "worker": "ReflectionAgent",
                    "task": "Identify research gaps and limitations",
                    "params": {"query": self.query}
                }
            ]
        
        # --- Web Search (NEW!) ---
        elif self.intent == "web_search":
            self.state["plan"] = [
                {
                    "step": 1,
                    "worker": "SearchTool",
                    "task": "Search the web for recent and real-time information",
                    "params": {"query": self.query}
                },
                {
                    "step": 2,
                    "worker": "ReflectionAgent",
                    "task": "Validate and synthesize web search results",
                    "params": {"query": self.query}
                }
            ]
        
        # --- Default Plan ---
        else:
            # If intent is unknown, use both RAG and Web Search
            self.state["plan"] = [
                {
                    "step": 1,
                    "worker": "ResearchAgent",
                    "task": "Retrieve general context from RAG database",
                    "params": {"query": self.query, "k": 3}
                },
                {
                    "step": 2,
                    "worker": "SearchTool",
                    "task": "Search the web for additional information",
                    "params": {"query": self.query}
                },
                {
                    "step": 3,
                    "worker": "ReflectionAgent",
                    "task": "Combine and validate both sources",
                    "params": {"query": self.query}
                }
            ]
        
        return self.state["plan"]
    
    def send_message(self, worker_name: str, payload: Dict) -> Dict:
        """
        Agent-to-Agent Communication Protocol
        Uses structured JSON messages between agents
        """
        message = {
            "from": "Orchestrator",
            "to": worker_name,
            "payload": payload,
            "metadata": {
                "intent": self.intent,
                "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
                "message_id": len(self.state["messages"]) + 1
            }
        }
        self.state["messages"].append(message)
        return message
    
    def receive_message(self, worker_name: str, response: Dict) -> None:
        """
        Receive and store responses from workers
        """
        response["from"] = worker_name
        response["to"] = "Orchestrator"
        self.state["execution_results"][worker_name] = response
        
    def get_plan_status(self) -> Dict:
        """
        Get current execution status
        """
        return {
            "total_steps": len(self.state["plan"]),
            "completed": len(self.state["execution_results"]),
            "plan": self.state["plan"],
            "results": self.state["execution_results"]
        }