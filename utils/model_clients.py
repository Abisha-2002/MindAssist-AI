"""
Model Client Management
Handles connections to Groq and OpenRouter APIs
"""
import streamlit as st
from groq import Groq
from openai import OpenAI

@st.cache_resource
def get_groq_client():
    """Initialize and cache Groq client"""
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None

@st.cache_resource
def get_openrouter_client():
    """Initialize and cache OpenRouter client"""
    try:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"],
        )
    except Exception as e:
        st.error(f"Failed to initialize OpenRouter client: {e}")
        return None

# Model selection mapping - USING CONFIRMED WORKING MODELS
MODELS = {
    "router": "llama-3.1-8b-instant",                    # Groq - Fast
    "reasoning": "meta-llama/llama-3.1-70b-instruct",   # OpenRouter - Free & Working!
}

def get_model_config(task_type):
    """Get the appropriate model for a specific task"""
    if task_type == "router":
        return {
            "model": MODELS["router"],
            "provider": "Groq",
            "client": get_groq_client()
        }
    elif task_type == "reasoning":
        return {
            "model": MODELS["reasoning"],
            "provider": "OpenRouter",
            "client": get_openrouter_client()
        }
    else:
        return None