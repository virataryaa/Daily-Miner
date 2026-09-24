"""
Robusta (RC) Grading Database Builder
=====================================
Database/source/RC_Grading_Feed.xlsx -> Database/rc_grading.parquet

The grading panel is NOT on LSEG (no LRC-*-PASSGRAD/PENDING RICs exist), so the
source is the manually maintained Excel feed. This script only cleans it:
  - PanelDate Excel serial -> datetime
  - strip padded strings (Origin), normalise Commodity to 'RC'
  - Class NaN -> 'NA' (unclassed, seen on UK/Vietnam rows)
  - drop exact duplicate rows
Tidy long table, one row per panel x exchange x origin x port x class x tenderable x allowance.

Run:  python rc_grading_build.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Database" / "source" / "RC_Grading_Feed.xlsx"
OUT = ROOT / "Database" / "rc_grading.parquet"


def main():
    g = pd.read_excel(SRC)
    g["PanelDate"] = pd.to_datetime(g["PanelDate"], unit="D", origin="1899-12-30").dt.normalize()
    for c in ["Commodity", "UKContUS", "Origin", "PortId", "Tenderable"]:
        g[c] = g[c].astype(str).str.strip()
    g["Commodity"] = g["Commodity"].str.upper()
    g["UKContUS"] = g["UKContUS"].str.upper().replace({"C": "C"})
    g["Class"] = g["Class"].astype("string").str.strip().fillna("NA")
    g["Allowance"] = pd.to_numeric(g["Allowance"], errors="coerce").fillna(0).astype(int)
    g["NoLots"] = pd.to_numeric(g["NoLots"], errors="coerce").fillna(0).astype(int)
    g = g.drop(columns=["PanelTime"])
    n0 = len(g)
    g = g.drop_duplicates().sort_values(["PanelDate", "UKContUS", "Origin", "PortId", "Class"]).reset_index(drop=True)
    g.to_parquet(OUT, index=False)
    print(f"[RC grading] {n0} -> {len(g)} rows ({n0 - len(g)} dupes dropped), "
          f"{g['PanelDate'].nunique()} panel dates, {g['PanelDate'].min().date()} -> {g['PanelDate'].max().date()}")


if __name__ == "__main__":
    main()
