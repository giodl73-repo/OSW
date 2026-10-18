# Pacific NECC paired-vector gap closure: source results

Continue the existing codex/current-measurement-gaps branch and draft PR 83. No per-gap PR or merge to main.

## Data gap closed

The previous 2013 OSCAR target section retained only eastward velocity. The extension retains both u/v at 220 E and the two adjacent native longitudes (219.66666666666669 and 220.33333333333334 E), all 37 latitudes from 0-12 N and all 72 source timestamps. Original CSV: 756,135 bytes; 7,992 vector positions, all paired finite. Every one of the old 2,664 target u values and masks agrees exactly after float64 decoding. Original and new metadata bytes are identical, including version 2017.0 and m/s units.

The actual source timestamps run from 2013-01-01 through 2013-12-26: 67 five-day gaps and four six-day gaps. Equal-sample monthly means are not exact daily/time-weighted calendar means. The nominal 15 m coordinate is product context, not a direct instrument slice. Source region cells are not all assigned to the named current.

The declaration/protocol was committed as 8ee4256 before velocity acquisition. Target u had already been viewed. No fully blinded or externally timestamped preregistration is claimed. Original producer/validator code and response pins are retained in acquisition.json, committed as 2fbcc06.

## Analysis and figures

Thirty-six monthly column profiles retain paired u/v, sample counts, source times, the unchanged connected-component thresholds and selected peak vectors. All twelve central paired-u monthly profiles and zero-crossing spans reproduce the earlier u-only results exactly.

Nine of 36 peak vectors exceed the prospectively declared 15-degree attention guide; maximum absolute departure from east is 46.087793 degrees. Three months have selected peak separation above two native latitude cells across the three columns. These guides are OSW diagnostic choices, not scientific admission thresholds. Same-product neighboring columns are not independent validation or uncertainty bounds.

Two new SVG/PNG figure pairs show (1) native-column monthly paired component fields and (2) peak direction/component-span context. Common zero-centered component palettes, explicit units, actual native columns, a direction guide kept separate from uncertainty, and scope captions avoid presenting source component spans as physical current edges. Layouts were visually inspected and adjusted to prevent label/legend overlap. Consecutive generation produces identical figure hashes.

Five tests and five subtests pass: complete offline reproduction, missing/duplicate/units rejection, old target-u and UTC revision rejection, missing-v propagation that stops boundary closure, and a synthetic 45-degree vector that remains uncorrected into physical width.

## Required shared integration

- Index the full source-vector inventory and report, acquisition/preflight/metadata/figure documents so all retained data can be inspected and queried.
- Bind the primary evidence and its original/derived dependencies in compiled Rust using the existing shared research-evidence contract.
- Add current-card, seasons and query presentation for the paired fields, direction and native-column context with numeric monthly alternatives and source pointers. Reuse existing pages; do not create a separate navigation destination.
- Give figure choices meaningful scene-specific labels while preserving existing scene labels.
- Keep all 150 width records, 79 owners, existing three research scenes and every other current unchanged. The raw/derived vector region does not admit a new physical current width, annual range, axis, polygon, length rank or current-state membership.
- Verify native/WASM source and diagnostic parity, new-source inspection, corruption rejection, keyboard/320px/reduced motion and preservation; then run the clean combined gate and publish to the same PR.

## Shared integration status

The shared registry now contains four research scenes. The new paired-vector report, full vector inventory and five supporting documents are indexed (314 sources total). The compiled Rust contract binds the new primary report; all 84 engine dependency hashes match. Cards, seasons and query use the existing renderer, with scene-specific figure labels, twelve numeric monthly rows and source inspection links. All 53 Rust unit tests pass.

Preservation comparison against the source-only parent passes: all 150 width records, 43 other query collections, 41 prior diagnostics and three prior research scenes are unchanged; only the Pacific countercurrent object and its new diagnostic are added/updated. No physical width is admitted.

The eb16678 clean full suite terminated with 1 failure, 1,650 passed tests and 1,094 passed subtests in 2,379.79 seconds. Its combined-chart test still expected five scene kinds after the WSC addition made six. The expectation now includes the WSC 28 km / 7 km reported-SD scene, keeps the earlier assertions using scene-kind lookup and passes its targeted rerun (10.92 seconds). That historical run does not cover this later NECC package.

The first shared browser run exercised all four owners and reached corruption rejection before its renderer closed during repeated full-packet WASM instantiation. Each corruption now uses and closes its own page to release its heap; all 22 corruption assertions remain. The browser rerun and a clean combined gate for this integration remain pending. Candidate browser checks read candidate static bytes through isolated Playwright routes on the existing localhost origin; this is not a claim that the normal server already serves the candidate.
