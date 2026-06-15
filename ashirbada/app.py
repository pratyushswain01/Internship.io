"""
╔══════════════════════════════════════════════════════════════════════════╗
║   🌍 DISASTER MANAGEMENT & EMERGENCY RESPONSE DASHBOARD                 ║
║   Complete Single-File Flask Application                                 ║
║   Version: 2.0 Enterprise                                                ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3, os, json, hashlib, secrets
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, g

# ─────────────────────────────────────────────
# APP CONFIG
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DB_PATH = "disaster_mgmt.db"

# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db:
        db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def mutate(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────────
# DATABASE INIT & SEED
# ─────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS disasters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    causes TEXT,
    warning_signs TEXT,
    impact TEXT,
    safety_measures TEXT,
    first_aid TEXT,
    icon TEXT DEFAULT '⚠️',
    color TEXT DEFAULT '#e74c3c',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS disaster_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_id INTEGER,
    title TEXT,
    location TEXT,
    country TEXT,
    latitude REAL,
    longitude REAL,
    severity TEXT,
    affected_population INTEGER DEFAULT 0,
    injured INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Active',
    reported_date TEXT,
    FOREIGN KEY(disaster_id) REFERENCES disasters(id)
);

CREATE TABLE IF NOT EXISTS emergency_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    category TEXT,
    available_24h INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS shelters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    city TEXT,
    capacity INTEGER,
    occupied INTEGER DEFAULT 0,
    latitude REAL,
    longitude REAL,
    amenities TEXT,
    status TEXT DEFAULT 'Open'
);

CREATE TABLE IF NOT EXISTS preparedness_checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disaster_type TEXT,
    item_name TEXT,
    description TEXT,
    priority TEXT DEFAULT 'High'
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    message TEXT,
    severity TEXT,
    region TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_msg TEXT,
    bot_msg TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

DISASTERS_SEED = [
    ("Earthquake","Geological","Sudden shaking of the Earth's surface caused by seismic waves.",
     "Tectonic plate movement, volcanic activity, underground explosions",
     "Foreshocks, ground tilting, unusual animal behavior, radon gas release",
     "Structural damage, casualties, tsunamis, landslides, fires",
     "Drop-Cover-Hold On, stay away from windows, have emergency kit ready",
     "Treat crush injuries, control bleeding, CPR if needed","🏚️","#e74c3c"),
    ("Flood","Hydrological","Overflow of water submerging land that is normally dry.",
     "Heavy rainfall, storm surge, dam failure, rapid snowmelt",
     "Rising water levels, heavy rainfall, weather alerts, waterlogged soil",
     "Property damage, crop loss, disease outbreaks, displacement",
     "Move to higher ground, avoid floodwaters, follow evacuation orders",
     "Treat hypothermia, water-borne disease prevention, wound care","🌊","#3498db"),
    ("Cyclone","Meteorological","Rotating storm system with low-pressure center and strong winds.",
     "Warm ocean water, atmospheric instability, Coriolis effect",
     "Decreasing barometric pressure, increasing winds, cloud formations",
     "Storm surge, flooding, wind damage, loss of life",
     "Reinforce home, stock supplies, know evacuation routes",
     "Treat wind injuries, hypothermia, wound infections","🌀","#9b59b6"),
    ("Tsunami","Oceanographic","Large ocean waves triggered by underwater disturbances.",
     "Undersea earthquakes, volcanic eruptions, underwater landslides",
     "Strong ground shaking, ocean withdrawal, roaring sound",
     "Coastal flooding, infrastructure damage, mass casualties",
     "Move inland immediately, go to high ground, follow sirens",
     "Treat drowning, hypothermia, trauma injuries","🌊","#2980b9"),
    ("Wildfire","Environmental","Uncontrolled fire spreading in wildland vegetation.",
     "Drought, lightning strikes, human activity, strong winds",
     "Smoke, unusual animal movement, dry conditions, hot weather",
     "Air quality degradation, habitat destruction, property loss",
     "Create defensible space, have go-bag ready, follow evacuation",
     "Treat smoke inhalation, burns, respiratory issues","🔥","#e67e22"),
    ("Drought","Climatological","Extended period of abnormally low rainfall.",
     "High pressure systems, deforestation, climate change, El Niño",
     "Low reservoir levels, dry soil, crop stress, reduced streamflow",
     "Food shortage, economic losses, water scarcity, migration",
     "Water conservation, crop diversification, drought-resistant crops",
     "Treat dehydration, malnutrition, heat stroke","🏜️","#f39c12"),
    ("Landslide","Geological","Mass movement of rock, earth, or debris down a slope.",
     "Heavy rainfall, earthquakes, slope instability, deforestation",
     "Cracks in ground, unusual sounds, tilting trees, spring water changes",
     "Property destruction, road blockages, casualties",
     "Avoid steep slopes during rain, install drainage, plant vegetation",
     "Treat crush injuries, trauma, respiratory issues","⛰️","#795548"),
    ("Volcanic Eruption","Geological","Expulsion of lava, ash, and gases from a volcano.",
     "Magma pressure, tectonic plate movement, hotspot activity",
     "Increased seismicity, ground deformation, gas emissions",
     "Lava flows, ash fall, pyroclastic flows, lahars",
     "Evacuate danger zones, wear N95 masks, protect water supply",
     "Treat burns, respiratory issues, eye irritation","🌋","#d35400"),
    ("Heatwave","Meteorological","Extended period of excessively hot weather.",
     "High pressure systems, urban heat island, climate change",
     "Consecutive hot days, high humidity, lack of wind, warnings",
     "Heat stroke, crop failure, power grid stress, deaths",
     "Stay hydrated, stay in cool areas, check on vulnerable people",
     "Treat heat stroke with cooling, IV fluids for dehydration","☀️","#f1c40f"),
    ("Cold Wave","Meteorological","Extended period of exceptionally cold weather.",
     "Arctic air masses, lack of cloud cover, wind chill",
     "Dropping temperatures, frost advisories, wind chill warnings",
     "Hypothermia, frostbite, pipe bursting, crop damage",
     "Layer clothing, insulate home, avoid unnecessary travel",
     "Treat hypothermia, frostbite with gradual rewarming","❄️","#bdc3c7"),
    ("Pandemic","Biological","Worldwide spread of a new infectious disease.",
     "Novel pathogens, globalization, zoonotic spillover, mutation",
     "Unusual disease clusters, rapid spread, mortality spikes",
     "Mass casualties, economic collapse, healthcare overwhelm",
     "Vaccination, mask wearing, quarantine, social distancing",
     "Isolate patients, supportive care, contact tracing","🦠","#1abc9c"),
    ("Thunderstorm","Meteorological","Severe weather with lightning, thunder, heavy rain.",
     "Atmospheric instability, moisture, lifting mechanisms",
     "Darkening skies, lightning, thunder, wind gusts, hail",
     "Lightning strikes, flash floods, wind damage, power outages",
     "Stay indoors, unplug electronics, avoid water",
     "Treat lightning strikes, CPR, wound care","⛈️","#2c3e50"),
    ("Avalanche","Geological","Rapid flow of snow down a slope.",
     "Heavy snowfall, temperature changes, steep terrain, human activity",
     "Cracking sounds, recent heavy snow, wind-loaded slopes",
     "Burial, trauma, road closures, infrastructure damage",
     "Carry beacon/probe/shovel, avoid avalanche terrain, check bulletins",
     "Rapid avalanche burial rescue, treat hypothermia, trauma","🏔️","#ecf0f1"),
    ("Industrial Disaster","Technological","Accidents at industrial facilities causing hazardous releases.",
     "Equipment failure, human error, poor safety protocols",
     "Unusual smells, alarms, visible leaks, worker reports",
     "Chemical exposure, explosions, environmental contamination",
     "Follow shelter-in-place or evacuation protocols",
     "Decontamination, treat chemical burns, respiratory support","🏭","#7f8c8d"),
    ("Nuclear Disaster","Radiological","Release of radioactive material from nuclear facilities.",
     "Reactor malfunction, natural disasters, human error",
     "Alarms, radiation monitors, unusual heat, steam releases",
     "Radiation exposure, evacuation zones, long-term contamination",
     "Evacuate, take potassium iodide, seal indoor spaces",
     "Treat radiation syndrome, decontamination, wound care","☢️","#8e44ad"),
    ("Chemical Leakage","Technological","Release of toxic chemicals into the environment.",
     "Storage failure, transport accidents, industrial sabotage",
     "Unusual odors, discoloration, people feeling unwell",
     "Toxic exposure, environmental damage, casualties",
     "Evacuate upwind, shelter-in-place, contact HAZMAT",
     "Decontaminate, treat chemical exposure, respiratory support","⚗️","#16a085"),
    ("Hurricane","Meteorological","Tropical cyclone with sustained winds ≥ 74 mph.",
     "Warm ocean temperatures, atmospheric moisture, low pressure",
     "Satellite imagery, barometric drops, tropical storm upgrades",
     "Storm surge, extreme winds, flooding, power outages",
     "Board windows, stock 3-day supplies, know evacuation zones",
     "Treat wind injuries, drowning, debris trauma","🌪️","#8e44ad"),
    ("Tornado","Meteorological","Violently rotating column of air touching the ground.",
     "Supercell thunderstorms, atmospheric instability, wind shear",
     "Dark funnel cloud, loud roar, flying debris, rotation",
     "Structural damage, casualties, power outages",
     "Go to basement or interior room, stay away from windows",
     "Treat penetrating injuries, crush syndrome, trauma","🌪️","#c0392b"),
    ("Sandstorm","Meteorological","Strong winds that carry large amounts of sand and dust.",
     "Dry conditions, strong winds, arid landscapes",
     "Hazy horizon, dropping visibility, wind gusts",
     "Respiratory issues, vehicle accidents, infrastructure damage",
     "Stay indoors, cover nose/mouth, secure loose objects",
     "Treat eye injuries, respiratory distress, skin abrasions","🏜️","#d4a017"),
    ("Locust Invasion","Biological","Large swarms of locusts devastating crops and vegetation.",
     "Weather conditions enabling breeding, overcrowding",
     "Small swarms appearing, increased locust sightings",
     "Crop destruction, food insecurity, economic losses",
     "Monitor swarms, coordinate pesticide application",
     "Treat secondary malnutrition effects from food shortage","🦗","#27ae60"),
]

EVENTS_SEED = [
    (1, "Nepal Earthquake 2024", "Jajarkot, Nepal", "Nepal", 28.8, 82.2, "High", 120000, 3500, 157, "Resolved", "2024-11-03"),
    (2, "Bangladesh Flooding", "Sylhet, Bangladesh", "Bangladesh", 24.9, 91.8, "Extreme", 500000, 12000, 89, "Active", "2025-06-01"),
    (3, "Cyclone Tej", "Andhra Pradesh, India", "India", 16.5, 80.6, "High", 200000, 4500, 34, "Resolved", "2024-10-23"),
    (4, "Japan Tsunami Warning", "Ishikawa, Japan", "Japan", 37.2, 137.0, "Medium", 80000, 1200, 15, "Active", "2025-01-01"),
    (5, "California Wildfire", "Los Angeles, USA", "USA", 34.0, -118.2, "Extreme", 150000, 890, 28, "Active", "2025-01-10"),
    (6, "East Africa Drought", "Turkana, Kenya", "Kenya", 3.1, 35.6, "High", 3000000, 200000, 1200, "Active", "2024-09-01"),
    (7, "Papua New Guinea Landslide", "Enga Province, PNG", "Papua New Guinea", -5.4, 143.2, "Extreme", 8000, 600, 316, "Resolved", "2024-05-24"),
    (8, "Iceland Volcanic Eruption", "Reykjanes Peninsula", "Iceland", 63.8, -22.4, "Medium", 30000, 200, 0, "Active", "2024-12-18"),
    (9, "India Heatwave", "Rajasthan, India", "India", 26.9, 75.8, "High", 5000000, 45000, 234, "Resolved", "2024-05-15"),
    (10, "Ukraine Cold Wave", "Kyiv, Ukraine", "Ukraine", 50.4, 30.5, "High", 1000000, 8000, 45, "Resolved", "2024-01-15"),
    (11, "COVID-19 Resurgence", "Multiple Regions", "Global", 0.0, 0.0, "Extreme", 50000000, 2000000, 15000, "Active", "2024-08-01"),
    (12, "Texas Thunderstorm", "Houston, USA", "USA", 29.7, -95.4, "Medium", 250000, 890, 12, "Resolved", "2024-04-02"),
    (13, "Swiss Avalanche", "Davos, Switzerland", "Switzerland", 46.8, 9.8, "Medium", 5000, 120, 8, "Resolved", "2024-02-10"),
    (14, "India Industrial Accident", "Visakhapatnam, India", "India", 17.7, 83.3, "High", 100000, 5000, 13, "Resolved", "2024-01-08"),
    (15, "Turkey Earthquake", "Kahramanmaras, Turkey", "Turkey", 37.5, 36.9, "Extreme", 1800000, 107000, 50783, "Resolved", "2023-02-06"),
    (16, "Typhoon Gaemi", "Taiwan", "Taiwan", 25.0, 121.5, "High", 180000, 2300, 44, "Resolved", "2024-07-25"),
    (17, "Missouri Tornado", "St. Louis, USA", "USA", 38.6, -90.2, "Medium", 50000, 700, 5, "Resolved", "2024-03-14"),
    (18, "Sahara Sandstorm", "Cairo, Egypt", "Egypt", 30.0, 31.2, "Medium", 500000, 3000, 2, "Resolved", "2024-04-29"),
    (19, "Morocco Earthquake", "Marrakesh, Morocco", "Morocco", 31.6, -7.9, "Extreme", 500000, 5600, 2960, "Resolved", "2023-09-08"),
    (20, "Canada Wildfire", "British Columbia, Canada", "Canada", 53.7, -127.6, "High", 200000, 5000, 0, "Resolved", "2024-08-12"),
    (1, "Ecuador Earthquake", "Pastaza, Ecuador", "Ecuador", -1.5, -78.0, "Medium", 45000, 1200, 14, "Active", "2025-03-18"),
    (2, "Pakistan Monsoon Flood", "Sindh, Pakistan", "Pakistan", 25.9, 68.4, "Extreme", 2000000, 80000, 456, "Active", "2025-07-10"),
    (3, "Philippines Typhoon", "Bicol Region, Philippines", "Philippines", 13.4, 123.4, "High", 250000, 6000, 67, "Resolved", "2024-11-16"),
    (6, "Somalia Drought", "Baidoa, Somalia", "Somalia", 3.1, 43.6, "Extreme", 8000000, 1000000, 4500, "Active", "2024-01-01"),
    (5, "Greece Wildfire", "Thessaly, Greece", "Greece", 39.6, 22.4, "High", 90000, 2000, 26, "Resolved", "2023-07-25"),
    (2, "China Flooding", "Zhengzhou, China", "China", 34.7, 113.6, "High", 1200000, 50000, 302, "Resolved", "2021-07-20"),
    (11, "Mpox Outbreak", "DRC", "Congo", -4.3, 15.3, "High", 500000, 50000, 1200, "Active", "2024-08-14"),
    (1, "Italy Earthquake", "Campi Flegrei, Italy", "Italy", 40.8, 14.1, "Medium", 80000, 2000, 0, "Active", "2024-09-30"),
    (8, "Indonesia Volcano", "Marapi, Indonesia", "Indonesia", -0.4, 100.5, "High", 150000, 3000, 24, "Resolved", "2023-12-03"),
    (7, "Colombia Landslide", "Cauca Department", "Colombia", 2.5, -76.6, "High", 20000, 800, 33, "Resolved", "2024-06-01"),
    (9, "Greece Heatwave", "Athens, Greece", "Greece", 37.9, 23.7, "High", 2000000, 30000, 187, "Resolved", "2024-07-15"),
    (4, "Philippines Tsunami", "Mindanao, Philippines", "Philippines", 7.0, 125.5, "Medium", 100000, 3000, 20, "Active", "2025-05-10"),
    (5, "Australia Bushfire", "Victoria, Australia", "Australia", -37.8, 144.9, "Extreme", 300000, 4000, 33, "Resolved", "2020-01-01"),
    (12, "Bangladesh Thunderstorm", "Dhaka, Bangladesh", "Bangladesh", 23.8, 90.4, "Low", 300000, 2000, 18, "Resolved", "2024-04-14"),
    (6, "Ethiopia Drought", "Oromia, Ethiopia", "Ethiopia", 7.5, 40.0, "Extreme", 10000000, 2000000, 5000, "Active", "2024-02-01"),
    (2, "Yemen Flooding", "Hadramaut, Yemen", "Yemen", 16.1, 48.8, "High", 400000, 20000, 89, "Active", "2024-08-19"),
    (17, "Oklahoma Tornado", "Oklahoma City, USA", "USA", 35.5, -97.5, "High", 100000, 1500, 36, "Resolved", "2024-05-06"),
    (3, "Myanmar Cyclone", "Rakhine, Myanmar", "Myanmar", 20.1, 92.9, "High", 300000, 10000, 145, "Resolved", "2024-05-10"),
    (10, "Europe Cold Wave", "Poland", "Poland", 52.2, 21.0, "High", 5000000, 100000, 234, "Resolved", "2024-01-20"),
    (19, "Algeria Earthquake", "Tipaza, Algeria", "Algeria", 36.5, 2.4, "Medium", 60000, 2000, 0, "Active", "2025-02-28"),
    (8, "Guatemala Volcano", "Santiaguito, Guatemala", "Guatemala", 14.7, -91.6, "Medium", 40000, 1000, 0, "Active", "2025-04-01"),
    (7, "Brazil Landslide", "Petropolis, Brazil", "Brazil", -22.5, -43.2, "Extreme", 60000, 2500, 233, "Resolved", "2022-02-15"),
    (5, "Portugal Wildfire", "Setubal, Portugal", "Portugal", 38.5, -8.9, "High", 70000, 1200, 7, "Resolved", "2024-09-17"),
    (13, "France Avalanche", "Chamonix, France", "France", 45.9, 6.9, "Medium", 8000, 200, 6, "Resolved", "2024-01-30"),
    (18, "Iraq Sandstorm", "Baghdad, Iraq", "Iraq", 33.3, 44.4, "High", 2000000, 10000, 0, "Active", "2025-05-20"),
    (11, "Bird Flu Outbreak", "Cambodia", "Cambodia", 12.6, 104.9, "Medium", 2000000, 100000, 45, "Resolved", "2024-03-01"),
    (16, "Japan Typhoon", "Okinawa, Japan", "Japan", 26.2, 127.7, "High", 200000, 3000, 22, "Resolved", "2024-08-30"),
    (14, "India Chemical Leak", "Bhopal, India", "India", 23.2, 77.4, "Extreme", 500000, 100000, 3787, "Resolved", "1984-12-03"),
    (15, "Afghanistan Earthquake", "Herat, Afghanistan", "Afghanistan", 34.3, 62.2, "Extreme", 250000, 10000, 1480, "Resolved", "2023-10-07"),
    (20, "Russia Wildfire", "Siberia, Russia", "Russia", 61.5, 105.0, "High", 50000, 1000, 0, "Active", "2025-06-10"),
]

CONTACTS_SEED = [
    ("National Disaster Response Force (NDRF)", "1078", "ndrf@gov.in", "https://ndrf.gov.in", "Government", 1),
    ("National Emergency Number", "112", "help@112.gov.in", "https://112.gov.in", "Emergency", 1),
    ("Police", "100", "police@gov.in", "https://police.gov.in", "Law Enforcement", 1),
    ("Fire Brigade", "101", "fire@gov.in", "https://fireservices.gov.in", "Fire & Rescue", 1),
    ("Ambulance", "102", "ambulance@gov.in", "https://health.gov.in", "Medical", 1),
    ("Women Helpline", "1091", "women@gov.in", "https://wcd.nic.in", "Social Services", 1),
    ("Child Helpline", "1098", "childline@gov.in", "https://childlineindia.org", "Social Services", 1),
    ("Mental Health Helpline", "iCall: 9152987821", "icall@iitb.ac.in", "https://icallhelpline.org", "Medical", 1),
    ("Coast Guard", "1554", "coastguard@gov.in", "https://indiancoastguard.gov.in", "Rescue", 1),
    ("Indian Red Cross Society", "+91-11-23711551", "info@indianredcross.org", "https://indianredcross.org", "NGO", 1),
    ("UNICEF India", "+91-11-24673400", "unicefindia@unicef.org", "https://unicef.org/india", "NGO", 1),
    ("WHO India", "+91-11-23370804", "searo@who.int", "https://who.int/india", "Health", 1),
    ("FEMA (USA)", "1-800-621-FEMA", "fema@dhs.gov", "https://fema.gov", "Government", 1),
    ("American Red Cross", "1-800-RED-CROSS", "info@redcross.org", "https://redcross.org", "NGO", 1),
    ("UN OCHA", "+1-212-963-1234", "ocha@un.org", "https://unocha.org", "International", 1),
    ("Doctors Without Borders", "+1-212-679-6800", "info@msf.org", "https://msf.org", "Medical NGO", 1),
    ("World Food Programme", "+39-06-65131", "wfp.info@wfp.org", "https://wfp.org", "NGO", 1),
    ("UNHCR", "+41-22-739-8111", "hqpi00@unhcr.org", "https://unhcr.org", "International", 1),
    ("Save the Children", "+1-203-221-4000", "webmaster@savechildren.org", "https://savethechildren.org", "NGO", 1),
    ("Oxfam International", "+44-1865-473-727", "oxfam@oxfam.org", "https://oxfam.org", "NGO", 1),
    ("CARE International", "+1-800-521-2273", "info@care.org", "https://care.org", "NGO", 1),
    ("International Rescue Committee", "+1-212-551-3000", "irc@rescue.org", "https://rescue.org", "NGO", 1),
    ("World Vision", "+1-888-511-6548", "info@worldvision.org", "https://worldvision.org", "NGO", 1),
    ("Plan International", "+1-401-649-6600", "info@planusa.org", "https://planusa.org", "NGO", 1),
    ("Action Against Hunger", "+1-212-967-7800", "info@actionagainsthunger.org", "https://actionagainsthunger.org", "NGO", 1),
    ("National Poison Control Center (India)", "1800-116-117", "npcc@aiims.ac.in", "https://aiims.edu", "Medical", 1),
    ("NDMA India", "011-26701700", "ndma@gov.in", "https://ndma.gov.in", "Government", 1),
    ("IMD (Weather)", "1800-180-1717", "imd@gov.in", "https://imd.gov.in", "Weather", 1),
    ("ISRO Disaster Management", "080-22172000", "disastermgmt@isro.gov.in", "https://isro.gov.in", "Government", 1),
    ("Central Water Commission", "011-26107271", "cwc@gov.in", "https://cwc.gov.in", "Government", 1),
]

SHELTERS_SEED = [
    ("Rajpath Community Center", "Rajpath, New Delhi", "New Delhi", 500, 120, 28.6139, 77.2090, "Food,Water,Medical,Beds", "Open"),
    ("Yamuna Flood Relief Camp", "ITO, New Delhi", "New Delhi", 1000, 450, 28.6280, 77.2416, "Food,Water,Beds,Toilets", "Open"),
    ("NCC Ground Shelter", "MG Marg, Mumbai", "Mumbai", 800, 200, 19.0760, 72.8777, "Food,Water,Medical", "Open"),
    ("Bandra Relief Center", "Bandra West, Mumbai", "Mumbai", 600, 310, 19.0596, 72.8295, "Food,Water,Beds", "Open"),
    ("Chennai Flood Shelter", "Marina Beach Road", "Chennai", 1200, 890, 13.0827, 80.2707, "Food,Water,Medical,Beds", "Open"),
    ("Kolkata Emergency Shelter", "Salt Lake, Kolkata", "Kolkata", 700, 234, 22.5726, 88.3639, "Food,Water,Beds", "Open"),
    ("Hyderabad Relief Camp", "Hussain Sagar Lake Road", "Hyderabad", 900, 400, 17.3850, 78.4867, "Food,Water,Medical", "Open"),
    ("Bangalore Safety Center", "MG Road, Bangalore", "Bangalore", 500, 180, 12.9716, 77.5946, "Food,Water,Beds", "Open"),
    ("Ahmedabad Cyclone Shelter", "Vastrapur, Ahmedabad", "Ahmedabad", 800, 290, 23.0225, 72.5714, "Food,Water,Medical,Beds", "Open"),
    ("Bhubaneswar Super Cyclone Camp", "NH16, Bhubaneswar", "Bhubaneswar", 1500, 600, 20.2961, 85.8245, "Food,Water,Medical,Beds,Generator", "Open"),
    ("FEMA Shelter Houston", "Reliant Center, Houston", "Houston", 5000, 1200, 29.6697, -95.4097, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("LA Earthquake Relief", "Staples Center, LA", "Los Angeles", 8000, 3400, 34.0430, -118.2673, "Food,Water,Medical,Beds", "Open"),
    ("New York Storm Shelter", "Madison Square Garden, NYC", "New York", 10000, 2100, 40.7505, -73.9934, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("Chicago Emergency Center", "McCormick Place, Chicago", "Chicago", 6000, 800, 41.8505, -87.6168, "Food,Water,Medical,Beds", "Open"),
    ("Miami Hurricane Shelter", "AmericanAirlines Arena", "Miami", 4000, 1600, 25.7814, -80.1870, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Tokyo Disaster Shelter", "Yoyogi Park, Tokyo", "Tokyo", 20000, 5600, 35.6762, 139.6503, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("Osaka Relief Center", "Namba Park, Osaka", "Osaka", 8000, 2300, 34.6937, 135.5023, "Food,Water,Medical,Beds", "Open"),
    ("Manila Typhoon Shelter", "Luneta Park, Manila", "Manila", 15000, 8900, 14.5893, 120.9786, "Food,Water,Medical,Beds", "Open"),
    ("Bangkok Flood Center", "Impact Arena, Bangkok", "Bangkok", 10000, 3400, 13.7563, 100.5018, "Food,Water,Medical,Beds", "Open"),
    ("Jakarta Emergency Shelter", "Senayan, Jakarta", "Jakarta", 12000, 5600, -6.2088, 106.8456, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Dhaka Flood Shelter", "National Stadium, Dhaka", "Dhaka", 8000, 4500, 23.8103, 90.4125, "Food,Water,Beds", "Open"),
    ("Karachi Cyclone Shelter", "National Stadium, Karachi", "Karachi", 6000, 1800, 24.8607, 67.0011, "Food,Water,Medical,Beds", "Open"),
    ("Kathmandu Earthquake Camp", "Tudikhel Ground, Kathmandu", "Kathmandu", 3000, 1200, 27.7172, 85.3240, "Food,Water,Medical,Beds", "Open"),
    ("Colombo Relief Center", "Galle Face Green, Colombo", "Colombo", 5000, 2100, 6.9271, 79.8612, "Food,Water,Medical", "Open"),
    ("Cairo Sandstorm Shelter", "Cairo International Center", "Cairo", 4000, 600, 30.0444, 31.2357, "Food,Water,Beds", "Open"),
    ("Nairobi Drought Relief", "Uhuru Park, Nairobi", "Nairobi", 6000, 3400, -1.2921, 36.8219, "Food,Water,Medical,Beds", "Open"),
    ("Addis Ababa Shelter", "Meskel Square, Addis Ababa", "Addis Ababa", 8000, 5600, 9.0250, 38.7469, "Food,Water,Medical", "Open"),
    ("Lagos Flood Center", "National Stadium, Lagos", "Lagos", 5000, 2200, 6.4541, 3.3947, "Food,Water,Beds", "Open"),
    ("Kinshasa Relief Camp", "Palais du Peuple, Kinshasa", "Kinshasa", 3000, 1800, -4.4419, 15.2663, "Food,Water,Medical", "Open"),
    ("Sydney Bushfire Shelter", "ANZ Stadium, Sydney", "Sydney", 8000, 1200, -33.8688, 151.2093, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("Melbourne Emergency Center", "Melbourne Park", "Melbourne", 6000, 800, -37.8136, 144.9631, "Food,Water,Medical,Beds", "Open"),
    ("Auckland Volcano Shelter", "Eden Park, Auckland", "Auckland", 4000, 500, -36.8485, 174.7633, "Food,Water,Medical,Beds", "Open"),
    ("Reykjavik Volcano Camp", "Laugardalur, Reykjavik", "Reykjavik", 1000, 200, 64.1466, -21.9426, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Istanbul Earthquake Shelter", "Atatürk Olympic Stadium", "Istanbul", 12000, 3400, 41.0082, 28.9784, "Food,Water,Medical,Beds", "Open"),
    ("Athens Wildfire Center", "Olympic Stadium, Athens", "Athens", 8000, 2100, 37.9838, 23.7275, "Food,Water,Medical,Beds", "Open"),
    ("Lisbon Earthquake Shelter", "Estadio da Luz, Lisbon", "Lisbon", 6000, 800, 38.7223, -9.1393, "Food,Water,Medical,Beds", "Open"),
    ("Rome Seismic Shelter", "Foro Italico, Rome", "Rome", 8000, 1200, 41.9028, 12.4964, "Food,Water,Medical,Beds", "Open"),
    ("Paris Flood Center", "Stade de France, Paris", "Paris", 10000, 900, 48.9244, 2.3601, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("London Storm Shelter", "Wembley Stadium, London", "London", 15000, 2100, 51.5560, -0.2796, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("Berlin Cold Wave Center", "Olympiastadion, Berlin", "Berlin", 8000, 1600, 52.5147, 13.2398, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Kyiv Shelter", "Olympic National Stadium, Kyiv", "Kyiv", 10000, 5600, 50.4337, 30.5214, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Bogota Landslide Shelter", "El Campin, Bogota", "Bogota", 5000, 1800, 4.6453, -74.0855, "Food,Water,Medical,Beds", "Open"),
    ("Lima Earthquake Center", "Estadio Nacional, Lima", "Lima", 6000, 2300, -12.0464, -77.0428, "Food,Water,Medical,Beds", "Open"),
    ("Santiago Earthquake Shelter", "Estadio Nacional, Santiago", "Santiago", 5000, 1200, -33.4645, -70.6453, "Food,Water,Medical,Beds", "Open"),
    ("Buenos Aires Flood Center", "Estadio Monumental, BA", "Buenos Aires", 8000, 1400, -34.5455, -58.4499, "Food,Water,Medical,Beds", "Open"),
    ("Rio Landslide Shelter", "Maracana, Rio de Janeiro", "Rio de Janeiro", 10000, 3400, -22.9121, -43.2302, "Food,Water,Medical,Beds", "Open"),
    ("São Paulo Relief Camp", "Morumbi Stadium, SP", "São Paulo", 12000, 2800, -23.5505, -46.6333, "Food,Water,Medical,Beds,WiFi", "Open"),
    ("Brasilia Emergency Center", "Estádio Nacional, Brasilia", "Brasilia", 6000, 900, -15.7833, -47.9292, "Food,Water,Medical,Beds", "Open"),
    ("Mexico City Earthquake Shelter", "Estadio Azteca, CDMX", "Mexico City", 15000, 4500, 19.3030, -99.1508, "Food,Water,Medical,Beds,Generator", "Open"),
    ("Guatemala City Volcano Shelter", "Estadio Mateo Flores", "Guatemala City", 5000, 2100, 14.6349, -90.5069, "Food,Water,Medical,Beds", "Open"),
    ("San José Relief Center", "Estadio Nacional, San José", "San José", 3000, 800, 9.9341, -84.0877, "Food,Water,Medical,Beds", "Open"),
]

CHECKLISTS_SEED = [
    ("Earthquake","Emergency water supply (1 gallon/person/day for 3 days)","Store in sealed containers","High"),
    ("Earthquake","Non-perishable food (3-day supply)","Canned goods, energy bars","High"),
    ("Earthquake","First aid kit","Bandages, antiseptic, medications","High"),
    ("Earthquake","Flashlight and extra batteries","LED flashlight preferred","High"),
    ("Earthquake","Whistle to signal for help","Attach to emergency bag","Medium"),
    ("Earthquake","Dust masks (N95)","To filter contaminated air","High"),
    ("Earthquake","Moist towelettes and garbage bags","For sanitation","Medium"),
    ("Earthquake","Wrench or pliers to turn off utilities","Keep near gas meter","High"),
    ("Earthquake","Manual can opener","For canned food","Medium"),
    ("Earthquake","Local maps","Waterproof maps of your area","Medium"),
    ("Earthquake","Cell phone with chargers and backup battery","Power bank essential","High"),
    ("Earthquake","Important documents in waterproof container","ID, insurance, medical records","High"),
    ("Flood","Waterproof bags for important documents","Keep electronics dry","High"),
    ("Flood","Rubber boots and waterproof clothing","Protection from contaminated water","High"),
    ("Flood","Water purification tablets","For emergency water treatment","High"),
    ("Flood","Emergency flotation device","Life jacket or ring buoy","High"),
    ("Flood","Rope (50 feet minimum)","For rescue operations","Medium"),
    ("Flood","Battery-powered or hand-crank radio","For emergency broadcasts","High"),
    ("Flood","Sandbags (if time permits)","To protect property","Medium"),
    ("Flood","Elevated storage for valuables","Move electronics and documents up","High"),
    ("Cyclone","Board up windows and doors","Use storm shutters or plywood","High"),
    ("Cyclone","Secure outdoor furniture and objects","Bring inside or tie down","High"),
    ("Cyclone","Fill bathtub with water","Emergency water reserve","High"),
    ("Cyclone","Charge all devices","Before storm hits","High"),
    ("Cyclone","Identify interior room for shelter","Away from windows","High"),
    ("Cyclone","Fuel vehicle tank","For potential evacuation","Medium"),
    ("Pandemic","N95 or higher masks (30-day supply)","One per person per day","High"),
    ("Pandemic","Hand sanitizer (70%+ alcohol)","Multiple bottles","High"),
    ("Pandemic","30-day prescription medication supply","Contact doctor in advance","High"),
    ("Pandemic","Thermometer and oximeter","Monitor symptoms","High"),
    ("Pandemic","Disinfecting wipes and spray","For surface cleaning","High"),
    ("Pandemic","Telemedicine app setup","For remote medical consultation","Medium"),
    ("Wildfire","Go-bag packed and ready","Can leave in 5 minutes","High"),
    ("Wildfire","N95 masks for smoke","Smoke protection","High"),
    ("Wildfire","Evacuation routes mapped","Know 2+ ways out","High"),
    ("Wildfire","Defensible space around home","Clear vegetation 100 feet around","High"),
    ("Wildfire","Close all vents and windows","Prevent ember intrusion","High"),
    ("General","Emergency contact list printed","Don't rely only on phone","High"),
    ("General","Meeting point designated","Family reunion location","High"),
    ("General","Emergency cash reserve","ATMs may not work","Medium"),
    ("General","Copies of IDs and documents","Stored separately","High"),
    ("General","Pet emergency kit","Food, medications, carrier","Medium"),
    ("General","Special needs supplies","For infants, elderly, disabled","High"),
]

ALERTS_SEED = [
    ("Cyclone Warning - Bay of Bengal", "Category 3 cyclone developing. Coastal areas of Odisha and Andhra Pradesh on high alert.", "High", "Eastern India", 1),
    ("Flood Alert - Brahmaputra Basin", "Water levels rising rapidly. Evacuation advisories issued for low-lying areas.", "Extreme", "Assam, India", 1),
    ("Earthquake Risk - Himalayan Belt", "Minor tremors detected. Stay prepared, avoid old structures.", "Medium", "North India", 1),
    ("Heat Wave Warning", "Temperature expected to exceed 45°C. Stay hydrated, avoid outdoor activities.", "High", "Rajasthan, India", 1),
    ("Landslide Alert", "Heavy rainfall may trigger landslides. Avoid hill travel.", "Medium", "Western Ghats", 1),
]

def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()

    # Seed disasters
    conn.executemany("""INSERT INTO disasters (name,category,description,causes,warning_signs,impact,safety_measures,first_aid,icon,color)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", DISASTERS_SEED)

    # Seed events
    conn.executemany("""INSERT INTO disaster_events (disaster_id,title,location,country,latitude,longitude,severity,
        affected_population,injured,deaths,status,reported_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", EVENTS_SEED)

    # Seed contacts
    conn.executemany("""INSERT INTO emergency_contacts (department,phone,email,website,category,available_24h)
        VALUES (?,?,?,?,?,?)""", CONTACTS_SEED)

    # Seed shelters
    conn.executemany("""INSERT INTO shelters (name,address,city,capacity,occupied,latitude,longitude,amenities,status)
        VALUES (?,?,?,?,?,?,?,?,?)""", SHELTERS_SEED)

    # Seed checklists
    conn.executemany("""INSERT INTO preparedness_checklists (disaster_type,item_name,description,priority)
        VALUES (?,?,?,?)""", CHECKLISTS_SEED)

    # Seed alerts
    conn.executemany("""INSERT INTO alerts (title,message,severity,region,is_active)
        VALUES (?,?,?,?,?)""", ALERTS_SEED)

    # Seed admin user
    conn.execute("""INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)""",
                 ("Admin","admin@disaster.gov", hash_pw("admin123"), "admin"))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# HTML TEMPLATE
# ─────────────────────────────────────────────
BASE_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DisasterWatch Pro — Emergency Management Platform</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg-deep:      #0a0d14;
  --bg-card:      #111827;
  --bg-card2:     #1a2236;
  --border:       rgba(255,255,255,0.07);
  --accent:       #f97316;
  --accent2:      #ef4444;
  --accent3:      #3b82f6;
  --accent4:      #10b981;
  --accent5:      #8b5cf6;
  --text:         #f1f5f9;
  --text-muted:   #94a3b8;
  --sidebar-w:    260px;
  --header-h:     64px;
  --glow:         0 0 20px rgba(249,115,22,0.25);
  --glow-blue:    0 0 20px rgba(59,130,246,0.25);
}
[data-theme="light"] {
  --bg-deep:    #f0f4f8;
  --bg-card:    #ffffff;
  --bg-card2:   #f8fafc;
  --border:     rgba(0,0,0,0.08);
  --text:       #1e293b;
  --text-muted: #64748b;
}
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; font-family: 'Inter', sans-serif; background: var(--bg-deep); color: var(--text); overflow-x: hidden; }
::selection { background: rgba(249,115,22,0.3); }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ─── SIDEBAR ─── */
#sidebar {
  position: fixed; left: 0; top: 0; height: 100vh; width: var(--sidebar-w);
  background: linear-gradient(180deg, #0d1322 0%, #0a0d14 100%);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  z-index: 1000; transition: transform .3s cubic-bezier(.4,0,.2,1);
  overflow-y: auto; overflow-x: hidden;
}
#sidebar.collapsed { transform: translateX(calc(-1 * var(--sidebar-w))); }
.sidebar-logo {
  padding: 20px 18px;
  display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.sidebar-logo .logo-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
  box-shadow: var(--glow);
}
.sidebar-logo .logo-text { font-size: 14px; font-weight: 700; color: var(--text); line-height: 1.2; }
.sidebar-logo .logo-sub { font-size: 10px; color: var(--text-muted); font-weight: 400; }
.nav-section-label {
  font-size: 9px; font-weight: 700; letter-spacing: .12em;
  color: var(--text-muted); padding: 16px 18px 6px;
  text-transform: uppercase; flex-shrink: 0;
}
.nav-item { flex-shrink: 0; }
.nav-link {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 18px; color: var(--text-muted);
  text-decoration: none; font-size: 13px; font-weight: 500;
  border-radius: 0; transition: all .2s;
  position: relative; cursor: pointer;
}
.nav-link:hover { color: var(--text); background: rgba(255,255,255,0.04); }
.nav-link.active {
  color: var(--accent); background: rgba(249,115,22,0.08);
}
.nav-link.active::before {
  content:''; position: absolute; left: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 24px; background: var(--accent); border-radius: 0 2px 2px 0;
}
.nav-link i { width: 18px; text-align: center; font-size: 14px; flex-shrink: 0; }
.nav-badge {
  margin-left: auto; font-size: 9px; font-weight: 700;
  padding: 2px 6px; border-radius: 10px;
}

/* ─── HEADER ─── */
#header {
  position: fixed; top: 0; left: var(--sidebar-w); right: 0; height: var(--header-h);
  background: rgba(10,13,20,0.92); backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 24px;
  gap: 16px; z-index: 999;
  transition: left .3s cubic-bezier(.4,0,.2,1);
}
#header.expanded { left: 0; }
.header-title { font-size: 15px; font-weight: 600; color: var(--text); }
.header-subtitle { font-size: 11px; color: var(--text-muted); }
.header-spacer { flex: 1; }
.alert-ticker {
  flex: 1; overflow: hidden; position: relative; height: 32px;
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
  border-radius: 6px; display: flex; align-items: center;
}
.alert-ticker-label {
  padding: 0 10px; font-size: 9px; font-weight: 800; letter-spacing: .1em;
  color: var(--accent2); text-transform: uppercase; white-space: nowrap;
  border-right: 1px solid rgba(239,68,68,0.2); flex-shrink: 0;
}
.alert-ticker-scroll {
  overflow: hidden; flex: 1;
}
.alert-ticker-inner {
  display: flex; animation: ticker 30s linear infinite;
  white-space: nowrap;
}
.alert-ticker-item {
  padding: 0 30px; font-size: 11px; font-weight: 500; color: var(--text-muted);
  display: flex; align-items: center; gap: 6px; white-space: nowrap;
}
@keyframes ticker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
.hdr-btn {
  width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border);
  background: var(--bg-card); color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 14px; transition: all .2s; flex-shrink: 0;
}
.hdr-btn:hover { color: var(--text); border-color: var(--accent); }
.hdr-avatar {
  width: 36px; height: 36px; border-radius: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #fff; cursor: pointer; flex-shrink: 0;
}

/* ─── MAIN CONTENT ─── */
#main {
  margin-left: var(--sidebar-w); margin-top: var(--header-h);
  padding: 28px; min-height: calc(100vh - var(--header-h));
  transition: margin-left .3s cubic-bezier(.4,0,.2,1);
}
#main.expanded { margin-left: 0; }
.page { display: none; }
.page.active { display: block; }

/* ─── CARDS ─── */
.glass-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px; padding: 20px;
  transition: transform .2s, box-shadow .2s;
}
.glass-card:hover { transform: translateY(-1px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
.stat-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 14px; padding: 20px; position: relative; overflow: hidden;
  transition: transform .2s, box-shadow .2s;
}
.stat-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.stat-card.orange::before { background: linear-gradient(90deg, var(--accent), transparent); }
.stat-card.red::before    { background: linear-gradient(90deg, var(--accent2), transparent); }
.stat-card.blue::before   { background: linear-gradient(90deg, var(--accent3), transparent); }
.stat-card.green::before  { background: linear-gradient(90deg, var(--accent4), transparent); }
.stat-card.purple::before { background: linear-gradient(90deg, var(--accent5), transparent); }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 12px 40px rgba(0,0,0,0.4); }
.stat-icon {
  width: 46px; height: 46px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
  margin-bottom: 14px;
}
.stat-icon.orange { background: rgba(249,115,22,0.12); }
.stat-icon.red    { background: rgba(239,68,68,0.12); }
.stat-icon.blue   { background: rgba(59,130,246,0.12); }
.stat-icon.green  { background: rgba(16,185,129,0.12); }
.stat-icon.purple { background: rgba(139,92,246,0.12); }
.stat-value { font-size: 28px; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-muted); font-weight: 500; }
.stat-delta { font-size: 11px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }
.delta-up   { color: var(--accent2); }
.delta-down { color: var(--accent4); }

/* ─── SECTION HEADERS ─── */
.section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.section-title { font-size: 17px; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 8px; }
.section-title i { color: var(--accent); font-size: 16px; }

/* ─── BADGES / PILLS ─── */
.pill {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600;
}
.pill-red    { background: rgba(239,68,68,0.12);   color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.pill-orange { background: rgba(249,115,22,0.12); color: #f97316; border: 1px solid rgba(249,115,22,0.2); }
.pill-yellow { background: rgba(234,179,8,0.12);  color: #eab308; border: 1px solid rgba(234,179,8,0.2); }
.pill-green  { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.2); }
.pill-blue   { background: rgba(59,130,246,0.12);  color: #3b82f6; border: 1px solid rgba(59,130,246,0.2); }
.pill-purple { background: rgba(139,92,246,0.12); color: #8b5cf6; border: 1px solid rgba(139,92,246,0.2); }
.pill-gray   { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.15); }

/* ─── TABLE ─── */
.dm-table { width: 100%; border-collapse: collapse; }
.dm-table th {
  font-size: 10px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  color: var(--text-muted); padding: 10px 14px; border-bottom: 1px solid var(--border);
  text-align: left; white-space: nowrap;
}
.dm-table td { padding: 12px 14px; border-bottom: 1px solid var(--border); font-size: 13px; vertical-align: middle; }
.dm-table tr:last-child td { border-bottom: none; }
.dm-table tbody tr { transition: background .15s; }
.dm-table tbody tr:hover { background: rgba(255,255,255,0.025); }

/* ─── MAP ─── */
#map { height: 500px; border-radius: 14px; overflow: hidden; border: 1px solid var(--border); }

/* ─── CHAT ─── */
.chat-container {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; height: 550px;
}
.chat-header {
  padding: 16px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
  background: linear-gradient(90deg, rgba(249,115,22,0.08), transparent);
}
.chat-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display: flex; align-items: center; justify-content: center; font-size: 18px;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(249,115,22,0.4)} 50%{box-shadow:0 0 0 8px rgba(249,115,22,0)} }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.msg-user { align-self: flex-end; }
.msg-bot  { align-self: flex-start; }
.msg-bubble {
  max-width: 75%; padding: 12px 16px; border-radius: 14px; font-size: 13px; line-height: 1.6;
}
.msg-user .msg-bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 4px; }
.msg-bot .msg-bubble  { background: var(--bg-card2); border: 1px solid var(--border); border-bottom-left-radius: 4px; }
.chat-input-row { padding: 14px 16px; border-top: 1px solid var(--border); display: flex; gap: 10px; }
.chat-input {
  flex: 1; background: var(--bg-card2); border: 1px solid var(--border);
  color: var(--text); padding: 10px 14px; border-radius: 8px; font-size: 13px; outline: none;
  font-family: 'Inter', sans-serif;
}
.chat-input:focus { border-color: var(--accent); }
.chat-send {
  padding: 10px 18px; background: var(--accent); border: none; color: #fff;
  border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: opacity .2s;
}
.chat-send:hover { opacity: .85; }
.typing-indicator { display: flex; gap: 4px; align-items: center; padding: 8px 12px; }
.typing-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
  animation: typing-bounce .8s infinite ease-in-out;
}
.typing-dot:nth-child(2) { animation-delay: .15s; }
.typing-dot:nth-child(3) { animation-delay: .3s; }
@keyframes typing-bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

/* ─── RISK GAUGE ─── */
.risk-gauge-wrap { text-align: center; padding: 20px 0; }
.risk-bar { height: 20px; border-radius: 10px; overflow: hidden; background: var(--bg-card2); border: 1px solid var(--border); }
.risk-fill { height: 100%; border-radius: 10px; transition: width .8s cubic-bezier(.4,0,.2,1); }

/* ─── ENCYCLOPEDIA ─── */
.enc-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 18px; cursor: pointer; transition: all .2s; text-align: center;
  position: relative; overflow: hidden;
}
.enc-card::after {
  content: ''; position: absolute; inset: 0; opacity: 0;
  background: radial-gradient(circle at center, rgba(249,115,22,0.1), transparent 70%);
  transition: opacity .3s;
}
.enc-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.enc-card:hover::after { opacity: 1; }
.enc-icon { font-size: 36px; margin-bottom: 10px; display: block; }
.enc-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.enc-cat  { font-size: 11px; color: var(--text-muted); }

/* ─── DETAIL PANEL ─── */
.detail-panel {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
  padding: 24px; display: none;
}
.detail-panel.open { display: block; animation: slideIn .3s ease; }
@keyframes slideIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.detail-section {
  margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border);
}
.detail-section:last-child { border-bottom: none; margin-bottom: 0; }
.detail-section h6 { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: var(--accent); margin-bottom: 10px; }
.detail-section p  { font-size: 13px; color: var(--text-muted); line-height: 1.7; }

/* ─── ALERT BANNER ─── */
.alert-banner {
  border-radius: 10px; padding: 14px 18px;
  border-left: 4px solid; margin-bottom: 12px;
  display: flex; align-items: flex-start; gap: 12px;
}
.alert-banner.extreme { border-color: #ef4444; background: rgba(239,68,68,0.08); }
.alert-banner.high    { border-color: #f97316; background: rgba(249,115,22,0.08); }
.alert-banner.medium  { border-color: #eab308; background: rgba(234,179,8,0.08); }
.alert-banner.low     { border-color: #10b981; background: rgba(16,185,129,0.08); }
.alert-title  { font-size: 13px; font-weight: 700; margin-bottom: 4px; }
.alert-msg    { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
.alert-time   { font-size: 10px; color: var(--text-muted); margin-top: 6px; font-family: 'JetBrains Mono', monospace; }

/* ─── CHECKLIST ─── */
.check-item {
  display: flex; align-items: flex-start; gap: 12px; padding: 12px;
  background: var(--bg-card2); border-radius: 8px; margin-bottom: 8px;
  border: 1px solid var(--border);
}
.check-item input[type=checkbox] { width: 16px; height: 16px; margin-top: 2px; accent-color: var(--accent4); flex-shrink: 0; }
.check-item label { font-size: 13px; cursor: pointer; flex: 1; }
.check-item label span { font-size: 11px; color: var(--text-muted); display: block; margin-top: 2px; }

/* ─── CONTACT CARD ─── */
.contact-card {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; transition: all .2s;
}
.contact-card:hover { border-color: var(--accent3); transform: translateY(-1px); }
.contact-dept { font-size: 13px; font-weight: 700; margin-bottom: 6px; }
.contact-phone { font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono', monospace; color: var(--accent); margin-bottom: 8px; }
.call-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600;
  background: linear-gradient(135deg, var(--accent4), #059669);
  color: #fff; text-decoration: none; cursor: pointer;
  border: none; transition: opacity .2s;
}
.call-btn:hover { opacity: .85; color: #fff; }

/* ─── SHELTER CARD ─── */
.shelter-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.shelter-name { font-size: 14px; font-weight: 700; margin-bottom: 4px; }
.shelter-addr { font-size: 12px; color: var(--text-muted); margin-bottom: 10px; }
.capacity-bar { height: 6px; border-radius: 3px; background: var(--bg-card2); overflow: hidden; margin: 6px 0; }
.capacity-fill { height: 100%; border-radius: 3px; }

/* ─── FORM ─── */
.dm-input, .dm-select, .dm-textarea {
  width: 100%; background: var(--bg-card2); border: 1px solid var(--border);
  color: var(--text); padding: 10px 14px; border-radius: 8px; font-size: 13px;
  font-family: 'Inter', sans-serif; outline: none; transition: border-color .2s;
}
.dm-input:focus, .dm-select:focus, .dm-textarea:focus { border-color: var(--accent); }
.dm-select option { background: var(--bg-card); }
.dm-label { font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; display: block; text-transform: uppercase; letter-spacing: .05em; }
.dm-btn {
  padding: 10px 20px; border-radius: 8px; border: none; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all .2s; display: inline-flex; align-items: center; gap: 8px;
}
.dm-btn-primary  { background: var(--accent); color: #fff; }
.dm-btn-primary:hover { opacity: .88; }
.dm-btn-danger   { background: var(--accent2); color: #fff; }
.dm-btn-success  { background: var(--accent4); color: #fff; }
.dm-btn-outline  { background: transparent; border: 1px solid var(--border); color: var(--text); }
.dm-btn-outline:hover { border-color: var(--accent); color: var(--accent); }

/* ─── MINI PROGRESS ─── */
.mini-prog { height: 4px; background: var(--bg-card2); border-radius: 2px; overflow: hidden; }
.mini-prog-fill { height: 100%; border-radius: 2px; }

/* ─── ACCORDION ─── */
.dm-acc { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-bottom: 8px; }
.dm-acc-header {
  padding: 14px 18px; background: var(--bg-card); cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
  font-size: 13px; font-weight: 600; transition: background .15s;
}
.dm-acc-header:hover { background: var(--bg-card2); }
.dm-acc-body { display: none; padding: 16px 18px; background: var(--bg-card2); border-top: 1px solid var(--border); font-size: 13px; line-height: 1.7; color: var(--text-muted); }
.dm-acc-body.open { display: block; }

/* ─── MISC ─── */
.page-header { margin-bottom: 28px; }
.page-header h2 { font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.page-header p  { font-size: 13px; color: var(--text-muted); }
.divider { height: 1px; background: var(--border); margin: 24px 0; }
.text-orange { color: var(--accent); }
.text-red    { color: var(--accent2); }
.text-blue   { color: var(--accent3); }
.text-green  { color: var(--accent4); }
.text-purple { color: var(--accent5); }
.text-muted  { color: var(--text-muted); }
.fw-800 { font-weight: 800; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; }
.dm-toast {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 18px; font-size: 13px; display: flex; align-items: center; gap: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.5); animation: toast-in .3s ease;
  min-width: 260px;
}
@keyframes toast-in { from{opacity:0;transform:translateX(30px)} to{opacity:1;transform:translateX(0)} }
.tooltip-text { font-size: 11px; }

/* ─── LOADING ─── */
.skeleton { background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card2) 50%, var(--bg-card) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 6px; }
@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ─── MOBILE ─── */
@media (max-width: 768px) {
  :root { --sidebar-w: 240px; }
  #sidebar { transform: translateX(calc(-1 * var(--sidebar-w))); }
  #sidebar.mobile-open { transform: translateX(0); }
  #header { left: 0 !important; }
  #main { margin-left: 0 !important; padding: 16px; }
  .alert-ticker { display: none; }
}
</style>
</head>
<body>

<!-- ████████ SIDEBAR ████████ -->
<nav id="sidebar">
  <div class="sidebar-logo">
    <div class="logo-icon">🌍</div>
    <div>
      <div class="logo-text">DisasterWatch</div>
      <div class="logo-sub">Emergency Response Platform</div>
    </div>
  </div>

  <div class="nav-section-label">Overview</div>
  <div class="nav-item">
    <a class="nav-link active" onclick="showPage('dashboard')">
      <i class="fas fa-gauge-high"></i> Dashboard
      <span class="nav-badge pill-red pill" id="badge-alerts">5</span>
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('encyclopedia')">
      <i class="fas fa-book-open"></i> Disaster Encyclopedia
    </a>
  </div>

  <div class="nav-section-label">Monitoring</div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('events')">
      <i class="fas fa-satellite-dish"></i> Live Disaster Events
      <span class="nav-badge pill-orange pill">{{event_count}}</span>
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('risk')">
      <i class="fas fa-triangle-exclamation"></i> Risk Assessment
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('alerts')">
      <i class="fas fa-bell"></i> Active Alerts
      <span class="nav-badge pill-red pill">{{alert_count}}</span>
    </a>
  </div>

  <div class="nav-section-label">Resources</div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('preparedness')">
      <i class="fas fa-kit-medical"></i> Preparedness Center
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('safety')">
      <i class="fas fa-shield-halved"></i> Safety Guides
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('contacts')">
      <i class="fas fa-phone-volume"></i> Emergency Contacts
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('shelters')">
      <i class="fas fa-house-chimney-medical"></i> Relief Shelters
    </a>
  </div>

  <div class="nav-section-label">Intelligence</div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('map')">
      <i class="fas fa-map-location-dot"></i> Interactive Map
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('statistics')">
      <i class="fas fa-chart-bar"></i> Statistics
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('reports')">
      <i class="fas fa-file-lines"></i> Reports
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('ai')">
      <i class="fas fa-robot"></i> AI Assistant
      <span class="nav-badge pill-purple pill" style="font-size:8px">AI</span>
    </a>
  </div>

  <div class="nav-section-label">Admin</div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('admin')">
      <i class="fas fa-sliders"></i> Admin Panel
    </a>
  </div>
  <div class="nav-item">
    <a class="nav-link" onclick="showPage('settings')">
      <i class="fas fa-gear"></i> Settings
    </a>
  </div>
</nav>

<!-- ████████ HEADER ████████ -->
<header id="header">
  <button class="hdr-btn" onclick="toggleSidebar()" id="sidebar-toggle" title="Toggle Sidebar">
    <i class="fas fa-bars"></i>
  </button>
  <div>
    <div class="header-title" id="page-title">Dashboard</div>
    <div class="header-subtitle" id="page-sub">Real-time disaster monitoring & response coordination</div>
  </div>
  <div class="alert-ticker ms-3 d-none d-md-flex" style="max-width:380px">
    <span class="alert-ticker-label">⚡ ALERTS</span>
    <div class="alert-ticker-scroll">
      <div class="alert-ticker-inner" id="ticker-content">
        {{ticker_html}}
        {{ticker_html}}
      </div>
    </div>
  </div>
  <div class="header-spacer"></div>
  <div class="d-flex align-items-center gap-2">
    <button class="hdr-btn" onclick="toggleTheme()" title="Toggle Theme" id="theme-btn"><i class="fas fa-moon"></i></button>
    <button class="hdr-btn" onclick="showPage('alerts')" title="Alerts">
      <i class="fas fa-bell text-orange"></i>
    </button>
    <div class="hdr-avatar" title="Admin">A</div>
  </div>
</header>

<!-- ████████ MAIN CONTENT ████████ -->
<main id="main">

<!-- ══════════════════════════════════════
     PAGE: DASHBOARD
══════════════════════════════════════ -->
<div id="page-dashboard" class="page active">
  <div class="page-header">
    <h2>🌍 Emergency Operations Dashboard</h2>
    <p>Real-time situational awareness and disaster intelligence platform</p>
  </div>

  <!-- KPI STATS -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card orange">
        <div class="stat-icon orange">🌋</div>
        <div class="stat-value text-orange">{{disaster_count}}</div>
        <div class="stat-label">Disaster Types</div>
        <div class="stat-delta"><i class="fas fa-database text-muted"></i> <span class="text-muted">In Encyclopedia</span></div>
      </div>
    </div>
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card red">
        <div class="stat-icon red">📡</div>
        <div class="stat-value text-red">{{active_events}}</div>
        <div class="stat-label">Active Events</div>
        <div class="stat-delta delta-up"><i class="fas fa-arrow-up"></i> 3 this week</div>
      </div>
    </div>
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card blue">
        <div class="stat-icon blue">👥</div>
        <div class="stat-value text-blue">{{affected_m}}M</div>
        <div class="stat-label">Affected Population</div>
        <div class="stat-delta delta-up"><i class="fas fa-arrow-up"></i> Global impact</div>
      </div>
    </div>
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card purple">
        <div class="stat-icon purple">🗺️</div>
        <div class="stat-value text-purple">{{countries}}</div>
        <div class="stat-label">Countries Affected</div>
        <div class="stat-delta"><i class="fas fa-globe text-muted"></i> <span class="text-muted">Worldwide</span></div>
      </div>
    </div>
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card green">
        <div class="stat-icon green">🏥</div>
        <div class="stat-value text-green">{{shelter_count}}</div>
        <div class="stat-label">Active Shelters</div>
        <div class="stat-delta delta-down"><i class="fas fa-arrow-up"></i> Capacity available</div>
      </div>
    </div>
    <div class="col-6 col-md-4 col-lg-2">
      <div class="stat-card orange">
        <div class="stat-icon orange">📞</div>
        <div class="stat-value text-orange">{{contact_count}}</div>
        <div class="stat-label">Emergency Contacts</div>
        <div class="stat-delta delta-down"><i class="fas fa-check text-green"></i> All operational</div>
      </div>
    </div>
  </div>

  <!-- CHARTS ROW -->
  <div class="row g-3 mb-4">
    <div class="col-lg-8">
      <div class="glass-card">
        <div class="section-header">
          <span class="section-title"><i class="fas fa-chart-line"></i> Disaster Events — Monthly Trend</span>
          <div class="d-flex gap-2">
            <span class="pill pill-gray">2024</span>
            <span class="pill pill-orange">2025</span>
          </div>
        </div>
        <canvas id="chart-trend" height="200"></canvas>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card">
        <div class="section-header">
          <span class="section-title"><i class="fas fa-chart-pie"></i> By Category</span>
        </div>
        <canvas id="chart-category" height="200"></canvas>
      </div>
    </div>
  </div>

  <!-- RECENT EVENTS + ALERTS -->
  <div class="row g-3 mb-4">
    <div class="col-lg-8">
      <div class="glass-card">
        <div class="section-header">
          <span class="section-title"><i class="fas fa-satellite-dish"></i> Recent Disaster Events</span>
          <button class="dm-btn dm-btn-outline" onclick="showPage('events')" style="padding:6px 12px;font-size:11px;">View All</button>
        </div>
        <div class="table-responsive">
          <table class="dm-table">
            <thead>
              <tr><th>Event</th><th>Location</th><th>Severity</th><th>Affected</th><th>Status</th><th>Date</th></tr>
            </thead>
            <tbody>
              {% for e in recent_events %}
              <tr>
                <td><span class="fw-800">{{e.title}}</span></td>
                <td><i class="fas fa-map-pin text-muted me-1" style="font-size:11px"></i>{{e.location}}</td>
                <td>
                  {% if e.severity == 'Extreme' %}<span class="pill pill-red">{{e.severity}}</span>
                  {% elif e.severity == 'High' %}<span class="pill pill-orange">{{e.severity}}</span>
                  {% elif e.severity == 'Medium' %}<span class="pill pill-yellow">{{e.severity}}</span>
                  {% else %}<span class="pill pill-green">{{e.severity}}</span>{% endif %}
                </td>
                <td class="font-mono text-blue">{{"{:,}".format(e.affected_population)}}</td>
                <td>
                  {% if e.status == 'Active' %}<span class="pill pill-red">● Active</span>
                  {% else %}<span class="pill pill-green">✓ Resolved</span>{% endif %}
                </td>
                <td class="text-muted font-mono" style="font-size:11px">{{e.reported_date}}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card">
        <div class="section-header">
          <span class="section-title"><i class="fas fa-bell"></i> Active Alerts</span>
          <button class="dm-btn dm-btn-outline" onclick="showPage('alerts')" style="padding:6px 12px;font-size:11px;">All</button>
        </div>
        {% for a in active_alerts %}
        <div class="alert-banner {{a.severity.lower()}}">
          <div>
            <div class="alert-title">{{a.title}}</div>
            <div class="alert-msg">{{a.message[:80]}}...</div>
            <div class="alert-time">📍 {{a.region}}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- SEVERITY BREAKDOWN -->
  <div class="row g-3">
    <div class="col-md-3">
      <div class="glass-card text-center">
        <div style="font-size:28px;font-weight:800;color:#ef4444" class="font-mono">{{severity_counts.extreme}}</div>
        <div class="text-muted" style="font-size:12px;margin-top:4px">Extreme Events</div>
        <div class="mini-prog mt-2"><div class="mini-prog-fill" style="width:{{severity_pct.extreme}}%;background:#ef4444"></div></div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="glass-card text-center">
        <div style="font-size:28px;font-weight:800;color:#f97316" class="font-mono">{{severity_counts.high}}</div>
        <div class="text-muted" style="font-size:12px;margin-top:4px">High Severity</div>
        <div class="mini-prog mt-2"><div class="mini-prog-fill" style="width:{{severity_pct.high}}%;background:#f97316"></div></div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="glass-card text-center">
        <div style="font-size:28px;font-weight:800;color:#eab308" class="font-mono">{{severity_counts.medium}}</div>
        <div class="text-muted" style="font-size:12px;margin-top:4px">Medium Severity</div>
        <div class="mini-prog mt-2"><div class="mini-prog-fill" style="width:{{severity_pct.medium}}%;background:#eab308"></div></div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="glass-card text-center">
        <div style="font-size:28px;font-weight:800;color:#10b981" class="font-mono">{{severity_counts.low}}</div>
        <div class="text-muted" style="font-size:12px;margin-top:4px">Low Severity</div>
        <div class="mini-prog mt-2"><div class="mini-prog-fill" style="width:{{severity_pct.low}}%;background:#10b981"></div></div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: ENCYCLOPEDIA
══════════════════════════════════════ -->
<div id="page-encyclopedia" class="page">
  <div class="page-header">
    <h2>📖 Disaster Encyclopedia</h2>
    <p>Comprehensive knowledge base covering all major disaster types worldwide</p>
  </div>
  <div class="row g-3 mb-4" id="enc-grid">
    {% for d in disasters %}
    <div class="col-6 col-md-4 col-lg-3 col-xl-2">
      <div class="enc-card" onclick="loadDisaster({{d.id}})">
        <span class="enc-icon">{{d.icon}}</span>
        <div class="enc-name">{{d.name}}</div>
        <div class="enc-cat"><span class="pill pill-gray">{{d.category}}</span></div>
      </div>
    </div>
    {% endfor %}
  </div>
  <div class="detail-panel" id="enc-detail">
    <div id="enc-detail-content"></div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: EVENTS
══════════════════════════════════════ -->
<div id="page-events" class="page">
  <div class="page-header d-flex align-items-start justify-content-between flex-wrap gap-2">
    <div>
      <h2>📡 Live Disaster Events</h2>
      <p>Real-time tracking of disaster events across the globe</p>
    </div>
    <div class="d-flex gap-2 flex-wrap">
      <select class="dm-select" style="width:auto" onchange="filterEvents(this.value)" id="ev-filter">
        <option value="">All Severity</option>
        <option value="Extreme">Extreme</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>
      <select class="dm-select" style="width:auto" onchange="filterEvStatus(this.value)">
        <option value="">All Status</option>
        <option value="Active">Active</option>
        <option value="Resolved">Resolved</option>
      </select>
    </div>
  </div>
  <div class="glass-card">
    <div class="table-responsive">
      <table class="dm-table" id="events-table">
        <thead>
          <tr><th>#</th><th>Event</th><th>Location</th><th>Country</th><th>Severity</th><th>Affected</th><th>Deaths</th><th>Status</th><th>Date</th></tr>
        </thead>
        <tbody>
          {% for e in all_events %}
          <tr class="ev-row" data-severity="{{e.severity}}" data-status="{{e.status}}">
            <td class="text-muted font-mono" style="font-size:11px">{{e.id}}</td>
            <td><span class="fw-800">{{e.title}}</span></td>
            <td>{{e.location}}</td>
            <td><span class="pill pill-gray">{{e.country}}</span></td>
            <td>
              {% if e.severity=='Extreme'%}<span class="pill pill-red">{{e.severity}}</span>
              {% elif e.severity=='High'%}<span class="pill pill-orange">{{e.severity}}</span>
              {% elif e.severity=='Medium'%}<span class="pill pill-yellow">{{e.severity}}</span>
              {% else %}<span class="pill pill-green">{{e.severity}}</span>{% endif %}
            </td>
            <td class="font-mono text-blue">{{"{:,}".format(e.affected_population)}}</td>
            <td class="font-mono text-red">{{"{:,}".format(e.deaths)}}</td>
            <td>{% if e.status=='Active'%}<span class="pill pill-red">● {{e.status}}</span>
                {% else %}<span class="pill pill-green">✓ {{e.status}}</span>{% endif %}</td>
            <td class="text-muted font-mono" style="font-size:11px">{{e.reported_date}}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: ALERTS
══════════════════════════════════════ -->
<div id="page-alerts" class="page">
  <div class="page-header">
    <h2>🔔 Active Alerts & Warnings</h2>
    <p>Current disaster alerts, warnings and advisories</p>
  </div>
  <div class="row g-3">
    <div class="col-lg-8">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-bell"></i> Current Active Alerts</div>
        {% for a in all_alerts %}
        <div class="alert-banner {{a.severity.lower()}} mb-3">
          <div style="font-size:20px">
            {% if a.severity=='Extreme'%}🔴{% elif a.severity=='High'%}🟠{% elif a.severity=='Medium'%}🟡{% else %}🟢{% endif %}
          </div>
          <div>
            <div class="alert-title">{{a.title}}</div>
            <div class="alert-msg">{{a.message}}</div>
            <div class="alert-time mt-1">📍 {{a.region}} &nbsp;·&nbsp; 🕒 {{a.created_at[:10]}}</div>
          </div>
          <div class="ms-auto">
            {% if a.severity=='Extreme'%}<span class="pill pill-red">EXTREME</span>
            {% elif a.severity=='High'%}<span class="pill pill-orange">HIGH</span>
            {% elif a.severity=='Medium'%}<span class="pill pill-yellow">MEDIUM</span>
            {% else %}<span class="pill pill-green">LOW</span>{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-plus-circle"></i> Add New Alert</div>
        <div class="mb-3">
          <label class="dm-label">Alert Title</label>
          <input class="dm-input" id="new-alert-title" placeholder="e.g. Flood Warning">
        </div>
        <div class="mb-3">
          <label class="dm-label">Message</label>
          <textarea class="dm-textarea" id="new-alert-msg" rows="3" placeholder="Alert details..."></textarea>
        </div>
        <div class="mb-3">
          <label class="dm-label">Severity</label>
          <select class="dm-select" id="new-alert-sev">
            <option>Extreme</option><option>High</option><option>Medium</option><option>Low</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Region</label>
          <input class="dm-input" id="new-alert-region" placeholder="e.g. South India">
        </div>
        <button class="dm-btn dm-btn-primary w-100" onclick="addAlert()"><i class="fas fa-paper-plane"></i> Broadcast Alert</button>
      </div>
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-chart-pie"></i> Alert Distribution</div>
        <canvas id="chart-alerts" height="180"></canvas>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: RISK ASSESSMENT
══════════════════════════════════════ -->
<div id="page-risk" class="page">
  <div class="page-header">
    <h2>⚠️ Risk Assessment Engine</h2>
    <p>Multi-factor disaster risk analysis and scoring system</p>
  </div>
  <div class="row g-3">
    <div class="col-lg-5">
      <div class="glass-card">
        <div class="section-title mb-4"><i class="fas fa-sliders"></i> Risk Parameters</div>
        <div class="mb-3">
          <label class="dm-label">Location Type</label>
          <select class="dm-select" id="r-location">
            <option value="5">Coastal (High Risk)</option>
            <option value="4">River Flood Plain</option>
            <option value="3">Hilly / Mountainous</option>
            <option value="2">Semi-Arid Zone</option>
            <option value="1">Plains (Lower Risk)</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Population Density</label>
          <select class="dm-select" id="r-pop">
            <option value="5">Very High (>10,000/km²)</option>
            <option value="4">High (5,000-10,000/km²)</option>
            <option value="3">Medium (1,000-5,000/km²)</option>
            <option value="2">Low (100-1,000/km²)</option>
            <option value="1">Very Low (<100/km²)</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Annual Rainfall</label>
          <select class="dm-select" id="r-rain">
            <option value="5">Very High (>3000mm)</option>
            <option value="4">High (2000-3000mm)</option>
            <option value="3">Moderate (1000-2000mm)</option>
            <option value="2">Low (500-1000mm)</option>
            <option value="1">Arid (<500mm)</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Seismic Zone</label>
          <select class="dm-select" id="r-seismic">
            <option value="5">Zone V (Severe)</option>
            <option value="4">Zone IV (High)</option>
            <option value="3">Zone III (Moderate)</option>
            <option value="2">Zone II (Low)</option>
            <option value="1">Zone I (Stable)</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Forest Coverage</label>
          <select class="dm-select" id="r-forest">
            <option value="1">Dense Forest (Low Fire Risk)</option>
            <option value="3">Moderate Forest</option>
            <option value="5">Dry Scrubland (High Fire Risk)</option>
            <option value="2">Mixed Vegetation</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">River Proximity</label>
          <select class="dm-select" id="r-river">
            <option value="5">Within 1km of Major River</option>
            <option value="4">1-5km from Major River</option>
            <option value="3">5-20km from River</option>
            <option value="2">20-50km from River</option>
            <option value="1">No nearby river</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="dm-label">Industrial Areas Nearby</label>
          <select class="dm-select" id="r-industrial">
            <option value="5">Heavy Industry (Chemical/Nuclear)</option>
            <option value="4">Industrial Zone (General)</option>
            <option value="3">Light Industry</option>
            <option value="1">No industry</option>
          </select>
        </div>
        <button class="dm-btn dm-btn-primary w-100" onclick="calcRisk()"><i class="fas fa-calculator"></i> Calculate Risk Score</button>
      </div>
    </div>
    <div class="col-lg-7">
      <div class="glass-card mb-3" id="risk-result" style="display:none">
        <div class="text-center mb-4">
          <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:8px">Risk Score</div>
          <div id="risk-score-val" style="font-size:72px;font-weight:900;line-height:1;font-family:'JetBrains Mono',monospace">0</div>
          <div id="risk-level" style="font-size:20px;font-weight:700;margin-top:6px"></div>
        </div>
        <div class="mb-3">
          <div class="d-flex justify-content-between mb-1" style="font-size:11px">
            <span class="text-muted">Risk Level</span>
            <span id="risk-pct" class="font-mono">0%</span>
          </div>
          <div class="risk-bar">
            <div class="risk-fill" id="risk-fill" style="width:0%;background:#10b981"></div>
          </div>
          <div class="d-flex justify-content-between mt-1" style="font-size:10px;color:var(--text-muted)">
            <span>Low</span><span>Medium</span><span>High</span><span>Extreme</span>
          </div>
        </div>
        <div id="risk-breakdown" class="row g-2 mt-2"></div>
      </div>
      <div class="glass-card" id="risk-recommendations" style="display:none">
        <div class="section-title mb-3"><i class="fas fa-lightbulb"></i> Recommendations</div>
        <div id="risk-rec-content"></div>
      </div>
      <div class="glass-card mt-3">
        <div class="section-title mb-3"><i class="fas fa-info-circle"></i> Risk Level Guide</div>
        <div class="row g-2">
          <div class="col-6"><div class="p-3 rounded" style="background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2)"><div class="fw-800 text-green">LOW</div><div class="text-muted" style="font-size:11px">Score: 1–25<br>Minimal immediate risk. Standard preparedness.</div></div></div>
          <div class="col-6"><div class="p-3 rounded" style="background:rgba(234,179,8,.08);border:1px solid rgba(234,179,8,.2)"><div class="fw-800" style="color:#eab308">MEDIUM</div><div class="text-muted" style="font-size:11px">Score: 26–50<br>Moderate risk. Enhanced monitoring needed.</div></div></div>
          <div class="col-6"><div class="p-3 rounded" style="background:rgba(249,115,22,.08);border:1px solid rgba(249,115,22,.2)"><div class="fw-800 text-orange">HIGH</div><div class="text-muted" style="font-size:11px">Score: 51–75<br>Significant risk. Active response required.</div></div></div>
          <div class="col-6"><div class="p-3 rounded" style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2)"><div class="fw-800 text-red">EXTREME</div><div class="text-muted" style="font-size:11px">Score: 76–100<br>Critical risk. Immediate action needed.</div></div></div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: PREPAREDNESS
══════════════════════════════════════ -->
<div id="page-preparedness" class="page">
  <div class="page-header">
    <h2>🧰 Preparedness Center</h2>
    <p>Comprehensive checklists and guides to prepare for all disaster types</p>
  </div>
  <div class="row g-3 mb-4">
    <div class="col-md-4">
      <div class="glass-card" style="position:sticky;top:80px">
        <div class="section-title mb-3"><i class="fas fa-list-check"></i> Select Disaster Type</div>
        {% for dtype in checklist_types %}
        <button class="dm-btn dm-btn-outline w-100 mb-2 text-start" onclick="loadChecklist('{{dtype}}')">
          <i class="fas fa-chevron-right text-orange" style="font-size:10px"></i> {{dtype}} Kit
        </button>
        {% endfor %}
      </div>
    </div>
    <div class="col-md-8">
      <div id="checklist-container" class="glass-card">
        <div class="text-center py-5 text-muted">
          <i class="fas fa-kit-medical" style="font-size:48px;opacity:.2;display:block;margin-bottom:16px"></i>
          <p>Select a disaster type to view the preparedness checklist</p>
        </div>
      </div>
    </div>
  </div>
  <div class="row g-3">
    <div class="col-md-6">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-bag-shopping"></i> Emergency Go-Bag Essentials</div>
        <div class="check-item"><input type="checkbox" id="g1"><label for="g1">Water (2L per person) <span>Sealed bottles, replace every 6 months</span></label></div>
        <div class="check-item"><input type="checkbox" id="g2"><label for="g2">Non-perishable snacks <span>Energy bars, dry fruits, crackers</span></label></div>
        <div class="check-item"><input type="checkbox" id="g3"><label for="g3">First aid kit <span>Complete kit with manual</span></label></div>
        <div class="check-item"><input type="checkbox" id="g4"><label for="g4">Flashlight + extra batteries <span>LED preferred, check monthly</span></label></div>
        <div class="check-item"><input type="checkbox" id="g5"><label for="g5">Whistle & multi-tool <span>Signal for help, multipurpose tool</span></label></div>
        <div class="check-item"><input type="checkbox" id="g6"><label for="g6">Important documents (copies) <span>ID, insurance, bank info in waterproof bag</span></label></div>
        <div class="check-item"><input type="checkbox" id="g7"><label for="g7">Emergency cash <span>Small bills, ATMs may be offline</span></label></div>
        <div class="check-item"><input type="checkbox" id="g8"><label for="g8">Phone charger + power bank <span>Fully charged power bank</span></label></div>
        <div class="check-item"><input type="checkbox" id="g9"><label for="g9">Warm blanket / emergency foil blanket <span>Space blanket is compact</span></label></div>
        <div class="check-item"><input type="checkbox" id="g10"><label for="g10">N95 Masks (pack of 10) <span>For smoke, dust, biological hazards</span></label></div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-house-flood-water"></i> Family Emergency Plan</div>
        <div class="dm-acc">
          <div class="dm-acc-header" onclick="toggleAcc(this)">
            <span>📍 Establish Meeting Points</span><i class="fas fa-chevron-down"></i>
          </div>
          <div class="dm-acc-body">Designate two meeting points: one near your home (e.g., front yard tree) and one away from neighborhood (e.g., school parking lot). Ensure all family members know both locations.</div>
        </div>
        <div class="dm-acc">
          <div class="dm-acc-header" onclick="toggleAcc(this)">
            <span>📞 Emergency Contact Tree</span><i class="fas fa-chevron-down"></i>
          </div>
          <div class="dm-acc-body">Create a list of emergency contacts. Include an out-of-state contact who can relay information between family members. Print and laminate this list.</div>
        </div>
        <div class="dm-acc">
          <div class="dm-acc-header" onclick="toggleAcc(this)">
            <span>🏃 Evacuation Routes</span><i class="fas fa-chevron-down"></i>
          </div>
          <div class="dm-acc-body">Identify at least 2 evacuation routes from your home and neighborhood. Practice driving/walking these routes with the family. Know your local evacuation zones.</div>
        </div>
        <div class="dm-acc">
          <div class="dm-acc-header" onclick="toggleAcc(this)">
            <span>🏥 Medical Information</span><i class="fas fa-chevron-down"></i>
          </div>
          <div class="dm-acc-body">Compile medical records, prescription information, and doctor contacts. Ensure adequate supply of all medications. Include special needs information for children or elderly.</div>
        </div>
        <div class="dm-acc">
          <div class="dm-acc-header" onclick="toggleAcc(this)">
            <span>🐾 Pet Emergency Plan</span><i class="fas fa-chevron-down"></i>
          </div>
          <div class="dm-acc-body">Prepare a pet emergency kit with food, water, medications, vet records, and carrier. Know which shelters accept pets. Ensure your pet has ID tags and microchip.</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: SAFETY GUIDES
══════════════════════════════════════ -->
<div id="page-safety" class="page">
  <div class="page-header">
    <h2>🛡️ Safety Guides</h2>
    <p>Step-by-step safety protocols for every disaster type</p>
  </div>
  <div class="row g-3 mb-3">
    <div class="col-12">
      <div class="d-flex gap-2 flex-wrap">
        {% for d in disasters[:8] %}
        <button class="dm-btn dm-btn-outline" onclick="loadSafetyGuide({{d.id}},'{{d.name}}','{{d.icon}}')">{{d.icon}} {{d.name}}</button>
        {% endfor %}
      </div>
    </div>
  </div>
  <div id="safety-content">
    <div class="row g-3">
      {% for d in disasters[:4] %}
      <div class="col-md-6">
        <div class="glass-card">
          <div class="section-title mb-3">{{d.icon}} {{d.name}} — Safety Protocol</div>
          <div class="row g-2">
            <div class="col-12">
              <div class="p-3 rounded mb-2" style="background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.15)">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#3b82f6;margin-bottom:6px">⏩ Before Disaster</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.6">{{d.safety_measures[:120]}}...</div>
              </div>
            </div>
            <div class="col-12">
              <div class="p-3 rounded mb-2" style="background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.15)">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#ef4444;margin-bottom:6px">🚨 During Disaster</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.6">{{d.first_aid[:120]}}...</div>
              </div>
            </div>
            <div class="col-12">
              <div class="p-3 rounded" style="background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.15)">
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#10b981;margin-bottom:6px">✅ After Disaster</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.6">Return only when authorities declare it safe. Document damage. Seek medical attention for injuries. Contact insurance.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: CONTACTS
══════════════════════════════════════ -->
<div id="page-contacts" class="page">
  <div class="page-header d-flex align-items-start justify-content-between flex-wrap gap-2">
    <div>
      <h2>📞 Emergency Contacts</h2>
      <p>Direct lines to emergency services worldwide — available 24/7</p>
    </div>
    <input class="dm-input" style="max-width:240px" placeholder="🔍 Search contacts..." onkeyup="filterContacts(this.value)">
  </div>
  <div class="row g-3" id="contacts-grid">
    {% for c in contacts %}
    <div class="col-md-4 col-lg-3 contact-item" data-name="{{c.department.lower()}}">
      <div class="contact-card">
        <div class="mb-2"><span class="pill pill-{{loop.cycle('blue','orange','green','purple','red')}}">{{c.category}}</span>
          {% if c.available_24h %}<span class="pill pill-green ms-1">24/7</span>{% endif %}
        </div>
        <div class="contact-dept">{{c.department}}</div>
        <div class="contact-phone">{{c.phone}}</div>
        <div class="d-flex gap-2 flex-wrap">
          <a href="tel:{{c.phone}}" class="call-btn"><i class="fas fa-phone"></i> Call Now</a>
          {% if c.email %}<a href="mailto:{{c.email}}" class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:12px"><i class="fas fa-envelope"></i></a>{% endif %}
          {% if c.website %}<a href="{{c.website}}" target="_blank" class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:12px"><i class="fas fa-globe"></i></a>{% endif %}
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: SHELTERS
══════════════════════════════════════ -->
<div id="page-shelters" class="page">
  <div class="page-header d-flex align-items-start justify-content-between flex-wrap gap-2">
    <div>
      <h2>🏥 Relief Shelters</h2>
      <p>Locate available emergency shelters and capacity information</p>
    </div>
    <div class="d-flex gap-2">
      <input class="dm-input" style="max-width:200px" placeholder="🔍 Search by city..." onkeyup="filterShelters(this.value)">
    </div>
  </div>
  <div class="row g-3 mb-3">
    <div class="col-md-3">
      <div class="stat-card green">
        <div class="stat-value text-green">{{shelter_count}}</div>
        <div class="stat-label">Total Shelters</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="stat-card blue">
        <div class="stat-value text-blue">{{total_capacity | int}}</div>
        <div class="stat-label">Total Capacity</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="stat-card orange">
        <div class="stat-value text-orange">{{total_occupied | int}}</div>
        <div class="stat-label">Currently Occupied</div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="stat-card red">
        <div class="stat-value text-red">{{total_available | int}}</div>
        <div class="stat-label">Available Beds</div>
      </div>
    </div>
  </div>
  <div class="row g-3" id="shelters-grid">
    {% for s in shelters %}
    <div class="col-md-4 col-lg-3 shelter-item" data-city="{{s.city.lower()}}">
      <div class="shelter-card">
        <div class="shelter-name">{{s.name}}</div>
        <div class="shelter-addr"><i class="fas fa-map-pin text-muted me-1" style="font-size:10px"></i>{{s.address}}</div>
        <div class="d-flex justify-content-between mb-1" style="font-size:11px">
          <span class="text-muted">Capacity</span>
          <span class="font-mono">{{s.occupied}}/{{s.capacity}}</span>
        </div>
        {% set pct = (s.occupied / s.capacity * 100)|int %}
        <div class="capacity-bar"><div class="capacity-fill" style="width:{{pct}}%;background:{{'#ef4444' if pct>80 else '#f97316' if pct>60 else '#10b981'}}"></div></div>
        <div class="d-flex gap-1 flex-wrap mt-2">
          <span class="pill pill-{{'red' if pct>80 else 'orange' if pct>60 else 'green'}}">{{100-pct}}% Free</span>
          <span class="pill pill-blue">{{s.status}}</span>
        </div>
        <div class="mt-2" style="font-size:10px;color:var(--text-muted)">
          {% for a in s.amenities.split(',') %}<span class="me-2">✓ {{a}}</span>{% endfor %}
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: MAP
══════════════════════════════════════ -->
<div id="page-map" class="page">
  <div class="page-header">
    <h2>🗺️ Interactive Disaster Map</h2>
    <p>Real-time visualization of disaster events, shelters and danger zones worldwide</p>
  </div>
  <div class="glass-card mb-3" style="padding:14px">
    <div class="d-flex gap-2 flex-wrap align-items-center">
      <span style="font-size:12px;color:var(--text-muted);font-weight:600">LAYERS:</span>
      <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="toggleLayer('events')"><i class="fas fa-satellite-dish text-red"></i> Disasters</button>
      <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="toggleLayer('shelters')"><i class="fas fa-house-medical text-green"></i> Shelters</button>
      <div class="ms-auto d-flex gap-2">
        <span class="pill pill-red">● Extreme</span>
        <span class="pill pill-orange">● High</span>
        <span class="pill pill-yellow">● Medium</span>
        <span class="pill pill-green">● Low / Shelter</span>
      </div>
    </div>
  </div>
  <div id="map"></div>
</div>

<!-- ══════════════════════════════════════
     PAGE: STATISTICS
══════════════════════════════════════ -->
<div id="page-statistics" class="page">
  <div class="page-header">
    <h2>📊 Analytics & Statistics</h2>
    <p>Deep-dive disaster data analysis and trend intelligence</p>
  </div>
  <div class="row g-3 mb-3">
    <div class="col-lg-6">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-chart-bar"></i> Deaths by Disaster Type</div>
        <canvas id="chart-deaths" height="250"></canvas>
      </div>
    </div>
    <div class="col-lg-6">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-people-group"></i> Affected Population by Region</div>
        <canvas id="chart-regions" height="250"></canvas>
      </div>
    </div>
  </div>
  <div class="row g-3 mb-3">
    <div class="col-lg-4">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-chart-pie"></i> Status Distribution</div>
        <canvas id="chart-status" height="220"></canvas>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-chart-line"></i> Severity Analysis</div>
        <canvas id="chart-severity" height="220"></canvas>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-hospital"></i> Shelter Utilization</div>
        <canvas id="chart-shelter-util" height="220"></canvas>
      </div>
    </div>
  </div>
  <!-- Summary stats table -->
  <div class="glass-card">
    <div class="section-title mb-3"><i class="fas fa-table"></i> Global Summary Statistics</div>
    <div class="table-responsive">
      <table class="dm-table">
        <thead><tr><th>Metric</th><th>Value</th><th>Notes</th></tr></thead>
        <tbody>
          <tr><td>Total Disaster Events Tracked</td><td class="font-mono text-blue">{{total_events}}</td><td class="text-muted">Since platform launch</td></tr>
          <tr><td>Total Deaths Recorded</td><td class="font-mono text-red">{{"{:,}".format(total_deaths)}}</td><td class="text-muted">Across all tracked events</td></tr>
          <tr><td>Total People Affected</td><td class="font-mono text-orange">{{"{:,}".format(total_affected)}}</td><td class="text-muted">Displaced, injured & impacted</td></tr>
          <tr><td>Total Injured</td><td class="font-mono text-purple">{{"{:,}".format(total_injured)}}</td><td class="text-muted">Requiring medical attention</td></tr>
          <tr><td>Most Deadly Disaster Type</td><td class="font-mono text-red">{{deadliest_type}}</td><td class="text-muted">By cumulative deaths</td></tr>
          <tr><td>Countries Affected</td><td class="font-mono text-blue">{{countries}}</td><td class="text-muted">Unique countries with events</td></tr>
          <tr><td>Shelter Bed Availability</td><td class="font-mono text-green">{{shelter_available_pct}}%</td><td class="text-muted">Of total shelter capacity</td></tr>
          <tr><td>Emergency Contacts</td><td class="font-mono">{{contact_count}}</td><td class="text-muted">Agencies and organizations</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: REPORTS
══════════════════════════════════════ -->
<div id="page-reports" class="page">
  <div class="page-header">
    <h2>📋 Reports Center</h2>
    <p>Generate and export comprehensive disaster management reports</p>
  </div>
  <div class="row g-3">
    <div class="col-md-4">
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-file-pdf"></i> Generate Reports</div>
        <div class="mb-3">
          <label class="dm-label">Report Type</label>
          <select class="dm-select" id="rpt-type">
            <option>Situation Report (SitRep)</option>
            <option>Damage Assessment</option>
            <option>Population Impact Report</option>
            <option>Shelter Utilization Report</option>
            <option>Risk Assessment Summary</option>
            <option>Emergency Contact Directory</option>
            <option>Monthly Statistics</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Date Range</label>
          <select class="dm-select" id="rpt-range">
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
            <option>Last 3 Months</option>
            <option>Last Year</option>
            <option>All Time</option>
          </select>
        </div>
        <div class="mb-3">
          <label class="dm-label">Region Filter</label>
          <select class="dm-select" id="rpt-region">
            <option>Global (All Regions)</option>
            <option>South Asia</option>
            <option>Southeast Asia</option>
            <option>East Asia</option>
            <option>Africa</option>
            <option>Europe</option>
            <option>Americas</option>
            <option>Middle East</option>
            <option>Oceania</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="dm-label">Format</label>
          <div class="d-flex gap-2">
            <label style="font-size:13px;display:flex;align-items:center;gap:6px;cursor:pointer"><input type="radio" name="rpt-fmt" value="json" checked> JSON</label>
            <label style="font-size:13px;display:flex;align-items:center;gap:6px;cursor:pointer"><input type="radio" name="rpt-fmt" value="csv"> CSV</label>
            <label style="font-size:13px;display:flex;align-items:center;gap:6px;cursor:pointer"><input type="radio" name="rpt-fmt" value="text"> Text</label>
          </div>
        </div>
        <button class="dm-btn dm-btn-primary w-100" onclick="generateReport()"><i class="fas fa-file-export"></i> Generate Report</button>
      </div>
    </div>
    <div class="col-md-8">
      <div class="glass-card" style="min-height:400px">
        <div class="section-title mb-3"><i class="fas fa-file-code"></i> Report Output</div>
        <pre id="report-output" style="background:var(--bg-deep);border:1px solid var(--border);border-radius:8px;padding:16px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text-muted);min-height:340px;overflow:auto;line-height:1.6">
╔══════════════════════════════════════════════════════════════╗
║  DisasterWatch Pro — Report Generator                        ║
║  Configure report parameters and click Generate.             ║
╚══════════════════════════════════════════════════════════════╝

Select report type, date range, and region, then click
"Generate Report" to produce the output.

Supported formats:
  • JSON  — Machine-readable structured data
  • CSV   — Spreadsheet-compatible format
  • Text  — Human-readable summary report
        </pre>
        <div class="mt-2 d-flex gap-2" id="report-actions" style="display:none!important">
          <button class="dm-btn dm-btn-success" onclick="copyReport()"><i class="fas fa-copy"></i> Copy</button>
          <button class="dm-btn dm-btn-outline" onclick="downloadReport()"><i class="fas fa-download"></i> Download</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: AI ASSISTANT
══════════════════════════════════════ -->
<div id="page-ai" class="page">
  <div class="page-header">
    <h2>🤖 AI Disaster Assistant</h2>
    <p>Intelligent disaster management advisor powered by embedded knowledge base</p>
  </div>
  <div class="row g-3">
    <div class="col-lg-8">
      <div class="chat-container">
        <div class="chat-header">
          <div class="chat-avatar">🤖</div>
          <div>
            <div style="font-size:14px;font-weight:700">DisasterAI Assistant</div>
            <div style="font-size:11px;color:var(--text-muted)">Expert in disaster preparedness, response & recovery</div>
          </div>
          <div class="ms-auto"><span class="pill pill-green">● Online</span></div>
        </div>
        <div class="chat-messages" id="chat-messages">
          <div class="msg-bot">
            <div class="msg-bubble">
              👋 Hello! I'm your AI Disaster Management Assistant. I have deep knowledge about:<br><br>
              🌋 <strong>All disaster types</strong> — causes, impacts & indicators<br>
              🛡️ <strong>Safety protocols</strong> — before, during & after events<br>
              🧰 <strong>Preparedness</strong> — kits, plans & checklists<br>
              🚑 <strong>First aid</strong> — emergency medical guidance<br>
              📍 <strong>Evacuation</strong> — routes & procedures<br><br>
              What would you like to know?
            </div>
          </div>
        </div>
        <div class="chat-input-row">
          <input class="chat-input" id="chat-input" placeholder="Ask about any disaster, safety tip, or emergency procedure..." onkeypress="if(event.key==='Enter')sendChat()">
          <button class="chat-send" onclick="sendChat()"><i class="fas fa-paper-plane"></i></button>
        </div>
      </div>
    </div>
    <div class="col-lg-4">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-lightbulb"></i> Quick Topics</div>
        <div class="d-flex flex-wrap gap-2">
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('What should I do during an earthquake?')">🏚️ Earthquake</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('How to prepare for a flood?')">🌊 Flood Prep</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('What to pack in an emergency go-bag?')">🎒 Go-Bag</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('How to treat someone for heat stroke?')">☀️ Heat Stroke</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('What are early warning signs of a tsunami?')">🌊 Tsunami Signs</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('How to create a family emergency plan?')">👨‍👩‍👧 Family Plan</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('How to stay safe during a wildfire?')">🔥 Wildfire</button>
          <button class="dm-btn dm-btn-outline" style="padding:6px 12px;font-size:11px" onclick="askQuick('What is the difference between a cyclone, hurricane, and typhoon?')">🌀 Cyclones</button>
        </div>
      </div>
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-info-circle"></i> Assistant Capabilities</div>
        <div style="font-size:12px;color:var(--text-muted);line-height:1.8">
          ✅ Explain any disaster type in detail<br>
          ✅ Provide step-by-step safety guidance<br>
          ✅ Recommend preparedness measures<br>
          ✅ First aid and emergency response<br>
          ✅ Evacuation route planning advice<br>
          ✅ Risk assessment guidance<br>
          ✅ Post-disaster recovery support<br>
          ✅ Emergency contact guidance<br>
          ✅ Compare disaster types<br>
          ✅ Regional risk information
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: ADMIN
══════════════════════════════════════ -->
<div id="page-admin" class="page">
  <div class="page-header">
    <h2>⚙️ Admin Panel</h2>
    <p>Platform administration and data management</p>
  </div>
  <div class="row g-3">
    <div class="col-lg-6">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-plus-circle text-green"></i> Add New Disaster Event</div>
        <div class="row g-2">
          <div class="col-md-6">
            <label class="dm-label">Disaster Type</label>
            <select class="dm-select" id="adm-dis-type">
              {% for d in disasters %}<option value="{{d.id}}">{{d.icon}} {{d.name}}</option>{% endfor %}
            </select>
          </div>
          <div class="col-md-6">
            <label class="dm-label">Event Title</label>
            <input class="dm-input" id="adm-title" placeholder="e.g. Cyclone Biparjoy">
          </div>
          <div class="col-md-6">
            <label class="dm-label">Location</label>
            <input class="dm-input" id="adm-loc" placeholder="City, Region">
          </div>
          <div class="col-md-6">
            <label class="dm-label">Country</label>
            <input class="dm-input" id="adm-country" placeholder="e.g. India">
          </div>
          <div class="col-md-6">
            <label class="dm-label">Severity</label>
            <select class="dm-select" id="adm-severity">
              <option>Extreme</option><option>High</option><option>Medium</option><option>Low</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="dm-label">Status</label>
            <select class="dm-select" id="adm-status">
              <option>Active</option><option>Resolved</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="dm-label">Affected Population</label>
            <input class="dm-input" id="adm-affected" type="number" placeholder="0">
          </div>
          <div class="col-md-4">
            <label class="dm-label">Injured</label>
            <input class="dm-input" id="adm-injured" type="number" placeholder="0">
          </div>
          <div class="col-md-4">
            <label class="dm-label">Deaths</label>
            <input class="dm-input" id="adm-deaths" type="number" placeholder="0">
          </div>
          <div class="col-md-6">
            <label class="dm-label">Latitude</label>
            <input class="dm-input" id="adm-lat" type="number" step="0.0001" placeholder="0.0000">
          </div>
          <div class="col-md-6">
            <label class="dm-label">Longitude</label>
            <input class="dm-input" id="adm-lng" type="number" step="0.0001" placeholder="0.0000">
          </div>
          <div class="col-12">
            <label class="dm-label">Reported Date</label>
            <input class="dm-input" id="adm-date" type="date">
          </div>
          <div class="col-12">
            <button class="dm-btn dm-btn-primary w-100" onclick="adminAddEvent()">
              <i class="fas fa-satellite-dish"></i> Add Disaster Event
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="col-lg-6">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-chart-simple"></i> Platform Statistics</div>
        <div class="table-responsive">
          <table class="dm-table">
            <tbody>
              <tr><td><i class="fas fa-circle-dot text-orange me-2"></i>Total Disasters</td><td class="text-right font-mono fw-800 text-orange">{{disaster_count}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-red me-2"></i>Total Events</td><td class="text-right font-mono fw-800 text-red">{{total_events}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-red me-2"></i>Active Events</td><td class="text-right font-mono fw-800 text-red">{{active_events}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-blue me-2"></i>Total Contacts</td><td class="text-right font-mono fw-800 text-blue">{{contact_count}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-green me-2"></i>Total Shelters</td><td class="text-right font-mono fw-800 text-green">{{shelter_count}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-purple me-2"></i>Active Alerts</td><td class="text-right font-mono fw-800 text-purple">{{alert_count}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-orange me-2"></i>Total Deaths</td><td class="text-right font-mono fw-800">{{"{:,}".format(total_deaths)}}</td></tr>
              <tr><td><i class="fas fa-circle-dot text-blue me-2"></i>People Affected</td><td class="text-right font-mono fw-800">{{"{:,}".format(total_affected)}}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-users"></i> User Management</div>
        <div class="table-responsive">
          <table class="dm-table">
            <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Since</th></tr></thead>
            <tbody>
              {% for u in users %}
              <tr>
                <td>{{u.name}}</td>
                <td class="text-muted" style="font-size:11px">{{u.email}}</td>
                <td><span class="pill {{'pill-orange' if u.role=='admin' else 'pill-blue'}}">{{u.role}}</span></td>
                <td class="text-muted font-mono" style="font-size:11px">{{u.created_at[:10]}}</td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════
     PAGE: SETTINGS
══════════════════════════════════════ -->
<div id="page-settings" class="page">
  <div class="page-header">
    <h2>⚙️ Settings</h2>
    <p>Customize your DisasterWatch Pro experience</p>
  </div>
  <div class="row g-3">
    <div class="col-md-6">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-palette"></i> Appearance</div>
        <div class="mb-3">
          <label class="dm-label">Theme</label>
          <div class="d-flex gap-3 mt-1">
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13px">
              <input type="radio" name="theme" value="dark" checked onchange="setTheme(this.value)"> 🌙 Dark Mode
            </label>
            <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:13px">
              <input type="radio" name="theme" value="light" onchange="setTheme(this.value)"> ☀️ Light Mode
            </label>
          </div>
        </div>
        <div class="mb-3">
          <label class="dm-label">Accent Color</label>
          <div class="d-flex gap-2 mt-1">
            <div onclick="setAccent('#f97316')" style="width:28px;height:28px;border-radius:6px;background:#f97316;cursor:pointer;border:2px solid transparent" class="accent-swatch"></div>
            <div onclick="setAccent('#ef4444')" style="width:28px;height:28px;border-radius:6px;background:#ef4444;cursor:pointer;border:2px solid transparent" class="accent-swatch"></div>
            <div onclick="setAccent('#3b82f6')" style="width:28px;height:28px;border-radius:6px;background:#3b82f6;cursor:pointer;border:2px solid transparent" class="accent-swatch"></div>
            <div onclick="setAccent('#10b981')" style="width:28px;height:28px;border-radius:6px;background:#10b981;cursor:pointer;border:2px solid transparent" class="accent-swatch"></div>
            <div onclick="setAccent('#8b5cf6')" style="width:28px;height:28px;border-radius:6px;background:#8b5cf6;cursor:pointer;border:2px solid transparent" class="accent-swatch"></div>
          </div>
        </div>
      </div>
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-bell"></i> Alert Preferences</div>
        <div class="d-flex flex-column gap-3">
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:13px">
            <span>Show ticker alerts in header</span>
            <input type="checkbox" checked style="accent-color:var(--accent);width:16px;height:16px">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:13px">
            <span>Sound alerts for Extreme events</span>
            <input type="checkbox" style="accent-color:var(--accent);width:16px;height:16px">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:13px">
            <span>Show desktop notifications</span>
            <input type="checkbox" style="accent-color:var(--accent);width:16px;height:16px">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:13px">
            <span>Email daily digest</span>
            <input type="checkbox" style="accent-color:var(--accent);width:16px;height:16px">
          </label>
        </div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="glass-card mb-3">
        <div class="section-title mb-3"><i class="fas fa-user-circle"></i> Account</div>
        <div class="mb-3">
          <label class="dm-label">Display Name</label>
          <input class="dm-input" value="Administrator">
        </div>
        <div class="mb-3">
          <label class="dm-label">Email</label>
          <input class="dm-input" value="admin@disaster.gov">
        </div>
        <div class="mb-3">
          <label class="dm-label">Role</label>
          <input class="dm-input" value="System Administrator" readonly style="opacity:.7">
        </div>
        <button class="dm-btn dm-btn-primary"><i class="fas fa-save"></i> Save Changes</button>
      </div>
      <div class="glass-card">
        <div class="section-title mb-3"><i class="fas fa-database"></i> System Information</div>
        <div style="font-size:12px;color:var(--text-muted);line-height:2">
          <div class="d-flex justify-content-between"><span>Platform Version</span><span class="font-mono text-orange">v2.0 Enterprise</span></div>
          <div class="d-flex justify-content-between"><span>Database</span><span class="font-mono">SQLite 3.x</span></div>
          <div class="d-flex justify-content-between"><span>Backend</span><span class="font-mono">Python Flask</span></div>
          <div class="d-flex justify-content-between"><span>Last DB Backup</span><span class="font-mono text-green">Today 00:00 UTC</span></div>
          <div class="d-flex justify-content-between"><span>Data Last Updated</span><span class="font-mono" id="last-updated">—</span></div>
          <div class="d-flex justify-content-between"><span>API Status</span><span class="font-mono text-green">● Operational</span></div>
        </div>
      </div>
    </div>
  </div>
</div>

</main>

<!-- TOAST CONTAINER -->
<div class="toast-container" id="toast-container"></div>

<!-- ████████ SCRIPTS ████████ -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
// ─── GLOBAL DATA (injected from Flask) ───
const EVENTS_DATA   = {{events_json|safe}};
const SHELTERS_DATA = {{shelters_json|safe}};
const DISASTERS_DATA= {{disasters_json|safe}};
const STATS_DATA    = {{stats_json|safe}};

// ─── SIDEBAR / HEADER TOGGLE ───
let sidebarOpen = true;
function toggleSidebar() {
  sidebarOpen = !sidebarOpen;
  document.getElementById('sidebar').classList.toggle('collapsed', !sidebarOpen);
  document.getElementById('header').classList.toggle('expanded', !sidebarOpen);
  document.getElementById('main').classList.toggle('expanded', !sidebarOpen);
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.remove('collapsed');
    document.getElementById('sidebar').classList.toggle('mobile-open', sidebarOpen);
  }
}

// ─── PAGE NAVIGATION ───
const pageTitles = {
  dashboard:    ['Dashboard', 'Real-time disaster monitoring & response coordination'],
  encyclopedia: ['Disaster Encyclopedia', 'Comprehensive knowledge base for all disaster types'],
  events:       ['Live Disaster Events', 'Real-time global disaster event tracking'],
  alerts:       ['Active Alerts', 'Current warnings and emergency advisories'],
  risk:         ['Risk Assessment', 'Multi-factor disaster risk analysis engine'],
  preparedness: ['Preparedness Center', 'Checklists and guides for disaster preparedness'],
  safety:       ['Safety Guides', 'Step-by-step safety protocols for every disaster'],
  contacts:     ['Emergency Contacts', '24/7 emergency services directory'],
  shelters:     ['Relief Shelters', 'Available emergency shelter locations'],
  map:          ['Interactive Map', 'Real-time disaster event visualization'],
  statistics:   ['Statistics & Analytics', 'Deep-dive disaster data intelligence'],
  reports:      ['Reports Center', 'Generate and export disaster management reports'],
  ai:           ['AI Disaster Assistant', 'Intelligent disaster management advisor'],
  admin:        ['Admin Panel', 'Platform administration and data management'],
  settings:     ['Settings', 'Customize your DisasterWatch Pro experience'],
};
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  const p = document.getElementById('page-' + id);
  if (p) p.classList.add('active');
  document.querySelectorAll('.nav-link').forEach(l => {
    if (l.getAttribute('onclick') && l.getAttribute('onclick').includes("'" + id + "'")) l.classList.add('active');
  });
  const t = pageTitles[id] || ['DisasterWatch Pro', ''];
  document.getElementById('page-title').textContent = t[0];
  document.getElementById('page-sub').textContent   = t[1];
  // Lazy-init certain pages
  if (id === 'map') initMap();
  if (id === 'statistics') initStatsCharts();
  if (id === 'settings') { document.getElementById('last-updated').textContent = new Date().toLocaleString(); }
}

// ─── THEME ───
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('theme-btn').innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
}
function setTheme(v) { document.documentElement.setAttribute('data-theme', v); }
function setAccent(color) { document.documentElement.style.setProperty('--accent', color); }

// ─── CHARTS (Dashboard) ───
const CHART_DEFAULTS = {
  font: { family: 'Inter', size: 11 },
  color: '#94a3b8',
  borderColor: 'rgba(255,255,255,0.06)',
  gridColor: 'rgba(255,255,255,0.04)',
};
function mkChart(id, type, labels, datasets, options={}) {
  const el = document.getElementById(id);
  if (!el) return;
  if (el._chart) el._chart.destroy();
  el._chart = new Chart(el, {
    type, data: { labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: { legend: { labels: { color: CHART_DEFAULTS.color, font: CHART_DEFAULTS.font, padding: 16, boxWidth: 10 } } },
      scales: type !== 'pie' && type !== 'doughnut' ? {
        x: { grid: { color: CHART_DEFAULTS.gridColor }, ticks: { color: CHART_DEFAULTS.color, font: { size: 10 } } },
        y: { grid: { color: CHART_DEFAULTS.gridColor }, ticks: { color: CHART_DEFAULTS.color, font: { size: 10 } } },
      } : {},
      ...options,
    }
  });
}

// Dashboard Charts
mkChart('chart-trend', 'line',
  ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
  [
    { label: '2024 Events', data: [8,6,10,12,14,11,15,13,9,16,10,8], borderColor:'#f97316', backgroundColor:'rgba(249,115,22,.08)', tension:.4, fill:true, pointRadius:3 },
    { label: '2025 Events', data: [10,8,12,14,18,13,null,null,null,null,null,null], borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,.08)', tension:.4, fill:true, pointRadius:3 },
  ]
);
mkChart('chart-category', 'doughnut',
  ['Geological','Hydrological','Meteorological','Biological','Technological','Climatological'],
  [{ data: [5,3,6,2,2,2], backgroundColor:['#ef4444','#3b82f6','#8b5cf6','#10b981','#f59e0b','#64748b'], borderWidth:2, borderColor:'#111827' }]
);

// ─── MAP ───
let mapInstance = null, evLayer = null, shLayer = null;
let mapInit = false;
function initMap() {
  if (mapInit) return;
  mapInit = true;
  mapInstance = L.map('map', { zoomControl: true, attributionControl: true })
    .setView([20, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    className: 'map-tiles',
  }).addTo(mapInstance);

  // Apply dark filter to tiles
  setTimeout(() => {
    document.querySelectorAll('.map-tiles img').forEach(img => {
      img.style.filter = 'invert(1) hue-rotate(180deg) brightness(0.8) contrast(1.1)';
    });
  }, 800);

  evLayer = L.layerGroup().addTo(mapInstance);
  shLayer = L.layerGroup().addTo(mapInstance);

  const sevColor = { Extreme:'#ef4444', High:'#f97316', Medium:'#eab308', Low:'#10b981' };
  EVENTS_DATA.forEach(ev => {
    if (!ev.latitude || !ev.longitude || (ev.latitude === 0 && ev.longitude === 0)) return;
    const color = sevColor[ev.severity] || '#f97316';
    L.circleMarker([ev.latitude, ev.longitude], {
      radius: ev.severity==='Extreme'?14:ev.severity==='High'?11:ev.severity==='Medium'?8:6,
      fillColor: color, color: color, weight: 2, opacity: 1, fillOpacity: 0.55,
    }).bindPopup(`
      <div style="font-family:Inter;min-width:200px">
        <b style="font-size:13px">${ev.title}</b><br>
        <span style="font-size:11px;color:#64748b">${ev.location}, ${ev.country}</span><br><br>
        <span style="background:${color};color:#fff;font-size:10px;padding:2px 8px;border-radius:12px;font-weight:700">${ev.severity}</span>
        <span style="background:${ev.status==='Active'?'rgba(239,68,68,.15)':'rgba(16,185,129,.15)'};color:${ev.status==='Active'?'#ef4444':'#10b981'};font-size:10px;padding:2px 8px;border-radius:12px;font-weight:700;margin-left:4px">${ev.status}</span><br><br>
        <div style="font-size:11px">👥 Affected: <b>${ev.affected_population.toLocaleString()}</b></div>
        <div style="font-size:11px">💀 Deaths: <b>${ev.deaths.toLocaleString()}</b></div>
        <div style="font-size:11px;color:#64748b;margin-top:4px">📅 ${ev.reported_date}</div>
      </div>
    `).addTo(evLayer);
  });

  SHELTERS_DATA.forEach(sh => {
    L.circleMarker([sh.latitude, sh.longitude], {
      radius: 6, fillColor:'#10b981', color:'#059669', weight:2, opacity:1, fillOpacity:0.7,
    }).bindPopup(`
      <div style="font-family:Inter;min-width:180px">
        <b style="font-size:13px">🏥 ${sh.name}</b><br>
        <span style="font-size:11px;color:#64748b">${sh.address}</span><br><br>
        <div style="font-size:11px">Capacity: <b>${sh.occupied}/${sh.capacity}</b></div>
        <div style="font-size:11px;color:#10b981;font-weight:700">${sh.capacity-sh.occupied} beds available</div>
      </div>
    `).addTo(shLayer);
  });
}
function toggleLayer(type) {
  if (!mapInstance) return;
  const layer = type==='events' ? evLayer : shLayer;
  if (mapInstance.hasLayer(layer)) mapInstance.removeLayer(layer);
  else mapInstance.addLayer(layer);
}

// ─── STATS CHARTS ───
let statsInited = false;
function initStatsCharts() {
  if (statsInited) return; statsInited = true;

  // Deaths by type
  const deathData = STATS_DATA.deaths_by_type;
  mkChart('chart-deaths','bar',
    deathData.map(d=>d.name),
    [{label:'Total Deaths',data:deathData.map(d=>d.deaths),backgroundColor:deathData.map((_,i)=>`hsl(${i*19+5},80%,${50+i%3*8}%)`),borderRadius:6}]
  );

  // Affected by region
  const regData = STATS_DATA.affected_by_country.slice(0,10);
  mkChart('chart-regions','bar',
    regData.map(d=>d.country),
    [{label:'Affected Population',data:regData.map(d=>d.affected),backgroundColor:'rgba(59,130,246,.7)',borderRadius:6}]
  );

  // Status distribution
  mkChart('chart-status','doughnut',
    ['Active','Resolved'],
    [{data:STATS_DATA.status_counts,backgroundColor:['#ef4444','#10b981'],borderWidth:2,borderColor:'#111827'}]
  );

  // Severity
  mkChart('chart-severity','bar',
    ['Extreme','High','Medium','Low'],
    [{label:'Events',data:STATS_DATA.severity_counts,backgroundColor:['#ef4444','#f97316','#eab308','#10b981'],borderRadius:6}]
  );

  // Shelter utilization
  mkChart('chart-shelter-util','doughnut',
    ['Occupied','Available'],
    [{data:STATS_DATA.shelter_util,backgroundColor:['#f97316','#10b981'],borderWidth:2,borderColor:'#111827'}]
  );

  // Alerts
  mkChart('chart-alerts','doughnut',
    ['Extreme','High','Medium','Low'],
    [{data:STATS_DATA.alert_counts,backgroundColor:['#ef4444','#f97316','#eab308','#10b981'],borderWidth:2,borderColor:'#111827'}]
  );
}

// ─── ENCYCLOPEDIA ───
function loadDisaster(id) {
  fetch('/api/disaster/' + id)
    .then(r => r.json())
    .then(d => {
      const html = `
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
          <span style="font-size:48px">${d.icon}</span>
          <div>
            <h3 style="font-size:22px;font-weight:800;margin-bottom:4px">${d.name}</h3>
            <span class="pill pill-gray">${d.category}</span>
          </div>
        </div>
        <div class="row g-3">
          <div class="col-md-6">
            <div class="detail-section">
              <h6>📖 What is it?</h6>
              <p>${d.description}</p>
            </div>
            <div class="detail-section">
              <h6>⚡ Causes</h6>
              <p>${d.causes}</p>
            </div>
            <div class="detail-section">
              <h6>⚠️ Warning Signs</h6>
              <p>${d.warning_signs}</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="detail-section">
              <h6>💥 Impact</h6>
              <p>${d.impact}</p>
            </div>
            <div class="detail-section">
              <h6>🛡️ Safety Measures</h6>
              <p>${d.safety_measures}</p>
            </div>
            <div class="detail-section">
              <h6>🚑 First Aid</h6>
              <p>${d.first_aid}</p>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <h6>📋 Do's & Don'ts</h6>
          <div class="row g-2">
            <div class="col-md-6">
              <div class="p-3 rounded" style="background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.2)">
                <div style="font-size:11px;font-weight:700;color:#10b981;margin-bottom:8px">✅ DO</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.8">
                  • Follow official evacuation orders immediately<br>
                  • Keep emergency kit ready at all times<br>
                  • Stay informed via official channels<br>
                  • Help neighbours, especially elderly<br>
                  • Document property damage for insurance
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="p-3 rounded" style="background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2)">
                <div style="font-size:11px;font-weight:700;color:#ef4444;margin-bottom:8px">❌ DON'T</div>
                <div style="font-size:12px;color:var(--text-muted);line-height:1.8">
                  • Ignore official warnings or advisories<br>
                  • Return to disaster zone prematurely<br>
                  • Use elevators during evacuation<br>
                  • Share unverified information<br>
                  • Approach unstable structures
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
      document.getElementById('enc-detail-content').innerHTML = html;
      const panel = document.getElementById('enc-detail');
      panel.classList.add('open');
      panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
}

// ─── RISK ASSESSMENT ───
function calcRisk() {
  const vals = ['r-location','r-pop','r-rain','r-seismic','r-forest','r-river','r-industrial']
    .map(id => parseInt(document.getElementById(id).value));
  const total = vals.reduce((s,v)=>s+v,0);
  const maxPossible = 5 * 7;
  const score = Math.round((total / maxPossible) * 100);
  const pct = score;

  let level, color, icon;
  if (score <= 25)      { level='LOW RISK';     color='#10b981'; icon='🟢'; }
  else if (score <= 50) { level='MEDIUM RISK';  color='#eab308'; icon='🟡'; }
  else if (score <= 75) { level='HIGH RISK';    color='#f97316'; icon='🟠'; }
  else                  { level='EXTREME RISK'; color='#ef4444'; icon='🔴'; }

  document.getElementById('risk-result').style.display='block';
  document.getElementById('risk-recommendations').style.display='block';
  const sv = document.getElementById('risk-score-val');
  sv.style.color = color; sv.textContent = score;
  const rl = document.getElementById('risk-level');
  rl.style.color = color; rl.textContent = icon + ' ' + level;
  document.getElementById('risk-pct').textContent = pct + '%';
  const fill = document.getElementById('risk-fill');
  fill.style.width = pct + '%'; fill.style.background = color;

  const labels = ['Location','Population','Rainfall','Seismic Zone','Vegetation','River Prox.','Industrial'];
  const breakdown = document.getElementById('risk-breakdown');
  breakdown.innerHTML = vals.map((v,i) => `
    <div class="col-6 col-md-3">
      <div class="p-2 rounded" style="background:var(--bg-card2);border:1px solid var(--border)">
        <div style="font-size:10px;color:var(--text-muted)">${labels[i]}</div>
        <div style="font-size:16px;font-weight:800;color:${v>=4?'#ef4444':v>=3?'#f97316':'#10b981'};font-family:'JetBrains Mono',monospace">${v}/5</div>
      </div>
    </div>`).join('');

  const recs = [];
  if (vals[0] >= 4) recs.push('🏖️ Coastal location requires tsunami and storm surge preparedness');
  if (vals[1] >= 4) recs.push('👥 High population density requires mass evacuation planning');
  if (vals[2] >= 4) recs.push('🌧️ High rainfall zone — flood barriers and drainage essential');
  if (vals[3] >= 4) recs.push('🏚️ High seismic zone — building codes and earthquake drills critical');
  if (vals[4] >= 4) recs.push('🔥 High wildfire risk — maintain defensible space, have evacuation plan');
  if (vals[5] >= 4) recs.push('🌊 River proximity — install flood monitors, know flood plain maps');
  if (vals[6] >= 4) recs.push('🏭 Industrial hazards nearby — HAZMAT protocol and shelter-in-place plan needed');
  if (recs.length === 0) recs.push('✅ Risk profile is manageable. Maintain standard preparedness protocols.');

  document.getElementById('risk-rec-content').innerHTML = recs.map(r =>
    `<div class="check-item mb-2"><div style="font-size:13px">${r}</div></div>`
  ).join('');

  showToast('Risk calculation complete', color === '#10b981' ? 'success' : color === '#ef4444' ? 'danger' : 'warning');
}

// ─── CHECKLIST LOADER ───
function loadChecklist(type) {
  fetch('/api/checklist/' + encodeURIComponent(type))
    .then(r => r.json())
    .then(items => {
      const priorityColor = { High:'#ef4444', Medium:'#f97316', Low:'#10b981' };
      let html = `<div class="section-title mb-3">🧰 ${type} Preparedness Checklist</div>`;
      items.forEach((item, i) => {
        html += `
          <div class="check-item">
            <input type="checkbox" id="ci${i}">
            <label for="ci${i}">
              ${item.item_name}
              <span>${item.description}</span>
            </label>
            <span class="pill ms-auto" style="background:rgba(0,0,0,.2);color:${priorityColor[item.priority]||'#94a3b8'};border-color:${priorityColor[item.priority]||'#94a3b8'};font-size:10px">${item.priority}</span>
          </div>`;
      });
      document.getElementById('checklist-container').innerHTML = html;
    });
}

// ─── SAFETY GUIDE ───
function loadSafetyGuide(id, name, icon) {
  fetch('/api/disaster/' + id)
    .then(r => r.json())
    .then(d => {
      document.getElementById('safety-content').innerHTML = `
        <div class="glass-card">
          <div class="section-title mb-4">${icon} ${name} — Complete Safety Guide</div>
          <div class="row g-3">
            <div class="col-md-4">
              <div class="p-4 rounded h-100" style="background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.2)">
                <h6 style="color:#3b82f6;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">⏩ BEFORE DISASTER</h6>
                <div style="font-size:13px;line-height:1.8;color:var(--text-muted)">${d.safety_measures}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-4 rounded h-100" style="background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2)">
                <h6 style="color:#ef4444;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">🚨 DURING DISASTER</h6>
                <div style="font-size:13px;line-height:1.8;color:var(--text-muted)">${d.first_aid}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="p-4 rounded h-100" style="background:rgba(16,185,129,.07);border:1px solid rgba(16,185,129,.2)">
                <h6 style="color:#10b981;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">✅ AFTER DISASTER</h6>
                <div style="font-size:13px;line-height:1.8;color:var(--text-muted)">
                  Return only when authorities say it is safe. Photograph all damage for insurance claims. Avoid entering structurally damaged buildings. Seek medical attention for any injuries. Listen to official radio for instructions. Contact family members to confirm safety. Begin recovery documentation.
                </div>
              </div>
            </div>
          </div>
          <div class="divider"></div>
          <div class="row g-3">
            <div class="col-md-6">
              <h6 style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:12px">⚠️ WARNING SIGNS</h6>
              <p style="font-size:13px;color:var(--text-muted);line-height:1.8">${d.warning_signs}</p>
            </div>
            <div class="col-md-6">
              <h6 style="font-size:12px;font-weight:700;color:var(--accent);margin-bottom:12px">💥 IMPACT ASSESSMENT</h6>
              <p style="font-size:13px;color:var(--text-muted);line-height:1.8">${d.impact}</p>
            </div>
          </div>
        </div>`;
    });
}

// ─── CONTACTS FILTER ───
function filterContacts(q) {
  q = q.toLowerCase();
  document.querySelectorAll('.contact-item').forEach(el => {
    el.style.display = el.dataset.name.includes(q) ? '' : 'none';
  });
}

// ─── SHELTERS FILTER ───
function filterShelters(q) {
  q = q.toLowerCase();
  document.querySelectorAll('.shelter-item').forEach(el => {
    el.style.display = el.dataset.city.includes(q) ? '' : 'none';
  });
}

// ─── EVENTS FILTER ───
function filterEvents(sev) {
  document.querySelectorAll('.ev-row').forEach(row => {
    row.style.display = (!sev || row.dataset.severity === sev) ? '' : 'none';
  });
}
function filterEvStatus(st) {
  document.querySelectorAll('.ev-row').forEach(row => {
    row.style.display = (!st || row.dataset.status === st) ? '' : 'none';
  });
}

// ─── ADD ALERT ───
function addAlert() {
  const payload = {
    title: document.getElementById('new-alert-title').value,
    message: document.getElementById('new-alert-msg').value,
    severity: document.getElementById('new-alert-sev').value,
    region: document.getElementById('new-alert-region').value,
  };
  if (!payload.title || !payload.message) { showToast('Fill all fields','danger'); return; }
  fetch('/api/alert', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    .then(r => r.json())
    .then(d => {
      showToast('Alert broadcast successfully','success');
      setTimeout(() => location.reload(), 1200);
    });
}

// ─── ADMIN ADD EVENT ───
function adminAddEvent() {
  const payload = {
    disaster_id: document.getElementById('adm-dis-type').value,
    title: document.getElementById('adm-title').value,
    location: document.getElementById('adm-loc').value,
    country: document.getElementById('adm-country').value,
    severity: document.getElementById('adm-severity').value,
    status: document.getElementById('adm-status').value,
    affected_population: parseInt(document.getElementById('adm-affected').value)||0,
    injured: parseInt(document.getElementById('adm-injured').value)||0,
    deaths: parseInt(document.getElementById('adm-deaths').value)||0,
    latitude: parseFloat(document.getElementById('adm-lat').value)||0,
    longitude: parseFloat(document.getElementById('adm-lng').value)||0,
    reported_date: document.getElementById('adm-date').value,
  };
  if (!payload.title || !payload.location) { showToast('Fill required fields','danger'); return; }
  fetch('/api/event', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    .then(r => r.json())
    .then(d => {
      showToast('Event added successfully','success');
    });
}

// ─── REPORT GENERATOR ───
function generateReport() {
  const type = document.getElementById('rpt-type').value;
  const range = document.getElementById('rpt-range').value;
  const region = document.getElementById('rpt-region').value;
  const fmt = document.querySelector('input[name="rpt-fmt"]:checked').value;

  fetch(`/api/report?type=${encodeURIComponent(type)}&range=${encodeURIComponent(range)}&region=${encodeURIComponent(region)}&format=${fmt}`)
    .then(r => r.json())
    .then(data => {
      let output;
      if (fmt === 'json') {
        output = JSON.stringify(data, null, 2);
      } else if (fmt === 'csv') {
        if (data.rows) {
          output = data.headers.join(',') + '\n' + data.rows.map(r => r.join(',')).join('\n');
        } else {
          output = JSON.stringify(data);
        }
      } else {
        output = data.text || JSON.stringify(data, null, 2);
      }
      document.getElementById('report-output').textContent = output;
      document.getElementById('report-actions').style.display = 'flex';
      showToast('Report generated successfully','success');
    });
}
function copyReport() {
  navigator.clipboard.writeText(document.getElementById('report-output').textContent);
  showToast('Copied to clipboard','success');
}
function downloadReport() {
  const text = document.getElementById('report-output').textContent;
  const blob = new Blob([text], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'disaster_report_' + Date.now() + '.txt';
  a.click();
}

// ─── AI CHAT ───
const KB = {
  earthquake: "During an earthquake: DROP to your hands and knees, take COVER under a sturdy table or against an interior wall, HOLD ON until shaking stops. Stay away from windows, exterior walls and anything that could fall. If outdoors, move away from buildings and utility wires. After: Check for injuries, be aware of aftershocks, check utilities for damage. Causes: tectonic plate movement. Warning signs: foreshocks, ground tilting, unusual animal behavior.",
  flood: "For floods: Never walk or drive through floodwaters — 6 inches can knock you down, 2 feet can sweep away a car. Move to higher ground immediately. Avoid bridges over fast-moving water. If trapped on upper floor, signal for help. Turn off utilities at main switches. Flood preparedness: elevate electrical systems, install check valves, waterproof basement walls.",
  cyclone: "For cyclones/hurricanes: Before — board windows, fill bathtubs with water, stock 3+ day supplies, know evacuation routes. During — stay indoors, avoid windows, shelter in interior room. After — beware of storm surge after eye passes, avoid floodwaters, check for gas leaks. Categories 1-5 based on wind speed.",
  tsunami: "Tsunami warning signs: Strong ground shaking, ocean withdrawal from shore (exposes seafloor), loud roaring sound. Action: Move inland immediately to high ground (100+ feet elevation). Don't wait for official warning. Don't go to shore to watch waves. A tsunami is a series of waves — first wave may not be the largest. Wait for official all-clear.",
  wildfire: "Wildfire safety: Create defensible space — clear vegetation 100 feet around home. Have go-bag ready. Know 2+ evacuation routes. During fire: close all windows and vents, don't shelter in garage. If trapped in car: park off road, windows up, headlights on, crouch below dashboard. Smoke inhalation is the #1 killer.",
  drought: "During drought: Conserve water — shorter showers, fix leaks, collect rainwater. Agricultural: drought-resistant crops, efficient irrigation. Health: stay hydrated, watch for heat stroke symptoms. Heat stroke signs: hot/dry skin, confusion, no sweating — cool victim with ice packs, call emergency services.",
  heatwave: "Heat safety: Stay in air-conditioned spaces during peak hours (11am-4pm). Wear lightweight, light-colored clothing. Drink water every 15-20 minutes. Never leave children/pets in parked cars. Heat stroke: move victim to cool area, apply cool compresses, give fluids if conscious, call emergency. Vulnerable groups: elderly, infants, chronic illness patients.",
  pandemic: "Pandemic preparedness: Stock 30-day medication supply. Have thermometer and oximeter. Masks (N95+), hand sanitizer, disinfectants. Isolation protocol: separate sick person, dedicated bathroom. Telemedicine setup. Contact tracing cooperation. Vaccination when available. Symptoms monitoring: fever, breathing difficulty = seek medical care.",
  preparedness: "Emergency kit essentials: 3-day water supply (1 gallon/person/day), non-perishable food, first aid kit, flashlight, batteries, whistle, N95 masks, phone charger/power bank, important documents in waterproof container, emergency cash, local maps, prescription medications (7-day supply), blanket.",
  gobag: "Go-bag (72-hour kit): Water (2L/person), energy bars/trail mix, first aid kit, flashlight + batteries, N95 masks (5+), hand sanitizer, emergency blanket, copies of ID/passport/insurance, emergency cash (small bills), phone charger + power bank, change of clothes, important medications, whistle, multi-tool. Keep it near exit, weigh under 15kg.",
  family: "Family Emergency Plan steps: 1) Establish 2 meeting points (near home + farther location). 2) Create printed emergency contact list. 3) Map 2+ evacuation routes from home. 4) Assign roles to each family member. 5) Plan for pets. 6) Address special needs (elderly, infants). 7) Know how to shut off utilities. 8) Practice the plan twice yearly.",
  firstaid: "Basic first aid: Bleeding — apply direct pressure, elevate wound. Burns — cool with running water 20 min, don't use ice or butter. Choking — 5 back blows + 5 abdominal thrusts (Heimlich). Unconscious — check breathing, place in recovery position. Cardiac arrest — CPR: 30 compressions + 2 breaths, 100-120/min. Call emergency services first.",
};

function getChatResponse(msg) {
  const lower = msg.toLowerCase();
  for (const [key, resp] of Object.entries(KB)) {
    if (lower.includes(key) || (key==='gobag' && lower.includes('bag')) || (key==='firstaid' && lower.includes('first aid'))) {
      return '🤖 **' + key.charAt(0).toUpperCase()+key.slice(1) + ' Guidance:**\n\n' + resp + '\n\n📞 **Emergency:** Call 112 / 911 for immediate assistance.';
    }
  }

  // Check against disasters data
  for (const d of DISASTERS_DATA) {
    if (lower.includes(d.name.toLowerCase())) {
      return `🤖 **${d.icon} ${d.name}:**\n\n**Causes:** ${d.causes}\n\n**Warning Signs:** ${d.warning_signs}\n\n**Safety:** ${d.safety_measures}\n\n**First Aid:** ${d.first_aid}\n\n📞 Call emergency services if in danger.`;
    }
  }

  if (lower.includes('contact') || lower.includes('helpline') || lower.includes('number')) {
    return '🤖 **Emergency Numbers:**\n\n🆘 National Emergency: **112**\n🚔 Police: **100**\n🔥 Fire: **101**\n🚑 Ambulance: **102**\n🌊 Coast Guard: **1554**\n🏥 NDRF: **1078**\n\nGo to the Emergency Contacts section for the complete directory.';
  }
  if (lower.includes('shelter')) {
    return '🤖 **Relief Shelters:**\n\nWe have ' + SHELTERS_DATA.length + ' registered shelters worldwide. Key features:\n• 24/7 operation during disasters\n• Food, water, and medical aid available\n• Pet-friendly shelters available\n• GPS coordinates for navigation\n\nVisit the "Relief Shelters" section to find the nearest one to you.';
  }
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
    return '🤖 Hello! I\'m your AI Disaster Assistant. Ask me about:\n• Any disaster type (earthquake, flood, cyclone...)\n• Safety procedures and protocols\n• Emergency preparedness tips\n• First aid guidance\n• Family emergency planning\n\nHow can I help you stay safe today?';
  }

  return `🤖 I can help with disaster safety, preparedness, and emergency response guidance.\n\nTry asking about:\n• Specific disasters: "earthquake safety", "flood preparedness"\n• Emergency kits: "what's in a go-bag"\n• First aid: "how to treat burns"\n• Planning: "family emergency plan"\n\n📞 For immediate emergencies, call **112** now.`;
}

function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  const container = document.getElementById('chat-messages');

  // User bubble
  container.innerHTML += `<div class="msg-user"><div class="msg-bubble">${msg}</div></div>`;

  // Typing indicator
  const typingId = 'typing-' + Date.now();
  container.innerHTML += `<div class="msg-bot" id="${typingId}"><div class="msg-bubble" style="padding:8px 14px"><div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div></div>`;
  container.scrollTop = container.scrollHeight;

  setTimeout(() => {
    document.getElementById(typingId)?.remove();
    const resp = getChatResponse(msg);
    container.innerHTML += `<div class="msg-bot"><div class="msg-bubble">${resp.replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>')}</div></div>`;
    container.scrollTop = container.scrollHeight;
  }, 800 + Math.random() * 600);
}
function askQuick(q) {
  document.getElementById('chat-input').value = q;
  sendChat();
}

// ─── ACCORDION ───
function toggleAcc(header) {
  const body = header.nextElementSibling;
  const icon = header.querySelector('i');
  body.classList.toggle('open');
  icon.style.transform = body.classList.contains('open') ? 'rotate(180deg)' : '';
}

// ─── TOAST ───
function showToast(msg, type='success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  const colors = { success:'#10b981', danger:'#ef4444', warning:'#f97316', info:'#3b82f6' };
  toast.className = 'dm-toast';
  toast.innerHTML = `<i class="fas fa-${type==='success'?'check-circle':type==='danger'?'exclamation-circle':'info-circle'}" style="color:${colors[type]||'#10b981'}"></i> ${msg}`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ─── INIT ───
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('adm-date').value = new Date().toISOString().split('T')[0];
});
</script>
</body>
</html>"""

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    db = get_db()

    disasters     = query("SELECT * FROM disasters ORDER BY id")
    all_events    = query("SELECT de.*,d.icon FROM disaster_events de LEFT JOIN disasters d ON de.disaster_id=d.id ORDER BY de.id DESC")
    recent_events = all_events[:8]
    active_events = query("SELECT COUNT(*) as c FROM disaster_events WHERE status='Active'", one=True)["c"]
    active_alerts = query("SELECT * FROM alerts WHERE is_active=1 ORDER BY id DESC LIMIT 5")
    all_alerts    = query("SELECT * FROM alerts WHERE is_active=1 ORDER BY id DESC")
    contacts      = query("SELECT * FROM emergency_contacts ORDER BY id")
    shelters      = query("SELECT * FROM shelters ORDER BY id")
    users         = query("SELECT * FROM users ORDER BY id")
    checklist_types = [r["disaster_type"] for r in query("SELECT DISTINCT disaster_type FROM preparedness_checklists ORDER BY disaster_type")]

    total_events    = query("SELECT COUNT(*) as c FROM disaster_events", one=True)["c"]
    total_deaths    = query("SELECT COALESCE(SUM(deaths),0) as s FROM disaster_events", one=True)["s"]
    total_affected  = query("SELECT COALESCE(SUM(affected_population),0) as s FROM disaster_events", one=True)["s"]
    total_injured   = query("SELECT COALESCE(SUM(injured),0) as s FROM disaster_events", one=True)["s"]
    countries       = query("SELECT COUNT(DISTINCT country) as c FROM disaster_events", one=True)["c"]
    total_capacity  = sum(s["capacity"] for s in shelters)
    total_occupied  = sum(s["occupied"] for s in shelters)
    total_available = total_capacity - total_occupied
    shelter_available_pct = round((total_available / total_capacity * 100) if total_capacity else 0)

    deadliest = query("""SELECT d.name, SUM(de.deaths) as td FROM disaster_events de
        JOIN disasters d ON de.disaster_id=d.id GROUP BY d.name ORDER BY td DESC LIMIT 1""", one=True)
    deadliest_type = deadliest["name"] if deadliest else "N/A"

    sev_q   = {k: query(f"SELECT COUNT(*) as c FROM disaster_events WHERE severity=?", (k,), one=True)["c"]
               for k in ["Extreme","High","Medium","Low"]}
    total_sev = sum(sev_q.values()) or 1
    severity_counts = {k.lower(): v for k,v in sev_q.items()}
    severity_pct    = {k.lower(): round(v/total_sev*100) for k,v in sev_q.items()}

    # Ticker HTML
    ticker_items = [f'<span class="alert-ticker-item">🔴 {a["title"]} — {a["region"]}</span>' for a in all_alerts[:5]]
    ticker_html  = "".join(ticker_items)

    # JSON for JS
    events_json   = json.dumps([dict(e) for e in all_events])
    shelters_json = json.dumps([dict(s) for s in shelters])
    disasters_json= json.dumps([dict(d) for d in disasters])

    deaths_by_type = [{"name": r["name"], "deaths": r["td"]} for r in
        query("""SELECT d.name, SUM(de.deaths) as td FROM disaster_events de
                 JOIN disasters d ON de.disaster_id=d.id GROUP BY d.name ORDER BY td DESC LIMIT 10""")]
    affected_by_country = [{"country": r["country"], "affected": r["ta"]} for r in
        query("""SELECT country, SUM(affected_population) as ta FROM disaster_events
                 GROUP BY country ORDER BY ta DESC LIMIT 10""")]
    status_counts    = [
        query("SELECT COUNT(*) as c FROM disaster_events WHERE status='Active'", one=True)["c"],
        query("SELECT COUNT(*) as c FROM disaster_events WHERE status='Resolved'", one=True)["c"],
    ]
    severity_counts2 = [sev_q[k] for k in ["Extreme","High","Medium","Low"]]
    shelter_util     = [int(total_occupied), int(total_available)]

    alert_counts = [
        query("SELECT COUNT(*) as c FROM alerts WHERE severity=? AND is_active=1", ("Extreme",), one=True)["c"],
        query("SELECT COUNT(*) as c FROM alerts WHERE severity=? AND is_active=1", ("High",), one=True)["c"],
        query("SELECT COUNT(*) as c FROM alerts WHERE severity=? AND is_active=1", ("Medium",), one=True)["c"],
        query("SELECT COUNT(*) as c FROM alerts WHERE severity=? AND is_active=1", ("Low",), one=True)["c"],
    ]

    stats_json = json.dumps({
        "deaths_by_type": deaths_by_type,
        "affected_by_country": affected_by_country,
        "status_counts": status_counts,
        "severity_counts": severity_counts2,
        "shelter_util": shelter_util,
        "alert_counts": alert_counts,
    })

    affected_m = round(total_affected / 1_000_000, 1)

    return render_template_string(BASE_HTML,
        disasters=disasters, all_events=all_events, recent_events=recent_events,
        active_events=active_events, active_alerts=active_alerts, all_alerts=all_alerts,
        contacts=contacts, shelters=shelters, users=users,
        checklist_types=checklist_types,
        disaster_count=len(disasters), event_count=total_events,
        alert_count=len(all_alerts), shelter_count=len(shelters),
        contact_count=len(contacts),
        total_events=total_events, total_deaths=int(total_deaths),
        total_affected=int(total_affected), total_injured=int(total_injured),
        countries=countries, affected_m=affected_m,
        deadliest_type=deadliest_type,
        total_capacity=total_capacity, total_occupied=total_occupied,
        total_available=total_available, shelter_available_pct=shelter_available_pct,
        severity_counts=severity_counts, severity_pct=severity_pct,
        ticker_html=ticker_html,
        events_json=events_json, shelters_json=shelters_json,
        disasters_json=disasters_json, stats_json=stats_json,
    )

# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────
@app.route("/api/disaster/<int:did>")
def api_disaster(did):
    d = query("SELECT * FROM disasters WHERE id=?", (did,), one=True)
    return jsonify(dict(d) if d else {})

@app.route("/api/checklist/<dtype>")
def api_checklist(dtype):
    items = query("SELECT * FROM preparedness_checklists WHERE disaster_type=? ORDER BY priority DESC, id", (dtype,))
    return jsonify([dict(i) for i in items])

@app.route("/api/alert", methods=["POST"])
def api_add_alert():
    data = request.get_json()
    aid = mutate("INSERT INTO alerts (title,message,severity,region,is_active) VALUES (?,?,?,?,1)",
                 (data["title"], data["message"], data["severity"], data["region"]))
    return jsonify({"success": True, "id": aid})

@app.route("/api/event", methods=["POST"])
def api_add_event():
    d = request.get_json()
    eid = mutate("""INSERT INTO disaster_events
        (disaster_id,title,location,country,latitude,longitude,severity,
         affected_population,injured,deaths,status,reported_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d.get("disaster_id",1), d["title"], d["location"], d.get("country",""), 
         d.get("latitude",0), d.get("longitude",0), d.get("severity","Medium"),
         d.get("affected_population",0), d.get("injured",0), d.get("deaths",0),
         d.get("status","Active"), d.get("reported_date", datetime.now().strftime("%Y-%m-%d"))))
    return jsonify({"success": True, "id": eid})

@app.route("/api/report")
def api_report():
    rtype  = request.args.get("type","Situation Report")
    rrange = request.args.get("range","Last 30 Days")
    region = request.args.get("region","Global")
    fmt    = request.args.get("format","json")

    events   = [dict(r) for r in query("SELECT de.*, d.name as disaster_name FROM disaster_events de LEFT JOIN disasters d ON de.disaster_id=d.id ORDER BY de.id DESC LIMIT 50")]
    shelters = [dict(r) for r in query("SELECT * FROM shelters LIMIT 20")]
    contacts = [dict(r) for r in query("SELECT * FROM emergency_contacts LIMIT 20")]

    total_ev  = len(events)
    total_d   = sum(e.get("deaths",0) or 0 for e in events)
    total_aff = sum(e.get("affected_population",0) or 0 for e in events)

    if fmt == "json":
        return jsonify({
            "report": {"type": rtype, "range": rrange, "region": region, "generated": datetime.now().isoformat()},
            "summary": {"total_events": total_ev, "total_deaths": int(total_d), "total_affected": int(total_aff)},
            "events": events[:20],
            "shelters": shelters[:10],
            "emergency_contacts": contacts[:10],
        })
    elif fmt == "csv":
        headers = ["id","title","location","country","severity","affected_population","deaths","status","reported_date"]
        rows = [[str(e.get(h,"")) for h in headers] for e in events[:30]]
        return jsonify({"headers": headers, "rows": rows})
    else:
        text = f"""
╔══════════════════════════════════════════════════════════════════╗
║  DISASTERWATCH PRO — {rtype.upper():<41} ║
╚══════════════════════════════════════════════════════════════════╝

Generated:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Region:       {region}
Date Range:   {rrange}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Events Tracked:     {total_ev:>10,}
Total Deaths Recorded:    {int(total_d):>10,}
Total People Affected:    {int(total_aff):>10,}
Active Events:            {sum(1 for e in events if e.get('status')=='Active'):>10}
Resolved Events:          {sum(1 for e in events if e.get('status')=='Resolved'):>10}
Shelters Monitored:       {len(shelters):>10}
Emergency Contacts:       {len(contacts):>10}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOP 10 RECENT EVENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{'Event':<35} {'Country':<15} {'Severity':<10} {'Affected':>12} {'Deaths':>8}
{'-'*80}
"""
        for e in events[:10]:
            text += f"{str(e.get('title',''))[:34]:<35} {str(e.get('country',''))[:14]:<15} {str(e.get('severity','')):<10} {int(e.get('affected_population',0)):>12,} {int(e.get('deaths',0)):>8,}\n"
        text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nDisasterWatch Pro v2.0 Enterprise | Confidential\n"
        return jsonify({"text": text})

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n╔══════════════════════════════════════════╗")
    print("║  🌍 DisasterWatch Pro v2.0 Enterprise    ║")
    print("╠══════════════════════════════════════════╣")
    print("║  URL:  http://127.0.0.1:5000             ║")
    print("║  DB:   disaster_mgmt.db (auto-seeded)    ║")
    print("║  Admin: admin@disaster.gov / admin123    ║")
    print("╚══════════════════════════════════════════╝\n")
    app.run()

    # ─────────────────────────────────────────────
# ADDITIONAL HELPER ROUTES (for completeness)
# ─────────────────────────────────────────────

@app.route("/api/stats")
def api_stats():
    db = get_db()
    stats = {
        "total_events": query("SELECT COUNT(*) as c FROM disaster_events", one=True)["c"],
        "active_events": query("SELECT COUNT(*) as c FROM disaster_events WHERE status='Active'", one=True)["c"],
        "total_deaths": query("SELECT COALESCE(SUM(deaths),0) as s FROM disaster_events", one=True)["s"],
        "total_affected": query("SELECT COALESCE(SUM(affected_population),0) as s FROM disaster_events", one=True)["s"],
    }
    return jsonify(stats)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = query("SELECT * FROM users WHERE email=? AND password=?", 
                 (email, hash_pw(password)), one=True)
    if user:
        session["user_id"] = user["id"]
        session["role"] = user["role"]
        return jsonify({"success": True, "role": user["role"]})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return """
    <h2 style="text-align:center;margin-top:100px;color:#f97316">
        404 — Page Not Found<br><br>
        <a href="/" style="color:#3b82f6">← Back to Dashboard</a>
    </h2>
    """, 404


@app.errorhandler(500)
def server_error(error):
    return """
    <h2 style="text-align:center;margin-top:100px;color:#ef4444">
        500 — Internal Server Error<br><br>
        Please check the console.
    </h2>
    """, 500


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n" + "═"*60)
    print("🌍 DisasterWatch Pro v2.0 Enterprise")
    print("═"*60)
    print("✅ Database initialized & seeded")
    print("🌐 Server running at: http://127.0.0.1:5000")
    print("👤 Admin Login → admin@disaster.gov / admin123")
    print("🔧 Debug mode: ON")
    print("═"*60 + "\n")
    
    # Run the app
    app.run()
