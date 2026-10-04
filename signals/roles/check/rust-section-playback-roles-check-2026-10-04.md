---
skill: roles-check
topic: rust-section-playback
date: 2026-10-04
source_commit: 759246d4fcab441a77eb965fbcea80bc91f08968
working_branch: codex/dated-section-maps
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Recorded section playback review

Internal functional review of Rust day/bounds inventories and explicit browser
playback. CURRENT checks physical claims; SOUNDER checks source identity; CHART
checks temporal/spatial comparison; BEACON checks explanation; HARBOR checks
control access; KEEL checks deterministic queries; LOGBOOK checks delivery.
ORBIT is excluded without a planetary comparison. This is not independent
scientific peer review.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Sparse recorded days cannot establish an annual cycle. | P3, verified | Only 17 recorded observations enter the inventory; no missing months synthesized. Keep seasonal admission separate. |
| 2 | CURRENT | A moving local span does not show a current footprint. | P3, verified | Each frame retains the fixed meridian, component metric and surface scope. Do not relabel this as whole-current evolution. |
| 3 | CURRENT | Changes can include processing-version effects. | P3, verified | Current frame shows its RADS version; playback note discloses version changes. Avoid purely physical attribution. |
| 4 | SOUNDER | Playback dates must come from queried source records. | P3, verified | Rust supplies sorted recorded_days, including filtered five-day 2026 inventory. No browser calendar expansion. |
| 5 | SOUNDER | Each frame needs its exact original receipt. | P3, verified | Frame result equals native query; SVG retains query, subset checksum, dates, metric and source pointer. Keep provenance per frame. |
| 6 | SOUNDER | Other source constraints must survive day replacement. | P2, resolved | Only the visible day predicate is replaced; metric, duplicate year and duplicate day constraints remain. Tested explicitly. |
| 7 | CHART | Automatic refitting could distort temporal comparisons. | P2, resolved | Full eligible bounds fit once; all four tested frames retain identical viewport. Chart axes remain source-based. |
| 8 | CHART | Uniform playback intervals are not uniform physical time. | P3, verified | One observation per second labelled ordinal playback; visible exact dates and no interpolation. Keep calendar gaps explicit. |
| 9 | CHART | Descending value sort must not reorder the day sequence. | P3, verified | Rust day inventory is ascending ISO calendar order, independent of value sort/page size. Test retains descending value sort. |
| 10 | BEACON | Readers need a visible date without hovering. | P3, verified | Recorded day and processing algorithm precede the map scope text on single-day scenes. Keep frame identity visible. |
| 11 | BEACON | Playback should end clearly. | P3, verified | Ends at last source day and resets button label/pressed state; no automatic loop. Explicit play starts again from selection. |
| 12 | BEACON | Filtering must be understandable. | P3, verified | Playback note identifies retained filters and the single replaced visible-day predicate. Duplicate constraints remain disclosed by structured-query UI. |
| 13 | HARBOR | Playback must require deliberate user action. | P3, verified | No autoplay; focusable native play/pause button with aria-pressed. Keyboard start/pause verified. |
| 14 | HARBOR | Pause and navigation must stop future frames. | P3, verified | Generation cancellation handles pause, new query and hidden page; pending inventory responses are ignored after cancellation. Existing in-flight frame can finish. |
| 15 | HARBOR | Small screens still need access to controls and captions. | P3, verified | 320 px reflow check passes; text explains dates/ranges and table remains alternative. No color-only playback meaning. |
| 16 | KEEL | Table pagination cannot truncate the playback inventory. | P3, verified | limit:1 inventory still returns five source dates and complete display bounds. Keep metadata before pagination. |
| 17 | KEEL | Animated frames must match static queries. | P3, verified | All four recorded frames compare exactly to native results; map endpoint/card tests retained. No renderer-only invented state. |
| 18 | KEEL | Playback cancellation needs a concrete regression. | P3, verified | New object query cancels ongoing section playback and remains selected after the next frame interval. Keep asynchronous generation checks. |
| 19 | LOGBOOK | Playback is additional local work after main merge. | P3, verified | Uncommitted on codex/dated-section-maps; no remote publication claimed. Preserve delivery boundary. |
| 20 | LOGBOOK | Diagnostic playback must not imply canonical admission. | P3, verified | Source data/canonical release unchanged; boundary/resolution admission still pending. No new length/range values. |
| 21 | LOGBOOK | Tests must describe current verification scope. | P3, verified | 22 Rust tests and dedicated recorded-day playback check passed; existing SVG/map/card regressions rerun. Full CI not run for this local addition. |

Synthesis: seven roles, zero open P1/P2 findings, 19 P3 notes. Conditional
approval for source-recorded diagnostic playback. CURRENT/CHART/SOUNDER agree
that ordinal animation must not imply continuous physical evolution.

Amendments: query-derived day inventory preserving all other predicates; fixed
eligible map bounds across frames; visible source date/version with explicit
no-interpolation timing. Evidence includes native frame equality, keyboard
play/pause, filter duplicates, query cancellation, mobile reflow and inspected
figures/rust-query-section-playback-review.png. Full CI and independent scientific
boundary/resolution admission remain open. No new annual cycle is admitted.
