---
skill: roles-check
topic: nwasc-source-reference-route
date: 2026-10-22
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Regional NwASC reference: internal role review

These are seven repository review lenses applied by the implementing agent,
not independent reviewers or scientific peer review. ORBIT is inapplicable:
no planetary analogy is proposed. Scope: source input/protocol/report, producer,
SVG, derived route catalogue, Rust admission/query maps and navigation checks.

| Role | Finding | Severity | Location | Resolution / recommendation |
|---|---|---|---|---|
| CURRENT | Connecting source reference points does not diagnose a current axis. | P1 resolved | protocol, report, route card | Separate source-anchor class; physical-axis and physical-state-join flags false. |
| CURRENT | A500m steering description supplies no sampled bathymetric contour. | P1 resolved | protocol/SVG | No isobath claim; no bathymetric input or invented contour. |
| CURRENT | Bend scenarios cannot measure seasonal length, width or uncertainty. | P1 resolved | scenarios/card | All anchors fixed; label260-270km as editorial bend probes; no rank/width additions or animation. |
| SOUNDER | P2 degrees/minutes require exact conversion and longitude signs. | P1 resolved | input/operator/tests | Preserve source DMS and exact anchor floats; independent WGS84 leg sum test. |
| SOUNDER | Frozen catalogue/source byte addresses must survive derived projection. | P1 resolved | builders/atlas snapshot | Old77 rows unchanged; derived78 catalogue separate; original source_json address preserved. |
| SOUNDER | The original paper is copyrighted and positional accuracy unspecified. | P2 resolved | source receipt/protocol | Private ignored PDF/renders, factual public metadata and own SVG; computational WGS84 convention explicitly qualified. |
| CHART | Straight map segments could cross land between anchors. | P1 resolved | dense coastline checks | All9 raw and rounded exports checked at <=1km against coarse and1:10M pinned masks. |
| CHART | One current may own several routes; query maps must select the requested candidate. | P1 resolved | map.rs/lib.rs | Match owner current_id and candidate_id plus editorial role; missing candidate stays unmapped; regression unit test. |
| CHART | Nominal and probe geometries need distinct visible explanation. | P2 resolved | SVG/card | Source point labels, dashed nominal, pale probes, title/description and explicit nonphysical scope. |
| BEACON |260km could be read as a new whole-current measurement. | P1 resolved | card/query scope | Source-reference-only language beside value; separate from studied reaches and published ranks. |
| BEACON | Newly mapped102 names could imply complete current axes. | P2 resolved | batch notes | Say geographic marks; keep89 unranked lengths and other coverage gaps explicit. |
| BEACON | A method should be reachable from the visual. | P2 resolved | source joins/card | Pinned input, protocol, report, factual source citation and full own SVG linked. |
| HARBOR | Map marks require keyboard access and a textual destination. | P2 verification | browser | Require focus/Enter from current card to route card/full SVG and query mark to route record. |
| HARBOR | A regional figure must remain usable at320px. | P2 verification | browser | Check no horizontal overflow; full-size SVG link and text measurements remain available. |
| HARBOR | Missing seasonal data must not become plausible animation. | P1 resolved | seasons validator/browser | No eligible indices; play disabled; no date/frame promoted from mean-field reference coordinates. |
| KEEL | Admitted geometry and source pins need native validation. | P1 resolved | nwasc_reference_route.rs | Reject modified anchors/role/date/frame/physical flags, earlier rows or source bindings. |
| KEEL | Linux reconstruction must be attributed to the new source head. | P2 pending | CI | Require all30 report retained/rebuilt SHA256 values match local; append terminal receipt. |
| KEEL | Complete offline/browser coverage remains incomplete. | P2 open | default suite | Full133 browser matrix unrun; local4GiB guard unmet; prior offline CI source HTTP403 before tests. Do not claim full green. |
| LOGBOOK | User rejects one PR per gap. | P1 resolved | publication | Continue existing draft PR83/branch only; no main merge. |
| LOGBOOK | New route must not silently rewrite historical measurements. | P1 resolved | preservation receipt | All earlier29 reports/producers,77 routes and439 source descriptors checked exact. |
| LOGBOOK | Large WASM and whole-snapshot memory remain delivery limits. | P2 open | artifacts | Record actual bytes; narrow viewport checks do not benchmark device memory. Keep packaging concern visible. |

## Synthesis and amendments

Seven lenses; zero unresolved P1 blockers. Three verification conditions require
terminal browser results and fresh30-report Linux evidence before publishing the
receipt. Two broader P2 issues remain open: complete-suite coverage and artifact
packaging/memory. Verdict: APPROVED-WITH-CONDITIONS for continued draft work;
not a merge or release approval.

Highest-priority amendments implemented: (1) separate the regional reference
from physical axes/ranks; (2) preserve source anchors and frozen source addresses;
(3) map route queries through only their admitted owner candidate and keep missing
geometries unmapped. Terminal verification receipts will follow below.

### Local evidence received

49 focused tests/2 subtests,125 Rust tests, native/WASM builds and complete native
atlas ingestion pass. Actual Chrome passes all5 exact native/WASM query comparisons,
including all78 route maps and all102 mapped named-current records, route record
inspection, keyboard card/SVG links, original source addresses,320px layout and
no seasonal playback. Own SVG screenshot visually checked. These close the three
HARBOR verification findings locally. Old29 reports/producers,77 route records and
439 source descriptors remain exact; all441 current hashes and428 engine pins verify.
Fresh30-report Linux reconstruction and terminal directory regression still pending.

Atlas-directory regression passes:102 currents/140 eddies or detections, search,
map selection, keyboard, updates, shared gateways, empty results and320px reflow.
Nine superseded generated parts were individually hash/length/containment checked
and retired after all consumers finished; current parts and research originals remain.

### Fresh Linux and publication receipt

Scientific source commit31b9cd45575b07f0fee6cf0ba3a4e72e86b5c639,
run39745580870, scientific-reproduction job119713070243:SUCCESS.
All30 retained/rebuilt report SHA256 values match local exactly. This proves
reconstruction of the admitted source references, not independent reconstruction
of the original satellite observations. NetCDF job119713069984:SUCCESS.
Offline job119713070276 stops at Rotschi1972 paper-fixture acquisition:
https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers20-05/010028590.pdf
returns HTTP403 before tests. This supersedes the preceding Stramma1992 failure
as the latest acquisition blocker. No overall green/full-suite claim.

All428 raw staged engine pins and441 index-source hashes verify. GitHub accepted
the source push with a >50MB recommendation warning for the54,834,640-byte WASM.
The following receipt-only commit changes these two review documents, preserving
all source/data/engine/artifact bytes from the Linux-tested source head. Source
and receipts continue in existing draft PR83; no new PR and no main merge.
Full133-browser matrix and complete local suite remain unrun;4GiB guard unmet.
The internal seven-role review has no unresolved P1; broader suite coverage and
snapshot packaging/memory remain open P2 conditions, not external peer approval.
