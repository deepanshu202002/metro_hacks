import json
import math
import glob
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def load_explicit_trips():
    trip_files = glob.glob(os.path.join(DATA_DIR, 'trips', '*.json'))
    all_trips = []
    for tf in trip_files:
        try:
            with open(tf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                trips = data.get('trips', [])
                all_trips.extend(trips)
        except Exception as e:
            print(f"Error loading {tf}: {e}")
    return all_trips

def generate_metro_timetable():
    with open(os.path.join(DATA_DIR, 'stations.json'), 'r', encoding='utf-8') as f:
        stations = json.load(f)
    with open(os.path.join(DATA_DIR, 'config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)

    station_dict = {s["id"]: s for s in stations}

    # Station sequences by line
    blue_sequence = [
        "thaltej_gam", "thaltej", "doordarshan_kendra", "gurukul_road",
        "gujarat_university", "commerce_six_road", "sp_stadium", "old_high_court",
        "shahpur", "ghee_kanta", "kalupur", "kankaria_east", "apparel_park",
        "amraivadi", "rabari_colony", "vastral", "nirant_cross_road", "vastral_gam"
    ]

    red_sequence = [
        "apmc", "jivraj_park", "rajiv_nagar", "shreyas", "paldi", "gandhigram",
        "old_high_court", "usmanpura", "vijay_nagar", "vadaj", "ranip",
        "sabarmati_railway_station", "aec", "sabarmati", "motera_stadium"
    ]

    yellow_sequence = [
        "motera_stadium", "koteshwar_road", "vishwakarma_college", "tapovan_circle",
        "narmada_canal", "koba_circle", "juna_koba", "koba_gaam", "gnlu",
        "raysan", "randesan", "dholakuva_circle", "infocity", "sector_1",
        "sector_10a", "sachivalaya", "akshardham", "juna_sachivalaya",
        "sector_16", "sector_24", "mahatma_mandir"
    ]

    station_timings = {s["id"]: [] for s in stations}
    all_trips_record = {}

    def get_travel_time(s1_id, s2_id, speed_kmh=35, dwell_sec=25):
        s1 = station_dict[s1_id]
        s2 = station_dict[s2_id]
        dist = haversine(s1["lat"], s1["lng"], s2["lat"], s2["lng"])
        time_sec = (dist / speed_kmh) * 3600
        return int(time_sec + dwell_sec)

    # 1. Process Headway-based Lines (Blue, Red, Yellow)
    def generate_headway_trips(line_key, station_seq):
        line_conf = config["lines"][line_key]
        speed = line_conf.get("speed_kmh", 35)
        dwell = line_conf.get("dwell_time_seconds", 25)
        fwd_times = [0]
        for i in range(1, len(station_seq)):
            fwd_times.append(fwd_times[-1] + get_travel_time(station_seq[i-1], station_seq[i], speed, dwell))
        
        bwd_times = [0]
        rev_seq = list(reversed(station_seq))
        for i in range(1, len(rev_seq)):
            bwd_times.append(bwd_times[-1] + get_travel_time(rev_seq[i-1], rev_seq[i], speed, dwell))

        start_time = datetime.strptime(line_conf["first_train"], "%H:%M")
        end_time = datetime.strptime(line_conf["last_train"], "%H:%M")
        curr = start_time
        trip_counter = 1

        while curr <= end_time:
            curr_str = curr.strftime("%H:%M")
            is_peak = False
            for p in config.get("peak_hours", []):
                if p["start"] <= curr_str <= p["end"]:
                    is_peak = True
                    break
            headway = line_conf["headway_peak_minutes"] if is_peak else line_conf["headway_offpeak_minutes"]

            # Forward trip
            fwd_trip_id = f"{line_key.upper()}_FWD_{trip_counter:03d}"
            fwd_stops = []
            for idx, st_id in enumerate(station_seq):
                arr = curr + timedelta(seconds=fwd_times[idx])
                arr_str = arr.strftime("%H:%M:%S")
                fwd_stops.append({"station_id": st_id, "arrival": arr_str, "departure": arr_str})
                station_timings[st_id].append({
                    "time": arr_str,
                    "line": line_key,
                    "direction": "forward",
                    "destination": station_seq[-1],
                    "trip_id": fwd_trip_id,
                    "service": f"{line_key} Regular"
                })
            all_trips_record[fwd_trip_id] = {
                "trip_id": fwd_trip_id, "line": line_key, "direction": "forward", "stop_times": fwd_stops
            }

            # Backward trip
            bwd_trip_id = f"{line_key.upper()}_BWD_{trip_counter:03d}"
            bwd_stops = []
            for idx, st_id in enumerate(rev_seq):
                arr = curr + timedelta(seconds=bwd_times[idx])
                arr_str = arr.strftime("%H:%M:%S")
                bwd_stops.append({"station_id": st_id, "arrival": arr_str, "departure": arr_str})
                station_timings[st_id].append({
                    "time": arr_str,
                    "line": line_key,
                    "direction": "backward",
                    "destination": rev_seq[-1],
                    "trip_id": bwd_trip_id,
                    "service": f"{line_key} Regular"
                })
            all_trips_record[bwd_trip_id] = {
                "trip_id": bwd_trip_id, "line": line_key, "direction": "backward", "stop_times": bwd_stops
            }

            curr += timedelta(minutes=headway)
            trip_counter += 1

    generate_headway_trips("Blue", blue_sequence)
    generate_headway_trips("Red", red_sequence)
    generate_headway_trips("Yellow", yellow_sequence)

    # 2. Process Explicit Trips (GMRC Notice explicit timetables, Violet shuttles & Direct Trains)
    explicit_trips = load_explicit_trips()
    for trip in explicit_trips:
        trip_id = trip["trip_id"]
        line = trip.get("line", "Violet")
        direction = trip.get("direction", "forward")
        service = trip.get("service", "Special Service")
        stops = trip.get("stop_times", [])
        if not stops:
            continue
        dest_station = stops[-1]["station_id"]

        all_trips_record[trip_id] = trip

        for stop in stops:
            st_id = stop["station_id"]
            if st_id in station_timings:
                station_timings[st_id].append({
                    "time": stop["departure"],
                    "line": line,
                    "direction": direction,
                    "destination": dest_station,
                    "trip_id": trip_id,
                    "service": service
                })

    # Sort all station timings chronologically
    for st_id in station_timings:
        station_timings[st_id].sort(key=lambda x: x["time"])

    output_data = {
        "source": "GMRC public notices (17-Sep-2024, 13-Feb-2025) and calibrated headway generation",
        "source_date": "2025-02-13",
        "verified": False,
        "station_timings": station_timings,
        "trips": all_trips_record
    }

    # Save to timetable.json (stations accessible directly as keys for backward compatibility)
    # Also save structured metadata
    combined_dict = dict(station_timings)
    combined_dict["__metadata__"] = {
        "source": output_data["source"],
        "source_date": output_data["source_date"],
        "verified": False,
        "total_trips": len(all_trips_record)
    }
    combined_dict["__trips__"] = all_trips_record

    with open(os.path.join(DATA_DIR, 'timetable.json'), 'w', encoding='utf-8') as f:
        json.dump(combined_dict, f, indent=2)

    print(f"Generated timetable.json with {len(all_trips_record)} total trips across 54 stations.")

if __name__ == "__main__":
    generate_metro_timetable()
