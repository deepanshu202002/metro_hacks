import pytest
from services.routing import find_route
from services.fares import calculate_fare_split

def test_offline_routing_multi_modal():
    # Test a route that includes BRTS
    route = find_route("sabarmati", "brts_hub", "10:00")
    
    assert route is not None
    assert len(route["legs"]) > 0
    
    # Check if there's a BRTS leg
    brts_legs = [l for l in route["legs"] if l.get("operator") == "BRTS"]
    assert len(brts_legs) > 0, "Route must contain a BRTS leg"
    
def test_fare_splitting_logic():
    # Synthetic legs
    legs = [
        {"operator": "Metro", "fare": 20, "dist": 10},
        {"operator": "BRTS", "fare": 10, "dist": 5}
    ]
    
    integrated_fare = 27 # 10% discount on 30
    
    splits = calculate_fare_split(legs, integrated_fare, method="pro-rata")
    
    assert len(splits) == 2
    
    metro_split = next(s for s in splits if s["operator"] == "Metro")
    brts_split = next(s for s in splits if s["operator"] == "BRTS")
    
    assert metro_split["share"] > brts_split["share"], "Metro should get more share since standalone fare is higher"
    assert round(metro_split["share"] + brts_split["share"], 2) == integrated_fare
