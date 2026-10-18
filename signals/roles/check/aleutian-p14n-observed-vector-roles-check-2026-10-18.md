---
skill: roles-check
topic: aleutian-p14n-observed-vector
date: 2026-10-18
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---
# Aleutian/Subarctic observed-section review

Direct application of the installed CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL and LOGBOOK lenses against changes on parent aec3c7f95c740dec1dfd1230df3e5fee6ce1d0df. Internal functional review, not independent scientific peer review. ORBIT is omitted: no planetary analogy is introduced.

| Role | Finding / evidence | Severity | Resolution or condition |
|---|---|---|---|
| CURRENT | Eastward velocity in this region can include multiple branches and eddies. | P2 | Paper-based search windows retained separately; named-flow association and current edges remain unresolved. |
| CURRENT | u and v must have the same support for a layer vector. | P2 | Joint masks, clipped thickness and 80% minimum support; no speed substitution. |
| CURRENT | A nonmonotone ship section cannot silently become one transverse width. | P2 | Acquisition order, 16 northward steps, spacing/bearings and gap records retained; no width admitted. |
| SOUNDER | Reduced hourly/10 m data differ from native five-minute/four-metre acquisition. | P2 | Source product named explicitly beside the figure and in provenance. |
| SOUNDER | Missing values and source calibration history affect interpretation. | P2 | Fill/range masks preserved; provider GPS, heading and wire-editing cautions visible; no per-cell native-history claim. |
| SOUNDER | Data custody must survive Git conversion and offline reconstruction. | P2 | Four exact original responses, producer/declaration pins, -text attributes and deterministic extraction; committed pins must verify. |
| CHART | Sorting by latitude would hide station loops. | P2 | Curves preserve acquisition order; no monotone interpolation or fabricated edge. |
| CHART | Coordinate context could look like a diagnosed current axis. | P2 | Unconnected hourly mean positions; no ribbon, coastline claim or physical polygon. |
| CHART | Missing samples and long temporal gaps must be visible. | P2 | Grey missing-value crosses; curve break over 90 minutes; unequal/invalid support remains explicit. |
| BEACON | More observed profiles could imply physical width is now known. | P2 | Card says width unknown; 155-record inventory remains unchanged and admission flags remain false. |
| BEACON | Aleutian/Subarctic, Alaskan Stream and North Slope names are easy to confuse. | P2 | Distinct regional flows named; no 30 km stream core or 20 km North Slope width assigned to Aleutian. |
| BEACON | One summer crossing cannot establish seasonal variability. | P2 | Actual July dates, single-transect scope and absence of annual ranges/playback remain visible. |
| HARBOR | Color alone cannot carry velocity sign or sampling validity. | P2 | u/v labels, zero line, marked missing cells, numeric source records and support table accompany the plot. |
| HARBOR | The chart must have an equivalent route to inspectable data. | P2 | Alt text, full-size figure and source queries expose profiles, branch support and sampling legs. |
| HARBOR | Disclosure and narrow layouts need actual checks. | P2 | Keyboard, 320 px/reduced-motion and source/inspector roundtrips required in final browser gate. |
| KEEL | Rehashed scientific changes must not bypass source-bound Rust validation. | P2 | Compiled study and registry bind exact row; coherent mutations tested in native and WASM. |
| KEEL | The new diagnostic must not modify older scalar measurements. | P2 | Require exact preservation of all 155 width rows, seasonal geometry, prior 42 diagnostics and earlier four scenes. |
| KEEL | Layer and gap operators need tests of failure cases. | P2 | Joint support, clipping, exact threshold, invalid depth order and source corruption tests; track metadata bound to original positions. |
| LOGBOOK | The prior full gate covers aec3c7f rather than this new batch. | P2 | Keep its receipt separate; require a clean committed successor gate before a full-pass claim. |
| LOGBOOK | Existing remote source hydration failures cannot be called a passing CI gate. | P2 | Latest two failures recorded by exact source/host; hashes retained and no verification bypass. |
| LOGBOOK | User rejects one PR per gap. | P2 | Same continuing branch and draft PR #83; no main merge. |

21 findings, no unresolved P1 findings. APPROVED-WITH-CONDITIONS: finish final source/Rust/browser checks, exact preservation and committed-pin checks, then run the clean combined suite on the committed batch. No independent current identification, physical width, annual extrema or scientific external approval is inferred from passing software checks.

## Amendments

1. Preserve both components and their actual source support; explicitly report stationary reversals and the long gap.
2. Share an observed-section figure and numeric inspection paths without promoting search windows to boundaries.
3. Bind the new diagnostic in Rust, retain existing rejection cases, and separate initial, final, historical and running gate results.

## Final focused evidence

See `plans/aleutian-p14n-observed-vector-verification-2026-10-18.md`: final12source/registry tests with10subtests,60Rust tests, the dashboard test withfive subtests, allfive actual browser owners and34source documents, and32native/WASM rejection cases pass. All89engine and128registry working/committed pins match;155width rows,42diagnostics andfour earlier scenes remain unchanged. The prior complete gate failed on three disk-exhausted fixture writes; allthree repaired tests now pass with every one of their28cases retained. A clean combined successor gate remains the approval condition. Exact generated/provider bytes retain their hashes rather than undergoing whitespace normalization.
