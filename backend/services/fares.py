import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def get_config():
    with open(os.path.join(DATA_DIR, 'config.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_metro_fare(distance_km, from_id=None, to_id=None):
    config = get_config()
    # Special promo / feeder fare for GNLU <-> GIFT City
    if (from_id == "gnlu" and to_id == "gift_city") or (from_id == "gift_city" and to_id == "gnlu"):
        return config.get("gnlu_gift_city_special_fare", 5)
        
    slabs = config.get("fare_slabs", [
        {"max_km": 2.5, "fare": 5},
        {"max_km": 5.0, "fare": 10},
        {"max_km": 10.0, "fare": 15},
        {"max_km": 15.0, "fare": 20},
        {"max_km": 25.0, "fare": 25},
        {"max_km": 999.0, "fare": 30}
    ])
    
    fare = slabs[-1]["fare"]
    for slab in slabs:
        if distance_km <= slab["max_km"]:
            fare = slab["fare"]
            break
            
    return fare

def calculate_smart_card_fare(base_fare):
    config = get_config()
    discount_pct = config.get("smart_card_discount_percent", 10)
    discounted = base_fare * (1.0 - discount_pct / 100.0)
    return round(discounted)

def calculate_bus_fare(distance_km):
    config = get_config()
    connector = config.get("gnlu_gift_connector_bus", {})
    return connector.get("fare", 10)

def calculate_cab_fare(distance_km):
    config = get_config()
    cab_config = config.get("cab", {"base_fare": 50, "fare_per_km": 14, "distance_multiplier": 1.35})
    route_dist = distance_km * cab_config.get("distance_multiplier", 1.35)
    return round(cab_config["base_fare"] + route_dist * cab_config["fare_per_km"], 2)

def calculate_shuttle_fare():
    config = get_config()
    return config.get("gift_city_shuttle", {}).get("fare", 0)

def get_cab_estimate(lat1, lon1, lat2, lon2):
    dist = haversine(lat1, lon1, lat2, lon2)
    config = get_config()
    cab_config = config.get("cab", {"base_fare": 50, "fare_per_km": 14, "distance_multiplier": 1.35, "speed_kmh": 25})
    route_dist = dist * cab_config.get("distance_multiplier", 1.35)
    time_hr = route_dist / max(1, cab_config.get("speed_kmh", 25))
    return {
        "fare": round(cab_config["base_fare"] + route_dist * cab_config["fare_per_km"], 2),
        "distance_km": round(route_dist, 2),
        "time_min": int(time_hr * 60)
    }

def calculate_fare_split(legs, integrated_fare: float, method: str = "pro-rata"):
    # Group legs by operator
    operator_totals = {}
    total_standalone_fare = 0.0
    total_distance = 0.0
    
    for leg in legs:
        op = leg.get("operator", "Metro")
        fare = leg.get("fare", 0)
        dist = leg.get("dist", 0)
        
        if op not in operator_totals:
            operator_totals[op] = {"legs": 0, "leg_fare": 0.0, "distance": 0.0, "transfers": 0}
            
        operator_totals[op]["legs"] += 1
        operator_totals[op]["leg_fare"] += fare
        operator_totals[op]["distance"] += dist
        total_standalone_fare += fare
        total_distance += dist
        
    for i in range(len(legs) - 1):
        # A transfer happens between consecutive legs. Give credit to both operators or the receiving operator.
        op_from = legs[i].get("operator", "Metro")
        op_to = legs[i+1].get("operator", "Metro")
        if op_from != op_to:
            operator_totals[op_from]["transfers"] += 1
            operator_totals[op_to]["transfers"] += 1

    operators = list(operator_totals.keys())
    split_result = {}
    
    if total_standalone_fare == 0:
        return []
        
    # Apportion integrated_fare
    remaining_fare = integrated_fare
    
    for i, op in enumerate(operators):
        op_data = operator_totals[op]
        
        if i == len(operators) - 1:
            # Last operator gets the remainder to avoid rounding issues
            share = round(remaining_fare, 2)
        else:
            if method == "distance-weighted" and total_distance > 0:
                share = round(integrated_fare * (op_data["distance"] / total_distance), 2)
            elif method == "transfer-incentive":
                # Give a small fixed bonus (e.g., Rs 1) per transfer involved, then pro-rata the rest
                total_transfers = sum(d["transfers"] for d in operator_totals.values())
                transfer_bonus_pool = min(total_transfers * 1.0, integrated_fare * 0.2)
                base_pool = integrated_fare - transfer_bonus_pool
                
                my_bonus = (op_data["transfers"] / total_transfers * transfer_bonus_pool) if total_transfers > 0 else 0
                my_base = (op_data["leg_fare"] / total_standalone_fare * base_pool)
                share = round(my_bonus + my_base, 2)
            else: # pro-rata
                share = round(integrated_fare * (op_data["leg_fare"] / total_standalone_fare), 2)
                
            remaining_fare -= share
            
        split_result[op] = {
            "operator": op,
            "legs": op_data["legs"],
            "leg_fare": op_data["leg_fare"],
            "share": share,
            "net_vs_standalone": round(share - op_data["leg_fare"], 2)
        }
        
    return list(split_result.values())

