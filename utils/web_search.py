"""
Web Search Utility using Serper API
Free tier: 2,500 searches/month
"""
import requests
import streamlit as st

def web_search(query, num_results=5):
    """
    Search the web using Serper API
    Returns: List of search results with title, link, snippet
    """
    try:
        api_key = st.secrets["SERPER_API_KEY"]
    except KeyError:
        return {"error": "SERPER_API_KEY not found in secrets.toml"}
    
    url = "https://google.serper.dev/search"
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,
        "num": num_results
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", "No Title"),
                "link": item.get("link", "#"),
                "snippet": item.get("snippet", "No description available")
            })
        
        return results
        
    except requests.exceptions.Timeout:
        return {"error": "Search request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Search failed: {str(e)}"}