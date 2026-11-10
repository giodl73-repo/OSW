---
skill: roles-check
topic: persian-gulf-geostrophic-scales
date: 2026-10-14
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Persian Gulf outflow: internal source, measurement and map review

Base: 456be367f5d1e71f3d5f07a244a18f6b8a943d82. The seven applicable
repository lenses review two source-described geostrophic scales, an editorial
northern cascading reach, provenance, Python/Rust checks and atlas integration.
ORBIT does not apply. Internal review is not independent scientific admission.

| Role | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| CURRENT | The 30 km band and 5 km faster peak are different spatial descriptions at R13. | P2 | Distinct operators; no physical variability interval, midpoint or two-occupation claim. |
| CURRENT | The quoted speeds do not define extracted lateral edges. | P2 | Explicit edge threshold null; no invented 0.1/0.4 m/s width-cutoff rule. |
| CURRENT | Reference-dependent geostrophy differs from contemporaneous ADCP sampling. | P2 | 30 m reference plus 0.09 m/s offset and missing R13/R12 ADCP retained; source cautions visible. |
| SOUNDER | R13 prose lacks the realization suffix attached to the companion figure. | P2 | R13b method link and three R13 occupation dates retained as context; exact width date null. |
| SOUNDER | Publisher and author-version page/table numbering differ. | P2 | Complete unchanged institutional author versions pinned; new locators explicitly name rendition. |
| SOUNDER | Existing salinity cores have a different boundary equation. | P2 | All six records preserved exactly and frozen independently of the two velocity definitions. |
| CHART | The regional line does not locate R13's velocity edges. | P2 | Sketch, section support and absent width geometry separated; no width band painted around the route. |
| CHART | Source section distances and buoy travel distances are different lengths. | P2 | 140 km OSW route is unranked and kept separate from the old 920 km section coordinate. |
| CHART | Standalone route legend overlapped endpoint labels. | P2 resolved | Map framing corrected; final SVG text rectangles checked for overlap and figure visually inspected. |
| BEACON | Two widths can misleadingly imply seasonal variation. | P2 | Captions explicitly identify two spatial descriptions, not a 5–30 km range. |
| BEACON | A geographic reference route can imply measured continuity. | P2 | Title, scope and caveats identify a source-guided editorial reach; full-current length remains unknown. |
| BEACON | Existing graphic-link wording implied seasonal model data. | P2 resolved | Optional source-specific label now says compare the flow band and faster peak. |
| HARBOR | A visual point needs equivalent textual support. | P2 | Numeric labels, accessible descriptions, operator, reference and missing-support text supplied. |
| HARBOR | Source inspection must select the exact definition. | P2 | Separate /measurements/0 and /measurements/1 links checked in browser. |
| HARBOR | New card navigation and narrow displays must retain caveats. | P3 | Dedicated 320 px route, phase, source and actual-inspector checks; full scope-review regression. |
| KEEL | Coherent edits to both receipts and rows must still be rejected. | P2 | Nine native/WASM corruption cases cover range, date, layer, cutoff, reference, erased context, missing row, legacy mutation and forged pin. |
| KEEL | Old route/data assumptions cannot be silently loosened. | P2 | All 141 prior widths and 74 prior route records unchanged; comparable-route ordering unchanged. |
| KEEL | Artifact validation must use the final visual output. | P2 | Initial regression run interrupted after visual defect; final rebuild and complete rerun required below. |
| LOGBOOK | Source copyright must remain accurate. | P2 | AGU copyright retained; both original PDFs ignored; public receipts, attributed facts and independent SVGs only. |
| LOGBOOK | Counts need separate owners, operators and routes. | P2 | 143 width records / 75 owners; 75 routes / 69 owners; 20 of 89 still lack routes. No canonical ledger or ranked-length additions. |
| LOGBOOK | Work must accumulate in the existing PR. | P2 | Same branch and draft PR83; no merge; local gates and remote acquisition failures reported separately. |

Amendments: preserve source reference/occupation ambiguity; separate velocity
scales from salinity widths; correct route-label overlap; retain the six-row
salinity table while adding separate velocity graphics; refresh only the family,
endpoint and monthly dependency hashes affected by the new non-family route.
No family interpretation or monthly values change.

## Validation

Final complete offline run: **1,409 tests / 1,054 subtests passed** in
1,358.38 s (22m38s). Locked native/WASM builds and **47 Rust tests passed**.
All **44 query collections** and **100 current cards / 143 width records** pass
native/WASM browser coverage, actual inspectors, pagination, keyboard and mobile
checks. The dedicated final Persian Gulf browser run passes both operators,
six old salinity records, corrected map, exact source pointers and nine coherent
rejection cases. The existing 40-source-scope atlas review also passes.

Independent graphics visually inspected. Corrected standalone route labels have
no overlapping SVG text rectangles. All engine dependency hashes, source/
acquisition/protocol pins, old 141 width records, old 74 route rows, unchanged
comparable-route order and monthly numerical values verified. Only the Persian
Gulf dashboard entry changes. Staged bytes and whitespace verified; both original
PDFs excluded. The earlier regression/UI coverage attempts were interrupted for
the map-framing correction and are not counted as completed final gates.

Previous remote-head offline jobs failed before validation: GEOMAR/Zenk HTTP403
(job115919126963) and Hawaii/Qiu timeout (job115919063694). No source pins relaxed.
New-head remote CI remains separate from these successful local gates. Same
PR83, no merge. Scientific admission, velocity edge geometry, width error and
whole-current/annual dimensions remain unresolved.
