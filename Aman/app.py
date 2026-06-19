"""
=====================================================================================
 GLOBAL SPECIES DISEASE EXPLORER
 Comprehensive Disease Surveillance and Biodiversity Health Analytics Platform
=====================================================================================
A single-file Streamlit application providing a synthetic, programmatically
generated dataset spanning 300+ species (mammals, birds, reptiles, amphibians,
fish, insects) and 1000+ species-disease association records, with analytics,
geographic visualization, machine-learning risk prediction, and report export.

IMPORTANT: All species/disease data in this application is synthetically
generated for academic and demonstration purposes (e.g. B.Sc. coursework,
zoology/biodiversity project work). Scientific names are real where well
established; disease-species associations, severities, mortality rates and
geographic coordinates are illustrative simulations, NOT a verified
veterinary, epidemiological, or taxonomic reference. See "About Project".

Run with:  streamlit run app.py
=====================================================================================
"""

import io
import json
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.units import cm

# =====================================================================================
# PAGE CONFIGURATION (must be the first Streamlit call)
# =====================================================================================
st.set_page_config(
    page_title="Global Species Disease Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

random.seed(42)
np.random.seed(42)

# =====================================================================================
# THEME: DARK BLUE + GOLD SCIENTIFIC GLASSMORPHISM THEME
# =====================================================================================
def inject_css():
    """Injects the global dark-blue/gold glassmorphism theme."""
    st.markdown(
        """
        <style>
        :root{
            --bg-deep:#060b16;
            --bg-mid:#0b1c33;
            --bg-panel:#0f2747;
            --gold:#d4af37;
            --gold-soft:#f1d77c;
            --text-main:#eaf1ff;
            --text-dim:#9fb3d1;
            --accent-green:#3ddc97;
            --accent-red:#ff5d6c;
            --accent-blue:#4ea1ff;
            --glass-bg: rgba(20, 41, 74, 0.55);
            --glass-border: rgba(212, 175, 55, 0.35);
        }
        html, body, [class*="css"]{
            font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
        }
        .stApp{
            background: radial-gradient(circle at 15% 0%, #112a4d 0%, #060b16 45%, #03060c 100%);
            color: var(--text-main);
        }
        section[data-testid="stSidebar"]{
            background: linear-gradient(180deg, #07111f 0%, #0b1c33 100%);
            border-right: 1px solid var(--glass-border);
        }
        section[data-testid="stSidebar"] * { color: var(--text-main) !important; }

        h1, h2, h3{ color: var(--gold-soft) !important; letter-spacing: 0.3px; }
        h4, h5, h6{ color: var(--text-main) !important; }
        p, span, label, li { color: var(--text-main); }
        .stCaption, .st-emotion-cache-1629p8f, small { color: var(--text-dim) !important; }

        /* Glass card */
        .glass-card{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 18px 20px;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: 0 4px 24px rgba(0,0,0,0.35);
            transition: transform 0.18s ease, box-shadow 0.18s ease, border 0.18s ease;
            margin-bottom: 14px;
        }
        .glass-card:hover{
            transform: translateY(-4px);
            box-shadow: 0 10px 28px rgba(212,175,55,0.18);
            border: 1px solid var(--gold);
        }
        .kpi-label{ font-size: 0.78rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1px; }
        .kpi-value{ font-size: 2.0rem; font-weight: 700; color: var(--gold-soft); margin: 2px 0 0 0; }
        .kpi-icon{ font-size: 1.6rem; }
        .kpi-sub{ font-size: 0.75rem; color: var(--text-dim); }

        .hero-title{
            font-size: 2.5rem; font-weight: 800;
            background: linear-gradient(90deg, var(--gold-soft), #ffffff 60%, var(--gold));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .hero-sub{ color: var(--text-dim); font-size: 1.05rem; margin-top: -6px;}

        .badge{
            display:inline-block; padding: 3px 10px; border-radius: 999px;
            font-size: 0.72rem; font-weight: 600; margin-right:6px; margin-bottom:4px;
        }
        .badge-low{ background: rgba(61,220,151,0.18); color: var(--accent-green); border:1px solid var(--accent-green);}
        .badge-moderate{ background: rgba(78,161,255,0.18); color: var(--accent-blue); border:1px solid var(--accent-blue);}
        .badge-high{ background: rgba(255,180,60,0.18); color: #ffb43c; border:1px solid #ffb43c;}
        .badge-critical{ background: rgba(255,93,108,0.18); color: var(--accent-red); border:1px solid var(--accent-red);}

        .severity-track{ width:100%; background: rgba(255,255,255,0.08); border-radius: 8px; height: 10px; overflow:hidden;}
        .severity-fill{ height: 100%; border-radius: 8px; }

        div[data-testid="stMetric"]{
            background: var(--glass-bg); border: 1px solid var(--glass-border);
            border-radius: 14px; padding: 10px 14px;
        }
        .stButton>button, .stDownloadButton>button{
            background: linear-gradient(90deg, var(--gold), var(--gold-soft));
            color: #0b1c33; font-weight: 700; border: none; border-radius: 10px;
        }
        .stButton>button:hover, .stDownloadButton>button:hover{
            box-shadow: 0 0 14px rgba(212,175,55,0.55);
        }
        .stTabs [data-baseweb="tab-list"] { gap: 6px; }
        .stTabs [data-baseweb="tab"]{
            background: var(--glass-bg); border-radius: 10px 10px 0 0; padding: 8px 16px;
            border: 1px solid var(--glass-border);
        }
        hr{ border-color: var(--glass-border) !important; }
        .footer-note{ color: var(--text-dim); font-size: 0.78rem; text-align:center; margin-top: 30px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(col, icon, label, value, sub=""):
    with col:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def severity_badge(severity):
    cls = {"Low": "badge-low", "Moderate": "badge-moderate",
           "High": "badge-high", "Critical": "badge-critical"}.get(severity, "badge-moderate")
    return f'<span class="badge {cls}">{severity}</span>'


def severity_meter(score, max_score=100):
    pct = max(2, min(100, (score / max_score) * 100))
    if pct < 35:
        color = "#3ddc97"
    elif pct < 60:
        color = "#4ea1ff"
    elif pct < 80:
        color = "#ffb43c"
    else:
        color = "#ff5d6c"
    return f"""
    <div class="severity-track"><div class="severity-fill" style="width:{pct}%; background:{color};"></div></div>
    """

# =====================================================================================
# CORE DATA ENGINE
# =====================================================================================
# 1. SPECIES NAME POOLS (curated, real animals, grouped by taxon)
# =====================================================================

MAMMALS = [
    "Bengal Tiger", "Siberian Tiger", "Sumatran Tiger", "Malayan Tiger",
    "African Lion", "Asiatic Lion", "Leopard", "Snow Leopard", "Clouded Leopard",
    "Jaguar", "Cheetah", "African Bush Elephant", "African Forest Elephant",
    "Asian Elephant", "White Rhinoceros", "Black Rhinoceros", "Indian Rhinoceros",
    "Javan Rhinoceros", "Sumatran Rhinoceros", "Sambar Deer", "Spotted Deer (Chital)",
    "Barking Deer", "Musk Deer", "Red Deer", "Sloth Bear", "Himalayan Black Bear",
    "Brown Bear", "Sun Bear", "Polar Bear", "Indian Wolf", "Grey Wolf",
    "Red Fox", "Arctic Fox", "Bengal Fox", "Fennec Fox", "Rhesus Macaque",
    "Hanuman Langur", "Capuchin Monkey", "Spider Monkey", "Howler Monkey",
    "Giant Panda", "Red Panda", "Fruit Bat", "Vampire Bat", "Horseshoe Bat",
    "Domestic Dog", "Domestic Cat", "Domestic Cow", "Water Buffalo", "Goat",
    "Sheep", "Dromedary Camel", "Bactrian Camel", "Horse", "Donkey", "Mule",
    "Domestic Pig", "Hippopotamus", "Giraffe", "Plains Zebra", "Gorilla",
    "Chimpanzee", "Bonobo", "Orangutan", "Gibbon", "Striped Hyena",
    "Spotted Hyena", "Golden Jackal", "River Otter", "Sea Otter", "Mongoose",
    "Civet Cat", "Pangolin", "Indian Porcupine", "Hedgehog", "Indian Giant Squirrel",
    "House Rat", "House Mouse", "European Rabbit", "Indian Hare", "Red Kangaroo",
    "Koala", "Common Wombat", "Tasmanian Devil", "Three-toed Sloth", "Giant Armadillo",
    "Giant Anteater", "Walrus", "Harbor Seal", "Sea Lion", "Bottlenose Dolphin",
    "Blue Whale", "Humpback Whale", "Narwhal", "Orca", "Moose", "Elk",
    "American Bison", "Yak", "Reindeer", "Blackbuck Antelope", "Thomson's Gazelle",
    "Wildebeest", "Common Warthog", "Wild Boar", "Eurasian Lynx", "Bobcat",
    "Puma (Cougar)", "Wolverine", "Eurasian Badger", "Striped Skunk", "Least Weasel",
    "Domestic Ferret", "American Mink", "Eurasian Beaver", "Capybara", "Llama",
    "Alpaca", "Malayan Tapir", "Okapi",
]

BIRDS = [
    "Bald Eagle", "Golden Eagle", "Indian Eagle", "Barn Owl", "Eagle Owl",
    "Indian Peafowl (Peacock)", "House Sparrow", "House Crow", "Rock Pigeon",
    "Mallard Duck", "Mute Swan", "Greater Flamingo", "Emperor Penguin",
    "King Penguin", "Egyptian Vulture", "Griffon Vulture", "Sarus Crane",
    "Whooping Crane", "Painted Stork", "Marabou Stork", "Great Hornbill",
    "African Grey Parrot", "Scarlet Macaw", "Sulphur-crested Cockatoo",
    "Red-tailed Hawk", "Peregrine Falcon", "Black Kite", "Grey Heron",
    "Great Egret", "Great White Pelican", "Great Cormorant", "Wandering Albatross",
    "Herring Gull", "Common Tern", "Common Kingfisher", "Great Spotted Woodpecker",
    "Ruby-throated Hummingbird", "European Robin", "Eastern Bluebird",
    "Northern Cardinal", "Zebra Finch", "Domestic Canary", "Common Ostrich",
    "Emu", "Southern Cassowary", "Brown Kiwi", "Wild Turkey", "Domestic Chicken",
    "Greylag Goose", "Common Quail", "Common Pheasant", "Grey Partridge",
    "Eurasian Magpie", "Blue Jay", "Common Raven", "Toco Toucan",
    "Laughing Kookaburra", "Snowy Owl", "Andean Condor", "Secretarybird",
    "Greater Roadrunner", "Resplendent Quetzal", "Indian Roller",
    "Common Myna", "Bar-headed Goose",
]

REPTILES = [
    "King Cobra", "Indian Cobra", "Reticulated Python", "Ball Python",
    "Saltwater Crocodile", "Nile Crocodile", "American Alligator",
    "Chinese Alligator", "Green Sea Turtle", "Common Box Turtle",
    "Aldabra Giant Tortoise", "Tokay Gecko", "Leopard Gecko", "Veiled Chameleon",
    "Panther Chameleon", "Komodo Dragon", "Bengal Monitor Lizard",
    "Green Iguana", "Green Anaconda", "Russell's Viper", "Eastern Diamondback Rattlesnake",
    "Boa Constrictor", "Common Garter Snake", "Blue-tongued Skink", "Gila Monster",
    "Tuatara", "Spectacled Caiman", "Common Snapping Turtle",
    "Galapagos Tortoise", "Western Diamondback Rattlesnake", "Frilled Lizard",
    "Thorny Devil", "Eastern Box Turtle",
]

AMPHIBIANS = [
    "Poison Dart Frog", "American Bullfrog", "Red-eyed Tree Frog",
    "Fire Salamander", "Tiger Salamander", "Cane Toad", "Common Toad",
    "Smooth Newt", "Axolotl", "Caecilian", "Goliath Frog", "Glass Frog",
    "Indian Bullfrog", "Marsh Frog", "Spotted Salamander", "Mudpuppy",
    "Hellbender", "Natterjack Toad", "Wood Frog", "African Clawed Frog",
    "Surinam Toad", "Japanese Giant Salamander", "Olm", "Pacman Frog",
    "Cuban Tree Frog",
]

FISH = [
    "Great White Shark", "Hammerhead Shark", "Tiger Shark", "Atlantic Bluefin Tuna",
    "Yellowfin Tuna", "Atlantic Salmon", "Pacific Salmon", "Golden Mahseer",
    "Walking Catfish", "Stingray", "Goldfish", "Koi Carp", "Common Carp",
    "Rainbow Trout", "Atlantic Cod", "Atlantic Halibut", "Swordfish",
    "Blue Marlin", "Great Barracuda", "Red-bellied Piranha", "European Eel",
    "Pufferfish", "Clownfish", "Angelfish", "Betta Fish", "Guppy", "Tilapia",
    "Atlantic Mackerel", "Sardine", "Anchovy", "Atlantic Herring", "Red Snapper",
    "Grouper", "Seahorse", "Manta Ray", "Lionfish",
    "Whale Shark", "Electric Eel", "Arapaima", "Flying Fish", "Sturgeon",
    "Catla", "Rohu",
]

INSECTS = [
    "Monarch Butterfly", "Swallowtail Butterfly", "Western Honeybee", "Bumblebee",
    "Common Darter Dragonfly", "Seven-spot Ladybird Beetle", "Dung Beetle",
    "Stag Beetle", "Carpenter Ant", "Fire Ant", "Asian Tiger Mosquito",
    "Subterranean Termite", "Desert Locust", "Field Cricket", "American Cockroach",
    "Luna Moth", "Paper Wasp", "European Hornet", "Praying Mantis",
    "Indian Stick Insect", "Domestic Silkworm", "Cat Flea", "Deer Tick",
    "Atlas Moth", "Rhinoceros Beetle", "Giant Weta", "Leafcutter Ant",
    "Assassin Bug",
]

SPECIES_GROUPS = {
    "Mammals": MAMMALS,
    "Birds": BIRDS,
    "Reptiles": REPTILES,
    "Amphibians": AMPHIBIANS,
    "Fish": FISH,
    "Insects": INSECTS,
}


# =====================================================================
# 2. SCIENTIFIC NAMES (real, for well-known species; templated fallback)
# =====================================================================
SCI_NAMES = {
    "Bengal Tiger": "Panthera tigris tigris", "Siberian Tiger": "Panthera tigris altaica",
    "Sumatran Tiger": "Panthera tigris sumatrae", "Malayan Tiger": "Panthera tigris jacksoni",
    "African Lion": "Panthera leo", "Asiatic Lion": "Panthera leo persica",
    "Leopard": "Panthera pardus", "Snow Leopard": "Panthera uncia",
    "Clouded Leopard": "Neofelis nebulosa", "Jaguar": "Panthera onca",
    "Cheetah": "Acinonyx jubatus", "African Bush Elephant": "Loxodonta africana",
    "African Forest Elephant": "Loxodonta cyclotis", "Asian Elephant": "Elephas maximus",
    "White Rhinoceros": "Ceratotherium simum", "Black Rhinoceros": "Diceros bicornis",
    "Indian Rhinoceros": "Rhinoceros unicornis", "Javan Rhinoceros": "Rhinoceros sondaicus",
    "Sumatran Rhinoceros": "Dicerorhinus sumatrensis", "Giant Panda": "Ailuropoda melanoleuca",
    "Red Panda": "Ailurus fulgens", "Domestic Dog": "Canis lupus familiaris",
    "Domestic Cat": "Felis catus", "Domestic Cow": "Bos taurus",
    "Water Buffalo": "Bubalus bubalis", "Goat": "Capra aegagrus hircus",
    "Sheep": "Ovis aries", "Dromedary Camel": "Camelus dromedarius",
    "Bactrian Camel": "Camelus bactrianus", "Horse": "Equus ferus caballus",
    "Domestic Pig": "Sus scrofa domesticus", "Hippopotamus": "Hippopotamus amphibius",
    "Giraffe": "Giraffa camelopardalis", "Plains Zebra": "Equus quagga",
    "Gorilla": "Gorilla gorilla", "Chimpanzee": "Pan troglodytes",
    "Bonobo": "Pan paniscus", "Orangutan": "Pongo pygmaeus",
    "Grey Wolf": "Canis lupus", "Indian Wolf": "Canis lupus pallipes",
    "Red Fox": "Vulpes vulpes", "Arctic Fox": "Vulpes lagopus",
    "Polar Bear": "Ursus maritimus", "Brown Bear": "Ursus arctos",
    "Sloth Bear": "Melursus ursinus", "Sun Bear": "Helarctos malayanus",
    "Rhesus Macaque": "Macaca mulatta", "Hanuman Langur": "Semnopithecus entellus",
    "Blue Whale": "Balaenoptera musculus", "Humpback Whale": "Megaptera novaeangliae",
    "Orca": "Orcinus orca", "Bottlenose Dolphin": "Tursiops truncatus",
    "Bald Eagle": "Haliaeetus leucocephalus", "Golden Eagle": "Aquila chrysaetos",
    "Indian Peafowl (Peacock)": "Pavo cristatus", "House Sparrow": "Passer domesticus",
    "House Crow": "Corvus splendens", "Rock Pigeon": "Columba livia",
    "Mallard Duck": "Anas platyrhynchos", "Mute Swan": "Cygnus olor",
    "Greater Flamingo": "Phoenicopterus roseus", "Emperor Penguin": "Aptenodytes forsteri",
    "King Penguin": "Aptenodytes patagonicus", "Sarus Crane": "Antigone antigone",
    "Whooping Crane": "Grus americana", "Great Hornbill": "Buceros bicornis",
    "African Grey Parrot": "Psittacus erithacus", "Scarlet Macaw": "Ara macao",
    "Peregrine Falcon": "Falco peregrinus", "Common Ostrich": "Struthio camelus",
    "Emu": "Dromaius novaehollandiae", "Domestic Chicken": "Gallus gallus domesticus",
    "King Cobra": "Ophiophagus hannah", "Indian Cobra": "Naja naja",
    "Reticulated Python": "Malayopython reticulatus", "Ball Python": "Python regius",
    "Saltwater Crocodile": "Crocodylus porosus", "Nile Crocodile": "Crocodylus niloticus",
    "American Alligator": "Alligator mississippiensis", "Green Sea Turtle": "Chelonia mydas",
    "Komodo Dragon": "Varanus komodoensis", "Bengal Monitor Lizard": "Varanus bengalensis",
    "Green Iguana": "Iguana iguana", "Green Anaconda": "Eunectes murinus",
    "Tuatara": "Sphenodon punctatus", "Poison Dart Frog": "Dendrobates spp.",
    "American Bullfrog": "Lithobates catesbeianus", "Fire Salamander": "Salamandra salamandra",
    "Axolotl": "Ambystoma mexicanum", "Cane Toad": "Rhinella marina",
    "Great White Shark": "Carcharodon carcharias", "Hammerhead Shark": "Sphyrna mokarran",
    "Whale Shark": "Rhincodon typus", "Atlantic Bluefin Tuna": "Thunnus thynnus",
    "Atlantic Salmon": "Salmo salar", "Golden Mahseer": "Tor putitora",
    "Goldfish": "Carassius auratus", "Koi Carp": "Cyprinus rubrofuscus",
    "Electric Eel": "Electrophorus electricus", "Western Honeybee": "Apis mellifera",
    "Monarch Butterfly": "Danaus plexippus", "Desert Locust": "Schistocerca gregaria",
    "American Cockroach": "Periplaneta americana", "Domestic Silkworm": "Bombyx mori",
}

GENUS_ROOTS = ["Panthero", "Cervo", "Aviceps", "Herpeto", "Ichthyo", "Amphibio",
               "Insecta", "Chelono", "Mammalo", "Ornitho", "Reptilo", "Pisco"]
SPECIES_ROOTS = ["ferus", "sylvaticus", "domesticus", "regalis", "minor", "major",
                 "indicus", "asiaticus", "africanus", "americanus", "orientalis",
                 "tropicalis", "borealis", "australis"]

def get_scientific_name(name, idx):
    if name in SCI_NAMES:
        return SCI_NAMES[name]
    rng = random.Random(idx * 7919 + len(name))
    genus = rng.choice(GENUS_ROOTS)
    species_epithet = rng.choice(SPECIES_ROOTS)
    return f"{genus} {species_epithet}"

# =====================================================================
# 3. DISEASE CATALOG (type, default symptom/treatment/prevention templates)
# =====================================================================
DISEASE_CATALOG = {
    "Rabies": "Viral", "Foot and Mouth Disease": "Viral", "Anthrax": "Bacterial",
    "Tuberculosis": "Bacterial", "Avian Influenza": "Viral", "Bird Flu (H5N1)": "Viral",
    "Newcastle Disease": "Viral", "White Nose Syndrome": "Fungal",
    "Canine Distemper": "Viral", "African Swine Fever": "Viral",
    "Chytridiomycosis": "Fungal", "Snake Fungal Disease": "Fungal",
    "Fibropapillomatosis": "Viral", "Columnaris Disease": "Bacterial",
    "Gill Rot": "Fungal", "Fin Rot": "Bacterial", "Brucellosis": "Bacterial",
    "Leptospirosis": "Bacterial", "Salmonellosis": "Bacterial",
    "Avian Pox": "Viral", "Psittacosis": "Bacterial", "Coccidiosis": "Protozoan",
    "Mange (Sarcoptic)": "Parasitic", "Heartworm Disease": "Parasitic",
    "Ringworm": "Fungal", "Lyme Disease": "Bacterial", "West Nile Virus": "Viral",
    "Bovine Tuberculosis": "Bacterial", "Bluetongue Disease": "Viral",
    "Rinderpest": "Viral", "Classical Swine Fever": "Viral",
    "Inclusion Body Disease": "Viral", "Ophidian Paramyxovirus": "Viral",
    "Cryptosporidiosis": "Protozoan", "Ranavirus Infection": "Viral",
    "Red Leg Syndrome": "Bacterial", "Toad Skin Fungus": "Fungal",
    "Ichthyophthirius (Ich)": "Parasitic", "Vibriosis": "Bacterial",
    "Viral Hemorrhagic Septicemia": "Viral", "Whirling Disease": "Parasitic",
    "Swim Bladder Disorder": "Other", "Anchor Worm Infestation": "Parasitic",
    "Nosema Disease": "Fungal/Microsporidian", "American Foulbrood": "Bacterial",
    "European Foulbrood": "Bacterial", "Varroa Mite Infestation": "Parasitic",
    "Deformed Wing Virus": "Viral", "Colony Collapse Disorder": "Multifactorial",
    "Black Death (Plague, Sylvatic)": "Bacterial", "Q Fever": "Bacterial",
    "Hantavirus Infection": "Viral", "Toxoplasmosis": "Protozoan",
    "Trypanosomiasis": "Protozoan", "Babesiosis": "Protozoan",
    "Ehrlichiosis": "Bacterial", "Feline Leukemia Virus": "Viral",
    "Feline Immunodeficiency Virus": "Viral", "Canine Parvovirus": "Viral",
    "Equine Influenza": "Viral", "Equine Encephalitis": "Viral",
    "Glanders": "Bacterial", "Johne's Disease": "Bacterial",
    "Avian Botulism": "Bacterial", "Duck Viral Enteritis": "Viral",
    "Marek's Disease": "Viral", "Mycoplasmosis (Avian)": "Bacterial",
    "Beak and Feather Disease": "Viral", "Aspergillosis": "Fungal",
    "Sea Turtle Cold Stunning Syndrome": "Other", "Shell Rot": "Bacterial",
    "Metabolic Bone Disease": "Other", "Mouth Rot (Infectious Stomatitis)": "Bacterial",
    "Paramyxovirus (Reptile)": "Viral", "Amphibian Perkinsea Infection": "Protozoan",
    "Saprolegniasis (Egg Fungus)": "Fungal", "Lateral Line Disease": "Other",
    "Dropsy": "Bacterial", "Anchor Worm Disease": "Parasitic",
    "Sea Lice Infestation": "Parasitic", "Tail Rot": "Bacterial",
    "Furunculosis": "Bacterial", "Velvet Disease": "Parasitic",
    "Tracheal Mite Infestation": "Parasitic", "Stonebrood Disease": "Fungal",
    "Chalkbrood Disease": "Fungal", "Sacbrood Virus": "Viral",
    "Black Queen Cell Virus": "Viral", "Acute Bee Paralysis Virus": "Viral",
    "Locust Fungal Epizootic": "Fungal", "Termite Nematode Infection": "Parasitic",
    "Insect Baculovirus Infection": "Viral", "Pebrine Disease": "Protozoan",
    "Flacherie Disease": "Bacterial", "Grasserie Disease": "Viral",
    "Parasitic Infections (General)": "Parasitic", "Fungal Infections (General)": "Fungal",
    "Bacterial Infections (General)": "Bacterial", "Viral Infections (General)": "Viral",
    "Protozoan Diseases (General)": "Protozoan", "Nutritional Deficiency Disorder": "Other",
    "Heavy Metal Toxicity": "Other", "Pesticide Poisoning": "Other",
    "Zoonotic Influenza Strain": "Viral", "Mycobacteriosis": "Bacterial",
}

SYMPTOM_BANK = {
    "Viral": ["fever", "lethargy", "loss of appetite", "respiratory distress",
              "nasal/ocular discharge", "neurological signs", "sudden mortality spikes"],
    "Bacterial": ["fever", "localized lesions", "abscess formation", "diarrhea",
                  "swelling of lymph nodes", "weight loss", "labored breathing"],
    "Fungal": ["skin lesions", "discoloration of tissue", "patchy fur/scale loss",
               "white fuzzy growths", "lethargy", "muzzle/snout damage"],
    "Parasitic": ["weight loss", "visible external parasites", "anemia",
                  "skin irritation", "reduced reproductive success", "poor coat/plumage condition"],
    "Protozoan": ["diarrhea", "dehydration", "weight loss", "lethargy",
                  "anemia", "intermittent fever"],
    "Fungal/Microsporidian": ["dysentery", "reduced lifespan", "disorientation", "weakness"],
    "Multifactorial": ["sudden colony/population decline", "disorientation", "weakened immunity"],
    "Other": ["behavioral changes", "buoyancy/posture issues", "organ dysfunction", "stunted growth"],
}
TREATMENT_BANK = {
    "Viral": ["supportive care and isolation", "antiviral therapy where available",
              "vaccination of unaffected population", "fluid therapy and rest"],
    "Bacterial": ["targeted antibiotic therapy", "wound debridement and care",
                  "isolation and quarantine", "supportive nutritional therapy"],
    "Fungal": ["topical/systemic antifungal treatment", "environmental decontamination",
               "improved habitat humidity/ventilation control"],
    "Parasitic": ["antiparasitic medication", "habitat treatment to break life-cycle",
                  "regular deworming/dipping protocols"],
    "Protozoan": ["antiprotozoal medication", "rehydration therapy", "sanitation improvement"],
    "Fungal/Microsporidian": ["antifungal feed additives", "colony requeening", "hive sanitation"],
    "Multifactorial": ["integrated pest management", "habitat restoration", "stress reduction measures"],
    "Other": ["dietary correction", "environmental remediation", "veterinary monitoring"],
}
PREVENTION_BANK = {
    "Viral": ["routine vaccination programs", "quarantine of new individuals", "vector control"],
    "Bacterial": ["sanitation and biosecurity", "regular health screening", "controlled population density"],
    "Fungal": ["humidity and habitat management", "avoiding contaminated substrates", "biosecurity at facility entry"],
    "Parasitic": ["regular parasite screening", "habitat hygiene", "controlled exposure to vectors"],
    "Protozoan": ["clean water access", "sanitation protocols", "routine fecal screening"],
    "Fungal/Microsporidian": ["hive hygiene", "resistant stock breeding", "regular apiary inspection"],
    "Multifactorial": ["habitat conservation", "reduced chemical exposure", "population monitoring"],
    "Other": ["balanced nutrition", "pollution control", "habitat quality monitoring"],
}
TRANSMISSION_METHODS = [
    "Direct contact", "Airborne/Respiratory droplets", "Vector-borne (insects/ticks)",
    "Waterborne", "Foodborne/Ingestion", "Soil contamination", "Vertical (mother to offspring)",
    "Contact with contaminated surfaces", "Wound contamination", "Predation/scavenging exposure",
]

# =====================================================================
# 4. GEOGRAPHIC REGIONS (for distribution & map plotting)
# =====================================================================
REGIONS = [
    ("South Asia", "India", 22.0, 79.0), ("Southeast Asia", "Indonesia", -2.5, 117.0),
    ("East Africa", "Kenya", 1.0, 38.0), ("Southern Africa", "South Africa", -29.0, 24.0),
    ("North America", "USA", 39.0, -98.0), ("South America", "Brazil", -10.0, -55.0),
    ("Western Europe", "Germany", 51.0, 10.0), ("Northern Europe", "Norway", 61.0, 8.5),
    ("East Asia", "China", 35.0, 103.0), ("Australia/Oceania", "Australia", -25.0, 133.0),
    ("Middle East", "Saudi Arabia", 24.0, 45.0), ("Central Asia", "Kazakhstan", 48.0, 67.0),
    ("Arctic Region", "Canada (Arctic)", 70.0, -100.0), ("Antarctic Region", "Antarctica", -75.0, 0.0),
    ("Amazon Basin", "Brazil (Amazon)", -3.0, -60.0), ("Sub-Saharan Africa", "Tanzania", -6.0, 35.0),
    ("Western North America", "Canada", 55.0, -110.0), ("Indian Subcontinent", "Nepal", 28.0, 84.0),
    ("Mediterranean", "Italy", 42.0, 13.0), ("Pacific Islands", "Fiji", -18.0, 178.0),
]


# =====================================================================
# 5. GROUP -> APPLICABLE DISEASE POOL
# =====================================================================
GENERAL_DISEASES = ["Parasitic Infections (General)", "Fungal Infections (General)",
                     "Bacterial Infections (General)", "Viral Infections (General)",
                     "Protozoan Diseases (General)", "Nutritional Deficiency Disorder",
                     "Heavy Metal Toxicity", "Pesticide Poisoning"]

GROUP_DISEASE_MAP = {
    "Mammals": ["Rabies", "Foot and Mouth Disease", "Anthrax", "Tuberculosis",
                "Canine Distemper", "African Swine Fever", "Brucellosis", "Leptospirosis",
                "Mange (Sarcoptic)", "Heartworm Disease", "Ringworm", "Lyme Disease",
                "Bovine Tuberculosis", "Bluetongue Disease", "Rinderpest",
                "Classical Swine Fever", "Hantavirus Infection", "Toxoplasmosis",
                "Trypanosomiasis", "Babesiosis", "Ehrlichiosis", "Feline Leukemia Virus",
                "Feline Immunodeficiency Virus", "Canine Parvovirus", "Equine Influenza",
                "Equine Encephalitis", "Glanders", "Johne's Disease", "Black Death (Plague, Sylvatic)",
                "Q Fever", "Mycobacteriosis", "Salmonellosis", "West Nile Virus"] + GENERAL_DISEASES,
    "Birds": ["Avian Influenza", "Bird Flu (H5N1)", "Newcastle Disease", "Avian Pox",
              "Psittacosis", "Coccidiosis", "Salmonellosis", "West Nile Virus",
              "Avian Botulism", "Duck Viral Enteritis", "Marek's Disease",
              "Mycoplasmosis (Avian)", "Beak and Feather Disease", "Aspergillosis",
              "Zoonotic Influenza Strain"] + GENERAL_DISEASES,
    "Reptiles": ["Snake Fungal Disease", "Inclusion Body Disease", "Ophidian Paramyxovirus",
                 "Shell Rot", "Metabolic Bone Disease", "Mouth Rot (Infectious Stomatitis)",
                 "Paramyxovirus (Reptile)", "Salmonellosis", "Cryptosporidiosis"] + GENERAL_DISEASES,
    "Amphibians": ["Chytridiomycosis", "Ranavirus Infection", "Red Leg Syndrome",
                   "Toad Skin Fungus", "Amphibian Perkinsea Infection",
                   "Saprolegniasis (Egg Fungus)", "Cryptosporidiosis"] + GENERAL_DISEASES,
    "Fish": ["Columnaris Disease", "Gill Rot", "Fin Rot", "Fibropapillomatosis",
             "Ichthyophthirius (Ich)", "Vibriosis", "Viral Hemorrhagic Septicemia",
             "Whirling Disease", "Swim Bladder Disorder", "Anchor Worm Infestation",
             "Lateral Line Disease", "Dropsy", "Sea Lice Infestation", "Tail Rot",
             "Furunculosis", "Velvet Disease"] + GENERAL_DISEASES,
    "Insects": ["Nosema Disease", "American Foulbrood", "European Foulbrood",
                "Varroa Mite Infestation", "Deformed Wing Virus", "Colony Collapse Disorder",
                "Tracheal Mite Infestation", "Stonebrood Disease", "Chalkbrood Disease",
                "Sacbrood Virus", "Black Queen Cell Virus", "Acute Bee Paralysis Virus",
                "Locust Fungal Epizootic", "Termite Nematode Infection",
                "Insect Baculovirus Infection", "Pebrine Disease", "Flacherie Disease",
                "Grasserie Disease"] + GENERAL_DISEASES,
}

HABITATS = {
    "Mammals": ["Tropical Forest", "Savanna", "Grassland", "Mountain Range", "Desert",
                "Temperate Forest", "Arctic Tundra", "Wetland", "Farmland", "Urban Area"],
    "Birds": ["Wetland", "Coastal Cliffs", "Tropical Forest", "Grassland", "Urban Area",
              "Farmland", "Mountain Range", "Arctic Tundra", "Mangrove"],
    "Reptiles": ["Tropical Forest", "Desert", "Wetland", "Savanna", "Riverbank", "Mangrove"],
    "Amphibians": ["Wetland", "Tropical Forest", "Riverbank", "Pond/Lake", "Temperate Forest"],
    "Fish": ["Open Ocean", "Coral Reef", "Freshwater River", "Lake", "Estuary", "Deep Sea"],
    "Insects": ["Tropical Forest", "Grassland", "Farmland", "Urban Area", "Wetland", "Temperate Forest"],
}

CONSERVATION_STATUSES = ["Least Concern", "Near Threatened", "Vulnerable",
                          "Endangered", "Critically Endangered", "Data Deficient"]
IUCN_CODES = {"Least Concern": "LC", "Near Threatened": "NT", "Vulnerable": "VU",
              "Endangered": "EN", "Critically Endangered": "CR", "Data Deficient": "DD"}
CONSERVATION_WEIGHTS = [0.32, 0.18, 0.18, 0.16, 0.10, 0.06]
POPULATION_TRENDS = ["Increasing", "Decreasing", "Stable", "Unknown"]
SEVERITY_LEVELS = ["Low", "Moderate", "High", "Critical"]
LIFESPAN_RANGES = {"Mammals": (5, 70), "Birds": (3, 60), "Reptiles": (5, 100),
                    "Amphibians": (2, 30), "Fish": (1, 50), "Insects": (0.1, 5)}

RESEARCH_NOTE_TEMPLATES = [
    "Long-term monitoring recommended due to {factor}.",
    "Disease surveillance data suggests correlation with {factor}.",
    "Population resilience appears linked to {factor}.",
    "Further field study warranted regarding {factor}.",
    "Conservation programs should prioritize {factor}.",
]
RESEARCH_FACTORS = ["habitat fragmentation", "climate-driven range shifts", "human-wildlife conflict",
                     "cross-species pathogen spillover", "captive breeding program outcomes",
                     "seasonal migration stress", "water quality degradation", "illegal trade pressure"]


@st.cache_data(show_spinner="Generating species & disease intelligence database...")
def generate_species_database():
    """Builds the species master table and the species-disease association table.
    Returns two pandas DataFrames: (species_df, disease_df)."""
    rng = random.Random(2026)
    species_rows = []
    disease_rows = []
    species_id = 1
    disease_record_id = 1

    for group, names in SPECIES_GROUPS.items():
        applicable_diseases = GROUP_DISEASE_MAP[group]
        lo, hi = LIFESPAN_RANGES[group]
        for name in names:
            sci_name = get_scientific_name(name, species_id)
            status = rng.choices(CONSERVATION_STATUSES, weights=CONSERVATION_WEIGHTS, k=1)[0]
            region_name, country, lat, lon = rng.choice(REGIONS)
            # jitter coordinates so species in the same region don't overlap on the map
            jlat = lat + rng.uniform(-6, 6)
            jlon = lon + rng.uniform(-6, 6)
            lifespan = round(rng.uniform(lo, hi), 1)
            trend = rng.choices(POPULATION_TRENDS, weights=[0.2, 0.35, 0.35, 0.1], k=1)[0]
            habitat = rng.choice(HABITATS[group])

            # assign 3-5 diseases per species
            n_diseases = rng.randint(3, 5)
            assigned = rng.sample(applicable_diseases, min(n_diseases, len(applicable_diseases)))

            disease_risk_scores = []
            mortality_rates = []
            disease_names_list = []

            for disease in assigned:
                dtype = DISEASE_CATALOG[disease]
                severity = rng.choices(SEVERITY_LEVELS, weights=[0.3, 0.35, 0.25, 0.10], k=1)[0]
                transmission = rng.choice(TRANSMISSION_METHODS)
                symptoms = ", ".join(rng.sample(SYMPTOM_BANK[dtype], k=min(3, len(SYMPTOM_BANK[dtype]))))
                treatment = rng.choice(TREATMENT_BANK[dtype])
                prevention = rng.choice(PREVENTION_BANK[dtype])
                severity_score = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}[severity]
                base_mortality = {"Low": (1, 10), "Moderate": (8, 25), "High": (20, 50), "Critical": (40, 85)}[severity]
                mortality_rate = round(rng.uniform(*base_mortality), 1)
                conservation_factor = (CONSERVATION_STATUSES.index(status) + 1) * 5
                risk_score = min(100, round(severity_score * 15 + mortality_rate * 0.4 + conservation_factor + rng.uniform(-5, 5), 1))
                risk_score = max(1, risk_score)

                disease_rows.append({
                    "record_id": disease_record_id,
                    "species_id": species_id,
                    "species_name": name,
                    "species_group": group,
                    "disease_name": disease,
                    "disease_type": dtype,
                    "severity": severity,
                    "transmission_method": transmission,
                    "symptoms": symptoms.capitalize(),
                    "treatment": treatment.capitalize(),
                    "prevention": prevention.capitalize(),
                    "mortality_rate": mortality_rate,
                    "risk_score": risk_score,
                })
                disease_record_id += 1
                disease_risk_scores.append(risk_score)
                mortality_rates.append(mortality_rate)
                disease_names_list.append(disease)

            avg_risk = round(sum(disease_risk_scores) / len(disease_risk_scores), 1)
            avg_mortality = round(sum(mortality_rates) / len(mortality_rates), 1)
            note_template = rng.choice(RESEARCH_NOTE_TEMPLATES)
            research_note = note_template.format(factor=rng.choice(RESEARCH_FACTORS))

            species_rows.append({
                "species_id": species_id,
                "species_name": name,
                "scientific_name": sci_name,
                "species_group": group,
                "avg_lifespan_years": lifespan,
                "conservation_status": status,
                "iucn_code": IUCN_CODES[status],
                "habitat": habitat,
                "region": region_name,
                "country": country,
                "latitude": round(jlat, 4),
                "longitude": round(jlon, 4),
                "population_trend": trend,
                "common_diseases": ", ".join(disease_names_list),
                "disease_count": len(disease_names_list),
                "avg_mortality_rate": avg_mortality,
                "disease_risk_score": avg_risk,
                "research_notes": research_note,
            })
            species_id += 1

    species_df = pd.DataFrame(species_rows)
    disease_df = pd.DataFrame(disease_rows)
    # bring conservation status onto the disease table for cross-analytics
    disease_df = disease_df.merge(
        species_df[["species_id", "conservation_status", "iucn_code", "country", "region",
                     "latitude", "longitude", "habitat", "population_trend"]],
        on="species_id", how="left",
    )
    return species_df, disease_df




# =====================================================================================
# SUPPORTING SYNTHETIC DATA: PROTECTED AREAS, OUTBREAK TIME TRENDS
# =====================================================================================
PROTECTED_AREA_TYPES = ["Wildlife Sanctuary", "National Park", "Biosphere Reserve", "Marine Protected Area"]

@st.cache_data
def generate_protected_areas():
    rng = random.Random(99)
    rows = []
    pid = 1
    for region_name, country, lat, lon in REGIONS:
        n = rng.randint(2, 4)
        for _ in range(n):
            jlat = lat + rng.uniform(-5, 5)
            jlon = lon + rng.uniform(-5, 5)
            area_type = rng.choice(PROTECTED_AREA_TYPES)
            rows.append({
                "area_id": pid,
                "name": f"{region_name} {area_type} #{pid}",
                "type": area_type,
                "region": region_name,
                "country": country,
                "latitude": round(jlat, 4),
                "longitude": round(jlon, 4),
                "area_sq_km": rng.randint(50, 12000),
            })
            pid += 1
    return pd.DataFrame(rows)


@st.cache_data
def generate_outbreak_trend(disease_df):
    """Synthetic illustrative 10-year outbreak-intensity trend per disease type,
    derived deterministically from the in-app dataset (NOT real surveillance data)."""
    rng = np.random.RandomState(7)
    years = list(range(datetime.now().year - 9, datetime.now().year + 1))
    types = sorted(disease_df["disease_type"].unique())
    rows = []
    for dtype in types:
        base = 20 + rng.randint(0, 40)
        walk = base
        for y in years:
            walk = max(5, walk + rng.randint(-6, 8))
            rows.append({"year": y, "disease_type": dtype, "reported_cases_index": walk})
    return pd.DataFrame(rows)


# =====================================================================================
# MACHINE LEARNING: RANDOM FOREST RISK / SEVERITY PREDICTION
# =====================================================================================
@st.cache_resource(show_spinner="Training Random Forest prediction model...")
def train_prediction_model(disease_df):
    df = disease_df.copy()

    le_group = LabelEncoder().fit(df["species_group"])
    le_type = LabelEncoder().fit(df["disease_type"])
    le_trans = LabelEncoder().fit(df["transmission_method"])
    le_cons = LabelEncoder().fit(df["conservation_status"])
    le_sev = LabelEncoder().fit(df["severity"])

    X = pd.DataFrame({
        "species_group": le_group.transform(df["species_group"]),
        "disease_type": le_type.transform(df["disease_type"]),
        "transmission_method": le_trans.transform(df["transmission_method"]),
        "conservation_status": le_cons.transform(df["conservation_status"]),
        "mortality_rate": df["mortality_rate"],
    })
    y = le_sev.transform(df["severity"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le_sev.classes_, output_dict=True)
    importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

    encoders = {
        "species_group": le_group, "disease_type": le_type,
        "transmission_method": le_trans, "conservation_status": le_cons, "severity": le_sev,
    }
    return {
        "model": model, "encoders": encoders, "accuracy": acc, "confusion_matrix": cm,
        "report": report, "importances": importances, "classes": le_sev.classes_,
        "feature_names": list(X.columns),
    }


# =====================================================================================
# EXPORT HELPERS
# =====================================================================================
def df_to_excel_bytes(sheets: dict):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    return buffer.getvalue()


def build_pdf_report(species_df, disease_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleGold", parent=styles["Title"], textColor=rl_colors.HexColor("#0b1c33"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=rl_colors.HexColor("#0b1c33"))
    body = styles["BodyText"]

    elements = [
        Paragraph("Global Species Disease Explorer", title_style),
        Paragraph("Comprehensive Disease Surveillance and Biodiversity Health Analytics Platform", body),
        Spacer(1, 0.4 * cm),
        Paragraph(f"Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", body),
        Spacer(1, 0.6 * cm),
        Paragraph(
            "Disclaimer: This report is generated from a synthetic, programmatically created "
            "dataset built for academic/demonstration purposes. It is not a verified scientific, "
            "veterinary, or epidemiological data source.", body,
        ),
        Spacer(1, 0.6 * cm),
        Paragraph("Summary Statistics", h2),
    ]

    summary_data = [
        ["Metric", "Value"],
        ["Total Species", str(len(species_df))],
        ["Total Disease Records", str(len(disease_df))],
        ["Unique Diseases Tracked", str(disease_df["disease_name"].nunique())],
        ["Threatened Species (VU/EN/CR)", str(species_df["conservation_status"].isin(
            ["Vulnerable", "Endangered", "Critically Endangered"]).sum())],
        ["Average Disease Risk Score", f"{species_df['disease_risk_score'].mean():.1f}"],
        ["Average Mortality Rate (%)", f"{disease_df['mortality_rate'].mean():.1f}"],
    ]
    t = Table(summary_data, colWidths=[8 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#d4af37")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.whitesmoke, rl_colors.HexColor("#f0f0f0")]),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.8 * cm))

    elements.append(Paragraph("Top 15 Highest-Risk Species", h2))
    top_risk = species_df.sort_values("disease_risk_score", ascending=False).head(15)
    risk_data = [["Species", "Group", "Risk Score", "IUCN"]] + top_risk[
        ["species_name", "species_group", "disease_risk_score", "iucn_code"]
    ].values.tolist()
    t2 = Table(risk_data, colWidths=[6 * cm, 3.5 * cm, 3 * cm, 2 * cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#0b1c33")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.whitesmoke, rl_colors.HexColor("#f0f0f0")]),
    ]))
    elements.append(t2)
    elements.append(PageBreak())

    elements.append(Paragraph("Top 15 Deadliest Diseases (by avg. mortality rate)", h2))
    deadliest = disease_df.groupby("disease_name")["mortality_rate"].mean().sort_values(ascending=False).head(15)
    deadly_data = [["Disease", "Avg Mortality Rate (%)"]] + [[k, f"{v:.1f}"] for k, v in deadliest.items()]
    t3 = Table(deadly_data, colWidths=[10 * cm, 5 * cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#0b1c33")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.whitesmoke, rl_colors.HexColor("#f0f0f0")]),
    ]))
    elements.append(t3)

    doc.build(elements)
    return buffer.getvalue()

# =====================================================================================
# PAGE: DASHBOARD
# =====================================================================================
def page_dashboard(species_df, disease_df):
    st.markdown('<div class="hero-title">🧬 Global Species Disease Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Comprehensive Disease Surveillance and Biodiversity Health Analytics Platform</div>', unsafe_allow_html=True)
    st.caption("Synthetic demonstration dataset · Not a verified scientific source · See **About Project** for details")
    st.write("")

    threatened = species_df["conservation_status"].isin(["Vulnerable", "Endangered", "Critically Endangered"]).sum()
    endangered = species_df["conservation_status"].isin(["Endangered", "Critically Endangered"]).sum()
    high_risk = (species_df["disease_risk_score"] >= 65).sum()
    outbreak_count = disease_df["severity"].isin(["High", "Critical"]).sum()
    recovered_proxy = disease_df["severity"].eq("Low").sum()
    avg_risk = species_df["disease_risk_score"].mean()

    r1 = st.columns(4)
    kpi_card(r1[0], "🐾", "Total Species", f"{len(species_df):,}", "across 6 taxonomic groups")
    kpi_card(r1[1], "🦠", "Total Disease Records", f"{len(disease_df):,}", f"{disease_df['disease_name'].nunique()} unique diseases")
    kpi_card(r1[2], "⚠️", "Threatened Species", f"{threatened:,}", "IUCN: VU + EN + CR")
    kpi_card(r1[3], "📈", "High Severity Cases", f"{outbreak_count:,}", "High + Critical severity records")

    r2 = st.columns(4)
    kpi_card(r2[0], "🔥", "High Risk Species", f"{high_risk:,}", "Risk score ≥ 65")
    kpi_card(r2[1], "🆘", "Endangered Species", f"{endangered:,}", "IUCN: EN + CR")
    kpi_card(r2[2], "✅", "Low-Severity (Recovered Proxy)", f"{recovered_proxy:,}", "Cases classified Low severity")
    kpi_card(r2[3], "📊", "Average Risk Score", f"{avg_risk:.1f} / 100", "Mean across all species")

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Species Distribution by Taxonomic Group")
        grp_counts = species_df["species_group"].value_counts().reset_index()
        grp_counts.columns = ["Group", "Count"]
        fig = px.pie(grp_counts, names="Group", values="Count", hole=0.5,
                     color_discrete_sequence=px.colors.sequential.Sunset)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#eaf1ff", legend=dict(orientation="h"))
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("#### Conservation Status Breakdown")
        cons_counts = species_df["conservation_status"].value_counts().reset_index()
        cons_counts.columns = ["Status", "Count"]
        fig2 = px.bar(cons_counts, x="Status", y="Count", color="Status",
                      color_discrete_sequence=px.colors.sequential.Agsunset)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#eaf1ff", showlegend=False)
        st.plotly_chart(fig2, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("#### Top 10 Most Frequently Recorded Diseases")
        top_dis = disease_df["disease_name"].value_counts().head(10).reset_index()
        top_dis.columns = ["Disease", "Records"]
        fig3 = px.bar(top_dis, x="Records", y="Disease", orientation="h",
                      color="Records", color_continuous_scale="YlOrBr")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#eaf1ff", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, width="stretch")
    with c4:
        st.markdown("#### Disease Risk Score Distribution")
        fig4 = px.histogram(species_df, x="disease_risk_score", nbins=25,
                            color_discrete_sequence=["#d4af37"])
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#eaf1ff", bargap=0.05)
        st.plotly_chart(fig4, width="stretch")


# =====================================================================================
# PAGE: SPECIES EXPLORER
# =====================================================================================
def risk_level_label(score):
    if score < 35:
        return "Low"
    elif score < 60:
        return "Moderate"
    elif score < 80:
        return "High"
    return "Critical"


def page_species_explorer(species_df, disease_df):
    st.markdown("## 🔎 Species Explorer")
    st.caption("Live search and multi-filter explorer across all 300+ species in the database.")

    species_df = species_df.copy()
    species_df["risk_level"] = species_df["disease_risk_score"].apply(risk_level_label)

    search = st.text_input("🔍 Live search by species name or scientific name", "")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        group_f = st.multiselect("Taxonomic Group", sorted(species_df["species_group"].unique()))
    with fc2:
        habitat_f = st.multiselect("Habitat", sorted(species_df["habitat"].unique()))
    with fc3:
        iucn_f = st.multiselect("IUCN Status", sorted(species_df["conservation_status"].unique()))
    with fc4:
        risk_f = st.multiselect("Risk Level", ["Low", "Moderate", "High", "Critical"])

    fc5, fc6 = st.columns(2)
    with fc5:
        country_f = st.multiselect("Country / Region", sorted(species_df["country"].unique()))
    with fc6:
        all_diseases = sorted(disease_df["disease_name"].unique())
        disease_f = st.multiselect("Affected by Disease", all_diseases)

    df = species_df.copy()
    if search:
        df = df[df["species_name"].str.contains(search, case=False) |
                df["scientific_name"].str.contains(search, case=False)]
    if group_f:
        df = df[df["species_group"].isin(group_f)]
    if habitat_f:
        df = df[df["habitat"].isin(habitat_f)]
    if iucn_f:
        df = df[df["conservation_status"].isin(iucn_f)]
    if risk_f:
        df = df[df["risk_level"].isin(risk_f)]
    if country_f:
        df = df[df["country"].isin(country_f)]
    if disease_f:
        valid_ids = disease_df[disease_df["disease_name"].isin(disease_f)]["species_id"].unique()
        df = df[df["species_id"].isin(valid_ids)]

    st.markdown(f"**{len(df)} species match your filters** (of {len(species_df)} total)")
    st.write("")

    for _, row in df.head(60).iterrows():
        health_score = max(0, 100 - row["disease_risk_score"])
        with st.expander(f"{row['species_name']}  —  {row['species_group']}  ·  {row['iucn_code']}"):
            colA, colB = st.columns([2, 1])
            with colA:
                st.markdown(f"**Scientific name:** *{row['scientific_name']}*")
                st.markdown(f"**Habitat:** {row['habitat']}  |  **Region:** {row['region']} ({row['country']})")
                st.markdown(f"**Avg. Lifespan:** {row['avg_lifespan_years']} years  |  **Population Trend:** {row['population_trend']}")
                st.markdown(f"**Conservation Status:** {row['conservation_status']} ({row['iucn_code']})")
                st.markdown(f"**Common Diseases:** {row['common_diseases']}")
                st.markdown(f"**Research Note:** _{row['research_notes']}_")
            with colB:
                st.markdown("**Species Health Score**")
                st.markdown(severity_meter(health_score), unsafe_allow_html=True)
                st.caption(f"{health_score:.0f} / 100")
                st.markdown("**Disease Risk Score**")
                st.markdown(severity_meter(row["disease_risk_score"]), unsafe_allow_html=True)
                st.caption(f"{row['disease_risk_score']:.1f} / 100  ·  {severity_badge(row['risk_level'])}", unsafe_allow_html=True)
                st.markdown(f"**Avg. Mortality Rate:** {row['avg_mortality_rate']}%")

    if len(df) > 60:
        st.info(f"Showing first 60 of {len(df)} matches. Refine filters to narrow further.")

# =====================================================================================
# PAGE: DISEASE DATABASE
# =====================================================================================
def page_disease_database(species_df, disease_df):
    st.markdown("## 🦠 Disease Database")
    st.caption(f"{disease_df['disease_name'].nunique()} unique diseases across {len(disease_df):,} species-disease association records.")

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        search = st.text_input("🔍 Search disease name", "")
    with fc2:
        type_f = st.multiselect("Disease Type", sorted(disease_df["disease_type"].unique()))
    with fc3:
        group_f = st.multiselect("Affects Group", sorted(disease_df["species_group"].unique()))
    with fc4:
        sev_f = st.multiselect("Severity", ["Low", "Moderate", "High", "Critical"])

    df = disease_df.copy()
    if search:
        df = df[df["disease_name"].str.contains(search, case=False)]
    if type_f:
        df = df[df["disease_type"].isin(type_f)]
    if group_f:
        df = df[df["species_group"].isin(group_f)]
    if sev_f:
        df = df[df["severity"].isin(sev_f)]

    st.markdown(f"**{len(df):,} records match your filters**")

    tab1, tab2 = st.tabs(["📋 Interactive Table", "🗂️ Disease Profile Cards"])
    with tab1:
        st.dataframe(
            df[["disease_name", "disease_type", "species_name", "species_group",
                "severity", "transmission_method", "symptoms", "treatment",
                "prevention", "mortality_rate", "risk_score"]].sort_values("risk_score", ascending=False),
            width="stretch", height=480,
        )
    with tab2:
        disease_summary = df.groupby("disease_name").agg(
            disease_type=("disease_type", "first"),
            species_affected=("species_name", "nunique"),
            avg_mortality=("mortality_rate", "mean"),
            avg_risk=("risk_score", "mean"),
            common_severity=("severity", lambda x: x.mode().iloc[0] if len(x) else "N/A"),
        ).reset_index().sort_values("avg_risk", ascending=False)

        for _, row in disease_summary.head(40).iterrows():
            with st.expander(f"{row['disease_name']}  ·  {row['disease_type']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    sample = df[df["disease_name"] == row["disease_name"]].iloc[0]
                    st.markdown(f"**Typical Transmission:** {sample['transmission_method']}")
                    st.markdown(f"**Typical Symptoms:** {sample['symptoms']}")
                    st.markdown(f"**Typical Treatment:** {sample['treatment']}")
                    st.markdown(f"**Typical Prevention:** {sample['prevention']}")
                    affected_species = df[df["disease_name"] == row["disease_name"]]["species_name"].unique()
                    st.markdown(f"**Species Affected ({len(affected_species)}):** " + ", ".join(affected_species[:15]) +
                                ("..." if len(affected_species) > 15 else ""))
                with c2:
                    st.markdown(severity_badge(row["common_severity"]), unsafe_allow_html=True)
                    st.metric("Species Affected", int(row["species_affected"]))
                    st.metric("Avg. Mortality Rate", f"{row['avg_mortality']:.1f}%")
                    st.markdown("**Avg. Risk Score**")
                    st.markdown(severity_meter(row["avg_risk"]), unsafe_allow_html=True)
                    st.caption(f"{row['avg_risk']:.1f} / 100")
        if len(disease_summary) > 40:
            st.info(f"Showing top 40 of {len(disease_summary)} diseases by risk score.")


# =====================================================================================
# PAGE: DISEASE ANALYTICS
# =====================================================================================
def page_disease_analytics(species_df, disease_df):
    st.markdown("## 📊 Disease Analytics")
    st.caption("Interactive Plotly visualizations across the full disease association dataset.")

    tabs = st.tabs(["Frequency", "Type Distribution", "Heatmap", "Treemap", "Sunburst",
                     "Mortality", "Risk Distribution", "Trends"])

    with tabs[0]:
        st.markdown("#### Disease Frequency Analysis (Top 20)")
        freq = disease_df["disease_name"].value_counts().head(20).reset_index()
        freq.columns = ["Disease", "Records"]
        fig = px.bar(freq, x="Records", y="Disease", orientation="h", color="Records",
                     color_continuous_scale="Tealgrn")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#eaf1ff", yaxis=dict(autorange="reversed"), height=600)
        st.plotly_chart(fig, width="stretch")

    with tabs[1]:
        st.markdown("#### Disease Type Distribution")
        c1, c2 = st.columns(2)
        with c1:
            type_counts = disease_df["disease_type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            fig = px.pie(type_counts, names="Type", values="Count", hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Plasma_r)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff")
            st.plotly_chart(fig, width="stretch")
        with c2:
            sev_counts = disease_df["severity"].value_counts().reindex(["Low", "Moderate", "High", "Critical"]).reset_index()
            sev_counts.columns = ["Severity", "Count"]
            fig2 = px.bar(sev_counts, x="Severity", y="Count", color="Severity",
                          color_discrete_map={"Low": "#3ddc97", "Moderate": "#4ea1ff",
                                               "High": "#ffb43c", "Critical": "#ff5d6c"})
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                font_color="#eaf1ff", showlegend=False)
            st.plotly_chart(fig2, width="stretch")

    with tabs[2]:
        st.markdown("#### Species Group vs Disease Type Heatmap")
        pivot = pd.crosstab(disease_df["species_group"], disease_df["disease_type"])
        fig = px.imshow(pivot, text_auto=True, color_continuous_scale="YlOrBr", aspect="auto")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", height=450)
        st.plotly_chart(fig, width="stretch")

    with tabs[3]:
        st.markdown("#### Disease Treemap (Type → Disease)")
        treemap_data = disease_df.groupby(["disease_type", "disease_name"]).size().reset_index(name="count")
        fig = px.treemap(treemap_data, path=["disease_type", "disease_name"], values="count",
                          color="count", color_continuous_scale="Sunsetdark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", height=550)
        st.plotly_chart(fig, width="stretch")

    with tabs[4]:
        st.markdown("#### Sunburst: Taxonomic Group → Disease Type → Severity")
        sb_data = disease_df.groupby(["species_group", "disease_type", "severity"]).size().reset_index(name="count")
        fig = px.sunburst(sb_data, path=["species_group", "disease_type", "severity"], values="count",
                           color="species_group", color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", height=600)
        st.plotly_chart(fig, width="stretch")

    with tabs[5]:
        st.markdown("#### Mortality Analysis by Severity")
        fig = px.box(disease_df, x="severity", y="mortality_rate", color="severity",
                     category_orders={"severity": ["Low", "Moderate", "High", "Critical"]},
                     color_discrete_map={"Low": "#3ddc97", "Moderate": "#4ea1ff",
                                          "High": "#ffb43c", "Critical": "#ff5d6c"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#eaf1ff", showlegend=False)
        st.plotly_chart(fig, width="stretch")

        st.markdown("#### Species vs Disease Count Analysis")
        avg_disease_count = species_df.groupby("species_group")["disease_count"].mean().reset_index()
        fig2 = px.bar(avg_disease_count, x="species_group", y="disease_count", color="species_group",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#eaf1ff", showlegend=False,
                            yaxis_title="Avg. Diseases per Species")
        st.plotly_chart(fig2, width="stretch")

    with tabs[6]:
        st.markdown("#### Risk Score Distribution Analysis")
        fig = px.histogram(disease_df, x="risk_score", color="species_group", nbins=30,
                           color_discrete_sequence=px.colors.qualitative.Vivid, opacity=0.75)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color="#eaf1ff", barmode="overlay")
        st.plotly_chart(fig, width="stretch")

    with tabs[7]:
        st.markdown("#### Illustrative 10-Year Outbreak Intensity Trend (simulated)")
        st.caption("Synthetic index generated for demonstration — not real surveillance data.")
        trend_df = generate_outbreak_trend(disease_df)
        fig = px.line(trend_df, x="year", y="reported_cases_index", color="disease_type", markers=True,
                      color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff")
        st.plotly_chart(fig, width="stretch")

# =====================================================================================
# PAGE: DISEASE RISK ASSESSMENT
# =====================================================================================
def page_risk_assessment(species_df, disease_df):
    st.markdown("## ⚠️ Disease Risk Assessment")
    st.caption("Interactive composite risk calculator built from the in-app dataset's risk model.")

    c1, c2 = st.columns([1, 1])
    with c1:
        species_name = st.selectbox("Select a species", sorted(species_df["species_name"].unique()))
    species_row = species_df[species_df["species_name"] == species_name].iloc[0]
    species_diseases = disease_df[disease_df["species_id"] == species_row["species_id"]]

    with c2:
        disease_options = species_diseases["disease_name"].tolist()
        disease_name = st.selectbox("Select an associated disease", disease_options) if disease_options else None

    if disease_name:
        drow = species_diseases[species_diseases["disease_name"] == disease_name].iloc[0]

        gauge_col, detail_col = st.columns([1, 1.3])
        with gauge_col:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=drow["risk_score"],
                title={"text": f"Composite Risk Score<br><span style='font-size:0.8em;color:#9fb3d1'>{species_name} — {disease_name}</span>"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#d4af37"},
                    "steps": [
                        {"range": [0, 35], "color": "#1a3a2f"},
                        {"range": [35, 60], "color": "#1a2e4d"},
                        {"range": [60, 80], "color": "#4d3a1a"},
                        {"range": [80, 100], "color": "#4d1a20"},
                    ],
                },
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", height=320)
            st.plotly_chart(fig, width="stretch")

        with detail_col:
            st.markdown(f"**Severity:** {severity_badge(drow['severity'])}", unsafe_allow_html=True)
            st.markdown(f"**Disease Type:** {drow['disease_type']}")
            st.markdown(f"**Transmission Method:** {drow['transmission_method']}")
            st.markdown(f"**Mortality Rate:** {drow['mortality_rate']}%")
            st.markdown(f"**Symptoms:** {drow['symptoms']}")
            st.markdown(f"**Recommended Treatment:** {drow['treatment']}")
            st.markdown(f"**Prevention Measures:** {drow['prevention']}")
            st.markdown(f"**Species Conservation Status:** {species_row['conservation_status']} ({species_row['iucn_code']})")

        st.markdown("#### Risk Factor Breakdown")
        severity_score = {"Low": 1, "Moderate": 2, "High": 3, "Critical": 4}[drow["severity"]]
        cons_factor = (["Least Concern", "Near Threatened", "Vulnerable", "Endangered",
                         "Critically Endangered", "Data Deficient"].index(species_row["conservation_status"]) + 1) * 5
        factors = pd.DataFrame({
            "Factor": ["Severity Weight", "Mortality Contribution", "Conservation Vulnerability", "Residual / Other"],
            "Contribution": [severity_score * 15, round(drow["mortality_rate"] * 0.4, 1), cons_factor,
                              max(0, round(drow["risk_score"] - (severity_score * 15 + drow["mortality_rate"] * 0.4 + cons_factor), 1))],
        })
        fig2 = px.bar(factors, x="Contribution", y="Factor", orientation="h", color="Factor",
                      color_discrete_sequence=px.colors.qualitative.Antique)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font_color="#eaf1ff", showlegend=False)
        st.plotly_chart(fig2, width="stretch")

        if drow["risk_score"] >= 80:
            st.error("🔴 **Critical Risk** — Immediate veterinary/conservation intervention recommended.")
        elif drow["risk_score"] >= 60:
            st.warning("🟠 **High Risk** — Active monitoring and preventive measures advised.")
        elif drow["risk_score"] >= 35:
            st.info("🔵 **Moderate Risk** — Routine surveillance recommended.")
        else:
            st.success("🟢 **Low Risk** — Standard monitoring protocols sufficient.")
    else:
        st.warning("No disease records found for this species.")

    st.divider()
    st.markdown("#### All High & Critical Risk Species (Risk Score ≥ 65)")
    high_risk_df = species_df[species_df["disease_risk_score"] >= 65].sort_values("disease_risk_score", ascending=False)
    st.dataframe(
        high_risk_df[["species_name", "species_group", "conservation_status", "disease_risk_score",
                      "avg_mortality_rate", "common_diseases"]],
        width="stretch", height=350,
    )


# =====================================================================================
# PAGE: GEOGRAPHICAL MAPPING
# =====================================================================================
def page_geo_mapping(species_df, disease_df):
    st.markdown("## 🗺️ Geographical Mapping")
    st.caption("Interactive Folium map of species distribution, disease hotspots, and protected areas.")

    view = st.radio("Map Layer", ["Species Distribution", "Disease Outbreak Hotspots", "Conservation Areas"],
                     horizontal=True)

    protected_df = generate_protected_areas()

    m = folium.Map(location=[15, 20], zoom_start=2, tiles="CartoDB dark_matter")

    if view == "Species Distribution":
        cluster = MarkerCluster().add_to(m)
        for _, row in species_df.iterrows():
            color = {"Least Concern": "green", "Near Threatened": "blue", "Vulnerable": "orange",
                     "Endangered": "red", "Critically Endangered": "darkred", "Data Deficient": "gray"}.get(row["conservation_status"], "blue")
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=5, color=color, fill=True, fill_color=color, fill_opacity=0.75,
                popup=folium.Popup(f"<b>{row['species_name']}</b><br>{row['species_group']}<br>"
                                    f"Status: {row['conservation_status']}<br>Risk: {row['disease_risk_score']}", max_width=250),
                tooltip=row["species_name"],
            ).add_to(cluster)

    elif view == "Disease Outbreak Hotspots":
        hot = disease_df[disease_df["severity"].isin(["High", "Critical"])]
        heat_data = hot[["latitude", "longitude"]].dropna().values.tolist()
        HeatMap(heat_data, radius=18, blur=22).add_to(m)
        cluster = MarkerCluster().add_to(m)
        for _, row in hot.sample(min(250, len(hot)), random_state=1).iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4, color="#ff5d6c", fill=True, fill_opacity=0.8,
                popup=folium.Popup(f"<b>{row['disease_name']}</b><br>{row['species_name']}<br>"
                                    f"Severity: {row['severity']}<br>Mortality: {row['mortality_rate']}%", max_width=250),
            ).add_to(cluster)

    else:  # Conservation Areas
        for _, row in protected_df.iterrows():
            icon_color = {"Wildlife Sanctuary": "green", "National Park": "darkgreen",
                          "Biosphere Reserve": "cadetblue", "Marine Protected Area": "blue"}.get(row["type"], "green")
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(f"<b>{row['name']}</b><br>Type: {row['type']}<br>Area: {row['area_sq_km']:,} km²", max_width=250),
                tooltip=row["name"],
                icon=folium.Icon(color=icon_color, icon="tree-conifer", prefix="glyphicon"),
            ).add_to(m)

    st_folium(m, width="stretch", height=540, returned_objects=[])

    if view == "Conservation Areas":
        st.dataframe(protected_df, width="stretch", height=300)

# =====================================================================================
# PAGE: RESEARCH CENTER
# =====================================================================================
def generate_research_summary(species_row, related_diseases):
    n = len(related_diseases)
    avg_mort = related_diseases["mortality_rate"].mean() if n else 0
    top_disease = related_diseases.sort_values("risk_score", ascending=False).iloc[0]["disease_name"] if n else "N/A"
    return (
        f"**{species_row['species_name']}** (*{species_row['scientific_name']}*) is classified as "
        f"**{species_row['conservation_status']}** under the in-app IUCN-style schema, with a population "
        f"trend recorded as **{species_row['population_trend']}**. Within this dataset, the species is "
        f"associated with **{n} tracked disease record(s)**, averaging a mortality rate of "
        f"**{avg_mort:.1f}%**. The highest-risk associated condition is **{top_disease}**. "
        f"Composite disease risk score stands at **{species_row['disease_risk_score']}/100**, placing it in the "
        f"**{risk_level_label(species_row['disease_risk_score'])}** risk band. {species_row['research_notes']}"
    )


def page_research_center(species_df, disease_df):
    st.markdown("## 🔬 Research Center")
    st.caption("Comparative analysis tools, rankings, and AI-style synthesized summaries from the in-app dataset.")

    tabs = st.tabs(["Species Comparison", "Disease Comparison", "Risk Rankings",
                     "Top 20 Vulnerable Species", "Top 20 Deadliest Diseases", "Research Summary Generator"])

    with tabs[0]:
        st.markdown("#### Species Comparison Tool")
        chosen = st.multiselect("Select 2–4 species to compare", sorted(species_df["species_name"].unique()),
                                 default=sorted(species_df["species_name"].unique())[:2])
        if len(chosen) >= 2:
            comp = species_df[species_df["species_name"].isin(chosen)]
            st.dataframe(comp[["species_name", "species_group", "conservation_status", "avg_lifespan_years",
                               "population_trend", "disease_count", "avg_mortality_rate", "disease_risk_score"]],
                         width="stretch")
            fig = go.Figure()
            for _, row in comp.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[row["disease_risk_score"], row["avg_mortality_rate"], row["disease_count"] * 10,
                       row["avg_lifespan_years"]],
                    theta=["Risk Score", "Mortality Rate", "Disease Count (×10)", "Lifespan (yrs)"],
                    fill="toself", name=row["species_name"],
                ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), paper_bgcolor="rgba(0,0,0,0)",
                              font_color="#eaf1ff", showlegend=True)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Select at least 2 species to compare.")

    with tabs[1]:
        st.markdown("#### Disease Comparison Tool")
        chosen_d = st.multiselect("Select 2–4 diseases to compare", sorted(disease_df["disease_name"].unique()),
                                   default=sorted(disease_df["disease_name"].unique())[:2])
        if len(chosen_d) >= 2:
            comp_d = disease_df[disease_df["disease_name"].isin(chosen_d)].groupby("disease_name").agg(
                species_affected=("species_name", "nunique"),
                avg_mortality=("mortality_rate", "mean"),
                avg_risk=("risk_score", "mean"),
                disease_type=("disease_type", "first"),
            ).reset_index()
            st.dataframe(comp_d, width="stretch")
            fig = px.bar(comp_d, x="disease_name", y=["avg_mortality", "avg_risk"], barmode="group",
                        color_discrete_sequence=["#ff5d6c", "#d4af37"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Select at least 2 diseases to compare.")

    with tabs[2]:
        st.markdown("#### Risk Ranking System")
        ranked = species_df.sort_values("disease_risk_score", ascending=False).reset_index(drop=True)
        ranked.index += 1
        st.dataframe(ranked[["species_name", "species_group", "conservation_status", "disease_risk_score",
                             "avg_mortality_rate"]], width="stretch", height=450)

    with tabs[3]:
        st.markdown("#### Top 20 Most Vulnerable Species")
        top20 = species_df.sort_values("disease_risk_score", ascending=False).head(20)
        fig = px.bar(top20, x="disease_risk_score", y="species_name", orientation="h", color="species_group",
                    color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff",
                          yaxis=dict(autorange="reversed"), height=600)
        st.plotly_chart(fig, width="stretch")

    with tabs[4]:
        st.markdown("#### Top 20 Deadliest Diseases (by avg. mortality rate)")
        deadliest = disease_df.groupby("disease_name").agg(
            avg_mortality=("mortality_rate", "mean"), disease_type=("disease_type", "first")
        ).reset_index().sort_values("avg_mortality", ascending=False).head(20)
        fig = px.bar(deadliest, x="avg_mortality", y="disease_name", orientation="h", color="disease_type",
                    color_discrete_sequence=px.colors.qualitative.Dark24)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff",
                          yaxis=dict(autorange="reversed"), height=600)
        st.plotly_chart(fig, width="stretch")

    with tabs[5]:
        st.markdown("#### AI-Style Research Summary Generator")
        sel = st.selectbox("Select a species for an auto-generated summary", sorted(species_df["species_name"].unique()), key="research_summary_select")
        srow = species_df[species_df["species_name"] == sel].iloc[0]
        related = disease_df[disease_df["species_id"] == srow["species_id"]]
        st.markdown(f'<div class="glass-card">{generate_research_summary(srow, related)}</div>', unsafe_allow_html=True)
        st.markdown("##### Smart Recommendations")
        if srow["disease_risk_score"] >= 65:
            st.markdown("- Prioritize this species for active disease surveillance.\n- Cross-reference with regional outbreak reports.\n- Evaluate captive/managed population health protocols.")
        else:
            st.markdown("- Maintain routine monitoring schedule.\n- Periodic re-assessment recommended (e.g. annually).")
        st.markdown("##### Suggested Further-Reading Categories")
        st.markdown(
            "- IUCN Red List species assessments\n"
            "- WOAH (World Organisation for Animal Health) disease technical cards\n"
            "- Journal of Wildlife Diseases\n"
            "- EcoHealth journal — wildlife/ecosystem health research\n"
            "- National/regional wildlife disease surveillance bulletins"
        )


# =====================================================================================
# PAGE: CONSERVATION DASHBOARD
# =====================================================================================
def page_conservation_dashboard(species_df, disease_df):
    st.markdown("## 🌿 Conservation Dashboard")
    st.caption("Cross-cutting view of disease burden, population trends, and conservation priorities.")

    threatened_df = species_df[species_df["conservation_status"].isin(
        ["Vulnerable", "Endangered", "Critically Endangered"])]

    r1 = st.columns(4)
    kpi_card(r1[0], "🚨", "Species Under Threat", f"{len(threatened_df):,}", "VU / EN / CR combined")
    kpi_card(r1[1], "📉", "Declining Populations", f"{(species_df['population_trend']=='Decreasing').sum():,}", "Trend: Decreasing")
    kpi_card(r1[2], "🏞️", "Habitats Tracked", f"{species_df['habitat'].nunique():,}", "Distinct habitat types")
    kpi_card(r1[3], "🩺", "Avg. Risk (Threatened Species)", f"{threatened_df['disease_risk_score'].mean():.1f}", "vs. overall avg "
             f"{species_df['disease_risk_score'].mean():.1f}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Disease Impact by Conservation Status")
        impact = species_df.groupby("conservation_status")["disease_risk_score"].mean().reindex(
            ["Least Concern", "Near Threatened", "Vulnerable", "Endangered", "Critically Endangered", "Data Deficient"]
        ).reset_index()
        fig = px.bar(impact, x="conservation_status", y="disease_risk_score", color="conservation_status",
                    color_discrete_sequence=px.colors.sequential.OrRd)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("#### Population Decline by Taxonomic Group")
        decline = species_df[species_df["population_trend"] == "Decreasing"]["species_group"].value_counts().reset_index()
        decline.columns = ["Group", "Declining Species"]
        fig2 = px.bar(decline, x="Group", y="Declining Species", color="Group",
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", showlegend=False)
        st.plotly_chart(fig2, width="stretch")

    st.markdown("#### Habitat Loss Indicators (species count per habitat, by population trend)")
    habitat_trend = species_df.groupby(["habitat", "population_trend"]).size().reset_index(name="count")
    fig3 = px.bar(habitat_trend, x="habitat", y="count", color="population_trend", barmode="stack",
                 color_discrete_map={"Increasing": "#3ddc97", "Stable": "#4ea1ff",
                                      "Decreasing": "#ff5d6c", "Unknown": "#9fb3d1"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff",
                       xaxis_tickangle=-30)
    st.plotly_chart(fig3, width="stretch")

    st.markdown("#### Conservation Actions & Recovery Programs (priority species)")
    priority = threatened_df.sort_values("disease_risk_score", ascending=False).head(10)
    actions_pool = [
        "Establish/expand captive breeding & assisted reproduction programs",
        "Strengthen anti-poaching and anti-trafficking enforcement",
        "Implement habitat corridor restoration projects",
        "Launch targeted vaccination/health-monitoring campaigns",
        "Increase community-based conservation incentive programs",
        "Expand protected area boundaries and buffer zones",
    ]
    rng = random.Random(11)
    for _, row in priority.iterrows():
        action = rng.choice(actions_pool)
        st.markdown(
            f'<div class="glass-card"><b>{row["species_name"]}</b> · {row["conservation_status"]} · '
            f'Risk Score: {row["disease_risk_score"]}<br>'
            f'<span style="color:#9fb3d1">Recommended action:</span> {action}</div>',
            unsafe_allow_html=True,
        )

# =====================================================================================
# PAGE: PREDICTION SYSTEM
# =====================================================================================
def page_prediction_system(species_df, disease_df):
    st.markdown("## 🤖 Prediction System")
    st.caption("Random Forest classifier trained on the in-app dataset to predict disease severity class.")

    bundle = train_prediction_model(disease_df)
    model, encoders = bundle["model"], bundle["encoders"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Model Accuracy", f"{bundle['accuracy']*100:.1f}%")
    m2.metric("Training Records", f"{int(len(disease_df)*0.8):,}")
    m3.metric("Test Records", f"{int(len(disease_df)*0.2):,}")

    tabs = st.tabs(["Live Prediction", "Model Performance", "Feature Importance"])

    with tabs[0]:
        st.markdown("#### Predict Disease Severity")
        c1, c2, c3 = st.columns(3)
        with c1:
            in_group = st.selectbox("Species Group", sorted(disease_df["species_group"].unique()))
            in_type = st.selectbox("Disease Type", sorted(disease_df["disease_type"].unique()))
        with c2:
            in_trans = st.selectbox("Transmission Method", sorted(disease_df["transmission_method"].unique()))
            in_cons = st.selectbox("Conservation Status", sorted(disease_df["conservation_status"].unique()))
        with c3:
            in_mort = st.slider("Mortality Rate (%)", 0.0, 100.0, 25.0, 0.5)

        if st.button("🔮 Predict Severity & Risk"):
            X_input = pd.DataFrame({
                "species_group": [encoders["species_group"].transform([in_group])[0]],
                "disease_type": [encoders["disease_type"].transform([in_type])[0]],
                "transmission_method": [encoders["transmission_method"].transform([in_trans])[0]],
                "conservation_status": [encoders["conservation_status"].transform([in_cons])[0]],
                "mortality_rate": [in_mort],
            })
            pred_class = model.predict(X_input)[0]
            pred_label = encoders["severity"].inverse_transform([pred_class])[0]
            pred_proba = model.predict_proba(X_input)[0]

            st.markdown(f"### Predicted Severity: {severity_badge(pred_label)}", unsafe_allow_html=True)
            proba_df = pd.DataFrame({"Severity": encoders["severity"].classes_, "Probability": pred_proba})
            fig = px.bar(proba_df, x="Severity", y="Probability", color="Severity",
                        category_orders={"Severity": ["Low", "Moderate", "High", "Critical"]},
                        color_discrete_map={"Low": "#3ddc97", "Moderate": "#4ea1ff",
                                             "High": "#ffb43c", "Critical": "#ff5d6c"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font_color="#eaf1ff", showlegend=False)
            st.plotly_chart(fig, width="stretch")
            st.caption("Prediction reflects patterns within this synthetic in-app dataset only.")

    with tabs[1]:
        st.markdown("#### Confusion Matrix")
        cm = bundle["confusion_matrix"]
        fig = px.imshow(cm, text_auto=True, x=list(bundle["classes"]), y=list(bundle["classes"]),
                        color_continuous_scale="Blues", labels=dict(x="Predicted", y="Actual"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#eaf1ff", height=420)
        st.plotly_chart(fig, width="stretch")

        st.markdown("#### Classification Report")
        report_df = pd.DataFrame(bundle["report"]).transpose().round(3)
        st.dataframe(report_df, width="stretch")

    with tabs[2]:
        st.markdown("#### Feature Importance")
        imp_df = bundle["importances"].reset_index()
        imp_df.columns = ["Feature", "Importance"]
        fig = px.bar(imp_df, x="Importance", y="Feature", orientation="h", color="Importance",
                    color_continuous_scale="YlOrBr")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="#eaf1ff", yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch")


# =====================================================================================
# PAGE: DATA DOWNLOAD CENTER
# =====================================================================================
def page_data_download(species_df, disease_df):
    st.markdown("## 📥 Data Download Center")
    st.caption("Export the full in-app dataset in CSV, Excel, JSON, or PDF report format.")

    st.markdown("#### Dataset Preview")
    tab1, tab2 = st.tabs(["Species Table", "Disease Records Table"])
    with tab1:
        st.dataframe(species_df, width="stretch", height=320)
    with tab2:
        st.dataframe(disease_df, width="stretch", height=320)

    st.divider()
    st.markdown("#### Export Options")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**CSV**")
        st.download_button("⬇️ Species CSV", species_df.to_csv(index=False).encode("utf-8"),
                          "species_database.csv", "text/csv")
        st.download_button("⬇️ Disease Records CSV", disease_df.to_csv(index=False).encode("utf-8"),
                          "disease_records.csv", "text/csv")

    with c2:
        st.markdown("**Excel**")
        excel_bytes = df_to_excel_bytes({"Species": species_df, "Disease Records": disease_df})
        st.download_button("⬇️ Full Workbook (.xlsx)", excel_bytes, "global_species_disease_explorer.xlsx",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with c3:
        st.markdown("**JSON**")
        json_bytes = json.dumps({
            "species": species_df.to_dict(orient="records"),
            "disease_records": disease_df.to_dict(orient="records"),
        }, indent=2).encode("utf-8")
        st.download_button("⬇️ Full Dataset (.json)", json_bytes, "global_species_disease_explorer.json",
                          "application/json")

    with c4:
        st.markdown("**PDF Report**")
        if st.button("📄 Generate PDF Report"):
            pdf_bytes = build_pdf_report(species_df, disease_df)
            st.session_state["pdf_bytes"] = pdf_bytes
        if "pdf_bytes" in st.session_state:
            st.download_button("⬇️ Download PDF Report", st.session_state["pdf_bytes"],
                              "species_disease_summary_report.pdf", "application/pdf")


# =====================================================================================
# PAGE: ABOUT PROJECT
# =====================================================================================
def page_about(species_df, disease_df):
    st.markdown("## ℹ️ About Project")
    st.markdown(
        f"""
        <div class="glass-card">
        <h3>Global Species Disease Explorer</h3>
        <p><i>Comprehensive Disease Surveillance and Biodiversity Health Analytics Platform</i></p>
        <p>Developed as an academic project (e.g. B.Sc. coursework / zoology, biodiversity research, or wildlife
        disease surveillance demonstration). Built entirely as a single self-contained Python file
        (<code>app.py</code>) using Streamlit — no external database required.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📦 Dataset Scope")
        st.markdown(
            f"""
            - **{len(species_df):,} species** across 6 taxonomic groups (Mammals, Birds, Reptiles, Amphibians, Fish, Insects)
            - **{len(disease_df):,} species–disease association records**
            - **{disease_df['disease_name'].nunique():,} unique tracked diseases**
            - **{len(generate_protected_areas()):,} synthetic protected-area markers** for geographic context
            """
        )
        st.markdown("#### 🛠️ Technology Stack")
        st.markdown(
            "- **Streamlit** — application framework & UI\n"
            "- **Pandas / NumPy** — data generation and processing\n"
            "- **Plotly** — interactive analytics (bar, pie, line, heatmap, treemap, sunburst, box, gauge)\n"
            "- **Folium + streamlit-folium** — interactive geographic mapping\n"
            "- **scikit-learn** — Random Forest severity-prediction model\n"
            "- **ReportLab** — PDF report generation\n"
            "- **openpyxl / XlsxWriter** — Excel export"
        )
    with c2:
        st.markdown("#### ⚠️ Important Data Disclaimer")
        st.warning(
            "All species and disease records in this application are **synthetically generated** "
            "programmatically for academic and demonstration purposes. Scientific names are accurate "
            "where well established in biology; however, **disease–species associations, severities, "
            "mortality rates, geographic coordinates, and the simulated outbreak trend are illustrative "
            "and randomly generated** — they are NOT a verified veterinary, epidemiological, or "
            "taxonomic data source and should not be used for real-world clinical, conservation, or "
            "policy decisions. For real data, consult primary sources such as the IUCN Red List, "
            "WOAH (World Organisation for Animal Health), or peer-reviewed wildlife disease journals."
        )
        st.markdown("#### 👤 Project Credit")
        st.text_input("Developed by (edit this field for your submission)", value="Your Name — B.Sc. Project", key="credit_field")
        st.markdown("#### 📚 Suggested Reference Categories")
        st.markdown(
            "- IUCN Red List of Threatened Species\n"
            "- WOAH / OIE Technical Disease Cards\n"
            "- Journal of Wildlife Diseases\n"
            "- EcoHealth Journal\n"
            "- National wildlife & veterinary surveillance bulletins"
        )

    st.markdown('<div class="footer-note">Global Species Disease Explorer · Synthetic Academic Demonstration Dataset · Built with Streamlit</div>', unsafe_allow_html=True)

# =====================================================================================
# MAIN APPLICATION / SIDEBAR NAVIGATION
# =====================================================================================
def main():
    inject_css()

    species_df, disease_df = generate_species_database()

    st.sidebar.markdown(
        """
        <div style="text-align:center; padding: 10px 0 4px 0;">
            <div style="font-size:2.2rem;">🧬</div>
            <div style="font-weight:800; color:#f1d77c; font-size:1.1rem;">Global Species<br>Disease Explorer</div>
            <div style="font-size:0.7rem; color:#9fb3d1; margin-top:4px;">Biodiversity Health Analytics</div>
        </div>
        <hr>
        """,
        unsafe_allow_html=True,
    )

    pages = {
        "Dashboard": ("📊", page_dashboard),
        "Species Explorer": ("🔎", page_species_explorer),
        "Disease Database": ("🦠", page_disease_database),
        "Disease Analytics": ("📈", page_disease_analytics),
        "Disease Risk Assessment": ("⚠️", page_risk_assessment),
        "Geographical Mapping": ("🗺️", page_geo_mapping),
        "Research Center": ("🔬", page_research_center),
        "Conservation Dashboard": ("🌿", page_conservation_dashboard),
        "Prediction System": ("🤖", page_prediction_system),
        "Data Download Center": ("📥", page_data_download),
        "About Project": ("ℹ️", page_about),
    }

    labels = [f"{icon}  {name}" for name, (icon, _) in pages.items()]
    choice = st.sidebar.radio("Navigate", labels, label_visibility="collapsed")
    selected_name = choice.split("  ", 1)[1]

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.75rem; color:#9fb3d1;">
        <b>{len(species_df):,}</b> species &nbsp;·&nbsp; <b>{len(disease_df):,}</b> disease records<br>
        Synthetic demo dataset
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, page_fn = pages[selected_name]
    try:
        page_fn(species_df, disease_df)
    except Exception as e:
        st.error(f"⚠️ Something went wrong rendering this page: {e}")
        st.caption("Try adjusting filters/selections, or reload the app.")


if __name__ == "__main__":
    main()