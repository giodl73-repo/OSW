---
skill: roles-check
topic: eac-csiro-100m-source
date: 2026-10-18
source_commit: 58afccb4b5a622f63ff0e901c90aa06dd5a95f92
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# EAC daily source intake: internal role review

Scope: source acquisition, offline reconstruction, source-index/query admission,
Rust/WASM scenes, shared atlas/seasons/query visualization and publication
record. These are repository review lenses, not independent peer review.
ORBIT is excluded: this batch introduces no planetary analogy or comparison.

## CURRENT — physical interpretation

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Daily mapped records are dependent and partially reconstructed. | P2 | Descriptor, quality `method_scope`, shared UI introduction | Retain five-day filtering/SOM qualification; implemented. Do not count independent observations. |
| 2 | Source bottom zeros and zero uncertainty can be mistaken for measured absence. | P2 | 6282 paired bottom cells in quality report, two100m positions | Retain exact zeros and explain prescribed boundary conditions beside charts and readout; implemented. |
| 3 | Array length and mapped spacing do not establish current width or length. | P2 | Fixed173.373km WGS84 array, wider instrument separation | Keep physical width and annual range unadmitted; no rotation or current polygon; implemented. |

## SOUNDER — source identity and exactness

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Metadata23 and data19 must remain distinguishable. | P2 | Collection69711 and NetCDF citation/header | Both versions, stable DOI/file ID, license and original hashes retained in acquisition/header. |
| 2 | Missing values must survive every representation. | P2 | 629 all-missing dates; NPZ/source-profile tests | Preserve NaN bits in NPZ, JSON nulls in all3770rows and original noon UTC schedule; implemented. |
| 3 | QC and interpolation descriptions disagree. | P2 | Header versus descriptor/provider metadata, pinned precursor cleaning code | Expose both discrepancies; precursor code is context and cannot authenticate final mapping. Implemented. |

## CHART — spatial and visual meaning

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | A sampled section can resemble current edges. | P2 | Shared map scene and124positions | Call geometry fixed sampling positions on approximate OSW basemap; preserve exact coordinates and Rust projection; implemented. |
| 2 | Missing dates can disappear in animation. | P2 | 124calendar bins and source-date controls | Keep every recorded date including missing days, explicit missing status, broken curves; implemented. |
| 3 | Changing chart scales could imply extra variability. | P3 | Rust scene field domains and four chart panels | Use fixed domains containing source values plus supplied uncertainty; implemented. |

## BEACON — public claim

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | A completed acquisition is not a completed dimensional measurement. | P2 | Batch plan and admission flags | Say source gap filled; physical width and seasonal extrema remain open. Implemented. |
| 2 | Provider uncertainty has no proved universal confidence convention. | P2 | Four supplied uncertainty fields and metadata | Label plus/minus supplied field; do not claim confidence interval or lateral-width error. Implemented. |
| 3 | A reader needs direct provenance from the selected date. | P3 | Exact-record, all-record, quality, provider and overview links | Retain all five paths beside visualization; implemented. |

## HARBOR — access

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Point colors cannot be the only means to inspect values. | P2 | Source-position selector and live text readout | Supply124keyboard choices with coordinates, bottom and all fields/uncertainty. Implemented; actual browser gate verifies controls. |
| 2 | Animation and narrow charts need explicit controls. | P2 | Reduced-motion handler, stop-at-month-end, scroll regions | Disable playback under reduced motion, preserve manual navigation and focusable horizontal regions; gate at320px. |
| 3 | Loading and missing state must remain textual. | P3 | Status region, all-missing readout and descriptive SVG titles | Preserve announcements without moving focus; implemented. |

## KEEL — executable evidence

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | A checksum of the derived subset alone cannot authenticate extraction. | P2 | Original ZIP CRC/NetCDF SHA and acquisition second read | Full original member verified, every selected bit compared twice;13source tests pass. |
| 2 | Large source corpus and compact scene need independent admission guards. | P2 | Rust source/figure/operator bindings, checked source index | Exercise changed packet, coherent rebinding, invented width and independently changed raw source in native and actual WASM. Durable browser gate registered. |
| 3 | Focused passes do not certify the complete new revision. | P2 | 72Rust tests; earlier published full suite runs separately | Publish exact gate scope and preserve failed attempts; run complete clean successor after the previous full run terminates. Do not label a running gate passed. |

## LOGBOOK — publication

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Each gap must not create a separate PR. | P2 | User direction and existing draft PR83 | Commit/push substantial batches to the same branch/PR; no main merge. |
| 2 | Public data should exclude huge originals and transient signed links. | P2 | Retained2.69MBNPZ,23.67MBJSON, ignored acquisition scratch | Commit licensed retained subset/derived outputs and stable source identities; leave381MBZIP and8GBNetCDF local. |
| 3 | Published bytes must agree with pinned hashes. | P2 | Engine/research/index plus8source-contract pins | Verify both working and committed blobs, refresh same PR status and retain truthful full-gate receipts. |

## Synthesis and amendments

Seven roles,21findings:0P1,18P2,3P3. Verdict:
**APPROVED-WITH-CONDITIONS** for source intake; no physical-width approval.
Top concern: source mapping/boundary values do not establish a measured current
edge. CURRENT, SOUNDER, CHART and BEACON agree on that restriction.

Three amendments are embodied in this batch:

1. Preserve629missing dates and prescribed bottom zeros through source storage,
   coverage accounting, checked queries, charts, map and textual controls.
2. Bind the exact retained corpus independently from the compact query scene;
   preserve original checksums, protocol and documentary disagreements.
3. Register the actual browser/source corruption check in the normal WASM runner;
   publish gate scope accurately and continue only in PR83.

Publication conditions: actual browser gate and committed-byte pins must pass;
complete clean-suite status must be reported with its tested commit. No claim
that the whole atlas is measured, annually resolved or externally validated.
