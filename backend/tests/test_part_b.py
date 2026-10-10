import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.analytics import (
    get_overview,
    get_station_congestion,
    get_top_congested_ranking,
    get_crowd_forecast,
    simulate_event,
    get_narrated_insights
)
from services.validator import validate_explanation

class TestPartB(unittest.TestCase):

    def test_overview_calibrated_totals(self):
        """Calibrated ridership must be within 1.5 - 2.0 lakh for weekday."""
        overview = get_overview(day_type="weekday", hour=9)
        daily = overview["daily_ridership"]
        self.assertGreaterEqual(daily, 150000, f"Weekday ridership {daily} below 1.5 lakh")
        self.assertLessEqual(daily, 200000, f"Weekday ridership {daily} above 2.0 lakh")
        self.assertEqual(overview["busiest_station"], "Old High Court")

    def test_ranking_sorted(self):
        """Top-10 ranking must be sorted in descending order of boardings."""
        ranking = get_top_congested_ranking(hour=9, day_type="weekday", top_k=10)
        self.assertEqual(len(ranking), 10)
        for i in range(len(ranking) - 1):
            self.assertGreaterEqual(
                ranking[i]["boardings"],
                ranking[i+1]["boardings"],
                f"Rank {i+1} has fewer boardings than rank {i+2}"
            )

    def test_crowd_forecast_within_bounds(self):
        """Forecast predictions and confidence intervals must be valid positive bounds."""
        forecast_data = get_crowd_forecast("old_high_court", current_hour=9)
        self.assertEqual(forecast_data["station_id"], "old_high_court")
        self.assertGreaterEqual(len(forecast_data["forecast"]), 1)
        for f in forecast_data["forecast"]:
            lower, upper = f["confidence_interval"]
            self.assertGreater(lower, 0)
            self.assertGreater(upper, lower)
            self.assertGreaterEqual(f["forecast_pax"], lower)
            self.assertLessEqual(f["forecast_pax"], upper)

    def test_event_simulator_reduces_load(self):
        """Simulator must reduce platform load index when extra trains are added."""
        sim_no_extra = simulate_event(attendance=85000, extra_trains=0, headway_minutes=12)
        sim_extra = simulate_event(attendance=85000, extra_trains=6, headway_minutes=5)
        
        self.assertGreater(
            sim_no_extra["after_platform_load_index"],
            sim_extra["after_platform_load_index"],
            "Deploying extra trains did not reduce platform load index!"
        )
        self.assertGreater(sim_extra["load_reduction_pct"], 0)

    def test_insight_narrator_grounding(self):
        """Insight narrator is accepted when grounded, rejected when stating numbers not in data."""
        # 1. Real grounded insights
        res = get_narrated_insights(lang="en")
        self.assertTrue(res["grounded"], "Grounded insights failed validation")

        # 2. Hallucinated / ungrounded statement with fake numbers
        fake_data_context = res["data_context"]
        hallucinated_text = "There were 999999 passengers stranded at the station today."
        is_grounded = validate_explanation(hallucinated_text, fake_data_context)
        self.assertFalse(is_grounded, "Validator should have rejected number 999999 not present in data")

if __name__ == "__main__":
    unittest.main()
