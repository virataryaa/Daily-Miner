import warnings
from pathlib import Path

import streamlit as st

warnings.filterwarnings("ignore")

APP_DIR = Path(__file__).resolve().parent
REPO_DIR = APP_DIR.parent
DB_DIR = REPO_DIR / "Database"

NAVY = "#0a2463"
TEAL = "#1f8a9c"
GREEN = "#1f9d6f"
RED = "#c94a4a"
AMBER = "#c98a1f"
GREY = "#8a94a8"

st.set_page_config(page_title="Softs Daily Miner", layout="wide")

# Strict light theme (same approach as the Cotton On-Call dashboard):
# colours hard-coded, .streamlit/config.toml pins base="light".
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: #fafafa !important;
}
[data-testid="stHeader"] { background: #fafafa !important; }
[data-testid="stSidebar"] {
    background: #f0f2f8 !important;
    border-right: 1px solid #dfe3ee;
}
h1, h2, h3, h4, h5, h6 { color: #0a2463 !important; }
body, .main { color: #1a1a2e; }
[data-testid="stSidebar"] { color: #1a1a2e; }

/* Pill / segmented-control tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #eef0f6;
    padding: 4px;
    border-radius: 999px;
    gap: 4px;
    display: inline-flex;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6688 !important;
    border-radius: 999px !important;
    padding: 8px 20px !important;
    font-weight: 600;
    border: none !important;
}
.stTabs [aria-selected="true"] { background: #0a2463 !important; color: #ffffff !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Radio as pill/segmented control (commodity selector) */
div[role="radiogroup"] { background: #eef0f6; padding: 4px; border-radius: 999px; gap: 2px; display: inline-flex; flex-wrap: wrap; }
div[role="radiogroup"] label { background: transparent !important; border-radius: 999px !important; padding: 4px 12px !important; margin: 0 !important; }
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display: none; }
div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 12px !important; color: #5a6688; }
div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

.stDataFrame { background: #ffffff; }
.card-desc { color: #5a6688; font-size: 0.82rem; margin-top: -6px; margin-bottom: 10px; }

/* Sidebar title (hero text) */
.sb-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.sb-caption { font-size: 11px; color: #7a86a8; margin-bottom: 16px; line-height: 1.4; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }
</style>
""",
    unsafe_allow_html=True,
)

COMMODITIES = ["Coffee", "Cocoa", "Sugar"]

with st.sidebar:
    st.markdown("<div class='sb-title'>Softs Daily Miner</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sb-caption'>Daily fundamentals: certified stocks and grading across the softs complex.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='sb-label'>Commodity</div>", unsafe_allow_html=True)
    commodity = st.radio("Commodity", COMMODITIES, label_visibility="collapsed")

if commodity == "Coffee":
    tab_arabica, tab_robusta = st.tabs(["Arabica", "Robusta"])
    with tab_arabica:
        st.markdown("<div class='card-desc'>Arabica (KC): coming next.</div>", unsafe_allow_html=True)
    with tab_robusta:
        st.markdown("<div class='card-desc'>Robusta (LRC): certified stocks and grading.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='card-desc'>{commodity}: not built yet.</div>", unsafe_allow_html=True)
