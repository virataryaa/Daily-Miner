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


def major_ports(view: pd.DataFrame, grade: str = "VG", min_share: float = 0.01) -> list:
    """Ports whose average share of the total in `view` is at least min_share,
    biggest first. Near-zero ports are left out of the charts."""
    tot = view[f"LRC-TOT-{grade}"].astype(float).mean()
    if not tot:
        return []
    share = {p: view[f"LRC-{p}-{grade}"].astype(float).mean() / tot for p in PORT_ORDER}
    return [p for p in sorted(share, key=lambda p: -(0 if pd.isna(share[p]) else share[p]))
            if pd.notna(share[p]) and share[p] >= min_share]


def ports_certs_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """Line per major port; the bigger the port's share, the bolder the line."""
    majors = major_ports(df, grade)
    tot = df[f"LRC-TOT-{grade}"].astype(float).mean()
    means = {p: df[f"LRC-{p}-{grade}"].astype(float).mean() / tot for p in majors}
    top = max(means.values()) if means else 1
    fig = go.Figure()
    for rank, p in enumerate(majors):
        s = df[["Date", f"LRC-{p}-{grade}"]].dropna()
        w = 1.2 + 3.4 * (means[p] / top)
        fig.add_trace(go.Scatter(
            x=s["Date"], y=s[f"LRC-{p}-{grade}"], mode="lines", name=p, legendrank=rank,
            line=dict(color=PORT_COLORS.get(p, GREY), width=w),
            opacity=0.55 + 0.45 * (means[p] / top),
            hovertemplate="%{y:,.0f}<extra>" + p + "</extra>"))
    fig.data = fig.data[::-1]  # draw the biggest port last, on top
    return chart_layout(fig, "Certs Per Port")


def rolling_fig(series: pd.Series, start: pd.Timestamp, end: pd.Timestamp, title: str) -> go.Figure:
    """Rolling 5- and 20-observation change of a stock series (computed on the
    full history, then cut to the chosen window)."""
    ser = series.dropna().astype(float)
    fig = go.Figure()
    for n, color, width in [(20, NAVY, 2.6), (5, TEAL, 1.6)]:
        r = ser.diff(n).dropna()
        r = r[(r.index >= start) & (r.index <= end)]
        fig.add_trace(go.Scatter(x=r.index, y=r.values, mode="lines", name=f"{n}d",
                                 line=dict(color=color, width=width),
                                 hovertemplate="%{y:+,.0f}<extra>" + f"{n}d" + "</extra>"))
    fig.add_hline(y=0, line=dict(color="#c5cbdd", width=1))
    chart_layout(fig, title, height=340)
    fig.update_layout(yaxis=dict(tickformat="+,"))
    return fig


def share_area_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """100% stacked area of each port's share; minor ports pooled into Other."""
    majors = major_ports(df, grade)
    minors = [p for p in PORT_ORDER if p not in majors]
    fig = go.Figure()
    for p in reversed(majors):
        s = df[["Date", f"LRC-{p}-{grade}"]].dropna()
        fig.add_trace(go.Scatter(x=s["Date"], y=s[f"LRC-{p}-{grade}"], mode="lines", name=p, stackgroup="one",
                                 groupnorm="percent", line=dict(width=0.6, color=PORT_COLORS.get(p, GREY)),
                                 fillcolor=PORT_COLORS.get(p, GREY), hovertemplate="%{y:.1f}%<extra>" + p + "</extra>"))
    if minors:
        other = df[[f"LRC-{p}-{grade}" for p in minors]].astype(float).sum(axis=1, min_count=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=other, mode="lines", name="Other", stackgroup="one",
                                 groupnorm="percent", line=dict(width=0.6, color="#c5cbdd"), fillcolor="#c5cbdd",
                                 hovertemplate="%{y:.1f}%<extra>Other</extra>"))
    chart_layout(fig, "Port Share of Total", height=340)
    fig.update_layout(yaxis=dict(ticksuffix="%", range=[0, 100]))
    return fig


def share_pie_fig(df: pd.DataFrame, grade: str = "VG") -> go.Figure:
    """Donut of the latest breakup; ports under 1% pooled into Other."""
    last = df.iloc[-1]
    tot = float(last[f"LRC-TOT-{grade}"])
    vals = {p: float(last[f"LRC-{p}-{grade}"]) for p in PORT_ORDER
            if pd.notna(last[f"LRC-{p}-{grade}"]) and last[f"LRC-{p}-{grade}"] > 0}
    big = {p: v for p, v in vals.items() if v / tot >= 0.01}
    rest = sum(v for p, v in vals.items() if p not in big)
    labels = sorted(big, key=lambda p: -big[p])
    amounts = [big[p] for p in labels]
    colors = [PORT_COLORS.get(p, GREY) for p in labels]
    if rest > 0:
        labels.append("Other")
        amounts.append(rest)
        colors.append("#c5cbdd")
    fig = go.Figure(go.Pie(
        labels=labels, values=amounts, hole=0.66, sort=False, direction="clockwise",
        marker=dict(colors=colors, line=dict(color="#fafafa", width=3)),
        textinfo="label+percent", textposition="outside", textfont=dict(size=12, color="#1a1a2e"),
        hovertemplate="%{label}: %{value:,.0f} (%{percent})<extra></extra>", showlegend=False))
    chart_layout(fig, f"Latest Breakup ({last['Date'].strftime('%d %b %Y')})", height=340)
    fig.update_layout(
        margin=dict(t=44, b=20, l=40, r=40),
        annotations=[dict(text=f"<b>{tot:,.0f}</b><br><span style='font-size:11px;color:#7a86a8'>total</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=22, color=NAVY))])
    return fig


def seasonality_fig(df: pd.DataFrame, col: str, title: str) -> go.Figure:
    """Day-of-year seasonality: history bands (min-max, 10-90, 25-75 pct), average,
    last year in red and the current year in navy (same styling as Cotton On-Call)."""
    s = df.set_index("Date")[col].dropna().astype(float)
    w = s.resample("D").last().ffill().to_frame("v")
    w["x"], w["yr"] = w.index.dayofyear, w.index.year
    w = w[w["x"] <= 365]
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
    fig.update_layout(xaxis=dict(title="Day of year", dtick=30, range=[1, 365]),
                      legend=dict(y=-0.28))
    return fig


def seasonality_options(df: pd.DataFrame, grade: str = "VG") -> dict:
    """Label -> column. Total first, then ports with the most stock today first."""
    last = df.iloc[-1]
    ports = [p for p in PORT_ORDER if df[f"LRC-{p}-{grade}"].fillna(0).abs().sum() > 0]
    ports.sort(key=lambda p: -(0 if pd.isna(last[f"LRC-{p}-{grade}"]) else last[f"LRC-{p}-{grade}"]))
    return {"Total": f"LRC-TOT-{grade}", **{p: f"LRC-{p}-{grade}" for p in ports}}


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


def distribution_fig(values: pd.Series, title: str, label: str) -> go.Figure:
    """Histogram (density) with a fitted normal curve and the latest value marked."""
    vals = values.dropna().astype(float)
    latest = float(vals.iloc[-1])
    mu, sd = float(vals.mean()), float(vals.std(ddof=0)) or 1.0
    xs = np.linspace(vals.min(), vals.max(), 240)
    pdf = np.exp(-0.5 * ((xs - mu) / sd) ** 2) / (sd * np.sqrt(2 * np.pi))
    z = (latest - mu) / sd
    pct = float((vals <= latest).mean() * 100)

    fig = go.Figure()
    span = float(vals.max() - vals.min()) or 1.0
    bin_size = max(1.0, span / 260)  # counts are integers, so 1 bag is the finest useful bin
    fig.add_trace(go.Histogram(x=vals, histnorm="probability density", name="Observed",
                               xbins=dict(start=float(vals.min()) - 0.5, end=float(vals.max()) + 0.5, size=bin_size),
                               marker=dict(color=NAVY, opacity=0.78, line=dict(color="#ffffff", width=0.5)),
                               hovertemplate="%{x:,.0f}<extra>Observed</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=pdf, mode="lines", name="Normal fit",
                             line=dict(color=TEAL, width=2.4), hoverinfo="skip"))
    fig.add_vline(x=latest, line=dict(color=AMBER, width=2, dash="dash"))
    chart_layout(fig, title, height=400)
    fig.update_layout(
        showlegend=False, hovermode="closest", margin=dict(t=40, b=8, l=8, r=8),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        xaxis=dict(tickformat=",", gridcolor="rgba(10,36,99,0.06)", showline=True, linecolor="#dfe3ee"),
        annotations=[dict(xref="paper", yref="paper", x=1, y=1.02, xanchor="right", yanchor="bottom", showarrow=False,
                          text=f"Latest {latest:+,.0f}  |  z {z:+.1f}  |  pctile {pct:.0f}" if label == "chg"
                          else f"Latest {latest:,.0f}  |  z {z:+.1f}  |  pctile {pct:.0f}",
                          font=dict(size=11, color="#5a6688"))],
    )
    return fig


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
            tab_data, tab_visuals, tab_season = st.tabs(["Data Table", "Visuals", "Seasonality & Distribution"])
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
                cfg = {"displayModeBar": False}
                with ch1:
                    st.plotly_chart(total_certs_fig(cview), width="stretch", config=cfg)
                with ch2:
                    st.plotly_chart(ports_certs_fig(cview), width="stretch", config=cfg)
                r1, r2 = st.columns(2)
                port_opts = [k for k in seasonality_options(certs) if k != "Total"]
                with r1:
                    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
                    st.plotly_chart(rolling_fig(certs.set_index("Date")["LRC-TOT-VG"], c_start, c_end,
                                                "Rolling Change: Total (20d / 5d)"), width="stretch", config=cfg)
                with r2:
                    roll_port = st.selectbox("Rolling port", port_opts, key="rc_roll_port", label_visibility="collapsed")
                    st.plotly_chart(rolling_fig(certs.set_index("Date")[f"LRC-{roll_port}-VG"], c_start, c_end,
                                                f"Rolling Change: {roll_port} (20d / 5d)"), width="stretch", config=cfg)
                sh1, sh2 = st.columns(2)
                with sh1:
                    st.plotly_chart(share_area_fig(cview), width="stretch", config=cfg)
                with sh2:
                    st.plotly_chart(share_pie_fig(certs), width="stretch", config=cfg)
            with tab_season:
                opts = seasonality_options(certs)
                s_left, s_right = st.columns([2, 3])
                with s_left:
                    view_pick = st.selectbox("Seasonality", list(opts), key="rc_season_view")
                    st.plotly_chart(seasonality_fig(certs, opts[view_pick], f"Seasonality: {view_pick}"),
                                    width="stretch", config={"displayModeBar": False})
                with s_right:
                    st.markdown(f"<div class='mt side'>Monthly Change: {view_pick}</div>", unsafe_allow_html=True)
                    st.markdown(monthly_change_html(certs, opts[view_pick]), unsafe_allow_html=True)
                lvl = certs.set_index("Date")[opts[view_pick]].dropna()
                lvl = lvl[lvl.index >= DIST_START]
                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
                _l, d1, _r = st.columns([1, 2, 1])
                with d1:
                    st.plotly_chart(distribution_fig(lvl.diff().dropna(), f"Daily Change Distribution: {view_pick}", "chg"),
                                    width="stretch", config={"displayModeBar": False})
