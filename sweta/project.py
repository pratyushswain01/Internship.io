"""
Gravitational Force Calculator
Developed by Swetabarnali Panda
A high-performance scientific tool using Newton's Law of Universal Gravitation.
"""

import streamlit as st
import math
from dataclasses import dataclass
from typing import Optional

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gravitational Force Calculator | Swetabarnali Panda",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Constants ────────────────────────────────────────────────────────────────
G: float = 6.67430e-11  # Gravitational constant (m³ kg⁻¹ s⁻²)

PRESET_BODIES: dict[str, float] = {
    "Custom": 0.0,
    "Earth (5.972 × 10²⁴ kg)": 5.972e24,
    "Moon (7.342 × 10²² kg)": 7.342e22,
    "Sun (1.989 × 10³⁰ kg)": 1.989e30,
    "Jupiter (1.898 × 10²⁷ kg)": 1.898e27,
    "Mars (6.417 × 10²³ kg)": 6.417e23,
    "Human (70 kg)": 70.0,
    "Proton (1.673 × 10⁻²⁷ kg)": 1.673e-27,
}

PRESET_DISTANCES: dict[str, float] = {
    "Custom": 0.0,
    "Earth–Moon (3.844 × 10⁸ m)": 3.844e8,
    "Earth–Sun (1.496 × 10¹¹ m)": 1.496e11,
    "Earth–Mars (avg 2.25 × 10¹¹ m)": 2.25e11,
    "1 km": 1e3,
    "1 m": 1.0,
}


# ─── CSS Injection ─────────────────────────────────────────────────────────────
def inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Fonts ── */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;600&display=swap');

        /* ── Root Palette ── */
        :root {
            --navy-900: #020917;
            --navy-800: #060f24;
            --navy-700: #0b1a3a;
            --navy-600: #102050;
            --cyan-400: #00d4ff;
            --cyan-300: #5ee7ff;
            --green-400: #00ff88;
            --green-300: #72ffb8;
            --white-90: rgba(255,255,255,0.90);
            --white-60: rgba(255,255,255,0.60);
            --white-20: rgba(255,255,255,0.20);
            --white-08: rgba(255,255,255,0.08);
            --glass-bg: rgba(11, 26, 58, 0.55);
            --glass-border: rgba(0, 212, 255, 0.18);
            --glow-cyan: 0 0 22px rgba(0, 212, 255, 0.35);
            --glow-green: 0 0 22px rgba(0, 255, 136, 0.35);
        }

        /* ── Global Reset ── */
        html, body, .stApp {
            background: var(--navy-900) !important;
            color: var(--white-90) !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        /* ── Starfield Background ── */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(0, 212, 255, 0.06) 0%, transparent 55%),
                radial-gradient(ellipse at 80% 80%, rgba(0, 255, 136, 0.05) 0%, transparent 55%),
                radial-gradient(ellipse at 50% 50%, rgba(6, 15, 36, 0.9) 0%, var(--navy-900) 100%);
            pointer-events: none;
            z-index: 0;
        }

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(160deg, #060f24 0%, #0b1a3a 100%) !important;
            border-right: 1px solid var(--glass-border) !important;
        }
        section[data-testid="stSidebar"] * {
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--white-90) !important;
        }
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stNumberInput label {
            color: var(--cyan-300) !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
        }

        /* ── Inputs & Selects ── */
        .stNumberInput input,
        .stSelectbox > div > div {
            background: var(--white-08) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            color: var(--white-90) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
        }
        .stNumberInput input:focus,
        .stSelectbox > div > div:focus-within {
            border-color: var(--cyan-400) !important;
            box-shadow: var(--glow-cyan) !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            background: linear-gradient(135deg, rgba(0,212,255,0.15) 0%, rgba(0,255,136,0.10) 100%) !important;
            border: 1px solid var(--cyan-400) !important;
            border-radius: 8px !important;
            color: var(--cyan-300) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.25s ease !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, rgba(0,212,255,0.28) 0%, rgba(0,255,136,0.20) 100%) !important;
            box-shadow: var(--glow-cyan) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--white-08) !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 4px !important;
            border: 1px solid var(--glass-border) !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 7px !important;
            color: var(--white-60) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 500 !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0,212,255,0.22) 0%, rgba(0,255,136,0.14) 100%) !important;
            color: var(--cyan-300) !important;
            border: 1px solid var(--glass-border) !important;
        }

        /* ── Expander ── */
        .streamlit-expanderHeader {
            background: var(--white-08) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            color: var(--cyan-300) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
        }
        .streamlit-expanderContent {
            background: rgba(6,15,36,0.6) !important;
            border: 1px solid var(--glass-border) !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
        }

        /* ── Hide Streamlit Chrome ── */
        #MainMenu, footer, header { visibility: hidden !important; }
        .block-container { padding-top: 1.5rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Data Structures ──────────────────────────────────────────────────────────
@dataclass
class GravityResult:
    force_newtons: float
    mantissa: float        # coefficient in scientific notation  e.g. 1.9823
    exponent: int          # power of 10                         e.g. 20
    mass1_kg: float
    mass2_kg: float
    distance_m: float
    log10_force: float
    equivalent_weight_kg: float


# ─── Calculation Engine ───────────────────────────────────────────────────────
def calculate_gravity(m1: float, m2: float, r: float) -> Optional[GravityResult]:
    """
    Compute gravitational force using Newton's Law of Universal Gravitation.

    F = G * (m1 * m2) / r²

    Args:
        m1: Mass of first object in kilograms (kg).
        m2: Mass of second object in kilograms (kg).
        r:  Distance between centres of mass in metres (m).

    Returns:
        GravityResult dataclass or None if inputs are invalid.
    """
    if m1 <= 0 or m2 <= 0 or r <= 0:
        return None

    force: float = G * (m1 * m2) / (r ** 2)

    exponent: int = int(math.floor(math.log10(abs(force)))) if force > 0 else 0
    mantissa: float = force / (10 ** exponent)

    return GravityResult(
        force_newtons=force,
        mantissa=mantissa,
        exponent=exponent,
        mass1_kg=m1,
        mass2_kg=m2,
        distance_m=r,
        log10_force=math.log10(force) if force > 0 else 0.0,
        equivalent_weight_kg=force / 9.80665,
    )


def format_si(value: float, unit: str = "") -> str:
    """Format a float into a compact SI-prefixed string."""
    prefixes = [
        (1e30, "× 10³⁰"), (1e27, "× 10²⁷"), (1e24, "× 10²⁴"),
        (1e21, "× 10²¹"), (1e18, "× 10¹⁸"), (1e15, "× 10¹⁵"),
        (1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "k"),
        (1e0, ""), (1e-3, "m"), (1e-6, "μ"), (1e-9, "n"),
        (1e-12, "p"), (1e-15, "f"), (1e-27, "× 10⁻²⁷"),
    ]
    for threshold, prefix in prefixes:
        if abs(value) >= threshold:
            return f"{value/threshold:.4f} {prefix}{unit}"
    return f"{value:.4e} {unit}"


# ─── UI Components ─────────────────────────────────────────────────────────────
def render_header() -> None:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(0,255,136,0.05) 100%);
            border: 1px solid rgba(0,212,255,0.22);
            border-radius: 14px;
            padding: 1.6rem 2rem 1.4rem;
            margin-bottom: 1.4rem;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position:absolute; inset:0;
                background: radial-gradient(ellipse at 80% 50%, rgba(0,212,255,0.07) 0%, transparent 65%);
                pointer-events: none;
            "></div>
            <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
                <div style="
                    font-size: 2.6rem; line-height:1;
                    filter: drop-shadow(0 0 14px rgba(0,212,255,0.6));
                ">🪐</div>
                <div>
                    <div style="
                        font-family:'Space Grotesk',sans-serif;
                        font-size:0.68rem; font-weight:600;
                        letter-spacing:0.18em; text-transform:uppercase;
                        color:rgba(0,212,255,0.75); margin-bottom:0.25rem;
                    ">Scientific Computation Tool</div>
                    <h1 style="
                        font-family:'Space Grotesk',sans-serif;
                        font-size:1.7rem; font-weight:700; margin:0;
                        background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text; line-height:1.2;
                    ">Gravitational Force Calculator</h1>
                    <div style="
                        font-family:'JetBrains Mono',monospace;
                        font-size:0.72rem; color:rgba(255,255,255,0.5);
                        margin-top:0.3rem; letter-spacing:0.04em;
                    ">Developed by <span style="color:#00ff88; font-weight:600;">Swetabarnali Panda</span>
                    &nbsp;·&nbsp; F = G·m₁m₂/r²
                    &nbsp;·&nbsp; G = 6.67430 × 10⁻¹¹ m³kg⁻¹s⁻²</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_card(result: GravityResult) -> None:
    # Build display strings BEFORE the HTML block — no HTML tags inside {braces}
    mantissa_str = f"{result.mantissa:.6f}"
    exponent_str = str(result.exponent)
    force_plain  = f"{result.force_newtons:.6e}"

    html = (
        '<div style="'
        "background: linear-gradient(135deg, rgba(0,212,255,0.10) 0%, rgba(0,255,136,0.07) 100%);"
        "border: 1.5px solid rgba(0,212,255,0.30);"
        "border-radius: 14px;"
        "padding: 1.8rem 2rem;"
        "margin-bottom: 1.2rem;"
        "backdrop-filter: blur(10px);"
        'box-shadow: 0 0 40px rgba(0,212,255,0.12), inset 0 1px 0 rgba(255,255,255,0.06);">'

        '<div style="'
        "font-family:'Space Grotesk',sans-serif;"
        "font-size:0.65rem; font-weight:700;"
        "letter-spacing:0.20em; text-transform:uppercase;"
        'color:rgba(0,212,255,0.70); margin-bottom:0.6rem;">⚡ Computed Result</div>'

        '<div style="'
        "font-family:'JetBrains Mono',monospace;"
        "font-size:0.9rem; color:rgba(255,255,255,0.55);"
        'margin-bottom:0.4rem;">Gravitational Force</div>'

        '<div style="'
        "font-family:'JetBrains Mono',monospace;"
        "font-size:2.3rem; font-weight:600; line-height:1.15;"
        "background: linear-gradient(90deg, #00d4ff 20%, #00ff88 100%);"
        "-webkit-background-clip:text; -webkit-text-fill-color:transparent;"
        "background-clip:text;"
        'filter: drop-shadow(0 0 12px rgba(0,212,255,0.25));">'
        + mantissa_str + " &times; 10<sup>" + exponent_str + "</sup> N"
        + "</div>"

        '<div style="'
        "font-family:'JetBrains Mono',monospace;"
        "font-size:0.78rem; color:rgba(255,255,255,0.40);"
        'margin-top:0.4rem;">= '
        + force_plain + " Newtons (N)</div>"

        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_metric_grid(result: GravityResult) -> None:
    metrics = [
        ("Mass 1",   format_si(result.mass1_kg, "kg"), "#00d4ff"),
        ("Mass 2",   format_si(result.mass2_kg, "kg"), "#00d4ff"),
        ("Distance", format_si(result.distance_m, "m"), "#5ee7ff"),
        ("log₁₀(F)", f"{result.log10_force:.4f}", "#00ff88"),
        ("Equiv. Weight", format_si(result.equivalent_weight_kg, "kg"), "#72ffb8"),
        ("G Constant", "6.67430 × 10⁻¹¹", "#00d4ff"),
    ]
    cards_html = ""
    for label, value, color in metrics:
        cards_html += f"""
        <div style="
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(0,212,255,0.15);
            border-radius: 10px;
            padding: 1rem 1.1rem;
            backdrop-filter: blur(8px);
        ">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.62rem; font-weight:700;
                letter-spacing:0.15em; text-transform:uppercase;
                color:rgba(255,255,255,0.45); margin-bottom:0.5rem;
            ">{label}</div>
            <div style="
                font-family:'JetBrains Mono',monospace;
                font-size:0.95rem; font-weight:600;
                color:{color};
                word-break:break-all;
            ">{value}</div>
        </div>"""

    st.markdown(
        f"""
        <div style="
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.2rem;
        ">
            {cards_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_force_bar(result: GravityResult) -> None:
    """Visual log-scale force intensity indicator."""
    # Map log10 force to a 0–100 percentage (typical range: -50 to +50)
    log_val = result.log10_force
    pct = max(0.0, min(100.0, (log_val + 50) / 100 * 100))
    bar_color = (
        "#00ff88" if log_val > 10
        else "#00d4ff" if log_val > -5
        else "#5ee7ff"
    )
    st.markdown(
        f"""
        <div style="margin-bottom:1.4rem;">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.65rem; font-weight:700;
                letter-spacing:0.16em; text-transform:uppercase;
                color:rgba(255,255,255,0.45); margin-bottom:0.5rem;
            ">Force Magnitude (log₁₀ scale)</div>
            <div style="
                background:rgba(255,255,255,0.06);
                border-radius:999px;
                height:10px;
                border: 1px solid rgba(0,212,255,0.12);
                overflow:hidden;
            ">
                <div style="
                    width:{pct:.1f}%;
                    height:100%;
                    background: linear-gradient(90deg, #00d4ff, {bar_color});
                    border-radius:999px;
                    box-shadow: 0 0 12px {bar_color}88;
                    transition: width 0.6s ease;
                "></div>
            </div>
            <div style="
                display:flex; justify-content:space-between;
                font-family:'JetBrains Mono',monospace;
                font-size:0.6rem; color:rgba(255,255,255,0.28);
                margin-top:0.3rem;
            ">
                <span>10⁻⁵⁰ N</span>
                <span>log₁₀(F) = {log_val:.2f}</span>
                <span>10⁵⁰ N</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_educational_section() -> None:
    st.markdown(
        """
        <div style="
            background: rgba(0,212,255,0.04);
            border: 1px solid rgba(0,212,255,0.15);
            border-radius: 14px;
            padding: 1.6rem 1.8rem;
            margin-top:0.5rem;
        ">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.65rem; font-weight:700;
                letter-spacing:0.18em; text-transform:uppercase;
                color:rgba(0,212,255,0.70); margin-bottom:1rem;
            ">📐 Educational Insights</div>

            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.9rem; line-height:1.75;
                color:rgba(255,255,255,0.78);
            ">
                <p style="margin:0 0 0.9rem;">
                    <span style="color:#00d4ff; font-weight:600;">Newton's Law of Universal Gravitation</span>
                    states that every particle of matter attracts every other particle with a force proportional
                    to the product of their masses and inversely proportional to the square of the distance
                    between them.
                </p>

                <div style="
                    background:rgba(0,0,0,0.35);
                    border-left: 3px solid #00d4ff;
                    border-radius: 0 8px 8px 0;
                    padding: 0.8rem 1rem;
                    margin-bottom: 0.9rem;
                    font-family:'JetBrains Mono',monospace;
                    font-size:1.05rem;
                    color:#00ff88;
                    letter-spacing:0.03em;
                ">F = G · (m₁ · m₂) / r²</div>

                <table style="width:100%; border-collapse:collapse; margin-bottom:0.9rem;">
                    <tr style="border-bottom:1px solid rgba(0,212,255,0.12);">
                        <td style="padding:0.4rem 0.6rem; color:#5ee7ff; font-family:'JetBrains Mono',monospace; font-size:0.82rem; width:60px;"><b>F</b></td>
                        <td style="padding:0.4rem 0.6rem; font-size:0.82rem; color:rgba(255,255,255,0.70);">Gravitational force between two objects (Newtons, N)</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(0,212,255,0.12);">
                        <td style="padding:0.4rem 0.6rem; color:#5ee7ff; font-family:'JetBrains Mono',monospace; font-size:0.82rem;"><b>G</b></td>
                        <td style="padding:0.4rem 0.6rem; font-size:0.82rem; color:rgba(255,255,255,0.70);">Gravitational constant: 6.67430 × 10⁻¹¹ m³ kg⁻¹ s⁻² (NIST CODATA)</td>
                    </tr>
                    <tr style="border-bottom:1px solid rgba(0,212,255,0.12);">
                        <td style="padding:0.4rem 0.6rem; color:#5ee7ff; font-family:'JetBrains Mono',monospace; font-size:0.82rem;"><b>m₁, m₂</b></td>
                        <td style="padding:0.4rem 0.6rem; font-size:0.82rem; color:rgba(255,255,255,0.70);">Masses of the two objects (kilograms, kg)</td>
                    </tr>
                    <tr>
                        <td style="padding:0.4rem 0.6rem; color:#5ee7ff; font-family:'JetBrains Mono',monospace; font-size:0.82rem;"><b>r</b></td>
                        <td style="padding:0.4rem 0.6rem; font-size:0.82rem; color:rgba(255,255,255,0.70);">Distance between the centres of mass (metres, m)</td>
                    </tr>
                </table>

                <p style="margin:0 0 0.6rem;">
                    <span style="color:#00ff88; font-weight:600;">Inverse-Square Law:</span>
                    Doubling the distance <em>reduces</em> the force by a factor of 4.
                    This fundamental relationship explains orbital mechanics, tidal forces, and the
                    structure of the solar system.
                </p>
                <p style="margin:0; color:rgba(255,255,255,0.50); font-size:0.78rem; font-style:italic;">
                    Originally published by Isaac Newton in <em>Philosophiæ Naturalis Principia Mathematica</em> (1687).
                    This classical model is accurate for everyday scales; relativistic corrections
                    (General Relativity) become necessary near extremely massive or dense objects.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div style="
            margin-top: 2.5rem;
            border-top: 1px solid rgba(0,212,255,0.12);
            padding-top: 1rem;
            text-align: center;
        ">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.72rem;
                color:rgba(255,255,255,0.28);
                letter-spacing:0.06em;
            ">
                🪐 &nbsp;<span style="color:rgba(0,212,255,0.60);">Gravitational Force Calculator</span>
                &nbsp;|&nbsp; Developed by
                <span style="color:#00ff88; font-weight:600;"> Swetabarnali Panda</span>
                &nbsp;|&nbsp; G = 6.67430 × 10⁻¹¹ m³·kg⁻¹·s⁻² (NIST CODATA 2018)
                &nbsp;|&nbsp; Newton's Law of Universal Gravitation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str) -> None:
    st.markdown(
        f"""
        <div style="
            background:rgba(255,60,60,0.08);
            border:1px solid rgba(255,80,80,0.30);
            border-radius:10px;
            padding:1rem 1.2rem;
            color:#ff8888;
            font-family:'Space Grotesk',sans-serif;
            font-size:0.85rem;
        ">⚠️ &nbsp;{message}</div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
        <div style="
            background: rgba(255,255,255,0.03);
            border: 1px dashed rgba(0,212,255,0.20);
            border-radius: 14px;
            padding: 3rem 2rem;
            text-align: center;
            margin-bottom: 1.2rem;
        ">
            <div style="font-size:2.8rem; margin-bottom:0.8rem; opacity:0.5;">🌌</div>
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:0.95rem; color:rgba(255,255,255,0.35);
            ">Enter mass and distance values in the sidebar<br>to compute the gravitational force.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar() -> tuple[float, float, float]:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:1rem 0 0.5rem;">
                <div style="
                    font-family:'Space Grotesk',sans-serif;
                    font-size:0.65rem; font-weight:700;
                    letter-spacing:0.18em; text-transform:uppercase;
                    color:rgba(0,212,255,0.70); margin-bottom:0.25rem;
                ">⚙ Input Parameters</div>
                <div style="
                    height:2px;
                    background:linear-gradient(90deg,#00d4ff,transparent);
                    border-radius:2px; margin-bottom:1rem;
                "></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Mass 1 ──
        st.markdown(
            "<div style='font-family:\"Space Grotesk\",sans-serif; font-size:0.72rem; font-weight:700; "
            "letter-spacing:0.12em; text-transform:uppercase; color:#00d4ff; margin-bottom:0.3rem;'>"
            "MASS 1 (m₁)</div>",
            unsafe_allow_html=True,
        )
        preset1 = st.selectbox("Preset body (m₁)", list(PRESET_BODIES.keys()), key="preset1", label_visibility="collapsed")
        default_m1 = PRESET_BODIES[preset1] if preset1 != "Custom" else st.session_state.get("m1_val", 5.972e24)
        m1: float = st.number_input(
            "Mass 1 (kg)", min_value=0.0, value=default_m1,
            format="%e", key="m1", label_visibility="collapsed",
            help="Mass of object 1 in kilograms (kg)",
        )

        st.markdown("<div style='margin:0.6rem 0;'></div>", unsafe_allow_html=True)

        # ── Mass 2 ──
        st.markdown(
            "<div style='font-family:\"Space Grotesk\",sans-serif; font-size:0.72rem; font-weight:700; "
            "letter-spacing:0.12em; text-transform:uppercase; color:#00d4ff; margin-bottom:0.3rem;'>"
            "MASS 2 (m₂)</div>",
            unsafe_allow_html=True,
        )
        preset2 = st.selectbox("Preset body (m₂)", list(PRESET_BODIES.keys()), index=1, key="preset2", label_visibility="collapsed")
        default_m2 = PRESET_BODIES[preset2] if preset2 != "Custom" else st.session_state.get("m2_val", 7.342e22)
        m2: float = st.number_input(
            "Mass 2 (kg)", min_value=0.0, value=default_m2,
            format="%e", key="m2", label_visibility="collapsed",
            help="Mass of object 2 in kilograms (kg)",
        )

        st.markdown("<div style='margin:0.6rem 0;'></div>", unsafe_allow_html=True)

        # ── Distance ──
        st.markdown(
            "<div style='font-family:\"Space Grotesk\",sans-serif; font-size:0.72rem; font-weight:700; "
            "letter-spacing:0.12em; text-transform:uppercase; color:#5ee7ff; margin-bottom:0.3rem;'>"
            "DISTANCE (r)</div>",
            unsafe_allow_html=True,
        )
        preset_r = st.selectbox("Preset distance", list(PRESET_DISTANCES.keys()), key="preset_r", label_visibility="collapsed")
        default_r = PRESET_DISTANCES[preset_r] if preset_r != "Custom" else st.session_state.get("r_val", 3.844e8)
        r: float = st.number_input(
            "Distance (m)", min_value=0.0, value=default_r,
            format="%e", key="r", label_visibility="collapsed",
            help="Distance between the centres of mass (m)",
        )

        st.markdown("<div style='margin:1rem 0 0.4rem;'></div>", unsafe_allow_html=True)

        # ── Reset Button ──
        if st.button("↺  Reset to Defaults", key="reset_btn"):
            for key in ["m1", "m2", "r", "preset1", "preset2", "preset_r"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown(
            """
            <div style="
                margin-top:1.8rem;
                padding:0.8rem 1rem;
                background:rgba(0,212,255,0.05);
                border:1px solid rgba(0,212,255,0.12);
                border-radius:8px;
            ">
                <div style="
                    font-family:'JetBrains Mono',monospace;
                    font-size:0.65rem; color:rgba(0,212,255,0.60);
                    line-height:1.7;
                ">
                    G = 6.67430 × 10⁻¹¹<br>
                    m³ · kg⁻¹ · s⁻²<br>
                    <span style="color:rgba(255,255,255,0.30);">NIST CODATA 2018</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return float(m1), float(m2), float(r)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main() -> None:
    inject_css()
    render_header()

    m1, m2, r = render_sidebar()

    tab_result, tab_education = st.tabs(["🔬  Computation Result", "📐  Educational Insights"])

    with tab_result:
        result: Optional[GravityResult] = calculate_gravity(m1, m2, r)

        if result is None:
            render_empty_state()
            if m1 <= 0 or m2 <= 0:
                render_error("Both masses must be positive (> 0 kg).")
            if r <= 0:
                render_error("Distance must be positive (> 0 m). A zero distance implies a singularity.")
        else:
            render_result_card(result)
            render_force_bar(result)
            render_metric_grid(result)

            with st.expander("🔍  Full Precision Breakdown", expanded=False):
                G_str      = f"{G:.10e}"
                m1_str     = f"{result.mass1_kg:.10e}"
                m2_str     = f"{result.mass2_kg:.10e}"
                r_str      = f"{result.distance_m:.10e}"
                r2_str     = f"{result.distance_m**2:.10e}"
                G_s        = f"{G:.5e}"
                m1_s       = f"{result.mass1_kg:.5e}"
                m2_s       = f"{result.mass2_kg:.5e}"
                r_s        = f"{result.distance_m:.5e}"
                F_str      = f"{result.force_newtons:.10e}"
                wt_str     = f"{result.equivalent_weight_kg:.6e}"
                exp_html = (
                    '<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.82rem;'
                    ' line-height:2; color:rgba(255,255,255,0.70); padding:0.5rem 0;">'
                    '<div><span style="color:#00d4ff;">G</span>  = ' + G_str + ' m\u00b3\u00b7kg\u207b\u00b9\u00b7s\u207b\u00b2</div>'
                    '<div><span style="color:#00d4ff;">m\u2081</span> = ' + m1_str + ' kg</div>'
                    '<div><span style="color:#00d4ff;">m\u2082</span> = ' + m2_str + ' kg</div>'
                    '<div><span style="color:#5ee7ff;">r</span>  = ' + r_str + ' m</div>'
                    '<div><span style="color:#5ee7ff;">r\u00b2</span> = ' + r2_str + ' m\u00b2</div>'
                    '<div style="border-top:1px solid rgba(0,212,255,0.15); margin-top:0.4rem; padding-top:0.4rem;">'
                    '<span style="color:#00ff88;">F</span>  = G \u00b7 m\u2081 \u00b7 m\u2082 / r\u00b2<br>'
                    '&nbsp;&nbsp; = ' + G_s + ' \u00d7 ' + m1_s + ' \u00d7 ' + m2_s + ' / (' + r_s + ')\u00b2<br>'
                    '&nbsp;&nbsp; = <span style="color:#00ff88; font-weight:600;">' + F_str + ' N</span>'
                    '</div>'
                    '<div style="margin-top:0.4rem; color:rgba(255,255,255,0.40); font-size:0.72rem;">'
                    'Equivalent earth-surface weight \u2248 ' + wt_str + ' kg\u00b7g\u2080'
                    '</div></div>'
                )
                st.markdown(exp_html, unsafe_allow_html=True)

    with tab_education:
        render_educational_section()

    render_footer()


if __name__ == "__main__":
    main()