"""
Agent Pattern 4: Reflection & Self-Critique
Uses free model (Gemini/Llama) via OpenRouter for reasoning and validation
"""
import json
from utils.model_clients import get_openrouter_client, MODELS

class ReflectionAgent:
    """
    Reflection Agent - Validates and synthesizes answers
    Pattern: Reflection/Self-Critique
    Prevents hallucinations by checking RAG context
    """
    
    def __init__(self):
        self.client = get_openrouter_client()
    
    def reflect_and_synthesize(self, user_query: str, rag_result: dict) -> dict:
        """
        Critique the RAG result and synthesize a final answer
        Pattern: Reflection - Self-validation before final output
        """
        # Step 1: Check if there was an error in retrieval
        if rag_result.get("status") == "error":
            return {
                "final_answer": "⚠️ I encountered an error retrieving information. Please check your PDF database.",
                "is_valid": False,
                "error": rag_result.get("error", "Unknown retrieval error")
            }
        
        chunks = rag_result.get("retrieved_chunks", [])
        
        # Step 2: Check if we have relevant content
        if not chunks:
            return {
                "final_answer": "📭 No relevant documents found in the database. Please add more PDFs to the `data/pdfs/` folder.",
                "is_valid": False
            }
        
        # Step 3: Prepare context for the model
        context_text = "\n---\n".join([
            f"Source {i+1}: {chunk['source']}\nContent: {chunk['content'][:500]}..."
            for i, chunk in enumerate(chunks[:3])
        ])
        
        # Step 4: Build prompt for the model
        prompt = f"""
        You are a strict academic research validator. Your task is to:
        
        1. Check if the provided context actually answers the user's query
        2. If it does, synthesize a concise, evidence-based answer
        3. If it doesn't, honestly say "Insufficient data" rather than making up an answer
        4. Never hallucinate information not present in the context
        
        User Query: {user_query}
        
        Retrieved Context from RAG Database:
        {context_text}
        
        Instructions:
        - If the context is sufficient, provide a 3-4 sentence summary
        - If not, say "Based on the available documents, I cannot find sufficient information to answer this query."
        - Always cite sources when possible
        
        Return your response as STRICT JSON:
        {{
            "is_sufficient": true/false,
            "summary": "your answer here",
            "sources_used": ["source1", "source2"]
        }}
        """
        
        try:
            # Use the model from MODELS (Gemini or whatever you set)
            model_name = MODELS["reasoning"]  # ← THIS IS THE KEY FIX!
            
            response = self.client.chat.completions.create(
                model=model_name,  # ← USING THE CORRECT MODEL!
                messages=[
                    {"role": "system", "content": "You are a strict academic validator. Never make up information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            # Step 5: Self-Correction/Reflection
            if not result.get("is_sufficient", False):
                return {
                    "final_answer": result.get("summary", "Insufficient information in the database."),
                    "is_valid": False,
                    "reflection_note": "Query requires additional context not in current database."
                }
            else:
                return {
                    "final_answer": result.get("summary", "Could not generate answer."),
                    "is_valid": True,
                    "sources_used": result.get("sources_used", []),
                    "reflection_note": "Answer validated against retrieved context."
                }
                
        except json.JSONDecodeError:
            return {
                "final_answer": "The reflection agent encountered a parsing error. Please try again.",
                "is_valid": False
            }
        except Exception as e:
            return {
                "final_answer": f"⚠️ Error during reflection: {str(e)}",
                "is_valid": False
            }
    
    def get_retrieval_quality_score(self, chunks: list) -> float:
        """
        Additional reflection: Score the quality of retrieved chunks
        """
        if not chunks:
            return 0.0
        
        scores = [chunk.get("relevance_score", 0) for chunk in chunks]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return avg_score