import warnings
from pathlib import Path

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

/* Certs report table */
.rwrap { height: 60vh; overflow: auto; border: 1px solid #dfe3ee; border-radius: 12px; background: #ffffff; width: fit-content; max-width: 100%; }
.rpt { width: max-content; border-collapse: separate; border-spacing: 0; font-size: 11px; line-height: 1.25; font-variant-numeric: tabular-nums; }
.rpt thead th { position: sticky; z-index: 2; background: #0a2463; color: #ffffff; font-weight: 600; padding: 4px 9px; font-size: 10.5px; text-align: center; white-space: nowrap; }
.rpt thead tr.h1 th { top: 0; height: 24px; background: #14357f; letter-spacing: .05em; font-size: 11px; }
.rpt thead tr.h2 th { top: 24px; height: 22px; background: #0f2c70; }
.rpt thead tr.h3 th { top: 46px; height: 22px; }
.rpt thead th.gs { border-left: 1px solid rgba(255,255,255,.28); }
.rpt td.gs { border-left: 1px solid #dfe3ee; }
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


COUNTRY_PORTS = {
    "Belgium": ["ANT"],
    "UK": ["LON", "FEL", "LIV"],
    "Netherlands": ["AMS", "ROT"],
    "Germany": ["HAM", "BRE"],
    "Spain": ["BAR"],
    "Italy": ["GEN", "TRI"],
    "Other": ["NOR"],
}


def countries_by_stock(df: pd.DataFrame, grade: str = "VG") -> list:
    """[(country, [ports])] with the biggest country first today, and the
    biggest port first inside each country."""
    last = df.iloc[-1]

    def stock(p):
        v = last[f"LRC-{p}-{grade}"]
        return 0 if pd.isna(v) else v

    out = [(c, sorted(ports, key=lambda p: -stock(p))) for c, ports in COUNTRY_PORTS.items()]
    return sorted(out, key=lambda cp: -sum(stock(p) for p in cp[1]))


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
    "HAM": "#1f9d6f", "BAR": "#c0722c", "BRE": "#4a5578", "GEN": "#8fa3d1", "LIV": "#b58f4a", "NOR": GREY,
}


def chart_layout(fig, title, height=380):
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


def total_certs_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    s = df[["Date", f"LRC-TOT-{grade}"]].dropna()
    fig = go.Figure(go.Scatter(
        x=s["Date"], y=s[f"LRC-TOT-{grade}"], mode="lines", name="Total certs",
        line=dict(color=NAVY, width=2), fill="tozeroy", fillcolor="rgba(10,36,99,0.07)",
        hovertemplate="%{y:,.0f}<extra></extra>"))
    return chart_layout(fig, "Total Certs")


def ports_certs_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    fig = go.Figure()
    for p in PORT_ORDER:
        c = f"LRC-{p}-{grade}"
        s = df[["Date", c]].dropna()
        if s[c].abs().sum() == 0:
            continue
        fig.add_trace(go.Scatter(
            x=s["Date"], y=s[c], mode="lines", name=p,
            line=dict(color=PORT_COLORS.get(p, GREY), width=1.8),
            hovertemplate="%{y:,.0f}<extra>" + p + "</extra>"))
    return chart_layout(fig, "Certs Per Port")


def seasonality_fig(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    """Week-of-year seasonality: history bands (min-max, 10-90, 25-75 pct), average,
    last year in red and the current year in navy (same styling as Cotton On-Call)."""
    s = df.set_index("Date")[col].dropna().astype(float)
    w = s.resample("W").last().ffill().to_frame("v")
    iso = w.index.isocalendar()
    w["x"], w["yr"] = iso.week.astype(int).values, iso.year.astype(int).values
    w = w[w["x"] <= 52]
    cur = int(w["yr"].max())
    hist = w[w["yr"] < cur]
    band = hist.groupby("x")["v"].agg(
        lo="min", p10=lambda v: v.quantile(0.10), p25=lambda v: v.quantile(0.25),
        avg="mean", p75=lambda v: v.quantile(0.75), p90=lambda v: v.quantile(0.90), hi="max").sort_index()

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
    chart_layout(fig, title, height=440)
    fig.update_layout(xaxis=dict(title="Week of year", dtick=4, range=[1, 52]))
    return fig


def seasonality_options(df: pd.DataFrame, grade: str = "VG") -> dict:
    """Label -> column. Total first, then ports with the most stock today first."""
    last = df.iloc[-1]
    ports = [p for p in PORT_ORDER if df[f"LRC-{p}-{grade}"].fillna(0).abs().sum() > 0]
    ports.sort(key=lambda p: -(0 if pd.isna(last[f"LRC-{p}-{grade}"]) else last[f"LRC-{p}-{grade}"]))
    return {"Total": f"LRC-TOT-{grade}", **{p: f"LRC-{p}-{grade}" for p in ports}}


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
            tab_data, tab_visuals = st.tabs(["Data Table", "Visuals"])
            with tab_data:
                st.markdown(certs_report_html(certs, start, end), unsafe_allow_html=True)
            with tab_visuals:
                c_min, c_max = certs["Date"].min(), certs["Date"].max()
                span = st.radio("History", ["1Y", "3Y", "5Y", "All", "Custom"], horizontal=True,
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
                ch1, ch2 = st.columns(2)
                with ch1:
                    st.plotly_chart(total_certs_fig(cview), width="stretch", config={"displayModeBar": False})
                with ch2:
                    st.plotly_chart(ports_certs_fig(cview), width="stretch", config={"displayModeBar": False})
                opts = seasonality_options(certs)
                view_pick = st.selectbox("Seasonality", list(opts), key="rc_season_view")
                st.plotly_chart(seasonality_fig(certs, opts[view_pick], f"Seasonality: {view_pick}"),
                                width="stretch", config={"displayModeBar": False})
