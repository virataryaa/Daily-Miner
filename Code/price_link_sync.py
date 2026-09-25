"""Arabica Price Link data (KC): c1/c2 spread, Rollex active-vs-next spread, month-end cert stocks history.

Outputs in Database/Main/KC/:
  price_link_kc.parquet     Date | c1 | c2 | spread_c12 (c1-c2) | rollex_px | active | spread_rollex (active - next contract)
  kc_certs_eom_hist.parquet Month-end | Bags   (ICE historical end-of-month certified stocks, Nov-1996 onward)

Sources
  c1/c2            LSEG KCc1 / KCc2 SETTLE, daily since 1979 (incremental: last 45 days re-pulled). Needs LSEG Workspace open.
  Rollex           LSEG/Rollex/Database/rollex_KC.parquet (updated daily by its own automator) gives the active contract
  contract prices  LSEG/Arb/Database/kc_futures.parquet (per-contract settlements), so active - next is exact
  EOM certs        Database/Archive/KC/EOM_KC_cert_stox_by_port_nov96-present.xls (ICE)

Run:  python price_link_sync.py            # daily: refresh c1/c2 tail + re-copy Rollex spread
      python price_link_sync.py --full     # re-pull c1/c2 from 1979
      python price_link_sync.py --no-lseg  # skip the LSEG pull, only rebuild from the local files
"""
import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "Database" / "Main" / "KC"
PL = OUT_DIR / "price_link_kc.parquet"
EOM = OUT_DIR / "kc_certs_eom_hist.parquet"
RC_PL = ROOT / "Database" / "Main" / "RC" / "price_link_rc.parquet"   # Robusta: LRCc1 / LRCc2 (USD/MT), 2008 onward
EOM_XLS = ROOT / "Database" / "Archive" / "KC" / "EOM_KC_cert_stox_by_port_nov96-present.xls"
LSEG_DIR = Path(r"C:\Users\virat.arya\ETG\SoftsDatabase - Documents\Database\Hardmine\LSEG")
ROLLEX = LSEG_DIR / "Rollex" / "Database" / "rollex_KC.parquet"
FUT = LSEG_DIR / "Arb" / "Database" / "kc_futures.parquet"
START = "1979-11-26"
OVERLAP_DAYS = 45
CYCLE = ["H", "K", "N", "U", "Z"]                   # KC contract months
MONTH_TO_LETTER = {"Mar": "H", "May": "K", "Jul": "N", "Sep": "U", "Dec": "Z"}


def pull_c1c2(full: bool, root: str = "KC", path: Path = PL, first: str = START) -> pd.DataFrame:
    import lseg.data as ld
    old = pd.read_parquet(path)[["c1", "c2"]] if path.exists() and not full else pd.DataFrame(columns=["c1", "c2"])
    start = first if old.empty else (old.index.max() - pd.Timedelta(days=OVERLAP_DAYS)).strftime("%Y-%m-%d")
    ld.open_session()
    try:
        cols = {}
        for ric, name in ((f"{root}c1", "c1"), (f"{root}c2", "c2")):
            d = ld.get_history(universe=ric, fields=["SETTLE"], start=start, end=pd.Timestamp.today().strftime("%Y-%m-%d"),
                               interval="daily", count=100000)
            d.index = pd.to_datetime(d.index)
            cols[name] = d["SETTLE"].astype(float)
    finally:
        ld.close_session()
    new = pd.DataFrame(cols)
    new.index.name = "Date"
    out = pd.concat([old.astype(float), new]).groupby(level=0).last().sort_index()   # new values win on the overlap
    out.index.name = "Date"
    return out


def rollex_spread() -> pd.DataFrame:
    """Rollex active contract minus the next contract in the KC cycle, from per-contract settlements."""
    rx = pd.read_parquet(ROLLEX)[["rollex_px", "active_label"]]
    rx.index = pd.to_datetime(rx.index)
    fut = pd.read_parquet(FUT, columns=["Date", "month", "year", "settlement"])
    fut["Date"] = pd.to_datetime(fut["Date"])
    px = fut.set_index(["Date", "month", "year"])["settlement"].astype(float)
    px = px[~px.index.duplicated(keep="last")]

    def parse(lbl):
        m = re.match(r"([A-Za-z]{3})'(\d{2})", str(lbl))
        if not m or m.group(1) not in MONTH_TO_LETTER:
            return None, None
        return MONTH_TO_LETTER[m.group(1)], 2000 + int(m.group(2))

    act, nxt = [], []
    for d, lbl in rx["active_label"].items():
        mth, yr = parse(lbl)
        if mth is None:
            act.append(float("nan")); nxt.append(float("nan")); continue
        i = CYCLE.index(mth)
        nm, ny = (CYCLE[0], yr + 1) if i == len(CYCLE) - 1 else (CYCLE[i + 1], yr)
        act.append(px.get((d, mth, yr), float("nan")))
        nxt.append(px.get((d, nm, ny), float("nan")))
    rx["active"] = act
    rx["spread_rollex"] = pd.Series(act, index=rx.index) - pd.Series(nxt, index=rx.index)
    return rx[["rollex_px", "active_label", "active", "spread_rollex"]]


def parse_eom() -> pd.DataFrame:
    """ICE end-of-month total certified bags. The date column is a mix of real dates and typed text
    (e.g. 'May31,2010', 'Augusr 29,2025'), so month/day/year are read out of the text."""
    raw = pd.read_excel(EOM_XLS, header=None).iloc[7:, [1, 10]]
    raw.columns = ["raw", "Bags"]
    months = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

    def to_date(x):
        if isinstance(x, (pd.Timestamp,)) or hasattr(x, "year"):
            return pd.Timestamp(x)
        m = re.match(r"\s*([A-Za-z]+)\s*(\d{1,2}),\s*(\d{4})", str(x))
        if not m or m.group(1)[:3].lower() not in months:
            return pd.NaT
        return pd.Timestamp(int(m.group(3)), months[m.group(1)[:3].lower()], int(m.group(2)))

    raw["Date"] = raw["raw"].map(to_date)
    out = raw.dropna(subset=["Date"]).copy()
    out["Bags"] = pd.to_numeric(out["Bags"], errors="coerce")
    out = out.dropna(subset=["Bags"])
    out["Month"] = out["Date"].dt.to_period("M").dt.to_timestamp("M")
    return out.groupby("Month", as_index=False)["Bags"].last().rename(columns={"Month": "Date"})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--no-lseg", action="store_true")
    a = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if a.no_lseg and PL.exists():
        base = pd.read_parquet(PL)[["c1", "c2"]]
    else:
        base = pull_c1c2(a.full)
    rx = rollex_spread()
    df = base.join(rx, how="left")
    df["spread_c12"] = df["c1"] - df["c2"]
    df = df[["c1", "c2", "spread_c12", "rollex_px", "active_label", "active", "spread_rollex"]]
    df.to_parquet(PL)
    print(f"price_link_kc: {len(df):,} rows {df.index.min().date()} -> {df.index.max().date()} "
          f"| rollex spread on {int(df['spread_rollex'].notna().sum()):,} days")

    eom = parse_eom()
    eom.to_parquet(EOM, index=False)
    print(f"kc_certs_eom_hist: {len(eom)} months {eom['Date'].min().date()} -> {eom['Date'].max().date()}")

    # Robusta: continuation c1/c2 only (its certs come from the LSEG rc_certs database)
    RC_PL.parent.mkdir(parents=True, exist_ok=True)
    if a.no_lseg and RC_PL.exists():
        rc = pd.read_parquet(RC_PL)[["c1", "c2"]]
    else:
        rc = pull_c1c2(a.full, "LRC", RC_PL, "2008-01-01")
    rc["spread_c12"] = rc["c1"] - rc["c2"]
    rc.to_parquet(RC_PL)
    print(f"price_link_rc: {len(rc):,} rows {rc.index.min().date()} -> {rc.index.max().date()}")
