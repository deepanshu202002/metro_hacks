import json
import random
import os
from services.routing import find_route
from services.fares import calculate_fare_split, get_config

def generate_settlement_report():
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    with open(os.path.join(data_dir, 'stations.json'), 'r', encoding='utf-8') as f:
        stations = json.load(f)
        
    config = get_config()
    clearing_fee_percent = config.get("clearing_fee_percent", 1.5)
    
    station_ids = [s["id"] for s in stations]
    
    trips_generated = 0
    total_integrated_revenue = 0.0
    clearing_fee_collected = 0.0
    operator_pools = {}
    
    # Generate 200 random trips
    while trips_generated < 200:
        s1 = random.choice(station_ids)
        s2 = random.choice(station_ids)
        if s1 == s2:
            continue
            
        time_str = f"{random.randint(7, 21):02d}:{random.randint(0, 59):02d}"
        route = find_route(s1, s2, time_str)
        if not route or len(route["legs"]) == 0:
            continue
            
        trips_generated += 1
        integrated_fare = route["fare"]
        total_integrated_revenue += integrated_fare
        
        # Deduct clearing fee
        fee = integrated_fare * (clearing_fee_percent / 100.0)
        clearing_fee_collected += fee
        net_fare = integrated_fare - fee
        
        # Split remaining net fare
        splits = calculate_fare_split(route["legs"], net_fare, method="pro-rata")
        for split in splits:
            op = split["operator"]
            if op not in operator_pools:
                operator_pools[op] = {"revenue_share": 0.0, "legs_served": 0}
            operator_pools[op]["revenue_share"] += split["share"]
            operator_pools[op]["legs_served"] += split["legs"]

    report = {
        "trips_processed": trips_generated,
        "total_integrated_revenue": round(total_integrated_revenue, 2),
        "clearing_fee_percent": clearing_fee_percent,
        "clearing_entity_revenue": round(clearing_fee_collected, 2),
        "operator_pools": {op: {"revenue_share": round(d["revenue_share"], 2), "legs_served": d["legs_served"]} for op, d in operator_pools.items()}
    }
    
    out_path = os.path.join(data_dir, 'settlement_report.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    print(f"Settlement report generated at {out_path}")

if __name__ == "__main__":
    generate_settlement_report()
