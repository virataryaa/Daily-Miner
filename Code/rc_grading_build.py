"""
Robusta (RC) Grading Database Builder
=====================================
Database/Manual Inputs/RC/RC_Grading_Feed.xlsx -> Database/Main/RC/rc_grading.parquet

The grading panel is NOT on LSEG (no LRC-*-PASSGRAD/PENDING RICs exist), so the
source is the Excel feed exported from the exchange. This script only cleans it:
  - PanelDate: real dates, or Excel serial numbers (older exports), both handled
  - strip padded strings (Origin), normalise Commodity to 'RC'
  - Class blank -> 'NA' (non-tenderable, Tenderable = N)
  - exact duplicate rows dropped (Excel rows 1211-1224 of the current feed re-paste rows 1195-1208:
    Indonesia / ANT, 14-23 Jan 2026, 578 lots double-counted)
Tidy long table: one row per panel x exchange x origin x port x class x tenderable x allowance.

Run:  python rc_grading_build.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Database" / "Manual Inputs" / "RC" / "RC_Grading_Feed.xlsx"
OUT = ROOT / "Database" / "Main" / "RC" / "rc_grading.parquet"


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
    n0 = len(g)
    g = g.drop_duplicates().sort_values(["PanelDate", "UKContUS", "Origin", "PortId", "Class"]).reset_index(drop=True)
    if n0 != len(g):
        print(f"[RC grading] dropped {n0 - len(g)} exact duplicate rows")
    g.to_parquet(OUT, index=False)
    print(f"[RC grading] {len(g)} rows, {g['PanelDate'].nunique()} panel dates, "
          f"{g['PanelDate'].min().date()} -> {g['PanelDate'].max().date()}, {int(g['NoLots'].sum()):,} lots")


if __name__ == "__main__":
    main()
