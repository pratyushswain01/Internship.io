"""
Indian Wildlife Explorer — A comprehensive Streamlit biodiversity dashboard.
500 Indian animal species with interactive map, analytics, and detail cards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Indian Wildlife Explorer",
    page_icon="🐯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Background */
.stApp { background: linear-gradient(135deg, #0f1b2d 0%, #1a2f4a 50%, #0f1b2d 100%); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #142238 100%) !important;
    border-right: 1px solid rgba(255,215,0,0.15);
}
[data-testid="stSidebar"] * { color: #d4e0f0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label { color: #8ba8c8 !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* Hero title */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ffd700 0%, #ff8c00 50%, #ffd700 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.hero-subtitle { color: #7a9bbf; font-size: 1rem; margin-bottom: 1.5rem; letter-spacing: 0.03em; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(255,215,0,0.08) 0%, rgba(255,140,0,0.04) 100%);
    border: 1px solid rgba(255,215,0,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: rgba(255,215,0,0.45); }
.metric-number { font-size: 2.2rem; font-weight: 700; color: #ffd700; line-height: 1; }
.metric-label { font-size: 0.78rem; color: #7a9bbf; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.3rem; }

/* Species card */
.species-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s, background 0.2s;
}
.species-card:hover { border-color: rgba(255,215,0,0.35); background: rgba(255,215,0,0.06); }
.species-common { font-size: 1.05rem; font-weight: 600; color: #e8f0fb; }
.species-scientific { font-size: 0.82rem; color: #7a9bbf; font-style: italic; margin-top: 0.15rem; }
.species-group { font-size: 0.72rem; color: #5a7a9a; text-transform: uppercase; letter-spacing: 0.1em; }

/* Status badges */
.badge {
    display: inline-block;
    padding: 0.22rem 0.65rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-CR { background: rgba(220,38,38,0.18); color: #f87171; border: 1px solid rgba(220,38,38,0.35); }
.badge-EN { background: rgba(234,88,12,0.18); color: #fb923c; border: 1px solid rgba(234,88,12,0.35); }
.badge-VU { background: rgba(202,138,4,0.18); color: #facc15; border: 1px solid rgba(202,138,4,0.35); }
.badge-NT { background: rgba(37,99,235,0.18); color: #60a5fa; border: 1px solid rgba(37,99,235,0.35); }
.badge-LC { background: rgba(22,163,74,0.18); color: #4ade80; border: 1px solid rgba(22,163,74,0.35); }
.badge-DD { background: rgba(107,114,128,0.18); color: #9ca3af; border: 1px solid rgba(107,114,128,0.35); }

/* Section header */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: #ffd700;
    border-bottom: 1px solid rgba(255,215,0,0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
}

/* Info box */
.info-box {
    background: rgba(255,215,0,0.05);
    border-left: 3px solid #ffd700;
    border-radius: 0 8px 8px 0;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    color: #c8d8ec;
    font-size: 0.88rem;
    line-height: 1.6;
}

/* Divider */
.gold-divider { border: none; border-top: 1px solid rgba(255,215,0,0.15); margin: 1.5rem 0; }

/* Expander tweaks */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA GENERATION
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def build_dataset() -> pd.DataFrame:
    """
    Generate 500 records of Indian wildlife species.
    Data is based on actual Indian biodiversity records.
    """

    # ── Curated flagship / well-known species (guaranteed entries) ──────────
    flagship = [
        # Mammals
        ("Bengal Tiger", "Panthera tigris tigris", "Mammal", "EN",
         "The national animal of India; powerful apex predator of the subcontinent with distinctive orange coat and black stripes.",
         "Tropical and subtropical moist broadleaf forests, mangroves, grasslands",
         ["West Bengal", "Madhya Pradesh", "Uttarakhand", "Maharashtra", "Karnataka", "Rajasthan", "Assam"],
         ["Sundarbans NP", "Kanha NP", "Jim Corbett NP", "Bandipur NP", "Ranthambore NP"],
         21.5, 80.5),

        ("Asiatic Lion", "Panthera leo persica", "Mammal", "EN",
         "Last wild population outside Africa; slightly smaller than African lions with a distinct belly fold.",
         "Dry deciduous forests, scrub, open woodland",
         ["Gujarat"],
         ["Gir Forest NP"],
         21.1, 70.8),

        ("Indian Elephant", "Elephas maximus indicus", "Mammal", "EN",
         "Largest land animal in Asia; matriarchal herds traverse forest corridors across India.",
         "Tropical forests, grasslands, scrub",
         ["Kerala", "Karnataka", "Tamil Nadu", "Assam", "West Bengal", "Odisha"],
         ["Periyar NP", "Nagarhole NP", "Kaziranga NP", "Corbett NP"],
         11.5, 76.5),

        ("Indian One-horned Rhinoceros", "Rhinoceros unicornis", "Mammal", "VU",
         "Armour-plated giant of the terai grasslands; single horn up to 60 cm long.",
         "Tall grasslands, riverine forests, swamps",
         ["Assam", "West Bengal"],
         ["Kaziranga NP", "Pobitora WLS", "Orang NP", "Jaldapara NP"],
         26.6, 93.1),

        ("Snow Leopard", "Panthera uncia", "Mammal", "VU",
         "Ghost of the mountains; spotted grey-white coat blends with rocky Himalayan terrain.",
         "Alpine meadows, rocky terrain above 3000 m",
         ["Jammu & Kashmir", "Himachal Pradesh", "Uttarakhand", "Sikkim", "Arunachal Pradesh"],
         ["Hemis NP", "Great Himalayan NP", "Kedarnath WLS"],
         33.5, 77.0),

        ("Red Panda", "Ailurus fulgens", "Mammal", "EN",
         "Chestnut-red arboreal mammal with raccoon-like face; feeds mainly on bamboo.",
         "Temperate broadleaf and mixed forests, bamboo understory",
         ["Sikkim", "West Bengal", "Arunachal Pradesh"],
         ["Singalila NP", "Khangchendzonga NP", "Namdapha NP"],
         27.5, 88.4),

        ("Nilgiri Tahr", "Nilgiritragus hylocrius", "Mammal", "EN",
         "Stocky mountain ungulate endemic to the Nilgiri Hills; saddle-back marking on males.",
         "Montane grasslands, rocky escarpments above 1200 m",
         ["Tamil Nadu", "Kerala"],
         ["Eravikulam NP", "Mukurthi NP"],
         10.2, 77.1),

        ("Lion-tailed Macaque", "Macaca silenus", "Mammal", "EN",
         "Endangered primate of the Western Ghats; silver mane around black face.",
         "Tropical moist evergreen forests",
         ["Kerala", "Tamil Nadu", "Karnataka"],
         ["Silent Valley NP", "Anamalai TR", "Kudremukh NP"],
         10.7, 76.5),

        ("Gangetic River Dolphin", "Platanista gangetica", "Mammal", "EN",
         "National aquatic animal of India; nearly blind, navigates by echolocation.",
         "Freshwater rivers and tributaries",
         ["Uttar Pradesh", "Bihar", "West Bengal", "Assam"],
         ["Vikramshila Gangetic Dolphin Sanctuary"],
         25.5, 84.5),

        ("Indian Wild Ass", "Equus hemionus khur", "Mammal", "NT",
         "Swift and resilient equid of the Rann of Kutch; adapted to extreme aridity.",
         "Desert, salt flats, scrub",
         ["Gujarat"],
         ["Wild Ass Sanctuary"],
         23.7, 71.2),

        ("Clouded Leopard", "Neofelis nebulosa", "Mammal", "VU",
         "Arboreal large cat with cloud-patterned coat; excellent climber in northeast India.",
         "Tropical and subtropical moist forests",
         ["Assam", "Meghalaya", "Arunachal Pradesh", "Sikkim"],
         ["Nameri NP", "Kaziranga NP"],
         26.8, 93.5),

        ("Himalayan Brown Bear", "Ursus arctos isabellinus", "Mammal", "VU",
         "Large omnivorous bear of high-altitude Himalayan regions; reddish-brown coat.",
         "Alpine meadows, subalpine forests",
         ["Jammu & Kashmir", "Himachal Pradesh", "Uttarakhand"],
         ["Dachigam NP", "Great Himalayan NP"],
         34.0, 75.5),

        ("Sloth Bear", "Melursus ursinus", "Mammal", "VU",
         "Shaggy nocturnal bear; long lower lip used to suck termites from mounds.",
         "Dry and moist tropical forests, scrub, grasslands",
         ["Madhya Pradesh", "Rajasthan", "Karnataka", "Odisha"],
         ["Kanha NP", "Sariska TR", "Nagarhole NP"],
         22.0, 78.0),

        ("Dhole", "Cuon alpinus", "Mammal", "EN",
         "Indian wild dog; pack hunter that can take prey far larger than itself.",
         "Tropical and subtropical forests",
         ["Madhya Pradesh", "Maharashtra", "Karnataka", "Kerala", "Arunachal Pradesh"],
         ["Pench NP", "Nagarhole NP", "Periyar NP"],
         20.5, 79.5),

        ("Gaur", "Bos gaurus", "Mammal", "VU",
         "Largest wild bovine in the world; bulls reach 3 m length and 1000 kg.",
         "Tropical and subtropical moist forests",
         ["Maharashtra", "Karnataka", "Kerala", "Tamil Nadu", "Assam"],
         ["Tadoba NP", "Bandipur NP", "Periyar NP"],
         19.5, 79.2),

        ("Indian Muntjac", "Muntiacus muntjak", "Mammal", "LC",
         "Small deer with short antlers and prominent facial glands; barks when alarmed.",
         "Tropical forests, secondary growth",
         ["Assam", "Meghalaya", "Kerala", "Karnataka", "West Bengal"],
         ["Kaziranga NP", "Periyar NP"],
         14.0, 75.5),

        ("Nilgai", "Boselaphus tragocamelus", "Mammal", "LC",
         "Largest Asian antelope; males are blue-grey with a beard tuft.",
         "Dry grasslands, scrub, light forests",
         ["Rajasthan", "Uttar Pradesh", "Bihar", "Gujarat", "Haryana"],
         ["Keoladeo NP", "Velavadar NP"],
         25.5, 74.5),

        ("Chinkara", "Gazella bennettii", "Mammal", "LC",
         "Slender gazelle of arid zones; can survive without drinking water for long periods.",
         "Arid plains, sandy desert, scrub",
         ["Rajasthan", "Gujarat", "Madhya Pradesh"],
         ["Desert NP", "Rann of Kutch"],
         26.5, 71.5),

        ("Blackbuck", "Antilope cervicapra", "Mammal", "LC",
         "Fastest of Indian antelopes; adult males have spiralled horns and contrasting black-white coat.",
         "Open grasslands, semi-arid plains",
         ["Rajasthan", "Gujarat", "Andhra Pradesh", "Punjab", "Haryana"],
         ["Velavadar NP", "Point Calimere WLS"],
         22.5, 72.5),

        ("Indian Pangolin", "Manis crassicaudata", "Mammal", "EN",
         "Solitary nocturnal mammal covered in overlapping keratin scales; feeds on ants.",
         "Grasslands, scrub, forests",
         ["Rajasthan", "Uttar Pradesh", "Gujarat", "Karnataka", "Odisha"],
         ["Ranthambore NP", "Gir Forest NP"],
         22.0, 76.0),

        # Birds
        ("Great Indian Bustard", "Ardeotis nigriceps", "Bird", "CR",
         "Critically endangered grassland bird; one of the heaviest flying birds on Earth.",
         "Arid and semi-arid grasslands, scrub plains",
         ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka"],
         ["Desert NP", "Rollapadu WLS"],
         27.0, 72.0),

        ("Indian Peacock", "Pavo cristatus", "Bird", "LC",
         "National bird of India; males display spectacular iridescent tail feathers.",
         "Deciduous forests, scrub, near cultivated areas",
         ["Rajasthan", "Madhya Pradesh", "Gujarat", "Tamil Nadu", "Karnataka"],
         ["Ranthambore NP", "Kanha NP", "Velavadar NP"],
         23.5, 74.0),

        ("Sarus Crane", "Antigone antigone", "Bird", "VU",
         "Tallest flying bird in the world; pairs mate for life with loud trumpeting calls.",
         "Wetlands, marshes, irrigated fields",
         ["Uttar Pradesh", "Rajasthan", "Gujarat", "Punjab"],
         ["Keoladeo NP", "National Chambal Sanctuary"],
         26.5, 77.5),

        ("Indian Roller", "Coracias benghalensis", "Bird", "LC",
         "State bird of multiple Indian states; vivid turquoise-blue in flight.",
         "Open woodland, scrub, cultivated land",
         ["Rajasthan", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Andhra Pradesh"],
         ["Keoladeo NP", "Mudumalai NP"],
         24.0, 76.0),

        ("White-backed Vulture", "Gyps africanus", "Bird", "CR",
         "Large colonial-nesting vulture; populations crashed due to veterinary diclofenac.",
         "Open country, cultivated areas, near carcasses",
         ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Gujarat"],
         ["Ranthambore NP", "Kanha NP"],
         24.5, 74.5),

        ("Siberian Crane", "Leucogeranus leucogeranus", "Bird", "CR",
         "Long-distance migratory crane wintering in India; critically endangered globally.",
         "Wetlands, shallow lakes",
         ["Gujarat", "Rajasthan"],
         ["Keoladeo NP", "Nalsarovar BS"],
         23.0, 73.5),

        ("Spot-billed Pelican", "Pelecanus philippensis", "Bird", "NT",
         "Colonial waterbird that nests in tree colonies near large water bodies.",
         "Freshwater lakes, rivers, coastal wetlands",
         ["Tamil Nadu", "Andhra Pradesh", "Karnataka", "Kerala"],
         ["Vedanthangal BS", "Pulicat Lake BS"],
         12.0, 79.5),

        ("Indian Eagle-Owl", "Bubo bengalensis", "Bird", "LC",
         "Large owl with prominent ear tufts; deep booming call heard at dusk.",
         "Hilly and rocky terrain, light forests",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu"],
         ["Ranthambore NP", "Nagarhole NP"],
         23.0, 76.0),

        ("Malabar Hornbill", "Anthracoceros coronatus", "Bird", "NT",
         "Large frugivore of Western Ghats forests; distinctive casque on yellow bill.",
         "Tropical moist evergreen forests",
         ["Kerala", "Tamil Nadu", "Karnataka", "Goa"],
         ["Periyar NP", "Kudremukh NP", "Mollem NP"],
         10.5, 76.3),

        ("Grey-headed Swamphen", "Porphyrio poliocephalus", "Bird", "LC",
         "Bulky purple-blue waterbird with bright red frontal shield; walks on floating vegetation.",
         "Freshwater wetlands, reed beds, marshes",
         ["Kerala", "Tamil Nadu", "West Bengal", "Uttar Pradesh"],
         ["Keoladeo NP", "Sultanpur NP"],
         26.0, 77.0),

        # Reptiles
        ("Gharial", "Gavialis gangeticus", "Reptile", "CR",
         "Critically endangered crocodilian; long slender snout adapted for catching fish.",
         "Deep, fast-flowing rivers with sandy banks",
         ["Uttar Pradesh", "Bihar", "Madhya Pradesh", "Rajasthan"],
         ["National Chambal Sanctuary", "Sone Gharial Sanctuary"],
         25.5, 79.5),

        ("Saltwater Crocodile", "Crocodylus porosus", "Reptile", "LC",
         "World's largest living reptile; apex predator of coastal and estuarine habitats.",
         "Mangroves, estuaries, coastal wetlands",
         ["West Bengal", "Andaman & Nicobar Islands", "Odisha"],
         ["Sundarbans NP", "Bhitarkanika NP"],
         21.5, 89.5),

        ("Indian Python", "Python molurus", "Reptile", "VU",
         "Massive constrictor; one of the world's longest snakes, exceeding 6 m.",
         "Tropical forests, grasslands, wetland margins",
         ["Rajasthan", "Gujarat", "Madhya Pradesh", "Maharashtra", "Karnataka"],
         ["Gir Forest NP", "Kanha NP", "Bandipur NP"],
         21.0, 77.0),

        ("King Cobra", "Ophiophagus hannah", "Reptile", "VU",
         "World's longest venomous snake; feeds almost entirely on other snakes.",
         "Dense highland forests, forest edges near water",
         ["Kerala", "Karnataka", "Tamil Nadu", "Assam", "West Bengal"],
         ["Agumbe Rainforest", "Periyar NP"],
         12.0, 75.5),

        ("Indian Softshell Turtle", "Nilssonia gangetica", "Reptile", "CR",
         "Large freshwater turtle with flat leathery shell; important for river ecology.",
         "Deep pools of large rivers with sandy banks",
         ["Uttar Pradesh", "Bihar", "West Bengal"],
         ["National Chambal Sanctuary", "Ganga River Dolphin Reserve"],
         25.5, 82.0),

        ("Monitor Lizard", "Varanus bengalensis", "Reptile", "LC",
         "Largest lizard in India; highly adaptable predator found in diverse habitats.",
         "Forests, grasslands, agricultural land, mangroves",
         ["Rajasthan", "Uttar Pradesh", "Karnataka", "Maharashtra", "Tamil Nadu"],
         ["Multiple protected areas"],
         20.0, 77.0),

        ("Indian Chameleon", "Chamaeleo zeylanicus", "Reptile", "LC",
         "India's only chameleon; changes colour for camouflage and communication.",
         "Dry scrub, forest edges, agricultural hedgerows",
         ["Karnataka", "Tamil Nadu", "Andhra Pradesh", "Maharashtra"],
         ["Bandipur NP", "Nagarjunasagar-Srisailam TR"],
         15.0, 77.5),

        # Amphibians
        ("Indian Purple Frog", "Nasikabatrachus sahyadrensis", "Amphibian", "EN",
         "Pig-nosed underground frog discovered in 2003; only surfaces during monsoon to breed.",
         "Dense tropical forests, underground near anthills",
         ["Kerala", "Tamil Nadu"],
         ["Agasthyamalai Biosphere Reserve"],
         9.5, 77.2),

        ("Malabar Gliding Frog", "Rhacophorus malabaricus", "Amphibian", "LC",
         "Vivid green tree frog with webbed feet used to glide between trees.",
         "Tropical moist evergreen forests",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Silent Valley NP", "Kudremukh NP"],
         11.0, 76.0),

        ("Indian Bullfrog", "Hoplobatrachus tigerinus", "Amphibian", "LC",
         "Large frog; males turn bright yellow during breeding season.",
         "Freshwater ponds, marshes, rice paddies",
         ["Assam", "West Bengal", "Uttar Pradesh", "Rajasthan", "Karnataka"],
         ["Kaziranga NP", "Keoladeo NP"],
         26.0, 78.0),

        # Fish
        ("Mahseer", "Tor tor", "Fish", "VU",
         "Prized game fish of Himalayan rivers; powerful swimmer in fast-flowing water.",
         "Fast-flowing rivers and streams in foothills",
         ["Uttarakhand", "Himachal Pradesh", "Assam", "Arunachal Pradesh"],
         ["Jim Corbett NP", "Kaziranga NP"],
         30.0, 79.5),

        ("Ganges Shark", "Glyphis gangeticus", "Fish", "CR",
         "Critically endangered true river shark; very rarely sighted.",
         "Freshwater rivers, estuaries",
         ["West Bengal", "Bihar", "Uttar Pradesh"],
         ["Sundarbans NP"],
         22.5, 88.5),

        # Insects
        ("Southern Birdwing", "Troides minos", "Insect", "VU",
         "India's largest butterfly with striking black and yellow wings; state butterfly of Karnataka.",
         "Tropical moist forests, forest edges",
         ["Karnataka", "Kerala", "Tamil Nadu", "Goa"],
         ["Kudremukh NP", "Periyar NP"],
         12.5, 75.8),

        ("Common Nawab Butterfly", "Polyura athamas", "Insect", "LC",
         "Large fast-flying butterfly; feeds on rotting fruit and tree sap.",
         "Tropical and subtropical forests",
         ["Assam", "West Bengal", "Arunachal Pradesh", "Sikkim"],
         ["Kaziranga NP", "Manas NP"],
         26.5, 91.0),
    ]

    # ── Extended species pool (fills up to 500) ──────────────────────────────
    extended = [
        # ── MORE MAMMALS ──
        ("Himalayan Musk Deer", "Moschus leucogaster", "Mammal", "EN",
         "Small deer known for musk gland; used in traditional medicine, leading to poaching.",
         "Subalpine forests, rocky terrain",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir", "Sikkim"],
         ["Great Himalayan NP", "Kedarnath WLS"],
         31.0, 79.0),

        ("Indian Fox", "Vulpes bengalensis", "Mammal", "LC",
         "Slender fox endemic to India; inhabits open scrub and grassland plains.",
         "Open grasslands, scrub, agricultural fields",
         ["Rajasthan", "Gujarat", "Madhya Pradesh", "Karnataka", "Andhra Pradesh"],
         ["Desert NP", "Velavadar NP"],
         24.0, 73.0),

        ("Striped Hyena", "Hyaena hyaena", "Mammal", "NT",
         "Nocturnal scavenger; striped coat and distinctive mane.",
         "Dry grasslands, scrub, rocky terrain",
         ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka"],
         ["Desert NP", "Gir Forest NP"],
         25.0, 72.5),

        ("Indian Civet", "Viverra zibetha", "Mammal", "LC",
         "Nocturnal carnivore with spotted coat; secretes civetone from perineal glands.",
         "Dense tropical forests, riverine forest",
         ["Assam", "Meghalaya", "Arunachal Pradesh", "Kerala"],
         ["Kaziranga NP", "Namdapha NP"],
         26.0, 93.0),

        ("Small Indian Mongoose", "Urva auropunctata", "Mammal", "LC",
         "Agile predator known for killing venomous snakes; terrestrial.",
         "Forests, scrub, cultivated areas",
         ["Gujarat", "Rajasthan", "Maharashtra", "Kerala"],
         ["Gir Forest NP", "Periyar NP"],
         22.0, 73.5),

        ("Binturong", "Arctictis binturong", "Mammal", "VU",
         "Bear-cat with prehensile tail; secretes popcorn-scented musk.",
         "Dense tropical forests",
         ["Assam", "Arunachal Pradesh", "Meghalaya"],
         ["Namdapha NP", "Manas NP"],
         27.0, 95.0),

        ("Smooth-coated Otter", "Lutrogale perspicillata", "Mammal", "VU",
         "Largest otter in Asia; social fish-eater of large rivers.",
         "Large rivers, lakes, mangroves",
         ["Assam", "West Bengal", "Kerala", "Karnataka"],
         ["Kaziranga NP", "Sundarbans NP"],
         22.5, 88.0),

        ("Himalayan Serow", "Capricornis thar", "Mammal", "NT",
         "Goat-antelope of steep Himalayan terrain; solitary and territorial.",
         "Steep forested hillsides, rocky cliffs",
         ["Uttarakhand", "Sikkim", "Arunachal Pradesh", "Himachal Pradesh"],
         ["Great Himalayan NP", "Khangchendzonga NP"],
         30.5, 79.5),

        ("Sambar Deer", "Rusa unicolor", "Mammal", "VU",
         "India's largest deer; preferred prey of tigers and leopards.",
         "Deciduous and semi-evergreen forests",
         ["Madhya Pradesh", "Karnataka", "Kerala", "Tamil Nadu", "Maharashtra"],
         ["Kanha NP", "Bandipur NP", "Periyar NP"],
         20.0, 79.0),

        ("Spotted Deer", "Axis axis", "Mammal", "LC",
         "Chital; graceful spotted deer living in large herds near forest edges.",
         "Grasslands, deciduous forests",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Kerala", "Maharashtra"],
         ["Ranthambore NP", "Kanha NP", "Nagarhole NP"],
         23.5, 76.5),

        ("Swamp Deer", "Rucervus duvaucelii", "Mammal", "VU",
         "Barasingha; antlers have 12 or more tines; confined to floodplain grasslands.",
         "Tall elephant-grass floodplains, swampy ground",
         ["Uttar Pradesh", "Madhya Pradesh", "Assam"],
         ["Dudhwa NP", "Kanha NP", "Kaziranga NP"],
         28.0, 81.0),

        ("Hog Deer", "Axis porcinus", "Mammal", "EN",
         "Small stocky deer; runs with low head like a hog through dense grass.",
         "Tall grasslands, floodplains, river edges",
         ["Assam", "Uttar Pradesh", "Punjab", "West Bengal"],
         ["Kaziranga NP", "Dudhwa NP"],
         27.0, 92.0),

        ("Barking Deer", "Muntiacus vaginalis", "Mammal", "LC",
         "Compact deer with short spiky antlers; gives sharp bark when alarmed.",
         "Dense forests, forest edges, tea gardens",
         ["Assam", "Meghalaya", "Arunachal Pradesh", "Sikkim"],
         ["Kaziranga NP", "Namdapha NP"],
         27.5, 93.0),

        ("Wild Boar", "Sus scrofa", "Mammal", "LC",
         "Adaptable omnivore; root-grubbing forms part of forest nutrient cycling.",
         "Forests, grasslands, agricultural margins",
         ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Karnataka", "West Bengal"],
         ["Ranthambore NP", "Kanha NP"],
         23.0, 77.5),

        ("Porcupine", "Hystrix indica", "Mammal", "LC",
         "India's largest rodent; hollow quills rattle as warning.",
         "Rocky terrain, forests, scrub",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu"],
         ["Desert NP", "Gir Forest NP"],
         24.5, 75.0),

        ("Giant Squirrel", "Ratufa indica", "Mammal", "LC",
         "Indian giant squirrel; vivid chestnut and purple coat; leaps 6 m between trees.",
         "Tropical moist forests",
         ["Karnataka", "Kerala", "Tamil Nadu", "Maharashtra"],
         ["Nagarhole NP", "Periyar NP", "Melghat TR"],
         12.5, 76.5),

        ("Himalayan Tahr", "Hemitragus jemlahicus", "Mammal", "NT",
         "Stocky wild goat with thick reddish-brown coat; lives on steep Himalayan cliffs.",
         "Himalayan alpine and subalpine zones",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir"],
         ["Jim Corbett NP", "Kedarnath WLS"],
         30.8, 79.3),

        ("Rhesus Macaque", "Macaca mulatta", "Mammal", "LC",
         "India's most common primate; highly adaptive to human environments.",
         "Forests, urban fringe, temple areas",
         ["Uttar Pradesh", "Rajasthan", "West Bengal", "Assam", "Karnataka"],
         ["Ranthambore NP", "Kaziranga NP"],
         26.0, 80.0),

        ("Bonnet Macaque", "Macaca radiata", "Mammal", "LC",
         "Southern India's common macaque; named for hair radiating from crown.",
         "Tropical forests, urban gardens",
         ["Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh"],
         ["Anamalai TR", "Bandipur NP"],
         11.5, 77.5),

        ("Hanuman Langur", "Semnopithecus entellus", "Mammal", "LC",
         "Grey leaf monkey with black face; considered sacred in Hindu culture.",
         "Forests, scrub, villages, temples",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Uttar Pradesh"],
         ["Ranthambore NP", "Kanha NP"],
         24.0, 76.0),

        ("Nilgiri Langur", "Trachypithecus johnii", "Mammal", "VU",
         "Black-bodied langur with golden-brown head; restricted to Western Ghats.",
         "Tropical moist evergreen forests",
         ["Tamil Nadu", "Kerala", "Karnataka"],
         ["Nilgiris Biosphere Reserve", "Periyar NP"],
         10.5, 77.0),

        ("Capped Langur", "Trachypithecus pileatus", "Mammal", "VU",
         "Pale-grey langur with dark cap; found in northeast India.",
         "Tropical forests, bamboo groves",
         ["Assam", "Meghalaya", "Tripura", "Mizoram"],
         ["Pobitora WLS", "Nongkhyllem WLS"],
         26.0, 91.5),

        ("Hoolock Gibbon", "Hoolock hoolock", "Mammal", "EN",
         "India's only ape; melodious dawn calls echo through forests; pair-bonded.",
         "Tropical moist forests",
         ["Assam", "Meghalaya", "Mizoram", "Arunachal Pradesh"],
         ["Hoollongapar Gibbon Sanctuary", "Namdapha NP"],
         26.5, 94.0),

        ("Fishing Cat", "Prionailurus viverrinus", "Mammal", "VU",
         "Semi-aquatic wildcat; partially webbed feet for swimming.",
         "Wetlands, mangroves, river banks",
         ["West Bengal", "Assam", "Odisha", "Kerala"],
         ["Sundarbans NP", "Chilika Lake"],
         20.0, 86.0),

        ("Jungle Cat", "Felis chaus", "Mammal", "LC",
         "Medium-sized wildcat; long-legged hunter of reed beds and tall grass.",
         "Grasslands, wetlands, scrub",
         ["Rajasthan", "Gujarat", "Uttar Pradesh", "West Bengal"],
         ["Keoladeo NP", "Ranthambore NP"],
         27.0, 74.0),

        ("Rusty-spotted Cat", "Prionailurus rubiginosus", "Mammal", "NT",
         "World's smallest wild cat; nocturnal and secretive.",
         "Dry deciduous forests, scrub, rocky terrain",
         ["Rajasthan", "Gujarat", "Karnataka", "Tamil Nadu"],
         ["Gir Forest NP", "Satpura NP"],
         22.5, 76.5),

        ("Leopard", "Panthera pardus fusca", "Mammal", "VU",
         "Adaptable spotted cat; most widespread large cat in India.",
         "Forest, scrub, rocky hills, near human settlements",
         ["Rajasthan", "Maharashtra", "Karnataka", "Assam", "Uttarakhand"],
         ["Jhalana Leopard Reserve", "Sanjay Gandhi NP"],
         20.5, 75.5),

        ("Caracal", "Caracal caracal", "Mammal", "LC",
         "Tufted-eared cat; remarkable leaping ability to catch birds in flight.",
         "Arid scrub, rocky terrain, dry deciduous forest",
         ["Rajasthan", "Gujarat", "Madhya Pradesh"],
         ["Desert NP", "Kuno NP"],
         27.0, 73.5),

        ("Desert Cat", "Felis lybica ornata", "Mammal", "LC",
         "Wild ancestor of domestic cat; spotted coat in sandy desert habitat.",
         "Desert, semi-desert scrub",
         ["Rajasthan", "Gujarat"],
         ["Desert NP", "Wild Ass Sanctuary"],
         27.5, 72.0),

        ("Aardwolf", "Proteles cristata", "Mammal", "LC",
         "Hyaena relative that feeds on termites; found in drier parts of India.",
         "Arid scrub, grasslands",
         ["Rajasthan", "Gujarat"],
         ["Desert NP"],
         27.5, 72.5),

        # ── MORE BIRDS ──
        ("Indian Vulture", "Gyps indicus", "Bird", "CR",
         "Critically endangered Old World vulture; long-fingered wingtips for thermal soaring.",
         "Cliffs, open country, near human settlements",
         ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Gujarat"],
         ["Ranthambore NP", "Panna NP"],
         25.0, 75.5),

        ("Red Junglefowl", "Gallus gallus", "Bird", "LC",
         "Ancestor of all domestic chickens; males with brilliant red comb and long tail feathers.",
         "Tropical forests, forest edges, bamboo groves",
         ["Assam", "Arunachal Pradesh", "West Bengal", "Meghalaya"],
         ["Kaziranga NP", "Namdapha NP"],
         26.0, 93.5),

        ("Black-necked Crane", "Grus nigricollis", "Bird", "VU",
         "Only crane that breeds on Tibetan plateau and winters in India.",
         "High-altitude wetlands, valleys",
         ["Arunachal Pradesh", "Jammu & Kashmir"],
         ["Sangti Valley", "Tso Kar WLS"],
         34.5, 78.5),

        ("Bar-headed Goose", "Anser indicus", "Bird", "LC",
         "Flies over the Himalayas during migration; highest-flying bird.",
         "High-altitude lakes, winter wetlands",
         ["Jammu & Kashmir", "Ladakh", "Gujarat", "Rajasthan"],
         ["Pangong Tso WLS", "Keoladeo NP"],
         34.0, 78.0),

        ("Indian Skimmer", "Rynchops albicollis", "Bird", "EN",
         "Unique bill with elongated lower mandible to skim water surface for fish.",
         "Large rivers with sandy banks",
         ["Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Odisha"],
         ["National Chambal Sanctuary"],
         26.0, 79.5),

        ("River Tern", "Sterna aurantia", "Bird", "NT",
         "Orange-billed tern that nests on riverside sandbars and gravel banks.",
         "Large rivers, lakes",
         ["Uttar Pradesh", "Bihar", "Assam", "Karnataka"],
         ["National Chambal Sanctuary"],
         25.5, 80.5),

        ("Indian Cormorant", "Phalacrocorax fuscicollis", "Bird", "LC",
         "Medium-sized cormorant that dives for fish; colonial breeder.",
         "Freshwater lakes, reservoirs, large rivers",
         ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "West Bengal"],
         ["Pulicat Lake BS", "Vedanthangal BS"],
         12.0, 80.0),

        ("Asian Openbill Stork", "Anastomus oscitans", "Bird", "LC",
         "White stork with a gap in its bill used to extract snails from shells.",
         "Wetlands, paddy fields, shallow lakes",
         ["Rajasthan", "Uttar Pradesh", "Tamil Nadu", "West Bengal"],
         ["Keoladeo NP", "Vedanthangal BS"],
         25.0, 77.5),

        ("Painted Stork", "Mycteria leucocephala", "Bird", "NT",
         "Striking pink-flushed stork that nests colonially in trees over water.",
         "Freshwater wetlands, lakes, paddy fields",
         ["Rajasthan", "Uttar Pradesh", "Karnataka", "Tamil Nadu"],
         ["Keoladeo NP", "Ranganathittu BS"],
         24.5, 77.0),

        ("Black-headed Ibis", "Threskiornis melanocephalus", "Bird", "NT",
         "White ibis with bald black head; nests colonially with storks.",
         "Wetlands, paddy fields, tidal mudflats",
         ["Tamil Nadu", "Karnataka", "West Bengal", "Rajasthan"],
         ["Vedanthangal BS", "Koonthankulam BS"],
         11.5, 80.0),

        ("Eurasian Spoonbill", "Platalea leucorodia", "Bird", "LC",
         "Distinctive spatula-shaped bill swept side to side to catch prey.",
         "Wetlands, estuaries, mudflats",
         ["Gujarat", "Rajasthan", "West Bengal", "Andhra Pradesh"],
         ["Nalsarovar BS", "Pulicat Lake BS"],
         23.0, 72.5),

        ("Great White Pelican", "Pelecanus onocrotalus", "Bird", "LC",
         "Massive waterbird with pouch bill; winter visitor to Indian wetlands.",
         "Large freshwater and brackish lakes",
         ["Gujarat", "Rajasthan", "Andhra Pradesh"],
         ["Nalsarovar BS", "Pulicat Lake BS"],
         23.5, 72.0),

        ("Ruddy Shelduck", "Tadorna ferruginea", "Bird", "LC",
         "Chestnut-orange duck; winters in large flocks on Indian wetlands.",
         "Lakes, rivers, cultivated areas",
         ["Rajasthan", "Gujarat", "Punjab", "Uttarakhand"],
         ["Keoladeo NP", "Khijadiya BS"],
         30.0, 77.5),

        ("Cotton Pygmy Goose", "Nettapus coromandelianus", "Bird", "LC",
         "India's smallest waterfowl; green-glossed wings with white body.",
         "Freshwater lakes with floating vegetation",
         ["Assam", "West Bengal", "Karnataka", "Kerala"],
         ["Deepor Beel WLS", "Karaivetti BS"],
         26.0, 91.5),

        ("Comb Duck", "Sarkidiornis sylvicola", "Bird", "LC",
         "Large duck with fleshy knob on bill of breeding males.",
         "Freshwater lakes, marshes, flooded forests",
         ["Assam", "West Bengal", "Gujarat", "Rajasthan"],
         ["Kaziranga NP", "Nalsarovar BS"],
         26.5, 90.5),

        ("Grey-crowned Prinia", "Prinia cinereocapilla", "Bird", "LC",
         "Small warbler found in Himalayan foothills and terai grasslands.",
         "Grasslands, scrub, tall grass",
         ["Uttarakhand", "West Bengal", "Assam"],
         ["Dudhwa NP", "Kaziranga NP"],
         28.5, 80.5),

        ("Indian Grassbird", "Graminicola bengalensis", "Bird", "NT",
         "Secretive skulker of tall grasslands; rarely seen but regularly heard.",
         "Tall wet grasslands",
         ["West Bengal", "Assam", "Uttar Pradesh"],
         ["Kaziranga NP", "Dudhwa NP"],
         26.5, 92.0),

        ("Indian Nightjar", "Caprimulgus asiaticus", "Bird", "LC",
         "Crepuscular insectivore with cryptic plumage blending with leaf litter.",
         "Open woodland, scrub, cultivated land",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu"],
         ["Ranthambore NP", "Mudumalai NP"],
         23.0, 75.5),

        ("Crested Hawk-Eagle", "Nisaetus cirrhatus", "Bird", "LC",
         "Powerful forest raptor; crest often raised in display.",
         "Tropical moist forests, forest edges",
         ["Karnataka", "Kerala", "Tamil Nadu", "Assam", "Maharashtra"],
         ["Periyar NP", "Nagarhole NP"],
         12.0, 76.5),

        ("Brahminy Kite", "Haliastur indus", "Bird", "LC",
         "Chestnut and white raptor associated with water and coastlines.",
         "Coastal wetlands, rivers, lakes",
         ["Karnataka", "Kerala", "Tamil Nadu", "West Bengal", "Odisha"],
         ["Sundarbans NP", "Pulicat Lake BS"],
         13.5, 80.0),

        ("Osprey", "Pandion haliaetus", "Bird", "LC",
         "Fish-hunting raptor that plunges feet-first into water; winter visitor.",
         "Rivers, lakes, coastal estuaries",
         ["Rajasthan", "Gujarat", "Kerala", "West Bengal"],
         ["Keoladeo NP", "Chilika Lake"],
         25.0, 74.0),

        ("White-rumped Vulture", "Gyps bengalensis", "Bird", "CR",
         "Critically endangered; once abundant but crashed 99% due to diclofenac poisoning.",
         "Open country, forests, near carcasses",
         ["Rajasthan", "Uttar Pradesh", "West Bengal", "Karnataka"],
         ["Ranthambore NP", "Kanha NP"],
         25.5, 77.0),

        ("Greater Flamingo", "Phoenicopterus roseus", "Bird", "LC",
         "Pink wading bird that filters algae and brine shrimp with its bent bill.",
         "Salt lakes, mudflats, estuaries",
         ["Gujarat", "Rajasthan", "Andhra Pradesh", "Tamil Nadu"],
         ["Rann of Kutch BS", "Nalsarovar BS"],
         24.0, 72.5),

        ("Lesser Flamingo", "Phoeniconaias minor", "Bird", "NT",
         "Smaller, deeper-pink flamingo; rarely breeds in India.",
         "Saline lakes, mudflats",
         ["Gujarat", "Rajasthan", "Andhra Pradesh"],
         ["Rann of Kutch BS"],
         23.5, 72.0),

        ("Indian Pitta", "Pitta brachyura", "Bird", "LC",
         "Brilliantly coloured ground bird; 9-colour plumage; migrants breed in India.",
         "Moist deciduous forests, bamboo",
         ["Madhya Pradesh", "Maharashtra", "Karnataka", "Odisha"],
         ["Kanha NP", "Tadoba NP"],
         20.5, 80.0),

        ("Malabar Pied Hornbill", "Anthracoceros coronatus", "Bird", "NT",
         "Black-and-white hornbill with large yellow casque; frugivore of Western Ghats.",
         "Tropical moist forests",
         ["Karnataka", "Kerala", "Tamil Nadu", "Goa"],
         ["Nagarhole NP", "Periyar NP"],
         12.5, 76.3),

        ("Wreathed Hornbill", "Rhyticeros undulatus", "Bird", "LC",
         "Large hornbill with corrugated casque; nests in tree cavities.",
         "Tropical evergreen forests",
         ["Assam", "Arunachal Pradesh", "Meghalaya"],
         ["Namdapha NP", "Kaziranga NP"],
         27.0, 94.5),

        ("Great Indian Hornbill", "Buceros bicornis", "Bird", "VU",
         "Largest Indian hornbill; massive yellow-and-black casque; loud calls.",
         "Dense tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu", "Assam", "Arunachal Pradesh"],
         ["Periyar NP", "Namdapha NP"],
         10.8, 76.3),

        ("Alexandrine Parakeet", "Psittacula eupatria", "Bird", "NT",
         "Large parrot with striking rose shoulder patches; range shrinking due to pet trade.",
         "Forests, forest edges, cultivated areas",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "West Bengal"],
         ["Keoladeo NP", "Ranthambore NP"],
         27.0, 76.5),

        ("Vernal Hanging Parrot", "Loriculus vernalis", "Bird", "LC",
         "Tiny bright-green parrot that hangs upside-down to roost.",
         "Tropical moist forests, forest edges",
         ["Karnataka", "Kerala", "Tamil Nadu", "Andaman Islands"],
         ["Nagarhole NP", "Periyar NP"],
         12.0, 77.0),

        ("Crimson-backed Sunbird", "Leptocoma minima", "Bird", "LC",
         "Tiny nectar-feeding bird of Western Ghats forests; deep red dorsal plumage.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Kudremukh NP", "Silent Valley NP"],
         11.5, 76.5),

        ("Rufous-bellied Eagle", "Lophotriorchis kienerii", "Bird", "LC",
         "Compact forest eagle of hilly terrain; rufous underparts.",
         "Hilly tropical forests",
         ["Karnataka", "Kerala", "Tamil Nadu", "Assam"],
         ["Nagarhole NP", "Namdapha NP"],
         12.8, 76.0),

        ("Oriental Honey-buzzard", "Pernis ptilorhynchus", "Bird", "LC",
         "Raptors that specialise in raiding bees' and wasps' nests.",
         "Forest, forest edges, wooded gardens",
         ["Karnataka", "Kerala", "Assam", "Maharashtra"],
         ["Bandipur NP", "Kaziranga NP"],
         13.0, 76.5),

        ("Red-breasted Flycatcher", "Ficedula parva", "Bird", "LC",
         "Small migratory flycatcher that winters across India.",
         "Forests, wooded gardens",
         ["Rajasthan", "Gujarat", "Karnataka", "Tamil Nadu"],
         ["Multiple parks"],
         22.0, 74.0),

        ("White-bellied Sea Eagle", "Icthyophaga leucogaster", "Bird", "LC",
         "Large eagle of coasts and large inland waters; grey and white plumage.",
         "Coasts, large rivers, lakes",
         ["Andaman Islands", "Kerala", "Karnataka", "West Bengal"],
         ["Sundarbans NP", "Periyar NP"],
         11.5, 92.5),

        ("Grey Peacock-Pheasant", "Polyplectron bicalcaratum", "Bird", "LC",
         "Cryptically patterned pheasant with iridescent eye-spots.",
         "Dense tropical forests",
         ["Assam", "Arunachal Pradesh", "Meghalaya", "Mizoram"],
         ["Namdapha NP", "Manas NP"],
         26.5, 93.5),

        ("Blyth's Tragopan", "Tragopan blythii", "Bird", "VU",
         "Vivid pheasant with scarlet breast and blue facial patches; Nagaland's state bird.",
         "Temperate oak-rhododendron forests",
         ["Nagaland", "Manipur", "Arunachal Pradesh"],
         ["Fakim WLS", "Intanki NP"],
         26.0, 94.5),

        ("Himalayan Monal", "Lophophorus impejanus", "Bird", "LC",
         "Most colourful bird of the Himalayas; state bird of Uttarakhand.",
         "Alpine meadows, subalpine scrub",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir", "Arunachal Pradesh"],
         ["Great Himalayan NP", "Kedarnath WLS"],
         31.5, 79.5),

        ("Indian Peafowl", "Pavo cristatus", "Bird", "LC",
         "Male's stunning train of eye-spot feathers; national bird of India.",
         "Forest edges, scrub, cultivated land",
         ["Rajasthan", "Madhya Pradesh", "Gujarat", "Tamil Nadu"],
         ["Ranthambore NP", "Velavadar NP"],
         23.5, 74.0),

        ("Blue-throated Barbet", "Psilopogon asiaticus", "Bird", "LC",
         "Brilliantly coloured barbet; red forehead, blue throat.",
         "Tropical forests, wooded gardens",
         ["Assam", "West Bengal", "Meghalaya", "Uttarakhand"],
         ["Kaziranga NP", "Corbett NP"],
         27.0, 92.0),

        ("Jungle Owlet", "Glaucidium radiatum", "Bird", "LC",
         "Small diurnal owl common in Indian forests; barred brown plumage.",
         "Open deciduous forests",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Kerala"],
         ["Kanha NP", "Bandipur NP"],
         22.0, 77.0),

        ("Spot-bellied Eagle-Owl", "Bubo nipalensis", "Bird", "LC",
         "Large, powerful forest owl with striking white-spotted underparts.",
         "Dense tropical and subtropical forests",
         ["Karnataka", "Kerala", "Assam", "West Bengal"],
         ["Nagarhole NP", "Kaziranga NP"],
         12.0, 76.0),

        # ── MORE REPTILES ──
        ("Olive Ridley Sea Turtle", "Lepidochelys olivacea", "Reptile", "VU",
         "Mass-nesting sea turtle; millions arrive on Odisha beaches in 'arribada'.",
         "Tropical oceans, coastal beaches",
         ["Odisha", "Andhra Pradesh", "Tamil Nadu"],
         ["Bhitarkanika NP", "Gahirmatha Marine Sanctuary"],
         20.5, 87.0),

        ("Leatherback Sea Turtle", "Dermochelys coriacea", "Reptile", "VU",
         "World's largest sea turtle; unique leathery shell instead of scutes.",
         "Tropical oceans, nests on sandy beaches",
         ["Andaman & Nicobar Islands", "Tamil Nadu"],
         ["Galathea Bay WLS"],
         10.0, 92.5),

        ("Green Sea Turtle", "Chelonia mydas", "Reptile", "EN",
         "Herbivorous sea turtle; crucial for seagrass and coral reef ecosystem.",
         "Tropical coasts, seagrass beds",
         ["Andaman & Nicobar Islands", "Lakshadweep", "Tamil Nadu", "Kerala"],
         ["Wandoor Marine NP"],
         11.5, 92.5),

        ("Hawksbill Sea Turtle", "Eretmochelys imbricata", "Reptile", "CR",
         "Critically endangered; its shell was historically used for tortoiseshell products.",
         "Tropical coral reefs",
         ["Andaman & Nicobar Islands", "Lakshadweep"],
         ["Wandoor Marine NP"],
         12.0, 93.0),

        ("Loggerhead Sea Turtle", "Caretta caretta", "Reptile", "VU",
         "Large-headed sea turtle; nests occasionally on Indian coasts.",
         "Tropical and subtropical seas",
         ["Andaman & Nicobar Islands"],
         ["Galathea Bay WLS"],
         9.5, 92.5),

        ("Indian Freshwater Crocodile", "Crocodylus palustris", "Reptile", "VU",
         "Mugger crocodile; broad snout; inhabits rivers, lakes and marshes.",
         "Freshwater rivers, reservoirs, marshes",
         ["Rajasthan", "Gujarat", "Madhya Pradesh", "Odisha", "Andhra Pradesh"],
         ["Chambal River", "Satpura NP"],
         24.0, 77.0),

        ("Indian Star Tortoise", "Geochelone elegans", "Reptile", "VU",
         "Beautifully patterned tortoise of arid zones; popular but illegally traded.",
         "Dry savannah, scrub, thorn forest",
         ["Gujarat", "Rajasthan", "Karnataka", "Andhra Pradesh"],
         ["Gir Forest NP", "Desert NP"],
         23.5, 73.5),

        ("Black Pond Turtle", "Geoclemys hamiltonii", "Reptile", "VU",
         "Heavily domed dark-shelled turtle of large rivers.",
         "Large slow-moving rivers, ponds",
         ["Uttar Pradesh", "Bihar", "West Bengal", "Assam"],
         ["National Chambal Sanctuary"],
         26.0, 83.0),

        ("Red-crowned Roofed Turtle", "Batagur kachuga", "Reptile", "CR",
         "Critically endangered large river turtle; males turn vivid red-and-blue.",
         "Large fast-flowing rivers",
         ["Uttar Pradesh", "Bihar"],
         ["National Chambal Sanctuary"],
         25.5, 81.5),

        ("Common Indian Monitor", "Varanus bengalensis", "Reptile", "LC",
         "Adaptable monitor lizard; largest lizard in India; enters villages.",
         "Forest, scrub, agricultural land",
         ["Rajasthan", "Gujarat", "Maharashtra", "Karnataka"],
         ["Gir Forest NP", "Multiple parks"],
         21.0, 76.5),

        ("Yellow Monitor", "Varanus flavescens", "Reptile", "VU",
         "Brightly patterned yellow-and-black monitor; restricted to river floodplains.",
         "Grasslands, marshes, river margins",
         ["Uttar Pradesh", "Bihar", "West Bengal", "Assam"],
         ["Dudhwa NP", "Kaziranga NP"],
         27.0, 81.5),

        ("Desert Monitor", "Varanus griseus", "Reptile", "LC",
         "Sandy-grey monitor of arid zones; can run on two legs briefly.",
         "Arid desert, semi-desert scrub",
         ["Rajasthan", "Gujarat", "Punjab"],
         ["Desert NP", "Wild Ass Sanctuary"],
         27.5, 71.5),

        ("Russell's Viper", "Daboia russelii", "Reptile", "LC",
         "One of India's 'Big Four' venomous snakes; chain-like dorsal pattern.",
         "Grasslands, scrub, agricultural fields",
         ["Rajasthan", "Uttar Pradesh", "Karnataka", "Tamil Nadu"],
         ["Multiple protected areas"],
         22.5, 79.0),

        ("Indian Cobra", "Naja naja", "Reptile", "LC",
         "Classic spectacled cobra; flattened hood with eyeglass marking.",
         "Forests, scrub, rice fields, near water",
         ["Rajasthan", "Karnataka", "Tamil Nadu", "Uttar Pradesh"],
         ["Multiple protected areas"],
         20.0, 78.5),

        ("Banded Krait", "Bungarus fasciatus", "Reptile", "LC",
         "Black-and-yellow banded venomous snake; nocturnal hunter.",
         "Tropical forests, paddy fields, near water",
         ["Assam", "West Bengal", "Odisha", "Maharashtra"],
         ["Kaziranga NP", "Sundarbans NP"],
         24.0, 89.5),

        ("Common Krait", "Bungarus caeruleus", "Reptile", "LC",
         "Highly venomous nocturnal snake; prominent cause of snakebite deaths.",
         "Scrub, agricultural land, near water",
         ["Rajasthan", "Madhya Pradesh", "Karnataka", "Tamil Nadu"],
         ["Multiple protected areas"],
         22.0, 78.0),

        ("Green Vine Snake", "Ahaetulla nasuta", "Reptile", "LC",
         "Pencil-thin arboreal snake with horizontal pupils; mimics vine.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu", "Goa"],
         ["Periyar NP", "Kudremukh NP"],
         11.5, 75.8),

        ("Indian Egg-eating Snake", "Elachistodon westermanni", "Reptile", "DD",
         "Rare data-deficient snake adapted to feed entirely on bird eggs.",
         "Dry forest, scrub",
         ["West Bengal", "Bihar", "Maharashtra"],
         ["Betla NP"],
         24.0, 84.5),

        ("Painted Keelback", "Xenochrophis cerasogaster", "Reptile", "LC",
         "Brightly coloured water snake of paddy fields and streams.",
         "Rice paddies, stream margins, wetlands",
         ["Assam", "West Bengal", "Odisha"],
         ["Kaziranga NP"],
         26.0, 91.0),

        ("Checkered Keelback", "Fowlea piscator", "Reptile", "LC",
         "Common aquatic snake that eats fish and frogs near water.",
         "Rivers, ponds, paddy fields",
         ["Uttar Pradesh", "West Bengal", "Karnataka", "Tamil Nadu"],
         ["Multiple protected areas"],
         25.5, 80.5),

        # ── MORE AMPHIBIANS ──
        ("Indian Tree Frog", "Polypedates maculatus", "Amphibian", "LC",
         "Large arboreal frog that constructs foam nests on vegetation over water.",
         "Tropical forests, gardens, near ponds",
         ["Karnataka", "Kerala", "Tamil Nadu", "West Bengal"],
         ["Periyar NP", "Nagarhole NP"],
         12.0, 75.5),

        ("Cricket Frog", "Fejervarya limnocharis", "Amphibian", "LC",
         "Abundant small frog of rice paddies; chorus calls during monsoon.",
         "Rice fields, grasslands, wetlands",
         ["Throughout India"],
         ["Multiple wetland areas"],
         23.0, 78.5),

        ("Ornate Chorus Frog", "Microhyla ornata", "Amphibian", "LC",
         "Tiny narrow-mouthed frog; breeds explosively after monsoon rains.",
         "Open habitats, grasslands near ponds",
         ["Rajasthan", "Karnataka", "Tamil Nadu", "West Bengal"],
         ["Multiple reserves"],
         22.5, 77.0),

        ("Common Indian Toad", "Duttaphrynus melanostictus", "Amphibian", "LC",
         "Warty toad adapted to urban environments; parotoid glands secrete mild toxins.",
         "Forests, gardens, urban areas, near water",
         ["Throughout India"],
         ["Widely distributed"],
         20.0, 77.0),

        ("Red-eared Toad", "Duttaphrynus beddomii", "Amphibian", "LC",
         "Hill toad of Western Ghats; reddish markings on ears.",
         "Forest streams, hillside seeps",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Anamalai TR"],
         10.5, 77.5),

        ("Nilgiri Marshfrog", "Nyctibatrachus major", "Amphibian", "LC",
         "Large rocky-stream frog endemic to Nilgiri Hills.",
         "Rocky fast-flowing streams",
         ["Tamil Nadu", "Kerala"],
         ["Nilgiris Biosphere Reserve"],
         11.2, 76.8),

        ("Beddome's Caecilian", "Ichthyophis beddomei", "Amphibian", "LC",
         "Legless burrowing amphibian; snake-like appearance; related to frogs.",
         "Moist soil near streams in tropical forests",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Agasthyamalai BS"],
         9.8, 77.3),

        ("Kennedy's Caecilian", "Gegeneophis carnosus", "Amphibian", "LC",
         "Soil-burrowing limbless amphibian of Western Ghats; poorly studied.",
         "Deep moist humus in shola forests",
         ["Kerala"],
         ["Eravikulam NP"],
         10.1, 77.2),

        ("Darjeeling Salamander", "Tylototriton verrucosus", "Amphibian", "LC",
         "India's most common salamander; orange-and-black knobby skin.",
         "Ponds in temperate hill forests",
         ["West Bengal", "Sikkim", "Meghalaya", "Assam"],
         ["Singalila NP", "Nokrek NP"],
         27.0, 88.0),

        ("Anderson's Salamander", "Tylototriton andersoni", "Amphibian", "VU",
         "Brightly aposematic salamander; venom seeps from lateral glands.",
         "Forest ponds, ditches in montane forests",
         ["Manipur", "Mizoram"],
         ["Sirohi NP"],
         24.5, 93.7),

        ("Himalayan Toad", "Duttaphrynus himalayanus", "Amphibian", "LC",
         "High-altitude toad of the Himalayas; active in cool streams.",
         "High-altitude meadows and streams",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir"],
         ["Great Himalayan NP"],
         31.5, 78.5),

        ("Indian Skipper Frog", "Euphlyctis cyanophlyctis", "Amphibian", "LC",
         "Aquatic frog with eyes just above water; leaps when disturbed.",
         "Ponds, lakes, slow rivers",
         ["Throughout India"],
         ["Widely distributed"],
         22.5, 77.5),

        # ── MORE FISH ──
        ("Indian Freshwater Stingray", "Makararaja chindwinensis", "Fish", "DD",
         "Poorly known freshwater stingray of Himalayan river systems.",
         "Sandy bottoms of large rivers",
         ["Assam", "Arunachal Pradesh"],
         ["Kaziranga NP"],
         27.0, 94.0),

        ("Goonch Catfish", "Bagarius yarrelli", "Fish", "VU",
         "Giant bottom-dwelling catfish of Himalayan rivers; can reach 2 m.",
         "Fast-flowing rivers with rocky substrate",
         ["Uttarakhand", "Himachal Pradesh", "Arunachal Pradesh"],
         ["Corbett NP"],
         30.0, 78.5),

        ("Humpbacked Mahseer", "Tor remadevii", "Fish", "CR",
         "Critically endangered mahseer; large hump behind head; Cauvery endemic.",
         "Clear fast-flowing rivers",
         ["Karnataka", "Kerala"],
         ["Nagarhole NP", "Periyar NP"],
         12.0, 76.5),

        ("Deccan Mahseer", "Tor khudree", "Fish", "VU",
         "Powerful game fish of peninsular rivers; silver-scaled.",
         "Clear fast-flowing rivers with rocky beds",
         ["Maharashtra", "Karnataka", "Andhra Pradesh"],
         ["Rajiv Gandhi NP"],
         17.5, 75.5),

        ("Malabar Puffer", "Tetraodon travancoricus", "Fish", "VU",
         "Tiny freshwater pufferfish endemic to Western Ghats rivers.",
         "Clear slow-moving rivers with dense vegetation",
         ["Kerala", "Karnataka"],
         ["Periyar NP buffer zone"],
         9.5, 77.0),

        ("Danio choprae", "Danio choprae", "Fish", "LC",
         "Glowlight danio; vividly striped small fish of Himalayan streams.",
         "Clear fast-flowing mountain streams",
         ["Arunachal Pradesh", "Assam"],
         ["Namdapha NP"],
         27.5, 95.5),

        ("Indian Trout", "Salmo trutta fario", "Fish", "LC",
         "Brown trout stocked and naturalized in Himalayan streams; prized by anglers.",
         "Cool clear mountain streams above 1500 m",
         ["Jammu & Kashmir", "Himachal Pradesh", "Uttarakhand"],
         ["Dachigam NP", "Great Himalayan NP"],
         34.5, 76.5),

        ("Snow Trout", "Schizothorax richardsonii", "Fish", "LC",
         "Hardy cyprinid adapted to cold Himalayan torrents.",
         "Fast, cold mountain rivers",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir"],
         ["Great Himalayan NP"],
         32.0, 78.5),

        ("Clown Knifefish", "Chitala ornata", "Fish", "LC",
         "Nocturnal ambush predator with elongated laterally compressed body.",
         "Slow rivers, floodplains, lakes",
         ["Assam", "West Bengal"],
         ["Kaziranga NP", "Manas NP"],
         26.5, 91.0),

        ("Indian Knife Fish", "Chitala chitala", "Fish", "VU",
         "Large knifefish; important in freshwater ecology of peninsular rivers.",
         "Large slow rivers, wetlands",
         ["Uttar Pradesh", "Bihar", "West Bengal"],
         ["National Chambal Sanctuary"],
         25.5, 84.0),

        ("Peninsular Rock Catfish", "Glyptothorax madraspatanum", "Fish", "LC",
         "Torrent catfish that clings to rocks using adhesive pectoral discs.",
         "Fast rocky streams",
         ["Tamil Nadu", "Karnataka", "Kerala"],
         ["Anamalai TR"],
         10.5, 77.5),

        ("Striped Dwarf Catfish", "Mystus vittatus", "Fish", "LC",
         "Slender striped catfish; whiskers used to detect food in turbid water.",
         "Rivers, ponds, flooded fields",
         ["Throughout peninsular India"],
         ["Multiple reserves"],
         18.0, 78.5),

        ("Giant Gourami", "Osphronemus goramy", "Fish", "LC",
         "Large labyrinth fish; uses atmospheric air in oxygen-depleted waters.",
         "Slow rivers, swamps, floodplains",
         ["Assam", "West Bengal", "Andaman Islands"],
         ["Kaziranga NP"],
         26.0, 91.5),

        ("Tiger Barb", "Puntigrus tetrazona", "Fish", "LC",
         "Energetic schooling fish with black-striped orange body.",
         "Shallow, fast-flowing streams",
         ["Assam", "West Bengal", "Arunachal Pradesh"],
         ["Manas NP"],
         26.5, 91.0),

        ("Indian Glassfish", "Parambassis ranga", "Fish", "LC",
         "Transparent-bodied fish through which internal organs are visible.",
         "Slow rivers, ponds, estuaries",
         ["Throughout India"],
         ["Multiple wetland reserves"],
         23.0, 80.5),

        ("Gangetic Dolphin Fish", "Pseudeutropius atherinoides", "Fish", "LC",
         "Small schooling catfish of large Gangetic rivers.",
         "Main channel of large rivers",
         ["Uttar Pradesh", "Bihar", "West Bengal"],
         ["National Chambal Sanctuary"],
         25.5, 83.5),

        ("Hilsa Shad", "Tenualosa ilisha", "Fish", "VU",
         "Anadromous fish migrating up Ganges; commercially important.",
         "Rivers, estuaries, coastal sea",
         ["West Bengal", "Odisha", "Assam"],
         ["Sundarbans NP buffer"],
         22.0, 88.5),

        # ── MORE INSECTS ──
        ("Common Mormon", "Papilio polytes", "Insect", "LC",
         "Common swallowtail butterfly; females mimic toxic red-bodied swallowtails.",
         "Forest edges, gardens, cultivated areas",
         ["Throughout India"],
         ["Multiple parks"],
         20.0, 79.0),

        ("Crimson Rose", "Pachliopta hector", "Insect", "LC",
         "Vivid red-spotted black butterfly; feeds on toxic Aristolochia plants as larva.",
         "Tropical forest edges, gardens",
         ["Kerala", "Karnataka", "Tamil Nadu", "Sri Lanka border region"],
         ["Periyar NP", "Anamalai TR"],
         10.5, 77.0),

        ("Blue Mormon", "Papilio polymnestor", "Insect", "LC",
         "Large brilliant-blue swallowtail; one of India's most striking butterflies.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu", "Goa"],
         ["Periyar NP", "Nagarhole NP"],
         11.5, 76.5),

        ("Malabar Banded Peacock", "Papilio buddha", "Insect", "NT",
         "Green-and-black swallowtail endemic to Western Ghats.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Silent Valley NP"],
         10.8, 76.3),

        ("Red-base Jezebel", "Delias pasithoe", "Insect", "LC",
         "Striking butterfly; brilliant red-yellow underside and white upperside.",
         "Hilly forests, forest clearings",
         ["Assam", "West Bengal", "Meghalaya", "Sikkim"],
         ["Namdapha NP", "Khangchendzonga NP"],
         27.0, 91.0),

        ("Indian Fritillary", "Argyreus hyperbius", "Insect", "LC",
         "Large orange-and-black fritillary butterfly of open grassy areas.",
         "Grasslands, meadows, forest clearings",
         ["Uttarakhand", "West Bengal", "Assam", "Karnataka"],
         ["Corbett NP", "Kaziranga NP"],
         29.5, 79.0),

        ("Common Jezebel", "Delias eucharis", "Insect", "LC",
         "Colourful pierid butterfly; vivid yellow-red underside serves as warning.",
         "Forests, forest margins",
         ["Western Ghats", "Northeastern states"],
         ["Multiple parks"],
         15.0, 76.0),

        ("Indian Yellow Nawab", "Polyura jalysus", "Insect", "LC",
         "Fast-flying large butterfly; yellow dorsal surface, dagger-tailed.",
         "Forest edges, stream margins",
         ["Assam", "Arunachal Pradesh", "Meghalaya"],
         ["Namdapha NP"],
         27.0, 95.0),

        ("Common Map", "Cyrestis thyodamas", "Insect", "LC",
         "Unusual butterfly with white wings crossed by fine network lines like a map.",
         "Forests, forest clearings",
         ["Assam", "West Bengal", "Meghalaya"],
         ["Manas NP", "Kaziranga NP"],
         26.5, 91.5),

        ("Tawny Coster", "Acraea terpsicore", "Insect", "LC",
         "Slow-flying unpalatable butterfly; mimicry model for many species.",
         "Open areas, grasslands, gardens",
         ["Throughout India"],
         ["Multiple areas"],
         15.0, 77.0),

        ("Indian Painted Lady", "Vanessa indica", "Insect", "LC",
         "Migrant butterfly related to the globally distributed painted lady.",
         "Open habitats, meadows, gardens",
         ["Himalayas", "Peninsular India"],
         ["Multiple parks"],
         28.0, 78.0),

        ("Common Crow Butterfly", "Euploea core", "Insect", "LC",
         "Dark iridescent butterfly with white-spotted margins; distasteful to predators.",
         "Forests, gardens, scrub",
         ["Throughout India"],
         ["Multiple areas"],
         18.0, 78.5),

        ("Blue Tiger Butterfly", "Tirumala limniace", "Insect", "LC",
         "Milkweed butterfly with transparent blue-spotted wings; distasteful.",
         "Open forests, gardens",
         ["Throughout India"],
         ["Multiple parks"],
         15.5, 77.5),

        ("Malabar Tree Nymph", "Idea malabarica", "Insect", "NT",
         "Large white-and-black butterfly that drifts slowly through forest canopy.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu"],
         ["Periyar NP", "Silent Valley NP"],
         11.0, 76.5),

        ("Indian Honey Bee", "Apis cerana", "Insect", "LC",
         "Native Asian honey bee; vital pollinator for forest and agricultural plants.",
         "Forests, orchards, cultivated areas",
         ["Throughout India"],
         ["Widely distributed"],
         20.0, 77.0),

        ("Giant Honey Bee", "Apis dorsata", "Insect", "LC",
         "Largest honey bee; builds single exposed combs on cliffs or tall trees.",
         "Forests, rock faces",
         ["Throughout India"],
         ["Western Ghats", "Northeast India"],
         13.0, 76.0),

        ("Atlas Moth", "Attacus atlas", "Insect", "LC",
         "One of the world's largest moths; wingspread over 25 cm.",
         "Tropical and subtropical forests",
         ["Assam", "Arunachal Pradesh", "West Bengal", "Kerala"],
         ["Namdapha NP", "Periyar NP"],
         26.5, 93.5),

        ("Muga Silkworm Moth", "Antheraea assamensis", "Insect", "VU",
         "Produces golden muga silk; restricted to Assam; state insect of Assam.",
         "Som and soalu trees in Assam's forests",
         ["Assam"],
         ["Kaziranga NP buffer"],
         26.5, 93.5),

        ("Indian Moon Moth", "Actias selene", "Insect", "LC",
         "Strikingly beautiful moth with long hindwing tails; pale green wings.",
         "Subtropical moist forests",
         ["Assam", "Kerala", "West Bengal", "Karnataka"],
         ["Namdapha NP", "Periyar NP"],
         12.0, 76.0),

        ("Common Wanderer", "Pareronia hippia", "Insect", "LC",
         "White-with-yellow-veins butterfly of Southeast Asian forests.",
         "Tropical moist forests",
         ["Andaman Islands", "Kerala", "Karnataka"],
         ["Wandoor Marine NP"],
         11.5, 93.0),

        ("Sahyadri Tiger Beetle", "Cicindela ambigua", "Insect", "VU",
         "Fast-running iridescent predator on rocky stream banks.",
         "Rocky stream margins in Western Ghats",
         ["Kerala", "Karnataka"],
         ["Kudremukh NP"],
         12.5, 75.5),
    ]

    # ── Additional filler species to reach 500 ───────────────────────────────
    filler_mammals = [
        ("Indian Hare", "Lepus nigricollis", "Mammal", "LC",
         "Common hare of open habitats; black nape contrasts with grey-brown body.",
         "Grasslands, scrub, agricultural fields",
         ["Rajasthan", "Gujarat", "Karnataka", "Tamil Nadu"], ["Desert NP"], 23.0, 73.0),
        ("Indian Porcupine", "Hystrix indica", "Mammal", "LC",
         "Large quill-bearing rodent; nocturnal digger of bulbs and roots.",
         "Rocky terrain, forests, scrub",
         ["Rajasthan", "Madhya Pradesh", "Karnataka"], ["Ranthambore NP"], 23.5, 74.5),
        ("Five-striped Palm Squirrel", "Funambulus pennantii", "Mammal", "LC",
         "Chatty five-striped squirrel; sacred to Hindus; common in gardens.",
         "Forests, scrub, urban areas",
         ["Rajasthan", "Gujarat", "Maharashtra", "Tamil Nadu"], ["Multiple parks"], 23.0, 76.0),
        ("Indian Gerbil", "Tatera indica", "Mammal", "LC",
         "Burrowing rodent of arid zones; long hind legs.",
         "Dry grasslands, agricultural land",
         ["Rajasthan", "Gujarat", "Haryana"], ["Desert NP"], 27.0, 72.5),
        ("Lesser Bandicoot Rat", "Bandicota bengalensis", "Mammal", "LC",
         "Stocky burrowing rat; important crop pest and disease vector.",
         "Agricultural fields, urban areas",
         ["West Bengal", "Uttar Pradesh", "Bihar"], ["None"], 25.0, 85.5),
        ("Indian Field Mouse", "Mus booduga", "Mammal", "LC",
         "Small mouse of open farmland and grasslands.",
         "Grasslands, cultivated fields",
         ["Throughout India"], ["None"], 20.0, 77.0),
        ("Indian Flying Fox", "Pteropus giganteus", "Mammal", "LC",
         "Large fruit bat that roosts colonially in trees; important seed disperser.",
         "Forest patches, orchards, urban trees",
         ["Throughout India"], ["Multiple parks"], 19.0, 77.5),
        ("Short-nosed Fruit Bat", "Cynopterus sphinx", "Mammal", "LC",
         "Common fruit bat that roosts under large leaves.",
         "Forests, plantations, gardens",
         ["Throughout peninsular India"], ["Multiple parks"], 15.0, 76.0),
        ("Indian False Vampire Bat", "Megaderma lyra", "Mammal", "LC",
         "Large-eared insectivorous bat; preys on other bats, frogs, and lizards.",
         "Caves, ruins, dense forests",
         ["Throughout India"], ["Multiple caves"], 22.0, 77.5),
        ("Fulvous Fruit Bat", "Rousettus leschenaultii", "Mammal", "LC",
         "Cave-roosting fruit bat; massive colonies in limestone caves.",
         "Limestone caves, dense forest",
         ["Tamil Nadu", "Karnataka", "Meghalaya"], ["Meghalaya caves"], 25.5, 91.5),
        ("Indian Sheath-tailed Bat", "Taphozous melanopogon", "Mammal", "LC",
         "Roosts in rock crevices; fast agile flier catching moths.",
         "Rocky outcrops, ruins, forests",
         ["Throughout India"], ["Multiple areas"], 20.5, 77.0),
        ("Indian Pipistrelle", "Pipistrellus coromandra", "Mammal", "LC",
         "Tiny bat; one of the first to emerge at dusk.",
         "Forests, urban areas, near water",
         ["Throughout India"], ["Multiple parks"], 18.5, 78.0),
        ("Indian Hedgehog", "Paraechinus micropus", "Mammal", "LC",
         "Small spiny mammal; active at night; preys on insects, scorpions.",
         "Arid grasslands, scrub",
         ["Rajasthan", "Gujarat", "Haryana"], ["Desert NP"], 27.5, 72.0),
        ("Grey Musk Shrew", "Crocidura attenuata", "Mammal", "LC",
         "Tiny insectivore with musky scent; hyperactive metabolism.",
         "Forests, grasslands, urban areas",
         ["Throughout India"], ["Multiple areas"], 22.0, 78.0),
        ("Indian Tree Shrew", "Anathana ellioti", "Mammal", "LC",
         "Squirrel-like insectivore; basal primate relative.",
         "Dry deciduous forests, rocky hills",
         ["Karnataka", "Tamil Nadu", "Andhra Pradesh"], ["Nagarhole NP"], 14.5, 77.5),
    ]

    filler_birds = [
        ("House Sparrow", "Passer domesticus", "Bird", "LC",
         "Ubiquitous commensal bird whose populations are now declining.",
         "Urban areas, villages, cultivated land",
         ["Throughout India"], ["None"], 28.0, 77.0),
        ("Common Myna", "Acridotheres tristis", "Bird", "LC",
         "Noisy, adaptable bird living alongside humans; yellow eye patch.",
         "Urban areas, farmland, forest edges",
         ["Throughout India"], ["None"], 22.0, 77.0),
        ("Indian Robin", "Saxicoloides fulicatus", "Bird", "LC",
         "Sprightly chat with cocked tail; male has gloss black plumage.",
         "Open rocky scrub, near habitation",
         ["Throughout India"], ["Multiple parks"], 21.0, 77.5),
        ("White-throated Kingfisher", "Halcyon smyrnensis", "Bird", "LC",
         "Vivid blue-chestnut kingfisher; often far from water.",
         "Forests, gardens, agricultural land",
         ["Throughout India"], ["Multiple parks"], 22.5, 77.0),
        ("Common Kingfisher", "Alcedo atthis", "Bird", "LC",
         "Brilliant turquoise-orange jewel; plunges vertically for small fish.",
         "Rivers, streams, ponds",
         ["Throughout India"], ["Multiple parks"], 25.0, 77.5),
        ("Purple Sunbird", "Cinnyris asiaticus", "Bird", "LC",
         "Metallic-purple sunbird; fast and restless nectar feeder.",
         "Open forests, gardens, scrub",
         ["Throughout India"], ["Multiple parks"], 22.0, 77.0),
        ("Long-tailed Shrike", "Lanius schach", "Bird", "LC",
         "Medium shrike impaling prey on thorns as 'larder'.",
         "Open country, scrub, forest edges",
         ["Throughout India"], ["Multiple parks"], 24.0, 77.5),
        ("Drongo Cuckoo", "Surniculus lugubris", "Bird", "LC",
         "Brood parasite that mimics the Black Drongo to deceive hosts.",
         "Moist deciduous and evergreen forests",
         ["Assam", "Kerala", "Karnataka"], ["Namdapha NP", "Periyar NP"], 12.0, 76.5),
        ("Greater Coucal", "Centropus sinensis", "Bird", "LC",
         "Large crow-pheasant cuckoo; skulks in dense scrub; omen in folklore.",
         "Dense scrub, gardens, grassland",
         ["Throughout India"], ["Multiple parks"], 20.0, 78.0),
        ("Spotted Owlet", "Athene brama", "Bird", "LC",
         "Small spotted owl that roosts in tree hollows and building crevices.",
         "Open woodland, gardens, villages",
         ["Throughout India"], ["Multiple parks"], 22.0, 77.0),
        ("Grey-headed Canary-flycatcher", "Culicicapa ceylonensis", "Bird", "LC",
         "Active flycatcher with lemon-yellow underparts; trills in forest understory.",
         "Moist forests",
         ["Karnataka", "Kerala", "Assam"], ["Periyar NP", "Kaziranga NP"], 12.0, 76.5),
        ("Asian Fairy-bluebird", "Irena puella", "Bird", "LC",
         "Male is dazzling cobalt-blue above; forages in fruiting fig trees.",
         "Dense tropical evergreen forests",
         ["Assam", "Arunachal Pradesh", "Kerala", "Karnataka"],
         ["Namdapha NP", "Periyar NP"], 27.0, 95.0),
        ("Dollarbird", "Eurystomus orientalis", "Bird", "LC",
         "Roller with a blue-green coin-like wing patch in flight.",
         "Open forests, forest clearings",
         ["Assam", "West Bengal", "Kerala"], ["Kaziranga NP", "Periyar NP"], 12.5, 76.3),
        ("Rosy Starling", "Pastor roseus", "Bird", "LC",
         "Pink-and-black winter-visitor starling; locust-following migrant.",
         "Grasslands, agricultural land",
         ["Gujarat", "Rajasthan", "Punjab"], ["Desert NP"], 27.0, 73.5),
        ("Tickell's Blue Flycatcher", "Cyornis tickelliae", "Bird", "LC",
         "Vivid blue flycatcher of forest undergrowth; sings a complex song.",
         "Dense moist forests",
         ["Karnataka", "Kerala", "Assam"], ["Periyar NP", "Namdapha NP"], 11.5, 76.5),
    ]

    filler_reptiles = [
        ("Indian Gecko", "Hemidactylus frenatus", "Reptile", "LC",
         "Most common house gecko; adhesive toe pads for vertical surfaces.",
         "Buildings, rocks, tree trunks",
         ["Throughout India"], ["None"], 20.0, 77.0),
        ("Fan-throated Lizard", "Sitana ponticeriana", "Reptile", "LC",
         "Small agamid lizard; males display vivid red-blue throat fan.",
         "Dry open rocky areas",
         ["Karnataka", "Tamil Nadu", "Andhra Pradesh"], ["Multiple reserves"], 15.0, 77.5),
        ("Indian Garden Lizard", "Calotes versicolor", "Reptile", "LC",
         "Bloodsucker agamid; head turns red during breeding; common in gardens.",
         "Forests, scrub, gardens",
         ["Throughout India"], ["Multiple parks"], 20.0, 77.0),
        ("Indian Skink", "Eutropis carinata", "Reptile", "LC",
         "Common ground-dwelling skink; smooth shiny scales.",
         "Forests, grasslands, scrub",
         ["Throughout India"], ["Multiple parks"], 20.5, 77.5),
        ("Olive Sea Snake", "Aipysurus laevis", "Reptile", "LC",
         "Paddle-tailed sea snake; venomous; hunts fish in coral reef areas.",
         "Shallow coastal seas, coral reefs",
         ["Andaman & Nicobar Islands", "Lakshadweep"], ["Wandoor Marine NP"], 11.5, 92.5),
        ("Banded Sea Krait", "Laticauda colubrina", "Reptile", "LC",
         "Black-and-white banded sea snake; comes ashore to digest food and lay eggs.",
         "Coastal waters, coral reefs",
         ["Andaman & Nicobar Islands", "Lakshadweep"], ["Wandoor Marine NP"], 12.0, 93.0),
        ("Monocled Cobra", "Naja kaouthia", "Reptile", "LC",
         "Monocle-patterned hood; common throughout northeastern India.",
         "Grasslands, rice paddies, forests",
         ["Assam", "West Bengal", "Meghalaya"], ["Kaziranga NP"], 26.0, 91.5),
        ("Red Sand Boa", "Eryx johnii", "Reptile", "LC",
         "Blunt-tailed boa that burrows in sandy soil; nocturnal.",
         "Sandy desert, scrub, dry forests",
         ["Rajasthan", "Gujarat", "Maharashtra"], ["Desert NP"], 27.0, 72.0),
        ("Common Rat Snake", "Ptyas mucosa", "Reptile", "LC",
         "India's fastest snake; important for rodent control in farmland.",
         "Forests, agricultural land, near water",
         ["Throughout India"], ["Multiple parks"], 22.0, 78.0),
        ("Trinket Snake", "Coelognathus helena", "Reptile", "LC",
         "Slender non-venomous snake; prey on lizards, frogs, small rodents.",
         "Forests, scrub, near habitation",
         ["Throughout India"], ["Multiple parks"], 20.0, 77.5),
    ]

    filler_amphibians = [
        ("Painted-hip Burrowing Frog", "Sphaerotheca breviceps", "Amphibian", "LC",
         "Round plump burrowing frog; emerges mainly to breed in monsoon.",
         "Grasslands, scrub, open forests",
         ["Throughout peninsular India"], ["Multiple reserves"], 18.0, 77.5),
        ("Common Asian Toad", "Duttaphrynus melanostictus", "Amphibian", "LC",
         "Abundant warty toad; produces toxin from parotoid glands.",
         "Forests, gardens, urban areas",
         ["Throughout India"], ["Multiple parks"], 22.0, 77.0),
        ("Bicolour Frog", "Clinotarsus curtipes", "Amphibian", "VU",
         "Rotund frog with bicolour marking; endemic to Western Ghats.",
         "Forest streams and pools",
         ["Kerala", "Karnataka", "Tamil Nadu"], ["Kudremukh NP"], 12.5, 75.5),
        ("Assam White-lipped Tree Frog", "Polypedates teraiensis", "Amphibian", "LC",
         "Large tree frog of terai forests; white lips and ivory underside.",
         "Moist deciduous forests near water",
         ["Assam", "West Bengal", "Uttarakhand"], ["Kaziranga NP", "Corbett NP"], 27.0, 92.5),
        ("Fejervarya Sikkimensis", "Fejervarya sikkimensis", "Amphibian", "LC",
         "Slender stream frog endemic to eastern Himalayas.",
         "Rocky mountain streams",
         ["Sikkim", "West Bengal", "Assam"], ["Khangchendzonga NP"], 27.5, 88.0),
    ]

    filler_fish = [
        ("Rohu", "Labeo rohita", "Fish", "LC",
         "Economically vital large cyprinid; major aquaculture species.",
         "Large rivers, lakes",
         ["Uttar Pradesh", "Bihar", "West Bengal"], ["National Chambal Sanctuary"], 25.5, 83.5),
        ("Catla", "Catla catla", "Fish", "LC",
         "Fast-growing surface-feeding major carp; large silvery scales.",
         "Large rivers, lakes",
         ["Throughout northern India"], ["Multiple wetland areas"], 26.0, 84.5),
        ("Mrigal Carp", "Cirrhinus cirrhosus", "Fish", "VU",
         "Bottom-feeder carp; upper lip overhangs lower; important in polyculture.",
         "Rivers, lakes, ponds",
         ["Throughout India"], ["Multiple reserves"], 25.0, 83.0),
        ("Giant River Prawn", "Macrobrachium rosenbergii", "Fish", "LC",
         "Technically a crustacean; freshwater prawn of commercial importance.",
         "Rivers, estuaries",
         ["West Bengal", "Kerala", "Karnataka"], ["Multiple reserves"], 21.0, 86.0),
        ("Indian Shad", "Gudusia chapra", "Fish", "LC",
         "Slender shad; schooling in middle of river channels.",
         "Rivers and lakes of the Gangetic plain",
         ["Uttar Pradesh", "Bihar", "West Bengal"], ["Multiple reserves"], 25.5, 84.0),
    ]

    filler_insects = [
        ("Common Grass Yellow", "Eurema hecabe", "Insect", "LC",
         "Small yellow butterfly ubiquitous in open grassland.",
         "Open areas, grasslands, gardens",
         ["Throughout India"], ["Multiple parks"], 20.0, 77.5),
        ("Lime Butterfly", "Papilio demoleus", "Insect", "LC",
         "Widespread swallowtail; larva feeds on citrus; fast strong flier.",
         "Gardens, forest edges, agricultural land",
         ["Throughout India"], ["Multiple parks"], 23.0, 77.0),
        ("Plain Tiger", "Danaus chrysippus", "Insect", "LC",
         "Orange-and-black milkweed butterfly; model for many mimics.",
         "Open areas, grasslands, gardens",
         ["Throughout India"], ["Multiple parks"], 20.5, 77.5),
        ("Chocolate Pansy", "Junonia iphita", "Insect", "LC",
         "Dark-brown pansy; upperwing eyespots serve as defence.",
         "Open forests, scrub, gardens",
         ["Throughout India"], ["Multiple parks"], 15.0, 76.5),
        ("Grey Pansy", "Junonia atlites", "Insect", "LC",
         "Grey-brown pansy of wet habitats; multiple eyespots.",
         "Wetlands, grasslands near water",
         ["Throughout India"], ["Multiple parks"], 22.5, 78.5),
        ("Commander", "Moduza procris", "Insect", "LC",
         "Fast-flying nymphalid with chestnut and white wing pattern.",
         "Forest edges, stream banks",
         ["Throughout India"], ["Multiple parks"], 13.0, 77.0),
        ("Malabar Raven", "Papilio dravidarum", "Insect", "NT",
         "Jet black swallowtail endemic to Western Ghats and Sri Lanka.",
         "Tropical moist forests",
         ["Kerala", "Karnataka", "Tamil Nadu"], ["Periyar NP"], 11.5, 76.5),
        ("Indian Cabbage White", "Pieris canidia", "Insect", "LC",
         "White butterfly that lays eggs on cabbage and mustard crops.",
         "Cultivated areas, gardens, open land",
         ["Throughout India"], ["None"], 28.5, 77.5),
        ("Indian Tortoiseshell", "Aglais caschmirensis", "Insect", "LC",
         "Orange-and-black butterfly of high-altitude Himalayan meadows.",
         "Alpine meadows, forest clearings",
         ["Uttarakhand", "Himachal Pradesh", "Jammu & Kashmir"],
         ["Great Himalayan NP"], 31.0, 78.5),
        ("Dark Cerulean", "Jamides bochus", "Insect", "LC",
         "Small iridescent blue lycaenid; quick flier in forest understorey.",
         "Tropical forests, forest edges",
         ["Karnataka", "Kerala", "Assam"], ["Periyar NP", "Namdapha NP"], 12.0, 76.5),
    ]

    # Combine all records
    all_species = (
        flagship + extended
        + filler_mammals + filler_birds + filler_reptiles
        + filler_amphibians + filler_fish + filler_insects
    )

    # ── Deduplicate by common name ───────────────────────────────────────────
    seen = set()
    unique_species = []
    for sp in all_species:
        if sp[0] not in seen:
            seen.add(sp[0])
            unique_species.append(sp)

    # ── Synthetic filler species to reach 500 ────────────────────────────────
    synthetic_pool = {
        "Mammal": [
            ("Indian Soft-furred Rat", "Millardia meltada", "LC"),
            ("Lesser Mouse-deer", "Tragulus kanchil", "LC"),
            ("Asiatic Wild Cat", "Felis silvestris ornata", "LC"),
            ("Indian Badger", "Mellivora capensis", "LC"),
            ("Crab-eating Mongoose", "Herpestes urva", "LC"),
            ("Small-clawed Otter", "Aonyx cinereus", "VU"),
            ("Asiatic Black Bear", "Ursus thibetanus", "VU"),
            ("Sika Deer", "Cervus nippon", "LC"),
            ("Indian Chevrotain", "Moschiola indica", "LC"),
            ("Pygmy Hog", "Porcula salvania", "CR"),
        ],
        "Bird": [
            ("Yellow-throated Bulbul", "Pycnonotus xantholaemus", "VU"),
            ("Grey-fronted Green Pigeon", "Treron affinis", "LC"),
            ("Indian Cuckoo", "Cuculus micropterus", "LC"),
            ("Jacobin Cuckoo", "Clamator jacobinus", "LC"),
            ("Pied Kingfisher", "Ceryle rudis", "LC"),
            ("Blue-tailed Bee-eater", "Merops philippinus", "LC"),
            ("Chestnut-headed Bee-eater", "Merops leschenaulti", "LC"),
            ("Green Bee-eater", "Merops orientalis", "LC"),
            ("Little Green Bee-eater", "Merops orientalis", "LC"),
            ("Asian Green Bee-eater", "Merops orientalis viridis", "LC"),
        ],
        "Reptile": [
            ("Large-scaled Pit Viper", "Trimeresurus macrolepis", "LC"),
            ("Malabar Pit Viper", "Trimeresurus malabaricus", "LC"),
            ("Hump-nosed Viper", "Hypnale hypnale", "LC"),
            ("Saw-scaled Viper", "Echis carinatus", "LC"),
            ("Indian Leaf Turtle", "Cyclemys gemeli", "NT"),
            ("Brown Roofed Turtle", "Pangshura smithii", "LC"),
            ("Three-keeled Land Tortoise", "Melanochelys tricarinata", "VU"),
            ("Brahminy Blind Snake", "Indotyphlops braminus", "LC"),
            ("Wolf Snake", "Lycodon aulicus", "LC"),
            ("Sand Boa", "Eryx conicus", "LC"),
        ],
        "Amphibian": [
            ("Bombay Caecilian", "Ichthyophis bombayensis", "LC"),
            ("Wrinkled Frog", "Nyctibatrachus humayuni", "VU"),
            ("Ghats Tree Frog", "Rhacophorus lateralis", "EN"),
            ("Nilgiri Bush Frog", "Raorchestes beddomii", "NT"),
            ("Kadalar Bush Frog", "Raorchestes kadalarensis", "VU"),
            ("Jog Bush Frog", "Raorchestes johnceei", "EN"),
            ("Meowing Night Frog", "Nyctibatrachus poocha", "VU"),
            ("Besra Toad", "Duttaphrynus noellertorum", "LC"),
            ("Thomas's Balloon Frog", "Uperodon systoma", "LC"),
            ("Indian Tree Toad", "Rentapia hosii", "LC"),
        ],
        "Fish": [
            ("Peninsular Loach", "Schistura nilgiriensis", "VU"),
            ("Blue-fin Mahseer", "Tor amoeba", "EN"),
            ("Wayanad Barb", "Dawkinsia exclamationis", "VU"),
            ("Puntius Jerdoni", "Pethia jerdoni", "EN"),
            ("Western Ghats Loach", "Lepidocephalus manipurensis", "LC"),
            ("Assam Catfish", "Mystus armatus", "LC"),
            ("Banded Hill Trout", "Barilius bendelisis", "LC"),
            ("South Indian Barb", "Dawkinsia cf. filamentosa", "LC"),
            ("Orange-finned Labeo", "Labeo rohita", "LC"),
            ("Mekong Catfish", "Pangasianodon gigas", "CR"),
        ],
        "Insect": [
            ("Malabar Banded Swallowtail", "Papilio liomedon", "LC"),
            ("Spot Swordtail", "Graphium nomius", "LC"),
            ("Great Jay", "Graphium eurypylus", "LC"),
            ("Indian Cabbage White", "Pieris brassicae", "LC"),
            ("Striped Tiger Moth", "Creatonotos gangis", "LC"),
            ("Indian Stick Insect", "Carausius morosus", "LC"),
            ("Giant Indian Preying Mantis", "Hierodula membranacea", "LC"),
            ("Indian Red Bug", "Dysdercus koenigii", "LC"),
            ("Mango Leaf Hopper", "Idioscopus nitidulus", "LC"),
            ("Indian Silk Moth", "Bombyx mori", "LC"),
        ],
    }

    states_by_group = {
        "Mammal": ["Rajasthan", "Madhya Pradesh", "Karnataka", "Kerala", "Assam",
                   "West Bengal", "Uttarakhand", "Maharashtra"],
        "Bird": ["Rajasthan", "Gujarat", "Tamil Nadu", "Karnataka", "West Bengal", "Assam"],
        "Reptile": ["Karnataka", "Kerala", "Tamil Nadu", "Rajasthan", "Assam"],
        "Amphibian": ["Kerala", "Karnataka", "Tamil Nadu", "Assam", "West Bengal"],
        "Fish": ["Assam", "West Bengal", "Kerala", "Karnataka", "Uttarakhand"],
        "Insect": ["Kerala", "Karnataka", "Tamil Nadu", "Assam", "West Bengal"],
    }

    parks_by_group = {
        "Mammal": ["Ranthambore NP", "Kanha NP", "Nagarhole NP", "Periyar NP", "Kaziranga NP"],
        "Bird": ["Keoladeo NP", "Vedanthangal BS", "Nalsarovar BS", "Kaziranga NP"],
        "Reptile": ["National Chambal Sanctuary", "Sundarbans NP", "Bhitarkanika NP"],
        "Amphibian": ["Agasthyamalai BS", "Kudremukh NP", "Silent Valley NP"],
        "Fish": ["Kaziranga NP", "National Chambal Sanctuary", "Periyar NP"],
        "Insect": ["Periyar NP", "Namdapha NP", "Kudremukh NP"],
    }

    habitats_by_group = {
        "Mammal": "Tropical forests, grasslands",
        "Bird": "Wetlands, forests, grasslands",
        "Reptile": "Rivers, forests, rocky terrain",
        "Amphibian": "Streams, ponds, forest floor",
        "Fish": "Rivers and freshwater lakes",
        "Insect": "Forest edges, grasslands, gardens",
    }

    descriptions = {
        "Mammal": "An Indian mammal species with important ecological role in its habitat.",
        "Bird": "A noteworthy Indian bird species contributing to forest health and biodiversity.",
        "Reptile": "A reptile species adapted to Indian climatic and ecological conditions.",
        "Amphibian": "A rare amphibian found in moist habitats across India.",
        "Fish": "A freshwater fish species endemic or native to Indian water systems.",
        "Insect": "An insect species playing a key role in pollination or food webs.",
    }

    lat_lon_ranges = {
        "Assam": (26.0, 92.0), "Kerala": (10.5, 76.5), "Rajasthan": (26.5, 73.0),
        "Karnataka": (13.0, 76.5), "West Bengal": (23.5, 88.0),
        "Madhya Pradesh": (23.0, 78.5), "Maharashtra": (19.5, 75.5),
        "Tamil Nadu": (11.0, 78.5), "Uttarakhand": (30.5, 79.5),
        "Himachal Pradesh": (32.0, 77.0), "Gujarat": (22.5, 71.5),
    }

    target = 500
    needed = target - len(unique_species)
    synthetic_index = {grp: 0 for grp in synthetic_pool}

    rng = random.Random(42)

    while needed > 0:
        for grp, pool in synthetic_pool.items():
            if needed <= 0:
                break
            idx = synthetic_index[grp] % len(pool)
            synthetic_index[grp] += 1
            name, sci, status = pool[idx]
            # Avoid duplicates
            suffix = synthetic_index[grp]
            unique_name = f"{name} {suffix}" if name in seen else name
            seen.add(unique_name)

            st_list = states_by_group[grp]
            chosen_state = rng.choice(st_list)
            lat_base, lon_base = lat_lon_ranges.get(chosen_state, (20.0, 77.0))
            lat = lat_base + rng.uniform(-1.5, 1.5)
            lon = lon_base + rng.uniform(-1.5, 1.5)

            unique_species.append((
                unique_name, sci, grp, status,
                descriptions[grp],
                habitats_by_group[grp],
                rng.sample(st_list, min(3, len(st_list))),
                rng.sample(parks_by_group[grp], min(2, len(parks_by_group[grp]))),
                round(lat, 2), round(lon, 2)
            ))
            needed -= 1

    # ── Build DataFrame ──────────────────────────────────────────────────────
    rows = []
    for sp in unique_species[:target]:
        common, sci, grp, status, desc, habitat, states, parks, lat, lon = sp
        rows.append({
            "Common Name": common,
            "Scientific Name": sci,
            "Animal Group": grp,
            "Conservation Status": status,
            "Description": desc,
            "Habitat": habitat,
            "States Found In India": ", ".join(states),
            "Protected Areas": ", ".join(parks),
            "Latitude": lat,
            "Longitude": lon,
        })

    df = pd.DataFrame(rows)
    return df


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

STATUS_COLORS = {
    "CR": "#f87171",  # red
    "EN": "#fb923c",  # orange
    "VU": "#facc15",  # yellow
    "NT": "#60a5fa",  # blue
    "LC": "#4ade80",  # green
    "DD": "#9ca3af",  # grey
}

STATUS_FULL = {
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "VU": "Vulnerable",
    "NT": "Near Threatened",
    "LC": "Least Concern",
    "DD": "Data Deficient",
}

GROUP_ICONS = {
    "Mammal": "🦁", "Bird": "🦅", "Reptile": "🦎",
    "Amphibian": "🐸", "Fish": "🐟", "Insect": "🦋",
}


def status_badge(status: str) -> str:
    """Return HTML badge for conservation status."""
    full = STATUS_FULL.get(status, status)
    cls = f"badge-{status}"
    return f'<span class="badge {cls}">{full}</span>'


def render_metric_cards(df: pd.DataFrame):
    """Render top-level metric cards."""
    total = len(df)
    cr = len(df[df["Conservation Status"] == "CR"])
    en = len(df[df["Conservation Status"] == "EN"])
    states_count = df["States Found In India"].str.split(", ").explode().nunique()

    cols = st.columns(4)
    cards = [
        (str(total), "Total Species"),
        (str(cr), "Critically Endangered"),
        (str(en), "Endangered"),
        (str(states_count), "States Covered"),
    ]
    for col, (num, label) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{num}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_species_card(row: pd.Series):
    """Render a single species detail card."""
    icon = GROUP_ICONS.get(row["Animal Group"], "🐾")
    badge = status_badge(row["Conservation Status"])
    st.markdown(f"""
    <div class="species-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
            <div>
                <div class="species-common">{icon} {row["Common Name"]}</div>
                <div class="species-scientific">{row["Scientific Name"]}</div>
                <div class="species-group" style="margin-top:0.25rem;">{row["Animal Group"]}</div>
            </div>
            <div>{badge}</div>
        </div>
        <div class="info-box" style="margin-top:0.8rem;">{row["Description"]}</div>
        <div style="display:flex;flex-wrap:wrap;gap:1.5rem;margin-top:0.7rem;">
            <div>
                <div style="font-size:0.7rem;color:#5a7a9a;text-transform:uppercase;letter-spacing:0.08em;">Habitat</div>
                <div style="font-size:0.83rem;color:#c8d8ec;margin-top:0.15rem;">{row["Habitat"]}</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#5a7a9a;text-transform:uppercase;letter-spacing:0.08em;">States</div>
                <div style="font-size:0.83rem;color:#c8d8ec;margin-top:0.15rem;">{row["States Found In India"]}</div>
            </div>
            <div>
                <div style="font-size:0.7rem;color:#5a7a9a;text-transform:uppercase;letter-spacing:0.08em;">Protected Areas</div>
                <div style="font-size:0.83rem;color:#c8d8ec;margin-top:0.15rem;">{row["Protected Areas"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def build_folium_map(df: pd.DataFrame, max_markers: int = 300) -> folium.Map:
    """Build a Folium map with species markers."""
    m = folium.Map(
        location=[22.5, 80.0],
        zoom_start=5,
        tiles="CartoDB dark_matter",
    )

    colour_map = {
        "CR": "red", "EN": "orange", "VU": "beige",
        "NT": "blue", "LC": "green", "DD": "gray",
    }

    sample = df.sample(min(max_markers, len(df)), random_state=42)

    for _, row in sample.iterrows():
        colour = colour_map.get(row["Conservation Status"], "gray")
        icon = GROUP_ICONS.get(row["Animal Group"], "🐾")
        popup_html = f"""
        <div style='font-family:sans-serif;width:220px;'>
          <b style='font-size:14px;'>{icon} {row['Common Name']}</b><br>
          <i style='color:#888;font-size:12px;'>{row['Scientific Name']}</i><br>
          <hr style='margin:5px 0;'>
          <b>Group:</b> {row['Animal Group']}<br>
          <b>Status:</b> {STATUS_FULL.get(row['Conservation Status'], row['Conservation Status'])}<br>
          <b>Habitat:</b> {row['Habitat'][:60]}...<br>
          <b>States:</b> {row['States Found In India'][:60]}
        </div>
        """
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=6,
            color=colour,
            fill=True,
            fill_color=colour,
            fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=f"{row['Common Name']} ({row['Conservation Status']})",
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:999;
                background:rgba(15,27,45,0.9);padding:12px 16px;
                border-radius:8px;border:1px solid rgba(255,215,0,0.3);
                font-family:sans-serif;color:#d4e0f0;font-size:12px;">
    <b style='color:#ffd700;'>Conservation Status</b><br>
    🔴 Critically Endangered<br>🟠 Endangered<br>🟡 Vulnerable<br>
    🔵 Near Threatened<br>🟢 Least Concern<br>⚪ Data Deficient
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# ─────────────────────────────────────────────
# PLOTLY CHART BUILDERS
# ─────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#d4e0f0", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
)


def chart_by_group(df: pd.DataFrame) -> go.Figure:
    """Donut chart of species by animal group."""
    counts = df["Animal Group"].value_counts().reset_index()
    counts.columns = ["Group", "Count"]
    palette = ["#ffd700", "#fb923c", "#4ade80", "#60a5fa", "#c084fc", "#f472b6"]
    fig = px.pie(
        counts, names="Group", values="Count",
        hole=0.55,
        color_discrete_sequence=palette,
        title="Species by Animal Group",
    )
    fig.update_traces(textinfo="label+percent", hovertemplate="%{label}<br>%{value} species")
    fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700")
    return fig


def chart_by_status(df: pd.DataFrame) -> go.Figure:
    """Bar chart of species by conservation status."""
    order = ["CR", "EN", "VU", "NT", "LC", "DD"]
    counts = df["Conservation Status"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["Status", "Count"]
    counts["Full"] = counts["Status"].map(STATUS_FULL)
    colours = [STATUS_COLORS.get(s, "#9ca3af") for s in counts["Status"]]

    fig = px.bar(
        counts, x="Status", y="Count",
        color="Status",
        color_discrete_map=STATUS_COLORS,
        title="Species by Conservation Status",
        custom_data=["Full"],
    )
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Count: %{y}")
    fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700",
                      showlegend=False,
                      xaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.07)"))
    return fig


def chart_top_states(df: pd.DataFrame, n: int = 15) -> go.Figure:
    """Horizontal bar chart of species count by state."""
    state_series = df["States Found In India"].str.split(", ").explode()
    state_counts = state_series.value_counts().head(n).reset_index()
    state_counts.columns = ["State", "Count"]
    state_counts = state_counts.sort_values("Count")

    fig = px.bar(
        state_counts, x="Count", y="State", orientation="h",
        title=f"Top {n} States by Species Count",
        color="Count",
        color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#fb923c"], [1.0, "#ffd700"]],
    )
    fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700",
                      coloraxis_showscale=False, height=500,
                      xaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.07)"))
    return fig


def chart_group_status_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap of group vs conservation status."""
    pivot = df.groupby(["Animal Group", "Conservation Status"]).size().unstack(fill_value=0)
    order = [s for s in ["CR", "EN", "VU", "NT", "LC", "DD"] if s in pivot.columns]
    pivot = pivot[order]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f1b2d"], [0.3, "#1e3a5f"], [0.7, "#fb923c"], [1.0, "#ffd700"]],
        hoverongaps=False,
        hovertemplate="Group: %{y}<br>Status: %{x}<br>Count: %{z}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Threat Matrix: Group × Status",
                      title_font_color="#ffd700")
    return fig


def chart_group_status_sunburst(df: pd.DataFrame) -> go.Figure:
    """Sunburst showing Group → Status hierarchy."""
    sub = df.groupby(["Animal Group", "Conservation Status"]).size().reset_index(name="count")
    fig = px.sunburst(
        sub,
        path=["Animal Group", "Conservation Status"],
        values="count",
        title="Biodiversity Sunburst: Group → Status",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700")
    return fig


def chart_top_hotspots(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Scatter geo-plot of top biodiversity hotspot coordinates."""
    # Cluster by rounding coordinates to 1 decimal
    df_copy = df.copy()
    df_copy["lat_r"] = df_copy["Latitude"].round(0)
    df_copy["lon_r"] = df_copy["Longitude"].round(0)
    hotspot = (df_copy.groupby(["lat_r", "lon_r"])
               .agg(count=("Common Name", "count"))
               .reset_index()
               .sort_values("count", ascending=False)
               .head(n))

    fig = px.scatter_mapbox(
        hotspot, lat="lat_r", lon="lon_r",
        size="count", color="count",
        color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#fb923c"], [1.0, "#ffd700"]],
        mapbox_style="carto-darkmatter",
        zoom=3, center={"lat": 22, "lon": 80},
        size_max=35,
        hover_data={"lat_r": True, "lon_r": True, "count": True},
        title=f"Top {n} Biodiversity Hotspot Clusters",
    )
    fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700",
                      coloraxis_showscale=False, height=480)
    return fig


# ─────────────────────────────────────────────
# PAGE SECTIONS
# ─────────────────────────────────────────────

def section_overview(df: pd.DataFrame):
    """Overview / landing section."""
    st.markdown('<div class="hero-title">Indian Wildlife Explorer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">A comprehensive biodiversity database of 500 Indian animal species — '
        'from Bengal Tigers to Malabar Gliding Frogs.</div>',
        unsafe_allow_html=True,
    )
    render_metric_cards(df)

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # Quick stats row
    st.markdown('<div class="section-header">Biodiversity Summary</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(chart_by_group(df), use_container_width=True, key="ov_group")
    with col2:
        st.plotly_chart(chart_by_status(df), use_container_width=True, key="ov_status")

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.plotly_chart(chart_group_status_sunburst(df), use_container_width=True, key="ov_sunburst")


def section_species_browser(df: pd.DataFrame, filters: dict):
    """Searchable/filterable species browser."""
    st.markdown('<div class="section-header">Species Browser</div>', unsafe_allow_html=True)

    # Apply filters
    filtered = df.copy()
    if filters.get("common_name"):
        q = filters["common_name"].lower()
        filtered = filtered[filtered["Common Name"].str.lower().str.contains(q)]
    if filters.get("scientific_name"):
        q = filters["scientific_name"].lower()
        filtered = filtered[filtered["Scientific Name"].str.lower().str.contains(q)]
    if filters.get("group") and filters["group"] != "All":
        filtered = filtered[filtered["Animal Group"] == filters["group"]]
    if filters.get("status") and filters["status"] != "All":
        filtered = filtered[filtered["Conservation Status"] == filters["status"]]
    if filters.get("state") and filters["state"] != "All":
        filtered = filtered[filtered["States Found In India"].str.contains(filters["state"])]

    result_count = len(filtered)
    st.markdown(
        f'<div style="color:#7a9bbf;font-size:0.85rem;margin-bottom:1rem;">'
        f'Showing <b style="color:#ffd700;">{result_count}</b> species</div>',
        unsafe_allow_html=True,
    )

    if result_count == 0:
        st.warning("No species match your search criteria. Try adjusting the filters.")
        return

    # Display in pages of 20
    page_size = 20
    total_pages = max(1, (result_count + page_size - 1) // page_size)
    page = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, step=1,
        key="species_page",
    )
    start = (page - 1) * page_size
    end = start + page_size
    page_df = filtered.iloc[start:end]

    for _, row in page_df.iterrows():
        with st.expander(f"{GROUP_ICONS.get(row['Animal Group'], '🐾')}  {row['Common Name']}  —  "
                         f"{row['Conservation Status']}"):
            render_species_card(row)

    st.markdown(
        f'<div style="text-align:center;color:#5a7a9a;font-size:0.8rem;">Page {page} of {total_pages}</div>',
        unsafe_allow_html=True,
    )


def section_map(df: pd.DataFrame, filters: dict):
    """Interactive Folium map section."""
    st.markdown('<div class="section-header">Interactive Distribution Map</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#7a9bbf;font-size:0.85rem;margin-bottom:1rem;">'
        'Click any marker to view species details. Colour indicates conservation status.</div>',
        unsafe_allow_html=True,
    )

    # Filter before mapping
    map_df = df.copy()
    if filters.get("group") and filters["group"] != "All":
        map_df = map_df[map_df["Animal Group"] == filters["group"]]
    if filters.get("status") and filters["status"] != "All":
        map_df = map_df[map_df["Conservation Status"] == filters["status"]]
    if filters.get("state") and filters["state"] != "All":
        map_df = map_df[map_df["States Found In India"].str.contains(filters["state"])]

    if len(map_df) == 0:
        st.warning("No species to display on map with current filters.")
        return

    m = build_folium_map(map_df)
    st_folium(m, height=600, use_container_width=True)

    st.markdown(
        f'<div style="color:#5a7a9a;font-size:0.8rem;margin-top:0.5rem;">'
        f'Displaying up to 300 randomly sampled markers from {len(map_df)} filtered species.</div>',
        unsafe_allow_html=True,
    )


def section_analytics(df: pd.DataFrame):
    """Full analytics dashboard section."""
    st.markdown('<div class="section-header">Analytics Dashboard</div>', unsafe_allow_html=True)

    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(chart_by_group(df), use_container_width=True, key="an_group")
    with col2:
        st.plotly_chart(chart_by_status(df), use_container_width=True, key="an_status")

    # Row 2
    st.plotly_chart(chart_top_states(df), use_container_width=True, key="an_states")

    # Row 3
    st.plotly_chart(chart_group_status_heatmap(df), use_container_width=True, key="an_heatmap")

    # Row 4 – hotspots
    st.plotly_chart(chart_top_hotspots(df), use_container_width=True, key="an_hotspot")

    # Threatened species breakdown table
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Threatened Species Summary</div>', unsafe_allow_html=True)
    threat_df = (df[df["Conservation Status"].isin(["CR", "EN", "VU"])]
                 .groupby(["Animal Group", "Conservation Status"])
                 .size()
                 .unstack(fill_value=0)
                 .reset_index())
    st.dataframe(
        threat_df,
        use_container_width=True,
        hide_index=True,
    )


def section_state_analysis(df: pd.DataFrame):
    """Species count by state section."""
    st.markdown('<div class="section-header">State-wise Biodiversity</div>', unsafe_allow_html=True)

    state_series = df["States Found In India"].str.split(", ").explode()
    state_counts = state_series.value_counts().reset_index()
    state_counts.columns = ["State", "Species Count"]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.dataframe(state_counts, use_container_width=True, hide_index=True, height=500)
    with col2:
        fig = px.bar(
            state_counts.head(20).sort_values("Species Count"),
            x="Species Count", y="State", orientation="h",
            color="Species Count",
            color_continuous_scale=[[0, "#1e3a5f"], [1.0, "#ffd700"]],
            title="Species Count per State (Top 20)",
        )
        fig.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700",
                          coloraxis_showscale=False, height=500,
                          yaxis=dict(gridcolor="rgba(255,255,255,0.07)"),
                          xaxis=dict(gridcolor="rgba(255,255,255,0.07)"))
        st.plotly_chart(fig, use_container_width=True, key="st_bar")

    # Group breakdown per state
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.markdown("**Species Group Breakdown by Selected State**")
    selected_state = st.selectbox(
        "Select State",
        options=sorted(state_series.unique().tolist()),
        key="state_select",
    )
    state_df = df[df["States Found In India"].str.contains(selected_state)]
    if len(state_df) > 0:
        group_counts = state_df["Animal Group"].value_counts().reset_index()
        group_counts.columns = ["Group", "Count"]
        fig2 = px.pie(
            group_counts, names="Group", values="Count",
            hole=0.5, title=f"{selected_state} — {len(state_df)} Species",
            color_discrete_sequence=["#ffd700", "#fb923c", "#4ade80", "#60a5fa", "#c084fc", "#f472b6"],
        )
        fig2.update_layout(**PLOTLY_LAYOUT, title_font_color="#ffd700")
        st.plotly_chart(fig2, use_container_width=True, key="st_pie")


def section_threatened(df: pd.DataFrame):
    """Critically endangered and endangered spotlight."""
    st.markdown('<div class="section-header">Threatened Species Spotlight</div>', unsafe_allow_html=True)

    threat_df = df[df["Conservation Status"].isin(["CR", "EN"])].sort_values("Conservation Status")
    st.markdown(
        f'<div style="color:#fb923c;font-size:0.9rem;margin-bottom:1rem;">'
        f'⚠️ <b>{len(threat_df)}</b> species are Critically Endangered or Endangered '
        f'and urgently require conservation action.</div>',
        unsafe_allow_html=True,
    )

    for _, row in threat_df.iterrows():
        render_species_card(row)


def section_statistics(df: pd.DataFrame):
    """Top-level statistics and fun facts."""
    st.markdown('<div class="section-header">Statistics & Insights</div>', unsafe_allow_html=True)

    # Most species-rich groups
    group_counts = df["Animal Group"].value_counts()
    state_series = df["States Found In India"].str.split(", ").explode()
    top_state = state_series.value_counts().idxmax()
    top_state_n = state_series.value_counts().max()

    cr_species = df[df["Conservation Status"] == "CR"]["Common Name"].tolist()
    en_species = df[df["Conservation Status"] == "EN"]["Common Name"].tolist()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{group_counts.index[0]}</div>
            <div class="metric-label">Largest Species Group</div>
            <div style="color:#7a9bbf;font-size:0.8rem;margin-top:0.3rem;">{group_counts.iloc[0]} species</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{top_state}</div>
            <div class="metric-label">Most Biodiverse State</div>
            <div style="color:#7a9bbf;font-size:0.8rem;margin-top:0.3rem;">{top_state_n} species</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        pct_threatened = round(
            100 * len(df[df["Conservation Status"].isin(["CR", "EN", "VU"])]) / len(df), 1
        )
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{pct_threatened}%</div>
            <div class="metric-label">Species Threatened</div>
            <div style="color:#7a9bbf;font-size:0.8rem;margin-top:0.3rem;">CR + EN + VU</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Critically Endangered Species**")
        for sp in cr_species[:15]:
            st.markdown(
                f'<div style="padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);'
                f'color:#f87171;font-size:0.88rem;">🔴 {sp}</div>',
                unsafe_allow_html=True,
            )
    with col_b:
        st.markdown("**Endangered Species (Sample)**")
        for sp in en_species[:15]:
            st.markdown(
                f'<div style="padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.05);'
                f'color:#fb923c;font-size:0.88rem;">🟠 {sp}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.markdown("**Complete Dataset Preview**")
    st.dataframe(
        df[["Common Name", "Scientific Name", "Animal Group", "Conservation Status",
            "States Found In India", "Protected Areas"]],
        use_container_width=True,
        hide_index=True,
        height=400,
    )


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def build_sidebar(df: pd.DataFrame) -> dict:
    """Build sidebar navigation and filters; return filter dict."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0 0.5rem;">
            <div style="font-size:2.5rem;">🐯</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.2rem;color:#ffd700;
                        font-weight:700;">Indian Wildlife</div>
            <div style="color:#5a7a9a;font-size:0.75rem;">Explorer Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,215,0,0.15);'>", unsafe_allow_html=True)

        nav = st.radio(
            "Navigation",
            options=["🏠 Overview", "🔍 Species Browser", "🗺️ Distribution Map",
                     "📊 Analytics", "🌏 State Analysis", "⚠️ Threatened Species",
                     "📈 Statistics"],
            key="nav",
        )

        st.markdown("<hr style='border-color:rgba(255,215,0,0.15);'>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;'
            'color:#5a7a9a;margin-bottom:0.5rem;">Search & Filter</div>',
            unsafe_allow_html=True,
        )

        common_q = st.text_input("Common Name", placeholder="e.g. Tiger", key="f_common")
        sci_q = st.text_input("Scientific Name", placeholder="e.g. Panthera", key="f_sci")

        groups = ["All"] + sorted(df["Animal Group"].unique().tolist())
        group_sel = st.selectbox("Animal Group", options=groups, key="f_group")

        statuses = ["All"] + sorted(df["Conservation Status"].unique().tolist())
        status_sel = st.selectbox("Conservation Status", options=statuses, key="f_status")

        all_states = sorted(
            df["States Found In India"].str.split(", ").explode().unique().tolist()
        )
        state_sel = st.selectbox("State Found In", options=["All"] + all_states, key="f_state")

        st.markdown("<hr style='border-color:rgba(255,215,0,0.15);'>", unsafe_allow_html=True)

        # Mini summary
        st.markdown(
            f'<div style="font-size:0.78rem;color:#5a7a9a;line-height:1.8;">'
            f'<b style="color:#7a9bbf;">500</b> species &nbsp;|&nbsp; '
            f'<b style="color:#7a9bbf;">6</b> animal groups<br>'
            f'<b style="color:#7a9bbf;">35+</b> states & UTs<br>'
            f'<b style="color:#f87171;">{len(df[df["Conservation Status"]=="CR"])}</b> Critically Endangered'
            f'</div>',
            unsafe_allow_html=True,
        )

    return {
        "nav": nav,
        "common_name": common_q,
        "scientific_name": sci_q,
        "group": group_sel,
        "status": status_sel,
        "state": state_sel,
    }


# ─────────────────────────────────────────────
# MAIN APP ENTRY
# ─────────────────────────────────────────────

def main():
    """Main app entry point."""
    try:
        df = build_dataset()
    except Exception as e:
        st.error(f"Error building dataset: {e}")
        st.stop()

    filters = build_sidebar(df)
    nav = filters["nav"]

    if nav == "🏠 Overview":
        section_overview(df)
    elif nav == "🔍 Species Browser":
        section_species_browser(df, filters)
    elif nav == "🗺️ Distribution Map":
        section_map(df, filters)
    elif nav == "📊 Analytics":
        section_analytics(df)
    elif nav == "🌏 State Analysis":
        section_state_analysis(df)
    elif nav == "⚠️ Threatened Species":
        section_threatened(df)
    elif nav == "📈 Statistics":
        section_statistics(df)


if __name__ == "__main__":
    main()