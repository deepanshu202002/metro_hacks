import json
import os
import math
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(__file__)

# 54 Official Stations (68.28 km)
# Blue Line: 18 stations (Thaltej Gam - Vastral Gam)
# Red Line: 15 stations (APMC - Motera Stadium, includes Old High Court)
# Yellow Line: 21 stations (Motera Stadium - Mahatma Mandir, includes GNLU)
# Violet Line: 3 stations (GNLU - PDEU - GIFT City)
# Total unique stations: 18 + 14 + 20 + 2 = 54 stations.

stations_raw = [
    # --- BLUE LINE (West to East) ---
    {"id": "thaltej_gam", "name_en": "Thaltej Gam", "name_gu": "થલતેજ ગામ", "name_hi": "थलतेज गाम", "lat": 23.0550, "lng": 72.5000, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "thaltej", "name_en": "Thaltej", "name_gu": "થલતેજ", "name_hi": "थलतेज", "lat": 23.0520, "lng": 72.5150, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "doordarshan_kendra", "name_en": "Doordarshan Kendra", "name_gu": "દૂરદર્શન કેન્દ્ર", "name_hi": "दूरदर्शन केंद्र", "lat": 23.0480, "lng": 72.5300, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "gurukul_road", "name_en": "Gurukul Road", "name_gu": "ગુરુકુળ રોડ", "name_hi": "गुरुकुल रोड", "lat": 23.0450, "lng": 72.5450, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "gujarat_university", "name_en": "Gujarat University", "name_gu": "ગુજરાત યુનિવર્સિટી", "name_hi": "गुजरात विश्वविद्यालय", "lat": 23.0350, "lng": 72.5550, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": ["BRTS"], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "commerce_six_road", "name_en": "Commerce Six Road", "name_gu": "કોમર્સ છ રસ્તા", "name_hi": "कॉमर्स छह रास्ता", "lat": 23.0380, "lng": 72.5650, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "sp_stadium", "name_en": "SP Stadium", "name_gu": "એસપી સ્ટેડિયમ", "name_hi": "एसपी स्टेडियम", "lat": 23.0400, "lng": 72.5700, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": ["Railway"], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "old_high_court", "name_en": "Old High Court", "name_gu": "જૂની હાઈકોર્ટ", "name_hi": "पुरानी हाई कोर्ट", "lat": 23.0425, "lng": 72.5710, "lines": ["Blue", "Red"], "interchange": True, "is_underground": False, "integrations": [], "line_name": "Interchange (Red / Blue)"},
    {"id": "shahpur", "name_en": "Shahpur", "name_gu": "શાહપુર", "name_hi": "शाहपुर", "lat": 23.0330, "lng": 72.5800, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "ghee_kanta", "name_en": "Ghee Kanta", "name_gu": "ઘી કાંટા", "name_hi": "घी कांटा", "lat": 23.0300, "lng": 72.5850, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "kalupur", "name_en": "Kalupur Railway Station", "name_gu": "કાલુપુર રેલ્વે સ્ટેશન", "name_hi": "कालूपुर रेलवे स्टेशन", "lat": 23.0250, "lng": 72.6000, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": ["Railway", "HSR"], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "kankaria_east", "name_en": "Kankaria East", "name_gu": "કાંકરિયા પૂર્વ", "name_hi": "कांकरिया पूर्व", "lat": 23.0150, "lng": 72.6100, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": ["Railway"], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "apparel_park", "name_en": "Apparel Park", "name_gu": "એપેરલ પાર્ક", "name_hi": "अपैरल पार्क", "lat": 23.0100, "lng": 72.6200, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "amraivadi", "name_en": "Amraivadi", "name_gu": "અમરાઈવાડી", "name_hi": "અમરાઈવાડી", "lat": 23.0080, "lng": 72.6300, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "rabari_colony", "name_en": "Rabari Colony", "name_gu": "રબારી કોલોની", "name_hi": "રબારી કોલોની", "lat": 23.0050, "lng": 72.6400, "lines": ["Blue"], "interchange": False, "is_underground": True, "integrations": ["BRTS"], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "vastral", "name_en": "Vastral", "name_gu": "વસ્ત્રાલ", "name_hi": "वस्त्राल", "lat": 23.0000, "lng": 72.6500, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "nirant_cross_road", "name_en": "Nirant Cross Road", "name_gu": "નિરાંત ક્રોસ રોડ", "name_hi": "निरांत क्रॉस रोड", "lat": 22.9980, "lng": 72.6600, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},
    {"id": "vastral_gam", "name_en": "Vastral Gam", "name_gu": "વસ્ત્રાલ ગામ", "name_hi": "वस्त्राल गाम", "lat": 22.9950, "lng": 72.6700, "lines": ["Blue"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Blue: Thaltej Gam-Vastral Gam"},

    # --- RED LINE (South to North) ---
    {"id": "apmc", "name_en": "APMC", "name_gu": "એપીએમસી", "name_hi": "एपीएमसी", "lat": 23.0031, "lng": 72.5404, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "jivraj_park", "name_en": "Jivraj Park", "name_gu": "જીવરાજ પાર્ક", "name_hi": "जीवराज पार्क", "lat": 23.0089, "lng": 72.5410, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "rajiv_nagar", "name_en": "Rajiv Nagar", "name_gu": "રાજીવ નગર", "name_hi": "राजीव नगर", "lat": 23.0145, "lng": 72.5415, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "shreyas", "name_en": "Shreyas", "name_gu": "શ્રેયસ", "name_hi": "श्रेयस", "lat": 23.0205, "lng": 72.5430, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "paldi", "name_en": "Paldi", "name_gu": "પાલડી", "name_hi": "पालडी", "lat": 23.0245, "lng": 72.5590, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": ["AMTS"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "gandhigram", "name_en": "Gandhigram", "name_gu": "ગાંધીગ્રામ", "name_hi": "गांधीग्राम", "lat": 23.0315, "lng": 72.5695, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": ["Railway"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "usmanpura", "name_en": "Usmanpura", "name_gu": "ઉસ્માનપુરા", "name_hi": "उस्मानपुरा", "lat": 23.0475, "lng": 72.5710, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "vijay_nagar", "name_en": "Vijay Nagar", "name_gu": "વિજય નગર", "name_hi": "विजय नगर", "lat": 23.0535, "lng": 72.5720, "lines": ["Red"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "vadaj", "name_en": "Vadaj", "name_gu": "વાડજ", "name_hi": "वाडज", "lat": 23.0615, "lng": 72.5720, "lines": ["Red"], "interchange": False, "is_underground": True, "integrations": ["BRTS"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "ranip", "name_en": "Ranip", "name_gu": "રાણીપ", "name_hi": "રાણીપ", "lat": 23.0695, "lng": 72.5740, "lines": ["Red"], "interchange": False, "is_underground": True, "integrations": ["BRTS"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "sabarmati_railway_station", "name_en": "Sabarmati Railway Station", "name_gu": "સાબરમતી રેલ્વે સ્ટેશન", "name_hi": "સાબરમતી રેલવે સ્ટેશન", "lat": 23.0760, "lng": 72.5840, "lines": ["Red"], "interchange": False, "is_underground": True, "integrations": ["Railway"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "aec", "name_en": "AEC", "name_gu": "એઇસી", "name_hi": "एईसी", "lat": 23.0820, "lng": 72.5855, "lines": ["Red"], "interchange": False, "is_underground": True, "integrations": ["BRTS"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "sabarmati", "name_en": "Sabarmati (HSR Hub)", "name_gu": "સાબરમતી", "name_hi": "સાબરમતી", "lat": 23.0900, "lng": 72.5875, "lines": ["Red"], "interchange": False, "is_underground": True, "integrations": ["BRTS", "Railway", "HSR"], "line_name": "Red: APMC-Motera Stadium"},
    {"id": "motera_stadium", "name_en": "Motera Stadium", "name_gu": "મોટેરા સ્ટેડિયમ", "name_hi": "મોટેરા સ્ટેડિયમ", "lat": 23.1000, "lng": 72.5975, "lines": ["Red", "Yellow"], "interchange": True, "is_underground": False, "integrations": ["Event Venue"], "line_name": "Interchange (Red / Yellow)"},

    # --- YELLOW LINE (Gandhinagar Corridor: Motera Stadium - Mahatma Mandir) ---
    {"id": "koteshwar_road", "name_en": "Koteshwar Road", "name_gu": "કોટેશ્વર રોડ", "name_hi": "કોટેશ્વર રોડ", "lat": 23.1080, "lng": 72.6025, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "vishwakarma_college", "name_en": "Vishwakarma College", "name_gu": "વિશ્વકર્મા કોલેજ", "name_hi": "વિશ્વકર્મા કોલેજ", "lat": 23.1180, "lng": 72.6075, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "tapovan_circle", "name_en": "Tapovan Circle", "name_gu": "તપોવન સર્કલ", "name_hi": "તપોવન સર્કલ", "lat": 23.1250, "lng": 72.6105, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "narmada_canal", "name_en": "Narmada Canal", "name_gu": "નર્મદા કેનાલ", "name_hi": "નર્મદા નહેર", "lat": 23.1350, "lng": 72.6150, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "koba_circle", "name_en": "Koba Circle", "name_gu": "કોબા સર્કલ", "name_hi": "કોબા સર્કલ", "lat": 23.1480, "lng": 72.6205, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "juna_koba", "name_en": "Juna Koba", "name_gu": "જૂના કોબા", "name_hi": "જૂના કોબા", "lat": 23.1550, "lng": 72.6255, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "koba_gaam", "name_en": "Koba Gaam", "name_gu": "કોબા ગામ", "name_hi": "કોબા ગામ", "lat": 23.1600, "lng": 72.6300, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "gnlu", "name_en": "GNLU", "name_gu": "જીએનએલયુ", "name_hi": "જીએનએલયુ", "lat": 23.1680, "lng": 72.6350, "lines": ["Yellow", "Violet"], "interchange": True, "is_underground": False, "integrations": ["Feeder Bus"], "line_name": "Interchange (Yellow / Violet)"},
    {"id": "raysan", "name_en": "Raysan", "name_gu": "રાયસણ", "name_hi": "રાયસણ", "lat": 23.1800, "lng": 72.6400, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "randesan", "name_en": "Randesan", "name_gu": "રંદેસણ", "name_hi": "રંદેસણ", "lat": 23.1900, "lng": 72.6430, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "dholakuva_circle", "name_en": "Dholakuva Circle", "name_gu": "ધોળાકુવા સર્કલ", "name_hi": "ધોલાકુઆં સર્કલ", "lat": 23.2000, "lng": 72.6450, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "infocity", "name_en": "Infocity", "name_gu": "ઇન્ફોસિટી", "name_hi": "ઇન્ફોસિટી", "lat": 23.2100, "lng": 72.6500, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "sector_1", "name_en": "Sector 1", "name_gu": "સેક્ટર ૧", "name_hi": "સેક્ટર 1", "lat": 23.2150, "lng": 72.6550, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "sector_10a", "name_en": "Sector 10A", "name_gu": "સેક્ટર ૧૦એ", "name_hi": "સેક્ટર 10A", "lat": 23.2200, "lng": 72.6600, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "sachivalaya", "name_en": "Sachivalaya", "name_gu": "સચિવાલય", "name_hi": "સચિવાલય", "lat": 23.2250, "lng": 72.6650, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "akshardham", "name_en": "Akshardham", "name_gu": "અક્ષરધામ", "name_hi": "અક્ષરધામ", "lat": 23.2350, "lng": 72.6700, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "juna_sachivalaya", "name_en": "Juna Sachivalaya", "name_gu": "જૂના સચિવાલય", "name_hi": "પુરાના સચિવાલય", "lat": 23.2450, "lng": 72.6650, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "sector_16", "name_en": "Sector 16", "name_gu": "સેક્ટર ૧૬", "name_hi": "સેક્ટર 16", "lat": 23.2500, "lng": 72.6600, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "sector_24", "name_en": "Sector 24", "name_gu": "સેક્ટર ૨૪", "name_hi": "સેક્ટર 24", "lat": 23.2550, "lng": 72.6550, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},
    {"id": "mahatma_mandir", "name_en": "Mahatma Mandir", "name_gu": "મહાત્મા મંદિર", "name_hi": "મહાત્મા મંદિર", "lat": 23.2600, "lng": 72.6500, "lines": ["Yellow"], "interchange": False, "is_underground": False, "integrations": ["Railway"], "line_name": "Yellow: Motera Stadium-Mahatma Mandir"},

    # --- VIOLET LINE (GIFT City Branch) ---
    {"id": "pdeu", "name_en": "PDEU", "name_gu": "પીડીઇયુ", "name_hi": "પીડીઇયુ", "lat": 23.1650, "lng": 72.6500, "lines": ["Violet"], "interchange": False, "is_underground": False, "integrations": [], "line_name": "Violet: GNLU-GIFT City"},
    {"id": "gift_city", "name_en": "GIFT City", "name_gu": "ગિફ્ટ સિટી", "name_hi": "ગિફ્ટ સિટી", "lat": 23.1600, "lng": 72.6850, "lines": ["Violet"], "interchange": False, "is_underground": False, "integrations": ["GIFT Shuttle", "Feeder Bus"], "line_name": "Violet: GNLU-GIFT City"}
]

# Enrich stations with metadata
for s in stations_raw:
    s["source"] = "GMRC Route Info & Phase 2 Official Alignment"
    s["source_date"] = "2025-02-13"
    s["verified"] = True

with open(os.path.join(DATA_DIR, "stations.json"), "w", encoding="utf-8") as f:
    json.dump(stations_raw, f, ensure_ascii=False, indent=2)

print(f"Generated stations.json with {len(stations_raw)} stations (Target: 54).")

# Create Trips dataset (Part A3 explicit timetable)
trips_data = {
    "source": "GMRC public notice 17-Sep-2024 and GMRC press note 13-Feb-2025",
    "source_date": "2025-02-13",
    "verified": False,
    "description": "Explicit timetables for GNLU<->GIFT City shuttles and Direct APMC/Motera<->GIFT City trains",
    "trips": []
}

# 1. GNLU -> PDEU -> GIFT City Shuttles
gnlu_gift_times = [
    ("08:25:00", "08:29:00", "08:35:00"),
    ("09:45:00", "09:49:00", "09:55:00"),
    ("11:05:00", "11:09:00", "11:15:00"),
    ("12:35:00", "12:39:00", "12:45:00"),
    ("13:55:00", "13:59:00", "14:05:00"),
    ("15:45:00", "15:49:00", "15:55:00"),
    ("17:05:00", "17:09:00", "17:15:00"),
    ("17:53:00", "17:57:00", "18:03:00"),
    ("18:25:00", "18:29:00", "18:35:00")
]
for idx, (t_gnlu, t_pdeu, t_gift) in enumerate(gnlu_gift_times):
    trips_data["trips"].append({
        "trip_id": f"VIOLET_SHUTTLE_UP_{idx+1}",
        "line": "Violet",
        "service": "GNLU-GIFT Shuttle",
        "direction": "forward",
        "stop_times": [
            {"station_id": "gnlu", "arrival": t_gnlu, "departure": t_gnlu},
            {"station_id": "pdeu", "arrival": t_pdeu, "departure": t_pdeu},
            {"station_id": "gift_city", "arrival": t_gift, "departure": t_gift}
        ]
    })

# 2. GIFT City -> PDEU -> GNLU Shuttles
gift_gnlu_times = [
    ("07:18:00", "07:23:00", "07:28:00"),
    ("08:38:00", "08:43:00", "08:48:00"),
    ("10:38:00", "10:43:00", "10:48:00"),
    ("11:28:00", "11:33:00", "11:38:00"),
    ("12:48:00", "12:53:00", "12:58:00"),
    ("14:38:00", "14:43:00", "14:58:00"),  # printed 14:58; TODO verify
    ("15:58:00", "16:03:00", "16:08:00"),
    ("17:18:00", "17:23:00", "17:28:00"),
    ("18:05:00", "18:10:00", "18:15:00"),
    ("18:38:00", "18:43:00", "18:48:00")
]
for idx, (t_gift, t_pdeu, t_gnlu) in enumerate(gift_gnlu_times):
    trips_data["trips"].append({
        "trip_id": f"VIOLET_SHUTTLE_DN_{idx+1}",
        "line": "Violet",
        "service": "GIFT-GNLU Shuttle",
        "direction": "backward",
        "stop_times": [
            {"station_id": "gift_city", "arrival": t_gift, "departure": t_gift},
            {"station_id": "pdeu", "arrival": t_pdeu, "departure": t_pdeu},
            {"station_id": "gnlu", "arrival": t_gnlu, "departure": t_gnlu}
        ]
    })

# Red line stations list APMC -> Motera
red_order = [s["id"] for s in stations_raw if "Red" in s["lines"] and s["id"] != "old_high_court"]
# insert old_high_court in correct position
red_full = [
    "apmc", "jivraj_park", "rajiv_nagar", "shreyas", "paldi", "gandhigram",
    "old_high_court", "usmanpura", "vijay_nagar", "vadaj", "ranip",
    "sabarmati_railway_station", "aec", "sabarmati", "motera_stadium"
]
# Yellow corridor Motera -> GNLU
yellow_to_gnlu = [
    "motera_stadium", "koteshwar_road", "vishwakarma_college", "tapovan_circle",
    "narmada_canal", "koba_circle", "juna_koba", "koba_gaam", "gnlu"
]

# 3. DIRECT APMC -> Motera -> GNLU -> GIFT City
# Given Motera, GNLU, GIFT City:
direct_up = [
    ("08:00:00", "08:27:00", "08:43:00"),
    ("09:24:00", "09:51:00", "10:07:00"),
    ("10:25:00", "10:52:00", "11:08:00"),
    ("15:34:00", "16:01:00", "16:17:00"),
    ("16:46:00", "17:13:00", "17:29:00"),
    ("17:52:00", "18:19:00", "18:35:00")
]

def parse_t(s):
    return datetime.strptime(s, "%H:%M:%S")

def fmt_t(dt):
    return dt.strftime("%H:%M:%S")

for idx, (t_motera_str, t_gnlu_str, t_gift_str) in enumerate(direct_up):
    t_motera = parse_t(t_motera_str)
    t_apmc = t_motera - timedelta(minutes=32)
    t_gnlu = parse_t(t_gnlu_str)
    t_gift = parse_t(t_gift_str)
    t_pdeu = t_gnlu + timedelta(minutes=5)
    
    # interpolate intermediate stations
    stop_times = []
    # APMC to Motera
    for s_idx, st_id in enumerate(red_full):
        frac = s_idx / (len(red_full) - 1)
        st_t = t_apmc + (t_motera - t_apmc) * frac
        stop_times.append({"station_id": st_id, "arrival": fmt_t(st_t), "departure": fmt_t(st_t)})
    # Motera to GNLU (skipping motera since already added)
    for s_idx, st_id in enumerate(yellow_to_gnlu[1:]):
        frac = (s_idx + 1) / (len(yellow_to_gnlu) - 1)
        st_t = t_motera + (t_gnlu - t_motera) * frac
        stop_times.append({"station_id": st_id, "arrival": fmt_t(st_t), "departure": fmt_t(st_t)})
    # GNLU to GIFT
    stop_times.append({"station_id": "pdeu", "arrival": fmt_t(t_pdeu), "departure": fmt_t(t_pdeu)})
    stop_times.append({"station_id": "gift_city", "arrival": fmt_t(t_gift), "departure": fmt_t(t_gift)})
    
    trips_data["trips"].append({
        "trip_id": f"DIRECT_APMC_GIFT_UP_{idx+1}",
        "line": "Direct",
        "service": "APMC-GIFT City Direct Train",
        "direction": "forward",
        "stop_times": stop_times
    })

# 4. DIRECT GIFT City -> GNLU -> Motera -> APMC
direct_dn = [
    ("09:03:00", "09:20:00", "09:46:00"),
    ("10:27:00", "10:44:00", "11:10:00"),
    ("11:28:00", "11:45:00", "12:11:00"),
    ("16:37:00", "16:54:00", "17:20:00"),
    ("17:49:00", "18:06:00", "18:32:00"),
    ("18:55:00", "19:12:00", "19:38:00")
]

for idx, (t_gift_str, t_gnlu_str, t_motera_str) in enumerate(direct_dn):
    t_gift = parse_t(t_gift_str)
    t_gnlu = parse_t(t_gnlu_str)
    t_motera = parse_t(t_motera_str)
    t_apmc = t_motera + timedelta(minutes=32)
    t_pdeu = t_gift + timedelta(minutes=5)
    
    stop_times = []
    stop_times.append({"station_id": "gift_city", "arrival": fmt_t(t_gift), "departure": fmt_t(t_gift)})
    stop_times.append({"station_id": "pdeu", "arrival": fmt_t(t_pdeu), "departure": fmt_t(t_pdeu)})
    stop_times.append({"station_id": "gnlu", "arrival": fmt_t(t_gnlu), "departure": fmt_t(t_gnlu)})
    
    # GNLU to Motera
    rev_yellow = list(reversed(yellow_to_gnlu))
    for s_idx, st_id in enumerate(rev_yellow[1:]):
        frac = (s_idx + 1) / (len(rev_yellow) - 1)
        st_t = t_gnlu + (t_motera - t_gnlu) * frac
        stop_times.append({"station_id": st_id, "arrival": fmt_t(st_t), "departure": fmt_t(st_t)})
    
    # Motera to APMC
    rev_red = list(reversed(red_full))
    for s_idx, st_id in enumerate(rev_red[1:]):
        frac = (s_idx + 1) / (len(rev_red) - 1)
        st_t = t_motera + (t_apmc - t_motera) * frac
        stop_times.append({"station_id": st_id, "arrival": fmt_t(st_t), "departure": fmt_t(st_t)})
        
    trips_data["trips"].append({
        "trip_id": f"DIRECT_GIFT_APMC_DN_{idx+1}",
        "line": "Direct",
        "service": "GIFT City-APMC Direct Train",
        "direction": "backward",
        "stop_times": stop_times
    })

os.makedirs(os.path.join(DATA_DIR, "trips"), exist_ok=True)
with open(os.path.join(DATA_DIR, "trips", "gmrc_trips.json"), "w", encoding="utf-8") as f:
    json.dump(trips_data, f, ensure_ascii=False, indent=2)

print(f"Generated trips/gmrc_trips.json with {len(trips_data['trips'])} explicit trips.")

# Write config.json with all specifications from Part A
config_data = {
    "demo_mode": True,
    "source": "GMRC public notices (17-Sep-2024, 13-Feb-2025) and calibrated operational estimates",
    "source_date": "2025-02-13",
    "verified": False,
    "lines": {
        "Blue": {
            "name": "Blue: Thaltej Gam-Vastral Gam",
            "color": "#1D6FD8",
            "first_train": "06:20",
            "last_train": "22:00",
            "headway_peak_minutes": 10,
            "headway_offpeak_minutes": 12,
            "speed_kmh": 35,
            "dwell_time_seconds": 25,
            "verified": False
        },
        "Red": {
            "name": "Red: APMC-Motera Stadium",
            "color": "#D7263D",
            "first_train": "06:20",
            "last_train": "22:00",
            "headway_peak_minutes": 10,
            "headway_offpeak_minutes": 12,
            "speed_kmh": 35,
            "dwell_time_seconds": 25,
            "verified": False
        },
        "Yellow": {
            "name": "Yellow: Motera Stadium-Mahatma Mandir",
            "color": "#F2B705",
            "first_train": "07:30",
            "last_train": "19:30",
            "headway_peak_minutes": 35,
            "headway_offpeak_minutes": 55,
            "speed_kmh": 34,
            "dwell_time_seconds": 25,
            "verified": False
        },
        "Violet": {
            "name": "Violet: GNLU-GIFT City",
            "color": "#7C3AED",
            "mode": "explicit_trips",
            "speed_kmh": 35,
            "dwell_time_seconds": 25,
            "verified": True
        }
    },
    "peak_hours": [
        {"start": "08:00", "end": "11:00"},
        {"start": "16:00", "end": "19:30"}
    ],
    "fare_slabs": [
        {"max_km": 2.5, "fare": 5},
        {"max_km": 5.0, "fare": 10},
        {"max_km": 10.0, "fare": 15},
        {"max_km": 15.0, "fare": 20},
        {"max_km": 25.0, "fare": 25},
        {"max_km": 999.0, "fare": 30}
    ],
    "gnlu_gift_city_special_fare": 5,
    "smart_card_discount_percent": 10,
    "smart_card_discount_flat": 2,
    "gnlu_gift_connector_bus": {
        "headway_minutes": 30,
        "first_bus": "07:00",
        "last_bus": "20:00",
        "fare": 10,
        "speed_kmh": 22,
        "travel_time_min": 14,
        "source": "SYNTHETIC feeder estimate; verify with GSRTC/GMRC",
        "verified": False
    },
    "gift_city_shuttle": {
        "shuttle_lead_minutes": 25,
        "fare": 0,
        "shuttle_reverse_enabled": False,
        "buffer_km": 2.0,
        "source": "GIFT City Transit Guidelines; verify with GIFT SEZ",
        "verified": False
    },
    "cab": {
        "base_fare": 50,
        "fare_per_km": 14,
        "speed_kmh": 25,
        "distance_multiplier": 1.35
    },
    "walk": {
        "speed_kmh": 4.5,
        "max_walking_leg_km": 1.5,
        "transfer_buffer_minutes": 3
    }
}

with open(os.path.join(DATA_DIR, "config.json"), "w", encoding="utf-8") as f:
    json.dump(config_data, f, ensure_ascii=False, indent=2)

print("Saved updated config.json with Part A specifications.")
