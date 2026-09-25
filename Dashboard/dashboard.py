import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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
/* Default selected-pill colour: a muted grey. Reserved for filter-type radios (History, Rolling
   window, Certs lag, Day/Week/Month, ...) and the third-level View tabs, so the visual weight
   fades as you go deeper - only the top navigation levels below keep their own bold colour. */
div[role="radiogroup"] label:has(input:checked) { background: #6b7690 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

/* Level 2 (Certs / Grading / Certs & Grading, and the Commodity sidebar list) stays bold navy -
   it's still primary navigation, not a filter. */
.st-key-rc_section_box div[role="radiogroup"] label:has(input:checked),
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }

/* Section / View pill radios: these replace st.tabs so only the picked branch runs each rerun
   (a real st.tabs renders every tab's body on every rerun; this radio does not). */
.st-key-rc_section_box div[role="radiogroup"] label { padding: 6px 16px !important; }
.st-key-rc_section_box div[role="radiogroup"] label p { font-size: 14px !important; }

/* Top-level commodity-section tabs (Arabica/Robusta): deep royal red instead of the navy every
   other pill uses, so this one level stands out as the primary switch. */
.st-key-coffee_section_box div[role="radiogroup"] label:has(input:checked) { background: #8e1b3a !important; }
.st-key-coffee_section_box div[role="radiogroup"] label { padding: 8px 34px !important; min-width: 90px; text-align: center; }
.st-key-coffee_section_box div[role="radiogroup"] label p { font-size: 15px !important; }

.st-key-rc_view_box div[role="radiogroup"] label, .st-key-rg_view_box div[role="radiogroup"] label, .st-key-cmb_pl_box div[role="radiogroup"] label { padding: 4px 13px !important; }
.st-key-rc_view_box div[role="radiogroup"] label p, .st-key-rg_view_box div[role="radiogroup"] label p, .st-key-cmb_pl_box div[role="radiogroup"] label p { font-size: 13px !important; }
.st-key-cmb_unit_box { display: flex; justify-content: flex-end; }
.st-key-cmb_unit_box div[role="radiogroup"] label { padding: 4px 13px !important; }
.st-key-cmb_unit_box div[role="radiogroup"] label p { font-size: 13px !important; }
.st-key-rcg_lag_box div[role="radiogroup"] { padding: 2px; }
.st-key-rcg_lag_box div[role="radiogroup"] label { padding: 1px 8px !important; }
.st-key-rcg_lag_box div[role="radiogroup"] label p { font-size: 10px !important; }

.stDataFrame { background: #ffffff; }

/* Sidebar title (hero text) */
.sb-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.5rem; font-weight: 600; color: #0a2463; margin-bottom: 2px; }
.sb-label { font-size: 11px; color: #7a86a8; text-transform: uppercase; letter-spacing: .06em; margin: 6px 0 4px; }


/* Sub-tabs (nested) stay smaller than the main tabs */
.stTabs .stTabs .stTabs [data-baseweb="tab"], .stTabs .stTabs .stTabs [data-baseweb="tab"] p { font-size: 12.5px !important; }
.stTabs .stTabs [data-baseweb="tab-list"] { padding: 2px; }
.stTabs .stTabs [data-baseweb="tab"] { padding: 5px 15px !important; font-size: 14px !important; }
.stTabs .stTabs [data-baseweb="tab"] p { font-size: 14px !important; }

/* Commodity selector: larger stacked pills */
[data-testid="stSidebar"] div[role="radiogroup"] { flex-direction: column; align-items: stretch; width: 100%; border-radius: 22px; padding: 5px; gap: 3px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 8px 18px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-size: 15px !important; }

/* Multiselect: navy tags, white dropdown */
span[data-baseweb="tag"], span[data-baseweb="tag"] div, span[data-baseweb="tag"] span { background-color: #0a2463 !important; color: #ffffff !important; }
span[data-baseweb="tag"] svg { fill: #ffffff !important; }
[data-baseweb="popover"] [data-baseweb="menu"] { background: #ffffff !important; }
[data-baseweb="popover"] [data-baseweb="menu"] li, [data-baseweb="popover"] [data-baseweb="menu"] li * { color: #1a1a2e !important; }
[data-baseweb="select"] > div { background: #ffffff !important; color: #1a1a2e !important; }

/* One-sided data bars (grading totals, monthly matrix) */
.rpt td.cbl { position: relative; font-weight: 700; color: #0a2463; background: #f0f2f8; min-width: 62px; }
.rpt td.cbl i { position: absolute; left: 0; top: 2px; bottom: 2px; background: #0a2463; opacity: .16; border-radius: 2px; }
.rpt td.cbl span { position: relative; z-index: 1; }

/* Certs report table */
.rwrap { height: 60vh; overflow: auto; border: 1px solid #dfe3ee; border-radius: 12px; background: #ffffff; width: fit-content; max-width: 100%; }
.rpt { width: max-content; border-collapse: separate; border-spacing: 0; font-size: 11px; line-height: 1.25; font-variant-numeric: tabular-nums; }
.rpt thead th { position: sticky; z-index: 2; background: #0a2463; color: #ffffff; font-weight: 600; padding: 4px 9px; font-size: 10.5px; text-align: center; white-space: nowrap; }
.rpt thead tr.h1 th { top: 0; height: 24px; background: #14357f; letter-spacing: .05em; font-size: 11px; }
.rpt thead tr.h2 th { top: 24px; height: 22px; background: #0f2c70; }
.rpt thead tr.h3 th { top: 46px; height: 22px; }
.rpt thead th.gs { border-left: 1px solid rgba(255,255,255,.28); }
.rpt.static thead th { position: static; }  /* small non-scrolling tables: avoid a sticky-header/first-row overlap quirk */
/* KC matrices: fixed column widths so the Change and Latest tables line up when shown side by side */
.rpt.kcmx { font-size: 10.5px; }
.rpt.kcmx th, .rpt.kcmx td { padding: 3px 6px; }

/* Compact date pickers for the Older/Latest Date row */
.st-key-ar_dates_custom_box input { padding: 4px 8px !important; font-size: 12px !important; height: auto !important; }
.st-key-ar_dates_custom_box [data-baseweb="base-input"], .st-key-ar_dates_custom_box [data-baseweb="input"] { min-height: 0 !important; }

.rpt thead th.certs-hdr { background: #9c6a17 !important; }
.rpt td.gs { border-left: 1px solid #dfe3ee; }
.rpt thead th.dt { top: 0; z-index: 3; }
.rpt thead th.l, .rpt td.l { text-align: left; }
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
.sec { font-size: 11px; font-weight: 700; color: #7a86a8; text-transform: uppercase; letter-spacing: .09em; margin: 22px 0 2px; padding-bottom: 5px; border-bottom: 1px solid #dfe3ee; }
.mt { font-size: 14px; font-weight: 600; color: #0a2463; margin: 18px 0 6px; }
.rpt td.yr { font-weight: 700; color: #0a2463; background: #f0f2f8; }
.rpt td.na { background: #f6f7fb; }
.rpt.mx { font-size: 11px; }
.rpt.mx td { padding: 3px 6px; }
.rpt.mx thead th { top: 0 !important; padding: 4px 6px; font-size: 10.5px; }
.rpt.mx td.cb { min-width: 58px; }
.rpt.cmp { font-size: 10px; }
.rpt.cmp td { padding: 1px 5px; }
.rpt.cmp thead th { padding: 3px 5px; font-size: 9.5px; }
.rpt.cmp td.cbl, .rpt.cmp td.cb { min-width: 46px; }
.rpt.tiny { font-size: 9.5px; }
.rpt.tiny td { padding: 1px 4px; min-width: 0; }
.rpt.tiny thead th { padding: 3px 4px; font-size: 9px; letter-spacing: 0; }
.rpt.tiny td.cbl, .rpt.tiny td.cb { min-width: 36px; }
.rpt.tiny td.pr, .rpt.tiny th.pr { font-size: 8px; padding: 1px 2px; min-width: 0; letter-spacing: 0; }
.rpt.big { font-size: 13.5px; }
.rpt.big td { padding: 8px 14px; min-width: 62px; }
.rpt.big thead th { padding: 8px 14px; font-size: 12.5px; top: 0 !important; }
.mt.side { margin-top: 30px; }
</style>
""",
    unsafe_allow_html=True,
)


COMMODITIES = ["Coffee", "Cocoa", "Sugar"]



@st.cache_data(ttl=600)
def load_rc_certs() -> pd.DataFrame:
    df = pd.read_parquet(DB_DIR / "Main" / "RC" / "rc_certs.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


@st.cache_data(ttl=600)
def load_kc_certs() -> pd.DataFrame:
    df = pd.read_parquet(DB_DIR / "Main" / "KC" / "kc_certs.parquet")
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


KC_ORIGIN_NAMES = {
    "BRZ": "Brazil", "BUR": "Burundi", "COL": "Colombia", "COS": "Costa Rica", "ELS": "El Salvador",
    "HON": "Honduras", "IND": "India", "MEX": "Mexico", "NIC": "Nicaragua", "PAN": "Papua New Guinea",
    "PER": "Peru", "RWA": "Rwanda", "TAN": "Tanzania", "UGA": "Uganda", "VEN": "Venezuela", "GUA": "Guatemala",
}
KC_PORT_NAMES = {"AN": "ANT", "BA": "BAR", "HA": "HA/BR", "HO": "HOU", "MI": "MIAMI", "NO": "NOLA", "NY": "NY"}
KC_GRADE_PORTS = ["AN", "HA", "HO", "MI", "NO", "NY"]


def kc_change_matrix_html(df: pd.DataFrame, older: pd.Timestamp, latest: pd.Timestamp) -> str:
    """Origin x port matrix of the change in certified stocks between two dates (bags), with a
    Total row (from the source's own KC-TOT-{port} column) and Total column (KC-{origin}-TOT)."""
    ro = df[df["Date"] == older]
    rl = df[df["Date"] == latest]
    if ro.empty or rl.empty:
        return "<div class='rwrap' style='padding:14px'>No data for one of the selected dates.</div>"
    ro, rl = ro.iloc[0], rl.iloc[0]
    origins, ports = list(KC_ORIGIN_NAMES), list(KC_PORT_NAMES)

    def d(o, p):
        c = f"KC-{o}-{p}"
        a, b = ro.get(c), rl.get(c)
        a = 0 if pd.isna(a) else a
        b = 0 if pd.isna(b) else b
        return float(b - a)

    grid = {(o, p): d(o, p) for o in origins for p in ports}
    row_tot = {o: d(o, "TOT") for o in origins}
    col_tot = {p: d("TOT", p) for p in ports}
    grand = d("TOT", "TOT")
    scale = max([abs(v) for v in grid.values()] + [1.0])

    def scell(v, sep=False):
        cls = "sep" if sep else ""
        if v == 0:
            return f"<td class='{cls}'></td>"
        alpha = min(abs(v) / scale, 1.0) * 0.85
        color = "31,157,111" if v > 0 else "201,74,74"
        return f"<td class='{cls}' style='background:rgba({color},{alpha:.2f})'>{v:+,.0f}</td>"

    def totcell(v, sep=False):
        cls = "tot" + (" sep" if sep else "")
        if v == 0:
            return f"<td class='{cls}'>0</td>"
        cls2 = "pos" if v > 0 else "neg"
        return f"<td class='{cls}'><span class='{cls2}'>{v:+,.0f}</span></td>"

    head = kc_matrix_head(ports, ["Total"])
    body = []
    for o in origins:
        row = [f"<tr><td class='d l'>{KC_ORIGIN_NAMES[o]}</td>"]
        row += [_kc_gs(scell(grid[(o, p)]), p) for p in ports]
        row.append(totcell(row_tot[o], sep=True))
        row.append("</tr>")
        body.append("".join(row))
    body.append("<tr><td class='d l tot'>Total</td>" + "".join(_kc_gs(totcell(col_tot[p]), p) for p in ports) +
               totcell(grand, sep=True) + "</tr>")
    return "".join(head) + "".join(body) + "</tbody></table></div>"


def kc_latest_matrix_html(df: pd.DataFrame, latest: pd.Timestamp) -> str:
    """Origin x port latest certified stocks (bags), green heat-map on one shared scale, with
    Total row/column, an Origin % (of grand total) column and a Port % row."""
    r = df[df["Date"] == latest]
    if r.empty:
        return "<div class='rwrap' style='padding:14px'>No data for the selected date.</div>"
    r = r.iloc[0]
    origins, ports = list(KC_ORIGIN_NAMES), list(KC_PORT_NAMES)

    def v(o, p):
        x = r.get(f"KC-{o}-{p}")
        return 0.0 if pd.isna(x) else float(x)

    grid = {(o, p): v(o, p) for o in origins for p in ports}
    row_tot = {o: v(o, "TOT") for o in origins}
    col_tot = {p: v("TOT", p) for p in ports}
    grand = v("TOT", "TOT")
    scale = max(list(grid.values()) + [1.0])
    pmax = max([row_tot[o] / grand * 100 if grand else 0 for o in origins] +
               [col_tot[p] / grand * 100 if grand else 0 for p in ports] + [1.0])

    def cell(x, sep=False):
        cls = "sep" if sep else ""
        if x == 0:
            return f"<td class='{cls}'></td>"
        alpha = min(x / scale, 1.0) * 0.85
        return f"<td class='{cls}' style='background:rgba(31,157,111,{alpha:.2f})'>{x:,.0f}</td>"

    def totcell(x, sep=False):
        cls = "tot" + (" sep" if sep else "")
        return f"<td class='{cls}'>{x:,.0f}</td>"

    def pctcell(x, sep=False):
        cls = "sep" if sep else ""
        pct = x / grand * 100 if grand else 0
        if pct == 0:
            return f"<td class='{cls}'></td>"
        alpha = min(pct / pmax, 1.0) * 0.85
        return f"<td class='{cls}' style='background:rgba(31,157,111,{alpha:.2f})'>{pct:.0f}%</td>"

    head = kc_matrix_head(ports, ["Total", "Origin %"])
    body = []
    for o in origins:
        row = [f"<tr><td class='d l'>{KC_ORIGIN_NAMES[o]}</td>"]
        row += [_kc_gs(cell(grid[(o, p)]), p) for p in ports]
        row.append(totcell(row_tot[o], sep=True))
        row.append(pctcell(row_tot[o], sep=True))
        row.append("</tr>")
        body.append("".join(row))
    body.append("<tr><td class='d l tot'>Total</td>" + "".join(_kc_gs(totcell(col_tot[p]), p) for p in ports) +
               totcell(grand, sep=True) + "<td class='sep'></td></tr>")
    body.append("<tr><td class='d l tot'>Port %</td>" +
               "".join(_kc_gs(pctcell(col_tot[p]), p) for p in ports) + "<td class='sep'></td><td class='sep'></td></tr>")
    return "".join(head) + "".join(body) + "</tbody></table></div>"


def fmt_int(v):
    return "-" if pd.isna(v) else f"{int(v):,}"


# ------------------------------------------------------------------ KC (Arabica) visuals
KC_PORT_COLORS = {"AN": NAVY, "NY": TEAL, "MI": AMBER, "HO": "#9b6bb3", "NO": RED, "BA": GREEN, "HA": "#6b7fb5"}

# 16-Nov to 30-Dec 2011: every KC origin AND port RIC except KC-TOT-AN went NaN in LSEG's own
# history for this ~6-week window, while KC-TOT-TOT kept updating fine - a one-off archive hole,
# not a recurring glitch. Forward-filling something that long would be fabricating data, so the
# origin/port breakdown charts (not the Total Certs one, which is unaffected) start after it clears.
KC_BREAKDOWN_START = "2012-01-01"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_major_ports(df: pd.DataFrame, min_share: float = 0.01) -> list:
    tot = df["KC-TOT-TOT"].astype(float).mean()
    if not tot:
        return []
    share = {p: df[f"KC-TOT-{p}"].astype(float).mean() / tot for p in KC_PORT_NAMES}
    return [p for p in sorted(share, key=lambda p: -(0 if pd.isna(share[p]) else share[p]))
            if pd.notna(share[p]) and share[p] >= min_share]


@st.cache_data(ttl=3600, show_spinner=False)
def kc_origin_palette(df: pd.DataFrame) -> tuple:
    """(origins biggest-first by average total stock, colours). Top 5 keep strong app colours,
    every smaller origin gets a lighter tint that fades with rank."""
    avg = {o: df[f"KC-{o}-TOT"].astype(float).mean() for o in KC_ORIGIN_NAMES}
    order = sorted(KC_ORIGIN_NAMES, key=lambda o: -(avg[o] or 0))
    strong = [NAVY, TEAL, AMBER, RED, GREEN]
    soft = ["#9b6bb3", "#6b7fb5", "#c0722c", "#4a5578", "#8fa3d1", "#b58f4a", GREY, "#c5cbdd"]
    colors = {}
    for i, o in enumerate(order):
        colors[o] = strong[i] if i < len(strong) else tint(soft[(i - 5) % len(soft)], max(0.75 - 0.06 * (i - 5), 0.32))
    return order, colors


@st.cache_data(ttl=3600, show_spinner=False)
def kc_total_certs_fig(df: pd.DataFrame) -> go.Figure:
    s = df[["Date", "KC-TOT-TOT"]].dropna()
    fig = go.Figure(go.Scatter(
        x=s["Date"], y=s["KC-TOT-TOT"], mode="lines", line=dict(color=NAVY, width=2),
        fill="tozeroy", fillcolor="rgba(10,36,99,0.07)", hovertemplate="%{y:,.0f}<extra></extra>"))
    return chart_layout(fig, "Total Certs")


@st.cache_data(ttl=3600, show_spinner=False)
def kc_ports_certs_fig(df: pd.DataFrame) -> go.Figure:
    """Stacked area of certs per port (biggest at the bottom); minor ports pooled into Other."""
    df = df[df["Date"] >= KC_BREAKDOWN_START]
    majors = kc_major_ports(df)
    minors = [p for p in KC_PORT_NAMES if p not in majors]
    fig = go.Figure()
    for p in majors:
        # a few RICs go NaN for an isolated day here and there (a holiday the feed skipped);
        # forward-fill short gaps rather than dropping to 0, or the stack shows a false one-day dip
        y = df[f"KC-TOT-{p}"].astype(float).ffill(limit=5).fillna(0)
        fig.add_trace(go.Scatter(
            x=df["Date"], y=y, mode="lines", name=KC_PORT_NAMES[p],
            stackgroup="one", line=dict(width=0.6, color=KC_PORT_COLORS.get(p, GREY)),
            fillcolor=KC_PORT_COLORS.get(p, GREY),
            hovertemplate="%{y:,.0f}<extra>" + KC_PORT_NAMES[p] + "</extra>"))
    if minors:
        other = df[[f"KC-TOT-{p}" for p in minors]].astype(float).ffill(limit=5).fillna(0).sum(axis=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=other, mode="lines", name="Other", stackgroup="one",
                                 line=dict(width=0.6, color="#c5cbdd"), fillcolor="#c5cbdd",
                                 hovertemplate="%{y:,.0f}<extra>Other</extra>"))
    return chart_layout(fig, "Certs Per Port")


@st.cache_data(ttl=3600, show_spinner=False)
def kc_origin_mix_fig(df: pd.DataFrame, show_all: bool = False, top_n: int = 5) -> go.Figure:
    """Stacked area of certs per origin. Aggregated to Top-N + Other by default; the 'show all
    origins' toggle expands to all 16."""
    df = df[df["Date"] >= KC_BREAKDOWN_START]
    order, colors = kc_origin_palette(df)
    shown = order if show_all else order[:top_n]
    minors = [] if show_all else order[top_n:]
    fig = go.Figure()
    for o in shown:
        # same isolated-holiday-NaN issue as the port chart: forward-fill short gaps, don't drop to 0
        y = df[f"KC-{o}-TOT"].astype(float).ffill(limit=5).fillna(0)
        fig.add_trace(go.Scatter(
            x=df["Date"], y=y, mode="lines", name=KC_ORIGIN_NAMES[o],
            stackgroup="one", line=dict(width=0.6, color=colors[o]), fillcolor=colors[o],
            hovertemplate="%{y:,.0f}<extra>" + KC_ORIGIN_NAMES[o] + "</extra>"))
    if minors:
        other = df[[f"KC-{o}-TOT" for o in minors]].astype(float).ffill(limit=5).fillna(0).sum(axis=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=other, mode="lines", name="Other", stackgroup="one",
                                 line=dict(width=0.6, color="#c5cbdd"), fillcolor="#c5cbdd",
                                 hovertemplate="%{y:,.0f}<extra>Other</extra>"))
    title = "Certs Per Origin" + ("" if show_all else f" (Top {top_n} + Other)")
    return chart_layout(fig, title)


@st.cache_data(ttl=3600, show_spinner=False)
def kc_origin_share_fig(df: pd.DataFrame, show_all: bool = False, top_n: int = 5) -> go.Figure:
    """Each origin's share of total certs (%) over time, as lines. Same Top-N + Other aggregation
    as the mix chart above it."""
    df = df[df["Date"] >= KC_BREAKDOWN_START]
    order, colors = kc_origin_palette(df)
    shown = order if show_all else order[:top_n]
    minors = [] if show_all else order[top_n:]
    tot = df["KC-TOT-TOT"].astype(float).where(lambda v: v > 0)
    fig = go.Figure()
    for o in shown:
        share = (df[f"KC-{o}-TOT"].astype(float).ffill(limit=5) / tot * 100)
        ok = share.notna()
        fig.add_trace(go.Scatter(x=df["Date"][ok], y=share[ok], mode="lines", name=KC_ORIGIN_NAMES[o],
                                 line=dict(color=colors[o], width=2.0),
                                 hovertemplate="%{y:.1f}%<extra>" + KC_ORIGIN_NAMES[o] + "</extra>"))
    if minors:
        other = df[[f"KC-{o}-TOT" for o in minors]].astype(float).ffill(limit=5).fillna(0).sum(axis=1) / tot * 100
        fig.add_trace(go.Scatter(x=df["Date"], y=other, mode="lines", name="Other",
                                 line=dict(color="#c5cbdd", width=2.0), hovertemplate="%{y:.1f}%<extra>Other</extra>"))
    chart_layout(fig, "Origin Share of Total", height=360)
    fig.update_layout(yaxis=dict(ticksuffix="%", range=[0, 100]))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def kc_latest_breakup_fig(df: pd.DataFrame, top_n: int = 5) -> go.Figure:
    """Donut of the latest breakup by origin, Top-N + Other (same aggregation as the mix chart)."""
    order, colors = kc_origin_palette(df)
    last = df.iloc[-1]
    tot = float(last["KC-TOT-TOT"])
    vals = {o: float(last[f"KC-{o}-TOT"]) for o in order
            if pd.notna(last[f"KC-{o}-TOT"]) and last[f"KC-{o}-TOT"] > 0}
    shown = [o for o in order if o in vals][:top_n]
    rest = sum(v for o, v in vals.items() if o not in shown)
    labels = [KC_ORIGIN_NAMES[o] for o in shown]
    amounts = [vals[o] for o in shown]
    cols = [colors[o] for o in shown]
    if rest > 0:
        labels.append("Other")
        amounts.append(rest)
        cols.append("#c5cbdd")
    fig = go.Figure(go.Pie(
        labels=labels, values=amounts, hole=0.66, sort=False, direction="clockwise",
        marker=dict(colors=cols, line=dict(color="#fafafa", width=3)),
        textinfo="label+percent", textposition="outside", textfont=dict(size=12, color="#1a1a2e"),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>", showlegend=False))
    chart_layout(fig, f"Latest Breakup ({last['Date'].strftime('%d %b %Y')})", 360)
    fig.update_layout(
        margin=dict(t=44, b=20, l=40, r=40),
        annotations=[dict(text=f"<b>{tot:,.0f}</b><br><span style='font-size:11px;color:#7a86a8'>total</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=22, color=NAVY))])
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def kc_rolling_origins_fig(df: pd.DataFrame, origins: list, n: int, start: pd.Timestamp,
                          end: pd.Timestamp) -> go.Figure:
    """Rolling n-observation change, one line per chosen origin."""
    _, colors = kc_origin_palette(df)
    fig = go.Figure()
    for o in origins:
        r = df.set_index("Date")[f"KC-{o}-TOT"].dropna().astype(float).diff(n).dropna()
        r = r[(r.index >= start) & (r.index <= end)]
        fig.add_trace(go.Scatter(x=r.index, y=r.values, mode="lines", name=KC_ORIGIN_NAMES[o],
                                 line=dict(color=colors.get(o, GREY), width=2.0),
                                 hovertemplate="%{y:+,.0f}<extra>" + KC_ORIGIN_NAMES[o] + "</extra>"))
    fig.add_hline(y=0, line=dict(color="#c5cbdd", width=1))
    label = ", ".join(KC_ORIGIN_NAMES[o] for o in origins) if origins else "no origin selected"
    chart_layout(fig, f"Rolling Change: {label} ({n}d)", height=360)
    fig.update_layout(yaxis=dict(tickformat="+,"), showlegend=len(origins) > 1)
    return fig




HISTORY_YEARS = 2
PORT_ORDER = ["AMS", "ANT", "BAR", "BRE", "FEL", "GEN", "HAM", "LIV", "LON", "NOR", "ROT", "TRI"]


COUNTRY_PORTS = {
    "Belgium": ["ANT"],
    "UK": ["LON", "FEL", "LIV"],
    "Netherlands": ["AMS", "ROT"],
    "Germany": ["HAM", "BRE"],
    "Spain": ["BAR"],
    "Italy": ["GEN", "TRI"],
    "USA": ["NOR"],
}


@st.cache_data(ttl=3600, show_spinner=False)
def countries_by_stock(df: pd.DataFrame, grade: str = "VG") -> list:
    """[(country, [ports])] with the biggest country first today, and the
    biggest port first inside each country."""
    last = df.iloc[-1]

    def stock(p):
        v = last[f"LRC-{p}-{grade}"]
        return 0 if pd.isna(v) else v

    out = [(c, sorted(ports, key=lambda p: -stock(p))) for c, ports in COUNTRY_PORTS.items()]
    return sorted(out, key=lambda cp: -sum(stock(p) for p in cp[1]))


@st.cache_data(ttl=3600, show_spinner=False)
def certs_report_html(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp,
                      grade: str = "VG", height: str = "60vh") -> str:
    """One table, dates down the rows. Columns are grouped Country > Port.
    Left block = certs, right block = day-over-day change (total change carries bars)."""
    tot = f"LRC-TOT-{grade}"
    groups = countries_by_stock(df, grade)
    ports = [p for _, ps in groups for p in ps]
    cols = [f"LRC-{p}-{grade}" for p in ports]
    lv = df[["Date", tot] + cols].copy()
    chg = lv[[tot] + cols].fillna(0).diff()
    view = pd.concat([lv["Date"], lv[[tot] + cols], chg.add_suffix("_c")], axis=1).iloc[1:]
    view = view[(view["Date"] >= start) & (view["Date"] <= end)].iloc[::-1]
    if view.empty:
        return "<div class='rwrap' style='padding:14px'>No data in the selected range.</div>"
    scale = max(view[f"{tot}_c"].abs().max(), 1)
    starts = set()
    i = 0
    for _, ps in groups:
        starts.add(i)
        i += len(ps)

    def num(v):
        return "" if pd.isna(v) or v == 0 else f"{int(v):,}"

    def sgn(v):
        if pd.isna(v) or v == 0:
            return ""
        return f"<span class='{'pos' if v > 0 else 'neg'}'>{int(v):+,}</span>"

    n = len(ports)
    head = [f"<div class='rwrap' style='height:{height}'><table class='rpt'><thead>",
            "<tr class='h1'><th class='dt' rowspan='3'>Date</th>",
            f"<th colspan='{n + 1}'>Certs Per Ports</th>",
            f"<th colspan='{n + 1}' class='sep'>Daily Change Per Port</th></tr>",
            "<tr class='h2'><th rowspan='2'>TOT</th>"]
    head += [f"<th colspan='{len(ps)}' class='gs'>{c}</th>" for c, ps in groups]
    head.append("<th rowspan='2' class='sep'>TOT</th>")
    head += [f"<th colspan='{len(ps)}' class='gs'>{c}</th>" for c, ps in groups]
    head.append("</tr><tr class='h3'>")
    head += [f"<th{' class=gs' if k in starts else ''}>{p}</th>" for k, p in enumerate(ports)]
    head += [f"<th{' class=gs' if k in starts else ''}>{p}</th>" for k, p in enumerate(ports)]
    head.append("</tr></thead><tbody>")

    body = []
    for _, r in view.iterrows():
        t = r[f"{tot}_c"]
        bar = ""
        if t:
            w = abs(t) / scale * 50
            bar = f"<i class='{'up' if t > 0 else 'dn'}' style='width:{w:.1f}%'></i>"
        row = [f"<tr><td class='d'>{r['Date'].strftime('%d-%b-%y')}</td><td class='tot'>{num(r[tot])}</td>"]
        row += [f"<td{' class=gs' if k in starts else ''}>{num(r[c])}</td>" for k, c in enumerate(cols)]
        row.append(f"<td class='cb sep'>{bar}<span>{sgn(t)}</span></td>")
        row += [f"<td{' class=gs' if k in starts else ''}>{sgn(r[c + '_c'])}</td>" for k, c in enumerate(cols)]
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


PORT_COLORS = {
    "ANT": NAVY, "LON": TEAL, "TRI": AMBER, "FEL": "#6b7fb5", "AMS": "#9b6bb3", "ROT": "#c94a4a",
    "LEH": "#6c8ebf", "HAM": "#1f9d6f", "BAR": "#c0722c", "BRE": "#4a5578", "GEN": "#8fa3d1", "LIV": "#b58f4a", "NOR": GREY,
}


def chart_layout(fig, title, height=360):
    fig.update_layout(
        template="plotly_white", height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e", size=12),
        title=dict(text=title, font=dict(size=14, color=NAVY), x=0, xanchor="left"),
        margin=dict(t=40, b=8, l=8, r=8), hovermode="x unified",
        legend=dict(orientation="h", y=-0.12, x=0, xanchor="left", yanchor="top",
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor="rgba(10,36,99,0.06)", color="#4a5578", showline=True, linecolor="#dfe3ee"),
        yaxis=dict(gridcolor="rgba(10,36,99,0.08)", color="#4a5578", tickformat=",", zeroline=False),
    )
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def total_certs_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    s = df[["Date", f"LRC-TOT-{grade}"]].dropna()
    fig = go.Figure(go.Scatter(
        x=s["Date"], y=s[f"LRC-TOT-{grade}"], mode="lines", name="Total certs",
        line=dict(color=NAVY, width=2), fill="tozeroy", fillcolor="rgba(10,36,99,0.07)",
        hovertemplate="%{y:,.0f}<extra></extra>"))
    return chart_layout(fig, "Total Certs")


@st.cache_data(ttl=3600, show_spinner=False)
def major_ports(view: pd.DataFrame, grade: str = "VG", min_share: float = 0.01) -> list:
    """Ports whose average share of the total in `view` is at least min_share,
    biggest first. Near-zero ports are left out of the charts."""
    tot = view[f"LRC-TOT-{grade}"].astype(float).mean()
    if not tot:
        return []
    share = {p: view[f"LRC-{p}-{grade}"].astype(float).mean() / tot for p in PORT_ORDER}
    return [p for p in sorted(share, key=lambda p: -(0 if pd.isna(share[p]) else share[p]))
            if pd.notna(share[p]) and share[p] >= min_share]


@st.cache_data(ttl=3600, show_spinner=False)
def ports_certs_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """Stacked area of certs per major port (biggest at the bottom); minor ports pooled into Other.
    2012-14 has total-only rows (all ports blank), which would collapse the stack, so only rows
    that carry port data are used here; the Total chart keeps every row."""
    port_cols = [f"LRC-{p}-{grade}" for p in PORT_ORDER]
    pv = df[df[port_cols].notna().any(axis=1)]
    majors = major_ports(pv, grade)
    minors = [p for p in PORT_ORDER if p not in majors]
    fig = go.Figure()
    for p in majors:
        fig.add_trace(go.Scatter(
            x=pv["Date"], y=pv[f"LRC-{p}-{grade}"].astype(float).fillna(0), mode="lines", name=p, stackgroup="one",
            line=dict(width=0.6, color=PORT_COLORS.get(p, GREY)), fillcolor=PORT_COLORS.get(p, GREY),
            hovertemplate="%{y:,.0f}<extra>" + p + "</extra>"))
    if minors:
        other = pv[[f"LRC-{p}-{grade}" for p in minors]].astype(float).fillna(0).sum(axis=1)
        fig.add_trace(go.Scatter(x=pv["Date"], y=other, mode="lines", name="Other", stackgroup="one",
                                 line=dict(width=0.6, color="#c5cbdd"), fillcolor="#c5cbdd",
                                 hovertemplate="%{y:,.0f}<extra>Other</extra>"))
    return chart_layout(fig, "Certs Per Port")


@st.cache_data(ttl=3600, show_spinner=False)
def rolling_fig(series: pd.Series, n: int, start: pd.Timestamp, end: pd.Timestamp, title: str) -> go.Figure:
    """Rolling n-observation change of a stock series (computed on the full
    history, then cut to the chosen window)."""
    r = series.dropna().astype(float).diff(n).dropna()
    r = r[(r.index >= start) & (r.index <= end)]
    fig = go.Figure(go.Scatter(x=r.index, y=r.values, mode="lines", name=f"{n}d",
                               line=dict(color=NAVY, width=2.2),
                               hovertemplate="%{y:+,.0f}<extra>" + f"{n}d" + "</extra>"))
    fig.add_hline(y=0, line=dict(color="#c5cbdd", width=1))
    chart_layout(fig, title, height=360)
    fig.update_layout(yaxis=dict(tickformat="+,"), showlegend=False)
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def rolling_ports_fig(df: pd.DataFrame, ports: list, n: int, start: pd.Timestamp, end: pd.Timestamp,
                      grade: str = "VG") -> go.Figure:
    """Rolling n-observation change, one line per chosen port."""
    fig = go.Figure()
    for p in ports:
        r = df.set_index("Date")[f"LRC-{p}-{grade}"].dropna().astype(float).diff(n).dropna()
        r = r[(r.index >= start) & (r.index <= end)]
        fig.add_trace(go.Scatter(x=r.index, y=r.values, mode="lines", name=p,
                                 line=dict(color=PORT_COLORS.get(p, GREY), width=2.0),
                                 hovertemplate="%{y:+,.0f}<extra>" + p + "</extra>"))
    fig.add_hline(y=0, line=dict(color="#c5cbdd", width=1))
    label = ", ".join(ports) if ports else "no port selected"
    chart_layout(fig, f"Rolling Change: {label} ({n}d)", height=360)
    fig.update_layout(yaxis=dict(tickformat="+,"), showlegend=len(ports) > 1)
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def share_line_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """Each major port's share of total certs (%) over time, as lines."""
    tot = df[f"LRC-TOT-{grade}"].astype(float).where(lambda v: v > 0)
    fig = go.Figure()
    for p in major_ports(df, grade):
        share = (df[f"LRC-{p}-{grade}"].astype(float) / tot * 100)
        ok = share.notna()
        fig.add_trace(go.Scatter(x=df["Date"][ok], y=share[ok], mode="lines", name=p,
                                 line=dict(color=PORT_COLORS.get(p, GREY), width=2.0),
                                 hovertemplate="%{y:.1f}%<extra>" + p + "</extra>"))
    chart_layout(fig, "Port Share of Total", height=360)
    fig.update_layout(yaxis=dict(ticksuffix="%", range=[0, 100]))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def country_share_line_fig(df: pd.DataFrame, grade: str = "VG", min_share: float = 0.01) -> go.Figure:
    """Each country's share of total certs (%) over time; countries under min_share on average are left out."""
    tot = df[f"LRC-TOT-{grade}"].astype(float).where(lambda v: v > 0)
    fig = go.Figure()
    for country, ports in countries_by_stock(df, grade):
        cols = [f"LRC-{p}-{grade}" for p in ports]
        vals = df[cols].astype(float).sum(axis=1, min_count=1)
        share = vals / tot * 100
        if not (share.mean() >= min_share * 100):
            continue
        ok = share.notna()
        fig.add_trace(go.Scatter(x=df["Date"][ok], y=share[ok], mode="lines", name=country,
                                 line=dict(color=PORT_COLORS.get(ports[0], GREY), width=2.0),
                                 hovertemplate="%{y:.1f}%<extra>" + country + "</extra>"))
    chart_layout(fig, "Country Share of Total", height=360)
    fig.update_layout(yaxis=dict(ticksuffix="%", range=[0, 100]))
    return fig


def tint(hex_color: str, keep: float = 0.55) -> str:
    """Blend a hex colour towards white; keep = share of the original colour."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    mix = lambda c: int(round(c * keep + 255 * (1 - keep)))
    return f"#{mix(r):02x}{mix(g):02x}{mix(b):02x}"


@st.cache_data(ttl=3600, show_spinner=False)
def share_pie_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """Latest breakup as a two-ring donut: inner ring = country, outer ring = port.
    Ports under 1% of the total are pooled into a grey Other."""
    last = df.iloc[-1]
    tot = float(last[f"LRC-TOT-{grade}"])

    def stock(p):
        v = last[f"LRC-{p}-{grade}"]
        return 0.0 if pd.isna(v) else float(v)

    ids, labels, parents, values, colors, texts = ["root"], [f"{tot:,.0f}"], [""], [tot], ["#fafafa"],         [f"<b>{tot:,.0f}</b><br>total"]
    used = 0.0
    for country, ports in countries_by_stock(df, grade):
        big = [p for p in ports if stock(p) / tot >= 0.01]
        c_val = sum(stock(p) for p in big)
        if not big:
            continue
        base = PORT_COLORS.get(big[0], GREY)
        ids.append(f"c:{country}"); labels.append(country); parents.append("root"); values.append(c_val)
        colors.append(tint(base, 0.5)); texts.append(country if c_val / tot >= 0.04 else "")
        for p in big:
            ids.append(f"p:{p}"); labels.append(p); parents.append(f"c:{country}"); values.append(stock(p))
            colors.append(PORT_COLORS.get(p, GREY))
            texts.append(f"{p}<br>{stock(p) / tot * 100:.0f}%" if stock(p) / tot >= 0.04 else "")
        used += c_val
    rest = tot - used
    if rest > 0.5:
        ids += ["c:Other", "p:Other"]; labels += ["Other", "Other"]; parents += ["root", "c:Other"]
        values += [rest, rest]; colors += ["#dfe3ee", "#c5cbdd"]; texts += ["", ""]
    fig = go.Figure(go.Sunburst(
        ids=ids, labels=labels, parents=parents, values=values, branchvalues="total", sort=False,
        marker=dict(colors=colors, line=dict(color="#fafafa", width=2.5)),
        text=texts, textinfo="text", insidetextorientation="horizontal",
        textfont=dict(size=11, color="#1a1a2e"),
        hovertemplate="%{label}: %{value:,.0f} (%{percentRoot:.1%})<extra></extra>",
        domain=dict(x=[0.2, 0.8], y=[0.04, 0.96])))
    chart_layout(fig, f"Latest Breakup ({last['Date'].strftime('%d %b %Y')})", height=360)
    fig.update_layout(margin=dict(t=44, b=8, l=8, r=8), showlegend=False)
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def seasonality_fig(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    """Day-of-year seasonality for a stock level (Certs, etc): thin wrapper around
    _dayofyear_bands_fig with weekends/holidays forward-filled from the last known level."""
    s = df.set_index("Date")[col].dropna().astype(float)
    w = s.resample("D").last().ffill()
    return _dayofyear_bands_fig(w, title)


def _dayofyear_bands_fig(s: pd.Series, title: str, height: int = 440) -> go.Figure:
    """Day-of-year seasonality: history bands (min-max, 10-90, 25-75 pct), average,
    last year in red and the current year in navy (same styling as Cotton On-Call).
    `s` should already be the series to plot as-is - a level series should be ffilled by the
    caller first; a flow/change series (e.g. Usage) should be left sparse so days without data
    (weekends) don't fabricate repeated or zero values in the bands."""
    w = s.dropna().to_frame("v")
    w["x"], w["yr"] = w.index.dayofyear, w.index.year
    w = w[w["x"] <= 366]  # 366 so a leap year keeps its last day
    cur = int(w["yr"].max())
    hist = w[w["yr"] < cur]
    band = hist.groupby("x")["v"].agg(lo="min", avg="mean", hi="max").sort_index()
    q = hist.groupby("x")["v"].quantile([0.10, 0.25, 0.75, 0.90]).unstack()
    band[["p10", "p25", "p75", "p90"]] = q[[0.10, 0.25, 0.75, 0.90]].values

    fig = go.Figure()
    for lo, hi, color, name in [("lo", "hi", "rgba(31,138,156,0.08)", "Min-Max"),
                                ("p10", "p90", "rgba(31,138,156,0.16)", "10th-90th pct"),
                                ("p25", "p75", "rgba(31,138,156,0.28)", "25th-75th pct")]:
        fig.add_trace(go.Scatter(x=band.index, y=band[hi], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=band.index, y=band[lo], fill="tonexty", fillcolor=color,
                                 line=dict(width=0), name=name, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=band.index, y=band["avg"], mode="lines", name="Average",
                             line=dict(color="#4a5578", width=1.5, dash="dot"), hovertemplate="%{y:,.0f}<extra>Avg</extra>"))
    for yr, color, width in [(cur - 1, RED, 2), (cur, NAVY, 3)]:
        g = w[w["yr"] == yr].sort_values("x")
        if not g.empty:
            fig.add_trace(go.Scatter(x=g["x"], y=g["v"], mode="lines", name=str(yr), line=dict(color=color, width=width),
                                     hovertemplate="%{y:,.0f}<extra>" + str(yr) + "</extra>"))
    chart_layout(fig, title, height)
    fig.update_layout(xaxis=dict(title="Day of year", dtick=30, range=[1, 366]),
                      legend=dict(y=-0.28))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def seasonality_options(df: pd.DataFrame, grade: str = "VG") -> dict:
    """Label -> column. Total first, then ports with the most stock today first."""
    last = df.iloc[-1]
    ports = [p for p in PORT_ORDER if df[f"LRC-{p}-{grade}"].fillna(0).abs().sum() > 0]
    ports.sort(key=lambda p: -(0 if pd.isna(last[f"LRC-{p}-{grade}"]) else last[f"LRC-{p}-{grade}"]))
    return {"Total": f"LRC-TOT-{grade}", **{p: f"LRC-{p}-{grade}" for p in ports}}


@st.cache_data(ttl=3600, show_spinner=False)
def monthly_change_html(df: pd.DataFrame, col: str) -> str:
    """Year x month matrix of month-end-to-month-end change, with in-cell bars
    and a YEAR total column."""
    ser = df.set_index("Date")[col].dropna().astype(float)
    try:
        me = ser.resample("ME").last()
    except ValueError:
        me = ser.resample("M").last()
    ch = me.ffill().diff().dropna()
    ch = ch[ch.index.year >= 2009]
    tbl = ch.groupby([ch.index.year, ch.index.month]).sum().unstack()
    tbl = tbl.reindex(columns=range(1, 13))
    year_tot = tbl.sum(axis=1, min_count=1)
    scale = max(tbl.abs().max().max(), 1)
    yscale = max(year_tot.abs().max(), 1)
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    def cell(v, sc, cls="cb"):
        if pd.isna(v):
            return "<td class='na'></td>"
        v = int(round(v))
        if v == 0:
            return f"<td class='{cls}'><span></span></td>"
        w = abs(v) / sc * 50
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{w:.1f}%'></i>"
        return f"<td class='{cls}'>{bar}<span class='{'pos' if v > 0 else 'neg'}'>{v:+,}</span></td>"

    out = ["<div class='rwrap' style='height:auto'><table class='rpt mx'><thead><tr class='h2'><th class='dt'>Year</th>"]
    out += [f"<th>{m}</th>" for m in months] + ["<th class='sep'>Year</th></tr></thead><tbody>"]
    for yr in tbl.index:
        row = [f"<tr><td class='d'>{yr}</td>"]
        row += [cell(tbl.loc[yr, m], scale) for m in range(1, 13)]
        row.append(cell(year_tot[yr], yscale, "cb sep"))
        row.append("</tr>")
        out.append("".join(row))
    out.append("</tbody></table></div>")
    return "".join(out)


DIST_START = "2015-01-01"  # daily-observation era; earlier data is roughly biweekly


@st.cache_data(ttl=3600, show_spinner=False)
def distribution_fig(values: pd.Series, title: str, label: str) -> go.Figure:
    """Histogram of non-zero daily changes (zero-change days are counted but not drawn, they only
    make one giant spike) over the 1st-99th percentile, with a fitted normal curve and the latest
    value marked."""
    vals = values.dropna().astype(float)
    latest = float(vals.iloc[-1])
    nz = vals[vals != 0]
    if len(nz) < 20:
        nz = vals
    n_zero = int((vals == 0).sum())
    lo, hi = float(nz.quantile(0.01)), float(nz.quantile(0.99))
    lo, hi = min(lo, latest, -1.0), max(hi, latest, 1.0)
    shown = nz[(nz >= lo) & (nz <= hi)]
    mu, sd = float(nz.mean()), float(nz.std(ddof=0)) or 1.0
    z = (latest - mu) / sd
    pct = float((nz <= latest).mean() * 100)
    bin_size = max(1.0, float(np.ceil((hi - lo) / 45)))
    xs = np.linspace(lo, hi, 300)
    pdf = np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=shown, histnorm="probability density", name="Observed",
                               xbins=dict(start=lo - bin_size / 2, end=hi + bin_size / 2, size=bin_size),
                               marker=dict(color=NAVY, opacity=0.85, line=dict(color="#fafafa", width=1)),
                               hovertemplate="%{x:,.0f}<extra>Observed</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=pdf, mode="lines", name="Normal fit",
                             line=dict(color=TEAL, width=2.4), hoverinfo="skip"))
    fig.add_vline(x=latest, line=dict(color=AMBER, width=2, dash="dash"))
    chart_layout(fig, title, height=540)
    zero_note = (f"zero-change days not drawn: {n_zero:,} ({n_zero / len(vals) * 100:.0f}%)  |  1st-99th percentile shown"
                 if label == "chg" else "1st-99th percentile shown")
    fig.update_layout(
        showlegend=False, hovermode="closest", margin=dict(t=40, b=8, l=8, r=8),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(title=dict(text=zero_note, font=dict(size=11, color="#7a86a8")), range=[lo - bin_size, hi + bin_size],
                   tickformat=",", gridcolor="rgba(10,36,99,0.06)", showline=True, linecolor="#dfe3ee"),
        annotations=[dict(xref="paper", yref="paper", x=1, y=1.02, xanchor="right", yanchor="bottom", showarrow=False,
                          text=f"Latest {latest:+,.0f}  |  z {z:+.1f}  |  pctile {pct:.0f}" if label == "chg"
                          else f"Latest {latest:,.0f}  |  z {z:+.1f}  |  pctile {pct:.0f}",
                          font=dict(size=11, color="#5a6688"))],
    )
    return fig


# ------------------------------------------------------------------ grading
GRADING_ORIGIN_MAIN = {"Brazilian Conillon": "Brazil", "Vietnam": "Vietnam", "Indonesia": "Indonesia"}
GRADING_ORIGIN_SHORT = {"Brazilian Conillon": "Brazil", "Republic of Madagascar": "Madagascar"}
GRADING_CLASS_ORDER = ["1", "2", "3", "4", "P", "NA"]
GRADING_CLASS_LABEL = {"NA": "NT"}
GRADING_CLASS_COLORS = {"1": NAVY, "2": TEAL, "3": AMBER, "4": RED, "P": GREEN, "NA": GREY}
GRADING_ORIGIN_COLORS = {"Brazil": NAVY, "Vietnam": TEAL, "Indonesia": AMBER, "Other": "#b8c0d6"}
PORT_COUNTRY = {"ANT": "Belgium", "LON": "UK", "FEL": "UK", "LIV": "UK", "AMS": "Netherlands", "ROT": "Netherlands",
                "HAM": "Germany", "BRE": "Germany", "BAR": "Spain", "TRI": "Italy", "GEN": "Italy",
                "LEH": "France", "NOR": "USA"}


@st.cache_data(ttl=600)
def load_rc_grading() -> pd.DataFrame:
    g = pd.read_parquet(DB_DIR / "Main" / "RC" / "rc_grading.parquet")
    g["PanelDate"] = pd.to_datetime(g["PanelDate"])
    g["Origin2"] = g["Origin"].map(GRADING_ORIGIN_MAIN).fillna("Other")
    g["OriginName"] = g["Origin"].map(GRADING_ORIGIN_SHORT).fillna(g["Origin"])
    g["Country"] = g["PortId"].map(PORT_COUNTRY).fillna("Other")
    return g


@st.cache_data(ttl=3600, show_spinner=False)
def grading_origin_palette(g: pd.DataFrame) -> tuple:
    """(origins biggest-first, colours). The top three keep the strong app colours; every smaller
    origin gets a lighter tint that fades with rank."""
    order = list(g.groupby("OriginName")["NoLots"].sum().sort_values(ascending=False).index)
    strong = [NAVY, TEAL, AMBER]
    soft = ["#9b6bb3", RED, GREEN, "#6b7fb5", "#c0722c", "#4a5578", "#8fa3d1", "#b58f4a", GREY, "#c5cbdd"]
    colors = {}
    for i, o in enumerate(order):
        if i < len(strong):
            colors[o] = strong[i]
        else:
            colors[o] = tint(soft[(i - 3) % len(soft)], max(0.75 - 0.06 * (i - 3), 0.32))
    return order, colors


@st.cache_data(ttl=3600, show_spinner=False)
def grading_table_html(g: pd.DataFrame, height: str = "60vh") -> str:
    """Panel dates down the rows. Left: total lots (data bars) then Origin > Class.
    Right: Country > Port. Empty columns are left out."""
    tot = g.groupby("PanelDate")["NoLots"].sum().sort_index(ascending=False)
    oc = g.groupby(["PanelDate", "Origin2", "Class"])["NoLots"].sum().to_dict()
    pc = g.groupby(["PanelDate", "PortId"])["NoLots"].sum().to_dict()
    origin_rank = g.groupby("Origin2")["NoLots"].sum().sort_values(ascending=False)
    country_rank = g.groupby("Country")["NoLots"].sum().sort_values(ascending=False)
    port_rank = g.groupby("PortId")["NoLots"].sum().sort_values(ascending=False)

    o_groups = []
    for o in origin_rank.index:
        cls = [c for c in GRADING_CLASS_ORDER if ((g["Origin2"] == o) & (g["Class"] == c)).any()]
        if cls:
            o_groups.append((o, cls))
    p_groups = []
    for c in country_rank.index:
        ports = [p for p in port_rank.index if PORT_COUNTRY.get(p, "Other") == c]
        if ports:
            p_groups.append((c, ports))
    o_cols = [(o, c) for o, cls in o_groups for c in cls]
    p_cols = [(c, p) for c, ps in p_groups for p in ps]
    o_start = set(); k = 0
    for _, cls in o_groups:
        o_start.add(k); k += len(cls)
    p_start = set(); k = 0
    for _, ps in p_groups:
        p_start.add(k); k += len(ps)
    top = max(float(tot.max()), 1.0)

    def num(v):
        return "" if not v else f"{int(v):,}"

    head = [f"<div class='rwrap' style='height:{height}'><table class='rpt'><thead>",
            "<tr class='h1'><th class='dt' rowspan='3'>Panel date</th>",
            f"<th colspan='{len(o_cols) + 1}'>Lots Graded by Origin and Class</th>",
            f"<th colspan='{len(p_cols)}' class='sep'>Lots Graded by Port</th></tr>",
            "<tr class='h2'><th rowspan='2'>TOT</th>"]
    head += [f"<th colspan='{len(cls)}' class='gs'>{o}</th>" for o, cls in o_groups]
    for i, (c, ps) in enumerate(p_groups):
        head.append(f"<th colspan='{len(ps)}' class='gs{' sep' if i == 0 else ''}'>{c}</th>")
    head.append("</tr><tr class='h3'>")
    head += [f"<th{' class=gs' if i in o_start else ''}>{GRADING_CLASS_LABEL.get(c, c)}</th>" for i, (o, c) in enumerate(o_cols)]
    head += [f"<th class='{'gs' if i in p_start else ''}{' sep' if i == 0 else ''}'>{p}</th>" for i, (c, p) in enumerate(p_cols)]
    head.append("</tr></thead><tbody>")

    body = []
    for d, t in tot.items():
        row = [f"<tr><td class='d'>{d.strftime('%d-%b-%y')}</td>",
               f"<td class='cbl'><i style='width:{t / top * 100:.1f}%'></i><span>{int(t):,}</span></td>"]
        row += [f"<td{' class=gs' if i in o_start else ''}>{num(oc.get((d, o, c), 0))}</td>" for i, (o, c) in enumerate(o_cols)]
        row += [f"<td class='{'gs' if i in p_start else ''}{' sep' if i == 0 else ''}'>{num(pc.get((d, p), 0))}</td>"
                for i, (c, p) in enumerate(p_cols)]
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def grading_bar_fig(view: pd.DataFrame, col: str, title: str, order: list, colors: dict,
                    labels: dict | None = None, height: int = 340) -> go.Figure:
    """Lots graded per panel date, stacked by `col` (category axis: only panel dates are shown)."""
    fig = go.Figure()
    if view.empty:
        return chart_layout(fig, title, height)
    dates = sorted(view["PanelDate"].unique())
    xs = pd.DatetimeIndex(dates).strftime("%d/%m/%y")
    for key in order:
        sub = view[view[col] == key]
        if sub.empty:
            continue
        name = (labels or {}).get(key, key)
        y = sub.groupby("PanelDate")["NoLots"].sum().reindex(dates, fill_value=0).values
        fig.add_trace(go.Bar(x=xs, y=y, name=name, marker_color=colors.get(key, GREY),
                             hovertemplate="%{y:,.0f}<extra>" + name + "</extra>"))
    total = view.groupby("PanelDate")["NoLots"].sum().reindex(dates, fill_value=0)
    if len(dates) <= 70:
        fig.add_trace(go.Scatter(x=xs, y=total.values, mode="text", text=[f"{int(v):,}" for v in total.values],
                                 textposition="top center", textfont=dict(size=10, color=NAVY),
                                 showlegend=False, hoverinfo="skip"))
    chart_layout(fig, title, height)
    fig.update_layout(
        barmode="stack", bargap=0.28,
        xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9), nticks=60),
        yaxis=dict(title=None, tickformat=","),
        legend=dict(orientation="v", x=1.01, y=1, xanchor="left", yanchor="top"),
        margin=dict(t=44, b=8, l=8, r=8))
    return fig


MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def crop_label(yr: int, m: int) -> str:
    """Calendar year when the crop year starts in January, otherwise e.g. 25/26."""
    return str(yr) if m == 1 else f"{yr % 100:02d}/{(yr + 1) % 100:02d}"


@st.cache_data(ttl=3600, show_spinner=False)
def crop_seasonality_fig(g_sel: pd.DataFrame, title: str, m: int, first: pd.Timestamp, last: pd.Timestamp,
                         height: int = 360) -> go.Figure:
    """Cumulative lots graded through the crop year (resets on the 1st of month m). Thin wrapper
    around _cumulative_bands_fig for the grading dataframe shape."""
    s = g_sel.groupby("PanelDate")["NoLots"].sum()
    return _cumulative_bands_fig(s, title, m, first, last, height)


def _cumulative_bands_fig(s: pd.Series, title: str, m: int, first: pd.Timestamp, last: pd.Timestamp,
                          height: int = 360) -> go.Figure:
    """Cumulative sum of a daily flow through the crop/calendar year (resets on the 1st of month m),
    history bands from past years, previous year in red, current one in navy. Years that began
    before the data did are skipped so no partial year distorts the bands."""
    fig = go.Figure()
    first_cy = first.year if first.month >= m else first.year - 1
    start0 = pd.Timestamp(year=first_cy, month=m, day=1)
    if (first - start0).days > 45:
        first_cy += 1
        start0 = pd.Timestamp(year=first_cy, month=m, day=1)
    idx = pd.date_range(start0, last)
    daily = s.reindex(idx, fill_value=0)
    cy = np.where(idx.month >= m, idx.year, idx.year - 1)
    cum = daily.groupby(cy).cumsum()
    starts = pd.to_datetime([f"{y}-{m:02d}-01" for y in cy])
    w = pd.DataFrame({"v": cum.values.astype(float), "x": (idx - starts).days + 1, "yr": cy}, index=idx)
    w = w[w["x"] <= 366]  # 366 so a leap year keeps its last day
    cur = int(w["yr"].max())
    hist = w[w["yr"] < cur]
    if not hist.empty:
        band = hist.groupby("x")["v"].agg(lo="min", avg="mean", hi="max").sort_index()
        q = hist.groupby("x")["v"].quantile([0.10, 0.25, 0.75, 0.90]).unstack()
        band[["p10", "p25", "p75", "p90"]] = q[[0.10, 0.25, 0.75, 0.90]].values
        for lo, hi, color in [("lo", "hi", "rgba(31,138,156,0.08)"), ("p10", "p90", "rgba(31,138,156,0.16)"),
                              ("p25", "p75", "rgba(31,138,156,0.28)")]:
            fig.add_trace(go.Scatter(x=band.index, y=band[hi], line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=band.index, y=band[lo], fill="tonexty", fillcolor=color, line=dict(width=0),
                                     showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=band.index, y=band["avg"], mode="lines", name="Average",
                                 line=dict(color="#4a5578", width=1.5, dash="dot"),
                                 hovertemplate="%{y:,.0f}<extra>Avg</extra>"))
    for yr, color, width in [(cur - 1, RED, 2), (cur, NAVY, 3)]:
        gg = w[w["yr"] == yr].sort_values("x")
        if not gg.empty:
            lbl = crop_label(yr, m)
            fig.add_trace(go.Scatter(x=gg["x"], y=gg["v"], mode="lines", name=lbl, line=dict(color=color, width=width),
                                     hovertemplate="%{y:,.0f}<extra>" + lbl + "</extra>"))
    order = [(m - 1 + i) % 12 for i in range(12)]
    offs = np.concatenate([[0], np.cumsum([MONTH_DAYS[k] for k in order])])[:12] + 1
    chart_layout(fig, title, height)
    fig.update_layout(xaxis=dict(tickmode="array", tickvals=list(offs[::2]),
                                 ticktext=[MONTH_ABBR[order[i]] for i in range(0, 12, 2)], range=[1, 366]),
                      legend=dict(font=dict(size=10)))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def usage_cumulative_fig(daily_usage: pd.Series, first: pd.Timestamp, last: pd.Timestamp,
                         m: int = 1, height: int = 360) -> go.Figure:
    """Cumulative Usage (Grading - Certs change), resetting on the 1st of month m."""
    return _cumulative_bands_fig(daily_usage, "Cumulative Usage", m, first, last, height)


@st.cache_data(ttl=3600, show_spinner=False)
def usage_by_origin_fig(gr: pd.DataFrame, certs: pd.DataFrame, grade: str = "VG", height: int = 380) -> go.Figure:
    """Monthly Usage split by origin (Brazil/Vietnam/Indonesia/Other), each origin's usage taken as
    its share of that month's total lots graded, applied to the month's total Usage."""
    lots_o = gr.groupby([gr["PanelDate"].dt.to_period("M"), "Origin2"])["NoLots"].sum().unstack(fill_value=0)
    lots_tot = lots_o.sum(axis=1)
    share = lots_o.div(lots_tot.replace(0, np.nan), axis=0).fillna(0)

    ser = certs.set_index("Date")[f"LRC-TOT-{grade}"].dropna().astype(float)
    chg = ser.resample("ME").last().ffill().diff().dropna()
    chg.index = chg.index.to_period("M")
    months = sorted(set(lots_tot.index) & set(chg.index))
    usage_tot = lots_tot.reindex(months) - chg.reindex(months)

    origins = list(lots_o.sum().sort_values(ascending=False).index)
    xs = [str(p) for p in months]
    fig = go.Figure()
    for o in origins:
        y = (share.reindex(months)[o].fillna(0) * usage_tot).values
        fig.add_trace(go.Bar(x=xs, y=y, name=o, marker_color=GRADING_ORIGIN_COLORS.get(o, GREY),
                             hovertemplate="%{y:+,.0f}<extra>" + o + "</extra>"))
    chart_layout(fig, "Monthly Usage by Origin (origin's share of that month's grading)", height)
    fig.update_layout(barmode="relative", bargap=0.25,
                      xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9)),
                      yaxis=dict(tickformat="+,"))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def monthly_lots_html(g: pd.DataFrame, m: int = 1) -> str:
    """Crop year x month lots graded (columns start at month m) with in-cell bars and a crop-year total."""
    s = g.groupby("PanelDate")["NoLots"].sum()
    if s.empty:
        return "<div class='rwrap' style='padding:14px'>No lots.</div>"
    cyear = np.where(s.index.month >= m, s.index.year, s.index.year - 1)
    months = [(m - 1 + i) % 12 + 1 for i in range(12)]
    tbl = s.groupby([cyear, s.index.month]).sum().unstack().reindex(columns=months)
    first, last = g["PanelDate"].min(), g["PanelDate"].max()
    for yr in tbl.index:
        for mo in months:
            cal_year = yr if (m == 1 or mo >= m) else yr + 1
            if (cal_year, mo) < (first.year, first.month) or (cal_year, mo) > (last.year, last.month):
                tbl.loc[yr, mo] = np.nan
            elif pd.isna(tbl.loc[yr, mo]):
                tbl.loc[yr, mo] = 0
    year_tot = tbl.sum(axis=1, min_count=1)
    scale, yscale = max(tbl.max().max(), 1), max(year_tot.max(), 1)

    def cell(v, sc, cls="cbl"):
        if pd.isna(v):
            return "<td class='na'></td>"
        v = int(round(v))
        bar = f"<i style='width:{v / sc * 100:.1f}%'></i>" if v else ""
        return f"<td class='{cls}'>{bar}<span>{v:,}</span></td>"

    out = ["<div class='rwrap' style='height:auto'><table class='rpt mx'><thead><tr class='h2'>"
           f"<th class='dt'>{'Year' if m == 1 else 'Crop yr'}</th>"]
    out += [f"<th>{MONTH_ABBR[mo - 1].upper()}</th>" for mo in months] + ["<th class='sep'>Total</th></tr></thead><tbody>"]
    for yr in tbl.index:
        row = [f"<tr><td class='d'>{crop_label(int(yr), m)}</td>"] + [cell(tbl.loc[yr, mo], scale) for mo in months]
        row.append(cell(year_tot[yr], yscale, "cbl sep"))
        row.append("</tr>")
        out.append("".join(row))
    out.append("</tbody></table></div>")
    return "".join(out)


@st.cache_data(ttl=3600, show_spinner=False)
def daily_usage_series(gr: pd.DataFrame, certs: pd.DataFrame, grade: str = "VG", lag: int = 1) -> pd.Series:
    """Daily Usage = Grading - Certs change, certs change looked up `lag` certs-trading-days ahead
    (default 1, matching the Data Table default). Covers every certs day from the grading feed's
    own start onward; days with no panel that day count as 0 lots graded."""
    lots_tot = gr.groupby("PanelDate")["NoLots"].sum()
    ser = certs.set_index("Date")[f"LRC-TOT-{grade}"].dropna().astype(float)
    chg = ser.diff().dropna()
    cd = list(chg.index.sort_values())

    def lagged(d):
        i = np.searchsorted(cd, d) + lag
        return chg.loc[cd[i]] if 0 <= i < len(cd) else np.nan

    g_start = gr["PanelDate"].min()
    idx = pd.DatetimeIndex(sorted(d for d in cd if d >= g_start))
    # a panel that ran on a day with no certs print (weekend / holiday) is attributed to the next certs day,
    # otherwise its lots would silently drop out of Usage
    cd_idx = pd.DatetimeIndex(cd)
    tpos = cd_idx.searchsorted(lots_tot.index)
    keep = tpos < len(cd_idx)
    g_on_day = lots_tot[keep].groupby(cd_idx[tpos[keep]]).sum().reindex(idx, fill_value=0)
    c_lagged = pd.Series([lagged(d) for d in idx], index=idx, dtype=float)
    return (g_on_day - c_lagged).dropna()


@st.cache_data(ttl=3600, show_spinner=False)
def monthly_grading_certs_html(gr: pd.DataFrame, certs: pd.DataFrame, grade: str = "VG",
                               height: str = "60vh") -> str:
    """One row per calendar month, capped to the grading feed's own range (it starts Jan 2022;
    certs go back to 2008 but there is nothing to grade-compare before grading itself exists).
    Every origin gets its own column (lots), LRC total certs change (lots) sits alongside it,
    both sharing a single Month column so the rows line up."""
    lots = gr.groupby([gr["PanelDate"].dt.to_period("M"), "OriginName"])["NoLots"].sum().unstack(fill_value=0)
    lots_tot = lots.sum(axis=1)
    origins = list(lots.sum().sort_values(ascending=False).index)

    ser = certs.set_index("Date")[f"LRC-TOT-{grade}"].dropna().astype(float)
    me = ser.resample("ME").last().ffill()
    level = me.copy()
    level.index = level.index.to_period("M")
    avg_level = ser.resample("ME").mean()
    avg_level.index = avg_level.index.to_period("M")
    chg = me.diff().dropna()
    chg.index = chg.index.to_period("M")

    g_start = gr["PanelDate"].min().to_period("M")
    months = sorted([p for p in (set(lots_tot.index) | set(chg.index)) if p >= g_start], reverse=True)
    if not months:
        return "<div class='rwrap' style='padding:14px'>No data.</div>"
    l_scale = max(lots_tot.max(), 1)
    c_scale = max(chg.abs().max(), 1) if len(chg) else 1
    usage = lots_tot.reindex(chg.index, fill_value=0) - chg
    u_scale = max(usage.abs().max(), 1) if len(usage) else 1
    usage_pct = usage / avg_level.reindex(usage.index) * 100
    p_scale = max(usage_pct.abs().max(), 1) if len(usage_pct) and usage_pct.notna().any() else 1

    all_max = max(float(lots[origins].max().max()), 1.0)

    def lcell(v):
        if pd.isna(v) or v == 0:
            return "<td></td>"
        v = int(v)
        alpha = min(v / all_max, 1.0) * 0.85  # one scale across every origin, so cells are comparable to each other
        return f"<td style='background:rgba(31,157,111,{alpha:.2f})'>{v:,}</td>"

    def totcell(v, sc):
        v = int(round(v)) if pd.notna(v) else 0
        bar = f"<i style='width:{v / sc * 100:.1f}%'></i>" if v else ""
        return f"<td class='cbl'>{bar}<span>{v:,}</span></td>"

    def chgcell(v):
        if pd.isna(v):
            return "<td class='na'></td>"
        v = int(round(v))
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / c_scale * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb'>{bar}<span class='{cls}'>{v:+,}</span></td>"

    def usecell(g, c):
        # Usage = Grading - Certs change: lots graded that weren't offset by a matching rise in
        # certified stocks (i.e. graded coffee that left the certified pool / was used).
        if pd.isna(c):
            return "<td class='na'></td>"
        g = 0 if pd.isna(g) else g
        v = int(round(g - c))
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / u_scale * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb'>{bar}<span class='{cls}'>{v:+,}</span></td>"

    def levelcell(v):
        if pd.isna(v):
            return "<td class='na sep'></td>"
        return f"<td class='tot sep'>{int(round(v)):,}</td>"

    def pctcell(v):
        if pd.isna(v):
            return "<td class='na'></td>"
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / p_scale * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb'>{bar}<span class='{cls}'>{v:+.1f}%</span></td>"

    head = ["<div class='mt' style='margin-bottom:4px'>Grading (lots) & LRC Certified Stocks Change (lots), by month. "
            "Usage % is Usage divided by that month's average certs level.</div>",
            "<div class='rwrap' style='height:", height, "'><table class='rpt'><thead>",
            "<tr class='h1'><th class='dt' rowspan='2'>Month</th>",
            f"<th colspan='{len(origins) + 1}'>Lots Graded by Origin</th>",
            "<th colspan='4' class='sep certs-hdr'>LRC Certs</th></tr><tr class='h2'>"]
    head += [f"<th>{o}</th>" for o in origins] + [
        "<th>Total</th><th class='sep certs-hdr'>Level</th><th class='certs-hdr'>Change</th>",
        "<th class='certs-hdr'>Usage</th><th class='certs-hdr'>Usage %</th></tr></thead><tbody>"]

    body = []
    for pr in months:
        row = [f"<tr><td class='d'>{pr.strftime('%b %Y')}</td>"]
        row += [lcell(lots.loc[pr, o] if pr in lots.index else np.nan) for o in origins]
        row.append(totcell(lots_tot.get(pr, 0), l_scale))
        row.append(levelcell(level.get(pr, np.nan)))
        row.append(chgcell(chg.get(pr, np.nan)))
        row.append(usecell(lots_tot.get(pr, np.nan), chg.get(pr, np.nan)))
        row.append(pctcell(usage_pct.get(pr, np.nan)))
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def daily_grading_certs_html(gr: pd.DataFrame, certs: pd.DataFrame, grade: str = "VG",
                             height: str = "60vh", lag: int = 1, nrows: int = 0) -> str:
    """Same idea as monthly_grading_certs_html, one row per calendar day instead of month: grading
    lots by origin only show up on days a panel actually ran, LRC certs change is day-over-day.
    Capped to grading's own range (from Jan 2022).

    `lag`: a day's grading isn't reflected in certified stocks until it clears, so the Change/Usage
    columns for a given row look `lag` certs-trading-days ahead of that row's own date (default 1 -
    today's grading shows up in tomorrow's certs print). The row's date itself doesn't move."""
    lots = gr.groupby([gr["PanelDate"], "OriginName"])["NoLots"].sum().unstack(fill_value=0)
    lots_tot = lots.sum(axis=1)
    origins = list(lots.sum().sort_values(ascending=False).index)

    ser = certs.set_index("Date")[f"LRC-TOT-{grade}"].dropna().astype(float)
    chg = ser.diff().dropna()
    cd = list(chg.index.sort_values())

    def lagged_chg(d):
        pos = int(np.searchsorted(cd, d))
        on_certs_day = pos < len(cd) and cd[pos] == d
        i = pos + (lag if on_certs_day else max(lag - 1, 0))  # an off-day's first certs day after it already counts as 1 day later
        return chg.loc[cd[i]] if 0 <= i < len(cd) else np.nan

    g_start = gr["PanelDate"].min()
    days = sorted([d for d in (set(lots_tot.index) | set(chg.index)) if d >= g_start], reverse=True)
    if not days:
        return "<div class='rwrap' style='padding:14px'>No data.</div>"
    all_max = max(float(lots[origins].max().max()), 1.0)
    l_scale = max(float(lots_tot.max()), 1.0)
    used_chg = {d: lagged_chg(d) for d in days}
    used_use = {d: (0.0 if pd.isna(lots_tot.get(d)) else lots_tot.get(d)) - used_chg[d]
               for d in days if pd.notna(used_chg[d])}
    c_scale = max((abs(v) for v in used_chg.values() if pd.notna(v)), default=1) or 1
    u_scale = max((abs(v) for v in used_use.values()), default=1) or 1

    def lcell(v):
        if pd.isna(v) or v == 0:
            return "<td></td>"
        v = int(v)
        alpha = min(v / all_max, 1.0) * 0.85
        return f"<td style='background:rgba(31,157,111,{alpha:.2f})'>{v:,}</td>"

    def totcell(v, sc):
        v = int(round(v)) if pd.notna(v) else 0
        bar = f"<i style='width:{v / sc * 100:.1f}%'></i>" if v else ""
        return f"<td class='cbl'>{bar}<span>{v:,}</span></td>"

    def chgcell(v):
        if pd.isna(v):
            return "<td class='na sep'></td>"
        v = int(round(v))
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / c_scale * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb sep'>{bar}<span class='{cls}'>{v:+,}</span></td>"

    def usecell(v):
        # Usage = Grading - Certs change: lots graded that weren't offset by a matching rise in
        # certified stocks (i.e. graded coffee that left the certified pool / was used).
        if pd.isna(v):
            return "<td class='na'></td>"
        v = int(round(v))
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / u_scale * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb'>{bar}<span class='{cls}'>{v:+,}</span></td>"

    lag_note = "same certs day" if lag == 0 else f"certs {lag} certs-day{'s' if lag != 1 else ''} after"
    head = [f"<div class='mt' style='margin-bottom:4px'>Grading (lots) & LRC Certified Stocks Change (lots), by day "
            f"&mdash; {lag_note} the grading date</div>",
            "<div class='rwrap' style='height:", height, "'><table class='rpt'><thead>",
            "<tr class='h1'><th class='dt' rowspan='2'>Date</th>",
            f"<th colspan='{len(origins) + 1}'>Lots Graded by Origin</th>",
            "<th colspan='2' class='sep certs-hdr'>LRC Certs</th></tr><tr class='h2'>"]
    head += [f"<th>{o}</th>" for o in origins] + ["<th>Total</th><th class='sep certs-hdr'>Change</th><th class='certs-hdr'>Usage</th></tr></thead><tbody>"]

    body = []
    for d in (days[:nrows] if nrows else days):
        row = [f"<tr><td class='d'>{d.strftime('%d-%b-%y')}</td>"]
        row += [lcell(lots.loc[d, o] if d in lots.index else np.nan) for o in origins]
        row.append(totcell(lots_tot.get(d, 0), l_scale))
        row.append(chgcell(used_chg.get(d, np.nan)))
        row.append(usecell(used_use.get(d, np.nan)))
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


# ---------------------------------------------------------------------------------------------
# Arabica (KC) grading, from the ICE daily certified-stock reports (Database/Main/KC/kc_grading)
# ---------------------------------------------------------------------------------------------
KC_GR_PORTS = ["Antwerp", "Barcelona", "Ham/Bre", "Houston", "Miami", "New Orleans", "New York", "Virginia"]
KC_GR_PORT_SHORT = {"Antwerp": "ANT", "Barcelona": "BAR", "Ham/Bre": "HA/BR", "Houston": "HOU", "Miami": "MIAMI",
                    "New Orleans": "NOLA", "New York": "NY", "Virginia": "VA"}
KC_GR_COLORS = {"Brazil": NAVY, "Honduras": TEAL, "Peru": AMBER, "Mexico": RED, "Nicaragua": GREEN}
KC_GR_OTHER = "#c5cbdd"
KC_GR_CY_COLORS = ["#8a94a8", RED, NAVY]  # oldest -> newest crop year shown


@st.cache_data(ttl=600)
def load_kc_grading():
    g = pd.read_parquet(DB_DIR / "Main" / "KC" / "kc_grading.parquet")
    g["Date"] = pd.to_datetime(g["Date"])
    days = pd.read_parquet(DB_DIR / "Main" / "KC" / "kc_grading_days.parquet")
    return g, pd.Series(sorted(pd.to_datetime(days["Date"]).unique()), name="Date")


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_wide(g: pd.DataFrame, days: pd.Series, tag: str, by: str = "Origin") -> pd.DataFrame:
    """Bags per reported day (rows) by origin/port (columns), biggest first. A reported day with no
    row for a block means ICE showed nothing there, i.e. zero. Days we hold no file for are simply absent."""
    days = pd.DatetimeIndex(days)
    s = g[g["Tag"] == tag].groupby(["Date", by])["Bags"].sum().unstack(fill_value=0)
    s = s.reindex(days, fill_value=0)
    return s[s.sum().sort_values(ascending=False).index]


def kc_gr_colors(origins) -> dict:
    soft = ["#9b6bb3", "#6b7fb5", "#c0722c", "#4a5578", "#8fa3d1", "#b58f4a", GREY, "#7fa8b5"]
    out, i = {}, 0
    for o in origins:
        if o in KC_GR_COLORS:
            out[o] = KC_GR_COLORS[o]
        else:
            out[o] = tint(soft[i % len(soft)], max(0.85 - 0.05 * i, 0.4))
            i += 1
    return out


def kc_range(pick: str, dmin: pd.Timestamp, dmax: pd.Timestamp):
    months = {"Last 1M": 1, "Last 3M": 3, "Last 6M": 6, "Last 1Y": 12}
    if pick == "All":
        return dmin, dmax
    return dmax - pd.DateOffset(months=months[pick]), dmax


# ---- small html cell helpers -----------------------------------------------------------------
def _fmt_i(v):
    return f"{int(round(v)):,}"


def _heat_td(v, mx, rgb="31,157,111"):
    if pd.isna(v) or v == 0:
        return "<td></td>"
    return f"<td style='background:rgba({rgb},{min(abs(v) / mx, 1.0) * 0.85:.2f})'>{_fmt_i(v)}</td>"


def _bar_td(v, sc, cls="cbl"):
    v = 0 if pd.isna(v) else v
    bar = f"<i style='width:{abs(v) / sc * 100:.1f}%'></i>" if v else ""
    return f"<td class='{cls}'>{bar}<span>{_fmt_i(v)}</span></td>"


def _delta_td(v, sc, cls="cb", pct=False):
    if pd.isna(v):
        return f"<td class='na {cls.replace('cb', '').strip()}'></td>"
    bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / sc * 50:.1f}%'></i>" if v else ""
    tone = "pos" if v > 0 else "neg" if v < 0 else ""
    txt = f"{v:+.1f}%" if pct else f"{int(round(v)):+,}"
    return f"<td class='{cls}'>{bar}<span class='{tone}'>{txt}</span></td>"


# ---- Grading tables -------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_daily_html(g: pd.DataFrame, days: pd.Series, height: str = "60vh", nrows: int = 0) -> str:
    """One row per reported day: Passed by origin (heat), Passed / Failed totals, Pass %, Pending stock."""
    days = pd.DatetimeIndex(days)
    p = kc_gr_wide(g, pd.Series(days), "Passed")
    f = kc_gr_wide(g, pd.Series(days), "Failed").sum(axis=1)
    pend = kc_gr_wide(g, pd.Series(days), "Pending").sum(axis=1)
    origins = [o for o in p.columns if p[o].sum() > 0]
    pt = p.sum(axis=1)
    rate = (pt / (pt + f).replace(0, np.nan) * 100)
    mx = max(float(p[origins].max().max()), 1.0)
    out = ["<div class='rwrap' style='height:", height, "'><table class='rpt cmp'><thead>",
           "<tr class='h1'><th class='dt' rowspan='2'>Date</th>",
           f"<th colspan='{len(origins) + 1}'>Bags Passed by Origin</th>",
           "<th colspan='4' class='sep'>Grading Summary</th></tr><tr class='h2'>"]
    out += [f"<th>{o}</th>" for o in origins]
    out += ["<th>Total</th><th class='sep'>Failed</th><th>Pass %</th><th>Pending</th><th>Passed + Failed</th></tr></thead><tbody>"]
    pt_sc, f_sc, pe_sc = max(float(pt.max()), 1.0), max(float(f.max()), 1.0), max(float(pend.max()), 1.0)
    for d in (days[::-1][:nrows] if nrows else days[::-1]):
        r = [f"<tr><td class='d'>{d.strftime('%d-%b-%y')}</td>"]
        r += [_heat_td(p.loc[d, o], mx) for o in origins]
        r.append(_bar_td(pt[d], pt_sc))
        r.append(_heat_td(f[d], f_sc, "201,74,74").replace("<td", "<td class='sep'", 1) if f[d] else "<td class='sep'></td>")
        r.append(f"<td>{'' if pd.isna(rate[d]) else f'{rate[d]:.1f}%'}</td>")
        r.append(_bar_td(pend[d], pe_sc))
        r.append(f"<td>{_fmt_i(pt[d] + f[d]) if pt[d] + f[d] else ''}</td></tr>")
        out.append("".join(r))
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_monthly_html(g: pd.DataFrame, days: pd.Series, tag: str, height: str = "60vh") -> str:
    """Month x origin, bags, one heat scale across every origin. Months with unfetched days run low."""
    days = pd.DatetimeIndex(days)
    w = kc_gr_measure(g, pd.Series(days), tag)
    mo = w.groupby(w.index.to_period("M")).sum()
    mo = mo[[o for o in mo.columns if mo[o].sum() > 0]]
    tot = mo.sum(axis=1)
    rgb = {"Passed": "31,157,111", "Failed": "201,74,74", "Total": "31,138,156"}[tag]
    mx, sc = max(float(mo.max().max()), 1.0), max(float(tot.max()), 1.0)
    out = ["<div class='rwrap' style='height:", height, "'><table class='rpt cmp'><thead><tr class='h1'>",
           f"<th class='dt' rowspan='2'>Month</th><th colspan='{len(mo.columns) + 1}'>Bags {'Passed + Failed' if tag == 'Total' else tag} by Origin</th></tr><tr class='h2'>"]
    out += [f"<th>{o}</th>" for o in mo.columns] + ["<th>Total</th></tr></thead><tbody>"]
    for pr in mo.index[::-1]:
        out.append(f"<tr><td class='d'>{pr.strftime('%b %Y')}</td>" + "".join(_heat_td(mo.loc[pr, o], mx, rgb) for o in mo.columns)
                   + _bar_td(tot[pr], sc) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_monthly_matrix_html(mser: pd.Series, m: int = 7, signed: bool = False, pct: bool = False) -> str:
    """Crop year x month matrix of a monthly Series (PeriodIndex). Only months that exist are filled."""
    if mser.empty:
        return "<div class='rwrap' style='padding:14px'>No data.</div>"
    per = mser.index
    cy = np.where(per.month >= m, per.year, per.year - 1)
    months = [(m - 1 + i) % 12 + 1 for i in range(12)]
    tbl = (pd.DataFrame({"v": mser.values.astype(float), "cy": cy, "mo": per.month})
           .pivot_table(index="cy", columns="mo", values="v", aggfunc="sum").reindex(columns=months))
    ytot = tbl.sum(axis=1, min_count=1)
    sc = max(float(np.nanmax(np.abs(tbl.values))), 1.0)
    ysc = max(float(np.nanmax(np.abs(ytot.values))), 1.0)

    def cell(v, s, cls="cbl"):
        if pd.isna(v):
            return "<td class='na'></td>"
        if pct:
            return _delta_td(v, s, "cb", pct=True)
        if signed:
            return _delta_td(v, s, "cb")
        return _bar_td(v, s, cls)

    out = ["<div class='rwrap' style='height:auto'><table class='rpt mx'><thead><tr class='h2'>"
           f"<th class='dt'>{'Year' if m == 1 else 'Crop yr'}</th>"]
    out += [f"<th>{MONTH_ABBR[mo - 1].upper()}</th>" for mo in months]
    out += [] if pct else ["<th class='sep'>Total</th>"]
    out += ["</tr></thead><tbody>"]
    for yr in tbl.index:
        row = [f"<tr><td class='d'>{crop_label(int(yr), m)}</td>"] + [cell(tbl.loc[yr, mo], sc) for mo in months]
        if not pct:
            row.append(cell(ytot[yr], ysc, "cbl sep") if not signed else _delta_td(ytot[yr], ysc, "cb sep"))
        out.append("".join(row) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


def kc_monthly_sum(s: pd.Series) -> pd.Series:
    return s.groupby(s.index.to_period("M")).sum()


# ---- Grading charts -------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_bar_fig(wide: pd.DataFrame, title: str, show_all: bool, top_n: int, start: pd.Timestamp,
                  end: pd.Timestamp, height: int = 340) -> go.Figure:
    w = wide[(wide.index >= start) & (wide.index <= end)]
    order = [o for o in w.sum().sort_values(ascending=False).index if w[o].sum() > 0]
    colors = kc_gr_colors(list(wide.columns))
    shown, minors = (order, []) if show_all else (order[:top_n], order[top_n:])
    fig = go.Figure()
    for o in shown:
        fig.add_trace(go.Bar(x=w.index, y=w[o], name=o, marker_color=colors[o],
                             hovertemplate="%{y:,.0f}<extra>" + o + "</extra>"))
    if minors:
        fig.add_trace(go.Bar(x=w.index, y=w[minors].sum(axis=1), name="Other", marker_color=KC_GR_OTHER,
                             hovertemplate="%{y:,.0f}<extra>Other</extra>"))
    chart_layout(fig, title + ("" if show_all else f" (Top {top_n} + Other)"), height)
    fig.update_layout(barmode="stack", bargap=0.15, yaxis=dict(title=None, tickformat=","))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_pending_fig(wide: pd.DataFrame, show_all: bool, top_n: int, start: pd.Timestamp,
                      end: pd.Timestamp, height: int = 340) -> go.Figure:
    w = wide[(wide.index >= start) & (wide.index <= end)]
    order = [o for o in w.sum().sort_values(ascending=False).index if w[o].sum() > 0]
    colors = kc_gr_colors(list(wide.columns))
    shown, minors = (order, []) if show_all else (order[:top_n], order[top_n:])
    fig = go.Figure()
    for o in shown:
        fig.add_trace(go.Scatter(x=w.index, y=w[o], mode="lines", name=o, stackgroup="one",
                                 line=dict(width=0.6, color=colors[o]), fillcolor=colors[o],
                                 hovertemplate="%{y:,.0f}<extra>" + o + "</extra>"))
    if minors:
        fig.add_trace(go.Scatter(x=w.index, y=w[minors].sum(axis=1), mode="lines", name="Other", stackgroup="one",
                                 line=dict(width=0.6, color=KC_GR_OTHER), fillcolor=KC_GR_OTHER,
                                 hovertemplate="%{y:,.0f}<extra>Other</extra>"))
    return chart_layout(fig, "Pending Grading Queue (bags)" + ("" if show_all else f" (Top {top_n} + Other)"), height)


def kc_cum_lines_fig(s: pd.Series, title: str, m: int, last: pd.Timestamp, n_years: int = 3,
                     height: int = 320) -> go.Figure:
    """Cumulative sum of a daily flow through the crop year (resets on the 1st of month m), one line
    per crop year for the latest `n_years` (no bands). Years that began long before the data are skipped."""
    fig = go.Figure()
    first = s.index.min()
    first_cy = first.year if first.month >= m else first.year - 1
    start0 = pd.Timestamp(year=first_cy, month=m, day=1)
    if (first - start0).days > 45:
        first_cy += 1
        start0 = pd.Timestamp(year=first_cy, month=m, day=1)
    idx = pd.date_range(start0, last)
    daily = s.reindex(idx, fill_value=0)
    cy = np.where(idx.month >= m, idx.year, idx.year - 1)
    cum = daily.groupby(cy).cumsum()
    starts = pd.to_datetime([f"{y}-{m:02d}-01" for y in cy])
    w = pd.DataFrame({"v": cum.values.astype(float), "x": (idx - starts).days + 1, "yr": cy}, index=idx)
    w = w[w["x"] <= 366]  # 366 so a leap year keeps its last day
    yrs = sorted(w["yr"].unique())[-n_years:]
    pal = KC_GR_CY_COLORS[-len(yrs):]
    for yr, color in zip(yrs, pal):
        gg = w[w["yr"] == yr].sort_values("x")
        lbl = crop_label(int(yr), m)
        fig.add_trace(go.Scatter(x=gg["x"], y=gg["v"], mode="lines", name=lbl,
                                 line=dict(color=color, width=3 if color == NAVY else 2),
                                 hovertemplate="%{y:,.0f}<extra>" + lbl + "</extra>"))
        fig.add_trace(go.Scatter(x=[gg["x"].iloc[-1]], y=[gg["v"].iloc[-1]], mode="markers+text", showlegend=False,
                                 marker=dict(color=color, size=6), text=[f"{gg['v'].iloc[-1]:,.0f}"],
                                 textposition="middle right", textfont=dict(size=10, color=color), hoverinfo="skip"))
    order = [(m - 1 + i) % 12 for i in range(12)]
    offs = np.concatenate([[0], np.cumsum([MONTH_DAYS[k] for k in order])])[:12] + 1
    chart_layout(fig, title, height)
    fig.update_layout(xaxis=dict(tickmode="array", tickvals=list(offs[::2]),
                                 ticktext=[MONTH_ABBR[order[i]] for i in range(0, 12, 2)], range=[1, 380]),
                      legend=dict(font=dict(size=10)))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cum_lines_cached(s: pd.Series, title: str, m: int, last: pd.Timestamp) -> go.Figure:
    return kc_cum_lines_fig(s, title, m, last)


KC_GR_PORT_COUNTRY = {"Antwerp": "Belgium", "Barcelona": "Spain", "Ham/Bre": "Germany", "Houston": "USA",
                      "Miami": "USA", "New Orleans": "USA", "New York": "USA", "Virginia": "USA"}
KC_GR_PORT_COLORS = {"Antwerp": NAVY, "Barcelona": GREEN, "Ham/Bre": "#6b7fb5", "Houston": "#9b6bb3", "Miami": AMBER,
                     "New Orleans": RED, "New York": TEAL, "Virginia": GREY}


def _rate_rgb(p: float) -> tuple:
    """Pastel red (<=50%) -> pale yellow (75%) -> pastel green (100%)."""
    stops = [(50, (233, 150, 150)), (75, (250, 238, 180)), (100, (150, 208, 168))]
    p = min(max(p, 50.0), 100.0)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if p <= b:
            t = (p - a) / (b - a)
            return tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return stops[-1][1]


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_measure(g: pd.DataFrame, days: pd.Series, measure: str, by: str = "Origin") -> pd.DataFrame:
    """Daily bags by origin (or port) for Passed, Failed or Total (= Passed + Failed)."""
    if measure != "Total":
        return kc_gr_wide(g, pd.Series(days), measure, by=by)
    w = kc_gr_wide(g, pd.Series(days), "Passed", by=by).add(kc_gr_wide(g, pd.Series(days), "Failed", by=by), fill_value=0)
    return w[w.sum().sort_values(ascending=False).index]


@st.cache_data(ttl=3600, show_spinner=False)
def kc_passrate_matrix_html(pm: pd.Series, fm: pd.Series, m: int = 7) -> str:
    """Crop year x month pass rate (Passed / (Passed + Failed)), pastel red to green."""
    idx = pm.index.union(fm.index)
    pm, fm = pm.reindex(idx, fill_value=0).astype(float), fm.reindex(idx, fill_value=0).astype(float)
    if len(idx) == 0:
        return "<div class='rwrap' style='padding:14px'>No data.</div>"
    cy = np.where(idx.month >= m, idx.year, idx.year - 1)
    months = [(m - 1 + i) % 12 + 1 for i in range(12)]
    df = pd.DataFrame({"p": pm.values, "f": fm.values, "cy": cy, "mo": idx.month})
    pp = df.pivot_table(index="cy", columns="mo", values="p", aggfunc="sum").reindex(columns=months)
    ff = df.pivot_table(index="cy", columns="mo", values="f", aggfunc="sum").reindex(columns=months)
    rate = pp / (pp + ff).replace(0, np.nan) * 100
    yrate = pp.sum(axis=1) / (pp.sum(axis=1) + ff.sum(axis=1)).replace(0, np.nan) * 100

    def cell(v, cls=""):
        if pd.isna(v):
            return f"<td class='na {cls}'></td>"
        r, gr, b = _rate_rgb(float(v))
        return f"<td class='{cls}' style='background:rgb({r},{gr},{b})'>{v:.0f}%</td>"

    out = ["<div class='rwrap' style='height:auto'><table class='rpt mx big'><thead><tr class='h2'>"
           f"<th class='dt'>{'Year' if m == 1 else 'Crop yr'}</th>"]
    out += [f"<th>{MONTH_ABBR[mo - 1].upper()}</th>" for mo in months] + ["<th class='sep'>Year</th></tr></thead><tbody>"]
    for yr in rate.index:
        out.append(f"<tr><td class='d'>{crop_label(int(yr), m)}</td>" + "".join(cell(rate.loc[yr, mo]) for mo in months)
                   + cell(yrate[yr], "sep") + "</tr>")
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_pending_port_fig(g: pd.DataFrame, days: pd.Series, start: pd.Timestamp, end: pd.Timestamp,
                           height: int = 340) -> go.Figure:
    w = kc_gr_wide(g, pd.Series(days), "Pending", by="Port")
    w = w[(w.index >= start) & (w.index <= end)]
    fig = go.Figure()
    for p in [p for p in KC_GR_PORTS if p in w.columns and w[p].sum() > 0]:
        fig.add_trace(go.Scatter(x=w.index, y=w[p], mode="lines", name=KC_GR_PORT_SHORT[p], stackgroup="one",
                                 line=dict(width=0.6, color=KC_GR_PORT_COLORS[p]), fillcolor=KC_GR_PORT_COLORS[p],
                                 hovertemplate="%{y:,.0f}<extra>" + p + "</extra>"))
    return chart_layout(fig, "Pending Grading Queue | Per Port (bags)", height)


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_pending_combo_fig(g: pd.DataFrame, days: pd.Series, origins: tuple, ports: tuple,
                            start: pd.Timestamp, end: pd.Timestamp, height: int = 340) -> go.Figure:
    days = pd.DatetimeIndex(days)
    src = g[g["Tag"] == "Pending"]
    pal = [NAVY, TEAL, AMBER, RED, GREEN, "#9b6bb3", "#6b7fb5", "#c0722c", "#4a5578", "#8fa3d1"]
    fig = go.Figure()
    k = 0
    for o in origins:
        for p in ports:
            s = src[(src["Origin"] == o) & (src["Port"] == p)].groupby("Date")["Bags"].sum().reindex(days, fill_value=0)
            s = s[(s.index >= start) & (s.index <= end)]
            nm = f"{o} | {KC_GR_PORT_SHORT.get(p, p)}"
            fig.add_trace(go.Scatter(x=s.index, y=s, mode="lines", name=nm, line=dict(color=pal[k % len(pal)], width=2),
                                     hovertemplate="%{y:,.0f}<extra>" + nm + "</extra>"))
            k += 1
    return chart_layout(fig, "Pending Grading Queue | Chosen Origins and Ports (bags)", height)


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_day_pf(g: pd.DataFrame, days: pd.Series, origin: str, port: str) -> pd.DataFrame:
    """Daily Passed and Failed bags for one origin (or all) at one port (or all)."""
    days = pd.DatetimeIndex(days)
    out = {}
    for tag in ("Passed", "Failed"):
        s = g[g["Tag"] == tag]
        if origin != "All origins":
            s = s[s["Origin"] == origin]
        if port != "Total Ports":
            s = s[s["Port"] == port]
        out[tag] = s.groupby("Date")["Bags"].sum().reindex(days, fill_value=0)
    return pd.DataFrame(out)


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_month_pf(g: pd.DataFrame, days: pd.Series, origin: str, port: str) -> pd.DataFrame:
    """Monthly Passed and Failed bags for one origin (or all) at one port (or all)."""
    d = kc_gr_day_pf(g, pd.Series(days), origin, port)
    return d.groupby(d.index.to_period("M")).sum()


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_rate_bar_fig(df: pd.DataFrame, title: str, start: pd.Timestamp, end: pd.Timestamp,
                       height: int = 380) -> go.Figure:
    """Pass rate per grading day as bars, labelled with the bags passed that day. Only days with
    grading are drawn (a day with nothing graded has no rate)."""
    d = df[(df.index >= start) & (df.index <= end)]
    d = d[(d["Passed"] + d["Failed"]) > 0]
    rate = d["Passed"] / (d["Passed"] + d["Failed"]) * 100
    tot_p, tot_f = float(d["Passed"].sum()), float(d["Failed"].sum())
    avg = tot_p / (tot_p + tot_f) * 100 if tot_p + tot_f else 0.0
    xs = d.index.strftime("%d %b %y")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=rate, marker_color=NAVY, text=[f"{v:,.0f}" for v in d["Passed"]],
                         textposition="outside", textangle=-90, textfont=dict(size=10, color="#1a1a2e"),
                         cliponaxis=False, customdata=np.stack([d["Passed"], d["Failed"]], axis=-1),
                         hovertemplate="%{y:.1f}%<br>Passed %{customdata[0]:,.0f} | Failed %{customdata[1]:,.0f}<extra></extra>"))
    if len(d):
        fig.add_hline(y=avg, line=dict(color=GREY, width=1, dash="dot"),
                      annotation_text=f"Period {avg:.0f}%", annotation_position="top left",
                      annotation_font=dict(size=10, color=GREY))
    chart_layout(fig, title, height)
    fig.update_layout(bargap=0.25, showlegend=False, margin=dict(t=48, b=8, l=8, r=8),
                      xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9)),
                      yaxis=dict(ticksuffix="%", range=[0, 122], tickvals=[0, 20, 40, 60, 80, 100]))
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def kc_gr_pf_bars_fig(mf: pd.DataFrame, title: str, proportion: bool = False, height: int = 340) -> go.Figure:
    xs = mf.index.strftime("%b %y")
    fig = go.Figure()
    if proportion:
        tot = (mf["Passed"] + mf["Failed"]).replace(0, np.nan)
        pv, fv = mf["Passed"] / tot * 100, mf["Failed"] / tot * 100
    else:
        pv, fv = mf["Passed"], mf["Failed"]
    for name, v, color in (("Failed", fv, RED), ("Passed", pv, GREEN)):
        fig.add_trace(go.Bar(x=xs, y=v, name=name, marker_color=color,
                             hovertemplate=("%{y:.1f}%" if proportion else "%{y:,.0f}") + "<extra>" + name + "</extra>"))
    chart_layout(fig, title, height)
    fig.update_layout(barmode="stack", bargap=0.2, xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9)),
                      yaxis=dict(tickformat=",", ticksuffix="%" if proportion else "", range=[0, 100] if proportion else None),
                      legend=dict(orientation="h", y=1.0, x=1, xanchor="right", yanchor="bottom"),
                      margin=dict(t=56, b=8, l=8, r=8))
    return fig


KC_PORT_COUNTRY = {"AN": "Belgium", "BA": "Spain", "HA": "Germany", "HO": "USA", "MI": "USA", "NO": "USA", "NY": "USA"}
KC_COUNTRY_COLORS = {"Belgium": "#4a63a8", "Spain": "#4a63a8", "Germany": "#4a63a8", "USA": TEAL}  # header bands: Europe slate blue, USA teal
KC_COUNTRY_CHART_COLORS = {"Belgium": NAVY, "Spain": "#6b7fb5", "Germany": "#8fa3d1", "USA": TEAL}
KC_GROUP_START = {"BA": "gs", "HA": "gs", "HO": "sep"}  # Europe|USA gets the heavy divider


def _kc_gs(td: str, p: str) -> str:
    """Add the group-divider class for the first port of a country to an already-built <td>."""
    cls = KC_GROUP_START.get(p)
    return td.replace("class='", f"class='{cls} ", 1) if cls and "class='" in td else td


def kc_matrix_head(ports: list, extra: list) -> list:
    """Two header rows for the Arabica origin x port matrices: a colour-coded country band over the
    port codes (ports shaded in their country's colour), Europe on the left and USA on the right."""
    groups = []
    for p in ports:
        c = KC_PORT_COUNTRY[p]
        if groups and groups[-1][0] == c:
            groups[-1][1].append(p)
        else:
            groups.append([c, [p]])
    h = ["<div class='rwrap' style='height:auto'><table class='rpt static kcmx'><thead><tr class='h1'>",
         "<th class='dt l' rowspan='2'>Origin</th>"]
    for i, (c, ps) in enumerate(groups):
        col = KC_COUNTRY_COLORS[c]
        edge = "border-left:2px solid #ffffff;" if i else ""
        h.append(f"<th colspan='{len(ps)}' style='background:{col};{edge}letter-spacing:.09em;font-size:11px;"
                 f"text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,.55)'>{c}</th>")
    h += [f"<th class='sep' rowspan='2'>{e}</th>" for e in extra]
    h += ["</tr><tr class='h2'>"]
    for i, (c, ps) in enumerate(groups):
        col = KC_COUNTRY_COLORS[c]
        for j, p in enumerate(ps):
            edge = "border-left:2px solid #ffffff;" if (i and j == 0) else ""
            h.append(f"<th style='background:color-mix(in srgb, {col} 58%, #0a2463);{edge}'>{KC_PORT_NAMES[p]}</th>")
    h += ["</tr></thead><tbody>"]
    return h


@st.cache_data(ttl=3600, show_spinner=False)
def kc_country_certs_fig(df: pd.DataFrame) -> go.Figure:
    """Stacked area of certs per country of the port (Belgium, Spain, Germany, USA)."""
    df = df[df["Date"] >= KC_BREAKDOWN_START]
    fig = go.Figure()
    for c in ["Belgium", "Spain", "Germany", "USA"]:
        cols = [f"KC-TOT-{p}" for p, ct in KC_PORT_COUNTRY.items() if ct == c and f"KC-TOT-{p}" in df.columns]
        y = df[cols].astype(float).ffill(limit=5).fillna(0).sum(axis=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=y, mode="lines", name=c, stackgroup="one",
                                 line=dict(width=0.6, color=KC_COUNTRY_CHART_COLORS[c]), fillcolor=KC_COUNTRY_CHART_COLORS[c],
                                 hovertemplate="%{y:,.0f}<extra>" + c + "</extra>"))
    return chart_layout(fig, "Certs Per Country of Port")


# ---- Certs & Grading (usage) ----------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_daily(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame) -> pd.DataFrame:
    """Same-day Usage = Bags Passed - change in total certs, on every day we hold a grading file
    for AND ICE published certs. Usage is the certified stock that left the pool that day."""
    days = pd.DatetimeIndex(days)
    passed = kc_gr_wide(g, pd.Series(days), "Passed").sum(axis=1)
    tot = kc.set_index("Date")["KC-TOT-TOT"].astype(float).dropna()
    chg = tot.diff()
    idx = days[days.isin(chg.dropna().index)]
    df = pd.DataFrame({"Passed": passed.reindex(idx), "Change": chg.reindex(idx), "Level": tot.reindex(idx)})
    df["Usage"] = df["Passed"] - df["Change"]
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def kc_origin_certs(kc: pd.DataFrame) -> pd.DataFrame:
    """Certs per origin by name. LSEG has no Kenya RIC, so Kenya is the residual of the total."""
    cols = {f"KC-{c}-TOT": n for c, n in KC_ORIGIN_NAMES.items() if f"KC-{c}-TOT" in kc.columns}
    o = kc.set_index("Date")[list(cols)].astype(float).rename(columns=cols).ffill(limit=5).fillna(0)  # a blank RIC means no stock of that origin
    tot = kc.set_index("Date")["KC-TOT-TOT"].astype(float)
    o["Kenya"] = (tot - o.sum(axis=1)).clip(lower=0)
    return o


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_monthly(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame) -> pd.DataFrame:
    days = pd.DatetimeIndex(days)
    d = kc_cg_daily(g, pd.Series(days), kc)
    tot = kc.set_index("Date")["KC-TOT-TOT"].astype(float).dropna()
    per = d.index.to_period("M")
    m = d.groupby(per).agg(Passed=("Passed", "sum"), Change=("Change", "sum"), Usage=("Usage", "sum"), Days=("Passed", "size"))
    m["Level"] = tot.groupby(tot.index.to_period("M")).last().reindex(m.index)
    m["Avg"] = tot.groupby(tot.index.to_period("M")).mean().reindex(m.index)
    m["Cal"] = tot[tot.index >= d.index.min()].groupby(tot[tot.index >= d.index.min()].index.to_period("M")).size().reindex(m.index)
    m["UsagePct"] = m["Usage"] / m["Avg"] * 100
    return m


def _chg_heat_td(v, mx):
    """Signed change cell: green up, red down, one shared scale."""
    if pd.isna(v) or v == 0:
        return "<td></td>"
    rgb = "31,157,111" if v > 0 else "201,74,74"
    return f"<td style='background:rgba({rgb},{min(abs(v) / mx, 1.0) * 0.85:.2f})'>{int(round(v)):+,}</td>"


def _cg_origin_split(p: pd.DataFrame, chg_o: pd.DataFrame, show_all: bool, top_n: int = 5, f: pd.DataFrame = None):
    """Origins with Passed bags, biggest first; Top-N + Other unless show_all. Returns the column labels
    and matching Passed / certs-change / Failed frames (Other = sum of the rest)."""
    origins = [o for o in p.columns if p[o].sum() > 0]
    shown, minors = (origins, []) if show_all else (origins[:top_n], origins[top_n:])
    pp = p[shown].copy()
    cc = chg_o.reindex(columns=shown, fill_value=0).copy()
    ff = (f if f is not None else p * 0).reindex(columns=shown, fill_value=0).copy()
    if minors:
        pp["Other"] = p[minors].sum(axis=1)
        cc["Other"] = chg_o.reindex(columns=minors, fill_value=0).sum(axis=1)
        ff["Other"] = (f if f is not None else p * 0).reindex(columns=minors, fill_value=0).sum(axis=1)
    return list(pp.columns), pp, cc, ff


_ABBR = {v: k for k, v in KC_ORIGIN_NAMES.items()}
_ABBR["Other"] = "OTH"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_queue_frame(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame) -> pd.DataFrame:
    """Per reported day: Failed bags, Pending stock, Certs level and Fresh Pending (= change in Pending + Passed + Failed)."""
    days = pd.DatetimeIndex(days)
    p = kc_gr_wide(g, pd.Series(days), "Passed").sum(axis=1)
    f = kc_gr_wide(g, pd.Series(days), "Failed").sum(axis=1)
    pend = kc_gr_wide(g, pd.Series(days), "Pending").sum(axis=1)
    tot = kc.set_index("Date")["KC-TOT-TOT"].astype(float)
    return pd.DataFrame({"Failed": f, "Pending": pend, "Certs": tot.reindex(days), "Fresh": pend.diff() + p + f})


@st.cache_data(ttl=3600, show_spinner=False)
def kc_fresh_frame(g: pd.DataFrame, days: pd.Series, by: str) -> pd.DataFrame:
    """Fresh Pending per origin (or port) per reported day = change in that Pending stock + Passed + Failed."""
    days = pd.Series(days)
    pend = kc_gr_wide(g, days, "Pending", by=by)
    pas = kc_gr_wide(g, days, "Passed", by=by)
    fail = kc_gr_wide(g, days, "Failed", by=by)
    cols = sorted(set(pend.columns) | set(pas.columns) | set(fail.columns))
    pend, pas, fail = (x.reindex(columns=cols, fill_value=0) for x in (pend, pas, fail))
    return pend.diff() + pas + fail


def _fresh_cols(fr_all: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Fresh Pending on the table's columns (Other = everything not shown) plus an exact Total."""
    shown = [c for c in cols if c != "Other"]
    out = fr_all.reindex(columns=shown, fill_value=0).copy()
    if "Other" in cols:
        out["Other"] = fr_all.drop(columns=[c for c in shown if c in fr_all.columns]).sum(axis=1)
    out["Total"] = fr_all.sum(axis=1)
    return out


def _fresh_td(v, mx: float, sep: bool = False) -> str:
    return _heat_td(v, mx).replace("<td", "<td class='pr sep'" if sep else "<td class='pr'", 1)


def _cg_queue_cells(q, sc: dict) -> str:
    """Pending stock (Grading Queue) and the Certs level, each in its own column group."""
    if q is None:
        return "<td class='na sep'></td><td class='na sep'></td>"
    pend = "" if pd.isna(q["Pending"]) or not q["Pending"] else _fmt_i(q["Pending"])
    cert = "" if pd.isna(q["Certs"]) else _fmt_i(q["Certs"])
    return f"<td class='sep'>{pend}</td><td class='tot sep'>{cert}</td>"


def _queue_scales(q: pd.DataFrame) -> dict:
    return {"qf": max(float(q["Failed"].max()), 1.0), "qfp": max(float(q["Fresh"].abs().max()), 1.0)}


def _cg_head(first_col: str, cols: list, with_rate: bool = False, with_queue: bool = False) -> list:
    """Header for the Certs & Grading tables: Passed | (Pass %) | Certs Change | Usage, each split by origin plus a Total."""
    n = len(cols) + 1
    h = ["<table class='rpt cmp" + (" tiny" if with_rate else "") + "'><thead><tr class='h1'>",
         f"<th class='dt' rowspan='2'>{first_col}</th>",
         f"<th colspan='{n}'>Bags Passed by Origin</th>"]
    if with_rate:
        h.append(f"<th colspan='{n}' class='sep'>Pass % by Origin</th>")
    h += [f"<th colspan='{n}' class='sep certs-hdr'>Certs Change by Origin</th>",
          f"<th colspan='{n}' class='sep certs-hdr'>Usage by Origin</th>"]
    if with_queue:
        h.append(f"<th colspan='{n}' class='sep'>Fresh Pending by Origin</th>")
        h.append("<th class='sep'>Grading Queue</th><th class='sep certs-hdr'>KC Certs</th>")
    h.append("</tr><tr class='h2'>")
    groups = 4 if with_rate else 3
    for grp in range(groups):
        certs = grp >= groups - 2
        sep_first = grp >= 1
        for i, o in enumerate(cols + ["Total"]):
            is_pr = with_rate and grp == 1
            cls = ("certs-hdr" if certs else "") + (" sep" if (sep_first and i == 0) else "") + (" pr" if is_pr else "")
            lbl = (_ABBR.get(o, o[:3].upper()) if o != "Total" else "Tot") if is_pr else o
            h.append(f"<th class='{cls.strip()}'>{lbl}</th>" if cls.strip() else f"<th>{lbl}</th>")
    if with_queue:
        for i, o in enumerate(cols + ["Total"]):
            lbl = _ABBR.get(o, o[:3].upper()) if o != "Total" else "Tot"
            h.append(f"<th class='pr{' sep' if i == 0 else ''}'>{lbl}</th>")
        h.append("<th class='sep'>Pending</th><th class='sep certs-hdr'>Level</th>")
    h.append("</tr></thead><tbody>")
    return h


def _rate_td(v, sep: bool = False) -> str:
    cls = " class='pr sep'" if sep else " class='pr'"
    if pd.isna(v):
        return f"<td{cls}></td>"
    alpha = 0.08 + 0.77 * min(max(float(v), 0.0), 100.0) / 100.0
    return f"<td{cls} style='background:rgba(31,157,111,{alpha:.2f})'>{v:.0f}%</td>"


def _cg_row(label: str, pas: pd.Series, chg: pd.Series, use: pd.Series, cols: list, sc: dict, has: bool = True,
            rate: pd.Series = None, queue=None, with_queue: bool = False, fresh: pd.Series = None) -> str:
    """One data row: Passed cells, (Pass % cells), Certs-change cells, Usage cells (origins then a Total each)."""
    r = [f"<tr><td class='d'>{label}</td>"]
    r += [_heat_td(pas[o], sc["p"]) for o in cols] + [_bar_td(pas.sum(), sc["pt"])]
    if rate is not None:
        r += [_rate_td(rate[o], i == 0) for i, o in enumerate(cols)] + [_rate_td(rate["Total"])]
    if has:
        for k, ser, tsc in (("c", chg, sc["ct"]), ("u", use, sc["ut"])):
            cells = [_chg_heat_td(ser[o], sc[k]) for o in cols]
            cells[0] = cells[0].replace("<td", "<td class='sep'", 1)
            r += cells + [_delta_td(ser.sum(), tsc)]
    else:
        r += ["<td class='na sep'></td>"] + ["<td class='na'></td>"] * len(cols) + ["<td class='na sep'></td>"] + ["<td class='na'></td>"] * len(cols)
    if with_queue:
        if fresh is not None:
            r += [_fresh_td(fresh[o], sc["fr"], i == 0) for i, o in enumerate(cols)] + [_fresh_td(fresh["Total"], sc["fr"])]
        r.append(_cg_queue_cells(queue, sc))
    return "".join(r) + "</tr>"


def _rate_frame(pp: pd.DataFrame, ff: pd.DataFrame, f_all_total: pd.Series) -> pd.DataFrame:
    """Pass % per shown column and in total (total uses every failed bag, including origins with no Passed)."""
    den = (pp + ff).replace(0, np.nan)
    r = pp / den * 100
    tp = pp.sum(axis=1)
    r["Total"] = tp / (tp + f_all_total).replace(0, np.nan) * 100
    return r


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_monthly_html(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame, show_all: bool = False,
                       height: str = "auto", with_rate: bool = False, with_queue: bool = False) -> str:
    days = pd.DatetimeIndex(days)
    d = kc_cg_daily(g, pd.Series(days), kc)
    p = kc_gr_wide(g, pd.Series(days), "Passed").reindex(d.index)
    f_full = kc_gr_wide(g, pd.Series(days), "Failed").reindex(d.index)
    chg_o = kc_origin_certs(kc).diff().reindex(d.index)
    cols, pp, cc, ff = _cg_origin_split(p, chg_o, show_all, f=f_full)
    per = d.index.to_period("M")
    lots, chg_m, ffm = pp.groupby(per).sum(), cc.groupby(per).sum(), ff.groupby(per).sum()
    rate = _rate_frame(lots, ffm, f_full.sum(axis=1).groupby(per).sum()) if with_rate else None
    use_m = lots - chg_m
    sc = {"p": max(float(lots.max().max()), 1.0), "pt": max(float(lots.sum(axis=1).max()), 1.0),
          "c": max(float(chg_m.abs().max().max()), 1.0), "ct": max(float(chg_m.sum(axis=1).abs().max()), 1.0),
          "u": max(float(use_m.abs().max().max()), 1.0), "ut": max(float(use_m.sum(axis=1).abs().max()), 1.0)}
    out = ["<div class='mt' style='margin-bottom:4px'>Monthly Grading, Certs Change and Usage by Origin (bags)</div>",
           f"<div class='rwrap' style='height:{height}'>"]
    out += _cg_head("Month", cols, with_rate, with_queue)
    qm = frm = None
    if with_queue:
        qd = kc_queue_frame(g, pd.Series(days), kc).reindex(d.index)
        qm = pd.DataFrame({"Failed": qd["Failed"].groupby(per).sum(), "Pending": qd["Pending"].groupby(per).last(),
                           "Certs": qd["Certs"].groupby(per).last(), "Fresh": qd["Fresh"].groupby(per).sum()})
        frm = _fresh_cols(kc_fresh_frame(g, pd.Series(days), "Origin").reindex(d.index).groupby(per).sum(), cols)
        sc["fr"] = max(float(frm.drop(columns="Total").abs().max().max()), 1.0)
    for pr in lots.index[::-1]:
        out.append(_cg_row(pr.strftime("%b %Y"), lots.loc[pr], chg_m.loc[pr], use_m.loc[pr], cols, sc, True,
                           rate.loc[pr] if with_rate else None, qm.loc[pr] if with_queue else None, with_queue,
                           frm.loc[pr] if with_queue else None))
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_daily_html(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame, show_all: bool = False,
                     height: str = "72vh", with_rate: bool = False, with_queue: bool = False, nrows: int = 0) -> str:
    days = pd.DatetimeIndex(days)
    p = kc_gr_wide(g, pd.Series(days), "Passed")
    f_full = kc_gr_wide(g, pd.Series(days), "Failed")
    d = kc_cg_daily(g, pd.Series(days), kc)
    chg_o = kc_origin_certs(kc).diff().reindex(days)
    cols, pp, cc, ff = _cg_origin_split(p, chg_o, show_all, f=f_full)
    use = pp - cc
    rate = _rate_frame(pp, ff, f_full.sum(axis=1)) if with_rate else None
    ok = cc.loc[cc.index.isin(d.index)]
    sc = {"p": max(float(pp.max().max()), 1.0), "pt": max(float(pp.sum(axis=1).max()), 1.0),
          "c": max(float(ok.abs().max().max()), 1.0), "ct": max(float(ok.sum(axis=1).abs().max()), 1.0),
          "u": max(float(use.loc[ok.index].abs().max().max()), 1.0), "ut": max(float(use.loc[ok.index].sum(axis=1).abs().max()), 1.0)}
    out = ["<div class='mt' style='margin-bottom:4px'>Daily Grading, Certs Change and Usage by Origin (bags)</div>",
           f"<div class='rwrap' style='height:{height}'>"]
    out += _cg_head("Date", cols, with_rate, with_queue)
    qd = frd = None
    if with_queue:
        qd = kc_queue_frame(g, pd.Series(days), kc)
        frd = _fresh_cols(kc_fresh_frame(g, pd.Series(days), "Origin"), cols)
        sc["fr"] = max(float(frd.drop(columns="Total").abs().max().max()), 1.0)
    for dt in (days[::-1][:nrows] if nrows else days[::-1]):
        out.append(_cg_row(dt.strftime("%d-%b-%y"), pp.loc[dt], cc.loc[dt].fillna(0), use.loc[dt].fillna(0), cols, sc,
                           dt in d.index, rate.loc[dt] if with_rate else None, qd.loc[dt] if with_queue else None, with_queue,
                           frd.loc[dt] if with_queue else None))
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_usage_origin(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame) -> pd.DataFrame:
    """Daily Usage per origin (same day): the origin's Passed minus the change in that origin's own certs."""
    d = kc_cg_daily(g, pd.Series(days), kc)
    oc = kc_origin_certs(kc)
    p = kc_gr_wide(g, pd.Series(days), "Passed").reindex(d.index).reindex(columns=oc.columns, fill_value=0).fillna(0)
    return p - oc.diff().reindex(d.index)


@st.cache_data(ttl=3600, show_spinner=False)
def kc_fill_from_ice(kc: pd.DataFrame, g: pd.DataFrame) -> pd.DataFrame:
    """LSEG occasionally has no certs row for a day ICE did report (e.g. 10-Aug-2026). Add such days from the
    ICE certified-stock file itself (identical to LSEG wherever both exist) so usage and certs change stay continuous."""
    ice = g[g["Tag"] == "Certs"]
    missing = sorted(set(ice["Date"].unique()) - set(kc["Date"]))
    missing = [d for d in missing if d >= kc["Date"].min() and pd.Timestamp(d).dayofweek < 5]
    if not missing:
        return kc
    name_to_code = {n: c for c, n in KC_ORIGIN_NAMES.items()}
    rows = []
    for d in missing:
        x = ice[ice["Date"] == d]
        row = {"Date": d, "KC-TOT-TOT": float(x["Bags"].sum())}
        for o, v in x.groupby("Origin")["Bags"].sum().items():
            if o in name_to_code:
                row[f"KC-{name_to_code[o]}-TOT"] = float(v)
        for pname, v in x.groupby("Port")["Bags"].sum().items():
            if pname in KC_PORT_CODE:
                row[f"KC-TOT-{KC_PORT_CODE[pname]}"] = float(v)
        for (o, pname), v in x.groupby(["Origin", "Port"])["Bags"].sum().items():
            if o in name_to_code and pname in KC_PORT_CODE:
                row[f"KC-{name_to_code[o]}-{KC_PORT_CODE[pname]}"] = float(v)
        rows.append(row)
    return pd.concat([kc, pd.DataFrame(rows)], ignore_index=True).sort_values("Date").reset_index(drop=True)


KC_PORT_CODE = {"Antwerp": "AN", "Barcelona": "BA", "Ham/Bre": "HA", "Houston": "HO", "Miami": "MI",
                "New Orleans": "NO", "New York": "NY"}


@st.cache_data(ttl=3600, show_spinner=False)
def kc_port_certs(kc: pd.DataFrame) -> pd.DataFrame:
    """Certs per port by name. LSEG has no Virginia RIC, so Virginia is the residual of the total. A day
    whose port RICs do not add up to the total (a feed glitch) is dropped and the last good day carried."""
    k = kc.set_index("Date")
    tot = k["KC-TOT-TOT"].astype(float)
    raw = pd.DataFrame({p: k[f"KC-TOT-{c}"].astype(float) for p, c in KC_PORT_CODE.items()})
    ok = (tot - raw.sum(axis=1)).between(0, 10000)
    out = raw.where(ok, np.nan).ffill(limit=5)
    va = (tot - out.sum(axis=1)).clip(lower=0)
    out["Virginia"] = va.where(va <= 10000, 0.0)
    return out[KC_GR_PORTS]


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_usage_port(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame) -> pd.DataFrame:
    """Daily Usage per port (same day): the port's Passed minus the change in that port's own certs."""
    d = kc_cg_daily(g, pd.Series(days), kc)
    p = kc_gr_wide(g, pd.Series(days), "Passed", by="Port").reindex(d.index).reindex(columns=KC_GR_PORTS, fill_value=0).fillna(0)
    return p - kc_port_certs(kc).diff().reindex(d.index).fillna(0)


def _cg_port_head(first_col: str, cols: list, with_rate: bool = False, with_queue: bool = False) -> list:
    """Three header rows: group (Passed | Pass % | Certs Change | Usage), country band, port codes."""
    groups = []
    for c in cols:
        ct = KC_GR_PORT_COUNTRY[c]
        if groups and groups[-1][0] == ct:
            groups[-1][1] += 1
        else:
            groups.append([ct, 1])
    n = len(cols) + 1
    edge = "border-left:2px solid #0a2463;"
    blocks = [("Bags Passed by Port", False, False)]
    if with_rate:
        blocks.append(("Pass % by Port", False, True))
    blocks += [("Certs Change by Port", True, False), ("Usage by Port", True, False)]
    if with_queue:
        blocks.append(("Fresh Pending by Port", False, True))
    h = ["<table class='rpt cmp" + (" tiny" if with_rate else "") + "'><thead><tr class='h1'>",
         f"<th class='dt' rowspan='3'>{first_col}</th>"]
    for gi, (title, certs, _small) in enumerate(blocks):
        h.append(f"<th colspan='{n}'{' class=certs-hdr' if certs else ''}{' style=' + repr(edge) if gi else ''}>{title}</th>")
    if with_queue:
        h.append(f"<th style={edge!r}>Grading Queue</th><th class='certs-hdr' style={edge!r}>KC Certs</th>")
    h.append("</tr><tr class='h2'>")
    for gi in range(len(blocks)):
        for i, (ct, k) in enumerate(groups):
            e = edge if (gi and i == 0) else ("border-left:2px solid #ffffff;" if i else "")
            pr = " class='pr'" if blocks[gi][2] else ""
            h.append(f"<th colspan='{k}'{pr} style='background:{KC_COUNTRY_COLORS[ct]};{e}letter-spacing:.06em;"
                     f"text-transform:uppercase'>{ct}</th>")
        tcls = "certs-hdr" if blocks[gi][1] else ("pr" if blocks[gi][2] else "")
        h.append(f"<th rowspan='2'{' class=' + tcls if tcls else ''}>{'Tot' if blocks[gi][2] else 'Total'}</th>")
    if with_queue:
        h.append(f"<th rowspan='2' style={edge!r}>Pending</th><th rowspan='2' class='certs-hdr' style={edge!r}>Level</th>")
    h.append("</tr><tr class='h3'>")
    for gi in range(len(blocks)):
        k = 0
        for i, (ct, kk) in enumerate(groups):
            for j in range(kk):
                c = cols[k]
                e = edge if (gi and k == 0) else ("border-left:2px solid #ffffff;" if j == 0 and i else "")
                pr = " class='pr'" if blocks[gi][2] else ""
                h.append(f"<th{pr} style='background:color-mix(in srgb, {KC_COUNTRY_COLORS[ct]} 58%, #0a2463);{e}'>"
                         f"{KC_GR_PORT_SHORT[c]}</th>")
                k += 1
    h.append("</tr></thead><tbody>")
    return h


@st.cache_data(ttl=3600, show_spinner=False)
def kc_cg_port_html(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame, monthly: bool, height: str = "auto",
                    with_rate: bool = False, with_queue: bool = False, nrows: int = 0) -> str:
    days = pd.DatetimeIndex(days)
    d = kc_cg_daily(g, pd.Series(days), kc)
    pas_all = kc_gr_wide(g, pd.Series(days), "Passed", by="Port").reindex(columns=KC_GR_PORTS, fill_value=0)
    fail_all = kc_gr_wide(g, pd.Series(days), "Failed", by="Port").reindex(columns=KC_GR_PORTS, fill_value=0)
    chg_all = kc_port_certs(kc).diff().reindex(days)
    cols = [p for p in KC_GR_PORTS if pas_all[p].sum() > 0 or chg_all[p].abs().sum() > 0]
    if monthly:
        per = d.index.to_period("M")
        pas = pas_all.reindex(d.index)[cols].groupby(per).sum()
        fl = fail_all.reindex(d.index)[cols].groupby(per).sum()
        f_tot = fail_all.reindex(d.index).sum(axis=1).groupby(per).sum()
        chg = chg_all.reindex(d.index)[cols].fillna(0).groupby(per).sum()
        rows = [(pr, pr.strftime("%b %Y"), True) for pr in pas.index[::-1]]
        first, title = "Month", "Monthly"
    else:
        pas, fl, f_tot, chg = pas_all[cols], fail_all[cols], fail_all.sum(axis=1), chg_all[cols].fillna(0)
        rows = [(dt, dt.strftime("%d-%b-%y"), dt in d.index) for dt in (days[::-1][:nrows] if nrows else days[::-1])]
        first, title = "Date", "Daily"
    use = pas - chg
    rate = _rate_frame(pas, fl, f_tot) if with_rate else None
    okr = [r for r, _, h in rows if h]
    sc = {"p": max(float(pas.max().max()), 1.0), "pt": max(float(pas.sum(axis=1).max()), 1.0),
          "c": max(float(chg.loc[okr].abs().max().max()), 1.0), "ct": max(float(chg.loc[okr].sum(axis=1).abs().max()), 1.0),
          "u": max(float(use.loc[okr].abs().max().max()), 1.0), "ut": max(float(use.loc[okr].sum(axis=1).abs().max()), 1.0)}
    out = [f"<div class='mt' style='margin-bottom:4px'>{title} Grading, Certs Change and Usage by Port (bags)</div>",
           f"<div class='rwrap' style='height:{height}'>"]
    out += _cg_port_head(first, cols, with_rate, with_queue)
    qq = frp = None
    if with_queue:
        qd = kc_queue_frame(g, pd.Series(days), kc)
        if monthly:
            qdm = qd.reindex(d.index)
            per = d.index.to_period("M")
            qq = pd.DataFrame({"Failed": qdm["Failed"].groupby(per).sum(), "Pending": qdm["Pending"].groupby(per).last(),
                               "Certs": qdm["Certs"].groupby(per).last(), "Fresh": qdm["Fresh"].groupby(per).sum()})
        else:
            qq = qd
        frp = kc_fresh_frame(g, pd.Series(days), "Port")
        frp = _fresh_cols(frp.reindex(d.index).groupby(d.index.to_period("M")).sum() if monthly else frp, cols)
        sc["fr"] = max(float(frp.drop(columns="Total").abs().max().max()), 1.0)
    for key, label, has in rows:
        out.append(_cg_row(label, pas.loc[key], chg.loc[key], use.loc[key], cols, sc, has,
                           rate.loc[key] if with_rate else None, qq.loc[key] if with_queue else None, with_queue,
                           frp.loc[key] if with_queue else None))
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_usage_by_origin_fig(g: pd.DataFrame, days: pd.Series, kc: pd.DataFrame, show_all: bool,
                           top_n: int = 5, height: int = 380) -> go.Figure:
    """Monthly Usage per origin: each origin's Passed minus the change in that origin's own certs."""
    days = pd.DatetimeIndex(days)
    p = kc_gr_wide(g, pd.Series(days), "Passed")
    oc = kc_origin_certs(kc)
    d = kc_cg_daily(g, pd.Series(days), kc)
    idx = d.index
    chg = oc.diff().reindex(idx)
    pas = p.reindex(idx).reindex(columns=chg.columns, fill_value=0)
    use = (pas - chg).groupby(idx.to_period("M")).sum()
    order = list(use.abs().sum().sort_values(ascending=False).index)
    colors = kc_gr_colors(order)
    shown, minors = (order, []) if show_all else (order[:top_n], order[top_n:])
    xs = [str(x) for x in use.index]
    fig = go.Figure()
    for o in shown:
        fig.add_trace(go.Bar(x=xs, y=use[o], name=o, marker_color=colors[o], hovertemplate="%{y:+,.0f}<extra>" + o + "</extra>"))
    if minors:
        fig.add_trace(go.Bar(x=xs, y=use[minors].sum(axis=1), name="Other", marker_color=KC_GR_OTHER,
                             hovertemplate="%{y:+,.0f}<extra>Other</extra>"))
    chart_layout(fig, "Monthly Usage by Origin (bags)" + ("" if show_all else f" (Top {top_n} + Other)"), height)
    fig.update_layout(barmode="relative", bargap=0.25, xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9)),
                      yaxis=dict(tickformat="+,"))
    return fig


RC_ORIGINS = ["Brazil", "Vietnam", "Indonesia", "Other"]
RC_ORIGIN_ABBR = {"Brazil": "BRA", "Vietnam": "VIE", "Indonesia": "IND", "Other": "OTH"}
RC_CERT_PORTS = ["AMS", "ANT", "BAR", "BRE", "FEL", "GEN", "HAM", "LIV", "LON", "NOR", "ROT", "TRI"]


def _rc_band(country: str) -> str:
    return TEAL if country == "USA" else ("#6c7a99" if country == "Other" else "#4a63a8")


@st.cache_data(ttl=3600, show_spinner=False)
def rc_comp_frames(gr: pd.DataFrame, certs: pd.DataFrame, grade: str = "VG") -> dict:
    """Everything the Robusta Comprehensive View needs, one row per certs day from the first grading panel.
    A panel on a day with no certs print is attributed to the next certs day. Certs Change and Usage use the
    Robusta 1-day lag: a row's grading is compared with the change in certs on the NEXT certs day."""
    c = certs.set_index("Date")
    tot = c[f"LRC-TOT-{grade}"].dropna().astype(float)
    chg_tot = tot.diff().dropna()
    cd = pd.DatetimeIndex(chg_tot.index.sort_values())
    idx = cd[cd >= gr["PanelDate"].min()]
    pos = cd.searchsorted(gr["PanelDate"])
    keep = pos < len(cd)
    gg = gr[keep].assign(Day=cd[pos[keep]])

    def piv(df, col):
        return df.groupby(["Day", col])["NoLots"].sum().unstack(fill_value=0).reindex(idx, fill_value=0)

    lots_o = piv(gg, "Origin2").reindex(columns=RC_ORIGINS, fill_value=0)
    ten_o = piv(gg[gg["Tenderable"] == "Y"], "Origin2").reindex(columns=RC_ORIGINS, fill_value=0)
    lots_p = piv(gg, "PortId")

    certs_p = pd.DataFrame({p: c[f"LRC-{p}-{grade}"].astype(float) for p in RC_CERT_PORTS
                            if f"LRC-{p}-{grade}" in c.columns}).ffill(limit=5).fillna(0)
    ports = sorted(set(lots_p.columns) | set(certs_p.columns))
    certs_p = certs_p.reindex(columns=ports, fill_value=0)
    lots_p = lots_p.reindex(columns=ports, fill_value=0)

    nxt = pd.Series(cd[1:], index=cd[:-1])                 # 1 certs day later
    nd = nxt.reindex(idx)
    chg_p = certs_p.diff().reindex(nd.values).set_axis(idx)   # NaN on the last day (no next print yet)
    chg_t = chg_tot.reindex(nd.values).set_axis(idx)
    use_p = lots_p - chg_p
    use_t = lots_o.sum(axis=1) - chg_t
    price = certs_price = c["LRC_Price"].astype(float) if "LRC_Price" in c.columns else pd.Series(dtype=float)
    return {"idx": idx, "lots_o": lots_o, "ten_o": ten_o, "lots_p": lots_p, "chg_p": chg_p, "chg_t": chg_t,
            "use_p": use_p, "use_t": use_t, "level": tot.reindex(idx), "price": price.reindex(idx),
            "price_chg": price.diff().reindex(idx), "ports": ports}


@st.cache_data(ttl=3600, show_spinner=False)
def rc_comp_html(gr: pd.DataFrame, certs: pd.DataFrame, monthly: bool, show_all: bool = False,
                 height: str = "72vh", grade: str = "VG", nrows: int = 0) -> str:
    f = rc_comp_frames(gr, certs, grade)
    idx = f["idx"]
    per = idx.to_period("M")

    def agg(x, how="sum"):
        if not monthly:
            return x
        gb = x.groupby(per)
        return gb.sum() if how == "sum" else gb.last()

    lots_o, ten_o = agg(f["lots_o"]), agg(f["ten_o"])
    lots_p, chg_p, use_p = agg(f["lots_p"]), agg(f["chg_p"]), agg(f["use_p"])
    chg_t, use_t = agg(f["chg_t"]), agg(f["use_t"])
    level = agg(f["level"], "last")
    rank = f["lots_p"].sum().sort_values(ascending=False)
    ranked = [p for p in rank.index if rank[p] > 0] + [p for p in f["ports"] if rank.get(p, 0) == 0
                                                       and f["chg_p"][p].abs().sum() > 0]
    shown = ranked if show_all else ranked[:5]
    rest = [p for p in f["ports"] if p not in shown]
    # ports of one country sit next to each other under a single country band (biggest country first)
    ctry = lambda p: PORT_COUNTRY.get(p, "Other")
    c_lots = {}
    for p in shown:
        c_lots[ctry(p)] = c_lots.get(ctry(p), 0) + float(rank.get(p, 0))
    shown = sorted(shown, key=lambda p: (-c_lots[ctry(p)], ctry(p), -float(rank.get(p, 0))))

    def cols_of(x):
        out = x.reindex(columns=shown, fill_value=0).copy()
        if rest and not show_all:
            out["Other"] = x.reindex(columns=rest, fill_value=0).sum(axis=1)
        return out

    lp, cp, up = cols_of(lots_p), cols_of(chg_p), cols_of(use_p)
    pcols = list(cp.columns)

    groups = []
    for p in pcols:
        ct = PORT_COUNTRY.get(p, "Other")
        if groups and groups[-1][0] == ct:
            groups[-1][1] += 1
        else:
            groups.append([ct, 1])
    no = len(RC_ORIGINS) + 1
    npn = len(pcols) + 1
    edge = "border-left:2px solid #0a2463;"
    h = ["<table class='rpt cmp tiny'><thead><tr class='h1'>",
         f"<th class='dt' rowspan='3'>{'Month' if monthly else 'Date'}</th>",
         f"<th colspan='{no}'>Lots Graded by Origin</th>", f"<th colspan='{npn}' class='sep'>Lots Graded by Port</th>",
         f"<th colspan='{npn}' class='sep certs-hdr'>Certs Change by Port (1-day lag)</th>",
         f"<th colspan='{npn}' class='sep certs-hdr'>Usage by Port (1-day lag)</th>",
         "<th colspan='1' class='sep certs-hdr'>Certs</th></tr><tr class='h2'>"]
    h += [f"<th rowspan='2'>{o}</th>" for o in RC_ORIGINS] + ["<th rowspan='2'>Total</th>"]
    for gi in range(3):
        for i, (ct, k) in enumerate(groups):
            e = edge if (i == 0) else "border-left:2px solid #ffffff;"
            h.append(f"<th colspan='{k}' style='background:{_rc_band(ct)};{e}letter-spacing:.06em;text-transform:uppercase'>{ct}</th>")
        h.append(f"<th rowspan='2'{' class=certs-hdr' if gi else ''}>Total</th>")
    h += ["<th rowspan='2' class='certs-hdr sep'>Level</th></tr><tr class='h3'>"]
    for gi in range(3):
        k = 0
        for i, (ct, kk) in enumerate(groups):
            for j in range(kk):
                e = edge if (i == 0 and j == 0) else ("border-left:2px solid #ffffff;" if j == 0 else "")
                h.append(f"<th style='background:color-mix(in srgb, {_rc_band(ct)} 58%, #0a2463);{e}'>{pcols[k]}</th>")
                k += 1
    h.append("</tr></thead><tbody>")

    mx = {"l": max(float(lots_o.max().max()), 1.0), "lt": max(float(lots_o.sum(axis=1).max()), 1.0),
          "lp": max(float(lp.max().max()), 1.0),
          "c": max(float(cp.abs().max().max()), 1.0), "ct": max(float(chg_t.abs().max()), 1.0),
          "u": max(float(up.abs().max().max()), 1.0), "ut": max(float(use_t.abs().max()), 1.0)}
    keys = list(lots_o.index)[::-1]
    if nrows and not monthly:
        keys = keys[:nrows]
    out = [f"<div class='mt' style='margin-bottom:4px'>{'Monthly' if monthly else 'Daily'} Robusta Grading (lots), "
           "Certs Change and Usage by Port, 1-day lag</div>", f"<div class='rwrap' style='height:{height}'>"] + h
    for k in keys:
        lab = k.strftime("%b %Y") if monthly else k.strftime("%d-%b-%y")
        r = [f"<tr><td class='d'>{lab}</td>"]
        r += [_heat_td(lots_o.loc[k, o], mx["l"]) for o in RC_ORIGINS] + [_bar_td(lots_o.loc[k].sum(), mx["lt"])]
        pcells = [_heat_td(lp.loc[k, p], mx["lp"]) for p in pcols]
        pcells[0] = pcells[0].replace("<td", "<td class='sep'", 1)
        r += pcells + [_bar_td(lp.loc[k].sum(), mx["lt"])]
        for grp, tot_v, sc_i, sc_t in ((cp, chg_t, "c", "ct"), (up, use_t, "u", "ut")):
            cells = [_chg_heat_td(grp.loc[k, p], mx[sc_i]) for p in pcols]
            cells[0] = cells[0].replace("<td", "<td class='sep'", 1)
            r += cells + [_delta_td(tot_v.loc[k], mx[sc_t])]
        lv = level.loc[k]
        r.append(f"<td class='tot sep'>{'' if pd.isna(lv) else _fmt_i(lv)}</td>")
        out.append("".join(r) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


# ---------------------------------------------------------------------------------------------
# Arabica Price Link: KC 1/2 spread vs certified stocks
# ---------------------------------------------------------------------------------------------
ROWS_OPTS = {"3M": 65, "6M": 130, "1Y": 260, "All": 0}


def rows_radio(key: str) -> int:
    """How many of the latest daily rows a big table draws (the browser, not the data, is what gets slow)."""
    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Daily rows</div>", unsafe_allow_html=True)
    return ROWS_OPTS[st.radio("Daily rows", list(ROWS_OPTS), index=1, horizontal=True,
                              label_visibility="collapsed", key=key)]


KC_SPREAD_COL = "spread_c12"     # C1 - C2 (LSEG continuation)


@st.cache_data(ttl=600)
def load_price_link() -> pd.DataFrame:
    d = pd.read_parquet(DB_DIR / "Main" / "KC" / "price_link_kc.parquet")
    d.index = pd.to_datetime(d.index)
    return d.sort_index()


@st.cache_data(ttl=600)
def load_eom_hist() -> pd.DataFrame:
    e = pd.read_parquet(DB_DIR / "Main" / "KC" / "kc_certs_eom_hist.parquet")
    e["Date"] = pd.to_datetime(e["Date"])
    return e


@st.cache_data(ttl=3600, show_spinner=False)
def kc_spread_certs_frame(pl: pd.DataFrame, kc: pd.DataFrame, eom: pd.DataFrame, freq: str = "Monthly") -> pd.DataFrame:
    """Spread (C1 - C2, c/lb) against certified stocks (000s bags).
    Monthly: average daily spread vs end-of-month stocks, ICE month-end history before LSEG's daily certs start and
    LSEG after; the latest month is month-to-date (PeriodIndex).
    Daily: each day's spread vs that day's certs total, from the first LSEG certs day (DatetimeIndex)."""
    sp = pl[KC_SPREAD_COL].dropna()
    tot = kc.dropna(subset=["KC-TOT-TOT"]).set_index("Date")["KC-TOT-TOT"].astype(float)
    if freq == "Daily":
        df = pd.concat([sp.rename("spread"), (tot / 1000.0).rename("stocks")], axis=1).dropna()
        return df[df["stocks"] > 0]
    live = tot.groupby(tot.index.to_period("M")).last()
    hist = eom.set_index(eom["Date"].dt.to_period("M"))["Bags"].astype(float)
    stocks = pd.concat([hist[hist.index < live.index.min()], live]).sort_index()
    df = pd.concat([sp.groupby(sp.index.to_period("M")).mean().rename("spread"), (stocks / 1000.0).rename("stocks")], axis=1).dropna()
    return df[df["stocks"] > 0]


@st.cache_data(ttl=600)
def load_price_link_rc() -> pd.DataFrame:
    d = pd.read_parquet(DB_DIR / "Main" / "RC" / "price_link_rc.parquet")
    d.index = pd.to_datetime(d.index)
    return d.sort_index()


@st.cache_data(ttl=3600, show_spinner=False)
def rc_spread_certs_frame(pl: pd.DataFrame, certs: pd.DataFrame, freq: str = "Monthly", grade: str = "VG") -> pd.DataFrame:
    """Robusta C1 - C2 (USD/MT) against LRC certified stocks (lots, the dashboard's VG series). Monthly: average
    spread vs the month's last certs print (latest month is month-to-date); Daily: same-day certs."""
    sp = pl["spread_c12"].dropna()
    tot = certs.dropna(subset=[f"LRC-TOT-{grade}"]).set_index("Date")[f"LRC-TOT-{grade}"].astype(float)
    if freq == "Daily":
        df = pd.concat([sp.rename("spread"), tot.rename("stocks")], axis=1).dropna()
    else:
        df = pd.concat([sp.groupby(sp.index.to_period("M")).mean().rename("spread"),
                        tot.groupby(tot.index.to_period("M")).last().rename("stocks")], axis=1).dropna()
    return df[df["stocks"] > 0]


def kc_spread_fit(df: pd.DataFrame):
    """spread = a + b * ln(stocks), least squares (stocks in 000s bags, at least 1k bags)."""
    d = df[df["stocks"] >= 1.0]
    b, a = np.polyfit(np.log(d["stocks"].values), d["spread"].values, 1)
    return a, b


@st.cache_data(ttl=3600, show_spinner=False)
def kc_spread_vs_certs_fig(df: pd.DataFrame, freq: str = "Monthly", height: int = 560, name: str = "KC",
                           x_title: str = "Cert Stocks (000s Bags)", y_title: str = "1/2 Spread (c/lb)",
                           x_unit: str = "k bags") -> go.Figure:
    a, b = kc_spread_fit(df)
    monthly = freq == "Monthly"
    fmt = "%b-%y" if monthly else "%d-%b-%y"
    hist, last = df.iloc[:-1], df.iloc[-1]
    lab = [p.strftime(fmt) for p in hist.index]
    last_lab = df.index[-1].strftime(fmt)
    Scatter = go.Scatter if monthly else go.Scattergl
    fig = go.Figure()
    fig.add_trace(Scatter(x=hist["stocks"], y=hist["spread"], mode="markers", name=freq,
                          marker=dict(symbol="square", size=6 if monthly else 4, color="#2f78b7",
                                      opacity=1 if monthly else 0.55),
                          customdata=lab, hovertemplate="%{customdata}<br>Certs %{x:,.0f} " + x_unit + " | Spread %{y:.1f}<extra></extra>"))
    xs = np.linspace(max(float(df["stocks"].min()), 1.0), float(df["stocks"].max()), 300)
    fig.add_trace(go.Scatter(x=xs, y=a + b * np.log(xs), mode="lines", name="Fit", line=dict(color="#111111", width=2),
                             hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[last["stocks"]], y=[last["spread"]], mode="markers", name=last_lab,
                             marker=dict(symbol="square", size=10, color=GREEN, line=dict(color="#111111", width=1)),
                             hovertemplate=f"{last_lab}{' (month to date)' if monthly else ''}<br>Certs %{{x:,.0f}} {x_unit} | "
                                           "Spread %{y:.1f}<extra></extra>"))
    fig.add_annotation(x=last["stocks"], y=last["spread"], text=f"<b>{last_lab}</b>", showarrow=True,
                       arrowhead=0, ax=28, ay=-30, font=dict(size=12, color="#111111"))
    sub = (f"Monthly average spreads, end-month cert stocks, {df.index[0].strftime('%b %Y')} to date" if monthly else
           f"Daily spreads vs daily cert stocks, {df.index[0].strftime('%b %Y')} to date")
    chart_layout(fig, f"<b>{name} 1/2 Spread vs Cert Stocks</b><br><sup>{sub}</sup>", height)
    fig.update_layout(showlegend=False, hovermode="closest", margin=dict(t=64, b=8, l=8, r=8),
                      xaxis=dict(title=x_title, tickformat=",", rangemode="tozero", gridcolor="rgba(10,36,99,0.06)"),
                      yaxis=dict(title=y_title, zeroline=True, zerolinecolor="#9aa3b8", gridcolor="rgba(10,36,99,0.08)"))
    return fig


# ============================================================================================
# Price Link (shared by Arabica and Robusta) and the combined Arabica & Robusta tab
# ============================================================================================
PL_CFG = {
    "KC": dict(name="KC", price_unit="c/lb", stock_unit="bags", stock_lbl="Cert Stocks (bags)"),
    "RC": dict(name="LRC", price_unit="$/MT", stock_unit="lots", stock_lbl="Cert Stocks (lots)"),
}
PL_SPANS = ["1Y", "3Y", "5Y", "All"]
BAG_MT = 0.06     # one 60 kg bag, in MT
LOT_MT = 10.0     # one Robusta lot, in MT
PL_SEC_CSS = "margin:-2px 0 6px"


def pl_span_radio(key: str, default: str = "3Y") -> str:
    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Span</div>", unsafe_allow_html=True)
    return st.radio("Span", PL_SPANS, index=PL_SPANS.index(default), horizontal=True, label_visibility="collapsed", key=key)


def pl_start(pick: str, last: pd.Timestamp):
    return None if pick == "All" else last - pd.DateOffset(years=int(pick[0]))


def pl_section(title: str, desc: str = "") -> None:
    st.markdown(f"<div class='sec'>{title}</div>", unsafe_allow_html=True)
    if desc:
        st.markdown(f"<div class='card-desc' style='{PL_SEC_CSS}'>{desc}</div>", unsafe_allow_html=True)


def _since(s, start):
    return s if start is None else s[s.index >= start]


def _mstamp(s: pd.Series) -> pd.Series:
    """Month-period indexed Series -> month-start timestamps (for plotting)."""
    out = s.copy()
    out.index = out.index.to_timestamp()
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def pl_series_kc(kc: pd.DataFrame, g: pd.DataFrame, days: pd.Series) -> dict:
    days = pd.Series(days)
    d = kc_cg_daily(g, days, kc)
    return {"certs": kc.set_index("Date")["KC-TOT-TOT"].astype(float).dropna(), "usage": d["Usage"],
            "pending": kc_gr_wide(g, days, "Pending").sum(axis=1), "fresh": kc_fresh_frame(g, days, "Origin").sum(axis=1)}


@st.cache_data(ttl=3600, show_spinner=False)
def pl_series_rc(gr: pd.DataFrame, certs: pd.DataFrame) -> dict:
    return {"certs": certs.set_index("Date")["LRC-TOT-VG"].dropna().astype(float),
            "usage": daily_usage_series(gr, certs, "VG", 1)}


def pl_dual_fig(l: pd.Series, r: pd.Series, title: str, l_name: str, r_name: str, l_title: str, r_title: str,
                kind: str = "area", height: int = 380) -> go.Figure:
    """Left-axis series (area, line or bars) with a right-axis line on top."""
    fig = go.Figure()
    if kind == "bar":
        fig.add_trace(go.Bar(x=l.index, y=l.values, name=l_name, marker_color=NAVY, opacity=0.78,
                             hovertemplate="%{y:,.0f}<extra>" + l_name + "</extra>"))
    else:
        fig.add_trace(go.Scatter(x=l.index, y=l.values, name=l_name, mode="lines", line=dict(color=NAVY, width=1.6),
                                 fill="tozeroy" if kind == "area" else None, fillcolor="rgba(10,36,99,0.08)",
                                 hovertemplate="%{y:,.0f}<extra>" + l_name + "</extra>"))
    fig.add_trace(go.Scatter(x=r.index, y=r.values, name=r_name, yaxis="y2", mode="lines", line=dict(color=AMBER, width=2),
                             hovertemplate="%{y:,.1f}<extra>" + r_name + "</extra>"))
    chart_layout(fig, title, height)
    fig.update_layout(yaxis=dict(title=l_title, tickformat=",", zeroline=kind == "bar", zerolinecolor="#9aa3b8"),
                      yaxis2=dict(title=r_title, overlaying="y", side="right", showgrid=False, tickformat=","),
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
                      margin=dict(t=64, b=8, l=8, r=8))
    return fig


def pl_scatter_fig(x: pd.Series, y: pd.Series, title: str, x_title: str, y_title: str, fmt: str = "%d %b %Y",
                   size: int = 560) -> go.Figure:
    """Square scatter with a least-squares line; the latest point is green."""
    d = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    slope, icpt = np.polyfit(d["x"].values, d["y"].values, 1)
    r = float(np.corrcoef(d["x"].values, d["y"].values)[0, 1])
    lab = [p.strftime(fmt) if hasattr(p, "strftime") else str(p) for p in d.index]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=d["x"], y=d["y"], mode="markers", marker=dict(size=5, color="#2f78b7", opacity=0.55),
                               customdata=lab, hovertemplate="%{customdata}<br>x %{x:,.1f} | y %{y:,.2f}<extra></extra>"))
    xs = np.array([d["x"].min(), d["x"].max()])
    fig.add_trace(go.Scatter(x=xs, y=icpt + slope * xs, mode="lines", line=dict(color="#111111", width=2), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[d["x"].iloc[-1]], y=[d["y"].iloc[-1]], mode="markers",
                             marker=dict(size=10, color=GREEN, line=dict(color="#111111", width=1)),
                             hovertemplate=f"{lab[-1]}<br>x %{{x:,.1f}} | y %{{y:,.2f}}<extra></extra>"))
    chart_layout(fig, f"<b>{title}</b><br><sup>correlation {r:+.2f}, R2 {r * r:.2f}, n {len(d):,}</sup>", size)
    fig.update_layout(width=size, height=size, showlegend=False, hovermode="closest", margin=dict(t=64, b=8, l=8, r=8),
                      xaxis=dict(title=x_title, tickformat=",", zeroline=True, zerolinecolor="#9aa3b8"),
                      yaxis=dict(title=y_title, zeroline=True, zerolinecolor="#9aa3b8"))
    return fig


def pl_seasonal_daily_fig(s: pd.Series, title: str, y_title: str, n_years=5, height: int = 400) -> go.Figure:
    """Daily Series by calendar day. Latest year navy, previous year red; the other years of the window give the
    P10-P90 and P25-P75 bands and the dotted average (short gaps carried forward, bands lightly smoothed)."""
    d = s.dropna()
    d = d[~((d.index.month == 2) & (d.index.day == 29))]
    doy = d.index.dayofyear - ((d.index.is_leap_year) & (d.index.dayofyear > 60)).astype(int)
    tbl = pd.DataFrame({"v": d.values.astype(float), "y": d.index.year, "doy": doy}).pivot_table(
        index="doy", columns="y", values="v", aggfunc="last").reindex(range(1, 366))
    yrs = sorted(tbl.columns)
    win = yrs[-n_years:] if n_years else yrs
    cur = win[-1]
    prev = win[-2] if len(win) > 1 else None
    filled = tbl[win].ffill(limit=10)
    filled.loc[filled.index > tbl[cur].last_valid_index(), cur] = np.nan
    hist = filled[[y for y in win if y != cur]]
    xs = pd.Timestamp("2001-01-01") + pd.to_timedelta(np.arange(365), unit="D")
    smooth = lambda z: z.rolling(7, center=True, min_periods=1).mean().values
    fig = go.Figure()
    if hist.shape[1] >= 3:
        for lo, hi, color, name in ((0.10, 0.90, "rgba(31,138,156,0.16)", "P10-P90"), (0.25, 0.75, "rgba(31,138,156,0.30)", "P25-P75")):
            fig.add_trace(go.Scatter(x=xs, y=smooth(hist.quantile(hi, axis=1)), mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=xs, y=smooth(hist.quantile(lo, axis=1)), mode="lines", line=dict(width=0), fill="tonexty",
                                     fillcolor=color, name=name, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=xs, y=smooth(hist.mean(axis=1)), mode="lines", name="Average", line=dict(color="#4a5578", width=1.5, dash="dot"),
                                 hovertemplate="%{y:,.1f}<extra>Average</extra>"))
    for y, col, w in ((prev, RED, 1.8), (cur, NAVY, 2.6)):
        if y is not None:
            fig.add_trace(go.Scatter(x=xs, y=filled[y].values, mode="lines", name=str(y), connectgaps=False, line=dict(color=col, width=w),
                                     hovertemplate="%{y:,.1f}<extra>" + str(y) + "</extra>"))
    rng = f"{win[0]}-{win[-1] - 1}" if len(win) > 1 else str(win[0])
    chart_layout(fig, f"{title} | bands from {rng}", height)
    fig.update_layout(yaxis=dict(title=y_title, tickformat=","), xaxis=dict(tickformat="%b", dtick="M1"), legend=dict(font=dict(size=10)))
    return fig


def render_price_link(comm: str, pl: pd.DataFrame, series: dict, frame_fn) -> None:
    """Price Link tab body, shared by Arabica (KC) and Robusta (RC). frame_fn(freq) -> spread/stocks frame."""
    cfg = PL_CFG[comm]
    views = ["Spread vs Certs", "Certs vs Price", "Usage vs Price"]
    if comm == "KC":
        views.append("Pending vs Spread")
    views.append("Seasonal")
    with st.container(key="rc_view_box"):
        view = st.radio("View", views, horizontal=True, label_visibility="collapsed", key=f"pl{comm}_view")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    cfgc = {"displayModeBar": False}
    certs = series["certs"]
    spread = pl["spread_c12"].dropna()

    if view == "Spread vs Certs":
        c1, _ = st.columns([1.4, 4])
        with c1:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Frequency</div>", unsafe_allow_html=True)
            freq = st.radio("Frequency", ["Monthly", "Daily"], horizontal=True, label_visibility="collapsed", key=f"pl{comm}_freq")
        df = frame_fn(freq)
        if comm == "KC":
            fig = kc_spread_vs_certs_fig(df, freq)
        else:
            fig = kc_spread_vs_certs_fig(df, freq, 560, "LRC", "Cert Stocks (Lots)", "1/2 Spread ($/MT)", "lots")
        st.plotly_chart(fig, width="stretch", config=cfgc, key=f"pl{comm}_chart1")

    elif view == "Certs vs Price":
        k1, k2, _ = st.columns([1.6, 1.6, 3])
        with k1:
            span = pl_span_radio(f"pl{comm}_span2", "All")
        with k2:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Scatter change over (days)</div>", unsafe_allow_html=True)
            h = st.radio("Horizon", [1, 5, 20], index=1, horizontal=True, label_visibility="collapsed", key=f"pl{comm}_h")
        start = pl_start(span, certs.index.max())
        cw = _since(certs, start)
        px, sp = _since(pl["c1"].dropna(), cw.index.min()), _since(spread, cw.index.min())
        pl_section("Certified stocks and C1 price")
        st.plotly_chart(pl_dual_fig(cw, px, f"{cfg['name']} certified stocks vs C1 price", "Certs", "C1", cfg["stock_lbl"],
                                    f"C1 ({cfg['price_unit']})"), width="stretch", config=cfgc, key=f"pl{comm}_c1")
        pl_section("Certified stocks and 1/2 spread")
        st.plotly_chart(pl_dual_fig(cw, sp, f"{cfg['name']} certified stocks vs 1/2 spread", "Certs", "C1 - C2", cfg["stock_lbl"],
                                    f"1/2 spread ({cfg['price_unit']})"), width="stretch", config=cfgc, key=f"pl{comm}_c2")
        pl_section("Certs change vs price return")
        base = _since(pd.concat([certs.rename("c"), pl["rollex_px"].rename("px")], axis=1).dropna(), cw.index.min())
        st.plotly_chart(pl_scatter_fig(base["c"].diff(h), base["px"].pct_change(h) * 100, f"{cfg['name']} certs change vs return, {h}d",
                                       f"Certs change ({cfg['stock_unit']})", "Price return (%)"), width="content", config=cfgc, key=f"pl{comm}_sc")

    elif view == "Usage vs Price":
        u = series["usage"].dropna()
        t0 = u.index.min()
        um = u.groupby(u.index.to_period("M")).sum()
        avg = certs.groupby(certs.index.to_period("M")).mean()
        upct = um / avg.reindex(um.index) * 100
        c1s = pl["c1"].dropna()
        c1m = c1s[c1s.index >= t0].groupby(c1s[c1s.index >= t0].index.to_period("M")).mean()
        spm = spread[spread.index >= t0].groupby(spread[spread.index >= t0].index.to_period("M")).mean()
        pl_section("Monthly usage and C1 price")
        st.plotly_chart(pl_dual_fig(_mstamp(um), _mstamp(c1m), f"{cfg['name']} monthly usage vs C1", "Usage", "C1", f"Usage ({cfg['stock_unit']})",
                                    f"C1 ({cfg['price_unit']})", "bar"), width="stretch", config=cfgc, key=f"pl{comm}_u1")
        pl_section("Usage rate and 1/2 spread")
        st.plotly_chart(pl_dual_fig(_mstamp(upct), _mstamp(spm), f"{cfg['name']} usage % of stocks vs 1/2 spread", "Usage %", "C1 - C2",
                                    "Usage (% of certs)", f"1/2 spread ({cfg['price_unit']})", "bar"), width="stretch", config=cfgc, key=f"pl{comm}_u2")
        pl_section("Usage rate vs spread")
        st.plotly_chart(pl_scatter_fig(upct, spm, f"{cfg['name']} usage % vs 1/2 spread (monthly)", "Usage (% of certs)",
                                       f"1/2 spread ({cfg['price_unit']})", "%b-%y"), width="content", config=cfgc, key=f"pl{comm}_u3")

    elif view == "Pending vs Spread":
        span = pl_span_radio(f"pl{comm}_span5", "All")
        pend = series["pending"]
        pend = _since(pend, pl_start(span, pend.index.max()))
        sp = _since(spread, pend.index.min())
        pl_section("Pending queue and 1/2 spread")
        st.plotly_chart(pl_dual_fig(pend, sp, "KC pending grading queue vs 1/2 spread", "Pending", "C1 - C2", "Pending (bags)",
                                    "1/2 spread (c/lb)"), width="stretch", config=cfgc, key=f"pl{comm}_p1")
        fr = series["fresh"].dropna()
        frm = fr.groupby(fr.index.to_period("M")).sum()
        spm = spread.groupby(spread.index.to_period("M")).mean()
        start = pl_start(span, frm.index.max().to_timestamp())
        cut = (lambda z: z if start is None else z[z.index.to_timestamp() >= start])
        pl_section("Fresh pending and 1/2 spread")
        st.plotly_chart(pl_dual_fig(_mstamp(cut(frm)), _mstamp(cut(spm)), "KC monthly fresh pending vs 1/2 spread", "Fresh pending", "C1 - C2",
                                    "Fresh pending (bags)", "1/2 spread (c/lb)", "bar"), width="stretch", config=cfgc, key=f"pl{comm}_p2")
        pl_section("Pending vs spread, Fresh pending vs spread change")
        pw = series["pending"]
        pw = _since(pw, pend.index.min())
        sp_d = spread.reindex(pw.index)
        fw = _since(series["fresh"], pend.index.min())
        d_sp = spread.reindex(fw.index).diff()
        sc1, sc2, _ = st.columns([1, 1, 0.3])
        with sc1:
            st.plotly_chart(pl_scatter_fig(pw, sp_d, "KC pending vs 1/2 spread", "Pending (bags)", "1/2 spread (c/lb)", size=520),
                            width="content", config=cfgc, key=f"pl{comm}_psc1")
        with sc2:
            st.plotly_chart(pl_scatter_fig(fw, d_sp, "KC fresh pending vs spread change", "Fresh pending (bags)", "1/2 spread change (c/lb)", size=520),
                            width="content", config=cfgc, key=f"pl{comm}_psc2")

    else:   # Seasonal
        sm1, _ = st.columns([2.4, 4])
        with sm1:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Period for the bands</div>", unsafe_allow_html=True)
            sper = st.radio("Period", ["5Y", "10Y", "15Y", "All"], index=0, horizontal=True, label_visibility="collapsed", key=f"pl{comm}_sper")
        n = None if sper == "All" else int(sper[:-1])
        pl_section("Seasonal 1/2 spread")
        st.plotly_chart(pl_seasonal_daily_fig(spread, f"{cfg['name']} 1/2 spread", f"1/2 spread ({cfg['price_unit']})", n),
                        width="stretch", config=cfgc, key=f"pl{comm}_s1")
        pl_section("Seasonal certified stocks")
        st.plotly_chart(pl_seasonal_daily_fig(certs, f"{cfg['name']} certified stocks", f"Certs ({cfg['stock_unit']})", n),
                        width="stretch", config=cfgc, key=f"pl{comm}_s2")


# ---------------------------------------------------------------- combined Arabica & Robusta
def to_unit(kind: str, s, unit: str):
    """kind KC = bags, RC = lots. Returns the values in bags or MT."""
    if unit == "Bags":
        return s if kind == "KC" else s * LOT_MT / BAG_MT
    return s * BAG_MT if kind == "KC" else s * LOT_MT


CMB_PORT = {"ANT": "Antwerp", "BAR": "Barcelona", "HAM": "Ham/Bre", "BRE": "Ham/Bre", "LON": "London", "FEL": "Felixstowe",
            "LIV": "Liverpool", "AMS": "Amsterdam", "ROT": "Rotterdam", "GEN": "Genoa", "TRI": "Trieste", "LEH": "Le Havre",
            "NOR": "Virginia"}      # Robusta port codes on the Arabica port names (Ham + Bre together, Norfolk = Virginia)


@st.cache_data(ttl=3600, show_spinner=False)
def cmb_certs_frame(kc_certs: pd.Series, rc_certs: pd.Series) -> pd.DataFrame:
    """Certs on every business day: A = Arabica bags, R = Robusta lots. Days without a print (holidays, Robusta sparse early
    years, feed gaps) carry the last value so the charts have no holes; is_kc marks days Arabica really printed."""
    idx = pd.bdate_range(min(kc_certs.index.min(), rc_certs.index.min()), max(kc_certs.index.max(), rc_certs.index.max()))
    df = pd.DataFrame({"A": kc_certs.reindex(idx), "R": rc_certs.reindex(idx)})
    df["is_kc"] = df["A"].notna()
    df["A"] = df["A"].ffill(limit=25)
    df["R"] = df["R"].ffill(limit=25)
    return df.dropna(subset=["A", "R"])


def cmb_certs_table_html(df: pd.DataFrame, unit: str, nrows: int = 0, height: str = "72vh", monthly: bool = False) -> str:
    if monthly:
        df = df.groupby(df.index.to_period("M"))[["A", "R"]].last()       # month-end (latest print for the current month)
    else:
        df = df[df["is_kc"]]                                              # days Arabica really printed
    a, r = to_unit("KC", df["A"], unit), to_unit("RC", df["R"], unit)
    t = a + r
    da, dr, dt = a.diff(), r.diff(), t.diff()
    idx = df.index[::-1]
    if nrows:
        idx = idx[:nrows]
    when = "Month-end certified stocks and monthly change" if monthly else "Certified stocks and daily change"
    lab = (lambda d: d.strftime("%b %Y")) if monthly else (lambda d: d.strftime("%d-%b-%y"))
    tsc = max(float(t.max()), 1.0)
    csc = max(float(pd.concat([da, dr]).abs().max()), 1.0)
    tcs = max(float(dt.abs().max()), 1.0)
    out = [f"<div class='mt' style='margin-bottom:4px'>{when}, Arabica and Robusta ({unit})</div>",
           f"<div class='rwrap' style='height:{height}'><table class='rpt cmp'><thead><tr class='h1'>"
           f"<th class='dt' rowspan='2'>{'Month' if monthly else 'Date'}</th>",
           f"<th colspan='3'>Certified stocks</th><th colspan='3' class='sep certs-hdr'>{'Change on the month' if monthly else 'Change on the day'}</th></tr><tr class='h2'>",
           "<th>Arabica</th><th>Robusta</th><th>Total</th><th class='sep certs-hdr'>Arabica</th><th class='certs-hdr'>Robusta</th>"
           "<th class='certs-hdr'>Total</th></tr></thead><tbody>"]
    for d in idx:
        out.append(f"<tr><td class='d'>{lab(d)}</td><td>{_fmt_i(a[d])}</td><td>{_fmt_i(r[d])}</td>{_bar_td(t[d], tsc)}"
                   + _delta_td(da[d], csc, "cb sep") + _delta_td(dr[d], csc) + _delta_td(dt[d], tcs) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


def cmb_certs_line_fig(df: pd.DataFrame, unit: str, height: int = 420) -> go.Figure:
    a, r = to_unit("KC", df["A"], unit), to_unit("RC", df["R"], unit)
    fig = go.Figure()
    for name, ser, col, w, dash in (("Arabica", a, NAVY, 2, None), ("Robusta", r, AMBER, 2, None), ("Total", a + r, "#8a94a8", 1.3, "dot")):
        fig.add_trace(go.Scatter(x=ser.index, y=ser.values, mode="lines", name=name, line=dict(color=col, width=w, dash=dash),
                                 hovertemplate="%{y:,.0f}<extra>" + name + "</extra>"))
    chart_layout(fig, f"Certified stocks by coffee ({unit})", height)
    fig.update_layout(hovermode="x unified", yaxis=dict(title=unit, tickformat=","),
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"), margin=dict(t=56, b=8, l=8, r=8))
    return fig


def cmb_certs_bar_fig(df: pd.DataFrame, unit: str, height: int = 420) -> go.Figure:
    a, r = to_unit("KC", df["A"], unit), to_unit("RC", df["R"], unit)
    fig = go.Figure()
    for name, ser, col in (("Arabica", a, NAVY), ("Robusta", r, AMBER)):
        fig.add_trace(go.Bar(x=ser.index, y=ser.values, name=name, marker=dict(color=col, line=dict(width=0)),
                             hovertemplate="%{y:,.0f}<extra>" + name + "</extra>"))
    chart_layout(fig, f"Certified stocks: Arabica and Robusta ({unit})", height)
    fig.update_layout(barmode="stack", bargap=0, hovermode="x unified", yaxis=dict(title=unit, tickformat=","),
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"), margin=dict(t=56, b=8, l=8, r=8))
    return fig


CMB_FREQ = {"1 day": None, "1 week": "W-SUN", "1 month": "M"}


@st.cache_data(ttl=3600, show_spinner=False)
def cmb_grading_blocks(g: pd.DataFrame, gdays: pd.Series, gr: pd.DataFrame, freq: str) -> tuple:
    """Graded by origin per day, week (Monday to Sunday) or month: Arabica Passed bags and Robusta lots (raw units)."""
    kp = kc_gr_wide(g, pd.Series(gdays), "Passed")
    rr = gr.groupby(["PanelDate", "OriginName"])["NoLots"].sum().unstack(fill_value=0)
    per = CMB_FREQ[freq]
    if per is None:
        return kp, rr
    return kp.groupby(kp.index.to_period(per)).sum(), rr.groupby(rr.index.to_period(per)).sum()


def cmb_row_label(k, freq: str) -> str:
    if freq == "1 day":
        return k.strftime("%d-%b-%y")
    if freq == "1 week":
        return "Wk " + k.start_time.strftime("%d-%b-%y")
    return k.strftime("%b %Y")


def cmb_grading_table_html(ka: pd.DataFrame, rm: pd.DataFrame, unit: str, show_all: bool, freq: str = "1 month",
                           nrows: int = 0, top_n: int = 6) -> str:
    A, R = to_unit("KC", ka, unit), to_unit("RC", rm, unit)

    def block(df):
        order = list(df.sum().sort_values(ascending=False).index)
        shown = order if show_all else order[:top_n]
        out = df[shown].copy()
        if not show_all and len(order) > top_n:
            out["Other"] = df[order[top_n:]].sum(axis=1)
        return out

    ab, rb = block(A), block(R)
    months = sorted(set(A.index) | set(R.index), reverse=True)
    if nrows:
        months = months[:nrows]
    ab, rb = ab.reindex(months), rb.reindex(months)          # periods before a coffee's data starts stay blank
    at_, rt = ab.sum(axis=1, min_count=1), rb.sum(axis=1, min_count=1)
    comb = at_.fillna(0) + rt.fillna(0)
    sa, sr = max(float(ab.max().max()), 1.0), max(float(rb.max().max()), 1.0)
    sta, str_, stc = max(float(at_.max()), 1.0), max(float(rt.max()), 1.0), max(float(comb.max()), 1.0)
    na, nr = len(ab.columns) + 1, len(rb.columns) + 1
    first = {"1 day": "Day", "1 week": "Week", "1 month": "Month"}[freq]
    out = [f"<div class='mt' style='margin-bottom:4px'>Graded per {freq.split()[1]} by origin, Arabica and Robusta side by side ({unit})</div>",
           f"<div class='rwrap' style='height:{'72vh' if freq != '1 month' else 'auto'}'><table class='rpt cmp'><thead><tr class='h1'>"
           f"<th class='dt' rowspan='2'>{first}</th>",
           f"<th colspan='{na}'>Arabica graded by origin</th><th colspan='{nr}' class='sep certs-hdr'>Robusta graded by origin</th>",
           "<th class='sep'>Both</th></tr><tr class='h2'>"]
    out += [f"<th>{o}</th>" for o in ab.columns] + ["<th>Total</th>"]
    out += [f"<th class='certs-hdr{' sep' if i == 0 else ''}'>{o}</th>" for i, o in enumerate(list(rb.columns) + ["Total"])]
    out += ["<th class='sep'>Total</th></tr></thead><tbody>"]
    for m in months:
        row = [f"<tr><td class='d'>{cmb_row_label(m, freq)}</td>"]
        row += [_heat_td(ab.loc[m, o], sa) for o in ab.columns] + [_bar_td(at_[m], sta) if pd.notna(at_[m]) else "<td class='na'></td>"]
        cells = [_heat_td(rb.loc[m, o], sr) for o in rb.columns]
        cells[0] = cells[0].replace("<td", "<td class='sep'", 1)
        row += cells + [_bar_td(rt[m], str_) if pd.notna(rt[m]) else "<td class='na'></td>"]
        row.append(_bar_td(comb[m], stc).replace("<td", "<td class='sep'", 1) if comb[m] else "<td class='na sep'></td>")
        out.append("".join(row) + "</tr>")
    return "".join(out) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def cmb_grading_daily(g: pd.DataFrame, gdays: pd.Series, gr: pd.DataFrame, origin: str, port: str) -> tuple:
    """Daily graded for one origin and port (or all), Arabica bags and Robusta lots (raw units)."""
    sub = g[g["Tag"] == "Passed"]
    if origin != "All origins":
        sub = sub[sub["Origin"] == origin]
    if port != "All ports":
        sub = sub[sub["Port"] == port]
    a = sub.groupby("Date")["Bags"].sum().reindex(pd.DatetimeIndex(gdays), fill_value=0)
    rr = gr.assign(PortName=gr["PortId"].map(CMB_PORT).fillna(gr["PortId"]))
    if origin != "All origins":
        rr = rr[rr["OriginName"] == origin]
    if port != "All ports":
        rr = rr[rr["PortName"] == port]
    r = rr.groupby("PanelDate")["NoLots"].sum().reindex(pd.bdate_range(gr["PanelDate"].min(), gr["PanelDate"].max()), fill_value=0)
    return a, r


def cmb_bar_fig(s: pd.Series, title: str, color: str, unit: str) -> go.Figure:
    m = s.groupby(s.index.to_period("M")).sum()
    fig = go.Figure(go.Bar(x=[p.strftime("%b %y") for p in m.index], y=m.values, marker_color=color,
                           hovertemplate="%{x}: %{y:,.0f}<extra></extra>"))
    chart_layout(fig, title, 360)
    fig.update_layout(showlegend=False, bargap=0.25, xaxis=dict(type="category", tickangle=-90, tickfont=dict(size=9)),
                      yaxis=dict(title=unit, tickformat=","))
    return fig


def cmb_rolling_fig(s: pd.Series, title: str, unit: str, start) -> go.Figure:
    lines = (("1 day", s, "#b8c0d6", 1.0), ("1 week (5d)", s.rolling(5, min_periods=1).sum(), TEAL, 1.8),
             ("1 month (21d)", s.rolling(21, min_periods=1).sum(), NAVY, 2.4))
    fig = go.Figure()
    for name, ser, col, w in lines:
        ser = ser if start is None else ser[ser.index >= start]
        fig.add_trace(go.Scatter(x=ser.index, y=ser.values, mode="lines", name=name, line=dict(color=col, width=w),
                                 hovertemplate="%{y:,.0f}<extra>" + name + "</extra>"))
    chart_layout(fig, title, 360)
    fig.update_layout(yaxis=dict(title=unit, tickformat=","), legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
                      margin=dict(t=56, b=8, l=8, r=8))
    return fig


def render_combined(kc: pd.DataFrame, g: pd.DataFrame, gdays: pd.Series, gr: pd.DataFrame, rc_certs: pd.DataFrame) -> None:
    cfgc = {"displayModeBar": False}
    top_l, top_r = st.columns([6, 1.6])
    with top_l:
        with st.container(key="rc_view_box"):
            view = st.radio("View", ["Certs Table", "Certs Visuals", "Grading", "Origin & Port", "Price Link"], horizontal=True,
                            label_visibility="collapsed", key="cmb_view")
    with top_r:
        with st.container(key="cmb_unit_box"):
            unit = st.radio("Unit", ["Bags", "MT"], horizontal=True, label_visibility="collapsed", key="cmb_unit")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if view in ("Certs Table", "Certs Visuals"):
        df = cmb_certs_frame(kc.set_index("Date")["KC-TOT-TOT"].astype(float).dropna(),
                             rc_certs.set_index("Date")["LRC-TOT-VG"].dropna().astype(float))
    if view == "Certs Table":
        c1, _ = st.columns([1.8, 5])
        with c1:
            n_rows = rows_radio("cmb_rows")
        st.markdown(cmb_certs_table_html(df, unit, n_rows), unsafe_allow_html=True)
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown(cmb_certs_table_html(df, unit, 0, "auto", True), unsafe_allow_html=True)

    elif view == "Certs Visuals":
        c1, _ = st.columns([1.8, 5])
        with c1:
            span = pl_span_radio("cmb_span", "All")
        dv = _since(df, pl_start(span, df.index.max()))
        left, right = st.columns(2)
        with left:
            st.plotly_chart(cmb_certs_bar_fig(dv, unit), width="stretch", config=cfgc, key="cmb_bar")
        with right:
            st.plotly_chart(cmb_certs_line_fig(dv, unit), width="stretch", config=cfgc, key="cmb_line")

    elif view == "Price Link":
        render_arb(kc, g, gdays, gr, rc_certs)

    elif view == "Grading":
        o0, o1, o2, _ = st.columns([2.2, 2.4, 2.4, 1.6])
        with o0:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Group by</div>", unsafe_allow_html=True)
            gfreq = st.radio("Group by", list(CMB_FREQ), index=2, horizontal=True, label_visibility="collapsed", key="cmb_gr_freq")
        with o1:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Origins shown</div>", unsafe_allow_html=True)
            show_all = st.radio("Origins", ["Top 6 + Other", "Show all origins"], horizontal=True, label_visibility="collapsed",
                                key="cmb_gr_all") == "Show all origins"
        n_gr = 0
        if gfreq == "1 day":
            with o2:
                n_gr = rows_radio("cmb_gr_rows")
        ka, rm = cmb_grading_blocks(g, gdays, gr, gfreq)
        st.markdown(cmb_grading_table_html(ka, rm, unit, show_all, gfreq, n_gr), unsafe_allow_html=True)

    else:
        kp_cols = list(kc_gr_wide(g, gdays, "Passed").columns)
        rc_orig = sorted(gr["OriginName"].unique())
        origins = ["All origins"] + sorted(set(kp_cols) | set(rc_orig))
        ports = ["All ports"] + sorted(set(g["Port"].unique()) | set(gr["PortId"].map(CMB_PORT).fillna(gr["PortId"]).unique()))
        f1, f2, f3, _ = st.columns([1.6, 1.6, 2.2, 2])
        with f1:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Origin</div>", unsafe_allow_html=True)
            origin = st.selectbox("Origin", origins, index=0, label_visibility="collapsed", key="cmb_op_origin")
        with f2:
            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Port</div>", unsafe_allow_html=True)
            port = st.selectbox("Port", ports, index=0, label_visibility="collapsed", key="cmb_op_port")
        with f3:
            span = pl_span_radio("cmb_op_span", "1Y")
        a_raw, r_raw = cmb_grading_daily(g, gdays, gr, origin, port)
        a, r = to_unit("KC", a_raw, unit), to_unit("RC", r_raw, unit)
        lab = f"{origin} at {port}"
        left, right = st.columns(2)
        pl_section("Graded per month")
        with left:
            st.plotly_chart(cmb_bar_fig(a, f"Arabica: {lab} ({unit})", NAVY, unit), width="stretch", config=cfgc, key="cmb_op_bar_a")
        with right:
            st.plotly_chart(cmb_bar_fig(r, f"Robusta: {lab} ({unit})", AMBER, unit), width="stretch", config=cfgc, key="cmb_op_bar_r")
        pl_section("Rolling graded: 1 day, 1 week, 1 month")
        start_a, start_r = pl_start(span, a.index.max()), pl_start(span, r.index.max())
        left, right = st.columns(2)
        with left:
            st.plotly_chart(cmb_rolling_fig(a, f"Arabica: {lab} ({unit})", unit, start_a), width="stretch", config=cfgc, key="cmb_op_roll_a")
        with right:
            st.plotly_chart(cmb_rolling_fig(r, f"Robusta: {lab} ({unit})", unit, start_r), width="stretch", config=cfgc, key="cmb_op_roll_r")


ARB_KG = 22.0462      # c/lb -> USD/MT


def _on(s: pd.Series, bd: pd.DatetimeIndex, limit: int = 25) -> pd.Series:
    return s.reindex(s.index.union(bd)).ffill(limit=limit).reindex(bd)


def _flow_on(s: pd.Series, bd: pd.DatetimeIndex) -> pd.Series:
    """A daily flow on the price calendar: unknown before it starts, zero on days without an entry after that."""
    out = s.reindex(bd)
    out.loc[out.index >= s.index.min()] = out.loc[out.index >= s.index.min()].fillna(0)
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def arb_frame(pl_k: pd.DataFrame, pl_r: pd.DataFrame, kc_certs: pd.Series, rc_certs: pd.Series, kc_graded: pd.Series,
              rc_graded: pd.Series, kc_usage: pd.Series, rc_usage: pd.Series) -> pd.DataFrame:
    """Arabica - Robusta arb (C1 on both, USD/MT) with the certs, graded and usage of each coffee in MT on the same days."""
    px = pd.concat([pl_k["c1"].rename("kc"), pl_r["c1"].rename("rc")], axis=1).dropna()
    bd = px.index
    d = pd.DataFrame(index=bd)
    d["spread"] = px["kc"] * ARB_KG - px["rc"]
    d["ratio"] = px["kc"] * ARB_KG / px["rc"]
    d["A_certs"], d["R_certs"] = _on(kc_certs * BAG_MT, bd), _on(rc_certs * LOT_MT, bd)
    for key, a, r in (("graded", kc_graded * BAG_MT, rc_graded * LOT_MT), ("usage", kc_usage * BAG_MT, rc_usage * LOT_MT)):
        d[f"A_{key}"] = _flow_on(a, bd).rolling(21, min_periods=21).sum()
        d[f"R_{key}"] = _flow_on(r, bd).rolling(21, min_periods=21).sum()
    for key in ("certs", "graded", "usage"):
        tot = d[f"A_{key}"] + d[f"R_{key}"]
        d[f"share_{key}"] = (d[f"A_{key}"] / tot * 100).where(tot > 0)
    return d


def arb_dual_fig(d: pd.DataFrame, lefts: list, right: str, right_name: str, title: str, l_title: str, r_title: str,
                 height: int = 340) -> go.Figure:
    """lefts: [(column, name, colour)] on the left axis, the arb line on the right axis."""
    fig = go.Figure()
    for col, name, colr in lefts:
        v = d[col].dropna()
        fig.add_trace(go.Scatter(x=v.index, y=v.values, mode="lines", name=name, line=dict(color=colr, width=1.8),
                                 hovertemplate="%{y:,.1f}<extra>" + name + "</extra>"))
    v = d[right].dropna()
    fig.add_trace(go.Scatter(x=v.index, y=v.values, mode="lines", name=right_name, yaxis="y2", line=dict(color=RED, width=1.6),
                             hovertemplate="%{y:,.1f}<extra>" + right_name + "</extra>"))
    chart_layout(fig, title, height)
    fig.update_layout(hovermode="x unified", yaxis=dict(title=l_title, tickformat=","),
                      yaxis2=dict(title=r_title, overlaying="y", side="right", showgrid=False, tickformat=","),
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"), margin=dict(t=56, b=8, l=8, r=8))
    return fig


def arb_together_fig(d: pd.DataFrame, height: int = 800) -> go.Figure:
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=("Arb spread, KC C1 - RC C1 (USD/MT)", "Arabica share of certified stocks (%)",
                                        "Arabica share of graded and usage, rolling 1 month (%)"))
    rows = ((1, "spread", "Arb", RED), (2, "share_certs", "Certs", NAVY), (3, "share_graded", "Graded", TEAL), (3, "share_usage", "Usage", AMBER))
    for r, col, name, colr in rows:
        v = d[col].dropna()
        fig.add_trace(go.Scatter(x=v.index, y=v.values, mode="lines", name=name, line=dict(color=colr, width=1.8),
                                 hovertemplate="%{y:,.1f}<extra>" + name + "</extra>"), row=r, col=1)
    chart_layout(fig, "Arb, certs, graded and usage together", height)
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=1.03, x=1, xanchor="right", yanchor="bottom"),
                      margin=dict(t=72, b=8, l=8, r=8))
    for ann in fig.layout.annotations:
        ann.font = dict(size=12, color=NAVY)
        ann.x = 0
        ann.xanchor = "left"
    return fig


def arb_lag_fig(d: pd.DataFrame, height: int = 340) -> go.Figure:
    ch = d["spread"].diff(21)
    fig = go.Figure()
    ks = list(range(-60, 61, 5))
    for col, name, colr in (("share_certs", "Certs", NAVY), ("share_graded", "Graded", TEAL), ("share_usage", "Usage", AMBER)):
        x = d[col].diff(21)
        fig.add_trace(go.Scatter(x=ks, y=[ch.corr(x.shift(k)) for k in ks], mode="lines+markers", name=name,
                                 line=dict(color=colr, width=1.8), marker=dict(size=4), hovertemplate="%{y:+.2f}<extra>" + name + "</extra>"))
    chart_layout(fig, "Correlation: 1-month change in Arabica share vs 1-month change in arb, by lead (days)", height)
    fig.update_layout(hovermode="x unified", xaxis=dict(title="Share leads arb by (days)", dtick=10),
                      yaxis=dict(title="Correlation", zeroline=True, zerolinecolor="#9aa3b8", tickformat=".2f"),
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"), margin=dict(t=56, b=8, l=8, r=8))
    return fig


def render_arb(kc: pd.DataFrame, g: pd.DataFrame, gdays: pd.Series, gr: pd.DataFrame, rc_certs: pd.DataFrame) -> None:
    cfgc = {"displayModeBar": False}
    ku, ru = pl_series_kc(kc, g, gdays), pl_series_rc(gr, rc_certs)
    d = arb_frame(load_price_link(), load_price_link_rc(), ku["certs"], ru["certs"],
                  kc_gr_wide(g, gdays, "Passed").sum(axis=1), gr.groupby("PanelDate")["NoLots"].sum(), ku["usage"].dropna(), ru["usage"].dropna())
    with st.container(key="cmb_pl_box"):
        v = st.radio("Arb view", ["Arb vs Certs", "Arb vs Grading", "Arb vs Usage", "All Together", "Scatter"], horizontal=True,
                     label_visibility="collapsed", key="cmb_pl_view")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    default = "3Y" if v in ("All Together", "Scatter") else "All"
    c1, _ = st.columns([1.8, 5])
    with c1:
        span = pl_span_radio("cmb_pl_span", default)
    dv = _since(d, pl_start(span, d.index.max()))
    A, R, arb = ("Arabica", NAVY), ("Robusta", AMBER), "spread"

    if v == "Arb vs Certs":
        pl_section("Arb and certified stocks")
        st.plotly_chart(arb_dual_fig(dv, [("share_certs", "Arabica share of certs (%)", NAVY)], arb, "Arb (USD/MT)",
                                     "Arb spread vs Arabica share of certified stocks", "Arabica share (%)", "Arb (USD/MT)"),
                        width="stretch", config=cfgc, key="arb_c1")
        st.plotly_chart(arb_dual_fig(dv, [("A_certs", "Arabica (MT)", NAVY), ("R_certs", "Robusta (MT)", AMBER)], "ratio", "KC / RC",
                                     "KC / RC ratio vs certified stocks", "Certs (MT)", "KC / RC"), width="stretch", config=cfgc, key="arb_c2")
    elif v == "Arb vs Grading":
        pl_section("Arb and graded, rolling 1 month")
        st.plotly_chart(arb_dual_fig(dv, [("A_graded", "Arabica (MT)", NAVY), ("R_graded", "Robusta (MT)", AMBER)], arb, "Arb (USD/MT)",
                                     "Arb spread vs graded", "Graded (MT)", "Arb (USD/MT)"), width="stretch", config=cfgc, key="arb_g1")
        st.plotly_chart(arb_dual_fig(dv, [("share_graded", "Arabica share of graded (%)", TEAL)], arb, "Arb (USD/MT)",
                                     "Arb spread vs Arabica share of graded", "Arabica share (%)", "Arb (USD/MT)"), width="stretch", config=cfgc, key="arb_g2")
    elif v == "Arb vs Usage":
        pl_section("Arb and usage, rolling 1 month")
        st.plotly_chart(arb_dual_fig(dv, [("A_usage", "Arabica (MT)", NAVY), ("R_usage", "Robusta (MT)", AMBER)], arb, "Arb (USD/MT)",
                                     "Arb spread vs usage", "Usage (MT)", "Arb (USD/MT)"), width="stretch", config=cfgc, key="arb_u1")
        st.plotly_chart(arb_dual_fig(dv, [("share_usage", "Arabica share of usage (%)", AMBER)], arb, "Arb (USD/MT)",
                                     "Arb spread vs Arabica share of usage", "Arabica share (%)", "Arb (USD/MT)"), width="stretch", config=cfgc, key="arb_u2")
    elif v == "All Together":
        st.plotly_chart(arb_together_fig(dv), width="stretch", config=cfgc, key="arb_all")
    else:
        pl_section("Arb vs Arabica share")
        cols = st.columns(3)
        for col_, (share, ttl) in zip(cols, (("share_certs", "certs"), ("share_graded", "graded"), ("share_usage", "usage"))):
            with col_:
                st.plotly_chart(pl_scatter_fig(dv[share], dv["spread"], f"Arb vs share of {ttl}", f"Arabica share of {ttl} (%)",
                                               "Arb (USD/MT)", size=430), width="content", config=cfgc, key=f"arb_sc_{share}")
        st.plotly_chart(arb_lag_fig(dv), width="stretch", config=cfgc, key="arb_lag")


with st.sidebar:
    st.markdown("<div class='sb-title'>Daily Miner</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-label'>Commodity</div>", unsafe_allow_html=True)
    commodity = st.radio("Commodity", COMMODITIES, label_visibility="collapsed")

if commodity == "Coffee":
    # Lazy radio again (see the note on rc_section_box below): Arabica now carries real work of
    # its own (the KC matrices and grading-flow table), so a real st.tabs here would rebuild all
    # of that every time something changes on the Robusta side, and vice versa.
    with st.container(key="coffee_section_box"):
        coffee_section = st.radio("Coffee section", ["Arabica", "Robusta", "Arabica & Robusta"], horizontal=True,
                                  label_visibility="collapsed", key="coffee_section")
    st.markdown("<hr style='border:none;border-top:1px solid #dfe3ee;margin:10px 0 14px'>", unsafe_allow_html=True)

    if coffee_section == "Arabica":
        kc = load_kc_certs()
        with st.container(key="rc_section_box"):
            ar_section = st.radio("Arabica section", ["Comprehensive View", "Certs", "Grading", "Usage", "Price Link"], horizontal=True,
                                  label_visibility="collapsed", key="ar_section")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if ar_section == "Certs":
            with st.container(key="rc_view_box"):
                ar_view = st.radio("View", ["Certs Change Matrix", "Visuals", "Seasonality"], horizontal=True,
                                   label_visibility="collapsed", key="ar_certs_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if ar_view == "Certs Change Matrix":
                k_min, k_max = kc["Date"].min(), kc["Date"].max()
                k_prev = kc["Date"].iloc[-2] if len(kc) > 1 else k_max  # previous trading day, not just latest-1
                k_dates = kc["Date"].values

                def on_or_before(target: pd.Timestamp) -> pd.Timestamp:
                    i = max(int(np.searchsorted(k_dates, np.datetime64(target), side="right")) - 1, 0)
                    return pd.Timestamp(k_dates[i])

                sp_col, _ = st.columns([1, 4])
                with sp_col:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Certs Change period</div>",
                               unsafe_allow_html=True)
                    span_pick = st.selectbox("Certs Change period", ["Day", "Week", "Month", "Custom"],
                                             label_visibility="collapsed", key="ar_span")
                if span_pick == "Day":
                    older_ts, latest_ts = k_prev, k_max
                elif span_pick == "Week":
                    older_ts, latest_ts = on_or_before(k_max - pd.DateOffset(weeks=1)), k_max
                elif span_pick == "Month":
                    older_ts, latest_ts = on_or_before(k_max - pd.DateOffset(months=1)), k_max
                else:
                    with st.container(key="ar_dates_custom_box"):
                        dc1, dc2, _ = st.columns([1, 1, 4])
                        with dc1:
                            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Older Date</div>", unsafe_allow_html=True)
                            older_pick = st.date_input("Older date", value=k_prev.date(),
                                                       min_value=k_min.date(), max_value=k_max.date(),
                                                       key="ar_older", label_visibility="collapsed")
                        with dc2:
                            st.markdown("<div class='sb-label' style='margin:0 0 2px'>Latest Date</div>", unsafe_allow_html=True)
                            latest_pick = st.date_input("Latest date", value=k_max.date(),
                                                        min_value=k_min.date(), max_value=k_max.date(),
                                                        key="ar_latest", label_visibility="collapsed")
                    older_ts, latest_ts = pd.Timestamp(older_pick), pd.Timestamp(latest_pick)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                # st.columns always splits the row into two EQUAL-width halves, but these tables
                # are fit-content width - if one table is narrower than its half, the leftover
                # space inside that column reads as a huge gap. A single flex wrapper sizes each
                # side to its own content instead, so the two tables sit right next to each other.
                st.markdown(
                    "<div style='display:flex; gap:20px; align-items:flex-start; flex-wrap:wrap;'>"
                    f"<div><div class='mt'>Certified Stocks Change ({older_ts.strftime('%d %b %Y')} "
                    f"&rarr; {latest_ts.strftime('%d %b %Y')}, bags)</div>"
                    f"{kc_change_matrix_html(kc, older_ts, latest_ts)}</div>"
                    f"<div><div class='mt'>Latest Certified Stocks ({latest_ts.strftime('%d %b %Y')}, bags)</div>"
                    f"{kc_latest_matrix_html(kc, latest_ts)}</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            elif ar_view == "Visuals":
                ac_min, ac_max = kc["Date"].min(), kc["Date"].max()
                ac_span = st.radio("History", ["1Y", "3Y", "5Y", "All", "Custom"], index=2, horizontal=True,
                                   label_visibility="collapsed", key="ac_chart_span")
                if ac_span == "Custom":
                    acs1, acs2, _ = st.columns([1, 1, 4])
                    with acs1:
                        ac_from = st.date_input("Start date", value=(ac_max - pd.DateOffset(years=3)).date(),
                                                min_value=ac_min.date(), max_value=ac_max.date(), key="ac_chart_from")
                    with acs2:
                        ac_to = st.date_input("End date", value=ac_max.date(),
                                              min_value=ac_min.date(), max_value=ac_max.date(), key="ac_chart_to")
                    ac_start, ac_end = pd.Timestamp(ac_from), pd.Timestamp(ac_to)
                elif ac_span == "All":
                    ac_start, ac_end = ac_min, ac_max
                else:
                    ac_start, ac_end = ac_max - pd.DateOffset(years=int(ac_span[0])), ac_max
                acview = kc[(kc["Date"] >= ac_start) & (kc["Date"] <= ac_end)]
                accfg = {"displayModeBar": False}

                st.markdown("<div class='sec'>Stock levels</div>", unsafe_allow_html=True)
                acv1, acv2, acv3 = st.columns(3)
                with acv1:
                    st.plotly_chart(kc_total_certs_fig(acview), width="stretch", config=accfg)
                with acv2:
                    st.plotly_chart(kc_ports_certs_fig(acview), width="stretch", config=accfg)
                with acv3:
                    st.plotly_chart(kc_country_certs_fig(acview), width="stretch", config=accfg)

                st.markdown("<div class='sec'>Origin mix</div>", unsafe_allow_html=True)
                show_all = st.radio("Origins shown", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                    label_visibility="collapsed", key="ac_origin_all") == "Show all origins"
                acm1, acm2, acm3 = st.columns(3)
                with acm1:
                    st.plotly_chart(kc_origin_mix_fig(acview, show_all=show_all), width="stretch", config=accfg)
                with acm2:
                    st.plotly_chart(kc_origin_share_fig(acview, show_all=show_all), width="stretch", config=accfg)
                with acm3:
                    st.plotly_chart(kc_latest_breakup_fig(kc), width="stretch", config=accfg)

                st.markdown("<div class='sec'>Momentum</div>", unsafe_allow_html=True)
                aco1, aco2 = st.columns(2)
                with aco1:
                    ac_roll_n = st.radio("Rolling window", [5, 20, 60], index=1, horizontal=True,
                                        format_func=lambda n: f"Rolling {n}d", label_visibility="collapsed",
                                        key="ac_roll_n")
                with aco2:
                    ac_order, _ = kc_origin_palette(kc)
                    ac_origin_opts = {KC_ORIGIN_NAMES[o]: o for o in ac_order}
                    ac_roll_pick = st.multiselect("Rolling origins", list(ac_origin_opts), default=["Brazil"],
                                                  key="ac_roll_origins", label_visibility="collapsed",
                                                  placeholder="Choose origins")
                acr1, acr2 = st.columns(2)
                with acr1:
                    st.plotly_chart(rolling_fig(kc.set_index("Date")["KC-TOT-TOT"], ac_roll_n, ac_start, ac_end,
                                                f"Rolling Change: Total ({ac_roll_n}d)"), width="stretch", config=accfg)
                with acr2:
                    ac_roll_codes = [ac_origin_opts[n] for n in ac_roll_pick]
                    st.plotly_chart(kc_rolling_origins_fig(kc, ac_roll_codes, ac_roll_n, ac_start, ac_end),
                                    width="stretch", config=accfg)

            else:
                ac_order, _ = kc_origin_palette(kc)
                as_origin_opts = ["Total"] + [KC_ORIGIN_NAMES[o] for o in ac_order]
                as_port_opts = ["Total"] + [KC_PORT_NAMES[p] for p in kc_major_ports(kc)]
                port_name_to_code = {v: k for k, v in KC_PORT_NAMES.items()}
                origin_name_to_code = {v: k for k, v in KC_ORIGIN_NAMES.items()}

                as_f1, as_f2, _ = st.columns([1, 1, 3])
                with as_f1:
                    as_origin_pick = st.selectbox("Origin", as_origin_opts,
                                                  index=0, key="ac_season_origin")
                with as_f2:
                    as_port_pick = st.selectbox("Port", as_port_opts,
                                                index=0, key="ac_season_port")
                as_o_code = "TOT" if as_origin_pick == "Total" else origin_name_to_code[as_origin_pick]
                as_p_code = "TOT" if as_port_pick == "Total" else port_name_to_code[as_port_pick]
                as_col = f"KC-{as_o_code}-{as_p_code}"
                as_label = f"{as_origin_pick} - {as_port_pick}"

                as_left, as_right = st.columns([2, 3])
                with as_left:
                    st.plotly_chart(seasonality_fig(kc, as_col, f"Seasonality: {as_label}"),
                                    width="stretch", config={"displayModeBar": False})
                with as_right:
                    st.markdown(f"<div class='mt side'>Monthly Change: {as_label}</div>", unsafe_allow_html=True)
                    st.markdown(monthly_change_html(kc, as_col), unsafe_allow_html=True)
                as_chg_all = kc.set_index("Date")[as_col].dropna().astype(float).diff().dropna()
                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
                _asl, asd, _asr = st.columns([1, 2, 1])
                with asd:
                    as_dist_span = st.radio("Distribution window", ["Last 1Y", "Last 5Y", "All"], index=1,
                                            horizontal=True, label_visibility="collapsed", key="ac_dist_span")
                    as_last_dt = as_chg_all.index.max()
                    if as_dist_span == "Last 1Y":
                        as_chg = as_chg_all[as_chg_all.index >= as_last_dt - pd.DateOffset(years=1)]
                    elif as_dist_span == "Last 5Y":
                        as_chg = as_chg_all[as_chg_all.index >= as_last_dt - pd.DateOffset(years=5)]
                    else:
                        as_chg = as_chg_all[as_chg_all.index >= DIST_START]
                    st.plotly_chart(distribution_fig(as_chg, f"Daily Change Distribution: {as_label}", "chg"),
                                    width="stretch", config={"displayModeBar": False})

        elif ar_section == "Grading":
            g, gdays = load_kc_grading()
            g_min, g_max = gdays.min(), gdays.max()
            with st.container(key="rc_view_box"):
                ar_g_view = st.radio("View", ["Table", "Visuals", "Cumulative", "Pending", "Pass Rate"], horizontal=True,
                                     label_visibility="collapsed", key="ar_grading_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            gcfg = {"displayModeBar": False}

            if ar_g_view == "Table":
                mc1, _ = st.columns([1, 5])
                with mc1:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Monthly grading shows</div>", unsafe_allow_html=True)
                    month_tag = st.selectbox("Monthly grading", ["Passed", "Failed", "Total"],
                                             label_visibility="collapsed", key="arg_month_tag")
                m_title = "Passed + Failed" if month_tag == "Total" else month_tag
                st.markdown(f"<div class='mt'>Monthly Grading: {m_title} (bags)</div>", unsafe_allow_html=True)
                st.markdown(kc_gr_monthly_html(g, gdays, month_tag, "auto"), unsafe_allow_html=True)
                st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
                st.markdown("<div class='mt'>Daily Grading (bags)</div>", unsafe_allow_html=True)
                n_g = rows_radio("arg_rows")
                st.markdown(kc_gr_daily_html(g, gdays, "72vh", n_g), unsafe_allow_html=True)

            elif ar_g_view == "Visuals":
                v1, v2, _ = st.columns([2.4, 1.8, 3])
                with v1:
                    g_span = st.radio("Grading history", ["3M", "6M", "1Y", "All", "Custom"], index=0, horizontal=True,
                                      label_visibility="collapsed", key="arg_span")
                with v2:
                    g_all = st.radio("Origins", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                     label_visibility="collapsed", key="arg_origin_all")
                if g_span == "Custom":
                    gc1, gc2, _ = st.columns([1, 1, 4])
                    with gc1:
                        g_from = st.date_input("Start date", value=(g_max - pd.DateOffset(months=3)).date(),
                                               min_value=g_min.date(), max_value=g_max.date(), key="arg_from")
                    with gc2:
                        g_to = st.date_input("End date", value=g_max.date(), min_value=g_min.date(),
                                             max_value=g_max.date(), key="arg_to")
                    gs_, ge_ = pd.Timestamp(g_from), pd.Timestamp(g_to)
                elif g_span == "All":
                    gs_, ge_ = g_min, g_max
                else:
                    gs_, ge_ = g_max - pd.DateOffset(months={"3M": 3, "6M": 6, "1Y": 12}[g_span]), g_max
                show_all_o = g_all == "Show all origins"
                p_w, f_w = kc_gr_wide(g, gdays, "Passed"), kc_gr_wide(g, gdays, "Failed")
                st.plotly_chart(kc_gr_bar_fig(p_w, "Daily Bags Passed | Per Origin", show_all_o, 5, gs_, ge_),
                                width="stretch", config=gcfg)
                st.plotly_chart(kc_gr_bar_fig(f_w, "Daily Bags Failed | Per Origin", show_all_o, 5, gs_, ge_),
                                width="stretch", config=gcfg)

            elif ar_g_view == "Cumulative":
                sc0, sc1, sc2, sc3, _ = st.columns([1, 1, 1.4, 1.4, 2])
                with sc0:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Measure</div>", unsafe_allow_html=True)
                    meas = st.selectbox("Measure", ["Total", "Passed", "Failed"], index=1,
                                        label_visibility="collapsed", key="ars_measure")
                m_w = kc_gr_measure(g, gdays, meas)
                m_p = kc_gr_measure(g, gdays, meas, by="Port")
                with sc1:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Crop year starts</div>", unsafe_allow_html=True)
                    scm = MONTH_ABBR.index(st.selectbox("Crop year starts", MONTH_ABBR, index=6,
                                                        label_visibility="collapsed", key="ars_crop_m")) + 1
                with sc2:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Fourth chart origin</div>", unsafe_allow_html=True)
                    fourth = st.selectbox("Fourth chart", ["Total"] + list(m_w.columns[3:]), index=0,
                                          label_visibility="collapsed", key="ars_fourth")
                with sc3:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Fourth chart port</div>", unsafe_allow_html=True)
                    fourth_p = st.selectbox("Fourth chart port", ["Total"] + list(m_p.columns[3:]), index=0,
                                            label_visibility="collapsed", key="ars_fourth_port")
                m_lbl = "passed + failed" if meas == "Total" else meas.lower()

                st.markdown("<div class='sec'>Per Origin</div>", unsafe_allow_html=True)
                for col_, o in zip(st.columns(4), list(m_w.columns[:3]) + [fourth]):
                    with col_:
                        s_ = m_w.sum(axis=1) if o == "Total" else m_w[o]
                        st.plotly_chart(kc_cum_lines_cached(s_, f"{o} | cumulative {m_lbl}", scm, g_max),
                                        width="stretch", config=gcfg, key=f"arg_cum_o_{o}")

                st.markdown("<div class='sec'>Per Port</div>", unsafe_allow_html=True)
                for col_, p_ in zip(st.columns(4), list(m_p.columns[:3]) + [fourth_p]):
                    with col_:
                        s_ = m_p.sum(axis=1) if p_ == "Total" else m_p[p_]
                        ttl = p_ if p_ == "Total" else f"{p_} ({KC_GR_PORT_COUNTRY[p_]})"
                        st.plotly_chart(kc_cum_lines_cached(s_, f"{ttl} | cumulative {m_lbl}", scm, g_max),
                                        width="stretch", config=gcfg, key=f"arg_cum_p_{p_}")

            elif ar_g_view == "Pending":

                pv1, pv2, _ = st.columns([1.6, 1.8, 3])
                with pv1:
                    p_span = st.radio("Pending history", ["3M", "6M", "1Y", "All"], index=2, horizontal=True,
                                      label_visibility="collapsed", key="arp_span")
                with pv2:
                    p_all = st.radio("Pending origins", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                     label_visibility="collapsed", key="arp_origin_all")
                ps_, pe_ = (g_min, g_max) if p_span == "All" else (
                    g_max - pd.DateOffset(months={"3M": 3, "6M": 6, "1Y": 12}[p_span]), g_max)
                st.plotly_chart(kc_gr_pending_fig(kc_gr_wide(g, gdays, "Pending"), p_all == "Show all origins", 5, ps_, pe_),
                                width="stretch", config=gcfg)
                st.plotly_chart(kc_gr_pending_port_fig(g, gdays, ps_, pe_), width="stretch", config=gcfg)

                pend_w = kc_gr_wide(g, gdays, "Pending")
                cc1, cc2, _ = st.columns([2, 2, 2])
                with cc1:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Origins</div>", unsafe_allow_html=True)
                    c_or = st.multiselect("Pending origins chosen", list(pend_w.columns), default=["Brazil"],
                                          label_visibility="collapsed", key="arp_origins", placeholder="Choose origins")
                with cc2:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Ports</div>", unsafe_allow_html=True)
                    c_po = st.multiselect("Pending ports chosen", KC_GR_PORTS, default=["Antwerp"],
                                          label_visibility="collapsed", key="arp_ports", placeholder="Choose ports")
                st.plotly_chart(kc_gr_pending_combo_fig(g, gdays, tuple(c_or), tuple(c_po), ps_, pe_),
                                width="stretch", config=gcfg)

            else:
                p_w, f_w = kc_gr_wide(g, gdays, "Passed"), kc_gr_wide(g, gdays, "Failed")
                origins_all = ["All origins"] + list(kc_gr_measure(g, gdays, "Total").columns)
                r1, r2, _ = st.columns([1.3, 1.3, 4])
                with r1:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Origin</div>", unsafe_allow_html=True)
                    r_or = st.selectbox("Pass rate origin", origins_all, index=origins_all.index("Brazil"),
                                        label_visibility="collapsed", key="arr_origin")
                with r2:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Port</div>", unsafe_allow_html=True)
                    r_po = st.selectbox("Pass rate port", ["Total Ports"] + KC_GR_PORTS, index=0,
                                        label_visibility="collapsed", key="arr_port")
                mf = kc_gr_month_pf(g, gdays, r_or, r_po)
                lbl = f"{r_or} at {r_po}"
                st.plotly_chart(kc_gr_pf_bars_fig(mf, f"Passed / Failed Bags by Month | {lbl}"),
                                width="stretch", config=gcfg)
                st.plotly_chart(kc_gr_pf_bars_fig(mf, f"Passed / Failed Proportion by Month | {lbl}", proportion=True),
                                width="stretch", config=gcfg)

                rs1, _ = st.columns([2.6, 4])
                with rs1:
                    r_span = st.radio("Pass rate period", ["3M", "6M", "1Y", "All", "Custom"], index=0, horizontal=True,
                                      label_visibility="collapsed", key="arr_span")
                if r_span == "Custom":
                    rc1, rc2, _ = st.columns([1, 1, 4])
                    with rc1:
                        r_from = st.date_input("Start date", value=(g_max - pd.DateOffset(months=3)).date(),
                                               min_value=g_min.date(), max_value=g_max.date(), key="arr_from")
                    with rc2:
                        r_to = st.date_input("End date", value=g_max.date(), min_value=g_min.date(),
                                             max_value=g_max.date(), key="arr_to")
                    rs_, re_ = pd.Timestamp(r_from), pd.Timestamp(r_to)
                elif r_span == "All":
                    rs_, re_ = g_min, g_max
                else:
                    rs_, re_ = g_max - pd.DateOffset(months={"3M": 3, "6M": 6, "1Y": 12}[r_span]), g_max
                st.plotly_chart(kc_gr_rate_bar_fig(kc_gr_day_pf(g, gdays, r_or, r_po),
                                                   f"Pass Rate by Day | {lbl} (label = bags passed)", rs_, re_),
                                width="stretch", config=gcfg)

                st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='mt'>Pass Rate Per Origin | {lbl}</div>", unsafe_allow_html=True)
                st.markdown(kc_passrate_matrix_html(mf["Passed"], mf["Failed"], 1), unsafe_allow_html=True)

        elif ar_section == "Usage":
            g, gdays = load_kc_grading()
            kc = kc_fill_from_ice(kc, g)
            with st.container(key="rc_view_box"):
                ar_cg_view = st.radio("View", ["Usage Per Origin", "Usage Per Port", "Cumulative"], horizontal=True,
                                      label_visibility="collapsed", key="ar_cg_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            ucfg = {"displayModeBar": False}

            if ar_cg_view == "Usage Per Origin":
                t_all = st.radio("Origins", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                 label_visibility="collapsed", key="acg_tbl_origins") == "Show all origins"
                st.markdown(kc_cg_monthly_html(g, gdays, kc, t_all), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                n_u = rows_radio("acg_rows")
                st.markdown(kc_cg_daily_html(g, gdays, kc, t_all, "72vh", False, False, n_u), unsafe_allow_html=True)

            elif ar_cg_view == "Usage Per Port":
                n_up = rows_radio("acg_port_rows")
                st.markdown(kc_cg_port_html(g, gdays, kc, True), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                st.markdown(kc_cg_port_html(g, gdays, kc, False, "72vh", False, False, n_up), unsafe_allow_html=True)

            else:
                du = kc_cg_daily(g, gdays, kc)
                uo = kc_cg_usage_origin(g, gdays, kc)
                up = kc_cg_usage_port(g, gdays, kc)
                ucm_col, _ = st.columns([1, 5])
                with ucm_col:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Cumulative starts</div>", unsafe_allow_html=True)
                    ucm = MONTH_ABBR.index(st.selectbox("Cumulative starts", MONTH_ABBR, index=6,
                                                        label_visibility="collapsed", key="acg_crop_m")) + 1
                last = gdays.max()

                st.markdown("<div class='sec'>Per Origin</div>", unsafe_allow_html=True)
                o_order = list(uo.sum().sort_values(ascending=False).index)
                of_col, _ = st.columns([1.4, 5])
                with of_col:
                    o_fourth = st.selectbox("Fourth chart origin", ["Total"] + o_order[3:], index=0,
                                            label_visibility="collapsed", key="acg_fourth")
                for col_, o in zip(st.columns(4), o_order[:3] + [o_fourth]):
                    with col_:
                        st.plotly_chart(kc_cum_lines_cached(du["Usage"] if o == "Total" else uo[o],
                                                            f"{o} | cumulative usage", ucm, last),
                                        width="stretch", config=ucfg, key=f"acg_cum_o_{o}")

                st.markdown("<div class='sec'>Per Port</div>", unsafe_allow_html=True)
                p_order = list(up.sum().sort_values(ascending=False).index)
                pf_col, _ = st.columns([1.4, 5])
                with pf_col:
                    p_fourth = st.selectbox("Fourth chart port", ["Total"] + p_order[3:], index=0,
                                            label_visibility="collapsed", key="acg_fourth_port")
                for col_, p_ in zip(st.columns(4), p_order[:3] + [p_fourth]):
                    with col_:
                        ttl = p_ if p_ == "Total" else f"{p_} ({KC_GR_PORT_COUNTRY[p_]})"
                        st.plotly_chart(kc_cum_lines_cached(du["Usage"] if p_ == "Total" else up[p_],
                                                            f"{ttl} | cumulative usage", ucm, last),
                                        width="stretch", config=ucfg, key=f"acg_cum_p_{p_}")

                st.markdown("<div class='sec'>Per Country of Port</div>", unsafe_allow_html=True)
                for col_, ct in zip(st.columns(4), ["Belgium", "Spain", "Germany", "USA"]):
                    with col_:
                        cs = up[[p_ for p_ in KC_GR_PORTS if KC_GR_PORT_COUNTRY[p_] == ct]].sum(axis=1)
                        st.plotly_chart(kc_cum_lines_cached(cs, f"{ct} | cumulative usage", ucm, last),
                                        width="stretch", config=ucfg, key=f"acg_cum_c_{ct}")

                st.markdown("<div class='sec'>Monthly Usage by Origin</div>", unsafe_allow_html=True)
                u_all = st.radio("Usage origins", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                 label_visibility="collapsed", key="acg_origin_all")
                st.plotly_chart(kc_usage_by_origin_fig(g, gdays, kc, u_all == "Show all origins"),
                                width="stretch", config=ucfg)

        elif ar_section == "Price Link":
            pl_k, eom_h = load_price_link(), load_eom_hist()
            g_pl, gdays_pl = load_kc_grading()
            render_price_link("KC", pl_k, pl_series_kc(kc_fill_from_ice(kc, g_pl), g_pl, gdays_pl),
                              lambda f: kc_spread_certs_frame(pl_k, kc, eom_h, f))

        else:
            g, gdays = load_kc_grading()
            kc = kc_fill_from_ice(kc, g)
            cv1, cv2, cv3, _ = st.columns([1.2, 2, 1.8, 2])
            with cv3:
                n_cv = rows_radio("acv_rows")
            with cv1:
                st.markdown("<div class='sb-label' style='margin:0 0 2px'>Split by</div>", unsafe_allow_html=True)
                cv_split = st.radio("Split by", ["Origin", "Port"], horizontal=True,
                                    label_visibility="collapsed", key="acv_split")
            cv_all = False
            if cv_split == "Origin":
                with cv2:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>Origins shown</div>", unsafe_allow_html=True)
                    cv_all = st.radio("Origins", ["Top 5 + Other", "Show all origins"], horizontal=True,
                                      label_visibility="collapsed", key="acv_origins") == "Show all origins"
            if cv_split == "Origin":
                st.markdown(kc_cg_daily_html(g, gdays, kc, cv_all, "72vh", True, True, n_cv), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                st.markdown(kc_cg_monthly_html(g, gdays, kc, cv_all, "auto", True, True), unsafe_allow_html=True)
            else:
                st.markdown(kc_cg_port_html(g, gdays, kc, False, "72vh", True, True, n_cv), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                st.markdown(kc_cg_port_html(g, gdays, kc, True, "auto", True, True), unsafe_allow_html=True)
    elif coffee_section == "Robusta":
        # A plain st.radio (not st.tabs) is used for these two levels of navigation: st.tabs
        # renders every tab's body on every rerun regardless of which one is showing, whereas a
        # radio only ever runs the branch that's picked. That is what made switching between
        # Certs/Grading views, or the sub-views inside them, feel slow - every click anywhere on
        # the page was silently rebuilding every table and chart in every tab, every time.
        with st.container(key="rc_section_box"):
            rc_section = st.radio("Section", ["Comprehensive View", "Certs", "Grading", "Certs & Grading", "Price Link"], horizontal=True,
                                  label_visibility="collapsed", key="rc_section")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if rc_section == "Comprehensive View":
            certs = load_rc_certs()
            gr = load_rc_grading()
            rcv_all = st.radio("Ports", ["Top 5 + Other", "Show all ports"], horizontal=True,
                               label_visibility="collapsed", key="rcv_ports") == "Show all ports"
            n_rv = rows_radio("rcv_rows")
            st.markdown(rc_comp_html(gr, certs, False, rcv_all, "72vh", "VG", n_rv), unsafe_allow_html=True)
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.markdown(rc_comp_html(gr, certs, True, rcv_all, "auto"), unsafe_allow_html=True)

        elif rc_section == "Price Link":
            certs = load_rc_certs()
            gr = load_rc_grading()
            pl_r = load_price_link_rc()
            render_price_link("RC", pl_r, pl_series_rc(gr, certs), lambda f: rc_spread_certs_frame(pl_r, certs, f))

        elif rc_section == "Certs":
            certs = load_rc_certs()
            end = certs["Date"].max()
            start = end - pd.DateOffset(years=HISTORY_YEARS)
            with st.container(key="rc_view_box"):
                rc_view = st.radio("View", ["Table", "Visuals", "Seasonality"], horizontal=True,
                                   label_visibility="collapsed", key="rc_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rc_view == "Table":
                st.markdown(certs_report_html(certs, start, end), unsafe_allow_html=True)
            elif rc_view == "Visuals":
                c_min, c_max = certs["Date"].min(), certs["Date"].max()
                span = st.radio("History", ["1Y", "3Y", "5Y", "All", "Custom"], index=2, horizontal=True,
                                label_visibility="collapsed", key="rc_chart_span")
                if span == "Custom":
                    cs, ce, _ = st.columns([1, 1, 4])
                    with cs:
                        c_from = st.date_input("Start date", value=(c_max - pd.DateOffset(years=3)).date(),
                                               min_value=c_min.date(), max_value=c_max.date(), key="rc_chart_from")
                    with ce:
                        c_to = st.date_input("End date", value=c_max.date(),
                                             min_value=c_min.date(), max_value=c_max.date(), key="rc_chart_to")
                    c_start, c_end = pd.Timestamp(c_from), pd.Timestamp(c_to)
                elif span == "All":
                    c_start, c_end = c_min, c_max
                else:
                    c_start, c_end = c_max - pd.DateOffset(years=int(span[0])), c_max
                cview = certs[(certs["Date"] >= c_start) & (certs["Date"] <= c_end)]
                cfg = {"displayModeBar": False}
                port_opts = [k for k in seasonality_options(certs) if k != "Total"]

                st.markdown("<div class='sec'>Stock levels</div>", unsafe_allow_html=True)
                lv1, lv2 = st.columns(2)
                with lv1:
                    st.plotly_chart(total_certs_fig(cview), width="stretch", config=cfg)
                with lv2:
                    st.plotly_chart(ports_certs_fig(cview), width="stretch", config=cfg)

                st.markdown("<div class='sec'>Port mix</div>", unsafe_allow_html=True)
                mx1, mx2, mx3 = st.columns(3)
                with mx1:
                    st.plotly_chart(share_line_fig(cview), width="stretch", config=cfg)
                with mx2:
                    st.plotly_chart(country_share_line_fig(cview), width="stretch", config=cfg)
                with mx3:
                    st.plotly_chart(share_pie_fig(certs), width="stretch", config=cfg)

                st.markdown("<div class='sec'>Momentum</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    roll_n = st.radio("Rolling window", [5, 20, 60], index=1, horizontal=True,
                                      format_func=lambda n: f"Rolling {n}d", label_visibility="collapsed",
                                      key="rc_roll_n")
                with c2:
                    roll_ports = st.multiselect("Rolling ports", port_opts, default=port_opts[:1], key="rc_roll_ports",
                                                label_visibility="collapsed", placeholder="Choose ports")
                mo1, mo2 = st.columns(2)
                with mo1:
                    st.plotly_chart(rolling_fig(certs.set_index("Date")["LRC-TOT-VG"], roll_n, c_start, c_end,
                                                f"Rolling Change: Total ({roll_n}d)"), width="stretch", config=cfg)
                with mo2:
                    st.plotly_chart(rolling_ports_fig(certs, roll_ports, roll_n, c_start, c_end),
                                    width="stretch", config=cfg)
            else:
                opts = seasonality_options(certs)
                s_left, s_right = st.columns([2, 3])
                with s_left:
                    view_pick = st.selectbox("Seasonality", list(opts), key="rc_season_view")
                    st.plotly_chart(seasonality_fig(certs, opts[view_pick], f"Seasonality: {view_pick}"),
                                    width="stretch", config={"displayModeBar": False})
                with s_right:
                    st.markdown(f"<div class='mt side'>Monthly Change: {view_pick}</div>", unsafe_allow_html=True)
                    st.markdown(monthly_change_html(certs, opts[view_pick]), unsafe_allow_html=True)
                chg_all = certs.set_index("Date")[opts[view_pick]].dropna().astype(float).diff().dropna()
                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
                _l, d1, _r = st.columns([1, 2, 1])
                with d1:
                    dist_span = st.radio("Distribution window", ["Last 1Y", "Last 5Y", "All"], index=1, horizontal=True,
                                         label_visibility="collapsed", key="rc_dist_span")
                    last_dt = chg_all.index.max()
                    if dist_span == "Last 1Y":
                        chg = chg_all[chg_all.index >= last_dt - pd.DateOffset(years=1)]
                    elif dist_span == "Last 5Y":
                        chg = chg_all[chg_all.index >= last_dt - pd.DateOffset(years=5)]
                    else:
                        chg = chg_all[chg_all.index >= DIST_START]
                    st.plotly_chart(distribution_fig(chg, f"Daily Change Distribution: {view_pick}", "chg"),
                                    width="stretch", config={"displayModeBar": False})

        elif rc_section == "Grading":
            gr = load_rc_grading()
            with st.container(key="rc_view_box"):
                rg_view = st.radio("View", ["Table", "Visuals", "Seasonality"], horizontal=True,
                                   label_visibility="collapsed", key="rg_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rg_view == "Table":
                st.markdown(grading_table_html(gr), unsafe_allow_html=True)
            elif rg_view == "Visuals":
                gcfg = {"displayModeBar": False}
                g_min, g_max = gr["PanelDate"].min(), gr["PanelDate"].max()
                g_span = st.radio("Grading history", ["3M", "6M", "1Y", "All", "Custom"], index=1, horizontal=True,
                                  label_visibility="collapsed", key="rg_span")
                if g_span == "Custom":
                    gc1, gc2, _ = st.columns([1, 1, 4])
                    with gc1:
                        g_from = st.date_input("Start date", value=(g_max - pd.DateOffset(months=6)).date(),
                                               min_value=g_min.date(), max_value=g_max.date(), key="rg_from")
                    with gc2:
                        g_to = st.date_input("End date", value=g_max.date(),
                                             min_value=g_min.date(), max_value=g_max.date(), key="rg_to")
                    gs_, ge_ = pd.Timestamp(g_from), pd.Timestamp(g_to)
                elif g_span == "All":
                    gs_, ge_ = g_min, g_max
                else:
                    gs_, ge_ = g_max - pd.DateOffset(months={"3M": 3, "6M": 6, "1Y": 12}[g_span]), g_max
                gview = gr[(gr["PanelDate"] >= gs_) & (gr["PanelDate"] <= ge_)]
                o_order, o_colors = grading_origin_palette(gr)
                st.plotly_chart(grading_bar_fig(gview, "OriginName", "Daily Gradings in Lots | Per Origin",
                                                o_order, o_colors), width="stretch", config=gcfg)
                st.plotly_chart(grading_bar_fig(gview, "Class", "Daily Gradings in Lots | Per Class",
                                                GRADING_CLASS_ORDER, GRADING_CLASS_COLORS, GRADING_CLASS_LABEL),
                                width="stretch", config=gcfg)
                port_order = list(gr.groupby("PortId")["NoLots"].sum().sort_values(ascending=False).index)
                st.plotly_chart(grading_bar_fig(gview, "PortId", "Daily Gradings in Lots | Per Port",
                                                port_order, PORT_COLORS), width="stretch", config=gcfg)

            else:
                gcfg2 = {"displayModeBar": False}
                origin_rank = list(gr.groupby("OriginName")["NoLots"].sum().sort_values(ascending=False).index)
                top3, rest = origin_rank[:3], origin_rank[3:]
                cm_col, _ = st.columns([1, 5])
                with cm_col:
                    crop_pick = st.selectbox("Crop year starts", MONTH_ABBR, index=6, key="rg_crop_m")
                crop_m = MONTH_ABBR.index(crop_pick) + 1
                g_first, g_last = gr["PanelDate"].min(), gr["PanelDate"].max()
                q1, q2, q3, q4 = st.columns(4)
                for col_, o in zip((q1, q2, q3), top3):
                    with col_:
                        st.markdown("<div style='height:42px'></div>", unsafe_allow_html=True)
                        st.plotly_chart(crop_seasonality_fig(gr[gr["OriginName"] == o], f"{o} | cumulative lots",
                                                             crop_m, g_first, g_last),
                                        width="stretch", config=gcfg2)
                with q4:
                    other_pick = st.selectbox("Other origin", ["Total Grading"] + rest, index=0,
                                              key="rg_other_origin", label_visibility="collapsed")
                    other_sel = gr if other_pick == "Total Grading" else gr[gr["OriginName"] == other_pick]
                    st.plotly_chart(crop_seasonality_fig(other_sel, f"{other_pick} | cumulative lots",
                                                         crop_m, g_first, g_last),
                                    width="stretch", config=gcfg2)

                st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
                mA, mB = st.columns(2)
                with mA:
                    st.markdown("<div class='mt side'>Monthly Lots Graded: Total</div>", unsafe_allow_html=True)
                    st.markdown(monthly_lots_html(gr, crop_m), unsafe_allow_html=True)
                with mB:
                    mo_pick = st.selectbox("Matrix origin", origin_rank, index=0, key="rg_matrix_origin",
                                           label_visibility="collapsed")
                    st.markdown(monthly_lots_html(gr[gr["OriginName"] == mo_pick], crop_m), unsafe_allow_html=True)

                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
                _gl, gd, _gr = st.columns([1, 2, 1])
                with gd:
                    gd_span = st.radio("Distribution window", ["Last 1Y", "All"], index=1, horizontal=True,
                                       label_visibility="collapsed", key="rg_dist_span")
                    per_panel = gr.groupby("PanelDate")["NoLots"].sum().sort_index()
                    if gd_span == "Last 1Y":
                        per_panel = per_panel[per_panel.index >= per_panel.index.max() - pd.DateOffset(years=1)]
                    st.plotly_chart(distribution_fig(per_panel, "Lots Graded per Panel: Total", "lvl"),
                                    width="stretch", config=gcfg2)

        else:
            certs = load_rc_certs()
            gr = load_rc_grading()
            with st.container(key="rc_view_box"):
                rcg_view = st.radio("View", ["Table", "Visuals", "Seasonality"], horizontal=True,
                                    label_visibility="collapsed", key="rcg_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rcg_view == "Table":
                st.markdown(monthly_grading_certs_html(gr, certs), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                _lag_l, _ = st.columns([1, 5])
                with _lag_l:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>LRC Certs lag</div>",
                               unsafe_allow_html=True)
                    with st.container(key="rcg_lag_box"):
                        lag_pick = st.radio("Certs lag", ["0d", "1d"], index=1, horizontal=True,
                                            label_visibility="collapsed", key="rcg_lag")
                n_rc = rows_radio("rcg_rows")
                st.markdown(daily_grading_certs_html(gr, certs, lag=int(lag_pick[0]), nrows=n_rc), unsafe_allow_html=True)
            elif rcg_view == "Visuals":
                du = daily_usage_series(gr, certs)
                u_min, u_max = du.index.min(), du.index.max()
                g_first, g_last = gr["PanelDate"].min(), gr["PanelDate"].max()
                ucfg = {"displayModeBar": False}
                ucm_col, _ = st.columns([1, 5])
                with ucm_col:
                    ucm_pick = st.selectbox("Cumulative starts", MONTH_ABBR, index=6, key="rcg_crop_m")
                ucm = MONTH_ABBR.index(ucm_pick) + 1
                u1, u2 = st.columns(2)
                with u1:
                    st.plotly_chart(usage_cumulative_fig(du, u_min, u_max, ucm), width="stretch", config=ucfg)
                with u2:
                    st.plotly_chart(crop_seasonality_fig(gr, "Cumulative Total Grading", ucm, g_first, g_last),
                                    width="stretch", config=ucfg)
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                st.plotly_chart(usage_by_origin_fig(gr, certs), width="stretch", config=ucfg)
            else:
                st.markdown("<div class='card-desc'>Coming next.</div>", unsafe_allow_html=True)
    else:
        g_c, gdays_c = load_kc_grading()
        render_combined(kc_fill_from_ice(load_kc_certs(), g_c), g_c, gdays_c, load_rc_grading(), load_rc_certs())
else:
    st.markdown(f"<div class='card-desc'>{commodity}: not built yet.</div>", unsafe_allow_html=True)
