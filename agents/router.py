"""
Agent Pattern 1: Router Agent
Uses Groq Llama 3.1 for ultra-fast, cheap intent classification
"""
import json
from utils.model_clients import get_groq_client, MODELS

def route_query(user_input: str):
    """
    Classify user query into one of four intents
    Pattern: Router - Uses cheap/fast model for routing decisions
    """
    client = get_groq_client()
    if not client:
        return {"intent": "literature_search", "error": "Groq client unavailable"}
    
    prompt = f"""
    You are an intelligent research assistant router. 
    Classify the user's research query into exactly ONE of these intents:
    
    1. 'literature_search' - If user is asking for general information, definitions, or seeking knowledge from existing documents (e.g., "What is PHQ-9?", "Explain depression symptoms")
    
    2. 'summarize_paper' - If user wants a specific paper or research summarized (e.g., "Summarize this research paper", "What does this study say?")
    
    3. 'gap_analysis' - If user asks about research gaps, limitations, or future directions (e.g., "What are the research gaps?", "What is missing in this field?")
    
    4. 'web_search' - If user asks for recent news, latest developments, real-time information, current events, or things not likely in academic papers (e.g., "Latest depression research 2024", "Recent AI breakthroughs", "Current mental health statistics")
    
    User Query: {user_input}
    
    Return ONLY a valid JSON object in this format:
    {{"intent": "intent_name", "confidence": 0.9}}
    """
    
    try:
        response = client.chat.completions.create(
            model=MODELS["router"],
            messages=[
                {"role": "system", "content": "You are a precise JSON router. Never explain, only return JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        # Parse response
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        return result
        
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {"intent": "literature_search", "confidence": 0.5}
    except Exception as e:
        return {"intent": "literature_search", "error": str(e)}