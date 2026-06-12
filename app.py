# =============================================================================
#  AETHERIA 3D — Advanced Molecular Visualizer
#  © 2025 Subhambada Sahu. All Rights Reserved.
#  Designed & Developed by Subhambada Sahu
# =============================================================================
#
#  Tech Stack : Python · Streamlit · RDKit · Py3Dmol · Pandas
#  Run        : streamlit run app.py
#  Install    : pip install streamlit rdkit pandas
#
# =============================================================================

import io
import json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# ── RDKit ──────────────────────────────────────────────────────────────────
try:
    from rdkit import Chem
    from rdkit.Chem import (
        AllChem, Descriptors, rdMolDescriptors,
        Draw, rdDepictor
    )
    from rdkit.Chem.rdForceFieldHelpers import MMFFOptimizeMolecule
    RDKIT_OK = True
except ImportError:
    RDKIT_OK = False

# ===========================================================================
#  PAGE CONFIG  (must be the very first Streamlit call)
# ===========================================================================
st.set_page_config(
    page_title="Aetheria 3D · Molecular Visualizer",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================================
#  CONSTANTS
# ===========================================================================
DEFAULT_SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"   # Aspirin

PRESETS = {
    "Aspirin":     "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Caffeine":    "Cn1cnc2c1c(=O)n(c(=O)n2C)C",
    "Ibuprofen":   "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
    "Paracetamol": "CC(=O)Nc1ccc(O)cc1",
    "Benzene":     "c1ccccc1",
    "Glucose":     "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
    "Cholesterol":
        "CC(C)CCCC(C)[C@@H]1CC[C@@H]2[C@@H]1CC=C1[C@@H]2CC[C@H]2CC(O)CC[C@H]12",
    "Ethanol":     "CCO",
    "Penicillin G":"CC1([C@@H](N2[C@H](S1)[C@@H](C2=O)NC(=O)Cc3ccccc3)C(=O)O)C",
    "Morphine":    "CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@@H]3[C@@H]1C5",
}

RENDER_STYLES = ["Ball & Stick", "Stick", "Sphere", "Cross", "Line"]

# ===========================================================================
#  GLOBAL CSS  –  dark scientific glassmorphism
# ===========================================================================
CSS = """
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Syne:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Variables ── */
:root{
  --void:        #020812;
  --surface:     rgba(5,14,35,0.85);
  --card:        rgba(8,20,50,0.72);
  --border:      rgba(0,200,255,0.22);
  --border-dim:  rgba(0,200,255,0.08);
  --cyan:        #00c8ff;
  --teal:        #00ffcc;
  --gold:        #f0a500;
  --red:         #ff4d6d;
  --green:       #00e676;
  --text:        #d8eeff;
  --muted:       #5a80a0;
  --dim:         #2a4060;
  --shadow-cyan: 0 0 22px rgba(0,200,255,0.35);
  --shadow-teal: 0 0 22px rgba(0,255,204,0.30);
  --r:           14px;
  --r-sm:        8px;
  --t:           0.2s cubic-bezier(.4,0,.2,1);
  --font-head:   'Orbitron',sans-serif;
  --font-ui:     'Syne',sans-serif;
  --font-mono:   'JetBrains Mono',monospace;
}

/* ── Reset ── */
html,body,[class*="css"]{ font-family:var(--font-ui)!important; color:var(--text)!important; }
*{ box-sizing:border-box; }

/* ── App background ── */
.stApp{
  background:var(--void)!important;
  background-image:
    radial-gradient(ellipse 70% 55% at 15% 15%,rgba(0,80,180,0.16) 0%,transparent 65%),
    radial-gradient(ellipse 55% 70% at 85% 85%,rgba(0,180,140,0.10) 0%,transparent 65%),
    radial-gradient(ellipse 35% 35% at 50% 50%,rgba(0,200,255,0.04) 0%,transparent 70%)!important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:rgba(0,0,0,0.2);}
::-webkit-scrollbar-thumb{background:rgba(0,200,255,0.25);border-radius:10px;}

/* ── Block container ── */
.block-container{
  padding-top:1.2rem!important;
  padding-bottom:5rem!important;
  max-width:1380px!important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,rgba(3,10,28,0.98) 0%,rgba(4,14,36,0.98) 100%)!important;
  border-right:1px solid var(--border)!important;
}
section[data-testid="stSidebar"] *{font-family:var(--font-ui)!important;}

/* ── Headings ── */
h1,h2,h3,h4{font-family:var(--font-head)!important;letter-spacing:0.05em!important;}

/* ── Masthead ── */
.masthead{
  display:flex;align-items:center;gap:18px;
  padding:20px 28px;
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--r);
  margin-bottom:20px;
  backdrop-filter:blur(18px);
  box-shadow:var(--shadow-cyan),inset 0 1px 0 rgba(255,255,255,0.04);
  position:relative;overflow:hidden;
  animation:fadeSlideIn .5s ease both;
}
.masthead::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--cyan),var(--teal),transparent);
}
.masthead-icon{font-size:2.6rem;filter:drop-shadow(0 0 14px var(--cyan));}
.masthead-title{
  font-family:var(--font-head)!important;font-size:1.8rem!important;
  font-weight:900!important;color:var(--cyan)!important;
  letter-spacing:0.14em!important;text-shadow:var(--shadow-cyan);
  margin:0!important;line-height:1!important;
}
.masthead-sub{
  font-family:var(--font-mono)!important;font-size:0.68rem!important;
  color:var(--muted)!important;letter-spacing:0.22em!important;
  text-transform:uppercase!important;margin-top:5px!important;
}
.masthead-badge{
  margin-left:auto;padding:5px 16px;
  background:rgba(0,200,255,0.07);
  border:1px solid var(--border);border-radius:20px;
  font-family:var(--font-mono)!important;font-size:0.66rem!important;
  color:var(--teal)!important;letter-spacing:0.16em;text-transform:uppercase;
}

/* ── Glass card ── */
.card{
  background:var(--card);border:1px solid var(--border-dim);
  border-radius:var(--r);padding:22px;
  backdrop-filter:blur(14px);
  box-shadow:0 4px 30px rgba(0,0,0,0.45);
  margin-bottom:18px;position:relative;overflow:hidden;
  animation:fadeSlideIn .5s ease both;
}
.card::before{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,200,255,0.35),transparent);
}
.card-title{
  font-family:var(--font-mono)!important;font-size:0.7rem!important;
  font-weight:500!important;color:var(--teal)!important;
  letter-spacing:0.22em!important;text-transform:uppercase!important;
  margin-bottom:16px!important;
  display:flex;align-items:center;gap:8px;
}
.card-title::before{
  content:'';display:inline-block;
  width:3px;height:13px;border-radius:2px;
  background:var(--cyan);box-shadow:var(--shadow-cyan);
}

/* ── Metric cards ── */
.metric-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(155px,1fr));
  gap:12px;margin:14px 0;
}
.mc{
  background:rgba(5,15,40,0.65);
  border:1px solid var(--border-dim);border-radius:var(--r-sm);
  padding:16px;position:relative;overflow:hidden;
  transition:border-color var(--t),box-shadow var(--t),transform var(--t);
}
.mc:hover{
  border-color:var(--border);box-shadow:var(--shadow-cyan);
  transform:translateY(-2px);
}
.mc::after{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  opacity:0;transition:opacity var(--t);
}
.mc:hover::after{opacity:1;}
.mc-lbl{
  font-family:var(--font-mono)!important;font-size:0.58rem!important;
  color:var(--dim)!important;text-transform:uppercase;
  letter-spacing:0.2em;margin-bottom:7px;
}
.mc-val{
  font-family:var(--font-head)!important;font-size:1.35rem!important;
  font-weight:700!important;color:var(--cyan)!important;
  text-shadow:var(--shadow-cyan);line-height:1;
}
.mc-unit{
  font-family:var(--font-mono)!important;font-size:0.58rem!important;
  color:var(--muted)!important;margin-top:4px;
}
.mc-icon{
  position:absolute;top:10px;right:12px;
  font-size:1rem;opacity:0.18;
}

/* ── Pill / badge ── */
.pill{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 11px;border-radius:20px;
  font-family:var(--font-mono)!important;
  font-size:0.6rem!important;letter-spacing:0.14em;text-transform:uppercase;
}
.pill-ok {background:rgba(0,230,118,0.08);border:1px solid rgba(0,230,118,0.25);color:var(--green)!important;}
.pill-ok::before{content:'●';font-size:0.5rem;color:var(--green);}
.pill-warn{background:rgba(240,165,0,0.08);border:1px solid rgba(240,165,0,0.25);color:var(--gold)!important;}
.pill-warn::before{content:'●';font-size:0.5rem;color:var(--gold);}
.pill-err {background:rgba(255,77,109,0.08);border:1px solid rgba(255,77,109,0.25);color:var(--red)!important;}
.pill-err::before{content:'●';font-size:0.5rem;color:var(--red);}

/* ── Section label ── */
.sec-lbl{
  font-family:var(--font-mono)!important;font-size:0.6rem!important;
  color:var(--dim)!important;letter-spacing:0.28em!important;
  text-transform:uppercase!important;
  padding:5px 0 4px;border-bottom:1px solid var(--border-dim);
  margin:12px 0 14px;
}

/* ── Sidebar logo ── */
.sb-logo{
  display:flex;flex-direction:column;align-items:center;
  padding:22px 16px 18px;
  border-bottom:1px solid var(--border-dim);margin-bottom:18px;
}
.sb-logo .icon{font-size:2.6rem;filter:drop-shadow(0 0 14px var(--cyan));}
.sb-logo .name{
  font-family:var(--font-head)!important;font-size:1rem!important;
  font-weight:700!important;color:var(--cyan)!important;
  letter-spacing:0.18em!important;margin-top:8px;
}
.sb-logo .ver{
  font-family:var(--font-mono)!important;font-size:0.58rem!important;
  color:var(--dim)!important;letter-spacing:0.22em;
  text-transform:uppercase;margin-top:3px;
}

/* ── Inputs ── */
.stTextInput input,
div[data-baseweb="select"]>div:first-child,
div[data-baseweb="input"]>div{
  background:rgba(3,10,28,0.85)!important;
  border:1px solid var(--border)!important;
  border-radius:var(--r-sm)!important;
  color:var(--text)!important;
  font-family:var(--font-mono)!important;
  font-size:0.82rem!important;
  transition:box-shadow var(--t),border-color var(--t)!important;
}
.stTextInput input:focus{box-shadow:var(--shadow-cyan)!important;border-color:var(--cyan)!important;}
.stTextInput label,.stSelectbox label,.stColorPicker label{
  font-family:var(--font-mono)!important;font-size:0.62rem!important;
  letter-spacing:0.2em!important;text-transform:uppercase!important;color:var(--dim)!important;
}

/* ── Selectbox option dropdown ── */
[data-baseweb="popover"]{background:#060f26!important;border:1px solid var(--border)!important;}
[role="option"]{font-family:var(--font-mono)!important;font-size:0.78rem!important;}

/* ── Buttons ── */
.stButton>button{
  font-family:var(--font-ui)!important;font-size:0.78rem!important;
  font-weight:700!important;letter-spacing:0.12em!important;text-transform:uppercase!important;
  background:rgba(0,200,255,0.07)!important;color:var(--cyan)!important;
  border:1px solid var(--border)!important;border-radius:var(--r-sm)!important;
  padding:8px 18px!important;transition:all var(--t)!important;width:100%!important;
}
.stButton>button:hover{
  background:rgba(0,200,255,0.16)!important;box-shadow:var(--shadow-cyan)!important;
  border-color:var(--cyan)!important;transform:translateY(-1px)!important;
}
.stDownloadButton>button{
  font-family:var(--font-ui)!important;font-size:0.78rem!important;
  font-weight:700!important;letter-spacing:0.12em!important;text-transform:uppercase!important;
  background:rgba(0,255,204,0.07)!important;color:var(--teal)!important;
  border:1px solid rgba(0,255,204,0.28)!important;border-radius:var(--r-sm)!important;
  padding:8px 18px!important;transition:all var(--t)!important;width:100%!important;
}
.stDownloadButton>button:hover{
  background:rgba(0,255,204,0.16)!important;box-shadow:var(--shadow-teal)!important;
  transform:translateY(-1px)!important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(3,10,28,0.65)!important;border-radius:var(--r-sm)!important;
  padding:4px!important;border:1px solid var(--border-dim)!important;gap:3px!important;
}
.stTabs [data-baseweb="tab"]{
  font-family:var(--font-ui)!important;font-size:0.75rem!important;
  font-weight:700!important;letter-spacing:0.1em!important;
  color:var(--muted)!important;border-radius:6px!important;
  padding:7px 18px!important;border:none!important;
  background:transparent!important;text-transform:uppercase;
  transition:all var(--t)!important;
}
.stTabs [aria-selected="true"]{
  background:rgba(0,200,255,0.12)!important;
  color:var(--cyan)!important;box-shadow:var(--shadow-cyan)!important;
}
.stTabs [data-baseweb="tab-highlight"]{display:none!important;}

/* ── Expander ── */
.streamlit-expanderHeader{
  font-family:var(--font-mono)!important;font-size:0.72rem!important;
  letter-spacing:0.14em!important;text-transform:uppercase!important;
  color:var(--muted)!important;
  background:rgba(3,10,28,0.55)!important;
  border:1px solid var(--border-dim)!important;border-radius:var(--r-sm)!important;
}
.streamlit-expanderContent{
  background:rgba(3,10,28,0.35)!important;
  border:1px solid var(--border-dim)!important;border-top:none!important;
  border-radius:0 0 var(--r-sm) var(--r-sm)!important;
}

/* ── Alert / info ── */
.stAlert{
  background:rgba(240,165,0,0.07)!important;
  border:1px solid rgba(240,165,0,0.28)!important;
  border-radius:var(--r-sm)!important;
  font-family:var(--font-ui)!important;
}

/* ── DataFrames ── */
.stDataFrame{
  background:var(--card)!important;
  border:1px solid var(--border-dim)!important;
  border-radius:var(--r-sm)!important;
}
.stDataFrame th{
  font-family:var(--font-mono)!important;font-size:0.65rem!important;
  letter-spacing:0.15em!important;color:var(--dim)!important;
  text-transform:uppercase!important;background:rgba(0,0,0,0.3)!important;
}
.stDataFrame td{
  font-family:var(--font-mono)!important;font-size:0.78rem!important;
  color:var(--text)!important;
}

/* ── Code block ── */
.stCode{
  background:rgba(3,10,28,0.8)!important;
  border:1px solid var(--border-dim)!important;
  border-radius:var(--r-sm)!important;
}
code{font-family:var(--font-mono)!important;}

/* ── Footer ── */
.footer{
  position:fixed;bottom:0;left:0;right:0;z-index:1000;
  background:linear-gradient(90deg,rgba(2,8,18,0.97) 0%,rgba(3,12,32,0.97) 50%,rgba(2,8,18,0.97) 100%);
  border-top:1px solid var(--border-dim);
  display:flex;align-items:center;justify-content:center;
  flex-wrap:wrap;gap:8px 16px;
  padding:8px 20px;backdrop-filter:blur(18px);
}
.footer-dot{width:3px;height:3px;border-radius:50%;background:var(--teal);box-shadow:var(--shadow-teal);}
.footer-txt{
  font-family:var(--font-mono)!important;font-size:0.65rem!important;
  color:var(--muted)!important;letter-spacing:0.14em;
}
.footer-name{color:var(--cyan)!important;font-weight:500;}
.footer-copy{color:var(--dim)!important;font-size:0.58rem!important;}

/* ── Animation ── */
@keyframes fadeSlideIn{
  from{opacity:0;transform:translateY(10px);}
  to{opacity:1;transform:translateY(0);}
}
@keyframes pulseGlow{
  0%,100%{opacity:1;} 50%{opacity:.55;}
}
.pulse{animation:pulseGlow 2.4s ease infinite;}

/* ── Divider ── */
.divider{
  border:none;border-top:1px solid var(--border-dim);margin:16px 0;
}

/* ── Rule row ── */
.rule-row{
  display:flex;align-items:center;justify-content:space-between;
  padding:9px 14px;
  background:rgba(5,14,40,0.5);
  border:1px solid var(--border-dim);border-radius:var(--r-sm);
  margin-bottom:7px;
}
.rule-lbl{font-family:var(--font-mono)!important;font-size:0.72rem!important;color:var(--text)!important;}
.rule-val{font-family:var(--font-head)!important;font-size:0.82rem!important;}

/* ── Identifier row ── */
.id-row{
  display:flex;gap:12px;align-items:flex-start;
  padding:8px 12px;
  background:rgba(0,0,0,0.2);
  border-radius:6px;border-left:2px solid rgba(0,200,255,0.28);
  margin-bottom:8px;
}
.id-key{
  font-family:var(--font-mono)!important;font-size:0.6rem!important;
  color:var(--dim)!important;min-width:150px;
  text-transform:uppercase;letter-spacing:0.14em;
}
.id-val{
  font-family:var(--font-mono)!important;font-size:0.72rem!important;
  color:var(--muted)!important;word-break:break-all;
}

/* ── Complexity bar ── */
.cx-bar-wrap{
  background:rgba(0,0,0,0.3);border-radius:4px;height:6px;
  margin-top:4px;overflow:hidden;
}
.cx-bar{
  height:100%;border-radius:4px;
  background:linear-gradient(90deg,var(--cyan),var(--teal));
  box-shadow:var(--shadow-cyan);
  transition:width .6s cubic-bezier(.4,0,.2,1);
}

/* ============================================================
   PRINT / @media print  –  clean white scientific report
   ============================================================ */
@media print{
  @page{margin:18mm 20mm;size:A4 portrait;}
  *{-webkit-print-color-adjust:exact!important;color-adjust:exact!important;}

  /* Hide UI chrome */
  section[data-testid="stSidebar"],
  .footer,
  .stDownloadButton,
  .stButton,
  .stTabs [data-baseweb="tab-list"],
  header,[data-testid="stToolbar"],
  [data-testid="stDecoration"],
  iframe{ display:none!important; }

  /* White page */
  .stApp,.block-container,body{
    background:#ffffff!important;color:#111!important;
  }

  /* Cards → plain white boxes */
  .card{
    background:#f8fafc!important;border:1px solid #cbd5e1!important;
    box-shadow:none!important;backdrop-filter:none!important;
    break-inside:avoid;
  }
  .card::before{display:none!important;}

  /* Metric cards */
  .mc{background:#f0f4f8!important;border:1px solid #cbd5e1!important;box-shadow:none!important;}
  .mc-lbl{color:#64748b!important;}
  .mc-val{color:#0369a1!important;text-shadow:none!important;}
  .mc-unit{color:#64748b!important;}

  /* Titles */
  .card-title,.masthead-title,.panel-title{color:#0369a1!important;}
  .card-title::before{background:#0369a1!important;box-shadow:none!important;}

  /* Masthead */
  .masthead{background:#f0f9ff!important;border:2px solid #0369a1!important;box-shadow:none!important;}
  .masthead::before{display:none!important;}
  .masthead-sub,.masthead-badge{color:#475569!important;}
  .masthead-badge{border-color:#94a3b8!important;}

  /* Rule rows */
  .rule-row{background:#f8fafc!important;border-color:#cbd5e1!important;}
  .rule-lbl{color:#111!important;}

  /* General text dark */
  h1,h2,h3,h4,p,span,div,td,th{color:#111!important;}

  /* Watermark */
  .print-watermark{
    display:block!important;
    position:fixed;
    top:50%;left:50%;
    transform:translate(-50%,-50%) rotate(-38deg);
    font-family:'Orbitron',sans-serif!important;
    font-size:5.5rem!important;font-weight:900!important;
    color:rgba(3,105,161,0.07)!important;
    letter-spacing:0.18em;
    white-space:nowrap;pointer-events:none;z-index:9999;
    text-transform:uppercase;
  }

  /* Print-only report block */
  .print-report{display:block!important;}
  .print-report *{color:#111!important;}
  .print-report table{width:100%;border-collapse:collapse;font-size:0.82rem;}
  .print-report th{
    background:#e0f2fe!important;color:#0369a1!important;
    padding:7px 10px;border:1px solid #bae6fd;
    font-family:'JetBrains Mono',monospace!important;font-size:0.65rem!important;
    text-transform:uppercase;letter-spacing:0.12em;
  }
  .print-report td{padding:6px 10px;border:1px solid #e2e8f0;}
  .print-report .pr-head{
    font-family:'Orbitron',sans-serif!important;
    font-size:1.5rem!important;color:#0369a1!important;
    border-bottom:3px solid #0369a1;padding-bottom:8px;margin-bottom:12px;
  }
  .print-report .pr-meta{font-size:0.8rem!important;color:#475569!important;margin-bottom:18px!important;}
  .print-report .pr-section{
    font-family:'Orbitron',sans-serif!important;
    font-size:0.88rem!important;color:#0369a1!important;
    margin:18px 0 8px;border-bottom:1px solid #bae6fd;padding-bottom:4px;
  }
  .print-report .pr-footer{
    margin-top:28px;padding-top:10px;border-top:1px solid #e2e8f0;
    font-size:0.68rem!important;color:#94a3b8!important;text-align:center!important;
  }
}

/* Hide print-only elements on screen */
.print-watermark,.print-report{display:none;}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ===========================================================================
#  FOOTER  (sticky, always visible)
# ===========================================================================
st.markdown("""
<div class="footer">
  <div class="footer-dot"></div>
  <span class="footer-txt">
    © 2025 <span class="footer-name">Subhambada Sahu</span>. All Rights Reserved.
  </span>
  <div class="footer-dot"></div>
  <span class="footer-txt">
    Aetheria 3D · Advanced Molecular Visualizer · v3.0
  </span>
  <div class="footer-dot"></div>
  <span class="footer-txt footer-copy">
    Powered by RDKit · Py3Dmol · Streamlit
  </span>
</div>
""", unsafe_allow_html=True)

# ===========================================================================
#  HELPER  –  Version-safe stereo center count
# ===========================================================================
def _count_stereo(mol) -> int:
    """Count stereo centers compatibly across all RDKit versions."""
    try:
        si = Chem.FindMolChiralCenters(mol, includeUnassigned=True, useLegacyImplementation=False)
        return int(len(si))
    except Exception:
        pass
    try:
        return int(len([
            a for a in mol.GetAtoms()
            if a.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED
        ]))
    except Exception:
        return 0


# ===========================================================================
#  HELPER  –  Molecule processing
# ===========================================================================
@st.cache_data(show_spinner=False)
def process_smiles(smiles: str):
    """
    Parse SMILES → AddHs → ETKDGv3 embed → MMFF94 minimise.
    Returns dict with props + mol_block, or error string.
    """
    if not RDKIT_OK:
        return None, "RDKit is not installed."
    smiles = smiles.strip()
    if not smiles:
        return None, "Empty SMILES."
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, "Invalid SMILES — could not parse structure."

    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol, params)
    if result == -1:
        result = AllChem.EmbedMolecule(mol, AllChem.EmbedParameters())
    if result == -1:
        return None, "3D embedding failed for this structure."

    try:
        MMFFOptimizeMolecule(mol, mmffVariant="MMFF94")
    except Exception:
        pass   # Proceed with un-minimised coords

    mol_block = Chem.MolToMolBlock(mol)

    mol_no_h    = Chem.RemoveHs(mol)
    formula     = rdMolDescriptors.CalcMolFormula(mol_no_h)
    canon       = Chem.MolToSmiles(mol_no_h)
    inchi_str   = Chem.MolToInchi(mol_no_h) or "N/A"
    inchikey    = Chem.InchiToInchiKey(inchi_str) if inchi_str != "N/A" else "N/A"

    props = {
        "Molecular Formula":            formula,
        "Exact MW (Da)":                round(Descriptors.ExactMolWt(mol), 4),
        "Avg MW (Da)":                  round(Descriptors.MolWt(mol_no_h), 4),
        "LogP":                         round(Descriptors.MolLogP(mol), 4),
        "TPSA (Å²)":                    round(Descriptors.TPSA(mol), 2),
        "Rotatable Bonds":              int(rdMolDescriptors.CalcNumRotatableBonds(mol)),
        "H-Bond Donors":                int(rdMolDescriptors.CalcNumHBD(mol)),
        "H-Bond Acceptors":             int(rdMolDescriptors.CalcNumHBA(mol)),
        "Ring Count":                   int(rdMolDescriptors.CalcNumRings(mol)),
        "Aromatic Rings":               int(rdMolDescriptors.CalcNumAromaticRings(mol)),
        "Heavy Atom Count":             int(mol_no_h.GetNumHeavyAtoms()),
        "Formal Charge":                int(sum(a.GetFormalCharge() for a in mol.GetAtoms())),
        "Fraction Csp3":                round(rdMolDescriptors.CalcFractionCSP3(mol), 4),
        "Stereo Centers":               _count_stereo(mol),
    }

    return {
        "props":     props,
        "mol_block": mol_block,
        "canon":     canon,
        "inchi":     inchi_str,
        "inchikey":  inchikey,
        "formula":   formula,
    }, None


def lipinski(props: dict):
    return [
        ("MW ≤ 500 Da",            props["Exact MW (Da)"]  <= 500),
        ("LogP ≤ 5",               props["LogP"]           <= 5),
        ("H-Bond Donors ≤ 5",     props["H-Bond Donors"]  <= 5),
        ("H-Bond Acceptors ≤ 10", props["H-Bond Acceptors"] <= 10),
    ]


def complexity_score(props: dict) -> float:
    """Rough complexity 0-100 score."""
    score = 0
    score += min(props["Heavy Atom Count"] / 60, 1) * 35
    score += min(props["Ring Count"] / 6, 1) * 25
    score += min(props["Stereo Centers"] / 8, 1) * 20
    score += min(props["Rotatable Bonds"] / 15, 1) * 10
    score += min(props["TPSA (Å²)"] / 200, 1) * 10
    return round(score, 1)


def viewer_html(mol_block: str, style: str, bg: str) -> str:
    """Build self-contained Py3Dmol HTML page."""
    style_js_map = {
        "Stick":
            "viewer.setStyle({},{stick:{radius:0.15,colorscheme:'Jmol'}});",
        "Sphere":
            "viewer.setStyle({},{sphere:{scale:0.38,colorscheme:'Jmol'}});",
        "Ball & Stick":
            "viewer.setStyle({},{stick:{radius:0.12,colorscheme:'Jmol'},sphere:{scale:0.22,colorscheme:'Jmol'}});",
        "Cross":
            "viewer.setStyle({},{cross:{lineWidth:5,colorscheme:'Jmol'}});",
        "Line":
            "viewer.setStyle({},{line:{lineWidth:2.5,colorscheme:'Jmol'}});",
    }
    sjs = style_js_map.get(style, style_js_map["Ball & Stick"])
    mb  = mol_block.replace("\\", "\\\\").replace("`", "\\`")

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:{bg};width:100%;height:100vh;overflow:hidden;
     display:flex;align-items:center;justify-content:center;}}
#vw{{width:100%;height:100vh;}}
.hint{{
  position:absolute;bottom:10px;left:50%;
  transform:translateX(-50%);
  background:rgba(0,0,0,0.5);color:rgba(255,255,255,0.45);
  font-family:'JetBrains Mono',monospace;font-size:9px;
  letter-spacing:0.16em;padding:3px 12px;border-radius:20px;
  border:1px solid rgba(255,255,255,0.08);pointer-events:none;white-space:nowrap;
}}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>
</head>
<body>
<div id="vw"></div>
<div class="hint">DRAG · rotate &nbsp;|&nbsp; SCROLL · zoom &nbsp;|&nbsp; RIGHT-DRAG · pan</div>
<script>
$(function(){{
  var viewer = $3Dmol.createViewer('vw',{{backgroundColor:'{bg}'}});
  var data = `{mb}`;
  viewer.addModel(data,'sdf');
  {sjs}
  viewer.zoomTo();
  viewer.zoom(0.82);
  viewer.spin('y', 0.45);
  viewer.render();
}});
</script>
</body>
</html>"""


# ===========================================================================
#  SIDEBAR
# ===========================================================================
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="icon">⬡</div>
      <div class="name">AETHERIA 3D</div>
      <div class="ver">Molecular Visualizer · v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-lbl">⬢ Molecular Input</div>', unsafe_allow_html=True)
    smiles_input = st.text_input(
        "SMILES String",
        value=DEFAULT_SMILES,
        placeholder="Paste valid SMILES…",
        help="Standard canonical SMILES notation"
    )
    mol_label = st.text_input("Molecule Label", value="Aspirin",
                              placeholder="e.g. Aspirin")

    st.markdown('<div class="sec-lbl">⬢ Quick Presets</div>', unsafe_allow_html=True)
    preset = st.selectbox("Load Preset Molecule",
                          ["— select —"] + list(PRESETS.keys()), index=0)
    if preset != "— select —":
        smiles_input = PRESETS[preset]
        mol_label    = preset

    st.markdown('<div class="sec-lbl">⬢ Viewport</div>', unsafe_allow_html=True)
    render_style = st.selectbox("Render Style", RENDER_STYLES, index=0)
    bg_color     = st.color_picker("Background Colour", value="#060e20")

    st.markdown('<div class="sec-lbl">⬢ Display</div>', unsafe_allow_html=True)
    show_lipinski  = st.checkbox("Lipinski Ro5 Panel",  value=True)
    show_admet     = st.checkbox("ADMET Estimates",     value=True)
    show_ids       = st.checkbox("Identifiers Panel",   value=True)
    show_raw       = st.checkbox("Raw Descriptor Table",value=False)

    st.markdown('<div class="sec-lbl">⬢ Status</div>', unsafe_allow_html=True)
    if RDKIT_OK:
        st.markdown('<span class="pill pill-ok">RDKit · Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-err">RDKit · Not Found</span>', unsafe_allow_html=True)
        st.warning("`pip install rdkit` then restart.")

# ===========================================================================
#  PROCESS MOLECULE
# ===========================================================================
label   = mol_label.strip() or "Unknown"
data, err = process_smiles(smiles_input)

# ===========================================================================
#  MASTHEAD
# ===========================================================================
status_html = (
    '<span class="pill pill-ok pulse">Structure · Valid</span>'
    if data else
    '<span class="pill pill-err pulse">Structure · Invalid</span>'
)

st.markdown(f"""
<div class="masthead">
  <div class="masthead-icon">⬡</div>
  <div>
    <div class="masthead-title">AETHERIA 3D</div>
    <div class="masthead-sub">Advanced Molecular Visualizer &amp; Cheminformatics Engine</div>
  </div>
  <div style="margin-left:auto;display:flex;flex-direction:column;align-items:flex-end;gap:7px;">
    <div class="masthead-badge">⬢ {label}</div>
    {status_html}
  </div>
</div>
""", unsafe_allow_html=True)

# Error banner
if err:
    st.warning(f"⚠️ **{err}** — Please enter a chemically valid SMILES string.")
    st.info("💡 Try: `CC(=O)OC1=CC=CC=C1C(=O)O` (Aspirin) or use a preset from the sidebar.")

# ===========================================================================
#  MAIN TABS
# ===========================================================================
tab_3d, tab_props, tab_drug, tab_export = st.tabs([
    "⬢  3D Viewer",
    "⬢  Properties",
    "⬢  Drug Analysis",
    "⬢  Export",
])

props = data["props"] if data else {}

# ───────────────────────────────────────────────────────────────────────────
#  TAB 1 · 3D VIEWER
# ───────────────────────────────────────────────────────────────────────────
with tab_3d:
    c_viewer, c_sidebar = st.columns([3, 1], gap="medium")

    with c_viewer:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Interactive 3D Viewport</div>', unsafe_allow_html=True)

        if data:
            html = viewer_html(data["mol_block"], render_style, bg_color)
            components.html(html, height=530, scrolling=False)
            st.markdown(f"""
            <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;">
              <span class="pill pill-ok">Style · {render_style}</span>
              <span class="pill pill-ok">MMFF94 Minimised</span>
              <span class="pill pill-ok">Formula · {data['formula']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:530px;display:flex;flex-direction:column;
                        align-items:center;justify-content:center;gap:16px;
                        border:1px dashed rgba(0,200,255,0.12);border-radius:10px;">
              <div style="font-size:4rem;opacity:0.15;">⬡</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                          color:#2a4060;letter-spacing:0.24em;">
                AWAITING VALID STRUCTURE
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with c_sidebar:
        st.markdown('<div class="card" style="height:calc(100% - 0px);">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Quick Metrics</div>', unsafe_allow_html=True)

        if props:
            quick = [
                ("MW", f'{props["Exact MW (Da)"]:.2f}', "Da", "⚖"),
                ("LogP", f'{props["LogP"]:.3f}', "", "💧"),
                ("TPSA", f'{props["TPSA (Å²)"]:.1f}', "Ų", "🌐"),
                ("Rot.", str(props["Rotatable Bonds"]), "bonds", "🔄"),
                ("HBD", str(props["H-Bond Donors"]), "", "🔵"),
                ("HBA", str(props["H-Bond Acceptors"]), "", "🔴"),
                ("Rings", str(props["Ring Count"]), "", "⬡"),
                ("Arom.", str(props["Aromatic Rings"]), "", "◎"),
            ]
            html_q = '<div style="display:flex;flex-direction:column;gap:9px;">'
            for lbl, val, unit, icon in quick:
                html_q += f"""
                <div class="mc">
                  <div class="mc-icon">{icon}</div>
                  <div class="mc-lbl">{lbl}</div>
                  <div class="mc-val">{val}</div>
                  {"<div class='mc-unit'>" + unit + "</div>" if unit else ""}
                </div>"""
            html_q += "</div>"
            st.markdown(html_q, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:30px 0;
                        font-family:'JetBrains Mono',monospace;
                        font-size:0.65rem;color:#2a4060;">NO DATA</div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
#  TAB 2 · PROPERTIES
# ───────────────────────────────────────────────────────────────────────────
with tab_props:
    if not props:
        st.markdown("""
        <div class="card" style="text-align:center;padding:50px;">
          <div style="font-size:3rem;opacity:0.2;margin-bottom:14px;">⬡</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                      color:#2a4060;letter-spacing:0.2em;">
            ENTER A VALID SMILES TO COMPUTE PROPERTIES
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Full KPI grid
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Physicochemical Descriptor Matrix</div>', unsafe_allow_html=True)

        kpis = [
            ("Exact MW",       f'{props["Exact MW (Da)"]:.4f}',       "Da",  "⚖"),
            ("Avg MW",         f'{props["Avg MW (Da)"]:.4f}',         "Da",  "⚖"),
            ("LogP",           f'{props["LogP"]:.4f}',                 "",   "💧"),
            ("TPSA",           f'{props["TPSA (Å²)"]:.2f}',           "Å²", "🌐"),
            ("Rot. Bonds",     str(props["Rotatable Bonds"]),          "",   "🔄"),
            ("HB Donors",      str(props["H-Bond Donors"]),            "",   "🔵"),
            ("HB Acceptors",   str(props["H-Bond Acceptors"]),         "",   "🔴"),
            ("Rings",          str(props["Ring Count"]),               "",   "⬡"),
            ("Arom. Rings",    str(props["Aromatic Rings"]),           "",   "◎"),
            ("Heavy Atoms",    str(props["Heavy Atom Count"]),         "",   "⚛"),
            ("Formal Charge",  str(props["Formal Charge"]),            "",   "⚡"),
            ("Frac. Csp3",    f'{props["Fraction Csp3"]:.4f}',        "",   "🔬"),
            ("Stereo Centers", str(props["Stereo Centers"]),           "",   "🧬"),
        ]
        g = '<div class="metric-grid">'
        for lbl, val, unit, icon in kpis:
            g += f"""
            <div class="mc">
              <div class="mc-icon">{icon}</div>
              <div class="mc-lbl">{lbl}</div>
              <div class="mc-val">{val}</div>
              {"<div class='mc-unit'>" + unit + "</div>" if unit else ""}
            </div>"""
        g += "</div>"
        st.markdown(g, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Molecular complexity
        cx = complexity_score(props)
        cx_color = ("#00e676" if cx < 35 else "#f0a500" if cx < 65 else "#ff4d6d")
        st.markdown(f"""
        <div class="card">
          <div class="card-title">Molecular Complexity Index</div>
          <div style="display:flex;align-items:center;gap:16px;">
            <div style="font-family:'Orbitron',sans-serif;font-size:2rem;
                        font-weight:700;color:{cx_color};text-shadow:0 0 18px {cx_color};">
              {cx}
              <span style="font-size:0.8rem;color:var(--muted);"> / 100</span>
            </div>
            <div style="flex:1;">
              <div class="cx-bar-wrap">
                <div class="cx-bar" style="width:{cx}%;background:linear-gradient(90deg,{cx_color},{cx_color}88);"></div>
              </div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                          color:var(--muted);margin-top:5px;letter-spacing:0.14em;">
                {"LOW COMPLEXITY" if cx < 35 else "MODERATE COMPLEXITY" if cx < 65 else "HIGH COMPLEXITY"}
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Identifiers
        if show_ids and data:
            with st.expander("⬢  IDENTIFIERS & NOTATION", expanded=True):
                for key, val in [
                    ("Input SMILES",     smiles_input),
                    ("Canonical SMILES", data["canon"]),
                    ("Formula",          data["formula"]),
                    ("InChI",            data["inchi"]),
                    ("InChIKey",         data["inchikey"]),
                ]:
                    st.markdown(f"""
                    <div class="id-row">
                      <span class="id-key">{key}</span>
                      <span class="id-val">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Raw table
        if show_raw:
            with st.expander("⬢  RAW DESCRIPTOR TABLE", expanded=False):
                df_raw = pd.DataFrame(
                    list(props.items()), columns=["Descriptor", "Value"]
                )
                st.dataframe(df_raw, use_container_width=True, hide_index=True)

# ───────────────────────────────────────────────────────────────────────────
#  TAB 3 · DRUG ANALYSIS
# ───────────────────────────────────────────────────────────────────────────
with tab_drug:
    if not props:
        st.markdown("""
        <div class="card" style="text-align:center;padding:50px;">
          <div style="font-size:3rem;opacity:0.2;margin-bottom:14px;">💊</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
                      color:#2a4060;letter-spacing:0.2em;">COMPUTE A MOLECULE FIRST</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Lipinski Ro5
        if show_lipinski:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Lipinski Rule of Five · Oral Bioavailability</div>',
                        unsafe_allow_html=True)
            rules = lipinski(props)
            passes = sum(1 for _, p in rules if p)
            rc4 = st.columns(4)
            for i, (rule, ok) in enumerate(rules):
                with rc4[i]:
                    c  = "#00e676" if ok else "#f0a500"
                    bg = f"rgba(0,230,118,0.06)" if ok else "rgba(240,165,0,0.06)"
                    br = f"rgba(0,230,118,0.22)" if ok else "rgba(240,165,0,0.22)"
                    st.markdown(f"""
                    <div style="background:{bg};border:1px solid {br};
                                border-radius:10px;padding:18px 14px;text-align:center;">
                      <div style="font-size:1.6rem;color:{c};margin-bottom:8px;">
                        {"✓" if ok else "✗"}
                      </div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                                  color:{c};letter-spacing:0.1em;text-transform:uppercase;">
                        {rule}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            vc = "#00e676" if passes == 4 else "#f0a500"
            vt = "PASSES ALL CRITERIA — Oral bioavailability candidate" if passes == 4 \
                 else f"FAILS {4-passes} RULE{'S' if 4-passes>1 else ''} — Potential bioavailability concern"
            st.markdown(f"""
            <div style="margin-top:14px;padding:12px 20px;
                        background:rgba(0,0,0,0.22);border-radius:8px;
                        border:1px solid {vc}33;
                        display:flex;align-items:center;gap:12px;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                           color:var(--dim);letter-spacing:0.16em;">VERDICT</span>
              <span style="font-family:'Orbitron',sans-serif;font-size:0.92rem;
                           font-weight:700;color:{vc};">{vt}</span>
              <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;
                           font-size:0.65rem;color:{vc};">{passes}/4 passed</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── ADMET Estimates
        if show_admet:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">ADMET Estimate Panel (Rule-Based)</div>',
                        unsafe_allow_html=True)

            mw   = props["Exact MW (Da)"]
            logp = props["LogP"]
            tpsa = props["TPSA (Å²)"]
            hbd  = props["H-Bond Donors"]
            rotb = props["Rotatable Bonds"]

            # Crude but indicative heuristics
            abs_ok    = (mw < 500) and (logp < 5) and (tpsa < 140) and (hbd <= 5)
            bbb_ok    = (mw < 400) and (logp > 0) and (logp < 5) and (tpsa < 90) and (hbd <= 3)
            sol_label = ("GOOD"   if logp < 1 else
                         "MODERATE" if logp < 3 else
                         "LOW" if logp < 5 else "POOR")
            sol_color = ("#00e676" if sol_label == "GOOD" else
                         "#00c8ff" if sol_label == "MODERATE" else
                         "#f0a500" if sol_label == "LOW" else "#ff4d6d")
            perm_ok   = (tpsa < 60) and (mw < 400)
            flex_ok   = rotb <= 10

            admet_rows = [
                ("Oral Absorption",     "LIKELY" if abs_ok else "UNCERTAIN",
                 "#00e676" if abs_ok else "#f0a500"),
                ("BBB Penetration",     "LIKELY" if bbb_ok else "UNLIKELY",
                 "#00e676" if bbb_ok else "#ff4d6d"),
                ("Aqueous Solubility",  sol_label, sol_color),
                ("GI Permeability",     "GOOD" if perm_ok else "MODERATE",
                 "#00e676" if perm_ok else "#f0a500"),
                ("Molecular Flexibility","GOOD" if flex_ok else "RESTRICTED",
                 "#00e676" if flex_ok else "#f0a500"),
                ("Drug-like Score",
                 "HIGH" if (abs_ok and sol_label in ("GOOD","MODERATE")) else
                 "MODERATE" if abs_ok else "LOW",
                 "#00e676" if (abs_ok and sol_label in ("GOOD","MODERATE")) else
                 "#f0a500" if abs_ok else "#ff4d6d"),
            ]

            for lbl, val, col in admet_rows:
                st.markdown(f"""
                <div class="rule-row">
                  <span class="rule-lbl">{lbl}</span>
                  <span class="rule-val" style="color:{col};">{val}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style="margin-top:10px;font-family:'JetBrains Mono',monospace;
                        font-size:0.58rem;color:var(--dim);letter-spacing:0.12em;">
              ⚠ Rule-based estimates only. Use ADMET-AI, SwissADME or pkCSM for validated predictions.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Veber / Egan / Ghose
        with st.expander("⬢  ADDITIONAL DRUG-LIKENESS FILTERS", expanded=False):
            mw   = props["Exact MW (Da)"]
            logp = props["LogP"]
            tpsa = props["TPSA (Å²)"]
            hbd  = props["H-Bond Donors"]
            hba  = props["H-Bond Acceptors"]
            rotb = props["Rotatable Bonds"]
            hac  = props["Heavy Atom Count"]

            filters = {
                "Veber (oral bioavailability)":
                    (rotb <= 10) and (tpsa <= 140),
                "Egan (passive intestinal absorption)":
                    (0.0 <= logp <= 5.88) and (tpsa <= 131.6),
                "Ghose (drug-like chemical space)":
                    (160 <= mw <= 480) and (-0.4 <= logp <= 5.6) and
                    (40 <= hac <= 70),
                "Muegge (drug-likeness)":
                    (200 <= mw <= 600) and (-2 <= logp <= 5) and
                    (tpsa <= 150) and (rotb <= 15) and
                    (hbd <= 5) and (hba <= 10),
            }
            for fname, result in filters.items():
                c   = "#00e676" if result else "#ff4d6d"
                txt = "PASS" if result else "FAIL"
                st.markdown(f"""
                <div class="rule-row">
                  <span class="rule-lbl">{fname}</span>
                  <span class="rule-val" style="color:{c};">{txt}</span>
                </div>
                """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
#  TAB 4 · EXPORT
# ───────────────────────────────────────────────────────────────────────────
with tab_export:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Export & Download Centre</div>', unsafe_allow_html=True)

    if not data:
        st.markdown("""
        <div style="text-align:center;padding:40px;
                    font-family:'JetBrains Mono',monospace;
                    font-size:0.72rem;color:#2a4060;letter-spacing:0.2em;">
          COMPUTE A VALID MOLECULE TO UNLOCK EXPORTS
        </div>
        """, unsafe_allow_html=True)
    else:
        ec1, ec2, ec3, ec4 = st.columns(4, gap="medium")

        # ── CSV
        with ec1:
            st.markdown("""
            <div style="text-align:center;margin-bottom:14px;">
              <div style="font-size:2rem;margin-bottom:7px;">📊</div>
              <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;
                          color:var(--teal);letter-spacing:0.1em;text-transform:uppercase;
                          margin-bottom:4px;">Properties CSV</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--dim);">
                All descriptors in<br>comma-separated format
              </div>
            </div>
            """, unsafe_allow_html=True)
            df_csv = pd.DataFrame([{"Molecule": label, "SMILES": smiles_input, **props}])
            st.download_button(
                "⬇ Download .CSV",
                df_csv.to_csv(index=False).encode(),
                f"{label.replace(' ','_')}_descriptors.csv",
                "text/csv", key="dl_csv"
            )

        # ── MOL
        with ec2:
            st.markdown("""
            <div style="text-align:center;margin-bottom:14px;">
              <div style="font-size:2rem;margin-bottom:7px;">🧬</div>
              <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;
                          color:var(--teal);letter-spacing:0.1em;text-transform:uppercase;
                          margin-bottom:4px;">3D MOL File</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--dim);">
                MMFF94-minimised<br>MDL Molfile format
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                "⬇ Download .MOL",
                data["mol_block"].encode(),
                f"{label.replace(' ','_')}_3D.mol",
                "chemical/x-mdl-molfile", key="dl_mol"
            )

        # ── JSON
        with ec3:
            st.markdown("""
            <div style="text-align:center;margin-bottom:14px;">
              <div style="font-size:2rem;margin-bottom:7px;">🗂️</div>
              <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;
                          color:var(--teal);letter-spacing:0.1em;text-transform:uppercase;
                          margin-bottom:4px;">JSON Report</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--dim);">
                Full descriptor report<br>in JSON schema format
              </div>
            </div>
            """, unsafe_allow_html=True)
            jdata = {
                "molecule":   label,
                "smiles":     smiles_input,
                "canonical":  data["canon"],
                "formula":    data["formula"],
                "inchi":      data["inchi"],
                "inchikey":   data["inchikey"],
                "properties": props,
                "lipinski":   {r: bool(p) for r, p in lipinski(props)},
                "generated_by": "Aetheria 3D · Subhambada Sahu",
            }
            st.download_button(
                "⬇ Download .JSON",
                json.dumps(jdata, indent=2).encode(),
                f"{label.replace(' ','_')}_report.json",
                "application/json", key="dl_json"
            )

        # ── Print
        with ec4:
            st.markdown("""
            <div style="text-align:center;margin-bottom:14px;">
              <div style="font-size:2rem;margin-bottom:7px;">🖨️</div>
              <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;
                          color:var(--cyan);letter-spacing:0.1em;text-transform:uppercase;
                          margin-bottom:4px;">Print PDF Report</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--dim);">
                White-background printable<br>report + watermark
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🖨 Open Print Dialog", key="print_btn"):
                components.html("<script>window.parent.print();</script>", height=0)

        # ── Canonical SMILES
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="card-title" style="margin-bottom:10px;">Canonical SMILES</div>',
                    unsafe_allow_html=True)
        st.code(data["canon"], language=None)

    st.markdown('</div>', unsafe_allow_html=True)

# ===========================================================================
#  PRINT-ONLY HIDDEN REPORT  (rendered into DOM; visible only when printing)
# ===========================================================================
if data and props:
    rules_html = "".join(
        f"<tr><td>{r}</td>"
        f"<td style='color:{'green' if p else 'orange'};font-weight:600;'>"
        f"{'✓ PASS' if p else '✗ FAIL'}</td></tr>"
        for r, p in lipinski(props)
    )
    desc_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in props.items()
    )

    st.markdown(f"""
    <!-- WATERMARK (print only) -->
    <div class="print-watermark">AETHERIA 3D</div>

    <!-- PRINT REPORT (print only) -->
    <div class="print-report">
      <div class="pr-head">⬡ Aetheria 3D — Molecular Analysis Report</div>
      <div class="pr-meta">
        Molecule: <strong>{label}</strong> &nbsp;|&nbsp;
        Formula: <strong>{data['formula']}</strong> &nbsp;|&nbsp;
        Generated by: <strong>Aetheria 3D · Subhambada Sahu</strong>
      </div>

      <div class="pr-section">Input SMILES</div>
      <code style="background:#f1f5f9;padding:7px 12px;border-radius:5px;
                   font-size:0.8rem;display:block;word-break:break-all;">
        {smiles_input}
      </code>

      <div class="pr-section">Canonical SMILES</div>
      <code style="background:#f1f5f9;padding:7px 12px;border-radius:5px;
                   font-size:0.8rem;display:block;word-break:break-all;">
        {data['canon']}
      </code>

      <div class="pr-section">Physicochemical Descriptors</div>
      <table>
        <thead>
          <tr><th>Descriptor</th><th>Value</th></tr>
        </thead>
        <tbody>{desc_rows}</tbody>
      </table>

      <div class="pr-section">Lipinski Rule of Five</div>
      <table>
        <thead>
          <tr><th>Rule</th><th>Status</th></tr>
        </thead>
        <tbody>{rules_html}</tbody>
      </table>

      <div class="pr-section">Identifiers</div>
      <table>
        <thead><tr><th>Key</th><th>Value</th></tr></thead>
        <tbody>
          <tr><td>InChI</td><td style="word-break:break-all;font-size:0.72rem;">{data['inchi']}</td></tr>
          <tr><td>InChIKey</td><td>{data['inchikey']}</td></tr>
        </tbody>
      </table>

      <div class="pr-footer">
        © 2026 Subhambada Sahu · All Rights Reserved &nbsp;|&nbsp;
        Aetheria 3D Advanced Molecular Visualizer v3.0 &nbsp;|&nbsp;
        Powered by RDKit · Py3Dmol · Streamlit
      </div>
    </div>
    """, unsafe_allow_html=True)

