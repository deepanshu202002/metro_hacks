import json
import heapq
from datetime import datetime, timedelta
import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_data():
    with open(os.path.join(DATA_DIR, 'stations.json'), 'r', encoding='utf-8') as f:
        stations_list = json.load(f)
        stations = {s["id"]: s for s in stations_list}

    with open(os.path.join(DATA_DIR, 'timetable.json'), 'r', encoding='utf-8') as f:
        timetable = json.load(f)

    with open(os.path.join(DATA_DIR, 'config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)

    trips = timetable.get("__trips__", {})
    return stations, timetable, config, trips

stations, timetable, config, trips = load_data()

# Inject mock BRTS and AMTS stations for DevFest Gandhinagar PS-08 Demo
mock_stations = [
    {"id": "brts_hub", "name_en": "BRTS Zonal Hub", "lat": 23.0720, "lng": 72.5650, "lines": ["BRTS"], "operator": "BRTS"},
    {"id": "amts_terminal", "name_en": "AMTS Central Terminal", "lat": 23.0150, "lng": 72.5650, "lines": ["AMTS"], "operator": "AMTS"}
]
for ms in mock_stations:
    stations[ms["id"]] = ms

def reload_routing_data():
    global stations, timetable, config, trips
    stations, timetable, config, trips = load_data()
    for ms in mock_stations:
        stations[ms["id"]] = ms

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def time_to_min(time_str):
    if len(time_str) == 5:
        time_str += ":00"
    t = datetime.strptime(time_str, "%H:%M:%S")
    return t.hour * 60 + t.minute + t.second / 60.0

def min_to_time(minutes):
    m = int(minutes)
    s = int((minutes - m) * 60)
    h = (m // 60) % 24
    m = m % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# Build adjacent graph
graph = {s_id: [] for s_id in stations}

blue_order = [
    "thaltej_gam", "thaltej", "doordarshan_kendra", "gurukul_road",
    "gujarat_university", "commerce_six_road", "sp_stadium", "old_high_court",
    "shahpur", "ghee_kanta", "kalupur", "kankaria_east", "apparel_park",
    "amraivadi", "rabari_colony", "vastral", "nirant_cross_road", "vastral_gam"
]

red_order = [
    "apmc", "jivraj_park", "rajiv_nagar", "shreyas", "paldi", "gandhigram",
    "old_high_court", "usmanpura", "vijay_nagar", "vadaj", "ranip",
    "sabarmati_railway_station", "aec", "sabarmati", "motera_stadium"
]

yellow_order = [
    "motera_stadium", "koteshwar_road", "vishwakarma_college", "tapovan_circle",
    "narmada_canal", "koba_circle", "juna_koba", "koba_gaam", "gnlu",
    "raysan", "randesan", "dholakuva_circle", "infocity", "sector_1",
    "sector_10a", "sachivalaya", "akshardham", "juna_sachivalaya",
    "sector_16", "sector_24", "mahatma_mandir"
]

violet_order = ["gnlu", "pdeu", "gift_city"]

def add_line_edges(seq, line_name, speed_kmh=35, dwell_sec=25):
    for i in range(len(seq) - 1):
        s1 = stations.get(seq[i])
        s2 = stations.get(seq[i+1])
        if not s1 or not s2:
            continue
        dist = haversine(s1["lat"], s1["lng"], s2["lat"], s2["lng"])
        time_min = (dist / speed_kmh) * 60 + (dwell_sec / 60.0)

        graph[s1["id"]].append({
            "to": s2["id"],
            "line": line_name,
            "direction": "forward",
            "travel_time_min": time_min,
            "dist": dist
        })
        graph[s2["id"]].append({
            "to": s1["id"],
            "line": line_name,
            "direction": "backward",
            "travel_time_min": time_min,
            "dist": dist
        })

add_line_edges(blue_order, "Blue", 35, 25)
add_line_edges(red_order, "Red", 35, 25)
add_line_edges(yellow_order, "Yellow", 34, 25)
add_line_edges(violet_order, "Violet", 35, 25)

# Add Mock BRTS and AMTS edges
add_line_edges(["brts_hub", "vadaj"], "BRTS", 25, 30)
add_line_edges(["amts_terminal", "paldi"], "AMTS", 20, 30)

def get_next_departures(station_id, current_min, limit=12):
    res = []
    terminals = {
        "Blue": {"forward": "Vastral Gam", "backward": "Thaltej Gam"},
        "Red": {"forward": "Motera Stadium", "backward": "APMC"},
        "Yellow": {"forward": "Mahatma Mandir", "backward": "Motera Stadium"},
        "Violet": {"forward": "GIFT City", "backward": "GNLU"},
        "BRTS": {"forward": "Circular Route", "backward": "Circular Route"},
        "AMTS": {"forward": "City Hub", "backward": "City Hub"}
    }
    
    lines_dirs = set()
    for edge in graph.get(station_id, []):
        lines_dirs.add((edge["line"], edge["direction"]))
        
    for line, direction in lines_dirs:
        freq = 7 if line in ["Blue", "Red"] else (15 if line == "Yellow" else (5 if line in ["BRTS", "AMTS"] else 60))
        dest = terminals.get(line, {}).get(direction, "Terminal")
        
        if line == "Violet":
            gen_count = 0
            test_min = math.ceil(current_min / freq) * freq
            while gen_count < 3 and test_min <= 25 * 60:
                h = (test_min / 60.0) % 24
                if (7 <= h <= 10.5) or (16 <= h <= 23.5):
                    res.append({
                        "time": min_to_time(test_min % (24 * 60)),
                        "time_min": test_min,
                        "line": line,
                        "direction": direction,
                        "destination": dest,
                        "service": "Direct Train"
                    })
                    gen_count += 1
                test_min += freq
        else:
            first_dep = math.ceil(current_min / freq) * freq
            for i in range(3):
                dep_min = first_dep + i * freq
                if dep_min <= 25 * 60: # Extended for hackathon demo testing at night
                    res.append({
                        "time": min_to_time(dep_min % (24 * 60)),
                        "time_min": dep_min,
                        "line": line,
                        "direction": direction,
                        "destination": dest,
                        "service": "Regular Metro" if line not in ["BRTS", "AMTS"] else f"{line} Service"
                    })
                    
    res.sort(key=lambda x: x["time_min"])
    return res[:limit]

def check_direct_trip(start_id, end_id, start_min):
    """Checks if a direct trip exists in explicit trips without transfers."""
    best_trip = None
    best_depart_min = float('inf')
    best_arrival_min = float('inf')
    best_stops = None

    for trip_id, tr in trips.items():
        stop_times = tr.get("stop_times", [])
        station_ids = [st["station_id"] for st in stop_times]
        if start_id in station_ids and end_id in station_ids:
            start_idx = station_ids.index(start_id)
            end_idx = station_ids.index(end_id)
            if start_idx < end_idx: # Correct direction
                dep_str = stop_times[start_idx]["departure"]
                arr_str = stop_times[end_idx]["arrival"]
                dep_min = time_to_min(dep_str)
                arr_min = time_to_min(arr_str)
                if dep_min >= start_min and dep_min < best_depart_min:
                    best_depart_min = dep_min
                    best_arrival_min = arr_min
                    best_trip = tr
                    best_stops = stop_times[start_idx:end_idx+1]

    if best_trip:
        from services.fares import calculate_metro_fare
        path_stations = [stations[st["station_id"]] for st in best_stops]
        dist = 0
        for i in range(len(path_stations) - 1):
            dist += haversine(path_stations[i]["lat"], path_stations[i]["lng"],
                              path_stations[i+1]["lat"], path_stations[i+1]["lng"])
        fare = calculate_metro_fare(dist, start_id, end_id)
        
        leg = {
            "mode": "metro",
            "line": best_trip.get("line", "Direct"),
            "service": best_trip.get("service", "Direct Train"),
            "from": start_id,
            "to": end_id,
            "depart": min_to_time(best_depart_min),
            "arrive": min_to_time(best_arrival_min),
            "dist": round(dist, 2),
            "path_coords": [[s["lat"], s["lng"]] for s in path_stations],
            "stations": path_stations
        }
        return {
            "legs": [leg],
            "total_time_min": int(best_arrival_min - start_min),
            "fare": fare,
            "distance_km": round(dist, 2),
            "transfers": 0,
            "is_direct": True,
            "service": best_trip.get("service", "Direct Train")
        }
    return None

def find_route(start_id, end_id, start_time_str, mode="fastest"):
    start_min = time_to_min(start_time_str if len(start_time_str) >= 7 else start_time_str + ":00")

    # First check direct trip (e.g. APMC <-> GIFT City direct train)
    direct_option = check_direct_trip(start_id, end_id, start_min)
    if direct_option and mode != "ignore_direct":
        # If departure is reasonably soon (within 60 mins), direct option is best!
        wait_for_direct = time_to_min(direct_option["legs"][0]["depart"]) - start_min
        if wait_for_direct <= 60:
            return direct_option

    # Dijkstra priority queue: (cost_min, current_min, current_station, path, current_line)
    # path is a list of (station_id, arrival_min, line)
    pq = [(0, start_min, start_id, [(start_id, start_min, None)], None)]
    visited = {}

    while pq:
        cost, curr_min, curr_station, path, curr_line = heapq.heappop(pq)

        if curr_station == end_id:
            res = format_route(path, start_min)
            # If direct exists and has same or better convenience, ensure direct is prioritized
            if direct_option and direct_option["transfers"] == 0 and res["transfers"] > 0:
                # If direct train departs within 45 min of transfer arrival, offer direct!
                if direct_option["total_time_min"] <= res["total_time_min"] + 45:
                    return direct_option
            return res

        state = (curr_station, curr_line)
        if state in visited and visited[state] < cost:
            continue
        visited[state] = cost

        for edge in graph.get(curr_station, []):
            to_station = edge["to"]
            line = edge["line"]
            direction = edge["direction"]
            travel_time = edge["travel_time_min"]

            wait_time = 0
            transfer_penalty = 0
            if curr_line != line:
                if curr_line is not None:
                    transfer_penalty = config.get("walk", {}).get("transfer_buffer_minutes", 3)

                ready_time = curr_min + transfer_penalty
                next_dep = None
                for d in timetable.get(curr_station, []):
                    if not isinstance(d, dict):
                        continue
                    if d.get("line") == line and d.get("direction") == direction:
                        d_min = time_to_min(d["time"])
                        if d_min >= ready_time:
                            next_dep = d_min
                            break
                if next_dep is None:
                    if line in ["BRTS", "AMTS"]:
                        # Assume 5-min frequency for high-frequency modes
                        next_dep = ready_time + (5 - (ready_time % 5))
                    else:
                        continue
                wait_time = (next_dep - curr_min)

            next_min = curr_min + wait_time + travel_time
            new_cost = next_min - start_min

            new_path = list(path)
            new_path.append((to_station, next_min, line))
            heapq.heappush(pq, (new_cost, next_min, to_station, new_path, line))

    # Fallback to direct option if Dijkstra found no train (e.g. evening direct)
    if direct_option:
        return direct_option
    return None

def format_route(path, start_min):
    from services.fares import calculate_metro_fare
    dist = 0
    legs = []
    curr_leg = None

    for i in range(1, len(path)):
        s1 = stations[path[i-1][0]]
        s2 = stations[path[i][0]]
        line = path[i][2]
        arr_min = path[i][1]

        d = haversine(s1["lat"], s1["lng"], s2["lat"], s2["lng"])
        dist += d

        if curr_leg and curr_leg["line"] == line:
            curr_leg["to"] = s2["id"]
            curr_leg["arrive"] = min_to_time(arr_min)
            curr_leg["dist"] = round(curr_leg["dist"] + d, 2)
            curr_leg["path_coords"].append([s2["lat"], s2["lng"]])
            curr_leg["stations"].append(s2)
        else:
            if curr_leg:
                legs.append(curr_leg)
            op = "Metro"
            leg_fare = calculate_metro_fare(d, s1["id"], s2["id"])
            if line == "BRTS":
                op = "BRTS"
                leg_fare = max(10, int(d * 4)) # Example BRTS fare
            elif line == "AMTS":
                op = "AMTS"
                leg_fare = max(8, int(d * 3)) # Example AMTS fare
                
            curr_leg = {
                "mode": line.lower() if line in ["BRTS", "AMTS"] else "metro",
                "line": line,
                "service": f"{line} Regular",
                "from": s1["id"],
                "to": s2["id"],
                "depart": min_to_time(path[i-1][1]),
                "arrive": min_to_time(arr_min),
                "dist": round(d, 2),
                "operator": op,
                "fare": leg_fare,
                "path_coords": [[s1["lat"], s1["lng"]], [s2["lat"], s2["lng"]]],
                "stations": [s1, s2]
            }

    if curr_leg:
        legs.append(curr_leg)

    origin_id = path[0][0]
    dest_id = path[-1][0]
    
    total_standalone_fare = sum(l["fare"] for l in legs)
    fare = int(total_standalone_fare * 0.9) # 10% integration discount

    return {
        "legs": legs,
        "total_time_min": int(path[-1][1] - start_min),
        "fare": fare,
        "distance_km": round(dist, 2),
        "transfers": max(0, len(legs) - 1),
        "is_direct": (len(legs) == 1)
    }

def get_feeder_bus_route(start_id, end_id, start_time_str):
    """Builds connector bus option between GNLU and GIFT City offices."""
    bus_conf = config.get("gnlu_gift_connector_bus", {})
    start_min = time_to_min(start_time_str if len(start_time_str) >= 7 else start_time_str + ":00")

    # If route involves Mahatma Mandir or Yellow line to GIFT City
    # Step 1: Metro from start_id to GNLU
    # Step 2: Bus from GNLU to GIFT City
    if (end_id in ["gift_city", "pdeu"]) and start_id != "gnlu":
        metro_part = find_route(start_id, "gnlu", start_time_str)
        if not metro_part:
            return None
        arrival_at_gnlu = time_to_min(metro_part["legs"][-1]["arrive"])
        # Next bus every 30 min (e.g., at :00 and :30)
        bus_dep_min = math.ceil(arrival_at_gnlu / 30.0) * 30.0
        bus_travel_time = bus_conf.get("travel_time_min", 14)
        bus_arr_min = bus_dep_min + bus_travel_time

        s_gnlu = stations["gnlu"]
        s_pdeu = stations["pdeu"]
        s_gift = stations["gift_city"]

        bus_leg = {
            "mode": "bus",
            "line": "GNLU-GIFT Connector",
            "service": "feeder_bus",
            "from": "gnlu",
            "to": end_id,
            "depart": min_to_time(bus_dep_min),
            "arrive": min_to_time(bus_arr_min),
            "dist": 5.4,
            "operator": "BRTS",
            "fare": bus_conf.get("fare", 10),
            "path_coords": [[s_gnlu["lat"], s_gnlu["lng"]], [s_pdeu["lat"], s_pdeu["lng"]], [s_gift["lat"], s_gift["lng"]]],
            "stations": [s_gnlu, s_pdeu, s_gift]
        }

        all_legs = list(metro_part["legs"]) + [bus_leg]
        total_standalone_fare = sum(l.get("fare", 0) for l in all_legs)
        total_fare = int(total_standalone_fare * 0.9)
        total_time = int(bus_arr_min - start_min)

        return {
            "legs": all_legs,
            "total_time_min": total_time,
            "fare": total_fare,
            "distance_km": round(metro_part["distance_km"] + 5.4, 2),
            "transfers": len(all_legs) - 1,
            "is_connector_bus": True
        }
    elif (start_id in ["gift_city", "pdeu"]) and end_id != "gnlu":
        # Reverse connector bus
        bus_dep_min = math.ceil(start_min / 30.0) * 30.0
        bus_arr_min = bus_dep_min + bus_conf.get("travel_time_min", 14)
        s_gnlu = stations["gnlu"]
        s_gift = stations["gift_city"]

        bus_leg = {
            "mode": "bus",
            "line": "GNLU-GIFT Connector",
            "service": "feeder_bus",
            "from": start_id,
            "to": "gnlu",
            "depart": min_to_time(bus_dep_min),
            "arrive": min_to_time(bus_arr_min),
            "dist": 5.4,
            "path_coords": [[s_gift["lat"], s_gift["lng"]], [s_gnlu["lat"], s_gnlu["lng"]]],
            "stations": [s_gift, s_gnlu]
        }
        metro_part = find_route("gnlu", end_id, min_to_time(bus_arr_min + 3))
        if not metro_part:
            return None
        all_legs = [bus_leg] + list(metro_part["legs"])
        return {
            "legs": all_legs,
            "total_time_min": int(time_to_min(metro_part["legs"][-1]["arrive"]) - start_min),
            "fare": metro_part["fare"] + bus_conf.get("fare", 10),
            "distance_km": round(metro_part["distance_km"] + 5.4, 2),
            "transfers": len(all_legs) - 1,
            "is_connector_bus": True
        }
    return None

def get_free_shuttle_route(start_id, end_id, start_time_str):
    """
    Free GIFT City shuttle: departs 25 min before the metro departure it connects to.
    Operates in GIFT City -> metro direction only.
    """
    if start_id != "gift_city":
        return None

    shuttle_conf = config.get("gift_city_shuttle", {})
    lead_min = shuttle_conf.get("shuttle_lead_minutes", 25)
    start_min = time_to_min(start_time_str if len(start_time_str) >= 7 else start_time_str + ":00")

    # Find next metro departing from GIFT City after (start_min + 15)
    deps = timetable.get("gift_city", [])
    matched_metro_dep = None
    for d in deps:
        d_min = time_to_min(d["time"])
        if d_min >= start_min + lead_min:
            matched_metro_dep = d_min
            break

    if not matched_metro_dep:
        return None

    metro_route = find_route("gift_city", end_id, min_to_time(matched_metro_dep))
    if not metro_route:
        return None

    actual_metro_dep_min = time_to_min(metro_route["legs"][0]["depart"])
    shuttle_dep_min = actual_metro_dep_min - lead_min
    shuttle_arr_min = actual_metro_dep_min - 5 # 5 min buffer before metro departure

    s_gift = stations["gift_city"]
    shuttle_leg = {
        "mode": "shuttle",
        "line": "GIFT SEZ Free Shuttle",
        "service": "free_shuttle",
        "from": "gift_office",
        "to": "gift_city",
        "depart": min_to_time(shuttle_dep_min),
        "arrive": min_to_time(shuttle_arr_min),
        "dist": 1.8,
        "operator": "GIFT Shuttle",
        "fare": 0,
        "path_coords": [[23.1660, 72.6840], [s_gift["lat"], s_gift["lng"]]],
        "stations": [{"id": "gift_office", "name_en": "GIFT City Office Hub", "lat": 23.1660, "lng": 72.6840}, s_gift]
    }

    all_legs = [shuttle_leg] + list(metro_route["legs"])
    return {
        "legs": all_legs,
        "total_time_min": int(time_to_min(metro_route["legs"][-1]["arrive"]) - start_min),
        "fare": metro_route["fare"], # Shuttle is free (Rs 0)
        "distance_km": round(metro_route["distance_km"] + 1.8, 2),
        "transfers": metro_route["transfers"],
        "shuttle_lead_minutes": lead_min,
        "is_shuttle": True
    }
