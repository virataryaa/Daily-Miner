import warnings
from pathlib import Path

import pandas as pd
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

/* Sidebar title (hero text) */
.sb-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }

/* Certs report table */
.rpt { width: 100%; border-collapse: separate; border-spacing: 0; background: #ffffff; border: 1px solid #dfe3ee; border-radius: 12px; overflow: hidden; font-size: 13px; }
.rpt th { background: #0a2463; color: #ffffff; font-weight: 600; text-align: right; padding: 10px 14px; font-size: 12px; letter-spacing: .03em; }
.rpt th.l, .rpt td.l { text-align: left; }
.rpt th.gap { background: #0a2463; width: 18px; padding: 0; }
.rpt td { padding: 9px 14px; text-align: right; border-bottom: 1px solid #eef0f6; color: #1a1a2e; font-variant-numeric: tabular-nums; }
.rpt td.l { font-weight: 600; color: #0a2463; }
.rpt td.gap { border-bottom: 1px solid #eef0f6; padding: 0; }
.rpt tr:last-child td { border-bottom: none; }
.rpt tr.tot td { background: #f0f2f8; font-weight: 700; color: #0a2463; }
.rpt td.chg { width: 260px; padding: 6px 14px; }
.chgcell { display: flex; align-items: center; gap: 10px; }
.chgval { width: 52px; text-align: right; font-weight: 600; }
.chgbar { position: relative; flex: 1; height: 16px; }
.chgbar::before { content: ''; position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #c5cbdd; }
.chgbar i { position: absolute; top: 2px; bottom: 2px; border-radius: 3px; }
.chgbar i.up { left: 50%; background: #1f9d6f; }
.chgbar i.dn { right: 50%; background: #c94a4a; }
.pos { color: #1f9d6f; } .neg { color: #c94a4a; } .zero { color: #8a94a8; }
.share { color: #5a6688; }
</style>
""",
    unsafe_allow_html=True,
)


COMMODITIES = ["Coffee", "Cocoa", "Sugar"]

PORT_NAMES = {
    "ANT": "Antwerp", "LON": "London", "FEL": "Felixstowe", "LIV": "Liverpool",
    "AMS": "Amsterdam", "ROT": "Rotterdam", "HAM": "Hamburg", "BRE": "Bremen",
    "BAR": "Barcelona", "GEN": "Genoa", "TRI": "Trieste", "NOR": "Northern",
}


@st.cache_data(ttl=600)
def load_rc_certs() -> pd.DataFrame:
    df = pd.read_parquet(DB_DIR / "rc_certs.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


def fmt_int(v):
    return "-" if pd.isna(v) else f"{int(v):,}"


def certs_report_html(df: pd.DataFrame, grade: str = "VG") -> str:
    """Certs by port (latest) with day-over-day change as in-cell bars."""
    last, prev = df.iloc[-1], df.iloc[-2]
    tot_col = f"LRC-TOT-{grade}"
    ports = [p for p in PORT_NAMES if f"LRC-{p}-{grade}" in df.columns]
    ports = [p for p in ports if pd.notna(last[f"LRC-{p}-{grade}"]) and last[f"LRC-{p}-{grade}"] != 0
             or pd.notna(prev[f"LRC-{p}-{grade}"]) and prev[f"LRC-{p}-{grade}"] != 0]
    rows = []
    for p in ports:
        c = f"LRC-{p}-{grade}"
        now = 0 if pd.isna(last[c]) else int(last[c])
        was = 0 if pd.isna(prev[c]) else int(prev[c])
        rows.append((PORT_NAMES[p], now, now - was))
    rows.sort(key=lambda r: -r[1])
    tot_now, tot_chg = int(last[tot_col]), int(last[tot_col] - prev[tot_col])
    scale = max([abs(r[2]) for r in rows] + [1])

    def chg_cell(chg):
        cls = "pos" if chg > 0 else "neg" if chg < 0 else "zero"
        txt = f"{chg:+,}" if chg else "0"
        bar = ""
        if chg:
            w = abs(chg) / scale * 50
            bar = f"<i class='{'up' if chg > 0 else 'dn'}' style='width:{w:.1f}%'></i>"
        return (f"<div class='chgcell'><span class='chgval {cls}'>{txt}</span>"
                f"<div class='chgbar'>{bar}</div></div>")

    d_now, d_prev = last["Date"].strftime("%d %b %Y"), prev["Date"].strftime("%d %b")
    html = ["<table class='rpt'><thead><tr>",
            "<th class='l'>Port</th>",
            f"<th>Certs ({d_now})</th><th>Share</th><th class='gap'></th>",
            f"<th class='l'>Change vs {d_prev}</th></tr></thead><tbody>"]
    for name, now, chg in rows:
        share = f"{now / tot_now * 100:.1f}%" if tot_now else "-"
        html.append(f"<tr><td class='l'>{name}</td><td>{now:,}</td><td class='share'>{share}</td>"
                    f"<td class='gap'></td><td class='chg'>{chg_cell(chg)}</td></tr>")
    html.append(f"<tr class='tot'><td class='l'>Total</td><td>{tot_now:,}</td><td>100%</td>"
                f"<td class='gap'></td><td class='chg'>{chg_cell(tot_chg)}</td></tr>")
    html.append("</tbody></table>")
    return "".join(html)


with st.sidebar:
    st.markdown("<div class='sb-title'>Softs Daily Miner</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-label'>Commodity</div>", unsafe_allow_html=True)
    commodity = st.radio("Commodity", COMMODITIES, label_visibility="collapsed")

if commodity == "Coffee":
    tab_arabica, tab_robusta = st.tabs(["Arabica", "Robusta"])
    with tab_robusta:
        sub_certs, sub_grading, sub_both = st.tabs(["Certs", "Grading", "Certs & Grading"])
        with sub_certs:
            st.markdown(certs_report_html(load_rc_certs()), unsafe_allow_html=True)
