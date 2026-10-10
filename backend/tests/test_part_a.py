import unittest
import json
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.routing import find_route, get_feeder_bus_route, get_free_shuttle_route, time_to_min, stations
from services.fares import calculate_metro_fare, calculate_smart_card_fare

class TestPartA(unittest.TestCase):

    def test_a1_54_stations(self):
        """A1. Network must have exactly 54 stations and proper line names."""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'stations.json'), 'r', encoding='utf-8') as f:
            stations_data = json.load(f)
        self.assertEqual(len(stations_data), 54, f"Expected 54 stations, got {len(stations_data)}")
        
        # Verify interchanges
        station_map = {s["id"]: s for s in stations_data}
        self.assertTrue(station_map["old_high_court"]["interchange"])
        self.assertIn("Blue", station_map["old_high_court"]["lines"])
        self.assertIn("Red", station_map["old_high_court"]["lines"])

        self.assertTrue(station_map["motera_stadium"]["interchange"])
        self.assertIn("Red", station_map["motera_stadium"]["lines"])
        self.assertIn("Yellow", station_map["motera_stadium"]["lines"])

        self.assertTrue(station_map["gnlu"]["interchange"])
        self.assertIn("Yellow", station_map["gnlu"]["lines"])
        self.assertIn("Violet", station_map["gnlu"]["lines"])

    def test_a2_timetable_loading(self):
        """A2. Timetable has explicit trips and headway departures with source metadata."""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'timetable.json'), 'r', encoding='utf-8') as f:
            tt = json.load(f)
        self.assertIn("__metadata__", tt)
        self.assertIn("source", tt["__metadata__"])
        self.assertFalse(tt["__metadata__"]["verified"])
        self.assertIn("__trips__", tt)
        self.assertGreater(len(tt["__trips__"]), 30)

    def test_a3_apmc_gift_direct_trips(self):
        """A3 & Part F. APMC <-> GIFT City direct trips return 0 transfers."""
        # 07:25 is right before the 07:28 departure of DIRECT_APMC_GIFT_UP_1
        route = find_route("apmc", "gift_city", "07:25:00")
        self.assertIsNotNone(route)
        self.assertEqual(route["transfers"], 0, f"Expected 0 transfers for direct train, got {route['transfers']}")

        # Reverse direct trip
        route_rev = find_route("gift_city", "apmc", "09:00:00")
        self.assertIsNotNone(route_rev)
        self.assertEqual(route_rev["transfers"], 0)

    def test_a4_a5_mahatma_mandir_to_gift(self):
        """A4/A5 & Part F. Mahatma Mandir -> GIFT City offers change at GNLU and 30-min connector bus."""
        # Option A: Metro (Change at GNLU)
        metro_route = find_route("mahatma_mandir", "gift_city", "08:00:00")
        self.assertIsNotNone(metro_route)
        self.assertEqual(metro_route["transfers"], 1)

        # Option B: Connector Bus (30 min bus from GNLU)
        bus_route = get_feeder_bus_route("mahatma_mandir", "gift_city", "08:00:00")
        self.assertIsNotNone(bus_route)
        self.assertTrue(bus_route.get("is_connector_bus"))
        self.assertEqual(len(bus_route["legs"]), 2) # Yellow metro leg + connector bus leg

    def test_a5_shuttle_lead_time(self):
        """A5 & Part F. Free shuttle leaves exactly 25 min before matched metro."""
        shuttle_route = get_free_shuttle_route("gift_city", "apmc", "08:00:00")
        self.assertIsNotNone(shuttle_route)
        shuttle_dep = time_to_min(shuttle_route["legs"][0]["depart"])
        metro_dep = time_to_min(shuttle_route["legs"][1]["depart"])
        self.assertEqual(metro_dep - shuttle_dep, 25.0)
        self.assertEqual(shuttle_route["fare"], shuttle_route["legs"][1].get("fare", shuttle_route["fare"]))

    def test_a6_fares(self):
        """A6. Fares follow slab table, smart card discount, and GNLU-GIFT special fare."""
        # GNLU to GIFT City special fare = 5
        fare_special = calculate_metro_fare(5.4, "gnlu", "gift_city")
        self.assertEqual(fare_special, 5)

        # Base slab (< 2.5km) = 5
        fare_short = calculate_metro_fare(2.0)
        self.assertEqual(fare_short, 5)

        # Smart card discount
        smart_card = calculate_smart_card_fare(20)
        self.assertEqual(smart_card, 18) # 10% discount on 20 = 18

if __name__ == "__main__":
    unittest.main()
