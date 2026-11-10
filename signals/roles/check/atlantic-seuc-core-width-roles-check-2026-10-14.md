---
skill: roles-check
topic: atlantic-seuc-core-width
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Atlantic SEUC core width: internal review

Base: 9c3732d52cb5c630d0e925deb345b9a63899675b. Data, protocol, Python and
Rust validation, independent graphic and existing atlas UI reviewed through
the seven applicable repository lenses. ORBIT does not apply. This internal
review does not constitute independent scientific admission.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | The 20 cm/s isotach defines a core, not the net-flow boundary. | P2 | Metric explicitly names the velocity-contour core; whole-current inference remains false. |
| CURRENT | The abstract says about 100 km; body says about 120 km. | P2 | Body value retained with its explicit operator; discrepancy preserved, no range, midpoint or error inferred. |
| CURRENT | Core depth, reference depth and width-layer bounds differ. | P2 | Fixed layer remains null; 1000 m prose and 1000 db captions retained separately. |
| SOUNDER | Six cruises do not provide six widths. | P2 | One regional summary; no dated occupation, calendar months, annual extrema or seasonal playback. |
| SOUNDER | The 2008 assessment still describes its own source correctly. | P2 | Original assessment preserved in audit history; 3–6 S float sampling not converted to width. |
| SOUNDER | Attribution does not supply an open license. | P2 | Copyright retained; ignored original hydrated with exact SHA and byte count; no source figures redistributed. |
| CHART | The newer 35 W route is a different spatial support. | P2 | No width geometry inferred from that route or its depth support. |
| CHART | Two textual approximations must not become a plotted interval. | P2 | Independent and inline graphics show one 120 km point; 100 km appears only as discrepancy context. |
| CHART | Existing comparison-link wording incorrectly claimed seasonal model data. | P2 resolved | This record now links to a source-defined core-width graphic. |
| BEACON | Readers need the physical boundary beside the number. | P2 | Captions say source-defined 20 cm/s core and retain unresolved abstract discrepancy. |
| BEACON | Whole-current completeness must not be implied by coverage counts. | P2 | Counts describe scoped evidence: 141 records / 75 owners; no whole-current width admission. |
| BEACON | Users need direct access to the source claim. | P3 | Atlas link queries the exact audit measurement; current inspector retains source and method. |
| HARBOR | Color alone cannot convey point versus range. | P2 | Numeric point label, caption and SVG accessible description explain the operator and absent range. |
| HARBOR | Narrow screens must retain caveats and controls. | P3 | Dedicated browser check covers 320 px reflow, source access and actual record inspector. |
| HARBOR | Nonseasonal evidence must not invite playback. | P2 | Existing disabled playback and empty eligible-index list explicitly tested. |
| KEEL | Removing scope context must not bypass validation. | P2 | Mandatory Python and Rust inventory binding plus frozen source checks; coherent receipt mutation cases cover both runtimes. |
| KEEL | Existing data must not drift during gap filling. | P2 | All 140 previous width records compared to base and preserved; other three no-numeric reviews unchanged. |
| KEEL | Complete local publication gates remain required. | P2 | Validation results recorded below after completion; no green status inferred from a build alone. |
| LOGBOOK | One batch must stay on the existing PR. | P2 | Same branch and draft PR83; no new PR or merge. |
| LOGBOOK | The original source must remain outside public Git. | P2 | PDF ignored; only acquisition receipt, attributed extraction and independent graphic published. |
| LOGBOOK | Previous remote CI was unsuccessful. | P2 | Job115900109751 failed downloading Qiu2010 from Hawaii after retries; report separately from local validation. |

Amendments: remove the validator's premature loop exit; correct the graphic
link's scientific wording; replace stale route-table test count with the
catalog's explicit comparison membership while retaining the studied-reach
exclusion assertion. Independent scientific admission, discrepancy resolution,
geographic edges and repeated compatible widths remain open.

## Validation

Complete default offline suite: **1,397 tests / 1,054 subtests passed** in
1,256.43 s (20m56s). Locked native/WASM build and **47 Rust tests passed**.
Dedicated Atlantic SEUC browser checks passed: point-only source interpretation,
exact source navigation, actual inspector heading/ID, disabled seasonal playback,
320 px reflow and eight coherent native/WASM rejection cases. Existing studied
reach/route exclusions and immutable ledger checks pass. All **44 collections**
and **100 current cards / 141 widths** pass mainline browser checks. Nordic
ownership/source/mobile and eight rejection cases pass unchanged.

Standalone SVG and narrow-screen inline chart visually inspected. All 63 engine
dependency hashes, original/acquisition/protocol hashes, index corpus checks and
staged-file bytes verified. Earlier partial focused run was interrupted in favor
of the complete suite and is not counted as a completed gate. Original PDF is
excluded from Git. Publication stays on draft PR83; remote CI is reported
separately and scientific admission remains pending.
