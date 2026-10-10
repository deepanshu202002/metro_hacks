from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import math
import requests
from datetime import datetime, timedelta
import os

# Ensure offline execution for HuggingFace models
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from services.routing import (
    find_route,
    get_next_departures,
    get_feeder_bus_route,
    get_free_shuttle_route,
    stations,
    graph,
    haversine,
    time_to_min,
    min_to_time
)
from services.fares import (
    calculate_metro_fare,
    calculate_smart_card_fare,
    calculate_cab_fare,
    get_cab_estimate,
    calculate_fare_split
)
import services.analytics as analytics_service

app = FastAPI(title="One Journey API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    origin_id: str
    destination_id: str
    time: str
    mode: str = "fastest"
    accessibility: bool = False

class EventSimRequest(BaseModel):
    attendance: int = 85000
    extra_trains: int = 4
    headway_minutes: int = 5

class CrowdReportRequest(BaseModel):
    station_id: str
    report: str # "empty" | "ok" | "crowded"

class LeaveByRequest(BaseModel):
    origin_id: str
    destination_id: str
    target_arrival_time: str

# In-memory store for crowd reports
crowd_reports_store: Dict[str, List[str]] = {}

@app.get("/")
def read_root():
    return {
        "name": "One Journey Transit Platform",
        "version": "2.0.0",
        "status": "online",
        "stations_count": len(stations),
        "network_km": 68.28
    }

@app.get("/api/health")
def health_check():
    ollama_ok = False
    try:
        res = requests.get("http://localhost:11434/", timeout=1)
        ollama_ok = res.status_code == 200
    except:
        pass
        
    # Check if Gemini key exists
    has_gemini = bool(os.environ.get("GEMINI_API_KEY"))
    
    ai_provider = "ollama" if ollama_ok else ("gemini" if has_gemini else "fallback")
    
    return {
        "status": "ok",
        "mode": "online", # Can be toggleable in client based on this, or client determines its own online/offline via navigator.onLine
        "ai_provider": ai_provider
    }

@app.post("/api/plan")
def plan_route(req: RouteRequest):
    def get_nearest_station(lat_str, lng_str):
        lat = float(lat_str)
        lng = float(lng_str)
        best = None
        best_d = float('inf')
        for s in stations.values():
            d = haversine(lat, lng, s["lat"], s["lng"])
            if d < best_d:
                best_d = d
                best = s["id"]
        return best, best_d

    def resolve_station_id(query_id):
        if query_id in stations or "," in query_id:
            return query_id
            
        q = query_id.lower().replace(" ", "_")
        if q in stations:
            return q
            
        q_no_underscore = q.replace("_", "")
        
        pois = {
            "vastrapur": "23.0371,72.5265",
            "alpha_one": "23.0396,72.5298",
            "palladium": "23.0531,72.5181",
            "kankaria": "23.0062,72.6026",
            "airport": "23.0772,72.6288",
            "law_garden": "23.0253,72.5562",
            "sidi_saiyyed": "23.0270,72.5807",
            "iskcon": "23.0298,72.5076",
            "science_city": "23.0740,72.4939",
            "gujarat_university": "23.0362,72.5447",
            "riverfront": "23.0258,72.5714",
            "akshardham": "23.2295,72.6739",
            "iim_ahmedabad": "23.0334,72.5323",
            "sg_highway": "23.0360,72.5065",
            "civil_hospital": "23.0526,72.6033",
            "prahlad_nagar": "23.0116,72.5020"
        }
        
        for k, coords in pois.items():
            if k.replace("_", "") in q_no_underscore:
                return coords
                
        aliases = {
            "gift": "gift_city",
            "gnlu": "gnlu",
            "motera": "motera_stadium",
            "ahmedabad": "kalupur",
            "kalupur": "kalupur",
            "brts": "brts_hub",
            "amts": "amts_terminal",
            "office": "gift_office"
        }
        
        for k, v in aliases.items():
            if k in q:
                return v
                
        for s_id, s_data in stations.items():
            name_en = s_data.get("name_en", "").lower().replace(" ", "")
            if q_no_underscore in s_id.replace("_", "") or q_no_underscore in name_en:
                return s_id
        return query_id

    origin_lat, origin_lng = None, None
    origin_dist = 0
    origin_id = resolve_station_id(req.origin_id)
    if "," in origin_id:
        origin_lat, origin_lng = map(float, origin_id.split(","))
        origin_id, origin_dist = get_nearest_station(origin_lat, origin_lng)

    dest_lat, dest_lng = None, None
    dest_dist = 0
    destination_id = resolve_station_id(req.destination_id)
    if "," in destination_id:
        dest_lat, dest_lng = map(float, destination_id.split(","))
        destination_id, dest_dist = get_nearest_station(dest_lat, dest_lng)

    if origin_id not in stations or destination_id not in stations:
        raise HTTPException(status_code=404, detail=f"Station not found. Origin: {origin_id}, Dest: {destination_id}")

    # 1. Primary Metro Route
    metro_route = find_route(origin_id, destination_id, req.time, mode=req.mode)
    
    # 2. Feeder Bus Option (GNLU <-> GIFT corridor)
    feeder_bus_route = get_feeder_bus_route(origin_id, destination_id, req.time)

    # 3. Free GIFT City Shuttle Option
    shuttle_route = get_free_shuttle_route(origin_id, destination_id, req.time)

    # 4. Cab fallback/comparison
    s_orig = stations[origin_id]
    s_dest = stations[destination_id]
    cab_est = get_cab_estimate(s_orig["lat"], s_orig["lng"], s_dest["lat"], s_dest["lng"])

    # If user provided GPS walking legs, inject them
    if origin_lat is not None and origin_dist > 0.08 and metro_route:
        walk_time_min = int((origin_dist / 4.0) * 60)
        walk_leg = {
            "mode": "walk",
            "line": "walk",
            "from": "user_origin",
            "to": origin_id,
            "depart": req.time,
            "arrive": req.time,
            "dist": round(origin_dist, 2),
            "path_coords": [[origin_lat, origin_lng], [s_orig["lat"], s_orig["lng"]]],
            "stations": [{"id": "user_origin", "name_en": "Your Location", "lat": origin_lat, "lng": origin_lng}, s_orig]
        }
        metro_route["legs"].insert(0, walk_leg)
        metro_route["total_time_min"] += walk_time_min
        metro_route["distance_km"] = round(metro_route["distance_km"] + origin_dist, 2)

    if dest_lat is not None and dest_dist > 0.08 and metro_route:
        walk_time_min = int((dest_dist / 4.0) * 60)
        walk_leg = {
            "mode": "walk",
            "line": "walk",
            "from": destination_id,
            "to": "user_dest",
            "depart": req.time,
            "arrive": req.time,
            "dist": round(dest_dist, 2),
            "path_coords": [[s_dest["lat"], s_dest["lng"]], [dest_lat, dest_lng]],
            "stations": [s_dest, {"id": "user_dest", "name_en": "Final Destination", "lat": dest_lat, "lng": dest_lng}]
        }
        metro_route["legs"].append(walk_leg)
        metro_route["total_time_min"] += walk_time_min
        metro_route["distance_km"] = round(metro_route["distance_km"] + dest_dist, 2)

    # Calculate Green Miles (CO2 saved vs cab: ~125g CO2/km)
    base_dist = metro_route["distance_km"] if metro_route else cab_est["distance_km"]
    co2_saved_grams = int(base_dist * 125)

    options: Dict[str, Any] = {}

    if metro_route:
        metro_route["smart_card_fare"] = calculate_smart_card_fare(metro_route["fare"])
        metro_route["co2_saved_grams"] = co2_saved_grams
        metro_route["badge"] = "Direct Train • Fast" if metro_route.get("is_direct") else "Lowest Fare • Recommended"
        options["metro_only"] = metro_route

    if feeder_bus_route:
        feeder_bus_route["smart_card_fare"] = feeder_bus_route["fare"]
        feeder_bus_route["co2_saved_grams"] = int(feeder_bus_route["distance_km"] * 105)
        feeder_bus_route["badge"] = "Feeder Bus • Frequent (Every 30m)"
        options["feeder_bus"] = feeder_bus_route

    if shuttle_route:
        shuttle_route["smart_card_fare"] = calculate_smart_card_fare(shuttle_route["fare"])
        shuttle_route["co2_saved_grams"] = co2_saved_grams
        shuttle_route["badge"] = f"Free Shuttle • Leaves {shuttle_route.get('shuttle_lead_minutes', 25)}m prior"
        options["shuttle"] = shuttle_route
        if "metro_only" in options:
            del options["metro_only"]

    # Cab Option (primary fallback when after last service)
    cab_leg = {
        "mode": "cab",
        "line": "Cab/Taxi",
        "from": origin_id,
        "to": destination_id,
        "depart": req.time,
        "arrive": req.time,
        "dist": cab_est["distance_km"],
        "path_coords": [[s_orig["lat"], s_orig["lng"]], [s_dest["lat"], s_dest["lng"]]],
        "stations": [s_orig, s_dest]
    }
    options["cab"] = {
        "legs": [cab_leg],
        "total_time_min": cab_est["time_min"],
        "fare": cab_est["fare"],
        "distance_km": cab_est["distance_km"],
        "transfers": 0,
        "co2_saved_grams": 0,
        "badge": "Night Fallback • Door-to-Door" if not metro_route else "Direct Cab • Premium"
    }

    # If metro is unavailable (e.g. late night), clearly flag fallback
    fallback_message = None
    if not metro_route and not feeder_bus_route:
        fallback_message = "Metro services have ended for today. Taxi / Cab recommended."

    return {
        "options": options,
        "co2_saved_grams": co2_saved_grams,
        "fallback_message": fallback_message
    }

@app.get("/api/network")
def get_network():
    lines = {"Red": [], "Blue": [], "Yellow": [], "Violet": [], "BRTS": []}

    for s_id, edges in graph.items():
        for edge in edges:
            if edge["direction"] == "forward" and edge["line"] in lines:
                lines[edge["line"]].append([
                    [stations[s_id]["lat"], stations[s_id]["lng"]],
                    [stations[edge["to"]]["lat"], stations[edge["to"]]["lng"]]
                ])

    # Multimodal BRTS corridor loop
    brts_route = [
        "rabari_colony", "kalupur", "vadaj", "ranip",
        "sabarmati", "gujarat_university", "paldi", "rabari_colony"
    ]
    for i in range(len(brts_route) - 1):
        s1 = stations.get(brts_route[i])
        s2 = stations.get(brts_route[i+1])
        if s1 and s2:
            lines["BRTS"].append([
                [s1["lat"], s1["lng"]],
                [s2["lat"], s2["lng"]]
            ])

    return {
        "stations": list(stations.values()),
        "lines": lines
    }

class FareSplitRequest(BaseModel):
    legs: List[Dict[str, Any]]
    integrated_fare: float
    method: str = "pro-rata"

@app.post("/api/fare/split")
def split_fare(req: FareSplitRequest):
    splits = calculate_fare_split(req.legs, req.integrated_fare, method=req.method)
    return {"splits": splits, "method": req.method}

@app.get("/api/settlement")
def get_settlement():
    try:
        with open(os.path.join(os.path.dirname(__file__), "data", "settlement_report.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"error": "Report not found. Run settlement.py first."}

@app.get("/api/departures")
def get_departures_board(station_id: str, time: Optional[str] = None):
    station_id = station_id.lower().replace(" ", "_")
    if station_id not in stations:
        raise HTTPException(status_code=404, detail="Station not found")

    cur_time_str = time if time else datetime.now().strftime("%H:%M:%S")
    cur_min = time_to_min(cur_time_str)

    deps = get_next_departures(station_id, cur_min, limit=8)
    enriched = []
    for d in deps:
        wait_min = int(d["time_min"] - cur_min)
        is_last = (d["time_min"] >= (21 * 60 + 45)) # after 21:45
        enriched.append({
            "line": d["line"],
            "direction": d["direction"],
            "destination": stations.get(d["destination"], {}).get("name_en", d["destination"]),
            "departure_time": d["time"],
            "wait_minutes": max(0, wait_min),
            "service": d.get("service", "Regular Metro"),
            "is_last_service": is_last
        })

    # Add feeder bus departures if GNLU or GIFT City
    if station_id in ["gnlu", "gift_city"]:
        next_bus_min = math.ceil(cur_min / 30.0) * 30.0
        enriched.append({
            "line": "Connector Bus",
            "direction": "PDEU / GIFT City" if station_id == "gnlu" else "PDEU / GNLU",
            "destination": "GIFT Offices" if station_id == "gnlu" else "GNLU Metro",
            "departure_time": min_to_time(next_bus_min),
            "wait_minutes": max(0, int(next_bus_min - cur_min)),
            "service": "Free 30-min Feeder Bus",
            "is_last_service": (next_bus_min >= 20 * 60)
        })

    return {
        "station": stations[station_id],
        "current_time": cur_time_str,
        "departures": enriched
    }

@app.post("/api/leave-by")
def calculate_leave_by(req: LeaveByRequest):
    """
    Leave-by planner: calculates exact minute to leave home/origin to catch
    the target train and arrive on time.
    """
    s_orig = stations.get(req.origin_id.lower().replace(" ", "_"))
    s_dest = stations.get(req.destination_id.lower().replace(" ", "_"))
    if not s_orig or not s_dest:
        raise HTTPException(status_code=404, detail="Station not found")

    target_min = time_to_min(req.target_arrival_time)
    # Search backwards from target arrival
    best_dep_time = None
    best_metro = None

    for test_h in range(6, 23):
        for test_m in (0, 15, 30, 45):
            t_str = f"{test_h:02d}:{test_m:02d}:00"
            r = find_route(s_orig["id"], s_dest["id"], t_str)
            if r:
                arr_min = time_to_min(r["legs"][-1]["arrive"])
                if arr_min <= target_min:
                    best_dep_time = r["legs"][0]["depart"]
                    best_metro = r

    if not best_dep_time:
        best_dep_time = req.target_arrival_time
        leave_by_time = req.target_arrival_time
    else:
        # Buffer of 10 min for walking to platform / ticket validation
        leave_by_min = time_to_min(best_dep_time) - 10
        leave_by_time = min_to_time(leave_by_min)

    return {
        "leave_by_time": leave_by_time,
        "recommended_train_departure": best_dep_time,
        "target_arrival_time": req.target_arrival_time,
        "walk_buffer_minutes": 10,
        "summary": f"Leave by {leave_by_time[:5]} to catch the {best_dep_time[:5]} train from {s_orig['name_en']}."
    }

@app.get("/api/nearby")
def get_nearby_stations(lat: float, lng: float, limit: int = 4):
    sorted_s = []
    for s in stations.values():
        dist = haversine(lat, lng, s["lat"], s["lng"])
        walk_min = int((dist / 4.2) * 60)
        sorted_s.append({
            "station": s,
            "distance_km": round(dist, 2),
            "walk_time_min": walk_min
        })

    sorted_s.sort(key=lambda x: x["distance_km"])
    top = sorted_s[:limit]

    # Enrich with next 2 departures
    cur_min = datetime.now().hour * 60 + datetime.now().minute
    for item in top:
        deps = get_next_departures(item["station"]["id"], cur_min, limit=2)
        item["next_departures"] = [
            {"time": d["time"][:5], "destination": stations.get(d["destination"], {}).get("name_en", d["destination"])}
            for d in deps
        ]

    return {"nearby": top}

@app.post("/api/crowd/report")
def submit_crowd_report(req: CrowdReportRequest):
    s_id = req.station_id.lower().replace(" ", "_")
    if s_id not in stations:
        raise HTTPException(status_code=404, detail="Station not found")

    if s_id not in crowd_reports_store:
        crowd_reports_store[s_id] = []
    crowd_reports_store[s_id].append(req.report)
    
    # Keep last 20 reports
    crowd_reports_store[s_id] = crowd_reports_store[s_id][-20:]

    return {
        "status": "success",
        "station_id": s_id,
        "total_reports": len(crowd_reports_store[s_id]),
        "latest_sentiment": req.report,
        "message": "Thank you! Live crowd report recorded."
    }

@app.post("/api/ticket/generate")
def generate_mock_ticket(req: Dict[str, Any]):
    origin = req.get("origin", "Old High Court")
    destination = req.get("destination", "GIFT City")
    fare = req.get("fare", 20)
    smart_card = req.get("use_smart_card", True)
    discounted_fare = calculate_smart_card_fare(fare) if smart_card else fare

    now = datetime.now()
    valid_until = now + timedelta(hours=3)

    return {
        "ticket_id": f"OJ-{now.strftime('%y%m%d')}-{abs(hash(origin+destination)) % 90000 + 10000}",
        "origin": origin,
        "destination": destination,
        "base_fare": fare,
        "fare_paid": discounted_fare,
        "discount_applied": (fare - discounted_fare),
        "smart_card_used": smart_card,
        "issued_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "valid_until": valid_until.strftime("%H:%M:%S"),
        "qr_payload": f"GMRC|TOKEN|{now.strftime('%Y%m%d%H%M')}|{origin}|{destination}|{discounted_fare}|INR"
    }

@app.get("/api/data-sources")
def get_data_sources():
    return {
        "datasets": [
            {
                "id": "network",
                "name": "GMRC Station Network (54 Stations, 68.28 km)",
                "source": "GMRC Route Info & Phase 2 Gandhinagar Alignment",
                "source_date": "2025-02-13",
                "verified": True,
                "type": "REAL GEOMETRY"
            },
            {
                "id": "direct_trips",
                "name": "APMC <-> GIFT City Direct & GNLU Shuttle Trips",
                "source": "GMRC Public Notice 17-Sep-2024 & Press Note 13-Feb-2025",
                "source_date": "2025-02-13",
                "verified": True,
                "type": "REAL TIMETABLE"
            },
            {
                "id": "headway_timetables",
                "name": "Red & Blue Lines Headway Timetable (10-12 min intervals)",
                "source": "GMRC Train Information Operating Schedule",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "SYNTHETIC SCHEDULE (Verify with GMRC)"
            },
            {
                "id": "yellow_line",
                "name": "Yellow Line Gandhinagar Extension Schedule",
                "source": "Phase 2 Commissioning Press Releases",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "SYNTHETIC SCHEDULE (Verify with GMRC)"
            },
            {
                "id": "feeder_bus",
                "name": "GNLU <-> GIFT City 30-min Connector Bus",
                "source": "Feeder Bus Guidelines (GSRTC/GMRC)",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "SYNTHETIC FEEDER (Verify with GSRTC)"
            },
            {
                "id": "gift_shuttle",
                "name": "Free GIFT City SEZ Internal Feeder Shuttle",
                "source": "GIFT SEZ Internal Transport Policy",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "SYNTHETIC FEEDER (GIFT City -> Metro only)"
            },
            {
                "id": "fares",
                "name": "GMRC Fare Structure & Slabs (₹5 - ₹25)",
                "source": "GMRC Published Fare Slabs & Smart Card Rules",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "OBSERVED SLABS (Check against GMRC chart)"
            },
            {
                "id": "ridership",
                "name": "Station Boardings & Crowd Model",
                "source": "GMRC Published Daily Totals (1.5-2.0 lakh weekday, 2.2 lakh event)",
                "source_date": "2025-02-13",
                "verified": False,
                "type": "SYNTHETIC DATA (Calibrated to published totals)"
            }
        ]
    }

@app.get("/api/disruptions")
def get_disruptions():
    return {
        "active_disruptions": [
            {
                "id": "d-1",
                "line": "Blue",
                "severity": "minor",
                "message": "Platform 2 escalator maintenance at Kalupur. Lift and stairs fully operational.",
                "valid_until": "22:00"
            }
        ]
    }

@app.get("/api/events/active")
def get_active_events():
    return {
        "events": [
            {
                "id": "ev-1",
                "title": "Match Day at Narendra Modi Stadium",
                "venue_station": "Motera Stadium",
                "expected_attendance": 85000,
                "impact_window": "16:00 - 23:00",
                "advisories": [
                    "Direct GIFT City <-> APMC trains available.",
                    "Use Sabarmati Railway Station or Koteshwar Road for lower platform queues.",
                    "Special post-match services operating until 00:30."
                ]
            }
        ]
    }

# ==================== ANALYTICS API ENDPOINTS (PART B) ====================

@app.get("/api/analytics/overview")
def get_analytics_overview(day_type: str = "weekday", hour: int = 9):
    return analytics_service.get_overview(day_type=day_type, hour=hour)

@app.get("/api/analytics/stations/congestion")
def get_stations_congestion(hour: int = 9, day_type: str = "weekday"):
    return {
        "hour": hour,
        "day_type": day_type,
        "stations": analytics_service.get_station_congestion(hour=hour, day_type=day_type)
    }

@app.get("/api/analytics/top-congested")
def get_top_congested(hour: int = 9, day_type: str = "weekday", limit: int = 10):
    return {
        "ranking": analytics_service.get_top_congested_ranking(hour=hour, day_type=day_type, top_k=limit)
    }

@app.get("/api/analytics/peak-hours")
def get_peak_hours(station_id: Optional[str] = None, day_type: str = "weekday"):
    return {
        "day_type": day_type,
        "chart": analytics_service.get_peak_hours_chart(selected_station_id=station_id, day_type=day_type)
    }

@app.get("/api/analytics/od-flows")
def get_od_flows():
    return {
        "flows": analytics_service.get_od_flows()
    }

@app.get("/api/analytics/forecast")
def get_crowd_forecast(station_id: str = "old_high_court", current_hour: int = 9, day_type: str = "weekday"):
    return analytics_service.get_crowd_forecast(station_id, current_hour, day_type)

@app.get("/api/analytics/interchanges")
def get_interchange_analytics():
    return analytics_service.get_interchange_analytics()

@app.get("/api/analytics/delays")
def get_delay_analytics():
    return analytics_service.get_delay_analytics()

@app.get("/api/analytics/clusters")
def get_clusters():
    return analytics_service.get_station_clusters()

@app.get("/api/analytics/anomalies")
def get_anomalies():
    return {"anomalies": analytics_service.get_anomalies()}

@app.post("/api/analytics/event-simulate")
def simulate_event_impact(req: EventSimRequest):
    return analytics_service.simulate_event(
        attendance=req.attendance,
        extra_trains=req.extra_trains,
        headway_minutes=req.headway_minutes
    )

@app.get("/api/analytics/insights")
def get_narrated_insights(lang: str = "en"):
    return analytics_service.get_narrated_insights(lang=lang)

# ==================== VOICE, AGENT, EXPLAIN ENDPOINTS ====================

@app.get("/api/search")
def search_places(q: str):
    # Local fallback search over stations and aliases instead of OpenStreetMap
    q_lower = q.lower().strip()
    results = []
    
    # Simple alias mapping
    aliases = {
        "gift": "gift_city",
        "gnlu": "gnlu",
        "old high court": "old_high_court",
        "motera": "motera_stadium",
        "ahmedabad station": "kalupur",
        "railway station": "kalupur"
    }
    
    for s_id, s_data in stations.items():
        score = 0
        name_en = s_data.get("name_en", "").lower()
        name_gu = s_data.get("name_gu", "").lower()
        name_hi = s_data.get("name_hi", "").lower()
        
        if q_lower in name_en or q_lower in name_gu or q_lower in name_hi or q_lower in s_id.lower():
            score = 100
            
        # Check aliases
        for alias, target_id in aliases.items():
            if q_lower in alias and s_id == target_id:
                score = 90
                
        if score > 0:
            results.append({
                "name": s_data.get("name_en"),
                "lat": s_data.get("lat"),
                "lng": s_data.get("lng"),
                "score": score
            })
            
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"results": results[:5]}

@app.post("/api/parse")
def parse_text(req: dict):
    from services.agent import process_chat_message
    response_text = process_chat_message(req.get("text", ""))
    return {"response": response_text}

@app.post("/api/explain")
def explain_route(req: dict):
    from services.validator import validate_explanation, get_fallback_explanation
    raw_explanation = "This trip takes 40 minutes and costs 30 rupees."
    if validate_explanation(raw_explanation, req):
        return {"explanation": raw_explanation}
    return {"explanation": get_fallback_explanation(req)}

@app.post("/api/voice")
async def voice_input(request: Request):
    return {
        "transcript": "Take me to GIFT city",
        "detected_language": "en-IN",
        "origin": "apmc",
        "destination": "gift_city",
        "time": "08:00:00",
        "confidence": 0.95
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
