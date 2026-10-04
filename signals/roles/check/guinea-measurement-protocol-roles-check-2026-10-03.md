---
skill: roles-check
topic: guinea-measurement-protocol
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Guinea route and measurement protocol v1.0

Internal review under the installed seven relevant .roles lenses. ORBIT
excluded because no planetary analogy is made. Not independent scientific
approval. Artifacts: Guinea input/report/SVG, two identity proposals,
protocol, audit, EAC metadata revision, atlas summary, docs and tests.

| Role | Finding | Severity | Amendment or remaining condition |
| --- | --- | --- | --- |
| CURRENT | A weakening region is not a whole-current termination. | P2 | Regional scope explicit; independent gate/continuity review remains. |
| CURRENT | Countercurrent and undercurrent need separate layer identities. | P3 | Null-length proposals; no undercurrent direction assumed. |
| CURRENT | Uniform offsets cannot establish uniform physical uncertainty. | P3 | Protocol M07 and consistency section distinguish editorial sensitivity. |
| SOUNDER | Source year differs from DOI suffix. | P3 | Alory publication date 8 January 2021 recorded. |
| SOUNDER | Earliest EAC retrieval date missing. | P3 | Source rechecked today; original date not fabricated; metadata revision explained. |
| SOUNDER | An automated audit cannot validate source meaning. | P3 | Protocol enumerates remaining reviewer judgments. |
| CHART | Coarse land clearance does not validate a shelf/core axis. | P2 | Independent physical correspondence gate retained. |
| CHART | Initial endpoint annotation overlapped legend. | P3 | Expanded view box; regenerated and visually inspected. |
| CHART | NASA and state joins can imply physical identification. | P3 | Display-only roles retained; C3 context and ETRA/GUIN crossings. |
| BEACON | A route length can be mistaken for whole-current length. | P3 | Scope beside estimate; protocol M01/M09/M13. |
| BEACON | Rules were scattered through progress history. | P3 | Versioned protocol, atlas summary and audit links added. |
| BEACON | Proposals can imply completed inventory expansion. | P3 | Eight proposals remain outside canonical inventory. |
| HARBOR | Rules must be accessible in atlas. | P3 | Semantic heading, prose summary and descriptive links. |
| HARBOR | Figure labels need legibility without colour. | P3 | Dash/text retained; inspected revised SVG. |
| HARBOR | Expanded route page needs mobile checks. | P3 | Full browser suite passes including 320 px reflow. |
| KEEL | Repeated computation must be auditable. | P3 | 29 input/generator/map/tile pins and 2052 scenario recomputations pass. |
| KEEL | Audit must reject invalid metadata and corrupted numbers. | P3 | Two negative test groups cover provenance/admission/distance/envelope corruption. |
| KEEL | New route changes ordering bounds. | P3 | 26 comparison rows; Zeehan positions17-26; updated browser assertions pass. |
| LOGBOOK | Convention changes need explicit revisions. | P3 | Protocol versioning requires impact assessment and re-audit. |
| LOGBOOK | Rules need a repeatable batch gate. | P3 | Audit command and generated hash-pinned report documented. |
| LOGBOOK | Internal review is not scientific admission. | P2 | Independent and canonical/publication gates remain open. |

Seven roles; 21 findings; zero P1, three P2, eighteen P3.
APPROVED-WITH-CONDITIONS for local editorial review. Scientific endpoint,
physical correspondence and canonical admission conditions remain open.
Three key amendments: regional weakening-gate scope; versioned common rules
with current-specific sensitivity choices; executable conformance audit that
explicitly leaves scientific judgments for reviewers.

Verification: 14 focused tests, full almanac checker and full Chromium browser
suite pass. All 29 candidates/2052 scenarios pass protocol audit; eight proposed
identities absent from pinned ledger with null nonranked lengths. Revised SVG
inspected with annotation overlap resolved. Eleven published ranks unchanged.

## Enforcement follow-up

The existing 21 findings and remaining scientific conditions still apply.
KEEL amendment: reconstruct every scenario from the declared Cartesian grid,
reject missing/duplicated/nonfinite results and invalid calendar dates; compare
all source metadata with pinned input. Catalog runs audit before output write,
then pins protocol/audit hashes. A mocked audit rejection proves no catalog
write occurs. SOUNDER/LOGBOOK amendment: reproducible conformance receipts now
link catalog to its protocol version and exact audit. CURRENT/CHART/BEACON/
HARBOR boundaries unchanged: no physical, scientific or presentation claims
expanded by this software gate.

Verification: 17 focused tests and full almanac checker pass. Successive catalog
and audit builds byte-identical; protocol and audit pins match their files.
Browser surface unchanged by this follow-up; prior full browser verification
above applies. All 29 reports/2052 scenarios still pass. No published rank or
canonical identity change. Remaining P2 conditions stay open.
