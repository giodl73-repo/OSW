---
skill: roles-check
topic: branching-source-selector
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 2
p2_remaining: 1
p3_count: 19
verdict: APPROVED-WITH-CONDITIONS
---

# Branching source selector review

Artifact: Rust support API, shared almanac monthly chart and its registered browser check, based on PR #30 head `3e935f7`. All seven installed role definitions were read. These are internal review lenses, not independent scientific peer review. CURRENT reviews scientific scope; SOUNDER source preservation; CHART signed axes and ranges; BEACON explanation and navigation; HARBOR equivalent access; KEEL reproducibility; LOGBOOK publication status.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Monthly regional branching latitude remains distinct from whole-current dimensions and route geometry. | P3 | Rust scope gates and chart scope text | Keep all physical dimension and annual-extrema admissions false. |
| 2 | Indian SSH, Indian upper 400 m and Pacific SSH retain distinct layer and historical period support. | P3 | Typed source/layer selection and selected period | Never borrow WOD09 dates from SSH. |
| 3 | The Pacific band retains its source label; denominator, multiplier and confidence probability are unresolved. | P3 | Root statistical gates and separate table allowances | Do not convert the band to confidence, annual extrema or a full observation envelope. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Both sources come from the checked Rust store; no new unchecked fetch path is introduced. | P3 | support_source and existing index worker | Preserve source hashes and exact input rows. |
| 2 | Mean and band endpoint readings have separate +/-0.1-degree allowances. | P3 | reading_bounds and returned original rows | Reject altered endpoint allowances rather than inflating source variability. |
| 3 | Source URL and full locator follow the owner; source files remain unchanged. | P3 | paint links and change inventory | Keep original extraction provenance available through source queries. |

## CHART

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Separate latitude axes avoid treating south-signed Indian coordinates as north-signed Pacific data. | P3 | Rust axis configuration and hemisphere formatter | Verify both labelled axes against source rows. |
| 2 | Shading is distinct from mean reading bars; no Indian band is invented. | P3 | conditional polygon and four-column table | Preserve band meaning in the legend and textual alternative. |
| 3 | Twelve source months become one repeated-climatology cycle, not two observed years. | P3 | twelve ordered points and legend | Keep playback as month selection without geographic motion. |

## BEACON

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The owner selector names basin-qualified inventory proposals and explains regional branching. | P3 | introductory text and dynamic heading | Keep proposal status separate from measured identity. |
| 2 | Scientific language is paired with a short explanation of spread around the mean. | P3 | amended Pacific legend | Retain statistical unknowns without making probability claims. |
| 3 | Source, proposed-card and share destinations update together. | P3 | dynamic links, owner URL and fail clearing | Verify both destinations and preserved state parameters. |

## HARBOR

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | SVG description and semantic table expose the selected mean and band without relying on color. | P3 | title, aria-label, table columns and selected row | Verify complete twelve-row equivalents. |
| 2 | Slider names months, controls remain keyboard-operated, and playback is explicit. | P3 | existing controller handlers and selection stop | Verify playback ends at December and stops on preference changes. |
| 3 | The longer band column and new owner selector require narrow-screen and target checks. | P2 | expanded mobile test and planned render inspection | Complete 320-pixel inspection and check six controls reach 44 pixels before publication. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Rust rejects unknown owners, unsupported layers, malformed bands and invented statistical/dimension scope. | P3 | new unit test and support request validation | Retain mutation rejections and both source fixtures. |
| 2 | The registered support check now compares all 36 months to source rows and native output. | P3 | expanded native/WASM/source oracle | Also verify polygon coordinates and owner round trips. |
| 3 | Exact candidate browser regression, engine hashes and the complete remote gate remain required. | P2 | local candidate status and protected main | Finish validation; only publish after required CI succeeds. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | PR #30 remains a separate live publication candidate; this branch extends its reviewed dependency. | P3 | Git branch and fresh remote CI state | Keep PR #30 frozen and reconcile with main after it lands. |
| 2 | No PDF, query source corpus, dimension record or frozen export is added by the selector. | P3 | inspected change inventory | Keep scope limited to the typed chart, tests and validation artifacts. |
| 3 | The new plan records original source contracts and exact publication limits. | P3 | plans/branching-source-selector.md | Version final validation evidence without relabelling earlier receipts. |

## Synthesis and amendments

Seven roles; zero P1 blockers, two pending P2 conditions, nineteen P3 observations. APPROVED-WITH-CONDITIONS. CURRENT, SOUNDER and CHART agree that shading must retain its source meaning; KEEL and LOGBOOK distinguish local validation from publication.

1. Complete the expanded browser check and inspect the Pacific mobile chart, including owner/layer switching and all six target sizes.
2. Complete source-store/index and all-collection regression with the rebuilt engine; verify manifests and unchanged source/frozen artifacts.
3. Commit the review and protocol with the candidate, reconcile its dependency with main and pass the complete protected-main gate before claiming publication.

## Final local amendment

The HARBOR P2 condition is addressed. Inspection identified small mobile axis labels; labels now enlarge to 22 SVG pixels at narrow widths, omit unnecessary decimal places on integer ticks and retain hemisphere labels. The selected readings remain in tenths. The table has a keyboard-focusable region and visible focus outline. Its arrow-key scroll was verified after waiting for actual compositor movement. The band has a non-scaling boundary outline with calculated 4.20:1 contrast against the plot background. These changes do not alter source geometry or numerical readings.

Final support validation passed all 36 source/native/WASM monthly samples, polygon coordinates, source periods, available layers, owner switching and unsupported-layer reset, shared state/month restoration, playback ending and stopping during owner changes, keyboard month controls, horizontal table scrolling, all six 44-pixel controls, mobile reflow and unavailable-source link clearing. The Pacific mobile render was inspected. The initial option-state assertion was corrected to read the option's actual DOM disabled property after a focused browser inspection confirmed the control was correctly disabled.

All 38 imported collections, 68 exact sources, index page and source-query UI passed with the new engine. The complete offline suite passed 773 tests and 598 subtests; the subsequent presentation-only amendments were verified through syntax and final browser checks. All 38 Rust unit tests and native/WASM builds passed. All 37 JavaScript modules and 14 page assignments pass, and every engine manifest hash matches. No original source, source catalog/corpus, query bundle, dimension record or frozen export changed.

Zero P1 blockers remain. The single remaining P2 condition is the complete protected-main publication gate for this exact candidate after PR #30 lands. Local success does not establish publication or independent scientific peer review.
