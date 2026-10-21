---
skill: roles-check
topic: eac-section-core-readback
date: 2026-10-20
source_commit: 16c8bb32c2030fe21b0d0ef04c3520618014a4a8
roles_used: [CURRENT, SOUNDER, CHART, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# EAC section-core readback review

Internal functional review using `.roles/ROLE.md`, not external peer review.
Selected lenses cover physical meaning, source identity, regenerated plots,
executable reconstruction and the accuracy of publication status.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Readback before peak selection could change admission. | P2 resolved | Full-precision operator functions remain unchanged; near-floor test preserves a below-floor failure even when its printed component rounds to0.3. |
| CURRENT | Supplied-component allowances are not confidence intervals. | P2 resolved | Only derived allowances are serialized; original uncertainty arrays and all scope flags remain exact. |
| CURRENT | Smaller decimal discrepancies do not justify physical widths. | P2 resolved | Physical widths, annual ranges, verified boundaries and ranks remain unadmitted. |
| SOUNDER | Broad numeric rounding could corrupt original peak components. | P2 resolved | Explicit field list excludes peak UCUR/VCUR and source coordinates/depths; original source JSON/NPZ and quality products remain byte-exact. |
| SOUNDER | Changes require a reproducible declaration. | P2 resolved | Helper validates protocol SHA; report pins protocol/helper/producer; changed-protocol tests reject. |
| SOUNDER | Derived values must remain traceable to the original calculation. | P2 resolved | Mocked final-stage audit reproduces the full preceding report exactly except producer identity; all33,930 case statuses and indices preserved. |
| CHART | Rebinding old plots could hide changed inputs. | P2 resolved | Both plots actually regenerated; core PNG has four one-level pixel changes, calendar assets byte-exact; both inspected visually. |
| CHART | Missing dates must remain in denominators. | P3 confirmed | All3,770 source dates and887 unresolved primary cases retained; calendar quantities and membership unchanged. |
| CHART | Browser controls and narrow layouts need runtime proof. | P2 resolved | Actual-WASM3770-profile/9-case/10-packet/2-index/source-link/320px checks and all calendar groups pass. |
| KEEL | Tolerant comparisons could conceal later errors. | P2 resolved | Exact object/encoded checks retained; field enumeration leaves future unknown fields untouched. |
| KEEL | New readback pins need adversarial coverage. | P2 resolved | Add helper/protocol hash corruptions to existing native/actual-WASM rejection cases; unit tests reject invalid selected values and wrong schema. |
| KEEL | Browser selector was ambiguous after calendar integration. | P2 resolved | Select the intended outcome summary by exact accessible text; keep keyboard/image assertions. |
| LOGBOOK | Seventeen-report Linux success is not eighteen-report success. | P2 condition | Keep independent Linux failure explicit until current repair's eighteen-target job is inspected. |
| LOGBOOK | Earlier full-suite results must remain tied to their scope. | P2 resolved |32 focused tests/4 subtests,81 Rust tests and local18-report rebuild are this repair's checks; older774 full suite is distinct. |
| LOGBOOK | User requested accumulated work in one PR. | P3 confirmed | Continue codex/current-measurement-gaps / draftPR83; no new PR or main merge. |

Five roles; no P1; one remaining P2 independent integration condition. Verdict:
APPROVED-WITH-CONDITIONS for continued draft work. Amendments implemented:
declare narrow final-field precision, audit full-precision/source/decision
preservation, and regenerate plots plus every dependent checksum in order.
