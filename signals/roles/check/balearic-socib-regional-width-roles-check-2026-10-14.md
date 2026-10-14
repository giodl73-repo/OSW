---
skill: roles-check
topic: balearic-socib-regional-width
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Balearic source-width internal review

Reviewed base: d6c3d07da2beafcdfda9001c98756b07d6fc2970.
Artifact: source extraction, frozen scope, inventory, query and graphic.
Seven applicable repository lenses; ORBIT is not applicable to this
Earth-only quantitative source record. Internal review is not external
scientific admission.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | BC is explicitly Balearic Current in the acronym key. | P2 | Table row identity retained; Northern Current and eddies excluded. |
| CURRENT | Mean GV 0.2 m/s is not an edge threshold. | P2 | Separate context, explicit unknown paired boundaries; mutation rejected. |
| CURRENT | Autumn temporal maximum is not explicitly a width maximum. | P2 | No numeric endpoints assigned to seasons or calendar months. |
| SOUNDER | Suggested citation year differs from reviewed document version. | P2 | 2021 citation and 2023-11-13 version separated from unknown observation dates. |
| SOUNDER | Generic Copernicus credits do not define reproducible width computation. | P2 | Product edition, grid, cutoff and sampling period remain unspecified. |
| SOUNDER | Exact original and license need source evidence. | P2 | 632269 bytes/hash verified fresh; CC BY 4.0 on page 2; original remains excluded. |
| CHART | Narrow range endpoints could be mistaken for a confidence interval. | P2 | Caption distinguishes reported range and unknown error; no midpoint selected. |
| CHART | Regional summary supplies no mapped paired edges. | P2 | Numeric axis only; existing route receives no width band. |
| CHART | Separate event-water band can look like current width. | P2 | Prior source review archived; Storm Blas band remains excluded. |
| BEACON | Source range can be mistaken for whole-current dimensions. | P2 | Regional scope and unknown whole-current/annual dimensions beside graphic. |
| BEACON | Autumn label could suggest 35 km seasonal frame. | P2 | Explicit text rejects that assignment; seasonal playback remains false. |
| BEACON | Generic summary must not imply underlying studies were reproduced. | P2 | Selected original pages reviewed; underlying fields/methods unreviewed. |
| HARBOR | Graphic needs equivalent textual quantities and limitations. | P2 | SVG description and card state both endpoints and unknowns. |
| HARBOR | New card needs source and atlas navigation. | P2 | Dedicated browser passed selection, card, source pointer and map links. |
| HARBOR | Long caveats must reflow at narrow viewport. | P2 | 320 px test passed; screenshot retained for visual review. |
| KEEL | Changed/reassigned range could retain plausible receipts. | P2 | Frozen Python and Rust source binding rejects altered records and rebinding. |
| KEEL | New evidence could disappear while counts remain plausible. | P2 | Unique reviewed inventory record required in both engines. |
| KEEL | Publication requires final offline and index gates. | P2 | Running on final data; results appended below. |
| LOGBOOK | Old no-numeric-width decision is now obsolete. | P2 | Active decision replaced; previous assessment preserved as source history. |
| LOGBOOK | New range does not complete broad measurement objective. | P2 | 139 records / 73 owners; physical widths, annual ranges and methods remain open. |
| LOGBOOK | Consolidated PR and remote status must reflect actual head. | P2 | PR83 retained; preceding Zenk acquisition 403 documented, no green remote claim. |

Amendments: preserve range without a representative scalar or seasons;
bind complete source scope in both engines; retain historical assessments
while updating active coverage. Implemented. Local publication verdict is
conditional on final full/index gate completion. Scientific measurement
admission and source-method reconstruction remain open.


## Final local verification

1,373 tests / 1,023 subtests passed in 1305.91 seconds (21m45s).
All 46 Rust tests and locked native/WASM builds passed. Dedicated browser
passed regional range, source/atlas navigation, 320 px mobile reflow,
native/WASM parity and five rejection cases. The 227-source index browser
passed exact source inventory, twelve seasonal snapshots, independent NOAA
oracle, parity and changed-input rejection. Source original/table,
independent figure and mobile graphic were visually reviewed. Fresh SOCIB
acquisition reproduced the exact 632269-byte original. All source/engine
pins and staged/workspace bytes verified. Previous 138 width records,
canonical arrays, routes, samples, geometry frames and observation dates
remain unchanged; seasonal frame receipt alone refreshed. Internal review
supports editorial delivery. Physical paired boundaries, exact width method,
annual ranges and independent admission remain open. The broader core-data
goal remains active. Publication stays in existing draft PR83, with no merge.
Earlier-head remote run 38541270456 failed Zenk acquisition with HTTP403;
new-head remote status is pending, not claimed green.
