"""KC (Arabica) grading database from ICE "Coffee C Certified Warehouse Stock Report" files.

Two sources, one output:
  1. History  : the three manual workbooks in Database/Archive/KC/*.xlsx (Sheet1), cleaned + de-duplicated.
     Any history date that fails reconciliation is quarantined (removed + logged) until a daily file replaces it.
  2. Daily    : one ICE xls per day dropped into Database/Manual Inputs/KC/ (any file name).

Output (tidy long):  Database/Main/KC/kc_grading.parquet   Date, Tag, Origin, Port, Bags
  Tag = Certs | Transition | Passed | Failed | Pending | Rebagging
  Rows = exactly what ICE reported (an origin absent from a day's block means 0 that day).
Coverage : Database/Main/KC/kc_grading_days.parquet  (which dates we hold, and from which source)
Log      : Database/Logs/KC/kc_grading_log.csv       (every rejection / conflict / reconciliation break)

Usage:
  python kc_grading_ingest.py                 # ingest new/changed files from Daily/
  python kc_grading_ingest.py --rebuild       # rebuild history from the workbooks, then ingest Daily/
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "Database"
HIST_DIR = DB / "Archive" / "KC"
DAILY_DIR = DB / "Manual Inputs" / "KC"
OUT = DB / "Main" / "KC" / "kc_grading.parquet"
DAYS = DB / "Main" / "KC" / "kc_grading_days.parquet"
LOG = DB / "Logs" / "KC" / "kc_grading_log.csv"
MISSING = DB / "Logs" / "KC" / "kc_grading_missing_days.csv"
CERTS = DB / "Main" / "KC" / "kc_certs.parquet"

PORT_ALIASES = {
    "ANT": "Antwerp", "ANTWERP": "Antwerp",
    "BAR": "Barcelona", "BARCELONA": "Barcelona",
    "HA/BR": "Ham/Bre", "HAM/BRE": "Ham/Bre", "HAMBURG / BREMEN": "Ham/Bre", "HAMBURG/BREMEN": "Ham/Bre",
    "HOU": "Houston", "HOUSTON": "Houston",
    "MIAMI": "Miami",
    "NOLA": "New Orleans", "NEW ORLEANS": "New Orleans",
    "NY": "New York", "NEW YORK": "New York",
    "VA": "Virginia", "VIRGINIA": "Virginia",
}
ORIGIN_ALIASES = {"PNG": "Papua New Guinea"}

SECTIONS = [
    (r"(total )?bags certified", "Certs"),
    (r"transition bags certified", "Transition"),
    (r"bags passed grading", "Passed"),
    (r"bags failed grading", "Failed"),
    (r"pending grading report", "Pending"),
    (r"flagged for rebagging", "Rebagging"),
]
TOTAL_LABEL = "total in bags"

_log = []


def log(date, source, kind, detail):
    _log.append({"Logged": datetime.now().strftime("%Y-%m-%d %H:%M"), "Date": date, "Source": source,
                 "Kind": kind, "Detail": detail})


def norm_port(x):
    return PORT_ALIASES.get(re.sub(r"\s+", " ", str(x).strip()).upper())


def norm_origin(x):
    s = re.sub(r"\s+", " ", str(x).strip())
    return ORIGIN_ALIASES.get(s.upper(), s)


def to_num(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def section_of(text):
    t = re.sub(r"\s+", " ", str(text).strip().lower()).rstrip(":")
    for pat, tag in SECTIONS:
        if re.fullmatch(pat, t):
            return tag
    return None


def parse_daily_file(path):
    """Return (date, tidy DataFrame, list of problems). Raises ValueError if the file is unusable."""
    raw = pd.read_excel(path, sheet_name=0, header=None, dtype=object)
    col0 = [("" if pd.isna(v) else str(v)) for v in raw[0].tolist()]

    date = None
    for s in col0[:15]:
        m = re.search(r"as of:?\s*([A-Za-z]{3,9}\.? \d{1,2},? \d{4})", s, re.I)
        if m:
            date = pd.to_datetime(m.group(1).replace(",", ""), format="%b %d %Y", errors="coerce")
            if pd.isna(date):
                date = pd.to_datetime(m.group(1), errors="coerce")
            break
    if date is None or pd.isna(date):
        raise ValueError("no 'As of:' date found")
    date = date.normalize()

    titles = [(i, section_of(s)) for i, s in enumerate(col0) if section_of(s)]
    if not any(t == "Certs" for _, t in titles):
        raise ValueError("no 'TOTAL BAGS CERTIFIED' / 'BAGS CERTIFIED' section found")

    problems, rows = [], []
    next_title = {i: (titles[k + 1][0] if k + 1 < len(titles) else len(col0)) for k, (i, _) in enumerate(titles)}

    for i, tag in titles:
        end = next_title[i]
        hdr = None
        for j in range(i + 1, min(end, i + 8)):
            ports = {c: norm_port(raw.iat[j, c]) for c in range(1, raw.shape[1]) if not pd.isna(raw.iat[j, c])}
            if sum(1 for p in ports.values() if p) >= 1 and all(p or str(raw.iat[j, c]).strip().lower() == "total"
                                                                 for c, p in ((c, ports[c]) for c in ports)):
                hdr = (j, {c: p for c, p in ports.items() if p},
                       next((c for c in ports if not ports[c]), None))
                break
        if hdr is None:
            empty = any(col0[j].strip().lower().startswith("no ") for j in range(i + 1, min(end, i + 8)))
            if tag in ("Certs", "Pending") and not empty:
                problems.append(f"{tag}: header not found")
            continue                                   # e.g. "No Bags Passed Today" -> genuinely empty
        hj, pmap, tcol = hdr

        origin_rows, total_row = [], None
        for j in range(hj + 1, end):
            name = col0[j].strip()
            if not name:
                continue
            vals = {c: to_num(raw.iat[j, c]) for c in list(pmap) + ([tcol] if tcol else [])}
            if name.lower() == TOTAL_LABEL:
                total_row = vals
                break
            origin_rows.append((norm_origin(name), vals))

        sums = {c: 0.0 for c in pmap}
        for origin, vals in origin_rows:
            rsum = 0.0
            for c, port in pmap.items():
                v = vals[c]
                if v is None:
                    problems.append(f"{tag}: non-numeric cell {origin}/{port}")
                    v = 0.0
                rows.append((date, tag, origin, port, v))
                sums[c] += v
                rsum += v
            if tcol and vals.get(tcol) is not None and abs(rsum - vals[tcol]) > 0.5:
                problems.append(f"{tag}: {origin} row sum {rsum:.0f} != row total {vals[tcol]:.0f}")
        if total_row:
            for c, port in pmap.items():
                if total_row[c] is not None and abs(sums[c] - total_row[c]) > 0.5:
                    problems.append(f"{tag}: {port} origins sum {sums[c]:.0f} != 'Total in Bags' {total_row[c]:.0f}")
        elif origin_rows:
            problems.append(f"{tag}: no 'Total in Bags' row")

    df = pd.DataFrame(rows, columns=["Date", "Tag", "Origin", "Port", "Bags"])
    df["Bags"] = df["Bags"].astype("int64")
    return date, df, problems


def ingest_daily():
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    days = pd.read_parquet(DAYS) if DAYS.exists() else pd.DataFrame(columns=["Date", "Source", "File", "Mtime"])
    seen = set(zip(days["File"], days["Mtime"].astype(float))) if len(days) else set()

    files = sorted([p for p in DAILY_DIR.iterdir() if p.suffix.lower() in (".xls", ".xlsx") and not p.name.startswith("~$")],
                   key=lambda p: p.stat().st_mtime)
    new = [p for p in files if (p.name, float(p.stat().st_mtime)) not in seen]
    print(f"Daily files: {len(files)} total, {len(new)} new/changed")
    if not new:
        return

    db = pd.read_parquet(OUT) if OUT.exists() else pd.DataFrame(columns=["Date", "Tag", "Origin", "Port", "Bags"])
    ok = 0
    for p in new:
        try:
            date, df, problems = parse_daily_file(p)
        except Exception as e:
            log("", p.name, "REJECTED", str(e))
            print(f"  REJECTED {p.name}: {e}")
            continue
        m = re.search(r"(20\d{2})(\d{2})(\d{2})", p.name)
        if m and pd.Timestamp(f"{m.group(1)}-{m.group(2)}-{m.group(3)}") != date:
            log(date.date(), p.name, "DATE_MISMATCH", f"file name says {m.group(0)}, report says {date.date()} (report date used)")
            print(f"  WARNING {p.name}: name date != report date {date.date()}")
        for pr in problems:
            log(date.date(), p.name, "RECONCILE", pr)
        if problems:
            print(f"  {p.name} ({date.date()}): {len(problems)} reconciliation issue(s), see log")
        db = pd.concat([db[db["Date"] != date], df], ignore_index=True)
        days = days[days["Date"] != date]
        days = pd.concat([days, pd.DataFrame([{"Date": date, "Source": "daily", "File": p.name,
                                               "Mtime": float(p.stat().st_mtime)}])], ignore_index=True)
        ok += 1
    save(db, days)
    print(f"Ingested {ok}/{len(new)} files.")


def save(db, days):
    db = db.sort_values(["Date", "Tag", "Origin", "Port"]).reset_index(drop=True)
    days = days.sort_values("Date").reset_index(drop=True)
    db.to_parquet(OUT, index=False)
    days.to_parquet(DAYS, index=False)
    if _log:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        new = pd.DataFrame(_log)
        old = pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(columns=new.columns)
        pd.concat([old, new], ignore_index=True).to_csv(LOG, index=False)
        _log.clear()
    write_missing_days(days)
    print(f"Saved {len(db):,} rows, {db['Date'].nunique()} dates ({db['Date'].min().date()} -> {db['Date'].max().date()})")


def write_missing_days(days):
    """Certs report days (LSEG calendar) that have no grading file yet: download these from ICE and drop them in Manual Inputs/KC."""
    if not CERTS.exists():
        return
    c = pd.read_parquet(CERTS, columns=["Date", "KC-TOT-TOT"])
    cal = pd.to_datetime(c.dropna(subset=["KC-TOT-TOT"])["Date"])
    cal = cal[cal >= days["Date"].min()]
    miss = sorted(set(cal) - set(pd.to_datetime(days["Date"])))
    MISSING.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"Date": [d.date() for d in miss],
                  "File to download": [f"coffee_cert_stock_{d:%Y%m%d}.xls" for d in miss]}).to_csv(MISSING, index=False)
    print(f"{len(miss)} certs days have no grading file yet -> {MISSING.name}")


# ---------------------------------------------------------------- history
def load_history_workbooks():
    frames = []
    for f in sorted(HIST_DIR.glob("Arabica BI*.xlsx")):
        d = pd.read_excel(f, sheet_name="Sheet1")
        d = d.rename(columns={"Type": "Tag"})
        d = d[["Date", "Origin", "Port", "Tag", "Bags"]].copy()
        d["Date"] = pd.to_datetime(d["Date"]).dt.normalize()
        d["Bags"] = pd.to_numeric(d["Bags"], errors="coerce")
        d["File"] = f.name
        d["Port"] = d["Port"].map(lambda x: "Total" if str(x).strip().lower() == "total" else norm_port(x) or str(x))
        d["Origin"] = d["Origin"].map(norm_origin)
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def clean_history(h):
    n0 = len(h)
    blank = h["Bags"].isna()
    log("", "history", "DROP_BLANK", f"{int(blank.sum())} rows with blank Bags (stale/pasted headers), blank != 0")
    h = h[~blank]

    is_tot_origin = h["Origin"].str.lower().eq(TOTAL_LABEL)
    tot = h[is_tot_origin & h["Port"].ne("Total")]                 # 'Total in Bags' rows kept only as reconciliation targets
    h = h[~is_tot_origin & h["Port"].ne("Total")]

    key = ["Date", "Tag", "Origin", "Port"]
    # identical repeats (same value, incl. the same value appearing in two workbooks) -> keep one
    h = h.drop_duplicates(key + ["Bags"])
    conf = h[h.duplicated(key, keep=False)]
    tot = tot.drop_duplicates(["Date", "Tag", "Port", "Bags"])

    drop_idx = []
    for k, g in conf.groupby(key):
        date, tag, origin, port = k
        # a 'Total in Bags' row for that date/tag/port arbitrates: pick the candidate whose port total reconciles
        others = h[(h.Date == date) & (h.Tag == tag) & (h.Port == port) & (h.Origin != origin)]["Bags"].sum()
        tcands = tot[(tot.Date == date) & (tot.Tag == tag) & (tot.Port == port)]["Bags"].tolist()
        pick = None
        for c in g["Bags"]:
            if any(abs(others + c - t) < 0.5 for t in tcands):
                pick = c
        if pick is not None and (g["Bags"] == pick).sum() >= 1:
            drop_idx += g.index[g["Bags"] != pick].tolist()
            log(date.date(), "history", "CONFLICT_RESOLVED", f"{tag}/{origin}/{port}: {sorted(g['Bags'].unique())} -> {pick:.0f} (matches Total in Bags)")
        else:
            drop_idx += g.index.tolist()
            log(date.date(), "history", "CONFLICT_DROPPED", f"{tag}/{origin}/{port}: {sorted(g['Bags'].unique())} unresolved, key removed")
    h = h.drop(index=drop_idx)
    h = h.drop_duplicates(key)
    wk = h["Date"].dt.dayofweek >= 5
    for d in sorted(h.loc[wk, "Date"].unique()):
        log(pd.Timestamp(d).date(), "history", "DROP_WEEKEND", "ICE does not report at weekends, row(s) removed")
    h = h[~wk]
    print(f"History: {n0:,} raw rows -> {len(h):,} clean rows")
    return h[key + ["Bags"]].assign(Bags=lambda x: x["Bags"].astype("int64")), tot


def reconcile_history(h, tot):
    s = h.groupby(["Date", "Tag", "Port"])["Bags"].sum()
    t = tot.groupby(["Date", "Tag", "Port"])["Bags"].max()
    j = pd.concat([s.rename("sum"), t.rename("tot")], axis=1).dropna()
    bad = j[(j["sum"] - j["tot"]).abs() > 0.5]
    for (d, tag, port), r in bad.iterrows():
        log(d.date(), "history", "RECONCILE", f"{tag}/{port}: origins sum {r['sum']:.0f} != Total in Bags {r['tot']:.0f}")
    print(f"History reconciliation: {len(j):,} date/tag/port totals checked, {len(bad)} mismatched (see log)")
    return set(bad.index.get_level_values(0))


def rebuild_history():
    h = load_history_workbooks()
    h, tot = clean_history(h)
    bad_dates = reconcile_history(h, tot)
    for d in sorted(bad_dates):
        log(d.date(), "history", "QUARANTINED", "date failed reconciliation, removed until a daily ICE file is supplied")
    h = h[~h["Date"].isin(bad_dates)]
    days = pd.DataFrame({"Date": sorted(h["Date"].unique())})
    days["Source"], days["File"], days["Mtime"] = "history", "Arabica BI*.xlsx", 0.0
    save(h, days)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="rebuild history from the manual workbooks first")
    a = ap.parse_args()
    if a.rebuild or not OUT.exists():
        if LOG.exists():
            LOG.unlink()
        rebuild_history()
    ingest_daily()
