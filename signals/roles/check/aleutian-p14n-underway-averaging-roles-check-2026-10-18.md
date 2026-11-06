---
skill: roles-check
topic: aleutian-p14n-underway-averaging
date: 2026-10-18
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Contiguous underway averaging review

Direct review through seven repository functional lenses; no independent
scientific peer review or separate agents. ORBIT is excluded because this
artifact makes no planetary comparison. Scope: the new declared operator,
report, tests, figure/receipt and decision record; production query/card
registration is not part of this research-only batch.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Both sides remain unresolved in all fixed experiments. | P3 | Report: 54 relative-peak and 72 displacement scenarios. Preserve null endpoints; no width admission. |
| CURRENT | Eastward component and moving footprints do not define flow-normal physical width. | P3 | Operator interpretation and report flags explicitly preserve this limit. Retain beside every future display. |
| CURRENT | The paper's uncertainty estimates do not calibrate these clipped averages. | P3 | Decision uncertainty section; no error propagation or width CI. A future composite needs a separate temporal assumption. |
| SOUNDER | Overlapping nominal ensembles could double-count temporal support. | P2, resolved | Exact union segmentation averages simultaneously active means once; independent analytic overlap test checks 900 covered/300 overlap seconds. |
| SOUNDER | An incomplete last window could falsely pass if its denominator shrinks. | P2, resolved | Full declared duration remains the denominator. Synthetic terminal-bin test retains 300/1800 coverage as ineligible. |
| SOUNDER | New averaging is distinguishable from the provider's earlier processing. | P3 | New report sets OSW temporal averaging true; historical native report remains unchanged and false. Source, verifier and protocol pins are explicit. |
| CHART | Horizontal support bars resemble statistical error bars. | P2, resolved | Caption, SVG description and receipt explicitly label contributor footprints, not uncertainty. No physical edge rendering. |
| CHART | Unqualified title could imply every averaging method fails. | P2, resolved | Final title says 'tested averages'; decision limits conclusion to these declared operators. |
| CHART | Plotting a connected transect could conceal station stops. | P3 | Plot uses individual means/footprints without joined runs; algorithm independently rejects cross-run boundaries. Preserve this grammar. |
| BEACON | A negative measurement is easy to mistake for completed width coverage. | P2, resolved | Decision begins with no new width and separates the answered operator question from the unresolved physical-width gap. |
| BEACON | Whole-reach bin counts could be mistaken for branch-only counts. | P2, resolved | Table headings and adjacent prose state 40-48 N reach; branch windows remain separately explicit. |
| BEACON | Earlier approximate 100/80 km values could fill missing new endpoints by implication. | P3 | Decision explicitly prohibits substituting the earlier hourly component spans. Preserve separate evidence classes. |
| HARBOR | Cutoff categories must remain recoverable without color. | P3 | Circle/square/triangle markers and labeled legend; visual review confirms readable text. |
| HARBOR | SVG paths alone do not expose the scientific claim to assistive technology. | P2, resolved | SVG role/title/description IDs are added and tested; decision table and full numeric JSON provide alternatives. |
| HARBOR | This image is not yet part of keyboard/mobile card navigation. | P2, open | Marked research-only in decision. Before card publication, register the source/figure and run actual keyboard, narrow-view and reduced-motion checks. |
| KEEL | Source drift could change averages without an obvious failure. | P3 | Three exact frozen input pins plus native report verifier; mutation test rejects before field access. |
| KEEL | A permanently-null implementation could falsely pass only actual-data checks. | P2, resolved | Synthetic resolved two-sided geometry and independent 22.226355 km expectation exercise the positive path. |
| KEEL | The already-running full gate covers a predecessor. | P2, open | Decision names 25b286e as predecessor; 8 focused tests/3 subtests pass for the successor. Require later combined gate before release. |
| LOGBOOK | User requested one continuing PR. | P3 | Keep branch codex/current-measurement-gaps and draft PR83; no merge or new PR. |
| LOGBOOK | Query/inventory counts must not increase for unregistered artifacts. | P3 | Production packet/registry/index stay unchanged in this batch; counts remain 330 indexed docs and 155 widths. |
| LOGBOOK | Native full gate and hosted acquisition failures require accurate scope. | P2, open | Preserve running predecessor receipt and inspected Reading connection-refused CI logs; do not claim successor full or hosted green. |

## Synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 11 (8 resolved, 3 open).
P3 notes: 10. **APPROVED-WITH-CONDITIONS for a research-only addition**;
not an atlas release or physical-width admission.

Top finding: no two-sided result may be created by bridging station stops.
CURRENT, SOUNDER and CHART agree on preserving the missing boundaries and
their sampling context. KEEL and LOGBOOK agree that predecessor full checks
cannot certify this later operator.

Three amendments applied: (1) exact union/time support and full terminal
denominators, (2) qualified visual claim plus accessible/data alternatives,
(3) explicit pending registration/full-gate status. Open conditions are
future query/card accessibility integration, successor combined validation,
and truthful hosted acquisition status at release.
