---
skill: roles-check
topic: loop-current-dated-streamline
date: 2026-10-04
source_commit: dcd9a61bfbcd7a24022ff5e6250919f799f64dfc
working_branch: codex/loop-current-dated-path
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Loop Current dated diagnostic review

Internal functional review of the source receipt, numerical experiment, protocol,
scope audit and visual page. CURRENT reviews physical claims; SOUNDER provenance;
CHART geometry; BEACON explanation; HARBOR equivalent access; KEEL reproducibility;
LOGBOOK local delivery. ORBIT is excluded without a planetary comparison.
This is not independent scientific peer review or canonical admission.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | SLA cannot substitute for ADT. | P2, resolved | Source inspection found SLA and absolute velocities but no ADT. Protocol forbids applying the 0.17 m method to SLA. |
| 2 | CURRENT | Strongest inflow seed does not prove a maximum-speed full path. | P3, verified | Method labelled OSW integration experiment, distinct from published contour algorithms. Independent ADT comparison remains open. |
| 3 | CURRENT | Four failed neighboring seeds block a robust length/range claim. | P3, verified | Failures retained with null connected lengths; rank, width, annual range and confidence interval null/false. |
| 4 | SOUNDER | Exact regional values must match the original response. | P3, verified | All packed ugos/vgos cells independently matched the checksum-pinned original NetCDF. Date, scale, fill, algorithm and experimental status retained. |
| 5 | SOUNDER | A mutable regional receipt could bypass original response identity. | P2, resolved | Offline builder requires the regional receipt SHA as well as original-response identity and date/grid. |
| 6 | SOUNDER | Published mean and SD are different from this diagnostic. | P3, verified | Separate method-specific source statistics in scope audit; SD is not a confidence interval or annual range. |
| 7 | CHART | Closed recirculation can look like an open current. | P3, verified | Explicit Yucatan-to-Florida gateway test, wrong-gate/return stops and distance cap; no closed ring appended. |
| 8 | CHART | Editorial gates need visible status. | P3, verified | Teal gateway lines and declared coordinates; endpoint and bathymetric review open. |
| 9 | CHART | Failed geometry must remain visible. | P3, verified | Four dashed failed traces shown with solid nominal path; full numerical outcomes in table. Screenshot inspected. |
| 10 | BEACON | A headline number might enter the ranking prematurely. | P3, verified | Local/unranked/review banner and adjacent failure summary; canonical release unchanged. |
| 11 | BEACON | Calculation precision could imply measurement accuracy. | P3, verified | Headline rounds to 100 km; table explicitly labels 0.1 km calculation readback. |
| 12 | BEACON | Readers need method and source access. | P3, verified | Page links exact NOAA file, protocol, complete diagnostic and primary comparison. |
| 13 | HARBOR | Color alone cannot communicate failure. | P3, verified | Solid/dashed patterns plus explicit text and nine-row outcomes table. |
| 14 | HARBOR | Map needs a textual equivalent. | P3, verified | SVG title/description and semantic table supply path/failure meaning without hover. |
| 15 | HARBOR | Narrow layouts can lose the table. | P3, verified | Table has its own horizontal scrolling region; 320 px page reflow checked. |
| 16 | KEEL | Source acquisition must be explicit. | P3, verified | Separate fetch script with optional local original file, pinned checksum and overwrite rejection. Offline builder has no network. |
| 17 | KEEL | Gate failures must not be accepted as lengths. | P3, verified | Tests cover wrong latitude at exit, southward return, missing cells and weak speed, with null connected lengths. |
| 18 | KEEL | Stored coordinates and length need to agree. | P3, verified | WGS84 inverse sum uses stored vertices; independent test recomputes length and reproduces receipt. |
| 19 | LOGBOOK | Regional raw subset source-use review remains open. | P3, open | Local receipt records pending review; no push/publication performed. Complete this gate before publishing the new subset. |
| 20 | LOGBOOK | Inventory counts must not imply new admission. | P3, verified | Ranked lengths and editorial reference-route census unchanged. This separate dated diagnostic has not entered those counts. |
| 21 | LOGBOOK | Broader release validation remains outstanding. | P3, open | Focused scientific/browser checks completed; full CI and independent science still required for publication/admission. |

## Synthesis

Roles reviewed: 7. Open P1/P2: 0. P3 notes: 19, including source-use and full
release review conditions. Verdict: APPROVED-WITH-CONDITIONS for a local diagnostic.
Top finding: seed failures prevent the connected nominal path becoming a robust
current length. CURRENT, CHART and BEACON agree this limit must stay beside the map.

## Amendments applied

1. Explicitly separate SLA from ADT and the published contour algorithms.
2. Pin the regional receipt and independently compare every packed velocity cell.
3. Preserve failed paths visually and numerically, reject wrong-gateway lengths,
   and provide a semantic outcomes table alongside the map.

## Verification

Offline reproduction and scientific gate/mask/readback tests; exact regional
source-array comparison against original pinned NetCDF; Playwright map counts,
all scenario rows and 320 px reflow; inspected generated screenshot.
