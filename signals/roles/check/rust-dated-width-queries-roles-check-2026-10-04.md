---
skill: roles-check
topic: rust-dated-width-queries
date: 2026-10-04
source_commit: 7f114b94e546e972a25151d8bd2b62f06aee5393
working_branch: codex/route-evidence-queries
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Recorded-day section width query review

Internal functional review of sample projection, source reconstruction, Rust
validation/date charts, browser controls and evidence cards. CURRENT evaluates
physical scope; SOUNDER evaluates source support; CHART evaluates dates/ranges;
BEACON evaluates language/navigation; HARBOR evaluates access; KEEL evaluates
reproduction; LOGBOOK evaluates release claims. ORBIT is excluded because this
change introduces no planetary comparison. Scientific admission remains open.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Fixed-meridian eastward-component span is not a flow-normal jet width. | P3, verified | Metric and inspector retain this distinction. Require compatible jet-coordinate evidence before changing the metric. |
| 2 | CURRENT | Threshold sensitivity cannot be relabelled measurement uncertainty. | P2, resolved | Separate diagnostic sensitivity and grid bracket fields; dashed whiskers, explicit labels, null measurement uncertainty. Keep range types distinct. |
| 3 | CURRENT | System samples cannot be inherited by the separate Gulf Stream Current or its streamline. | P3, verified | All 17 samples remain owned by current:gulf-stream-system, with no map buffer or width transfer. Preserve identity/layer support. |
| 4 | SOUNDER | Source processing changes accompany the recorded-day series. | P3, verified | Original RADS 4.7.0/4.7.1/4.8.1 retained per sample and in chart notes. Do not attribute the plotted change solely to physics. |
| 5 | SOUNDER | Projection must reproduce the original section diagnostic. | P3, verified | Bundle builder runs pinned-source reconstruction against all 17 subsets and protocol/generator/sampler hashes. Keep reconstruction before projection. |
| 6 | SOUNDER | JSON f64 readback can differ in its last bit. | P3, verified | Original bundle payloads are exact; readback test permits only 1e-15 m/s derived-speed and 1e-14 degree boundary-latitude roundoff. Dates, widths, scenarios and flags remain exact. Preserve original files and receipts. |
| 7 | CHART | Equal sample spacing would conceal the long date gap. | P2, resolved | Gregorian elapsed-day axis preserves monthly 2025 spacing, the December-to-September gap and daily clustering. Keep ticks as calendar coordinates, not invented observations. |
| 8 | CHART | Dense September observations can overlap. | P3, verified | All 17 points retained with separate keyboard targets; chart discloses overlap and provides table access. Never jitter dates into false time positions. |
| 9 | CHART | Filtered views must not silently change scale. | P3, verified | Single-day view retains the complete source x/y domains and exact point primitive. Keep source axes fixed unless an explicit zoom contract is added. |
| 10 | BEACON | Raw six-decimal grid brackets imply unjustified display precision. | P2, resolved | Inspector rounds outward to 10 km and identifies display rounding; raw brackets retained in JSON. Preserve computation separately from reporting precision. |
| 11 | BEACON | One day per month could be mistaken for a monthly mean. | P3, verified | Chart/card explicitly say individual recorded days; source dates remain selectable. Keep monthly diagnostics and daily samples distinct. |
| 12 | BEACON | Each point needs a short evidence path. | P3, verified | Selection opens its exact sample, parent diagnostic, measurement protocol and source URL. Preserve direct receipts and navigation. |
| 13 | HARBOR | Range meaning cannot rely on color alone. | P3, verified | Solid/dashed shapes plus text/ARIA range descriptions distinguish allowances and sensitivity. Keep redundant encoding. |
| 14 | HARBOR | Date/year selections need visible controls and retention. | P3, verified | Labelled year/day selects preserve filters when sorting; additional source constraints retain the existing disclosure contract. Keep unsupported values as explicit extra filters. |
| 15 | HARBOR | Point cards must work without a pointer and on small screens. | P3, verified | Enter selects the exact final-day sample; 320 px reflow passes with scrolling chart frame and text/table alternatives. Preserve focus and original records. |
| 16 | KEEL | Dates, source algorithms and range types could drift on import. | P3, verified | Rust binds each field to its original frame; eight mutations are rejected at load. Keep typed source bindings. |
| 17 | KEEL | Calendar math must handle leap and century boundaries. | P3, verified | Tests cover 1900/2000/2024 differences and roundtrip years 1–9999; plotted tick labels match Python Gregorian ordinal coordinates. Keep exact calendar semantics. |
| 18 | KEEL | New sample family could break existing charts/queries. | P3, verified | Native/WASM dated checks, all-width query and chart regressions pass with 105 samples, seven panels and five unresolved older readings. Retain legacy source values. |
| 19 | LOGBOOK | New query coverage must not imply canonical measurements. | P3, verified | Canonical release diff empty; existing research diagnostic stays review-pending. Keep independent admission gates. |
| 20 | LOGBOOK | Manifest and test counts must describe the actual snapshot. | P3, verified | Engine/source/generator hashes match; checks updated to 105 samples and seven panels; documentation records the 17-sample addition. Regenerate explicitly on updates. |
| 21 | LOGBOOK | Local work must remain distinguishable from main. | P3, verified | Changes remain uncommitted on codex/route-evidence-queries together with the prior worklist slice. No publication claimed. Preserve delivery status. |

Amendments: distinct threshold/grid/uncertainty fields and labels; elapsed-date
axes with calendar ticks and dense-point access; outward grid-bracket display
rounding with raw source retention.

Verification: 21 Rust tests, nine Python checks and seven subtests; standalone
dated-sample, all-width query and width-chart browser/native/WASM checks; source
mutation rejections, year/day filter retention, keyboard and mobile evidence;
screenshots inspected; JS syntax, whitespace and SHA manifest checks pass.
Full default CI has not been run for this local slice. Conditions: scientific
identity, boundary/orientation/resolution validation, broader temporal coverage
and canonical admission remain open. Sampled spans do not establish annual
extrema, an observed footprint or width of an alongstream diagnostic trace.
