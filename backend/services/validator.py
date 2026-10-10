import re
import json

def extract_numbers(text):
    # Extract all numbers from text
    return set(re.findall(r'\b\d+(?:\.\d+)?\b', text))
    
def extract_places(text, route_data):
    # A simple approach: verify if the named stations in the text actually exist in the route
    found_places = []
    # For now, we'll just check the numbers as primary grounding
    return found_places

def validate_explanation(explanation: str, route_data: dict) -> bool:
    text_numbers = extract_numbers(explanation)
    
    route_json_str = json.dumps(route_data)
    route_numbers = extract_numbers(route_json_str)
    
    # Are all numbers in the explanation present in the route data?
    # This is a strict check. For a hackathon, we can allow small deviations or just flag them.
    for num in text_numbers:
        if num not in route_numbers:
            # Maybe it's a derived number, but strict grounding says NO
            return False
            
    return True

def get_fallback_explanation(route_data: dict) -> str:
    # Deterministic template
    metro = route_data.get("metro_only", {})
    if not metro or "error" in metro:
        return "Sorry, I couldn't find a route for that request."
        
    fare = metro.get("fare", "?")
    time = metro.get("total_time_min", "?")
    
    return f"You can take the Metro. The fare will be ₹{fare} and it takes about {time} minutes."
