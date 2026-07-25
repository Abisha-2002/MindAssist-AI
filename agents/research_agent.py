"""
Agent Pattern 3: Tool-Use Agent
Uses RAG as a tool to retrieve relevant information
"""
import streamlit as st
from rag.loader import get_vector_store, query_retrieval

class ResearchAgent:
    """
    Research Agent - Uses RAG Tool to retrieve information
    Pattern: Tool-Use
    """
    
    def __init__(self):
        self.vector_db = get_vector_store()
        self.tools = {
            "rag_search": self._rag_search,
            "context_analyzer": self._analyze_context
        }
    
    def _rag_search(self, query: str, k: int = 5):
        """
        Tool 1: RAG Search - Query the vector database
        """
        if not self.vector_db:
            return {
                "status": "error",
                "error": "Vector database not initialized. Please add PDFs."
            }
        
        try:
            results = query_retrieval(query, k=k)
            return {
                "status": "success",
                "results": results,
                "num_results": len(results)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_context(self, results):
        """
        Tool 2: Context Analyzer - Analyze retrieved chunks
        """
        if not results or results.get("status") != "success":
            return {"status": "error", "message": "No valid results to analyze"}
        
        chunks = results["results"]
        analyzed = []
        for doc, score in chunks:
            analyzed.append({
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "source": doc.metadata.get("source", "Unknown"),
                "relevance_score": round(1 - score, 3),  # Chroma returns distance, convert to similarity
                "chunk_length": len(doc.page_content)
            })
        
        return {
            "status": "success",
            "analyzed_chunks": analyzed,
            "total_chunks": len(analyzed)
        }
    
    def execute_task(self, task_message: dict) -> dict:
        """
        Execute a task based on the structured message from Orchestrator
        Agent-to-Agent Communication - Receives structured JSON
        """
        task = task_message.get("payload", {}).get("task", "rag_search")
        query = task_message.get("payload", {}).get("query", "")
        k = task_message.get("payload", {}).get("k", 5)
        
        if task == "rag_search":
            result = self._rag_search(query, k)
            if result["status"] == "success":
                # Further analyze the context
                analysis = self._analyze_context(result)
                return {
                    "status": "success",
                    "worker": "ResearchAgent",
                    "retrieved_chunks": analysis.get("analyzed_chunks", []),
                    "total_chunks": analysis.get("total_chunks", 0),
                    "full_results": result
                }
            else:
                return {
                    "status": "error",
                    "worker": "ResearchAgent",
                    "error": result.get("error", "Unknown error")
                }
        else:
            return {
                "status": "error",
                "worker": "ResearchAgent",
                "error": f"Unknown task: {task}"
            }