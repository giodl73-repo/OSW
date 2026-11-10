---
skill: roles-check
topic: redsox-direct-source
date: 2026-10-17
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# REDSOX direct source and metadata review

Artifacts:906 original numerical profiles, two inventories, reviewed support
ledger, parsers, tests, sampling figure and plan. Seven installed role lenses
were applied directly by the implementing agent; no independent reviewer or
sub-agent review is claimed.

| Role | ID | Severity | Finding and applied disposition |
|---|---|---|---|
| CURRENT | C1 | P2 | Archive membership is not descending-plume identity. Keep all membership and width flags false. |
| CURRENT | C2 | P2 | Pressure and geometric depth differ. Preserve all three schemas, native units and missing depth; no p=z conversion. |
| CURRENT | C3 | P3 | Reference and tides affect physical edges. Per-cast reference, obliquity and tidal admission remain measurement gates. |
| SOUNDER | S1 | P2 | Source column declarations conflict. Retain310 nquan conflicts and source sequence without inventing columns. |
| SOUNDER | S2 | P2 | Filename identity can hide bad metadata. Preserve raw labels/coordinates/times; reviewed support has separate authority and exact raw-file bindings. |
| SOUNDER | S3 | P3 | Winter/summer quality summaries differ. Keep0.03/0.04m/s separate; neither becomes a per-cast interval or width error. |
| CHART | M1 | P2 | Connecting stations could imply an axis or footprint. Render points only and identify viewport rectangle as a display choice. |
| CHART | M2 | P2 | Coarse coastline cannot resolve channels. Use it only for overview; omit inferred coastline in detail panels. |
| CHART | M3 | P3 | Combined panels obscure winter sampling. Separate campaigns into four panels with identical view limits. |
| BEACON | B1 | P2 | Profile count could be sold as measured currents. State906 source profiles and unchanged149/79 width coverage. |
| BEACON | B2 | P2 | Recovered event time could fabricate a CTD start. Preserve unknown start and label the cast event separately. |
| BEACON | B3 | P3 | Published tables also have errors. Transcribe only cited rows/fields and disclose other clipping/formatting issues. |
| HARBOR | H1 | P2 | Color-only campaign identity is inaccessible. Separate panels and use distinct marker/legend combinations. |
| HARBOR | H2 | P3 | Static maps need equivalent facts. Add SVG title/description, text/table and full coordinate/issue JSON. |
| HARBOR | H3 | P3 | Dense scientific figure is not a mobile UI. Provide scalable SVG and numerical alternative; no unsupported interactive/mobile claim. |
| KEEL | K1 | P2 | Network hydration could undermine reproduction. Version deterministic ZIPs with original member hashes; builders run offline. |
| KEEL | K2 | P2 | Error handling must be exercised. Test sentinels, units, schemas, frame, counts, conflicting identities and event/start distinction. |
| KEEL | K3 | P3 | Old full pass cannot validate new tests. Record1573/1061 baseline separately from33 focused checks; require combined gate. |
| LOGBOOK | L1 | P2 | Reconciliations must not silently rewrite originals. Exact raw bytes and source issue counts persist; reviewed support is separate. |
| LOGBOOK | L2 | P3 | Source distribution must be clear. Bundle numerical records and attribution; omit authored PDFs, figures and quality-note prose. |
| LOGBOOK | L3 | P3 | Per-gap PRs conflict with user preference. Same rolling branch/PR83; no main merge. |

Selected lenses cover physical meaning, provenance, cartography, public
interpretation, accessibility, reproducibility and repository truth.
Original findings:0 P1,12 P2,9 P3. All12 P2 findings have amendments applied.

Verdict: **APPROVED-WITH-CONDITIONS** for source preparation and reviewed
metadata support. No physical width admission is approved. Complete combined
validation and independent measurement admission remain open.

Top finding: matching filenames do not prove paired physical observations.
CURRENT, SOUNDER and KEEL agree on retaining source conflicts and explicit
reviewed evidence before any velocity/hydrography measurement.

Three amendments:

1. Preserve every raw source issue; bind reviewed identities/positions/event
   context to original hashes and explicit visually reviewed log rows.
2. Keep pressure, missing depth, reference and cruise-specific quality apart;
   forbid physical-width/annual-range promotion in both inventories.
3. Add offline original bundles, failure-oriented parser/reconciliation tests
   and separate campaign panels with text and numerical equivalents.

Executed:33 focused tests passed in7.83s. Four-panel figure and seven cited
cruise-log pages visually inspected. Baseline1573 tests/1061 subtests passed
in2028.82s at663bae6; this is not the combined branch gate.

Final candidate staging verifies22 exact files with no source/publisher PDFs.
The SVG repeats SHA256
`37e18e022a188893eb2731ea1edd446c2a77ba017bf3c97afd51b97638cc172d`
on consecutive figure builds. Numerical source facts, parser outputs and
reviewed metadata retain their separate evidence classes. Compiled assets,
width inventory, seasonal frames and atlas geometry remain unchanged.
