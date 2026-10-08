# Monthly source-chart keyboard continuity

2026-10-08. Publication fix following Norwegian coastal width batch ee6bc45.

## Failure and correction

Completed PR30 run 37749997604, head 0ff10d0, passed source acquisition,
offline tests and many browser checks, then failed index-support browser line
134: after Home selected January, ArrowRight did not select February within
30 seconds. `controls(true)` disabled the focused range input during its query,
allowing the browser to drop focus. Subsequent arrow keys missed the input.

Keep the month slider enabled after initial readiness during query refreshes.
Initial loading and actual unavailable-source failures still disable it.
Existing request serials discard superseded replies; repeated keyboard changes
can now request a newer month without losing focus or exposing an old reply.
Other controls retain their existing pending behavior.

The regression holds the Home request, verifies pending status, enabled slider,
focus and value 1, presses ArrowRight, waits for ready month 2, then releases
the older request and verifies month/value/focus remain 2. The remainder of the
full browser check exercises source/owner/layer switching, source variability
bands, monthly playback, reduced motion, sharing, reflow and unavailable data.
No longer timeout, skipped check, synthetic key substitute or fixture relaxation.

## Consolidation

The reviewed Agulhas Return and Norwegian coastal batches advance the scientific
snapshot to 79 scoped width records / 40 owners / 53 unassessed; 82 indexed
source documents. They remain editorial extracts with separate source limits.
Existing full local scientific suite on ee6bc45: 824 tests, 745 subtests;
38 Rust tests. This focus change modifies only JS presentation and its browser
test plus publication documentation. Its affected browser result is recorded
below; this does not assert a rerun of every browser check on the final commit.

Protected-main checks and existing human-enabled squash auto-merge remain the
publication gate. Source acquisition retries and exact original checksums are
unchanged. No restricted original PDF is redistributed or cached.

## Local result

Full `analysis/test_rust_index_support_browser.py` completed successfully on the
final focus code: exact source decisions, 24 display spans, 56 state diagnostic
joins, 36 branching samples with native/WASM parity, distinct source bands and
endpoint reading allowances, owner/layer switching, held older request with
real Home/ArrowRight focus continuity, playback, sharing, reduced motion,
320 px controls and unavailable corpus. All 39 JavaScript syntax checks and
fourteen page assignments pass; assignments are not passing test claims.
`git -c core.whitespace=cr-at-eol diff --check` passes.
