from google import genai
from google.genai import types
import json
import os

from services.routing import find_route
from services.fares import get_cab_estimate
from services.timetable import get_next_departures

from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path, override=True)

import requests

# Try to get API key, else fallback to templates
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def init_agent():
    if not GEMINI_API_KEY:
        return None
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client

client = init_agent()

def plan_route_tool(origin_id: str, destination_id: str, time: str, mode: str = "fastest"):
    """Plan a multimodal route."""
    route = find_route(origin_id, destination_id, time, mode=mode)
    if not route:
        return {"error": "No route found"}
    return {"metro_only": route}

def compare_options_tool(origin_id: str, destination_id: str, time: str):
    """Get multiple modal options to compare."""
    route = find_route(origin_id, destination_id, time)
    # fake lat lng for cab estimate
    cab = get_cab_estimate(23.0, 72.5, 23.1, 72.6) # placeholder coords
    
    return {
        "metro_only": route,
        "cab": cab,
        "walk": {"time_min": cab["time_min"] * 5, "distance_km": cab["distance_km"], "fare": 0}
    }

def process_chat_message(message: str):
    # 1. Try Ollama (Local)
    ollama_model = os.environ.get("OLLAMA_MODEL", "gemma:2b")
    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": ollama_model, "prompt": message, "stream": False, "options": {"num_ctx": 4096}},
            timeout=3
        )
        if res.status_code == 200:
            return f"[Ollama] {res.json().get('response', '')}"
    except Exception:
        pass
        
    # 2. Try Gemini (Online)
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=message,
            )
            return f"[Gemini] {response.text}"
        except Exception:
            pass
            
    # 3. Fallback to Regex / deterministic rules
    return "[Local Fallback] I understood your message, but AI features are currently offline. Please use the search bar above to plan your journey."
