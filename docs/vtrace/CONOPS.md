# OSW Concept of Operations

Status: settled at native-role fixed point, 2026-09-06

## Scope

Repo: OSW — Ocean States of the World

This CONOPS defines how the existing static atlas, research artifacts, evidence
receipts, and repository controls are used. It derives from the accepted
[Mission](MISSION.md) and does not select a new application architecture,
schema, detector, region partition, scientific mechanism, or public release.

## System boundary

OSW has two coupled operating surfaces:

1. **Public atlas surface:** static HTML, CSS, JavaScript, SVG, and display-ready
   data served without a live scientific provider.
2. **Repository research surface:** source registers, explicit acquisition
   scripts, analysis code, committed receipts, generated artifacts, tests, and
   review records used by maintainers and researchers.

External observational/model archives supply inputs but do not belong to OSW.
GitHub Pages hosts a release but does not determine scientific readiness.
External reviewers advise; they do not become endorsers or release authorities.
Forecast, hazard, navigation, policy, and scientific-peer-review authorities
remain outside OSW.

## Actors

| ID | Actor | Responsibility | Needed outcome |
|---|---|---|---|
| ACT-OSW-001 | Curious reader or learner | Explore a place or event and interpret the principal finding and limitation. | A short, legible route from map to evidence without repository expertise. |
| ACT-OSW-002 | Research auditor | Inspect exact source lineage, quantity, method, sensitivity, and claim ceiling. | A resolvable receipt and reproducible or explainably divergent result. |
| ACT-OSW-003 | Keyboard, screen-reader, low-vision, motion-sensitive, touch, or narrow-screen reader | Operate and interpret the same atlas states through an appropriate access path. | Equivalent scientific meaning without color, hover, fine pointer control, animation, or wide layout. |
| ACT-OSW-004 | Educator or science communicator | Use a bounded visual explanation with learners or a public audience. | A stable link, text alternative, source path, and nearby caveat. |
| ACT-OSW-005 | Scientific contributor | Add or challenge a source, diagnostic, event, pathway, budget term, or classification. | An explicit claim ceiling, reproducible transformation, tests, and disposition. |
| ACT-OSW-006 | Cartographic/interface contributor | Add or revise a projection, hierarchy, label, interaction, or responsive view. | A declared visual encoding that cannot silently promote the evidence. |
| ACT-OSW-007 | Release steward and owner | Decide whether a reviewed branch is ready to replace the hosted atlas. | One reconciled release state, passing gates, bounded open risks, and an explicit owner decision. |
| ACT-OSW-008 | External reviewer | Challenge a scoped artifact through a scientific, data, cartographic, editorial, accessibility, reproducibility, or planetary lens. | A bounded review target and visible disposition without implied endorsement. |

## Operational states

| State | Meaning | Permitted public claim |
|---|---|---|
| Released | Owner-approved artifact matches public site, citation, and release records. | The declared released evidence and behavior only. |
| Review preview | Committed and reviewable on a non-publication branch; role gate may be complete while owner promotion remains open. | Preview status and bounded findings; not current public behavior. |
| Experiment | Comparative projection, map, detector, sensitivity, or method study without default-product status. | What the experiment compares and cannot establish. |
| Research intake | Source question, request, inventory, or contract without a supported result. | Availability, planned test, and known gap only. |
| Degraded | A source, asset, interaction, receipt, or verification path is unavailable or inconsistent. | The preserved supported subset plus explicit failure; never a fabricated replacement. |

## Pitfall exercise matrix

| Scenario | Pitfalls exercised | Required behavior |
|---|---|---|
| `OPS-SCN-OSW-001` | `SI-01`, `SI-02`, `DL-02` | Quantities and residual remain bounded; displayed values agree with receipts. |
| `OPS-SCN-OSW-002` | `DN-01`, `DN-02`, `DL-02` | Sign/reference, sampling geometry, source lineage, and divergence remain inspectable. |
| `OPS-SCN-OSW-003` | `CA-01`, `CA-02` | Seams, land, missing support, boundary class, and non-color meaning survive interaction. |
| `OPS-SCN-OSW-004` | `SI-01`, `SI-02`, `SI-03`, `DN-01`, `DN-02`, `DL-02` | Unsupported claims and malformed scientific inputs fail before preview promotion. |
| `OPS-SCN-OSW-005` | `SI-03`, `CA-02` | A tidy partition cannot outrank contrary transport evidence. |
| `OPS-SCN-OSW-006` | `DL-01`, `DL-03` | Release state reconciles and public payload regression is explicit. |
| `OPS-SCN-OSW-007` | `SI-01` | Compared quantities are named before mechanism transfer or visual analogy. |

## Scenarios

### OPS-SCN-OSW-001 — follow a marine-heatwave event from footprint to partial budget

**Mission parents:** `NEED-OSW-002`, `NEED-OSW-003`, `NEED-OSW-005`;
`CON-OSW-001` through `CON-OSW-004`

**Actor and trigger:** ACT-OSW-001 opens the “follow heat” entrance and selects
the worked North Atlantic event.

**Inputs:** committed D1-D14 display artifacts and receipts; selected scene;
optional direct URL state.

**Normal path:**

1. The atlas identifies the event, date/window, location, and evidence class.
2. The reader advances through duration/footprint, lineage, surface
   temperature, surface forcing, 0-50 m storage, and horizontal advection.
3. The map frame remains geographically recognizable while depth, support, and
   quantity changes are announced visually and textually.
4. Every scene presents one finding beside its strongest limitation and links
   to the underlying receipt.
5. The final scene shows measured terms and the unresolved partial residual
   without naming the remainder as a process or closure.

**Failure or degraded path:** missing or invalid scene data produces an
identified unavailable state and retains the prior supported scene. A
cross-product time/support mismatch disables the combined comparison. Small
screens move detail below the map rather than hiding either claim or caveat.

**Outputs:** shareable scene URL, visual and data-oriented text view, evidence
badge, key values, limitations, and receipt link.

**Handoff:** ACT-OSW-001 may continue to a province/object view; ACT-OSW-002
may enter the audit path. No operational or causal decision is handed off.

**Validation evidence:** execute `VAL-SCN-OSW-001` and
`VAL-SCN-OSW-003`; require finding-and-limitation recall and exact receipt/value
agreement.

### OPS-SCN-OSW-002 — audit and reproduce a quantitative claim

**Mission parents:** `NEED-OSW-003`, `NEED-OSW-006`; `CON-OSW-002`,
`CON-OSW-008`, `CON-OSW-009`

**Actor and trigger:** ACT-OSW-002 follows the evidence link from a map or claim.

**Inputs:** claim identifier, evidence receipt, source-register row, committed
derived input/output, analysis/build scripts, dependency profile, and declared
network acquisition record where applicable.

**Normal path:**

1. The auditor identifies provider/product, variable, units, sign/reference,
   time, depth, support, grid/mask, transformation, checksum, evidence class,
   and claim ceiling.
2. Offline verification checks committed transformations and artifacts.
3. Optional explicit acquisition reproduces upstream input when it remains
   available and redistribution permits it.
4. A byte or result difference is attributed to a changed source, environment,
   request, method, or unsupported claim rather than silently normalized away.

**Failure or degraded path:** unavailable/mutated upstream bytes retain the
request, source identity, acquisition time, expected checksum, and failure.
Missing optional dependencies stop only the declared optional path. A checksum,
schema, dimension, coordinate, unit, or mask mismatch fails the claim refresh.

**Outputs:** reproduced artifact or bounded divergence report, command result,
source/receipt chain, and any proposed correction.

**Handoff:** a scientific disagreement goes to ACT-OSW-005 and relevant roles;
a source-custody issue blocks redistribution; a code/artifact defect enters a
bounded implementation change after the relevant VTRACE baseline exists.

**Validation evidence:** execute `VAL-SCN-OSW-002` and
`VAL-SCN-OSW-006` against one observation-derived and one model-derived view.

### OPS-SCN-OSW-003 — explore an ocean state and its overlapping objects

**Mission parents:** `NEED-OSW-001`, `NEED-OSW-004`, `NEED-OSW-005`;
`CON-OSW-005` through `CON-OSW-007`, `CON-OSW-011`

**Actor and trigger:** ACT-OSW-001 or ACT-OSW-003 selects a province from the
world atlas by pointer, keyboard, search, or direct URL.

**Inputs:** projection, selected province identity, optional conceptual lens,
observed field/depth, object filter, and hairline/hierarchy preference.

**Normal path:**

1. Selection zooms or spotlights the province without replacing its coastline,
   projection, or polar/seam context.
2. The atlas lists overlapping objects by type and evidence class rather than
   implying exclusive ownership of every water parcel.
3. Region/realm membership remains a provisional organizational overlay.
4. The reader can move from place to a relevant pathway, event, section, or
   budget only when that relationship is explicitly supported.
5. URL, focus, announcement, and text alternative update together.

**Failure or degraded path:** when no province-aggregated observation exists,
the atlas preserves direct grid projection and says “no state aggregation.” An
object crossing the seam retains one identity. Missing, land, ice, and
out-of-domain support remain distinct rather than being filled decoratively.
An unknown URL state falls back to a documented default and announces the
rejected parameter. If a locally hosted feature or province SVG fails to load,
the base evidence map remains usable and identifies the unavailable overlay.

**Outputs:** shareable place state, name/hierarchy, overlapping-object list,
selected evidence view, text summary, and supported onward routes.

**Handoff:** ACT-OSW-004 may reuse the stable state; ACT-OSW-002 may inspect
evidence; a proposed boundary correction goes to OPS-SCN-OSW-005.

**Validation evidence:** execute `VAL-SCN-OSW-003` and
`VAL-SCN-OSW-004` across pointer-free, non-color, narrow, seam, polar, and
coastal cases.

### OPS-SCN-OSW-004 — contribute a new or revised scientific view

**Mission parents:** `NEED-OSW-003`, `NEED-OSW-006`; `CON-OSW-001` through
`CON-OSW-004`, `CON-OSW-008` through `CON-OSW-010`

**Actor and trigger:** ACT-OSW-005 proposes a source, calculation, sensitivity,
event, or correction.

**Inputs:** consequential question, authoritative or explicitly synthetic
source, rights posture, requested product result, claim ceiling, existing
pitfall scan, and expected shortest demonstration.

**Normal path:**

1. The contributor classifies the source and proposed quantity before
   acquisition or implementation.
2. Reuse of existing analysis, schemas, generators, and tests is preferred.
3. Network retrieval writes a checksummed receipt and does not become a default
   offline dependency.
4. Analysis emits derived data plus limitations; rendering reads or verifies
   those data rather than copying independent headline constants.
5. Targeted tests, full offline verification, source registration, browser
   inspection where visual, and relevant `.roles` review complete before a
   preview claim advances.

**Failure or degraded path:** unclear rights, unidentified field, invalid
units/dimensions, unsupported grid collocation, failed sensitivity, stale
generated artifact, or unresolved P1/P2 finding stops promotion while retaining
the question and negative evidence. Null results are valid outputs.

**Outputs:** source/derived receipts, analysis and display artifacts, tests,
claim/limitation update, role review, and explicit preview or rejected status.

**Handoff:** ACT-OSW-006 owns cartographic integration; ACT-OSW-007 owns release
promotion. External publication or correspondence requires separate owner
authority.

**Validation evidence:** clean-checkout reproduction of one existing D-series
slice plus a malformed or unsupported fixture that fails safely.

### OPS-SCN-OSW-005 — challenge or revise an ocean-state boundary

**Mission parents:** `NEED-OSW-004`, `NEED-OSW-007`; `CON-OSW-005`,
`CON-OSW-011`

**Actor and trigger:** ACT-OSW-005 or ACT-OSW-008 challenges an 11-realm,
22-region, or 56-province relationship using motion/exchange evidence.

**Inputs:** candidate boundary class and geometry; declared scale/depth/time;
persistence, cross-boundary exchange, retention, convergence, vertical
agreement, and gate-dependence diagnostics with uncertainty/sensitivity.

**Normal path:**

1. The reviewer distinguishes classic reference identity, OSW organizational
   membership, and any diagnosed dynamic boundary.
2. Candidate borders receive comparable diagnostic scorecards.
3. Evidence may retain, merge, split, move, or demote a region without changing
   the 56-name reference directory automatically.
4. Maps show both the proposed organization and its failure/uncertainty regions.

**Failure or degraded path:** inadequate depth, duration, resolution, or
closure leaves the boundary provisional. A visually cleaner projection or
preferred count cannot substitute for transport evidence. Conflicting tests
remain visible instead of being collapsed to one score without rationale.

**Outputs:** candidate disposition, evidence scorecard, revised or retained
organizational registry, limitations, and change-control record when a
controlled interface is affected.

**Handoff:** accepted organizational change proceeds through ACT-OSW-006 and
then release review; unresolved science returns to a bounded research question.

**Validation evidence:** execute `VAL-SCN-OSW-005` with at least one attractive
but exchange-poor boundary that must be rejected or demoted.

### OPS-SCN-OSW-006 — review and promote a public atlas release

**Mission parents:** `NEED-OSW-005`, `NEED-OSW-006`; `CON-OSW-007` through
`CON-OSW-010`, `CON-OSW-014`

**Actor and trigger:** ACT-OSW-007 considers a specific reviewed commit for
promotion from preview to the public site.

**Inputs:** immutable candidate commit; full offline/CI results; browser,
accessibility, performance, source/license, link, generated-artifact, and
native-role evidence; open risks; owner visual decision.

**Normal path:**

1. The steward compares the candidate with the currently hosted release.
2. README, roadmap, preview status, source register, publication checklist,
   citation metadata, milestone/version, and hosted target are reconciled.
3. Critical-path bytes and load-on-demand behavior are compared with the
   measured baseline.
4. The owner records promote, hold, or reject. Only promote updates public
   release claims and deployment state.
5. The deployed site receives a smoke check against the approved commit.

**Failure or degraded path:** any hash mismatch, broken critical link,
unresolved P1/P2, inaccessible primary journey, source-rights gap, unexplained
payload regression, or status disagreement holds release. A hosting failure
retains the prior released site and records the failed transition.

**Outputs:** release decision, reconciled metadata, deployed commit or retained
prior release, smoke evidence, and bounded open risks.

**Handoff:** a held candidate returns to its owning contributor; public
communications follow only a successful owner-approved deployment.

**Validation evidence:** execute `VAL-SCN-OSW-006` from a clean checkout and
compare the hosted commit and primary journey after deployment.

### OPS-SCN-OSW-007 — compare an Earth ocean object with a gas-giant flow

**Mission parents:** `NEED-OSW-008`; `CON-OSW-012`

**Actor and trigger:** ACT-OSW-001, ACT-OSW-004, or ACT-OSW-005 opens or proposes
a planetary comparison.

**Inputs:** exact Earth object/quantity, exact planetary object/observable,
shared candidate mechanism or nondimensional property, source evidence, and
known forcing/stratification/rotation/depth/compressibility/boundary/observation
differences.

**Normal path:**

1. Earth-side and planetary-side quantities are identified independently.
2. The comparison names what transfers, what does not, and what remains unknown.
3. Visual resemblance is supporting context only after the mechanism-level
   comparison.
4. At least one observation or simulation outcome is stated that would weaken
   or falsify the analogy.

**Failure or degraded path:** absent depth, incompatible variables, unmatched
scales, or a color/stripe resemblance without mechanism leaves the comparison
speculative or removes it. A cloud-top field is not promoted to a full-depth
heat map.

**Outputs:** paired explanation, evidence pointers, transfer limits, and
falsifier.

**Handoff:** ORBIT reviews only after CURRENT and SOUNDER accept both sides'
quantities and evidence.

**Validation evidence:** execute `VAL-SCN-OSW-007` with one defensible and one
deliberately visual-only comparison.

## Operational assumptions

- A modern browser can load the released static atlas without a server-side
  application or live data API.
- Git and Python are available to maintainers; optional scientific dependencies
  are pinned separately from the default browser experience.
- Public upstream archives can change, disappear, throttle, or require terms;
  receipts preserve identity and failure without guaranteeing future service.
- Generated artifacts may be committed when they are necessary for the static
  site or reproducible review, subject to a deliberate payload/custody policy.
- Native `.roles` review is internal assurance and does not replace external
  domain peer review, user validation, owner approval, or hosting verification.
- Direct URLs are durable within a declared compatibility/version boundary;
  later stages must define migration behavior.
- The current public atlas has no account, user-upload, cookie, or telemetry
  workflow. Adding one changes the operating and privacy boundary and requires
  explicit later-stage change control.

## Open questions and assigned stage

| ID | Question | Decision stage |
|---|---|---|
| OQ-OSW-001 | Is the guided event anatomy a mode inside the current atlas, a new route, or both? | Architecture / Interfaces |
| OQ-OSW-002 | Which Atlas 10 capabilities form the observed-current baseline versus an optional experiment? | Specification baseline |
| OQ-OSW-003 | What exact receipt/claim descriptor becomes common across all quantitative views? | Requirements / Interfaces |
| OQ-OSW-004 | What compatibility promise applies to province, object, mode, depth, event, and scene URL parameters? | Requirements / Interfaces |
| OQ-OSW-005 | Which heavyweight inputs remain in Git, move to release assets/external custody, or become reproducible-on-demand only? | Architecture / Interfaces / Release design |
| OQ-OSW-006 | What measured page-weight and interaction budgets apply to the public critical path? | Requirements after hosted baseline measurement |
| OQ-OSW-007 | Who participates in non-specialist and assistive-technology validation beyond owner inspection? | Validation plan |
| OQ-OSW-008 | Does OSW enter TRACKER's canonical registry and submodule map? | Separate TRACKER owner decision; outside product stages |

## Source links

- [Mission](MISSION.md)
- [Central roadmap](../../ROADMAP.md)
- [Pitfall register](../../design/pitfalls/README.md)
- [Motion study](../../MOTION.md)
- [Atlas method](../../atlas/README.md)
- [Review roles](../../.roles/ROLE.md)

The native-role fixed-point review is recorded in
[`conops-roles-check-2026-09-06.md`](../../signals/roles/check/conops-roles-check-2026-09-06.md).
