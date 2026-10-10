import json
import os

data_dir = r"e:\metro_hacks\backend\data"
stations_path = os.path.join(data_dir, "stations.json")
config_path = os.path.join(data_dir, "config.json")
timetable_path = os.path.join(data_dir, "timetable.json")

with open(stations_path, 'r', encoding='utf-8') as f:
    stations = json.load(f)

# Update line names
for st in stations:
    if "North-South" in st.get("lines", []) or "Red" in st.get("lines", []):
        st["lines"] = ["Red"]
        
red_stations = ["apmc", "jivraj_park", "rajiv_nagar", "shreyas", "paldi", "gandhigram", "old_high_court", "usmanpura", "vijay_nagar", "vadaj", "ranip", "sabarmati_railway_station", "aec", "sabarmati", "motera_stadium"]
yellow_stations = ["motera_stadium", "koteshwar_road", "vishwakarma_college", "tapovan_circle", "narmada_canal", "koba_circle", "juna_koba", "koba_gaam", "gnlu", "raysan", "randesan", "dholakuva_circle", "infocity", "sector_1", "sector_10a", "sachivalaya", "akshardham", "juna_sachivalaya", "sector_16", "sector_24", "mahatma_mandir"]
violet_stations = ["gnlu", "pdeu", "gift_city"]
blue_stations = ["thaltej_gam", "thaltej", "doordarshan_kendra", "gurukul_road", "gujarat_university", "commerce_six_road", "sp_stadium", "old_high_court", "shahpur", "ghee_kanta", "kalupur", "kankaria_east", "apparel_park", "amraivadi", "rabari_colony", "vastral", "nirant_cross_road", "vastral_gam"]

# Apply lines
for st in stations:
    sid = st["id"]
    st["lines"] = []
    if sid in red_stations:
        st["lines"].append("Red")
    if sid in blue_stations:
        st["lines"].append("Blue")
    if sid in yellow_stations:
        st["lines"].append("Yellow")
    if sid in violet_stations:
        st["lines"].append("Violet")
        
# Interchanges
for st in stations:
    if len(st["lines"]) > 1:
        st["interchange"] = True

# BRTS/AMTS flags
brts = ["vadaj", "ranip", "aec", "sabarmati", "gujarat_university", "rabari_colony"]
amts = ["paldi"]

for st in stations:
    sid = st["id"]
    if sid in brts:
        st["has_brts"] = True
    if sid in amts:
        st["has_amts"] = True
        
with open(stations_path, 'w', encoding='utf-8') as f:
    json.dump(stations, f, indent=2, ensure_ascii=False)

# Update config.json with discount and method
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

config["integrated_fare_discount_percent"] = 10
config["clearing_fee_percent"] = 1.5
config["gift_city_shuttle"] = {"fare": 0, "lead_minutes": 25}
config["gnlu_gift_connector_bus"] = {"fare": 10}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("Data corrections applied.")
