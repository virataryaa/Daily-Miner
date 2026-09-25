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
div[role="radiogroup"] label:has(input:checked) { background: #0a2463 !important; }
div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600; }

/* Section / View pill radios: these replace st.tabs so only the picked branch runs each rerun
   (a real st.tabs renders every tab's body on every rerun; this radio does not). */
.st-key-rc_section_box div[role="radiogroup"] label { padding: 6px 16px !important; }
.st-key-rc_section_box div[role="radiogroup"] label p { font-size: 14px !important; }
.st-key-rc_view_box div[role="radiogroup"] label, .st-key-rg_view_box div[role="radiogroup"] label { padding: 4px 13px !important; }
.st-key-rc_view_box div[role="radiogroup"] label p, .st-key-rg_view_box div[role="radiogroup"] label p { font-size: 13px !important; }
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
.mt.side { margin-top: 30px; }
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


@st.cache_data(ttl=600)
def load_kc_certs() -> pd.DataFrame:
    df = pd.read_parquet(DB_DIR / "kc_certs.parquet")
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

    head = ["<div class='rwrap' style='height:auto'><table class='rpt static'><thead><tr class='h2'>",
            "<th class='dt l'>Origin</th>"]
    head += [f"<th>{KC_PORT_NAMES[p]}</th>" for p in ports] + ["<th class='sep'>Total</th></tr></thead><tbody>"]
    body = []
    for o in origins:
        row = [f"<tr><td class='d l'>{KC_ORIGIN_NAMES[o]}</td>"]
        row += [scell(grid[(o, p)]) for p in ports]
        row.append(totcell(row_tot[o], sep=True))
        row.append("</tr>")
        body.append("".join(row))
    body.append("<tr><td class='d l tot'>Total</td>" + "".join(totcell(col_tot[p]) for p in ports) +
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

    head = ["<div class='rwrap' style='height:auto'><table class='rpt static'><thead><tr class='h2'>",
            "<th class='dt l'>Origin</th>"]
    head += [f"<th>{KC_PORT_NAMES[p]}</th>" for p in ports] + [
        "<th class='sep'>Total</th><th class='sep'>Origin %</th></tr></thead><tbody>"]
    body = []
    for o in origins:
        row = [f"<tr><td class='d l'>{KC_ORIGIN_NAMES[o]}</td>"]
        row += [cell(grid[(o, p)]) for p in ports]
        row.append(totcell(row_tot[o], sep=True))
        row.append(pctcell(row_tot[o], sep=True))
        row.append("</tr>")
        body.append("".join(row))
    body.append("<tr><td class='d l tot'>Total</td>" + "".join(totcell(col_tot[p]) for p in ports) +
               totcell(grand, sep=True) + "<td class='sep'></td></tr>")
    body.append("<tr><td class='d l tot'>Port %</td>" +
               "".join(pctcell(col_tot[p]) for p in ports) + "<td class='sep'></td><td class='sep'></td></tr>")
    return "".join(head) + "".join(body) + "</tbody></table></div>"


@st.cache_data(ttl=3600, show_spinner=False)
def kc_grading_flow_html(df: pd.DataFrame, height: str = "70vh") -> str:
    """Daily KC grading-queue flow: Passed/Failed lots, % passed, Pending, Certs level, Certs
    change, Fresh Pending (= change in Pending + Passed + Failed) and Implied Decerts
    (= Passed - Certs change). Same formulas as the desk's original Excel/Streamlit prototype."""
    d = df.sort_values("Date").copy()
    pass_cols = [f"KC-{p}-PASSGRAD" for p in KC_GRADE_PORTS]
    fail_cols = [f"KC-{p}-FAILGRAD" for p in KC_GRADE_PORTS]
    d["Passed"] = d[pass_cols].sum(axis=1, min_count=1)
    d["Failed"] = d[fail_cols].sum(axis=1, min_count=1)
    d["PctPassed"] = d["Passed"] / (d["Passed"] + d["Failed"]) * 100
    d["Pending"] = d["KC-TOT-PENDING"].astype(float)
    d["Certs"] = d["KC-TOT-TOT"].astype(float)
    d["CertsChg"] = d["Certs"].diff()
    d["FreshPending"] = d["Pending"].diff() + d["Passed"].fillna(0) + d["Failed"].fillna(0)
    d["ImplDecerts"] = d["Passed"].fillna(0) - d["CertsChg"]
    d = d.dropna(subset=["CertsChg"]).sort_values("Date", ascending=False)

    p_scale = max(d["Passed"].max(), 1)
    f_scale = max(d["Failed"].max(), 1)
    c_scale = max(d["CertsChg"].abs().max(), 1)
    fp_scale = max(d["FreshPending"].abs().max(), 1)
    id_scale = max(d["ImplDecerts"].abs().max(), 1)

    def num(v):
        return "" if pd.isna(v) or v == 0 else f"{v:,.0f}"

    def pct(v):
        return "" if pd.isna(v) else f"{v:.0f}%"

    def heat(v, sc, rgb):
        if pd.isna(v) or v == 0:
            return "<td></td>"
        alpha = min(abs(v) / sc, 1.0) * 0.85
        return f"<td style='background:rgba({rgb},{alpha:.2f})'>{v:,.0f}</td>"

    def signed(v, sc):
        if pd.isna(v):
            return "<td class='na'></td>"
        bar = f"<i class='{'up' if v > 0 else 'dn'}' style='width:{abs(v) / sc * 50:.1f}%'></i>" if v else ""
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f"<td class='cb'>{bar}<span class='{cls}'>{v:+,.0f}</span></td>"

    head = ["<div class='rwrap' style='height:", height, "'><table class='rpt'><thead><tr class='h2'>",
            "<th class='dt'>Date</th><th>Passed</th><th>Failed</th><th>%</th><th class='sep'>Pending</th>",
            "<th>Certs</th><th>Certs Change</th><th>Fresh Pending</th><th>Impl Decerts</th></tr></thead><tbody>"]
    body = []
    for _, r in d.iterrows():
        row = [f"<tr><td class='d'>{r['Date'].strftime('%d-%b-%y')}</td>"]
        row.append(heat(r["Passed"], p_scale, "31,157,111"))
        row.append(heat(r["Failed"], f_scale, "201,74,74"))
        row.append(f"<td>{pct(r['PctPassed'])}</td>")
        row.append(f"<td class='sep'>{num(r['Pending'])}</td>")
        row.append(f"<td class='tot'>{num(r['Certs'])}</td>")
        row.append(signed(r["CertsChg"], c_scale))
        row.append(heat(r["FreshPending"], fp_scale, "31,157,111"))
        row.append(heat(r["ImplDecerts"], id_scale, "201,74,74"))
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


def fmt_int(v):
    return "-" if pd.isna(v) else f"{int(v):,}"


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
    w = w[w["x"] <= 365]
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
    fig.update_layout(xaxis=dict(title="Day of year", dtick=30, range=[1, 365]),
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
    g = pd.read_parquet(DB_DIR / "rc_grading.parquet")
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
    w = w[w["x"] <= 365]
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
                                 ticktext=[MONTH_ABBR[order[i]] for i in range(0, 12, 2)], range=[1, 365]),
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
    g_on_day = lots_tot.reindex(idx, fill_value=0)
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
                             height: str = "60vh", lag: int = 1) -> str:
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
        i = np.searchsorted(cd, d) + lag
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
    for d in days:
        row = [f"<tr><td class='d'>{d.strftime('%d-%b-%y')}</td>"]
        row += [lcell(lots.loc[d, o] if d in lots.index else np.nan) for o in origins]
        row.append(totcell(lots_tot.get(d, 0), l_scale))
        row.append(chgcell(used_chg.get(d, np.nan)))
        row.append(usecell(used_use.get(d, np.nan)))
        row.append("</tr>")
        body.append("".join(row))
    return "".join(head) + "".join(body) + "</tbody></table></div>"


with st.sidebar:
    st.markdown("<div class='sb-title'>Daily Miner</div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-label'>Commodity</div>", unsafe_allow_html=True)
    commodity = st.radio("Commodity", COMMODITIES, label_visibility="collapsed")

if commodity == "Coffee":
    # Lazy radio again (see the note on rc_section_box below): Arabica now carries real work of
    # its own (the KC matrices and grading-flow table), so a real st.tabs here would rebuild all
    # of that every time something changes on the Robusta side, and vice versa.
    with st.container(key="coffee_section_box"):
        coffee_section = st.radio("Coffee section", ["Arabica", "Robusta"], horizontal=True,
                                  label_visibility="collapsed", key="coffee_section")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if coffee_section == "Arabica":
        kc = load_kc_certs()
        with st.container(key="rc_section_box"):
            ar_view = st.radio("Arabica view", ["Matrix", "Visuals", "Seasonals & Distribution"], horizontal=True,
                               label_visibility="collapsed", key="ar_view")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if ar_view == "Matrix":
            k_min, k_max = kc["Date"].min(), kc["Date"].max()
            k_prev = kc["Date"].iloc[-2] if len(kc) > 1 else k_max  # previous trading day, not just latest-1
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
            st.markdown("<div class='mt'>Certified Stocks Change (bags)</div>", unsafe_allow_html=True)
            st.markdown(kc_change_matrix_html(kc, older_ts, latest_ts), unsafe_allow_html=True)
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='mt'>Latest Certified Stocks ({latest_ts.strftime('%d %b %Y')}, bags)</div>",
                       unsafe_allow_html=True)
            st.markdown(kc_latest_matrix_html(kc, latest_ts), unsafe_allow_html=True)
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.markdown("<div class='mt'>KC Grading Flow (bags)</div>", unsafe_allow_html=True)
            st.markdown(kc_grading_flow_html(kc), unsafe_allow_html=True)
        else:
            st.markdown("<div class='card-desc'>Coming next.</div>", unsafe_allow_html=True)

    else:
        # A plain st.radio (not st.tabs) is used for these two levels of navigation: st.tabs
        # renders every tab's body on every rerun regardless of which one is showing, whereas a
        # radio only ever runs the branch that's picked. That is what made switching between
        # Certs/Grading views, or the sub-views inside them, feel slow - every click anywhere on
        # the page was silently rebuilding every table and chart in every tab, every time.
        with st.container(key="rc_section_box"):
            rc_section = st.radio("Section", ["Certs", "Grading", "Certs & Grading"], horizontal=True,
                                  label_visibility="collapsed", key="rc_section")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if rc_section == "Certs":
            certs = load_rc_certs()
            end = certs["Date"].max()
            start = end - pd.DateOffset(years=HISTORY_YEARS)
            with st.container(key="rc_view_box"):
                rc_view = st.radio("View", ["Data Table", "Visuals", "Seasonality & Distribution"], horizontal=True,
                                   label_visibility="collapsed", key="rc_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rc_view == "Data Table":
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
                rg_view = st.radio("View", ["Data Table", "Visuals", "Cumulative & Seasonals"], horizontal=True,
                                   label_visibility="collapsed", key="rg_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rg_view == "Data Table":
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
                rcg_view = st.radio("View", ["Data Table", "Visuals"], horizontal=True,
                                    label_visibility="collapsed", key="rcg_view")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if rcg_view == "Data Table":
                st.markdown(monthly_grading_certs_html(gr, certs), unsafe_allow_html=True)
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                _lag_l, _ = st.columns([1, 5])
                with _lag_l:
                    st.markdown("<div class='sb-label' style='margin:0 0 2px'>LRC Certs lag</div>",
                               unsafe_allow_html=True)
                    with st.container(key="rcg_lag_box"):
                        lag_pick = st.radio("Certs lag", ["0d", "1d"], index=1, horizontal=True,
                                            label_visibility="collapsed", key="rcg_lag")
                st.markdown(daily_grading_certs_html(gr, certs, lag=int(lag_pick[0])), unsafe_allow_html=True)
            else:
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
    st.markdown(f"<div class='card-desc'>{commodity}: not built yet.</div>", unsafe_allow_html=True)
