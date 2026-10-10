import json
import numpy as np
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz
import os

model = None
place_embeddings = None
places = []

def init_places():
    global model, place_embeddings, places
    # Load stations
    with open('backend/data/stations.json', 'r', encoding='utf-8') as f:
        stations = json.load(f)
        
    for s in stations:
        # Index english, hindi, gujarati names
        places.append({"id": s["id"], "type": "station", "name": s["name_en"]})
        places.append({"id": s["id"], "type": "station", "name": s["name_hi"]})
        places.append({"id": s["id"], "type": "station", "name": s["name_gu"]})
        
    # Also add some landmarks based on prompt
    landmarks = [
        {"id": "law_garden", "name": "Law Garden"},
        {"id": "akshardham", "name": "Akshardham"},
        {"id": "kankaria", "name": "Kankaria"},
        {"id": "gift_city", "name": "GIFT City"},
        {"id": "sabarmati_ashram", "name": "Sabarmati Ashram"}
    ]
    for l in landmarks:
        places.append({"id": l["id"], "type": "landmark", "name": l["name"]})

    # Initialize model (using a lightweight multilingual model if available, else paraphrase-multilingual-MiniLM-L12-v2)
    # Note: Downloading this model might take a bit of time on first run
    print("Loading multilingual sentence transformer...")
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        names = [p["name"] for p in places]
        place_embeddings = model.encode(names, convert_to_tensor=True)
    except Exception as e:
        print("Failed to load sentence transformer, will fallback to fuzzy matching.", e)

init_places()

def search_place(query, threshold=0.85):
    # Try fuzzy matching first as backup or fast path
    names = [p["name"] for p in places]
    best_match_fuzz = process.extractOne(query, names, scorer=fuzz.WRatio)
    
    if best_match_fuzz and best_match_fuzz[1] > 90:
        idx = names.index(best_match_fuzz[0])
        return {"id": places[idx]["id"], "name": places[idx]["name"], "confidence": best_match_fuzz[1]/100.0, "method": "fuzz"}
        
    # Semantic search
    if model is not None and place_embeddings is not None:
        from sentence_transformers import util
        query_emb = model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_emb, place_embeddings, top_k=3)[0]
        
        if hits[0]['score'] >= threshold:
            idx = hits[0]['corpus_id']
            return {"id": places[idx]["id"], "name": places[idx]["name"], "confidence": hits[0]['score'], "method": "semantic"}
            
        # Return top 3 alternatives if confidence is low
        alts = []
        for h in hits:
            idx = h['corpus_id']
            alts.append({"id": places[idx]["id"], "name": places[idx]["name"], "score": h['score']})
        return {"alternatives": alts}
        
    # Fallback to fuzz
    if best_match_fuzz:
        idx = names.index(best_match_fuzz[0])
        return {"id": places[idx]["id"], "name": places[idx]["name"], "confidence": best_match_fuzz[1]/100.0, "method": "fuzz_fallback"}
        
    return None
    
if __name__ == "__main__":
    print(search_place("Sabarmati stesan"))
    print(search_place("સાબરમતી સ્ટેશન"))
