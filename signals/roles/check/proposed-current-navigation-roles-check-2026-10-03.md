---
skill: roles-check
topic: proposed-current-navigation
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 1
verdict: APPROVED-WITH-CONDITIONS
---
# Proposed-current navigation review

Internal editorial review: CURRENT for physical meaning, SOUNDER for identity
provenance, CHART for visual arrival, BEACON for labels, HARBOR for equivalent
access, KEEL for load/order/history checks, LOGBOOK for status. ORBIT not applicable.
Reviewed input relations, builder validation, generated notes, browser navigation,
rendered mobile focus and targeted test results.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Pending relation could imply a physical connection | P3 | Links labelled proposed separate current; no connectivity added. |
| CURRENT | Navigation might silently borrow an axis | P3 | Aleutian route/width remain absent. |
| CURRENT | Proposed width might become canonical | P3 | Proposal relation carries ID/name only. |
| SOUNDER | Labels could drift from pending records | P3 | Builder resolves labels from proposal inventory. |
| SOUNDER | Unknown or duplicate proposal links could persist | P3 | Validator rejects missing/canonical/duplicate/malformed references. |
| SOUNDER | Generated empty metadata could light up all notes | P3 | Only notes with related proposals get resolved field. |
| CHART | Arriving card could be below viewport | P3 | Direct links reveal heading after asynchronous render. |
| CHART | Final short card cannot align at viewport top | P3 | Visible page-end heading accepted without artificial space. |
| CHART | Return must preserve global entry point | P3 | Back to current atlas invokes existing global navigation. |
| BEACON | Pending records could look like released currents | P3 | Proposed separate current wording and admission text retained. |
| BEACON | Users need reusable current-specific addresses | P3 | Card link is explicit and shareable. |
| BEACON | Original link did not focus proposed card | P2 (addressed) | Card targets now included in fragment navigation. |
| HARBOR | Section was not focusable on arrival | P3 | Negative tab index and visible outline supplied. |
| HARBOR | Pointer-only relation would limit access | P3 | Keyboard Enter relation opens/focuses proposed target. |
| HARBOR | New controls might break reflow | P3 | 320 px repeated-link check and inspected focus screenshot. |
| KEEL | Independent loads could move target after arrival | P3 | Both callbacks reveal current fragment; delayed-order checks pass. |
| KEEL | Browser Back could restore URL without focus | P3 | All 23 proposal Back paths verified. |
| KEEL | Changes could regress mapped cards | P3 | Two existing mapped deep links still pass. |
| LOGBOOK | Link support might imply identity admission | P3 | Counts and editorial status unchanged. |
| LOGBOOK | Verification failure could be concealed | P3 | Page-end assertion correction recorded. |
| LOGBOOK | Focused checks cannot prove a full release | P3 | Full repository release gate remains open; no publication claimed. |

21 findings: no P1, one addressed P2, 20 P3 conditions. Approved for editorial
inspection. BEACON/HARBOR agree that a shared URL must reveal and focus its
actual card. Amendments: made proposals fragment targets; added share/return
links; validated and labelled pending scope relations. Twelve dashboard tests,
31 scope previews, all 23 proposal navigation paths and delayed-load checks pass.
Scientific identity admission and full clean-checkout release gates remain open.
No canonical measurement, ranking, commit, push or publication action performed.
