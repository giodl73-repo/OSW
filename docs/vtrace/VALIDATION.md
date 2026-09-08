# OSW Validation Plan

Status: settled at native-role fixed point, 2026-09-07

## Scope

Repo: OSW — Ocean States of the World

This plan defines how OSW will determine whether the implemented atlas is
useful, understandable, scientifically disciplined, accessible, reproducible,
cartographically honest, and safe to promote. It operationalizes the eight
Mission validation scenarios without claiming that any has already run.

Validation asks whether OSW solves the intended human and research problem.
Verification remains responsible for conformance to requirements, interfaces,
invariants, schemas, commands, and fixtures. A passing automated surrogate
cannot substitute for a required human, independent-scientist, rendered-map,
or staged-transition validation.

All nine work packages remain proposed. This document authorizes no
participant contact, data collection, implementation, commit, push,
deployment, release, or external endorsement.

## Validation principles

1. The consequential task is observed without coaching through the answer.
   Training, prompts, interventions, and retries are recorded separately.
2. Finding recall and limitation recall are separate outcomes. A visually
   attractive journey fails if it causes a stronger unsupported conclusion.
3. Critical misconceptions have a zero-tolerance gate: budget closure or
   causation from the worked partial comparison; motion as proven delivery;
   schematic borders as uniquely physical; sea ice as absent subsurface ocean;
   Earth/gas-giant material equivalence; or OSW as forecast, navigation,
   intervention, peer-review, endorsement, or release authority.
4. A result may be `pass`, `fail`, `blocked`, or `not_applicable` only with a
   controlled rationale. “Conditional pass” is not a release pass.
5. Null, contrary, unavailable, degraded, and participant-confusion outcomes
   are evidence. They are not removed to protect the preferred story.
6. Independent reviewers advise within a named lens; participation never
   implies endorsement, institutional approval, or release authority.
7. Validation artifacts bind immutable product/evidence identities and avoid
   raw personal data. The static public atlas retains its no-collection rule.

## Validation scenario matrix

| ID | Actor and need | Controlled workflow | Hard acceptance criteria | Evidence | State |
|---|---|---|---|---|---|
| VAL-SCN-OSW-001 | Curious readers must understand the worked heat event and its principal limit; educators must be able to reuse it without dropping the caveat. | From the public entry, five uncoached participants who did not build the slice follow event → surface → boundary → column → motion, then explain what happened and what remains unresolved. Separately, one educator/science communicator uses the stable link, text alternative, source, and caveat to prepare a short explanation without coaching. | At least 4/5 readers independently reach the final receipt and accurately state one principal finding and the strongest limitation; 5/5 avoid closure, causation, and motion-as-delivery claims. The educator preserves evidence class, source route, and strongest limitation. Any critical misconception after the completed journey fails the scenario. | Task paths, state/receipt IDs, prompt-free recall coded against a frozen rubric, educator reuse artifact, interventions, completion and misconception counts. | blocked until WP-OSW-004 plus VFY-OSW-004/008–010/013/019/020 pass |
| VAL-SCN-OSW-002 | Research auditors must identify and challenge an exact quantitative claim. | Two auditors, including at least one person who did not author the analysis, choose quantitative scenes, recover source/variable/time/depth/support/transformation/rights and run the documented local path or explain a bounded divergence. | Both reach the controlling receipt without reverse-engineering prose, identify every applicable identity/limitation field, and reproduce the declared comparison or produce a traceable explained divergence; zero live-provider dependency in the default path. | Artifact/receipt hashes, commands/environment, field audit, reproduced/different result, explanation and unresolved issues. | blocked until WP-OSW-001/004 and VFY-OSW-002–006/008/012–014/019/020 pass |
| VAL-SCN-OSW-003 | Keyboard, screen-reader, low-vision, motion-sensitive, touch, and narrow-screen readers need equivalent meaning. | Execute the full primary journey with keyboard only; one screen-reader configuration; 200% and 400% zoom; 320 CSS-pixel reflow; reduced motion; and touch emulation or device. At least one participant routinely uses the tested screen reader, and at least one routinely uses keyboard/zoom or an equivalent non-pointer access path; one person may satisfy both. An independent accessibility reviewer observes or separately audits. | Every primary action completes with visible/stable focus and no trap; visual, programmatic, announced, and text states share identity/finding/limitation; no unique meaning requires color/hover/motion; map/finding/limitation/controls/receipt remain jointly usable without two-dimensional page scrolling; no unexpected focus move. If routine-user participation is unavailable, the scenario remains blocked rather than replaced by simulation. | Browser/AT/input/version matrix, focus sequence, announcements, state digest, text output, reflow/request captures, defects and retest IDs. | blocked until WP-OSW-002–005 and VFY-OSW-007–012/019/020 pass |
| VAL-SCN-OSW-004 | Cartographic reviewers must recognize what each projection and boundary can and cannot support. | A reviewer who did not build the view compares Oceanic Mollweide, province, local-event, antimeridian, polar, coastline, land, ice, missing, and out-of-domain cases using map and text forms. | Reviewer correctly identifies projection/aspect, scale/comparison limits, boundary class, evidence/quantity, support states, seam/polar behavior, and uncertainty/unavailable status for every applicable case; no false object, land overlap, hidden discontinuity, or promoted schematic boundary remains. | Frozen map-family applicability inventory, reviewed view IDs/hashes, structured beliefs/defects, visual/text comparison and disposition. | blocked until WP-OSW-003 and VFY-OSW-005/009–012/019/020 pass |
| VAL-SCN-OSW-005 | Zoning reviewers must be able to reject an attractive but physically weak border. | CURRENT and CHART independently inspect at least one known contradiction case and one supported/control candidate without seeing the proposed retain/merge/split/move/demote outcome first. | The attractive exchange-poor/depth-inconsistent candidate cannot advance; all persistence/exchange/retention/convergence/vertical/gate diagnostics and unavailable/contrary states remain visible; reviewers can select a non-status-quo disposition without preserving region count. | Frozen candidates/method, diagnostic receipts, blind-first dispositions, disagreements, final rationale and boundary-class result. | blocked until WP-OSW-007 and VFY-OSW-005/009/012/015/019/020 pass |
| VAL-SCN-OSW-006 | Maintainers must reproduce evidence and recognize truthful release state without private knowledge. | A maintainer who did not implement the package uses a fresh temporary checkout with outbound provider access denied, follows public docs, runs L1, regenerates or integrity-checks one supported artifact from each admitted family, and rehearses status reconciliation without deployment. | Documented commands suffice; every admitted family succeeds or yields its declared bounded unavailable result; no undeclared network/secret/private path or tree mutation occurs; maintainer identifies released/preview/experiment/research/degraded state and every intentional hold correctly. | Checkout/commit/environment, network policy, before/after manifest, family command/results, status packet, issues/interventions and role decision. | blocked until WP-OSW-001/005/009 and VFY-OSW-001–003/006/012/013/017/019/020 pass |
| VAL-SCN-OSW-007 | Readers must learn from an Earth/gas-giant comparison without inferring equivalence. | Five uncoached readers inspect one mechanism-supported pair and one resemblance-only pair, then state the shared property, important physical/observational differences, and what would weaken the analogy. | At least 4/5 identify the intended shared mechanism/property and at least two material differences plus one weakening outcome; 5/5 avoid material equivalence, cloud-color/full-depth-heat, and transferred-causation claims; ORBIT/CURRENT/SOUNDER accept the underlying comparison records. | Pair identities/receipts, prompt-free coded recall, order randomization, differences/falsifier counts, expert dispositions. | blocked until WP-OSW-008 and VFY-OSW-002–004/009/012/016/019/020 pass |
| VAL-SCN-OSW-008 | Scientists must be able to challenge the heat story and retain null or contrary evidence. | At least one scientist who did not author the primary result applies a frozen alternative depth, time, product, missing-term, or control test and compares it with the primary claim. | Alternative is independently traceable; method/support differences remain explicit; result may strengthen, weaken, reverse, or remain unavailable without relabeling the residual; any generalization states the tested scope and unresolved terms. | Frozen challenge, inputs/method/tolerances, result/receipt hashes, comparison, contrary/null ledger, CURRENT/SOUNDER disposition. | blocked until WP-OSW-006 and VFY-OSW-002/004–006/012/014/019/020 pass |

The small reader-session counts are formative release gates, not population
estimates or claims of statistical generality. A failed critical-misconception
gate is repaired and rerun with new or clearly separated participants; the
failed evidence is retained.

## Scenario protocol

### Entry packet

Before any session, freeze:

- scenario, participant/reviewer lens, recruitment relationship, and conflicts;
- immutable product commit, hosted/local target, view/state/receipt IDs and
  artifact hashes;
- prerequisite VFY results and open defects;
- task wording, success rubric, critical misconceptions, permitted prompts,
  environment/matrix, and stop conditions;
- consent, recording choice, note retention, redaction, and compensation if
  applicable; and
- facilitator, independent observer/coder where required, and decision owner.

The facilitator may explain task mechanics only as the frozen protocol allows.
Scientific terminology questions and recovery prompts are logged; coached
success is not counted as unassisted success.

Prompt-free reader responses and critical-misconception decisions are coded
independently by two people against the frozen rubric, with at least one coder
not responsible for the tested content. Disagreement is retained and resolved
before the scenario decision; the rubric is not changed after responses are
seen without versioning the protocol and rerunning the affected case.

### Evidence envelope

Each result records:

| Field group | Required content |
|---|---|
| Identity | Validation/scenario ID, protocol revision, product commit, artifact/view/state/receipt hashes, related VFY/FIX/WP/requirement IDs. |
| Conditions | Date, locale, device class, browser/AT/input/version, viewport/zoom/motion/network state, relevant dependencies and source availability. |
| Participant boundary | Pseudonymous session ID, relevant experience band and reviewer lens; no name, contact data, raw account identifier, health/disability disclosure, or unnecessary demographics in the repo. |
| Execution | Start/end, task path, unassisted result, prompts/interventions, errors/degraded paths, focus/announcement/request state where applicable. |
| Outcome | Per-criterion pass/fail/blocked, prompt-free response coding, critical misconception flags, contrary/null/unavailable results, defect IDs and severity. |
| Decision | Scenario disposition, role decisions, owner acceptance where required, rerun trigger, evidence-file checksum and public/internal classification. |

Raw recordings, transcripts, contact information, consent forms, and
participant recruitment records are not committed to the public repository.
If collected, they remain in separately authorized bounded custody with an
explicit retention/deletion date. Repository evidence contains minimal
redacted observations and aggregate counts. Validation tooling adds no atlas
telemetry, cookies, accounts, uploads, or passive user collection.

## Controlled environment matrix

Exact supported browser versions are recorded at execution time rather than
frozen to aging version numbers here.

| Surface | Minimum controlled cases | Acceptance boundary |
|---|---|---|
| Desktop browsers | Current supported Edge, Chrome, and Firefox releases at execution | Primary routes/state/scenes/maps/receipts agree; no browser-specific scientific meaning. |
| Keyboard | Complete primary journey without pointer | Every action reachable; logical order, visible focus, no trap or unexpected focus move. |
| Screen reader | One supported desktop browser/AT pairing, independently reviewed | Names/states/announcements/text alternative convey same accepted state, finding, limitation, loading and error. |
| Zoom/reflow | 200%, 400%, and 320 CSS-pixel-wide case | Map, finding, limitation, controls and receipt jointly usable; no two-dimensional page scrolling or hidden meaning. |
| Motion/color | Reduced-motion plus monochrome/non-color inspection | Equivalent static result; sign/category/confidence/support/selection remain recoverable. |
| Touch | Emulated or physical coarse pointer at narrow and ordinary widths | Primary controls activate without precision targeting or overlap. |
| Network/privacy | Normal local/hosted requests plus enforced scientific-provider denial | Only declared same-origin selected assets; no persistence/collection; degraded path remains useful. |

Contrast and target-size thresholds must be numeric in the execution packet and
approved by HARBOR before the first public-release candidate. Validation does
not accept “looks readable” or browser-default styling as a threshold.

## Scientific and cartographic decision rules

| Domain | Pass requires | Automatic fail or block |
|---|---|---|
| Heat/budget | Independent identities, depth/time/space/reference/support, named tolerance, unresolved terms, alternative/control evidence. | Residual named as process, numerical proximity as closure, crossed products treated as one model budget, unsupported causation. |
| Motion/transport | Evidence ceiling matches velocity/path/section/control-volume quantity. | Motion/path/count/open section presented as delivery, probability, residence, convergence, or regional closure without required evidence. |
| Zoning | Frozen candidate/method, disaggregated diagnostics, contrary/unavailable evidence, revisable outcome. | Visual fit or desired region count promotes a border; missing evidence becomes neutral/pass. |
| Cartography | Applicable projection/scale/support/boundary/uncertainty metadata and equivalent text; edge cases reviewed. | Land/seam/pole/support creates false object; styling widens boundary authority; unsupported metric comparison. |
| Planetary comparison | Independent admitted quantities, shared mechanism/property, regime and observation differences, weakening outcome. | Visual rhyme or cloud appearance alone supports mechanism/full-depth claim; material equivalence implied. |

CURRENT breaks physical disagreements, then SOUNDER for data identity, CHART for
representation, BEACON for public claim, HARBOR for equivalent access, KEEL for
proof, LOGBOOK for status/release, and ORBIT for the remaining planetary lens.
No tiebreaker may overrule a failed higher-priority scientific/data/map domain
or the federated admission rule.

## Performance and release acceptance

WP-OSW-005 must first measure critical-path bytes, request count, selected and
unselected payloads, render/interaction indicators, controlled devices, and
variance. KEEL and HARBOR then propose numeric budgets; the owner records the
accepted values and rationale in the immutable validation packet. Until that
decision exists, performance is `blocked`, not pass, and no unexplained
regression is acceptable.

WP-OSW-009 must discover and rehearse host identity, immutable hosted-commit
proof, primary smoke paths, and atomic or compensating retain/restore. Public
transition requires all applicable scenario passes, verification evidence,
resolved P1/P2 findings, payload/privacy proof, a reconciled candidate packet,
and explicit owner approval. Failed deploy/smoke leaves the prior site and
current/citation metadata unchanged or restored together.

## Acceptance evidence ledger

| Evidence ID | Scenario | Evidence | State |
|---|---|---|---|
| EVID-VAL-OSW-001 | VAL-SCN-OSW-001 | Reader path and finding/limitation/misconception study | target blocked |
| EVID-VAL-OSW-002 | VAL-SCN-OSW-002 | Independent receipt audit and reproduction/divergence packet | target blocked |
| EVID-VAL-OSW-003 | VAL-SCN-OSW-003 | Keyboard/screen-reader/zoom/reflow/motion/touch evidence | target blocked |
| EVID-VAL-OSW-004 | VAL-SCN-OSW-004 | Independent cartographic edge/comparison review | target blocked |
| EVID-VAL-OSW-005 | VAL-SCN-OSW-005 | Blind-first zoning contradiction/control decisions | target blocked |
| EVID-VAL-OSW-006 | VAL-SCN-OSW-006 | Fresh-checkout network-denied reproduction/status rehearsal | target blocked |
| EVID-VAL-OSW-007 | VAL-SCN-OSW-007 | Planetary supported/resemblance reader and expert study | target blocked |
| EVID-VAL-OSW-008 | VAL-SCN-OSW-008 | Independent scientific challenge/null/contrary packet | target blocked |
| EVID-VAL-OSW-009 | all applicable | Performance budget and release-transition acceptance packet | target blocked |
| EVID-VAL-OSW-010 | validation stage | Eight native-role review and fixed-point artifact identity | passed: 8 roles, 0 P1, 16 P2 resolved |

No scenario currently has acceptance evidence. Existing owner visual feedback,
role reviews, automated tests, and research results are inputs—not substitutes
for executing these controlled protocols against the implemented candidate.

## Deferred validation and triggers

| Validation | Why deferred | Risk while deferred | Revisit trigger / owner |
|---|---|---|---|
| VAL-SCN-OSW-001–004 | Guided/state/view implementation does not exist. | Mission usability, access, and map honesty are unproven. | WP-OSW-004 candidate plus prerequisite VFY; BEACON/HARBOR/CHART/CURRENT. |
| VAL-SCN-OSW-005 | Zoning package remains deferred pending stronger transport evidence. | 11/22 organization remains provisional and must not be promoted. | WP-OSW-007 candidate; CURRENT/CHART. |
| VAL-SCN-OSW-006 | Family registry, network-denial, non-mutation, and release reconciler are pending. | Reproduction/release truth is unproven. | WP-OSW-001/005/009 candidate; KEEL/LOGBOOK/SOUNDER. |
| VAL-SCN-OSW-007 | Planetary package remains independently deferred. | Analogies remain explanatory drafts, not validated product claims. | WP-OSW-008 candidate; ORBIT/CURRENT/SOUNDER. |
| VAL-SCN-OSW-008 | New alternative/control/second-case analysis is pending. | Current heat result remains a bounded 0–50 m case, not general mechanism. | WP-OSW-006 candidate; CURRENT/SOUNDER. |
| Numeric performance budget | No accepted hosted integrated baseline. | Public usability regression cannot be adjudicated numerically. | WP-OSW-005 measurements; KEEL/HARBOR/owner. |
| Hosted transition | Host/proof/retain-restore mechanism not settled. | No release readiness can be claimed. | WP-OSW-009 discovery/rehearsal; LOGBOOK/KEEL/owner. |

## Validation-to-mission and package coverage

| Scenario | Mission success | Principal work packages | Principal verification |
|---|---|---|---|
| VAL-SCN-OSW-001 | MSC-OSW-002 | WP-OSW-002–004 | VFY-OSW-004, VFY-OSW-007–010, VFY-OSW-013, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-002 | MSC-OSW-003 | WP-OSW-001, WP-OSW-004, WP-OSW-006 | VFY-OSW-002–006, VFY-OSW-008, VFY-OSW-012–014, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-003 | MSC-OSW-004 | WP-OSW-002–005 | VFY-OSW-007–012, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-004 | MSC-OSW-005 | WP-OSW-003, WP-OSW-007 | VFY-OSW-005, VFY-OSW-009–012, VFY-OSW-015, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-005 | MSC-OSW-005, MSC-OSW-006 | WP-OSW-007 | VFY-OSW-005, VFY-OSW-009, VFY-OSW-012, VFY-OSW-015, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-006 | MSC-OSW-003, MSC-OSW-007, MSC-OSW-008 | WP-OSW-001, WP-OSW-005, WP-OSW-009 | VFY-OSW-001–003, VFY-OSW-006, VFY-OSW-011–013, VFY-OSW-017, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-007 | MSC-OSW-009 | WP-OSW-008 | VFY-OSW-002–004, VFY-OSW-009, VFY-OSW-012, VFY-OSW-016, VFY-OSW-019, VFY-OSW-020 |
| VAL-SCN-OSW-008 | MSC-OSW-006 | WP-OSW-006 | VFY-OSW-002, VFY-OSW-004–006, VFY-OSW-012, VFY-OSW-014, VFY-OSW-019, VFY-OSW-020 |

MSC-OSW-001 was satisfied by the settled Requirements trace and is not a
product-session scenario. MSC-OSW-008 additionally requires the performance
acceptance packet after WP-OSW-005 measurement.

Machine-expanded verification inventory: VFY-OSW-001, VFY-OSW-002,
VFY-OSW-003, VFY-OSW-004, VFY-OSW-005, VFY-OSW-006, VFY-OSW-007,
VFY-OSW-008, VFY-OSW-009, VFY-OSW-010, VFY-OSW-011, VFY-OSW-012,
VFY-OSW-013, VFY-OSW-014, VFY-OSW-015, VFY-OSW-016, VFY-OSW-017,
VFY-OSW-018, VFY-OSW-019, and VFY-OSW-020.

## Validation gate

Decision: `pass_with_risk`

- [x] All eight Mission scenarios have actors, tasks, prerequisites, hard criteria, evidence, privacy, and rerun rules.
- [x] Critical scientific/cartographic/authority misconceptions have a zero-tolerance gate.
- [x] Verification conformance and Validation usefulness are not conflated.
- [x] Reader counts are labeled formative rather than statistically general.
- [x] Accessibility evidence requires behavior and meaning, not screenshots alone.
- [x] Null, contrary, unavailable, degraded, and failed results remain evidence.
- [x] Performance/release thresholds stay blocked until measured and accepted.
- [x] No scenario is represented as already executed or passed.
- [x] All eight native roles resolve every P1/P2 validation-plan finding.

Trace is authorized next but remains unopened. All validation execution
evidence stays blocked; work packages remain proposed and no participant study
or external contact is authorized.

## Source links

- [Mission](MISSION.md)
- [CONOPS](CONOPS.md)
- [Requirements](REQUIREMENTS.md)
- [Verification](VERIFICATION.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Work Packages](WORK_PACKAGES.md)
- [PITFALL register](../../design/pitfalls/README.md)
- [Native roles](../../.roles/ROLE.md)
- [Validation roles review](../../signals/roles/check/validation-roles-check-2026-09-07.md)
