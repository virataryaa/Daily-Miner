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

st.set_page_config(page_title="Daily Miner", layout="wide")

# Strict light theme (same approach as the Cotton On-Call dashboard):
# colours hard-coded, .streamlit/config.toml pins base="light".
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
    background: #fafafa !important;
}
[data-testid="stHeader"] { background: #fafafa !important; }
.block-container { padding-top: 3.2rem !important; padding-bottom: 1rem !important; }
[data-testid="stSidebarUserContent"] { padding-top: 1rem !important; }
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
    padding: 3px;
    border-radius: 999px;
    gap: 2px;
    display: inline-flex;
}
.stTabs [data-baseweb="tab-list"] { margin-bottom: 6px; }
.stTabs [data-baseweb="tab"] p { font-size: 16px !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6688 !important;
    border-radius: 999px !important;
    padding: 8px 24px !important;
    font-size: 16px !important;
    min-height: 0 !important;
    height: auto !important;
    font-weight: 600;
    border: none !important;
}
.stTabs [aria-selected="true"] { background: #0a2463 !important; color: #ffffff !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Radio as pill/segmented control (commodity selector) */
div[role="radiogroup"] { background: #eef0f6; padding: 3px; border-radius: 999px; gap: 2px; display: inline-flex; flex-wrap: wrap; }
div[role="radiogroup"] label { background: transparent !important; border-radius: 999px !important; padding: 2px 10px !important; margin: 0 !important; }
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child { display: none; }
div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 11.5px !important; color: #5a6688; }
div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

.stDataFrame { background: #ffffff; }

/* Sidebar title (hero text) */
.sb-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }


/* Sub-tabs (nested) stay smaller than the main tabs */
.stTabs .stTabs [data-baseweb="tab-list"] { padding: 2px; }
.stTabs .stTabs [data-baseweb="tab"] { padding: 5px 15px !important; font-size: 14px !important; }
.stTabs .stTabs [data-baseweb="tab"] p { font-size: 14px !important; }

/* Commodity selector: larger stacked pills */
[data-testid="stSidebar"] div[role="radiogroup"] { flex-direction: column; align-items: stretch; width: 100%; border-radius: 22px; padding: 5px; gap: 3px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 8px 18px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }

/* Certs report table */
.rwrap { height: 60vh; overflow: auto; border: 1px solid #dfe3ee; border-radius: 12px; background: #ffffff; width: fit-content; max-width: 100%; }
.rpt { width: max-content; border-collapse: separate; border-spacing: 0; font-size: 11px; line-height: 1.25; font-variant-numeric: tabular-nums; }
.rpt thead th { position: sticky; z-index: 2; background: #0a2463; color: #ffffff; font-weight: 600; padding: 4px 9px; font-size: 10.5px; text-align: center; white-space: nowrap; }
.rpt thead tr.h1 th { top: 0; height: 24px; background: #14357f; letter-spacing: .05em; font-size: 11px; }
.rpt thead tr.h2 th { top: 24px; }
.rpt thead th.dt { top: 0; z-index: 3; }
.rpt .sep { border-left: 2px solid #0a2463; }
.rpt td { padding: 2px 9px; text-align: center; border-bottom: 1px solid #eef0f6; color: #1a1a2e; white-space: nowrap; }
.rpt td.d { color: #5a6688; font-weight: 500; }
.rpt td.tot { font-weight: 700; color: #0a2463; background: #f0f2f8; }
.rpt td.cb { position: relative; font-weight: 700; min-width: 74px; background: #f6f7fb; }
.rpt td.cb i { position: absolute; top: 2px; bottom: 2px; border-radius: 2px; opacity: .35; }
.rpt td.cb i.up { left: 50%; background: #1f9d6f; }
.rpt td.cb i.dn { right: 50%; background: #c94a4a; }
.rpt td.cb::before { content: ''; position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #c5cbdd; }
.rpt td.cb span { position: relative; z-index: 1; }
.rpt tr:hover td { background: #f3f6ff; }
.rpt tr:hover td.tot, .rpt tr:hover td.cb { background: #e6ebf7; }
.pos { color: #1f9d6f; } .neg { color: #c94a4a; }
</style>
""",
    unsafe_allow_html=True,
)


COMMODITIES = ["Coffee", "Cocoa", "Sugar"]



@st.cache_data(ttl=600)
def load_rc_certs() -> pd.DataFrame:
    df = pd.read_parquet(DB_DIR / "rc_certs.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


def fmt_int(v):
    return "-" if pd.isna(v) else f"{int(v):,}"


HISTORY_YEARS = 2
PORT_ORDER = ["AMS", "ANT", "BAR", "BRE", "FEL", "GEN", "HAM", "LIV", "LON", "NOR", "ROT", "TRI"]


def certs_report_html(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, grade: str = "VG") -> str:
    """One table, dates down the rows: 'Certs Per Ports' block on the left,
    'Daily Change Per Port' block on the right (total change carries bars)."""
    cols = [f"LRC-{p}-{grade}" for p in PORT_ORDER]
    tot = f"LRC-TOT-{grade}"
    lv = df[["Date", tot] + cols].copy()
    chg = lv[[tot] + cols].fillna(0).diff()
    view = pd.concat([lv["Date"], lv[[tot] + cols], chg.add_suffix("_c")], axis=1).iloc[1:]
    view = view[(view["Date"] >= start) & (view["Date"] <= end)].iloc[::-1]
    if view.empty:
        return "<div class='rwrap' style='padding:14px'>No data in the selected range.</div>"
    scale = max(view[f"{tot}_c"].abs().max(), 1)

    def num(v):
        return "" if pd.isna(v) or v == 0 else f"{int(v):,}"

    def sgn(v):
        if pd.isna(v) or v == 0:
            return ""
        return f"<span class='{'pos' if v > 0 else 'neg'}'>{int(v):+,}</span>"

    n = len(PORT_ORDER)
    head = ["<div class='rwrap'><table class='rpt'><thead>",
            "<tr class='h1'><th class='dt' rowspan='2'>Date</th>",
            f"<th colspan='{n + 1}'>Certs Per Ports</th>",
            f"<th colspan='{n + 1}' class='sep'>Daily Change Per Port</th></tr>",
            "<tr class='h2'><th>TOT</th>"]
    head += [f"<th>{p}</th>" for p in PORT_ORDER]
    head.append("<th class='sep'>TOT</th>")
    head += [f"<th>{p}</th>" for p in PORT_ORDER]
    head.append("</tr></thead><tbody>")

    body = []
    for _, r in view.iterrows():
        t = r[f"{tot}_c"]
        bar = ""
        if t:
            w = abs(t) / scale * 50
            bar = f"<i class='{'up' if t > 0 else 'dn'}' style='width:{w:.1f}%'></i>"
        row = [f"<tr><td class='d'>{r['Date'].strftime('%d-%b-%y')}</td><td class='tot'>{num(r[tot])}</td>"]
        row += [f"<td>{num(r[c])}</td>" for c in cols]
        row.append(f"<td class='cb sep'>{bar}<span>{sgn(t)}</span></td>")
        row += [f"<td>{sgn(r[c + '_c'])}</td>" for c in cols]
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


with st.sidebar:
    st.markdown("<div class='sb-title'>Daily Miner</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-label'>Commodity</div>", unsafe_allow_html=True)
    commodity = st.radio("Commodity", COMMODITIES, label_visibility="collapsed")

if commodity == "Coffee":
    tab_arabica, tab_robusta = st.tabs(["Arabica", "Robusta"])
    with tab_robusta:
        sub_certs, sub_grading, sub_both = st.tabs(["Certs", "Grading", "Certs & Grading"])
        with sub_certs:
            certs = load_rc_certs()
            end = certs["Date"].max()
            start = end - pd.DateOffset(years=HISTORY_YEARS)
            st.markdown(certs_report_html(certs, start, end), unsafe_allow_html=True)
