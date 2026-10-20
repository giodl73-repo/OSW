---
skill: roles-check
topic: eac-section-core-spans
date: 2026-10-20
source_commit: 82c290a8163e2978ff1cd1dec81073e231113273
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# EAC section-core diagnostics: internal review

Repository lenses, not independent scientific peer review. Scope: declared
operator, every dated outcome, source custody, diagrams, query contracts,
shared atlas/seasons/query UI and source-store loading. ORBIT is excluded
because this batch makes no planetary comparison.

## CURRENT — physical interpretation

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | A section-normal velocity core does not establish a flow-normal physical width. | P2 | Protocol projection, exact boundary cells and summary scope flags | Keep distances along section, local alignment context and physical-width admission false; implemented. |
| 2 | Success sets change with peak threshold and supplied-magnitude scenario. | P2 | Nine outcomes per date; primary2883resolved/887unresolved | Preserve all33930attempts, monthly denominators and conditional-statistics language; implemented. No sensitivity extrema as annual ranges. |
| 3 | Bottom zeros, weak flow and missing data have different meanings. | P2 | Excluded bottom<=100m,0.3m/s gate,629missing dates | Preserve three failure classes and one-sided edges; never infer zero width or substitute another lobe; implemented and known-case tested. |

## SOUNDER — source identity

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Derived fields must remain traceable to original vectors and coordinates. | P2 | Protocol, report input pins, original source pointers and peak components | Freeze subset/quality/query contract, preserve all original dates and fields; implemented. |
| 2 | Supplied uncertainty does not specify covariance or a confidence convention. | P2 | Algebraic projected-magnitude scenarios and source metadata | State deterministic sensitivity and independent peak selection, not statistical bounds; implemented. |
| 3 | The initial compass label disagreed with the actual source bearing. | P2 | Bearings near81degrees; initial protocol hash and correction note | Correct description transparently. All geometry, profiles, summaries and numeric outcomes verified identical; completed. Original QC/mapping disagreements remain unresolved. |

## CHART — geographic/visual fidelity

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Map markers could be mistaken for current edges. | P2 | Two within-cell interpolated section rings in shared map | Label approximate sampling-section intersections, retain cell/distances in text and draw no geographic polygon; implemented. |
| 2 | Successful-only plots could hide truncated or weak cases. | P2 | All-date figure, selected missing/domain/weak UI cases | Plot every primary outcome, preserve denominators and fixed examples0/1885/3769; implemented. Final example remains weak. |
| 3 | Sensitivity changes should not rescale the chart deceptively. | P3 | Summary fixed component domain from all projected magnitude cases | Keep one domain and explicit m/s/section-km units; implemented. |

## BEACON — public meaning

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Readers may repeat the conditional numerical extent as an annual width range. | P2 | Plan, summary limitations and selected-case readout | Explicitly reject that inference beside plot and statistics; implemented. |
| 2 | Interpolation-cell support is not instrument uncertainty. | P2 | Boundary-cell brackets, mapped-grid description | Preserve the distinction beside every resolved span and its source cells; implemented. |
| 3 | The extra outcomes do not add independent source observations. | P3 | Dashboard preserves time samples, dates and all28series | Count derived dated diagnostics separately and retain source-method qualifications; implemented. |

## HARBOR — equivalent access

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Scenario, threshold and date selection must work without pointer input. | P2 | Native select controls, recorded-day navigation, focusable chart region | Actual browser gate covers all nine cases and320px keyboard scrolling; required before publication. |
| 2 | Color cannot be the only crossing/failure explanation. | P2 | Live textual edge reasons, source indices, bracket distances and exact-record link | Retain textual alternatives for green rings/brackets, orange exclusion and unresolved cases; implemented. |
| 3 | Animation must preserve original recorded dates and reduced motion. | P3 | Existing source playback/manual controls reused without synthetic frames | Retain reduced-motion behavior and month-end stop; original-source browser gate checks regression. |

## KEEL — reproducibility and execution

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | Loading every large Value tree caused an actual initial browser timeout. | P2 | Two retained failed attempts; source request90second timeout | Authenticate all source bytes/root/schema/complete JSON and numeric range, then build requested trees lazily. Rust tests include1e400 rejection and signed-zero/null preservation; actual browser recheck required. |
| 2 | The compact scene and full corpus require independent admission. | P2 | Frozen summary/operator/figure contract and checked source catalog | Test changed/coherently rebound summaries, invented widths and independently changed corpus records in native and actual WASM; durable gate registered. |
| 3 | Focused Rust/Python checks do not certify a whole revision. | P2 | Source/operator tests; live clean82c290asuite predates new work | Keep full-gate commit/scope explicit, preserve failures and verify committed pins.30minute aggregate budget for two complete EAC matrices changes no90second interaction assertion. |

## LOGBOOK — custody and publication

| # | Finding | Severity | Evidence | Recommendation / disposition |
|---|---|---|---|---|
| 1 | One PR per gap contradicts the user's workflow. | P2 | Continuing branch and draft PR83 | Commit/push only into PR83, without main merge; implemented workflow. |
| 2 | A45.4MBcorpus must not be duplicated into an already large main packet. | P2 | Separate checked corpus and0.462MBsummary; packet89,712,747bytes | Keep raw profiles in the source index and compact scene in Rust; implemented. |
| 3 | This batch leaves broader measurement gaps open. | P3 | Preserved155width rows/81owners,11lengths,76routes and explicit remaining work | Publish exact progress, not complete measurement coverage or physical-width approval. |

## Synthesis

Seven roles,21findings:0P1,17P2,4P3. **APPROVED-WITH-CONDITIONS** for
exploratory section diagnostics; no physical-width or annual-range approval.
CURRENT, SOUNDER, CHART and BEACON agree that a source-section crossing is not
a mapped physical current edge. KEEL and LOGBOOK agree that running gates are
not passed gates and that the earlier tested commit cannot certify new changes.

Three amendments:

1. Keep all failure classes, one-sided cell support and original timestamps;
   correct the compass description without changing numerical decisions.
2. Bind the complete corpus independently from the compact scene, and reduce
   startup memory through deferred query-tree construction while preserving
   complete source authentication and JSON numeric validation.
3. Register real-browser checks, preserve the original source regression,
   verify every committed input and publish only through existing PR83.

Publication conditions: actual UI/source pagination and corruption gates,
original-source regression, preservation and committed-byte checks must pass.
Full clean-suite status must identify its tested commit. Scientific physical-
width validation, annual ranges and complete current-length coverage remain open.
