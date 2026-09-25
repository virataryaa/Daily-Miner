# Daily Miner — Certified Stocks & Grading (KC Arabica / LRC Robusta)

Working folder for the daily-updates rebuild. Starts from the Brainstorm prototype
(`Fundamental/Daily Updates/Brainstorm`), which is the reference for everything below.
Order of work: **Robusta (LRC / RC) first**, then Arabica (KC).

## Folder layout (same 4 folders as every other project)

| Folder | Purpose |
|---|---|
| Code | Ingest / builder scripts (LSEG pulls, parquet writers) |
| Database | Main/ (parquet DBs), Manual Inputs/ (daily excel drops), Archive/ (old workbooks), Logs/ (each split by KC, RC, CC, QC) |
| Dashboard | Streamlit app (`cert_app.py` equivalent) |
| Automator | Scheduler / bat / email automation |

## Source: LSEG API (not ICE)

- `lseg.data` (`ld.get_history`) for all RIC pulls, field `COMM_LAST`.
- `refinitiv.data` (`rd.get_history`) for futures settle, field `TR.SETTLEMENTPRICE`.
- Needs LSEG Workspace open and logged in (session opened with `ld.open_session()` / `rd.open_session()`).
- Python: `C:/Users/virat.arya/AppData/Local/anaconda3/python.exe`.

## RIC reference

### Robusta (LRC) — start here

| Group | RIC | Notes |
|---|---|---|
| Cert stocks by port, VG grade | `LRC-{port}-VG` | ports: AMS, ANT, BAR, BRE, FEL, GEN, HAM, LIV, LON, NOR, ROT, TRI, TOT |
| Total by other grades | `LRC-TOT-NT`, `LRC-TOT-CL` | totals only. `LRC_GRADES = [VG, NT, CL]` was defined in the prototype but never used per port |
| Futures price | `LRCc1` | field `TR.SETTLEMENTPRICE` (Refinitiv session) |
| Grading feed | not an RIC | manual Excel `RC_Grading_Feed.xlsx` (see below) |

Port names: AMS Amsterdam, ANT Antwerp, BAR Barcelona, BRE Bremen, FEL Felixstowe, GEN Genoa,
HAM Hamburg, LIV Liverpool, LON London, NOR Northern (Ports), ROT Rotterdam, TRI Trieste, TOT Total.
(The prototype only labels ANT, LON, FEL, BAR explicitly; the rest are ICE Europe port codes, verify when rebuilding.)

### Arabica (KC) — second phase

| Group | RIC pattern | Members |
|---|---|---|
| Cert stocks | `KC-{origin}-{port}` (17 x 8 = 136) | origins: BRZ Brazil, BUR Burundi, COL Colombia, COS Costa Rica, ELS El Salvador, HON Honduras, IND India, MEX Mexico, NIC Nicaragua, PAN Papua New Guinea, PER Peru, RWA Rwanda, TAN Tanzania, UGA Uganda, VEN Venezuela, GUA Guatemala, TOT Total. ports: AN Antwerp, BA Barcelona, HA Hamburg/Bremen, HO Houston, MI Miami, NO New Orleans, NY New York, TOT Total |
| Grading queue | `KC-{port}-PASSGRAD`, `KC-{port}-FAILGRAD` | ports AN, HA, HO, MI, NO, NY |
| Grading totals | `KC-TOT-PASSGRAD`, `KC-TOT-FAILGRAD`, `KC-TOT-TOTGRADE`, `KC-TOT-PENDING` | |
| Differentials (`COF-ARB`) | `COF-ARB-BRDIF` Brazil NY 3/4, `-BRSDF` Brazil Santos, `-BRMIF` Brazil Rio 15/16, `-BRRDF` Brazil Rio 17/18, `-ETDIF` Ethiopia Djimmah, `-UGDIF` Uganda Drugar, `-INDIF` India Cherry | |
| Differentials (`COF-WARB`) | `COF-WARB-CODIF` Colombia Excelso, `-HNHDF` Honduras HG, `-PEDIF` Peru MCM, `-GTDIF` Guatemala SHB | |
| Futures price | `KCc1` | field `TR.SETTLEMENTPRICE` |

Fallback: if differentials come back empty on `COMM_LAST`, retry with `TRDPRC_1`.

## Data as of prototype (last date 2026-03-27, stale)

| File | Shape | Range |
|---|---|---|
| cert_lrc.parquet | 2,557 x 17 (Date + 13 port VG + TOT-NT + TOT-CL + LRC_Price) | 2015-01-05 to 2026-03-27, roughly biweekly early then daily |
| cert_kc.parquet | 816 x 165 | 2023-01-03 to 2026-03-27 daily |
| RC_Grading_Feed.xlsx | 1,235 x 10 | panel dates from ~Jan 2022 |

### RC Grading feed schema

Columns: `Commodity, UKContUS, PanelDate, PanelTime, Origin, PortId, Class, Tenderable, Allowance, NoLots`.

- `PanelDate` is an Excel serial number (convert with `origin="1899-12-30"`, unit `D`).
- `UKContUS` values: `C` Continent, `UK`, `US`.
- Origins (13): Brazilian Conillon, Vietnam, Indonesia, India, Cameroon, Guinea, Cote d'Ivoire, Sierra Leone, Tanzania, Angola, Venezuela, Uganda, Republic of Madagascar. Values are space-padded, so strip.
- Ports: ANT, HAM, BRE, BAR, LON, LEH, AMS, GEN, TRI, FEL, NOR.
- Class: 1, 2, 3, 4, P (plus NaN). Tenderable Y/N. Allowance in points: 0, -30, -60, -90, 30.
- Commodity column has mixed case (`RC`, `c`, `C`), normalise it.
- The feed is maintained manually in Excel, not pulled from LSEG. Automating this is an open item.

## Ingest logic (prototype `cert_ingest.py`)

1. `fetch_batch(rics, field, start)`: `ld.get_history(..., interval="daily", count=10000)`, flatten MultiIndex columns, return empty frame on error.
2. KC: cert stocks in batches of 50 RICs from 2023-01-01, then grading queue, then differentials (renamed to friendly names), then `KCc1` settle. Concat, drop duplicate columns, forward-fill price onto the date index, drop rows where `KC-TOT-TOT` is null. Save `cert_kc.parquet`.
3. LRC: 13 port VG RICs plus `LRC-TOT-NT` and `LRC-TOT-CL` from 2015-01-01, add `LRCc1` settle as `LRC_Price` (forward-fill), drop rows where `LRC-TOT-VG` is null. Save `cert_lrc.parquet`.

## Dashboard logic (prototype `cert_app.py`, Streamlit)

Top radio: Arabica / Robusta. Style: light theme (`#fafafa`), navy `#0a2463`, red `#8b1a00`, green `#1a7a1a` up / `#c0392b` down, custom HTML KPI cards, no emojis.

### Robusta

Tab 1, Certified Stocks:
- Date-range slider, default start 2020-01-01.
- KPI strip: latest date, LRC total certs with day change, Antwerp, ANT % of total, London.
- LRC total certified stocks (line, full history) next to port share pie.
- Current stocks by port (bar) and day-over-day change by port (bar).
- Port stocks over time (lines).
- Rolling 20-day change: `diff().rolling(20).sum()` on Total, ANT, and UK (= LON + FEL summed, then diffed).
- Monthly change table: per month Start (first), End (last), High, Low, `Δ Bags = End - Start`, `Δ % = Δ Bags / Start`. Bar chart of last 36 months, green/red by sign.

Tab 2, Grading (driven by RC_Grading_Feed.xlsx):
- Filters: Panel Date (default latest), Exchange (C/UK/US), Origin.
- KPIs: panel date, total lots, Continent / UK / US lots, origin count, port count.
- Charts: lots by origin, class, port, allowance (pts), origin x class heatmap, total lots over time across all panel dates.

### Arabica (for later)

- Two-date change matrix (older vs latest date, origin x port) and latest origin x port stocks.
- KC total certs with date slider, origin share %, stocks by origin (multiselect), total pending, origin drill-down (origin vs total, % share).
- Origin differentials vs KC futures (cts/lb): latest value and change vs previous observation per differential.
- KC Grading Flow, from the grading queue:
  - `Passed` = sum of PASSGRAD across ports, `Failed` = sum of FAILGRAD, `% Fail = Failed / (Passed + Failed)`.
  - `Certs Δ = diff(KC-TOT-TOT)`, `Pend Δ = diff(KC-TOT-PENDING)`.
  - `Fresh Pending = Pend Δ + Passed + Failed`.
  - `Implied Decerts = Passed - Certs Δ`.
  - Keep only days where Passed + Failed > 0.

## Learnings and gotchas

- Prototype ingest does a full refetch and overwrites the parquet every run. Rebuild should upsert incrementally (per the Master Database pattern).
- Errors in `fetch_batch` are swallowed with a printed warning, so a failed batch silently drops columns. Rebuild should fail loudly or log missing RICs.
- Two different LSEG libraries and sessions are used (`lseg.data` and `refinitiv.data`). Rebuild should consolidate on `lseg.data` if `TR.SETTLEMENTPRICE` works there.
- Price uses `TR.SETTLEMENTPRICE` on `KCc1` / `LRCc1`. Elsewhere in the desk `TRDPRC_1` was found to be the wrong price for CTA/Rollex; prefer SETTLE.
- Differential RICs (`COF-ARB` / `COF-WARB`) are sparse, updating only on some days, so expect many blanks.
- LRC history is irregular early on, roughly biweekly from 2015, so rolling "20-day" windows are 20 observations, not 20 calendar days, in the early years.
- `cert_ingest.py` was git-ignored in the prototype, so the deployed Streamlit repo never had the ingest code. Keep code and dashboard together in this rebuild.
- Prototype Streamlit deploy: requirements = streamlit, pandas, numpy, plotly, pyarrow, openpyxl. If Streamlit crashes with GZip/Starlette errors, pin `streamlit==1.56.0`.
- Grading feed strings are space-padded and `Commodity` case is mixed; always strip and normalise.
- Data in the prototype ends 2026-03-27, so a backfill from that date is needed.

## Repo note

This folder has no `.git` of its own. Running git here resolves to the git repo at the home directory
(remote `Quarks-Quants-EquityMonitor`), which is unrelated. Create or attach a dedicated repo before committing or deploying.

## Next steps

1. Confirm LSEG Workspace is open and test RIC availability for Robusta (`LRC-*-VG`, `LRC-TOT-NT/CL`, `LRCc1`).
2. Build the LRC ingest into Code/, output parquet to Database/, incremental upsert.
3. Decide the RC grading feed source (manual Excel vs automated).
4. Build the Robusta dashboard in Dashboard/, then Automator/.
5. Then repeat for Arabica (KC).


## Database layout

| Folder | Purpose |
|---|---|
| Database/Manual Inputs/{KC,RC,CC,QC} | Daily excel files saved by hand. KC = ICE Coffee C certified stock report (any file name), RC = RC_Grading_Feed.xlsx |
| Database/Main/{KC,RC,CC,QC} | Final parquet databases read by the dashboard |
| Database/Archive/{KC,RC} | Old manual workbooks (Arabica BI*.xlsx), used only by kc_grading_ingest.py --rebuild |
| Database/Logs/{KC,RC,CC,QC} | Cleaning, quarantine and reconciliation logs |

KC grading: drop the day's ICE xls into Manual Inputs/KC and run Code/kc_grading_ingest.py. It parses by section title, reconciles every block against Total in Bags, and a daily file overrides history for its date.
