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
.stTabs [data-baseweb="tab"] p { font-size: 12px !important; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #5a6688 !important;
    border-radius: 999px !important;
    padding: 4px 13px !important;
    font-size: 12px !important;
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

/* Certs report table */
.rwrap { max-height: 78vh; overflow: auto; border: 1px solid #dfe3ee; border-radius: 12px; background: #ffffff; }
.rpt { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 11px; line-height: 1.25; font-variant-numeric: tabular-nums; }
.rpt thead th { position: sticky; top: 0; z-index: 2; background: #0a2463; color: #ffffff; font-weight: 600; padding: 4px 6px; font-size: 10.5px; text-align: right; white-space: nowrap; }
.rpt thead th small { display: block; font-weight: 500; font-size: 9px; color: #9fb0e0; margin-top: 1px; }
.rpt thead th.l { text-align: left; }
.rpt thead th.sec { background: #14357f; text-align: center; letter-spacing: .04em; }
.rpt thead th.gap { background: #fafafa; padding: 0; width: 8px; min-width: 8px; }
.rpt td { padding: 2px 6px; text-align: right; border-bottom: 1px solid #eef0f6; color: #1a1a2e; white-space: nowrap; }
.rpt td.d { text-align: left; color: #5a6688; font-weight: 500; }
.rpt td.tot { font-weight: 700; color: #0a2463; background: #f0f2f8; }
.rpt td.gap { padding: 0; background: #fafafa; border-bottom: none; }
.rpt td.cb { position: relative; font-weight: 700; min-width: 74px; text-align: center; background: #f6f7fb; }
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


PORT_ORDER = ["AMS", "ANT", "BAR", "BRE", "FEL", "GEN", "HAM", "LIV", "LON", "NOR", "ROT", "TRI"]
N_ROWS = 250


def certs_report_html(df: pd.DataFrame, grade: str = "VG", n_rows: int = N_ROWS) -> str:
    """Dates down the rows: stocks by port on the left, day-over-day change
    by port on the right (total change carries in-cell bars)."""
    cols = [f"LRC-{p}-{grade}" for p in PORT_ORDER]
    tot = f"LRC-TOT-{grade}"
    lv = df[["Date", tot] + cols].copy()
    chg = lv[[tot] + cols].fillna(0).diff()
    view = pd.concat([lv["Date"], lv[[tot] + cols], chg.add_suffix("_c")], axis=1).iloc[1:].tail(n_rows)
    view = view.iloc[::-1]
    scale = max(view[f"{tot}_c"].abs().max(), 1)
    latest = lv.iloc[-1]

    def num(v):
        return "" if pd.isna(v) or v == 0 else f"{int(v):,}"

    def sgn(v):
        if pd.isna(v) or v == 0:
            return ""
        return f"<span class='{'pos' if v > 0 else 'neg'}'>{int(v):+,}</span>"

    head = ["<div class='rwrap'><table class='rpt'><thead><tr>",
            "<th class='l'>Date</th><th>TOT</th>"]
    for p, c in zip(PORT_ORDER, cols):
        share = latest[c] / latest[tot] * 100 if latest[tot] and pd.notna(latest[c]) else 0
        head.append(f"<th>{p}<small>{share:.0f}%</small></th>")
    head.append("<th class='gap'></th><th class='l'>Date</th><th>TOT chg</th>")
    head += [f"<th>{p}</th>" for p in PORT_ORDER]
    head.append("</tr></thead><tbody>")

    body = []
    for _, r in view.iterrows():
        d = r["Date"].strftime("%d-%b-%y")
        t = r[f"{tot}_c"]
        bar = ""
        if t:
            w = abs(t) / scale * 50
            bar = f"<i class='{'up' if t > 0 else 'dn'}' style='width:{w:.1f}%'></i>"
        row = [f"<tr><td class='d'>{d}</td><td class='tot'>{num(r[tot])}</td>"]
        row += [f"<td>{num(r[c])}</td>" for c in cols]
        row.append("<td class='gap'></td>")
        row.append(f"<td class='d'>{d}</td><td class='cb'>{bar}<span>{sgn(t)}</span></td>")
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
            st.markdown(certs_report_html(load_rc_certs()), unsafe_allow_html=True)
