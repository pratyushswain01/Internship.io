"""
╔══════════════════════════════════════════════════════════════════════════╗
║   🌍 DISASTER MANAGEMENT & EMERGENCY RESPONSE DASHBOARD                 ║
║   Streamlit Version — Converted from Flask v2.0 Enterprise              ║
╚══════════════════════════════════════════════════════════════════════════╝

Run:  streamlit run disaster_streamlit.py
Install: pip install streamlit plotly pandas
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DisasterWatch Pro — Emergency Management",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #0d1322; }
[data-testid="stSidebar"] .stMarkdown p { color: #94a3b8; font-size: 12px; }
h1,h2,h3 { color: #f1f5f9 !important; }
.metric-card {
    background: #111827; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 18px; text-align: center;
}
.metric-val { font-size: 28px; font-weight: 800; font-family: monospace; }
.metric-lbl { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.pill-red    { background:#ef444422;color:#ef4444;border:1px solid #ef444444;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700; }
.pill-orange { background:#f9731622;color:#f97316;border:1px solid #f9731644;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700; }
.pill-green  { background:#10b98122;color:#10b981;border:1px solid #10b98144;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700; }
.pill-yellow { background:#eab30822;color:#eab308;border:1px solid #eab30844;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700; }
.pill-blue   { background:#3b82f622;color:#3b82f6;border:1px solid #3b82f644;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700; }
.alert-box-extreme { border-left:4px solid #ef4444;background:#ef444411;padding:14px 18px;border-radius:8px;margin-bottom:10px; }
.alert-box-high    { border-left:4px solid #f97316;background:#f9731611;padding:14px 18px;border-radius:8px;margin-bottom:10px; }
.alert-box-medium  { border-left:4px solid #eab308;background:#eab30811;padding:14px 18px;border-radius:8px;margin-bottom:10px; }
.alert-box-low     { border-left:4px solid #10b981;background:#10b98111;padding:14px 18px;border-radius:8px;margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATABASE  (same schema / seed as Flask app)
# ─────────────────────────────────────────────
DB_PATH = "disaster_mgmt.db"

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
    ("Pandemic","Biological","Worldwide spread of a new infectious disease.",
     "Novel pathogens, globalization, zoonotic spillover, mutation",
     "Unusual disease clusters, rapid spread, mortality spikes",
     "Mass casualties, economic collapse, healthcare overwhelm",
     "Vaccination, mask wearing, quarantine, social distancing",
     "Isolate patients, supportive care, contact tracing","🦠","#1abc9c"),
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
]

EVENTS_SEED = [
    (1,"Nepal Earthquake 2024","Jajarkot, Nepal","Nepal",28.8,82.2,"High",120000,3500,157,"Resolved","2024-11-03"),
    (2,"Bangladesh Flooding","Sylhet, Bangladesh","Bangladesh",24.9,91.8,"Extreme",500000,12000,89,"Active","2025-06-01"),
    (3,"Cyclone Tej","Andhra Pradesh, India","India",16.5,80.6,"High",200000,4500,34,"Resolved","2024-10-23"),
    (4,"Japan Tsunami Warning","Ishikawa, Japan","Japan",37.2,137.0,"Medium",80000,1200,15,"Active","2025-01-01"),
    (5,"California Wildfire","Los Angeles, USA","USA",34.0,-118.2,"Extreme",150000,890,28,"Active","2025-01-10"),
    (6,"East Africa Drought","Turkana, Kenya","Kenya",3.1,35.6,"High",3000000,200000,1200,"Active","2024-09-01"),
    (7,"Papua New Guinea Landslide","Enga Province, PNG","Papua New Guinea",-5.4,143.2,"Extreme",8000,600,316,"Resolved","2024-05-24"),
    (8,"Iceland Volcanic Eruption","Reykjanes Peninsula","Iceland",63.8,-22.4,"Medium",30000,200,0,"Active","2024-12-18"),
    (9,"India Heatwave","Rajasthan, India","India",26.9,75.8,"High",5000000,45000,234,"Resolved","2024-05-15"),
    (10,"COVID-19 Resurgence","Multiple Regions","Global",0.0,0.0,"Extreme",50000000,2000000,15000,"Active","2024-08-01"),
    (11,"Turkey Earthquake","Kahramanmaras, Turkey","Turkey",37.5,36.9,"Extreme",1800000,107000,50783,"Resolved","2023-02-06"),
    (5,"Greece Wildfire","Thessaly, Greece","Greece",39.6,22.4,"High",90000,2000,26,"Resolved","2023-07-25"),
    (10,"Mpox Outbreak","DRC","Congo",-4.3,15.3,"High",500000,50000,1200,"Active","2024-08-14"),
    (8,"Indonesia Volcano","Marapi, Indonesia","Indonesia",-0.4,100.5,"High",150000,3000,24,"Resolved","2023-12-03"),
    (2,"Pakistan Monsoon Flood","Sindh, Pakistan","Pakistan",25.9,68.4,"Extreme",2000000,80000,456,"Active","2025-07-10"),
    (6,"Somalia Drought","Baidoa, Somalia","Somalia",3.1,43.6,"Extreme",8000000,1000000,4500,"Active","2024-01-01"),
    (6,"Ethiopia Drought","Oromia, Ethiopia","Ethiopia",7.5,40.0,"Extreme",10000000,2000000,5000,"Active","2024-02-01"),
    (1,"Morocco Earthquake","Marrakesh, Morocco","Morocco",31.6,-7.9,"Extreme",500000,5600,2960,"Resolved","2023-09-08"),
    (1,"Afghanistan Earthquake","Herat, Afghanistan","Afghanistan",34.3,62.2,"Extreme",250000,10000,1480,"Resolved","2023-10-07"),
    (5,"Australia Bushfire","Victoria, Australia","Australia",-37.8,144.9,"Extreme",300000,4000,33,"Resolved","2020-01-01"),
]

CONTACTS_SEED = [
    ("National Disaster Response Force (NDRF)","1078","ndrf@gov.in","https://ndrf.gov.in","Government",1),
    ("National Emergency Number","112","help@112.gov.in","https://112.gov.in","Emergency",1),
    ("Police","100","police@gov.in","https://police.gov.in","Law Enforcement",1),
    ("Fire Brigade","101","fire@gov.in","https://fireservices.gov.in","Fire & Rescue",1),
    ("Ambulance","102","ambulance@gov.in","https://health.gov.in","Medical",1),
    ("Women Helpline","1091","women@gov.in","https://wcd.nic.in","Social Services",1),
    ("Child Helpline","1098","childline@gov.in","https://childlineindia.org","Social Services",1),
    ("Mental Health Helpline","iCall: 9152987821","icall@iitb.ac.in","https://icallhelpline.org","Medical",1),
    ("Coast Guard","1554","coastguard@gov.in","https://indiancoastguard.gov.in","Rescue",1),
    ("Indian Red Cross Society","+91-11-23711551","info@indianredcross.org","https://indianredcross.org","NGO",1),
    ("UNICEF India","+91-11-24673400","unicefindia@unicef.org","https://unicef.org/india","NGO",1),
    ("WHO India","+91-11-23370804","searo@who.int","https://who.int/india","Health",1),
    ("FEMA (USA)","1-800-621-FEMA","fema@dhs.gov","https://fema.gov","Government",1),
    ("American Red Cross","1-800-RED-CROSS","info@redcross.org","https://redcross.org","NGO",1),
    ("UN OCHA","+1-212-963-1234","ocha@un.org","https://unocha.org","International",1),
    ("Doctors Without Borders","+1-212-679-6800","info@msf.org","https://msf.org","Medical NGO",1),
    ("NDMA India","011-26701700","ndma@gov.in","https://ndma.gov.in","Government",1),
    ("IMD (Weather)","1800-180-1717","imd@gov.in","https://imd.gov.in","Weather",1),
]

SHELTERS_SEED = [
    ("Rajpath Community Center","Rajpath, New Delhi","New Delhi",500,120,28.6139,77.2090,"Food,Water,Medical,Beds","Open"),
    ("Yamuna Flood Relief Camp","ITO, New Delhi","New Delhi",1000,450,28.6280,77.2416,"Food,Water,Beds,Toilets","Open"),
    ("NCC Ground Shelter","MG Marg, Mumbai","Mumbai",800,200,19.0760,72.8777,"Food,Water,Medical","Open"),
    ("Bandra Relief Center","Bandra West, Mumbai","Mumbai",600,310,19.0596,72.8295,"Food,Water,Beds","Open"),
    ("Chennai Flood Shelter","Marina Beach Road","Chennai",1200,890,13.0827,80.2707,"Food,Water,Medical,Beds","Open"),
    ("Kolkata Emergency Shelter","Salt Lake, Kolkata","Kolkata",700,234,22.5726,88.3639,"Food,Water,Beds","Open"),
    ("FEMA Shelter Houston","Reliant Center, Houston","Houston",5000,1200,29.6697,-95.4097,"Food,Water,Medical,Beds,WiFi","Open"),
    ("LA Earthquake Relief","Staples Center, LA","Los Angeles",8000,3400,34.0430,-118.2673,"Food,Water,Medical,Beds","Open"),
    ("Tokyo Disaster Shelter","Yoyogi Park, Tokyo","Tokyo",20000,5600,35.6762,139.6503,"Food,Water,Medical,Beds,WiFi","Open"),
    ("Manila Typhoon Shelter","Luneta Park, Manila","Manila",15000,8900,14.5893,120.9786,"Food,Water,Medical,Beds","Open"),
]

CHECKLISTS_SEED = [
    ("Earthquake","Emergency water supply (1 gal/person/day × 3 days)","Store in sealed containers","High"),
    ("Earthquake","Non-perishable food (3-day supply)","Canned goods, energy bars","High"),
    ("Earthquake","First aid kit","Bandages, antiseptic, medications","High"),
    ("Earthquake","Flashlight and extra batteries","LED flashlight preferred","High"),
    ("Earthquake","N95 Dust masks","To filter contaminated air","High"),
    ("Earthquake","Wrench or pliers to turn off utilities","Keep near gas meter","High"),
    ("Earthquake","Important documents in waterproof container","ID, insurance, medical records","High"),
    ("Flood","Waterproof bags for important documents","Keep electronics dry","High"),
    ("Flood","Rubber boots and waterproof clothing","Protection from contaminated water","High"),
    ("Flood","Water purification tablets","For emergency water treatment","High"),
    ("Flood","Emergency flotation device","Life jacket or ring buoy","High"),
    ("Flood","Battery-powered radio","For emergency broadcasts","High"),
    ("Cyclone","Board up windows and doors","Use storm shutters or plywood","High"),
    ("Cyclone","Secure outdoor furniture and objects","Bring inside or tie down","High"),
    ("Cyclone","Fill bathtub with water","Emergency water reserve","High"),
    ("Cyclone","Identify interior room for shelter","Away from windows","High"),
    ("Pandemic","N95 or higher masks (30-day supply)","One per person per day","High"),
    ("Pandemic","Hand sanitizer (70%+ alcohol)","Multiple bottles","High"),
    ("Pandemic","30-day prescription medication supply","Contact doctor in advance","High"),
    ("Pandemic","Thermometer and oximeter","Monitor symptoms","High"),
    ("Wildfire","Go-bag packed and ready","Can leave in 5 minutes","High"),
    ("Wildfire","N95 masks for smoke","Smoke protection","High"),
    ("Wildfire","Evacuation routes mapped","Know 2+ ways out","High"),
    ("General","Emergency contact list printed","Don't rely only on phone","High"),
    ("General","Meeting point designated","Family reunion location","High"),
    ("General","Emergency cash reserve","ATMs may not work","Medium"),
]

ALERTS_SEED = [
    ("Cyclone Warning - Bay of Bengal","Category 3 cyclone developing. Coastal areas on high alert.","High","Eastern India"),
    ("Flood Alert - Brahmaputra Basin","Water levels rising rapidly. Evacuation advisories issued.","Extreme","Assam, India"),
    ("Earthquake Risk - Himalayan Belt","Minor tremors detected. Stay prepared, avoid old structures.","Medium","North India"),
    ("Heat Wave Warning","Temperature expected to exceed 45°C. Stay hydrated.","High","Rajasthan, India"),
    ("Landslide Alert","Heavy rainfall may trigger landslides. Avoid hill travel.","Medium","Western Ghats"),
]

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS disasters (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT,
        description TEXT, causes TEXT, warning_signs TEXT, impact TEXT,
        safety_measures TEXT, first_aid TEXT, icon TEXT DEFAULT '⚠️', color TEXT DEFAULT '#e74c3c'
    );
    CREATE TABLE IF NOT EXISTS disaster_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, disaster_id INTEGER, title TEXT,
        location TEXT, country TEXT, latitude REAL, longitude REAL, severity TEXT,
        affected_population INTEGER DEFAULT 0, injured INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0, status TEXT DEFAULT 'Active', reported_date TEXT
    );
    CREATE TABLE IF NOT EXISTS emergency_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, department TEXT, phone TEXT,
        email TEXT, website TEXT, category TEXT, available_24h INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS shelters (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, address TEXT, city TEXT,
        capacity INTEGER, occupied INTEGER DEFAULT 0, latitude REAL, longitude REAL,
        amenities TEXT, status TEXT DEFAULT 'Open'
    );
    CREATE TABLE IF NOT EXISTS preparedness_checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT, disaster_type TEXT, item_name TEXT,
        description TEXT, priority TEXT DEFAULT 'High'
    );
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, message TEXT,
        severity TEXT, region TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, is_active INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE,
        password TEXT, role TEXT DEFAULT 'user'
    );
    """)
    conn.executemany("INSERT INTO disasters (name,category,description,causes,warning_signs,impact,safety_measures,first_aid,icon,color) VALUES (?,?,?,?,?,?,?,?,?,?)", DISASTERS_SEED)
    conn.executemany("INSERT INTO disaster_events (disaster_id,title,location,country,latitude,longitude,severity,affected_population,injured,deaths,status,reported_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", EVENTS_SEED)
    conn.executemany("INSERT INTO emergency_contacts (department,phone,email,website,category,available_24h) VALUES (?,?,?,?,?,?)", CONTACTS_SEED)
    conn.executemany("INSERT INTO shelters (name,address,city,capacity,occupied,latitude,longitude,amenities,status) VALUES (?,?,?,?,?,?,?,?,?)", SHELTERS_SEED)
    conn.executemany("INSERT INTO preparedness_checklists (disaster_type,item_name,description,priority) VALUES (?,?,?,?)", CHECKLISTS_SEED)
    conn.executemany("INSERT INTO alerts (title,message,severity,region,is_active) VALUES (?,?,?,?,1)", ALERTS_SEED)
    conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)", ("Admin","admin@disaster.gov",hash_pw("admin123"),"admin"))
    conn.commit()
    conn.close()

def qdf(sql, params=()):
    """Run a SELECT and return a DataFrame."""
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)

def mutate(sql, params=()):
    """Run INSERT/UPDATE/DELETE."""
    conn = get_connection()
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.lastrowid

# ─────────────────────────────────────────────
# SEVERITY HELPERS
# ─────────────────────────────────────────────
SEV_COLOR = {"Extreme":"🔴","High":"🟠","Medium":"🟡","Low":"🟢"}
SEV_PILL  = {"Extreme":"pill-red","High":"pill-orange","Medium":"pill-yellow","Low":"pill-green"}

def sev_pill(s):
    cls = SEV_PILL.get(s,"pill-blue")
    ico = SEV_COLOR.get(s,"⚪")
    return f'<span class="{cls}">{ico} {s}</span>'

# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = "guest"
    st.session_state.user_name = "Guest"
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 20px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:8px'>
        <div style='font-size:36px'>🌍</div>
        <div style='color:#f1f5f9;font-size:16px;font-weight:800;margin-top:6px'>DisasterWatch Pro</div>
        <div style='color:#94a3b8;font-size:11px'>Emergency Response Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📊 Overview**")
    pages_overview = ["Dashboard", "Disaster Encyclopedia"]
    for p in pages_overview:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

    st.markdown("**📡 Monitoring**")
    pages_monitor = ["Live Disaster Events", "Active Alerts", "Risk Assessment"]
    for p in pages_monitor:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

    st.markdown("**🛡️ Resources**")
    pages_res = ["Preparedness Center", "Emergency Contacts", "Relief Shelters"]
    for p in pages_res:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

    st.markdown("**⚙️ Admin**")
    pages_admin = ["Add Event", "Add Alert", "Login"]
    for p in pages_admin:
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p

    st.divider()
    if st.session_state.logged_in:
        st.success(f"✅ {st.session_state.user_name} ({st.session_state.user_role})")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_role = "guest"
            st.session_state.user_name = "Guest"
            st.rerun()
    else:
        st.info("🔒 Not logged in")

page = st.session_state.page

# ════════════════════════════════════════════
# PAGE: DASHBOARD
# ════════════════════════════════════════════
if page == "Dashboard":
    st.title("🌍 Disaster Management Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")

    # ── Active alerts banner ──
    alerts_df = qdf("SELECT * FROM alerts WHERE is_active=1 ORDER BY id DESC LIMIT 3")
    if not alerts_df.empty:
        for _, row in alerts_df.iterrows():
            sev = row["severity"].lower()
            st.markdown(f"""
            <div class="alert-box-{sev}">
                <b>🔔 {row['title']}</b> &nbsp;
                <span style='color:#94a3b8;font-size:12px'>{row['region']}</span><br>
                <span style='font-size:13px;color:#cbd5e1'>{row['message']}</span>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── KPI metrics ──
    ev_df   = qdf("SELECT * FROM disaster_events")
    sh_df   = qdf("SELECT * FROM shelters")
    tot_ev  = len(ev_df)
    active  = int((ev_df["status"]=="Active").sum())
    deaths  = int(ev_df["deaths"].sum())
    aff     = int(ev_df["affected_population"].sum())
    inj     = int(ev_df["injured"].sum())
    countries = ev_df["country"].nunique()
    tot_cap = int(sh_df["capacity"].sum())
    tot_occ = int(sh_df["occupied"].sum())
    avail   = tot_cap - tot_occ
    avail_pct = round(avail/tot_cap*100) if tot_cap else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1:
        st.metric("📋 Total Events", f"{tot_ev:,}")
    with c2:
        st.metric("🔴 Active Events", f"{active}")
    with c3:
        st.metric("💀 Total Deaths", f"{deaths:,}")
    with c4:
        st.metric("👥 Affected (M)", f"{aff/1_000_000:.1f}M")
    with c5:
        st.metric("🏥 Injured", f"{inj:,}")
    with c6:
        st.metric("🌐 Countries", f"{countries}")

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📍 Global Disaster Map")
        map_df = ev_df[(ev_df["latitude"] != 0) | (ev_df["longitude"] != 0)].copy()
        sev_colors = {"Extreme":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#10b981"}
        map_df["color"] = map_df["severity"].map(sev_colors).fillna("#94a3b8")
        map_df["size"]  = map_df["affected_population"].fillna(0).clip(lower=10000) / 50000 + 5

        fig_map = px.scatter_mapbox(
            map_df, lat="latitude", lon="longitude",
            hover_name="title", hover_data={"country":True,"severity":True,"deaths":True,"status":True,"latitude":False,"longitude":False},
            color="severity",
            color_discrete_map=sev_colors,
            size="size", size_max=25,
            zoom=1, height=420,
            mapbox_style="carto-darkmatter",
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", legend_font_color="#94a3b8")
        st.plotly_chart(fig_map, use_container_width=True)

    with col_right:
        st.subheader("📊 Severity Breakdown")
        sev_counts = ev_df["severity"].value_counts().reindex(["Extreme","High","Medium","Low"], fill_value=0)
        fig_pie = go.Figure(go.Pie(
            labels=sev_counts.index, values=sev_counts.values,
            marker_colors=["#ef4444","#f97316","#eab308","#10b981"],
            hole=0.5, textinfo="label+percent",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8", showlegend=False, height=200, margin=dict(t=0,b=0,l=0,r=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("🏠 Shelter Utilization")
        fig_sh = go.Figure(go.Pie(
            labels=["Occupied","Available"], values=[tot_occ, avail],
            marker_colors=["#f97316","#10b981"], hole=0.55,
            textinfo="label+percent",
        ))
        fig_sh.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8",
            showlegend=False, height=200, margin=dict(t=0,b=0,l=0,r=0)
        )
        st.plotly_chart(fig_sh, use_container_width=True)
        st.caption(f"Total capacity: {tot_cap:,} | Available: {avail:,} ({avail_pct}%)")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("💀 Deaths by Disaster Type")
        deaths_df = qdf("""SELECT d.name, SUM(de.deaths) as total_deaths
            FROM disaster_events de JOIN disasters d ON de.disaster_id=d.id
            GROUP BY d.name ORDER BY total_deaths DESC LIMIT 10""")
        fig_bar = px.bar(deaths_df, x="total_deaths", y="name", orientation="h",
                         color="total_deaths", color_continuous_scale="Reds",
                         labels={"total_deaths":"Deaths","name":""})
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color="#94a3b8", coloraxis_showscale=False,
                               height=320, margin=dict(t=0,b=0,l=0,r=0))
        fig_bar.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
        fig_bar.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.subheader("🌍 Most Affected Countries")
        country_df = qdf("""SELECT country, SUM(affected_population) as total_affected
            FROM disaster_events GROUP BY country ORDER BY total_affected DESC LIMIT 10""")
        fig_c = px.bar(country_df, x="total_affected", y="country", orientation="h",
                       color="total_affected", color_continuous_scale="Blues",
                       labels={"total_affected":"Affected","country":""})
        fig_c.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="#94a3b8", coloraxis_showscale=False,
                             height=320, margin=dict(t=0,b=0,l=0,r=0))
        fig_c.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
        fig_c.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
        st.plotly_chart(fig_c, use_container_width=True)

    st.divider()
    st.subheader("🕒 Recent Disaster Events")
    recent = qdf("""SELECT de.title, de.country, de.severity, de.affected_population,
                        de.deaths, de.status, de.reported_date, d.icon
                    FROM disaster_events de LEFT JOIN disasters d ON de.disaster_id=d.id
                    ORDER BY de.id DESC LIMIT 10""")
    recent["severity_fmt"] = recent["severity"].map(lambda s: SEV_COLOR.get(s,"⚪")+" "+s)
    recent["status_fmt"]   = recent["status"].map(lambda s: "🔴 "+s if s=="Active" else "✅ "+s)
    st.dataframe(
        recent[["icon","title","country","severity_fmt","affected_population","deaths","status_fmt","reported_date"]]
        .rename(columns={"icon":"","title":"Event","country":"Country",
                         "severity_fmt":"Severity","affected_population":"Affected",
                         "deaths":"Deaths","status_fmt":"Status","reported_date":"Date"}),
        use_container_width=True, hide_index=True
    )

# ════════════════════════════════════════════
# PAGE: DISASTER ENCYCLOPEDIA
# ════════════════════════════════════════════
elif page == "Disaster Encyclopedia":
    st.title("📚 Disaster Encyclopedia")
    st.caption("Click any disaster to explore details, causes, warning signs, safety measures and first aid.")

    dis_df = qdf("SELECT * FROM disasters ORDER BY id")
    search = st.text_input("🔍 Search disasters…", placeholder="e.g. Earthquake, Flood…")
    if search:
        dis_df = dis_df[dis_df["name"].str.contains(search, case=False)]

    cols = st.columns(4)
    selected = st.session_state.get("enc_selected", None)

    for i, row in dis_df.iterrows():
        with cols[i % 4]:
            if st.button(f"{row['icon']} {row['name']}\n*{row['category']}*",
                         key=f"enc_{row['id']}", use_container_width=True):
                st.session_state.enc_selected = int(row["id"])
                selected = int(row["id"])

    if selected:
        st.divider()
        d = qdf("SELECT * FROM disasters WHERE id=?", (selected,)).iloc[0]
        st.subheader(f"{d['icon']} {d['name']}")
        st.caption(f"Category: **{d['category']}**")

        c1, c2 = st.columns(2)
        with c1:
            with st.expander("📖 Description", expanded=True):
                st.write(d["description"])
            with st.expander("⚡ Causes"):
                for item in d["causes"].split(","):
                    st.markdown(f"- {item.strip()}")
            with st.expander("⚠️ Warning Signs"):
                for item in d["warning_signs"].split(","):
                    st.markdown(f"- {item.strip()}")
        with c2:
            with st.expander("💥 Impact"):
                for item in d["impact"].split(","):
                    st.markdown(f"- {item.strip()}")
            with st.expander("🛡️ Safety Measures"):
                for item in d["safety_measures"].split(","):
                    st.markdown(f"- {item.strip()}")
            with st.expander("🏥 First Aid"):
                for item in d["first_aid"].split(","):
                    st.markdown(f"- {item.strip()}")

# ════════════════════════════════════════════
# PAGE: LIVE DISASTER EVENTS
# ════════════════════════════════════════════
elif page == "Live Disaster Events":
    st.title("📡 Live Disaster Events")

    ev_df = qdf("""SELECT de.*, d.name as disaster_name, d.icon
                   FROM disaster_events de LEFT JOIN disasters d ON de.disaster_id=d.id
                   ORDER BY de.id DESC""")

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All","Active","Resolved"])
    with col2:
        sev_filter = st.selectbox("Severity", ["All","Extreme","High","Medium","Low"])
    with col3:
        country_filter = st.text_input("Country filter", "")

    filtered = ev_df.copy()
    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]
    if sev_filter != "All":
        filtered = filtered[filtered["severity"] == sev_filter]
    if country_filter:
        filtered = filtered[filtered["country"].str.contains(country_filter, case=False)]

    st.caption(f"Showing {len(filtered)} of {len(ev_df)} events")

    for _, row in filtered.iterrows():
        sev = row["severity"]
        sev_ico = SEV_COLOR.get(sev,"⚪")
        status_ico = "🔴" if row["status"]=="Active" else "✅"
        with st.expander(f"{row['icon']} {row['title']} — {row['country']} {sev_ico}{sev} {status_ico}{row['status']}"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Affected", f"{int(row['affected_population']):,}")
            c2.metric("Injured",  f"{int(row['injured']):,}")
            c3.metric("Deaths",   f"{int(row['deaths']):,}")
            c4.metric("Date",     row["reported_date"])
            st.caption(f"📍 {row['location']}  |  Type: {row['disaster_name']}")

# ════════════════════════════════════════════
# PAGE: ACTIVE ALERTS
# ════════════════════════════════════════════
elif page == "Active Alerts":
    st.title("🔔 Active Alerts")

    alerts_df = qdf("SELECT * FROM alerts WHERE is_active=1 ORDER BY id DESC")
    if alerts_df.empty:
        st.info("No active alerts at this time.")
    else:
        for _, row in alerts_df.iterrows():
            sev = row["severity"].lower()
            ico = {"extreme":"🔴","high":"🟠","medium":"🟡","low":"🟢"}.get(sev,"⚪")
            st.markdown(f"""
            <div class="alert-box-{sev}">
                <b>{ico} {row['title']}</b>
                <span style='float:right;font-size:11px;color:#94a3b8'>📍 {row['region']}</span><br>
                <p style='margin:6px 0 0;font-size:13px;color:#cbd5e1'>{row['message']}</p>
                <div style='font-size:10px;color:#64748b;margin-top:8px;font-family:monospace'>{row.get('created_at','')}</div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# PAGE: RISK ASSESSMENT
# ════════════════════════════════════════════
elif page == "Risk Assessment":
    st.title("⚠️ Risk Assessment")

    ev_df = qdf("SELECT * FROM disaster_events")
    dis_df = qdf("SELECT * FROM disasters")

    st.subheader("Global Risk Overview")
    sev_counts = ev_df["severity"].value_counts().reindex(["Extreme","High","Medium","Low"], fill_value=0)
    total = sev_counts.sum() or 1

    for sev, cnt in sev_counts.items():
        pct = int(cnt/total*100)
        color = {"Extreme":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#10b981"}.get(sev,"#94a3b8")
        st.markdown(f"**{SEV_COLOR.get(sev,'')} {sev}** — {cnt} events ({pct}%)")
        st.progress(pct/100)

    st.divider()
    st.subheader("Events by Disaster Type")
    type_df = qdf("""SELECT d.name, d.icon, COUNT(de.id) as event_count,
                        SUM(de.deaths) as total_deaths, SUM(de.affected_population) as total_affected
                     FROM disasters d LEFT JOIN disaster_events de ON d.id=de.disaster_id
                     GROUP BY d.id ORDER BY event_count DESC""")
    fig = px.treemap(type_df, path=["name"], values="event_count",
                     color="total_deaths", color_continuous_scale="Reds",
                     hover_data=["total_affected","total_deaths"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f1f5f9",
                      margin=dict(t=0,b=0,l=0,r=0), height=400)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════
# PAGE: PREPAREDNESS CENTER
# ════════════════════════════════════════════
elif page == "Preparedness Center":
    st.title("🏥 Preparedness Center")

    cl_df = qdf("SELECT DISTINCT disaster_type FROM preparedness_checklists ORDER BY disaster_type")
    dtype = st.selectbox("Select Disaster Type", cl_df["disaster_type"].tolist())

    items = qdf("SELECT * FROM preparedness_checklists WHERE disaster_type=? ORDER BY priority DESC, id",
                (dtype,))

    st.subheader(f"✅ {dtype} Preparedness Checklist")
    progress = 0
    checked_count = 0

    for _, row in items.iterrows():
        key = f"chk_{row['id']}"
        if key not in st.session_state:
            st.session_state[key] = False
        col1, col2 = st.columns([1, 12])
        with col1:
            checked = st.checkbox("", key=key)
            if checked:
                checked_count += 1
        with col2:
            prio_color = {"High":"🔴","Medium":"🟡","Low":"🟢"}.get(row["priority"],"⚪")
            st.markdown(f"**{row['item_name']}** {prio_color}")
            st.caption(row["description"])

    total_items = len(items)
    if total_items > 0:
        pct = int(checked_count / total_items * 100)
        st.divider()
        st.subheader(f"Progress: {checked_count}/{total_items} ({pct}%)")
        st.progress(pct/100)
        if pct == 100:
            st.success("🎉 You're fully prepared!")
        elif pct >= 70:
            st.warning("⚠️ Almost there — finish the remaining items!")
        else:
            st.error("🚨 Critical items still pending!")

# ════════════════════════════════════════════
# PAGE: EMERGENCY CONTACTS
# ════════════════════════════════════════════
elif page == "Emergency Contacts":
    st.title("📞 Emergency Contacts")

    con_df = qdf("SELECT * FROM emergency_contacts ORDER BY category, id")
    cat_filter = st.selectbox("Filter by Category", ["All"] + sorted(con_df["category"].unique().tolist()))

    if cat_filter != "All":
        con_df = con_df[con_df["category"] == cat_filter]

    for cat, group in con_df.groupby("category"):
        st.subheader(f"🏷️ {cat}")
        cols = st.columns(3)
        for i, (_, row) in enumerate(group.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style='background:#111827;border:1px solid rgba(255,255,255,0.07);
                            border-radius:12px;padding:16px;margin-bottom:12px'>
                    <div style='font-size:13px;font-weight:700;color:#f1f5f9;margin-bottom:6px'>
                        {row['department']}
                    </div>
                    <div style='font-size:22px;font-weight:800;font-family:monospace;
                                color:#f97316;margin-bottom:8px'>{row['phone']}</div>
                    <a href='{row['website']}' target='_blank'
                       style='color:#3b82f6;font-size:12px'>🔗 Website</a>
                    {"&nbsp;&nbsp;<span style='color:#10b981;font-size:11px'>✅ 24/7</span>" if row['available_24h'] else ""}
                </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# PAGE: RELIEF SHELTERS
# ════════════════════════════════════════════
elif page == "Relief Shelters":
    st.title("🏠 Relief Shelters")

    sh_df = qdf("SELECT * FROM shelters ORDER BY city")
    city_filter = st.selectbox("Filter by City", ["All"] + sorted(sh_df["city"].unique().tolist()))
    if city_filter != "All":
        sh_df = sh_df[sh_df["city"] == city_filter]

    # Map
    st.subheader("📍 Shelter Locations")
    sh_map = sh_df[(sh_df["latitude"]!=0) | (sh_df["longitude"]!=0)].copy()
    sh_map["util_pct"] = (sh_map["occupied"]/sh_map["capacity"]*100).round(1)
    fig_sh = px.scatter_mapbox(
        sh_map, lat="latitude", lon="longitude",
        hover_name="name", hover_data={"city":True,"capacity":True,"occupied":True,"util_pct":True,"latitude":False,"longitude":False},
        color="util_pct", color_continuous_scale="RdYlGn_r",
        size_max=15, zoom=1, height=350, mapbox_style="carto-darkmatter",
    )
    fig_sh.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sh, use_container_width=True)

    st.subheader("🏠 Shelter Details")
    cols = st.columns(3)
    for i, (_, row) in enumerate(sh_df.iterrows()):
        util_pct = int(row["occupied"]/row["capacity"]*100) if row["capacity"] else 0
        bar_color = "#ef4444" if util_pct > 80 else "#f97316" if util_pct > 60 else "#10b981"
        with cols[i % 3]:
            st.markdown(f"""
            <div style='background:#111827;border:1px solid rgba(255,255,255,0.07);
                        border-radius:12px;padding:16px;margin-bottom:12px'>
                <div style='font-size:14px;font-weight:700;color:#f1f5f9'>{row['name']}</div>
                <div style='font-size:12px;color:#94a3b8;margin:4px 0 10px'>📍 {row['city']}</div>
                <div style='display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px'>
                    <span style='color:#94a3b8'>Capacity</span>
                    <span style='color:#f1f5f9;font-weight:700'>{row['occupied']:,} / {row['capacity']:,}</span>
                </div>
                <div style='height:6px;background:#1a2236;border-radius:3px'>
                    <div style='height:100%;width:{util_pct}%;background:{bar_color};border-radius:3px'></div>
                </div>
                <div style='font-size:11px;color:#94a3b8;margin-top:6px'>
                    🛏️ {row.get('amenities','N/A')}
                </div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════
# PAGE: ADD EVENT (Admin)
# ════════════════════════════════════════════
elif page == "Add Event":
    st.title("➕ Add Disaster Event")
    if not st.session_state.logged_in:
        st.warning("⚠️ Please log in as admin to add events.")
    else:
        dis_df = qdf("SELECT id, name FROM disasters ORDER BY name")
        with st.form("add_event_form"):
            title    = st.text_input("Event Title *")
            dis_name = st.selectbox("Disaster Type *", dis_df["name"].tolist())
            dis_id   = int(dis_df[dis_df["name"]==dis_name]["id"].values[0])
            col1,col2 = st.columns(2)
            location = col1.text_input("Location")
            country  = col2.text_input("Country")
            col3,col4 = st.columns(2)
            severity = col3.selectbox("Severity", ["Extreme","High","Medium","Low"])
            status   = col4.selectbox("Status", ["Active","Resolved"])
            col5,col6,col7 = st.columns(3)
            affected = col5.number_input("Affected Population", min_value=0, value=0)
            injured  = col6.number_input("Injured", min_value=0, value=0)
            deaths   = col7.number_input("Deaths", min_value=0, value=0)
            col8,col9 = st.columns(2)
            lat = col8.number_input("Latitude", value=0.0, format="%.4f")
            lon = col9.number_input("Longitude", value=0.0, format="%.4f")
            rep_date = st.date_input("Reported Date", value=datetime.now())
            submitted = st.form_submit_button("✅ Add Event", use_container_width=True)

        if submitted:
            if not title:
                st.error("Event title is required.")
            else:
                mutate("""INSERT INTO disaster_events
                    (disaster_id,title,location,country,latitude,longitude,severity,
                     affected_population,injured,deaths,status,reported_date)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (dis_id, title, location, country, lat, lon, severity,
                     affected, injured, deaths, status, str(rep_date)))
                st.success(f"✅ Event '{title}' added successfully!")
                st.balloons()

# ════════════════════════════════════════════
# PAGE: ADD ALERT (Admin)
# ════════════════════════════════════════════
elif page == "Add Alert":
    st.title("🔔 Add Alert")
    if not st.session_state.logged_in:
        st.warning("⚠️ Please log in as admin to add alerts.")
    else:
        with st.form("add_alert_form"):
            title   = st.text_input("Alert Title *")
            message = st.text_area("Message *", height=120)
            col1,col2 = st.columns(2)
            severity = col1.selectbox("Severity", ["Extreme","High","Medium","Low"])
            region   = col2.text_input("Region *")
            submitted = st.form_submit_button("🚨 Publish Alert", use_container_width=True)

        if submitted:
            if not title or not message or not region:
                st.error("Please fill in all required fields.")
            else:
                mutate("INSERT INTO alerts (title,message,severity,region,is_active) VALUES (?,?,?,?,1)",
                       (title, message, severity, region))
                st.success(f"✅ Alert '{title}' published!")
                st.balloons()

# ════════════════════════════════════════════
# PAGE: LOGIN
# ════════════════════════════════════════════
elif page == "Login":
    st.title("🔐 Login")
    if st.session_state.logged_in:
        st.success(f"You are already logged in as **{st.session_state.user_name}** ({st.session_state.user_role}).")
    else:
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="admin@disaster.gov")
            password = st.text_input("Password", type="password", placeholder="admin123")
            submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            conn = get_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, hash_pw(password))
            ).fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.user_role = user["role"]
                st.session_state.user_name = user["name"]
                st.success(f"✅ Welcome back, **{user['name']}**!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
        st.caption("Default admin: admin@disaster.gov / admin123")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#64748b;font-size:11px'>"
    "🌍 DisasterWatch Pro v2.0 — Emergency Management Platform &nbsp;|&nbsp; "
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    "</div>",
    unsafe_allow_html=True
)
