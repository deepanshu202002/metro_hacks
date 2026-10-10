import json

stations = [
    # Red line (South to North)
    {"id": "apmc", "name_en": "APMC", "name_gu": "એપીએમસી", "name_hi": "एपीएमसी", "lat": 23.0031, "lng": 72.5404, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "jivraj_park", "name_en": "Jivraj Park", "name_gu": "જીવરાજ પાર્ક", "name_hi": "जीवराज पार्क", "lat": 23.0089, "lng": 72.5410, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "rajiv_nagar", "name_en": "Rajiv Nagar", "name_gu": "રાજીવ નગર", "name_hi": "राजीव नगर", "lat": 23.0145, "lng": 72.5415, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "shreyas", "name_en": "Shreyas", "name_gu": "શ્રેયસ", "name_hi": "श्रेयस", "lat": 23.0205, "lng": 72.5430, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "paldi", "name_en": "Paldi", "name_gu": "પાલડી", "name_hi": "पालडी", "lat": 23.0245, "lng": 72.5590, "line": "Red", "is_underground": False, "interchange": False, "integrations": ["AMTS"]},
    {"id": "gandhigram", "name_en": "Gandhigram", "name_gu": "ગાંધીગ્રામ", "name_hi": "गांधीग्राम", "lat": 23.0315, "lng": 72.5695, "line": "Red", "is_underground": False, "interchange": False, "integrations": ["Railway"]},
    {"id": "old_high_court", "name_en": "Old High Court", "name_gu": "જૂની હાઈકોર્ટ", "name_hi": "पुरानी हाई कोर्ट", "lat": 23.0425, "lng": 72.5710, "line": "Red", "is_underground": False, "interchange": True, "integrations": []}, # Interchange
    {"id": "usmanpura", "name_en": "Usmanpura", "name_gu": "ઉસ્માનપુરા", "name_hi": "उस्मानपुरा", "lat": 23.0475, "lng": 72.5710, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "vijay_nagar", "name_en": "Vijay Nagar", "name_gu": "વિજય નગર", "name_hi": "विजय नगर", "lat": 23.0535, "lng": 72.5720, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "vadaj", "name_en": "Vadaj", "name_gu": "વાડજ", "name_hi": "वाडज", "lat": 23.0615, "lng": 72.5720, "line": "Red", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "ranip", "name_en": "Ranip", "name_gu": "રાણીપ", "name_hi": "राणीप", "lat": 23.0695, "lng": 72.5740, "line": "Red", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "sabarmati_railway_station", "name_en": "Sabarmati Railway Station", "name_gu": "સાબરમતી રેલ્વે સ્ટેશન", "name_hi": "साबरमती रेलवे स्टेशन", "lat": 23.0760, "lng": 72.5840, "line": "Red", "is_underground": True, "interchange": False, "integrations": ["Railway"]},
    {"id": "aec", "name_en": "AEC", "name_gu": "એઇસી", "name_hi": "एईसी", "lat": 23.0820, "lng": 72.5855, "line": "Red", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "sabarmati", "name_en": "Sabarmati", "name_gu": "સાબરમતી", "name_hi": "साबरमती", "lat": 23.0900, "lng": 72.5875, "line": "Red", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "motera_stadium", "name_en": "Motera Stadium", "name_gu": "મોટેરા સ્ટેડિયમ", "name_hi": "मोटेरा स्टेडियम", "lat": 23.1000, "lng": 72.5975, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "koteshwar_road", "name_en": "Koteshwar Road", "name_gu": "કોટેશ્વર રોડ", "name_hi": "कोटेश्वर रोड", "lat": 23.1080, "lng": 72.6025, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "vishwakarma_college", "name_en": "Vishwakarma College", "name_gu": "વિશ્વકર્મા કોલેજ", "name_hi": "विश्वकर्मा कॉलेज", "lat": 23.1180, "lng": 72.6075, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "tapovan_circle", "name_en": "Tapovan Circle", "name_gu": "તપોવન સર્કલ", "name_hi": "तपोवन सर्कल", "lat": 23.1250, "lng": 72.6105, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "narmada_canal", "name_en": "Narmada Canal", "name_gu": "નર્મદા કેનાલ", "name_hi": "नर्मदा नहर", "lat": 23.1350, "lng": 72.6150, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "koba_circle", "name_en": "Koba Circle", "name_gu": "કોબા સર્કલ", "name_hi": "कोबा सर्कल", "lat": 23.1480, "lng": 72.6205, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "juna_koba", "name_en": "Juna Koba", "name_gu": "જૂના કોબા", "name_hi": "जूना कोबा", "lat": 23.1550, "lng": 72.6255, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "koba_gaam", "name_en": "Koba Gaam", "name_gu": "કોબા ગામ", "name_hi": "कोबा गाम", "lat": 23.1600, "lng": 72.6300, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "gnlu", "name_en": "GNLU", "name_gu": "જીએનએલયુ", "name_hi": "जीएनएलयू", "lat": 23.1680, "lng": 72.6350, "line": "Red", "is_underground": False, "interchange": True, "integrations": []},
    {"id": "raysan", "name_en": "Raysan", "name_gu": "રાયસણ", "name_hi": "रायसण", "lat": 23.1800, "lng": 72.6400, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "randesan", "name_en": "Randesan", "name_gu": "રંદેસણ", "name_hi": "रंदेसण", "lat": 23.1900, "lng": 72.6430, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "dholakuva_circle", "name_en": "Dholakuva Circle", "name_gu": "ધોળાકુવા સર્કલ", "name_hi": "धोलाकुआं सर्कल", "lat": 23.2000, "lng": 72.6450, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "infocity", "name_en": "Infocity", "name_gu": "ઇન્ફોસિટી", "name_hi": "इन्फोसिटी", "lat": 23.2100, "lng": 72.6500, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sector_1", "name_en": "Sector 1", "name_gu": "સેક્ટર ૧", "name_hi": "सेक्टर 1", "lat": 23.2150, "lng": 72.6550, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sector_10a", "name_en": "Sector 10A", "name_gu": "સેક્ટર ૧૦એ", "name_hi": "सेक्टर 10A", "lat": 23.2200, "lng": 72.6600, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sachivalaya", "name_en": "Sachivalaya", "name_gu": "સચિવાલય", "name_hi": "सचिवालय", "lat": 23.2250, "lng": 72.6650, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "akshardham", "name_en": "Akshardham", "name_gu": "અક્ષરધામ", "name_hi": "अक्षरधाम", "lat": 23.2350, "lng": 72.6700, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "juna_sachivalaya", "name_en": "Juna Sachivalaya", "name_gu": "જૂના સચિવાલય", "name_hi": "पुराना सचिवालय", "lat": 23.2450, "lng": 72.6650, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sector_16", "name_en": "Sector 16", "name_gu": "સેક્ટર ૧૬", "name_hi": "सेक्टर 16", "lat": 23.2500, "lng": 72.6600, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sector_24", "name_en": "Sector 24", "name_gu": "સેક્ટર ૨૪", "name_hi": "सेक्टर 24", "lat": 23.2550, "lng": 72.6550, "line": "Red", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "mahatma_mandir", "name_en": "Mahatma Mandir", "name_gu": "મહાત્મા મંદિર", "name_hi": "महात्मा मंदिर", "lat": 23.2600, "lng": 72.6500, "line": "Red", "is_underground": False, "interchange": False, "integrations": ["Railway"]},

    # GIFT City branch
    {"id": "pdeu", "name_en": "PDEU", "name_gu": "પીડીઇયુ", "name_hi": "पीडीईयू", "lat": 23.1650, "lng": 72.6500, "line": "Branch", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "gift_city", "name_en": "GIFT City", "name_gu": "ગિફ્ટ સિટી", "name_hi": "गिफ्ट सिटी", "lat": 23.1600, "lng": 72.6850, "line": "Branch", "is_underground": False, "interchange": False, "integrations": []},

    # Blue line (West to East)
    {"id": "thaltej_gam", "name_en": "Thaltej Gam", "name_gu": "થલતેજ ગામ", "name_hi": "थलतेज गाम", "lat": 23.0550, "lng": 72.5000, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "thaltej", "name_en": "Thaltej", "name_gu": "થલતેજ", "name_hi": "थलतेज", "lat": 23.0520, "lng": 72.5150, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "doordarshan_kendra", "name_en": "Doordarshan Kendra", "name_gu": "દૂરદર્શન કેન્દ્ર", "name_hi": "दूरदर्शन केंद्र", "lat": 23.0480, "lng": 72.5300, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "gurukul_road", "name_en": "Gurukul Road", "name_gu": "ગુરુકુળ રોડ", "name_hi": "गुरुकुल रोड", "lat": 23.0450, "lng": 72.5450, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "gujarat_university", "name_en": "Gujarat University", "name_gu": "ગુજરાત યુનિવર્સિટી", "name_hi": "गुजरात विश्वविद्यालय", "lat": 23.0350, "lng": 72.5550, "line": "Blue", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "commerce_six_road", "name_en": "Commerce Six Road", "name_gu": "કોમર્સ છ રસ્તા", "name_hi": "कॉमर्स छह रास्ता", "lat": 23.0380, "lng": 72.5650, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "sp_stadium", "name_en": "SP Stadium", "name_gu": "એસપી સ્ટેડિયમ", "name_hi": "एसपी स्टेडियम", "lat": 23.0400, "lng": 72.5700, "line": "Blue", "is_underground": False, "interchange": False, "integrations": ["Railway"]},
    {"id": "shahpur", "name_en": "Shahpur", "name_gu": "શાહપુર", "name_hi": "शाहपुर", "lat": 23.0330, "lng": 72.5800, "line": "Blue", "is_underground": True, "interchange": False, "integrations": []},
    {"id": "ghee_kanta", "name_en": "Ghee Kanta", "name_gu": "ઘી કાંટા", "name_hi": "घी कांटा", "lat": 23.0300, "lng": 72.5850, "line": "Blue", "is_underground": True, "interchange": False, "integrations": []},
    {"id": "kalupur", "name_en": "Kalupur", "name_gu": "કાલુપુર", "name_hi": "कालूपुर", "lat": 23.0250, "lng": 72.6000, "line": "Blue", "is_underground": True, "interchange": False, "integrations": ["Railway"]},
    {"id": "kankaria_east", "name_en": "Kankaria East", "name_gu": "કાંકરિયા પૂર્વ", "name_hi": "कांकरिया पूर्व", "lat": 23.0150, "lng": 72.6100, "line": "Blue", "is_underground": True, "interchange": False, "integrations": ["Railway"]},
    {"id": "apparel_park", "name_en": "Apparel Park", "name_gu": "એપેરલ પાર્ક", "name_hi": "अपैरल पार्क", "lat": 23.0100, "lng": 72.6200, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "amraivadi", "name_en": "Amraivadi", "name_gu": "અમરાઈવાડી", "name_hi": "अमराईवाडी", "lat": 23.0080, "lng": 72.6300, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "rabari_colony", "name_en": "Rabari Colony", "name_gu": "રબારી કોલોની", "name_hi": "रबारी कॉलोनी", "lat": 23.0050, "lng": 72.6400, "line": "Blue", "is_underground": True, "interchange": False, "integrations": ["BRTS"]},
    {"id": "vastral", "name_en": "Vastral", "name_gu": "વસ્ત્રાલ", "name_hi": "वस्त्राल", "lat": 23.0000, "lng": 72.6500, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "nirant_cross_road", "name_en": "Nirant Cross Road", "name_gu": "નિરાંત ક્રોસ રોડ", "name_hi": "निरांत क्रॉस रोड", "lat": 22.9980, "lng": 72.6600, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []},
    {"id": "vastral_gam", "name_en": "Vastral Gam", "name_gu": "વસ્ત્રાલ ગામ", "name_hi": "वस्त्राल गाम", "lat": 22.9950, "lng": 72.6700, "line": "Blue", "is_underground": False, "interchange": False, "integrations": []}
    # Old High Court is interchange, already added above, but we need to ensure the graph builder knows Blue line stops there. We'll add it again with line="Blue" or handle it in logic.
    # To handle graph easily, let's keep stations unique by ID, and lines as list.
]

# Update Old High court line
for s in stations:
    if s["id"] == "old_high_court":
        s["line"] = ["Red", "Blue"]
    elif s["id"] == "gnlu":
        s["line"] = ["Red", "Branch"]
    else:
        s["line"] = [s["line"]]

with open('backend/data/stations.json', 'w', encoding='utf-8') as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

print("Generated stations.json")
