"""
theme.py
---------
Defines the Neon UI theme (Dark Neon + Light Neon variants) and injects the
CSS into every page so the whole app keeps a consistent neon look.
"""

import streamlit as st

# Neon accent palette - stays identical across both themes so the app always
# "feels" neon; only the background / text base colors change.
NEON_PINK = "#ff2fd6"
NEON_CYAN = "#00fff2"
NEON_PURPLE = "#b537f2"
NEON_GREEN = "#39ff14"
NEON_YELLOW = "#f9f871"


def _dark_theme_vars():
    return {
        "bg": "#0a0014",
        "bg_secondary": "#140026",
        "card_bg": "rgba(255, 255, 255, 0.04)",
        "text": "#f5f5ff",
        "text_muted": "#b8aee0",
        "border": NEON_PURPLE,
    }


def _light_theme_vars():
    return {
        "bg": "#f6f4ff",
        "bg_secondary": "#ffffff",
        "card_bg": "rgba(0, 0, 0, 0.03)",
        "text": "#180033",
        "text_muted": "#5b4a85",
        "border": NEON_PURPLE,
    }


def inject_css(theme: str = "dark"):
    """Inject the neon CSS. theme is either 'dark' or 'light'."""
    colors = _dark_theme_vars() if theme == "dark" else _light_theme_vars()

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;600;700&display=swap');

    :root {{
        --neon-pink: {NEON_PINK};
        --neon-cyan: {NEON_CYAN};
        --neon-purple: {NEON_PURPLE};
        --neon-green: {NEON_GREEN};
        --neon-yellow: {NEON_YELLOW};
        --bg: {colors['bg']};
        --bg-secondary: {colors['bg_secondary']};
        --card-bg: {colors['card_bg']};
        --text: {colors['text']};
        --text-muted: {colors['text_muted']};
        --border: {colors['border']};
    }}

    .stApp {{
        background: var(--bg);
        color: var(--text);
        font-family: 'Rajdhani', sans-serif;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Orbitron', sans-serif !important;
        color: var(--neon-cyan) !important;
        text-shadow: 0 0 8px var(--neon-cyan), 0 0 20px rgba(0,255,242,0.35);
        letter-spacing: 1px;
    }}

    p, span, label, li, div {{
        color: var(--text);
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: var(--bg-secondary);
        border-right: 2px solid var(--neon-purple);
        box-shadow: 4px 0 20px rgba(181, 55, 242, 0.25);
    }}

    /* Neon card container */
    .neon-card {{
        background: var(--card-bg);
        border: 1px solid var(--neon-purple);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 0 15px rgba(181, 55, 242, 0.35), inset 0 0 25px rgba(0,255,242,0.03);
    }}

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button {{
        background: linear-gradient(90deg, var(--neon-pink), var(--neon-purple), var(--neon-cyan));
        background-size: 200% auto;
        color: #0a0014 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 0 12px var(--neon-pink), 0 0 24px var(--neon-cyan);
        transition: 0.35s ease;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{
        background-position: right center;
        box-shadow: 0 0 20px var(--neon-cyan), 0 0 40px var(--neon-pink);
        transform: translateY(-2px);
        color: #0a0014 !important;
    }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: var(--bg-secondary) !important;
        color: var(--text) !important;
        border: 1px solid var(--neon-cyan) !important;
        border-radius: 8px !important;
        box-shadow: 0 0 6px rgba(0,255,242,0.25);
    }}

    /* Radio / toggle */
    .stRadio label, .stCheckbox label {{
        color: var(--text) !important;
    }}

    /* File uploader */
    section[data-testid="stFileUploaderDropzone"] {{
        background: var(--card-bg) !important;
        border: 2px dashed var(--neon-pink) !important;
        border-radius: 12px !important;
    }}

    /* Progress / bars */
    .stProgress > div > div {{
        background-image: linear-gradient(90deg, var(--neon-pink), var(--neon-cyan)) !important;
    }}

    /* Neon badge for skills */
    .neon-badge {{
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 999px;
        border: 1px solid var(--neon-green);
        color: var(--neon-green);
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        box-shadow: 0 0 8px rgba(57, 255, 20, 0.5);
        font-size: 0.85rem;
    }}

    /* Divider glow */
    hr {{
        border: none;
        height: 2px;
        background: linear-gradient(90deg, var(--neon-pink), var(--neon-cyan));
        box-shadow: 0 0 10px var(--neon-purple);
    }}

    /* Alerts (success / error / info) keep neon glow border */
    div[data-testid="stAlert"] {{
        border-radius: 10px;
        border: 1px solid var(--neon-cyan);
        box-shadow: 0 0 10px rgba(0,255,242,0.3);
    }}

    a {{
        color: var(--neon-cyan) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def neon_card_start():
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)


def neon_card_end():
    st.markdown("</div>", unsafe_allow_html=True)


def skill_badges(skills: list):
    if not skills:
        st.info("No matching skills detected.")
        return
    html = "".join(f'<span class="neon-badge">{s}</span>' for s in skills)
    st.markdown(html, unsafe_allow_html=True)
