---
skill: roles-check
topic: south-indian-front-level-source
date: 2026-10-22
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Supplementary source and conditional temperature-conversion review

Internal review through the seven relevant installed role lenses: CURRENT for
physical support, SOUNDER for custody, CHART for source-versus-boundary meaning,
BEACON for interpretation, HARBOR for later equivalent access, KEEL for exact
reproduction, LOGBOOK for the continuing batch. ORBIT is inapplicable. This is
not an independent scientific review or approval of a measured current width.

| Role | Finding | Severity | Resolution / condition |
|---|---|---|---|
| CURRENT |100m/200m criteria cannot be inferred from15m/1000m. | P1 resolved in selection | Exact native indices19/22 supplement the original source without changing it. |
| CURRENT | Pressure and temperature reference are not directly observed by this source. | P1 resolved in method/scope | Use negative depth, explicit zero dynamic height/geopotential, and recorded ITS-90 assumption; no historical scale equivalence claimed. |
| CURRENT | Property brackets do not identify velocity edges or SAF salinity-minimum descent. | P2 retained limit | No named front/current, width, length, axis or footprint admitted; later classification requires its own method. |
| SOUNDER | New source values require an earlier immutable declaration. | P1 resolved | Selection/preflight and operator/protocol/dependency pins precede field acquisition; existing values prevent declaration. |
| SOUNDER | Additional layers could silently alter dates or packing. | P1 resolved in tests | Same363 timestamps, earlier grid, masks, Float32 packing and calendar quota enforced; wrong support rejected. |
| SOUNDER | GSW can silently clamp invalid negative salinity. | P1 resolved in tests | Reject negative common-valid SP before conversion; retain missing cells and record units/assumptions. |
| CHART | A new profile could be mistaken for current occupancy. | P1 resolved in scope | No current outline or occupied-state geometry generated. |
| CHART | Raw and derived temperature need distinct labels/units. | P2 condition for presentation | Raw remains in-situ; derived key explicitly names0dbar and the ITS-90 assumption. Actual later visual checks required. |
| CHART | Existing profiles must not silently change source or depths. | P1 resolved | Separate selection, operator, schemas and directory; old15m/1000m view unchanged. |
| BEACON | Filling vertical support could look like filling a physical width. | P1 resolved | Protocol and batch retain all physical-admission gates closed. |
| BEACON | An old climatology is not reproduced by a2013 model year. | P1 resolved | Explicit model-year comparison and historical/reference limitations. |
| BEACON | Declaration/tests alone cannot prove acquisition success. | P2 condition | Batch separates fourteen passing focused tests from pending actual source/derived/UI results. |
| HARBOR | Added depth/derived choices need equivalent text and tables. | P2 condition for presentation | Require updated native-depth controls, units and complete values before claiming visual delivery. |
| HARBOR | Failure and missingness must stay visible beyond color. | P1 resolved in contract | Nullable means, common-day counts, eligibility and explicit failure status retained. |
| HARBOR | New-layer keyboard/phone behavior is unverified. | P2 condition | Existing view remains unchanged; new actual browser/navigation/reflow gates required later. |
| KEEL | Partition changes could drop or duplicate days. | P1 resolved in tests/operator | Entire cohort compared to the old selection; at most three dates per request; exact monthly time vector required. |
| KEEL | Converting monthly mean inputs is not mean daily conversion. | P1 resolved in tests | Daily paired conversion before means; nonlinear counterexample and common-mask/eligibility regression pass. |
| KEEL | Old GSW web values are not exact references for a newer salinity atlas. | P1 resolved in test | Use3.6.23's full MATLAB check cast and supplied conformance bound; strict canonical replay remains a distinct future gate. |
| LOGBOOK | Existing published source/diagnostic custody must survive new work. | P1 resolved in declaration | Pin both earlier diagnostics and old source/dependencies; no back-edit or reacquisition. |
| LOGBOOK | Resource recovery must preserve original inputs. | P1 resolved in policy |1GiB acquisition floor; no original deletion or weakened engine/full-suite gates. |
| LOGBOOK | User requested one continuing review batch. | P1 resolved in scope | Same branch/draft PR83; no separate PR or main merge. |

Twenty-one findings, no unresolved P1 for the declared supplementary acquisition.
Verdict: **APPROVED-WITH-CONDITIONS** for acquisition and source-method work.
Actual source completion, offline reconstruction, derived portability and
accessible presentation remain required before those milestones can be claimed.
Physical measurement limits remain open across all roles.
