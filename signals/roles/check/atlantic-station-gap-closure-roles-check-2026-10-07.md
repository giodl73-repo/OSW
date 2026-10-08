---
skill: roles-check
topic: atlantic-station-gap-closure
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Atlantic station gap closure review

Internal seven-role review of source reconciliation, archive recovery, source custody and sampling maps. These lenses cover physics, provenance, cartography, public explanation, accessibility, reproducibility and publication. This is not independent scientific peer review.

| Role | Finding | Severity | Recommendation / disposition |
|---|---|---|---|
| CURRENT | Station date reconciliation cannot establish current edges. | P2 | Resolved: boundary pairing remains unresolved and footprint/state/annual eligibility stays false. |
| CURRENT | Cruise-wide cast selection differs from the paper model subset. | P3 | Explain the subset distinction; preserve 143 archive casts versus 112 paper stations for CD171. |
| CURRENT | No published width, length or seasonal range changes here. | P3 | Keep corrected sampling timestamps separate from dimensional admissions. |
| SOUNDER | A year substitution would erase contradictory original metadata. | P2 | Resolved: preserve all 46 original 2005 dates and add independently matched sampling fields from the corrected product. |
| SOUNDER | Three product times differ by one minute. | P3 | Retain both timestamps and signed differences; use corrected-product time beside corrected-product date. |
| SOUNDER | Matching requires identity, position and timing corroboration. | P3 | Reject missing/extra casts, identity/date/position differences and time differences above one minute. |
| CHART | Map dots could be mistaken for a diagnosed current boundary. | P3 | Draw unconnected sampling points, keep OSW boundaries as background context. |
| CHART | The CD171 archive label Atl32N differs from paper A03/36 N. | P3 | Retain both labels; map actual positions rather than deriving geography from the label. |
| CHART | Coordinate precision is not coordinate accuracy. | P3 | Keep original coordinates and null datum/uncertainty; no new distances. |
| BEACON | Readers need the timestamp correction explained adjacent to maps. | P3 | Show corrected-product explanation and exact reconciliation query link. |
| BEACON | Recovering all 30 sampling contexts does not close all atlas gaps. | P3 | Report remaining current-edge, length, width and eddy-footprint work separately. |
| BEACON | Primary provider and edition should remain recoverable. | P3 | Archive exact bottle edition, source summary and acquisition/citation receipts. |
| HARBOR | Timestamp alternatives must be accessible without hover. | P3 | Keep semantic station tables and source-record/reconciliation query links. |
| HARBOR | Selection changes need explicit loading/error/scope announcements. | P3 | Retain labeled selector/status region and current-switch cleanup. |
| HARBOR | Narrow layouts must preserve the source explanation. | P3 | Keep 320 px viewport and keyboard-scroll browser checks. |
| KEEL | Independent products need exact local reproducibility. | P2 | Resolved: pin both sources, verify byte/hash, rebuild exact reconciliation and require it in the checked index. |
| KEEL | Alternative metadata pairings must fail closed. | P3 | Add five mutation cases and missing/extra-cast tests; preserve unchanged source events. |
| KEEL | A disk-full build is terminal and needs a verified recovery. | P3 | Remove only disposable workspace incremental cache, then rebuild and test the final engine. |
| LOGBOOK | Protected main and exact-head CI are not complete. | P2 | Open condition: required publication gates must pass before landing the stack. |
| LOGBOOK | The prior station batch receipt describes its earlier source snapshot. | P3 | Keep it as historical evidence; record this newer 18-cruise/30-context batch separately. |
| LOGBOOK | Archive line endings must survive cross-platform checkouts. | P3 | Preserve CSV/TXT source bytes with scoped .gitattributes and verify committed blobs. |

## Synthesis

Seven roles reviewed. P1: 0. P2: 4 (three resolved, protected-main publication open). P3: 17. APPROVED-WITH-CONDITIONS.

CURRENT and CHART agree that recovered station metadata is sampling context, not current edge evidence. SOUNDER and KEEL require independent product pairing rather than a silent year edit.

## Amendments

1. Preserve original summary events and attach separately sourced sampling timestamps with row pointers.
2. Restore CD171 sampling context while retaining the archive/paper label and model-subset distinctions.
3. Verify corrected-source mutations, exact regenerated index, shipped-WASM maps and committed archive bytes before publication.
