---
skill: roles-check
topic: south-indian-monthly-section
date: 2026-10-13
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
p3_count: 21
verdict: APPROVED-WITH-CONDITIONS
---

# South Indian monthly section review

Seven installed role lenses applied internally; no delegation or independent
scientific approval claimed. ORBIT is irrelevant to this data batch.
Publication is conditional on the final offline and browser gates.

## CURRENT

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | A peak near 40 S may be ACC or an eddy | P3 | attribution | Association remains false; no named-current width admission. |
| 2 | Upper-1000 m historical context is not a 2013 surface layer | P3 | layer | Nominal 15 m satellite product is explicit; no historical velocity or transport transfer. |
| 3 | Monthly peak changes need not track a current | P3 | time | Full curves retained; annual dimensions null and map animation ineligible. |

## SOUNDER

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | New acquisition must not borrow the earlier acquisition time | P3 | provenance | New CSV receipt has its own timestamp and exact original SHA. |
| 2 | Eastern longitude can be requested incorrectly | P3 | coordinates | Query uses 80 E, not 440 E; native CSV values and normalized positions tested. |
| 3 | Calendar shorthand can invent archive samples | P3 | cadence | Actual 72 timestamps/four six-day gaps and complete pair counts retained. |

## CHART

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Section marks could imply a current axis | P3 | map | Only paired section endpoints; no buffered route or occupied polygon. |
| 2 | Interpolation can hide coarse resolution | P3 | profile sheet | Six narrow-span flags and June search-edge flag retained beside readings. |
| 3 | Grey search window might be read as measured edges | P3 | legend | Caption explicitly distinguishes search context from orange threshold crossings. |

## BEACON

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Fewer unassessed owners could imply completed widths | P3 | status | One owner gains a diagnostic; source-width coverage remains 132 / 71. |
| 2 | 120–180 km might be repeated as annual current width | P3 | explanation | Span of local monthly-mean component values; annual and uncertainty limits remain null. |
| 3 | Method should be reachable from each reading | P3 | navigation | Query inspector links to parent diagnostic, source inventory and all-month profiles. |

## HARBOR

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Chart selection needs keyboard equivalence | P3 | controls | Enter selection, native month select and inspector buttons exercised. |
| 2 | Color alone cannot convey limitations | P3 | alternatives | Sample rows, text flags, live SVG text and accessible title/description accompany charts. |
| 3 | Sources must survive reduced motion and narrow viewports | P3 | reflow | 320 px inspector and manual playback covered in browser gate. |

## KEEL

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Shared dependency refresh could change earlier measurements | P3 | reproducibility | Exact original months/profiles/summaries compared against HEAD; only four dependency hashes differ. |
| 2 | Rebinding a source checksum could permit forged widths | P3 | engine | Frozen four-source Rust receipts and sample binding retain native/WASM rejection tests. |
| 3 | UI and data artifacts need stable gates | P3 | testing | Serialized engine build precedes browser/full offline execution; receipt appended after completion. |

## LOGBOOK

| # | Finding | Severity | Section | Resolution |
| --- | --- | --- | --- | --- |
| 1 | Individual gap PRs conflict with user direction | P3 | workflow | All work continues in existing draft PR #83. |
| 2 | Renewed fingerprints could be misreported as new observations | P3 | dashboard | Four changed owners explained; existing observation dates preserved. |
| 3 | Local gates are distinct from remote source availability | P3 | publication | No remote-green or scientific-release claim inferred from local tests. |

## Synthesis

Seven roles, 21 addressed P3 findings, no open P1/P2. APPROVED-WITH-CONDITIONS
for editorial diagnostics after final gates. CURRENT, CHART and BEACON agree
that surface section spans remain unresolved named-current widths.

Amendments: preserve per-file acquisition time and eastern longitude; expose
resolution/search-edge flags and attribution; verify unchanged earlier profiles
and freeze source/sample binding. Scientific admission remains a separate gate.

## Final gate receipt

Complete offline suite: **1,332 tests and 944 subtests passed in 1278.92 seconds (21m18s).** All 46 Rust tests and locked native/WASM builds passed. The earlier sample browser retained all 127 original samples and five missing readings.

After the full suite, restored the original CRLF in two inventory files without changing any JSON values or route frames; refreshed their dependency hashes and rebuilt the final artifacts. Final browser checks passed all four contexts / 48 monthly samples, keyboard inspection, 320 px reflow, five native and three WASM rejection cases. Final index-store check passed all 201 exact documents, 12 seasonal snapshots, independent NOAA oracle, native/WASM parity and checked-input failures. All 61 engine pins and 201 source pins match final workspace bytes. Profile sheet and mobile capture were visually inspected. All 30 staged files match the workspace exactly; whitespace gate passed.

Editorial publication conditions are satisfied. Named-current association, flow-normal width, effective resolution, whole-current representativeness and annual extrema remain unresolved scientific gates. Prior-head remote run 38489198298 failed before tests when Melet source bytes differed from the original pin; local original fixture verification passed all 30 originals. No source edition or pin was substituted.
