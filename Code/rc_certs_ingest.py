"""
Robusta (LRC) Certified Stocks Ingest
=====================================
LSEG (lseg.data) -> Database/rc_certs.parquet

Wide table: Date | LRC-{port}-{grade} (13 ports x VG/NT/CL) | LRC_Price (LRCc1 SETTLE)
Incremental: first run backfills from START, later runs re-pull the last
OVERLAP_DAYS and upsert (new values win), so late revisions are picked up.

Run:  python rc_certs_ingest.py [--full]
Needs LSEG Workspace open.
"""
import sys
import datetime as dt
from pathlib import Path

import pandas as pd
import lseg.data as ld

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Database" / "rc_certs.parquet"
START = "2000-01-01"
OVERLAP_DAYS = 45

PORTS = ["AMS", "ANT", "BAR", "BRE", "FEL", "GEN", "HAM", "LIV", "LON", "NOR", "ROT", "TRI", "TOT"]
GRADES = ["VG", "NT", "CL"]
CERT_RICS = [f"LRC-{p}-{g}" for g in GRADES for p in PORTS]
PRICE_RIC = "LRCc1"


def get_hist(rics, field, start, end):
    raw = ld.get_history(universe=rics, fields=[field], start=start, end=end,
                         interval="daily", count=100000)
    if raw is None or raw.empty:
        return pd.DataFrame()
    raw.index = pd.to_datetime(raw.index)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.droplevel(1)
    if isinstance(rics, str):
        raw.columns = [rics]
    return raw


def main():
    full = "--full" in sys.argv
    today = dt.date.today().isoformat()
    old = None
    start = START
    if OUT.exists() and not full:
        old = pd.read_parquet(OUT)
        old["Date"] = pd.to_datetime(old["Date"])
        start = (old["Date"].max() - pd.Timedelta(days=OVERLAP_DAYS)).date().isoformat()
    print(f"[RC certs] {'incremental' if old is not None else 'full'} from {start} to {today}")

    ld.open_session()
    parts, missing = [], []
    for i in range(0, len(CERT_RICS), 20):
        batch = CERT_RICS[i:i + 20]
        try:
            df = get_hist(batch, "COMM_LAST", start, today)
        except Exception as e:
            print(f"  batch {i // 20 + 1} failed: {str(e)[:120]}")
            df = pd.DataFrame()
        got = [c for c in batch if c in df.columns]
        missing += [c for c in batch if c not in got]
        if not df.empty:
            parts.append(df)
    if not parts:
        sys.exit("[RC certs] no cert data returned; is Workspace open?")
    certs = pd.concat(parts, axis=1)
    certs = certs.loc[:, ~certs.columns.duplicated()]
    if missing:
        print("  MISSING RICs:", missing)

    px = get_hist(PRICE_RIC, "SETTLE", start, today)
    px.columns = ["LRC_Price"]

    new = certs.join(px, how="outer")
    new.index.name = "Date"
    new = new.dropna(subset=["LRC-TOT-VG"]).reset_index()
    new["LRC_Price"] = new["LRC_Price"].ffill()

    if old is not None:
        cut = pd.Timestamp(start)
        new = pd.concat([old[old["Date"] < cut], new], ignore_index=True)
    new = (new.drop_duplicates("Date", keep="last").sort_values("Date").reset_index(drop=True))
    cols = ["Date"] + [c for c in CERT_RICS if c in new.columns] + ["LRC_Price"]
    new = new.reindex(columns=cols)
    new.to_parquet(OUT, index=False)
    print(f"[RC certs] saved {OUT.name}: {len(new)} rows, {new['Date'].min().date()} -> {new['Date'].max().date()}")


if __name__ == "__main__":
    main()
