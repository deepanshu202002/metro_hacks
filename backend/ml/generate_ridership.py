import json
import os
import math
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BACKEND_DIR, 'data')

def load_stations():
    with open(os.path.join(DATA_DIR, 'stations.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def get_station_archetype(s):
    s_id = s["id"]
    if s_id in ["old_high_court", "gnlu", "motera_stadium"]:
        return "interchange"
    if s_id in ["apmc", "vastral_gam", "thaltej_gam", "mahatma_mandir"]:
        return "terminal"
    if any(i in ["Railway", "HSR"] for i in s.get("integrations", [])):
        return "railway_link"
    if s_id in ["gift_city", "pdeu", "infocity", "sachivalaya", "juna_sachivalaya"]:
        return "office_hub"
    if s_id in ["gujarat_university", "vishwakarma_college", "commerce_six_road"]:
        return "university"
    if s_id == "motera_stadium":
        return "event_venue"
    return "commuter"

def generate_calibrated_ridership():
    stations = load_stations()
    hours = list(range(6, 23)) # 06:00 to 22:00 (17 operating hours)
    day_types = ["weekday", "weekend", "event_day", "rain_day"]

    # Target daily totals (in passengers):
    targets = {
        "weekday": 178000,    # ~1.78 lakh
        "weekend": 115000,    # ~1.15 lakh
        "event_day": 222000,  # ~2.22 lakh
        "rain_day": 132000     # ~1.32 lakh
    }

    # Archetype base weights
    archetype_base_weights = {
        "interchange": 4.5,
        "railway_link": 2.6,
        "terminal": 2.1,
        "office_hub": 2.2,
        "university": 1.7,
        "event_venue": 1.8,
        "commuter": 1.0
    }

    hourly_patterns = {
        "weekday": {
            # Hour: AM peak 8-10, PM peak 17-19
            6: 0.02, 7: 0.04, 8: 0.09, 9: 0.12, 10: 0.09, 11: 0.06, 12: 0.05,
            13: 0.05, 14: 0.05, 15: 0.06, 16: 0.07, 17: 0.11, 18: 0.10, 19: 0.08,
            20: 0.05, 21: 0.04, 22: 0.02
        },
        "weekend": {
            6: 0.01, 7: 0.03, 8: 0.05, 9: 0.06, 10: 0.07, 11: 0.08, 12: 0.08,
            13: 0.08, 14: 0.07, 15: 0.07, 16: 0.08, 17: 0.09, 18: 0.09, 19: 0.07,
            20: 0.05, 21: 0.03, 22: 0.02
        },
        "event_day": {
            # Big surge at Motera Stadium & feeder corridors around 15:00 - 22:00
            6: 0.02, 7: 0.03, 8: 0.06, 9: 0.08, 10: 0.06, 11: 0.05, 12: 0.05,
            13: 0.05, 14: 0.06, 15: 0.08, 16: 0.10, 17: 0.11, 18: 0.12, 19: 0.09,
            20: 0.05, 21: 0.05, 22: 0.04
        },
        "rain_day": {
            6: 0.02, 7: 0.03, 8: 0.08, 9: 0.10, 10: 0.08, 11: 0.06, 12: 0.06,
            13: 0.06, 14: 0.06, 15: 0.06, 16: 0.08, 17: 0.10, 18: 0.09, 19: 0.07,
            20: 0.04, 21: 0.03, 22: 0.02
        }
    }

    raw_boardings = {dt: {s["id"]: {} for s in stations} for dt in day_types}

    for dt in day_types:
        target_total = targets[dt]
        pat = hourly_patterns[dt]

        # Calculate unnormalized station-hour values
        station_hour_matrix = np.zeros((len(stations), len(hours)))

        for i, s in enumerate(stations):
            arch = get_station_archetype(s)
            base_w = archetype_base_weights.get(arch, 1.0)
            
            # Special boost for event day at Motera
            if dt == "event_day":
                if s["id"] == "motera_stadium":
                    base_w *= 4.5
                elif s["id"] in ["old_high_court", "sabarmati", "kalupur"]:
                    base_w *= 1.6

            # Special boost for GIFT City & PDEU on weekdays
            if dt in ["weekday", "rain_day"] and s["id"] in ["gift_city", "pdeu"]:
                base_w *= 1.3

            for j, h in enumerate(hours):
                h_weight = pat[h]
                # Archetype specific hourly modulations
                mod = 1.0
                if arch == "office_hub":
                    # Heavy afternoon exit peak
                    if h in [17, 18, 19]:
                        mod = 1.6
                    elif h in [8, 9, 10]:
                        mod = 1.3
                    elif h in [12, 13, 14]:
                        mod = 0.7
                elif arch == "university":
                    if h in [8, 9, 13, 14, 15]:
                        mod = 1.4
                elif arch == "interchange":
                    if h in [8, 9, 10, 17, 18, 19]:
                        mod = 1.35
                elif s["id"] == "motera_stadium" and dt == "event_day":
                    if h in [16, 17, 18, 21, 22]:
                        mod = 3.5

                station_hour_matrix[i, j] = base_w * h_weight * mod

        # Normalize matrix to strictly match target_total
        matrix_sum = station_hour_matrix.sum()
        calibrated_matrix = (station_hour_matrix / matrix_sum) * target_total

        # Populate dictionary with rounded integers
        for i, s in enumerate(stations):
            for j, h in enumerate(hours):
                raw_boardings[dt][s["id"]][str(h)] = int(round(calibrated_matrix[i, j]))

    # Perform KMeans Clustering on weekday hourly profile
    feature_matrix = []
    station_ids = [s["id"] for s in stations]
    for s_id in station_ids:
        row = [raw_boardings["weekday"][s_id][str(h)] for h in hours]
        # Normalize by station sum to cluster by pattern shape
        s_sum = max(1, sum(row))
        feature_matrix.append([v / s_sum for v in row])

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(feature_matrix)

    # Name clusters based on peak signatures
    cluster_names = {}
    cluster_hourly_profiles = {}
    for c in range(4):
        c_mean = kmeans.cluster_centers_[c]
        cluster_hourly_profiles[c] = {str(hours[idx]): round(float(c_mean[idx]), 4) for idx in range(len(hours))}
        am_ratio = sum(c_mean[2:5]) # 8, 9, 10
        pm_ratio = sum(c_mean[11:14]) # 17, 18, 19
        mid_ratio = sum(c_mean[6:9]) # 12, 13, 14

        if pm_ratio > 0.32:
            cluster_names[c] = "office_hub"
        elif mid_ratio > 0.22:
            cluster_names[c] = "education_university"
        elif am_ratio > 0.32:
            cluster_names[c] = "commuter_residential"
        else:
            cluster_names[c] = "interchange_multimodal"

    station_clusters = {}
    for idx, s_id in enumerate(station_ids):
        c_id = int(cluster_labels[idx])
        station_clusters[s_id] = {
            "cluster_id": c_id,
            "cluster_name": cluster_names.get(c_id, "commuter")
        }

    # Anomaly Detection using IsolationForest
    # Flag hours where station ridership is anomalous
    iso_features = []
    iso_keys = []
    for s_id in station_ids:
        for dt in ["weekday", "event_day"]:
            for h in hours:
                val = raw_boardings[dt][s_id][str(h)]
                iso_features.append([val])
                iso_keys.append((dt, s_id, str(h)))

    iso = IsolationForest(contamination=0.03, random_state=42)
    anom_preds = iso.fit_predict(iso_features)
    anomalies = []
    for idx, pred in enumerate(anom_preds):
        if pred == -1: # Anomaly
            dt, s_id, h = iso_keys[idx]
            val = iso_features[idx][0]
            if val > 600: # filter for high surge anomalies
                anomalies.append({
                    "day_type": dt,
                    "station_id": s_id,
                    "hour": int(h),
                    "boardings": val,
                    "reason": "Sudden crowd surge / stadium match traffic" if s_id == "motera_stadium" else "Interchange rush"
                })

    # Top Origin-Destination corridor flows
    od_corridor_flows = [
        {"origin": "apmc", "destination": "motera_stadium", "daily_pax": 14200, "corridor": "Red Line Spine"},
        {"origin": "thaltej_gam", "destination": "vastral_gam", "daily_pax": 16800, "corridor": "Blue Line East-West"},
        {"origin": "apmc", "destination": "gift_city", "daily_pax": 8900, "corridor": "Ahmedabad <-> GIFT City Direct"},
        {"origin": "old_high_court", "destination": "gift_city", "daily_pax": 7400, "corridor": "Central Interchange to GIFT"},
        {"origin": "kalupur", "destination": "gujarat_university", "daily_pax": 11200, "corridor": "Railway to University"},
        {"origin": "motera_stadium", "destination": "mahatma_mandir", "daily_pax": 9500, "corridor": "Gandhinagar Phase 2 Extension"},
        {"origin": "gnlu", "destination": "gift_city", "daily_pax": 6200, "corridor": "GNLU Feeder / Shuttle Link"},
        {"origin": "old_high_court", "destination": "kalupur", "daily_pax": 12400, "corridor": "Metro to Bullet Train/Railway"}
    ]

    output_dataset = {
        "metadata": {
            "badge": "Synthetic data calibrated to published ridership totals, not official station-level data",
            "source": "Published GMRC ridership totals (1.5-2.0 lakh weekday, 2.2 lakh event day)",
            "source_date": "2025-02-13",
            "verified": False,
            "daily_targets": targets,
            "peak_windows": {"am": "08:00 - 11:00", "pm": "16:00 - 19:30"}
        },
        "boardings": raw_boardings,
        "clusters": {
            "cluster_profiles": {str(k): {"name": cluster_names[k], "hourly_signature": cluster_hourly_profiles[k]} for k in cluster_names},
            "station_clusters": station_clusters
        },
        "anomalies": anomalies[:25],
        "od_flows": od_corridor_flows
    }

    with open(os.path.join(DATA_DIR, 'ridership.json'), 'w', encoding='utf-8') as f:
        json.dump(output_dataset, f, indent=2)

    print(f"Generated ridership.json successfully! Weekday total: {sum(sum(raw_boardings['weekday'][s][str(h)] for h in hours) for s in raw_boardings['weekday']):,} boardings.")

if __name__ == "__main__":
    generate_calibrated_ridership()
