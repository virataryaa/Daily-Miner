"""
Robusta (RC) Grading Database Builder
=====================================
Database/source/RC_Grading_Feed.xlsx -> Database/rc_grading.parquet

The grading panel is NOT on LSEG (no LRC-*-PASSGRAD/PENDING RICs exist), so the
source is the Excel feed exported from the exchange. This script only cleans it:
  - PanelDate: real dates, or Excel serial numbers (older exports), both handled
  - strip padded strings (Origin), normalise Commodity to 'RC'
  - Class blank -> 'NA' (non-tenderable, Tenderable = N)
  - NO de-duplication: identical rows can be genuine separate entries and the desk's own
    pivot sums every row, so totals here match it
Tidy long table: one row per panel x exchange x origin x port x class x tenderable x allowance.

Run:  python rc_grading_build.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Database" / "source" / "RC_Grading_Feed.xlsx"
OUT = ROOT / "Database" / "rc_grading.parquet"


def main():
    g = pd.read_excel(SRC)
    pdte = g["PanelDate"]
    if np.issubdtype(pdte.dtype, np.datetime64):
        g["PanelDate"] = pdte.dt.normalize()
    else:
        g["PanelDate"] = pd.to_datetime(pdte, unit="D", origin="1899-12-30").dt.normalize()
    for c in ["Commodity", "UKContUS", "Origin", "PortId", "Tenderable"]:
        g[c] = g[c].astype(str).str.strip()
    g["Commodity"] = g["Commodity"].str.upper()
    g["UKContUS"] = g["UKContUS"].str.upper()
    g["Class"] = g["Class"].astype("string").str.strip().fillna("NA").replace({"nan": "NA", "": "NA"})
    g["Allowance"] = pd.to_numeric(g["Allowance"], errors="coerce").fillna(0).astype(int)
    g["NoLots"] = pd.to_numeric(g["NoLots"], errors="coerce").fillna(0).astype(int)
    g = g.drop(columns=["PanelTime"])
    g = g.sort_values(["PanelDate", "UKContUS", "Origin", "PortId", "Class"]).reset_index(drop=True)
    g.to_parquet(OUT, index=False)
    print(f"[RC grading] {len(g)} rows, {g['PanelDate'].nunique()} panel dates, "
          f"{g['PanelDate'].min().date()} -> {g['PanelDate'].max().date()}, {int(g['NoLots'].sum()):,} lots")


if __name__ == "__main__":
    main()
