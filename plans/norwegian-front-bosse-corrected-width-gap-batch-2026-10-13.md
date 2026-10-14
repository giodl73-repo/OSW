# Corrected Norwegian front width gap batch

Continue `codex/current-measurement-gaps` and draft PR83. The previous source
QA turn changed authoritative state at `a0cced7`; this batch adds an actual
source-reported width and integrates both artifacts into the atlas/source UI.
The full goal remains incomplete.

## Measurement and scope

Reviewed corrected publisher text for Bosse and Fer (2019),
doi:10.1029/2019GL084723, current authoritative version corrected 2020-09-28:
https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2019GL084723

One new proposed-branch record: **38 ± 2 km**, Mohn Ridge Polar Front.
Retain positive-poleward Gaussian integration definition; not FWHM or our
fixed-component half-peak diagnostic. ±2 is a reported source statistic with
width-specific interpretation awaiting corrected Table S1, not an annual range
or declared confidence interval. Reviewed corrected text does not establish
original PDF/SI acquisition or independent raw-data reproduction.

The published mean-structure width is separate from the 2010 unquantified
Svinoy mean, from earlier 30–50 km branch summaries and from raw-mission
vector magnitudes. No inter-method trend, inferred seasonal numbers, full-route
dimension, fixed-depth width slab or occupied geometry follows. Generic
canonical Norwegian Current remains ambiguous; no alias transfer admitted.

## Integration

Proposed Norwegian branch widths: three → four records, still two branch
owners. Mean width of the 2010 Svinoy front remains unresolved. Proposed
identity count stays 28. Canonical counts unchanged: 100 names, 11 published
ranked lengths / 89 length gaps; 73 routes across 67 of those owners / 22 route
gaps; 136 scoped widths across 72 owners; 13 unassessed width owners and seven
section-diagnostic owners whose widths remain unresolved.

The proposed Front card shows the new point and reported ±2 alongside earlier
evidence, with actual method labels, source edition/access and uncertainty
meaning. Reported-statistic text stays beside the chart. No width error bar
is drawn as an annual envelope. The card links the scientific glider source-QA
visual and current records. Both newly registered documents are available in
the checked Rust source-query UI; MR1 has 673 retained records with four
missing pairs. The full source audit includes both missions and original epochs.

Corpus: 210 exact JSON source documents. Core query collections, canonical
data, 199 samples, 24 diagnostics and 16 series remain unchanged. All canonical
dashboard entries/fingerprints and observation dates remain unchanged; only
proposal/audit input receipts and dashboard build time update. Refresh the
equatorial endpoint proposal checksum and two dependent extraction receipts;
their numerical values and source originals remain unchanged.

The whole reviewed record is frozen by Python source SHA and compiled Rust
comparison. Proposal and branch-audit copies must agree. Source store checks
the standalone corrected record too. A coherently rebound proposal receipt
with altered ±2 is rejected in native Rust and WASM. No original paper pin
or edition changed to satisfy a guard.

## Verification

Focused gate: eight tests / 111 subtests passed. All 46 Rust tests passed;
native and shipped WASM built serially. Corrected-source browser passed branch
card/mobile, query links, 673 raw records, native/WASM source parity and coherent
uncertainty rewrite rejection. Existing regional-width browser passed previous
Norwegian coastal/slope and other source-width cards and source/temporal scope
guards. Index-store browser passed 210 exact originals, twelve seasonal
snapshots, independent NOAA oracle, native/WASM parity and checked-input errors.
The mean/range chart and adjacent statistic explanation were visually inspected.

Full offline gate: **1,347 tests and 990 subtests passed in 1291.26 seconds
(21m31s)**. Final publication integrity: all 61 engine pins and all 210 source
document hashes/byte counts verified; staged files match workspace bytes.
Five earlier component-section reports remain byte-identical. Canonical
dashboard entries, fingerprints and observation dates are unchanged; two
equatorial numerical extractions refresh only their scope-audit receipts.
The corrected-source browser initially failed its test harness's attempt to
rewrite an external index catalog as though it were inside the payload. The
catalog is compiled and immutable. The corrected test coherently rewrites the
mutable main-store proposal receipt and verifies native/WASM semantic rejection.
All final browser and source-store gates passed.

Prior-head remote CI at `a0cced7` failed before tests while retrieving the
Melet original paper, whose current download differs from the pinned source.
The source pin was not changed or waived; local results do not prove remote CI.
Internal seven-role review covers editorial extraction only. Direction
corroboration, corrected supporting table, exact width occupations, compatible
seasonal sections, branch geometry and canonical scientific admission remain
open. Current unassessed width and length totals have not been reduced by this
proposed-branch evidence.

Reproduce: branch validator; dashboard/index/query builders; serialized engine
build; default offline pytest; corrected-source, regional-width and index-store
browser checks. Use the existing localhost:8788 server. Raw source QA can be
regenerated from the documented pinned NMDC originals; no acquisition is
performed by the width extraction or default tests.
