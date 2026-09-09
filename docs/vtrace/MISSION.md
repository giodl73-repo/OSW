# OSW Mission

Status: settled at native-role fixed point, 2026-09-06

## Scope

Repo: OSW — Ocean States of the World

VTRACE adoption scope: baseline the mission of the existing repository and its
transition from a large collection of ocean maps and research receipts into a
coherent public atlas. This stage defines intent only. It does not approve a
new scientific claim, region boundary, interface, implementation, Atlas
milestone, or public release.

## Mission need

| ID | Need | Success signal | Status |
|---|---|---|---|
| NEED-OSW-001 | Give the world ocean a legible geography of places, objects, motions, layers, and exchanges rather than treating it as unlabeled space between continents. | A visitor can orient to ocean structures without land becoming the primary organizing surface. | accepted |
| NEED-OSW-002 | Connect compelling maps to the physical distinctions required to interpret heat in a moving ocean. | Temperature, heat content, transport, convergence, transformation, and causation remain distinguishable throughout a visitor journey. | accepted |
| NEED-OSW-003 | Let readers move from a mapped claim to the exact evidence and limitations that support it. | Every quantitative scene exposes source, variable, time, depth, spatial support, method, evidence class, and receipt; committed derived results reproduce, while unavailable upstream bytes retain enough identity to explain or challenge a difference. | accepted |
| NEED-OSW-004 | Show ocean motion at multiple scales without turning currents, pathways, gates, events, or provinces into permanent walls. | Global orientation, province inspection, pathways, sections, and control volumes retain their distinct identity tests and leakage/uncertainty. | accepted |
| NEED-OSW-005 | Make the atlas understandable and operable by curious non-specialists while remaining auditable by professional researchers. | A plain-language path and a researcher path reach the same claim boundary and underlying evidence. | accepted |
| NEED-OSW-006 | Preserve reproducibility, source custody, and release truth as the atlas evolves. | A fresh maintainer can run the offline gate, identify optional network refreshes, reproduce derived artifacts, and distinguish public release from preview work. | accepted |
| NEED-OSW-007 | Test proposed ocean-state organization against motion and exchange evidence rather than visual tidiness or a preferred count. | Region decisions can be retained, merged, split, moved, or demoted using declared transport diagnostics. | accepted |
| NEED-OSW-008 | Use Earth/gas-giant comparison to illuminate shared rotating-fluid mechanisms without asserting material or dynamical equivalence. | Every comparison names the shared property, failed assumptions, and a possible falsifier. | accepted |

## Users

| User | Need | Success signal |
|---|---|---|
| Curious reader or learner | See recognizable ocean geography and understand what the water and heat are doing. | Can complete a short map-led story and accurately repeat both its finding and its main limitation. |
| Ocean, climate, or Earth-system researcher | Audit the source, transformation, scale, assumptions, and evidentiary status of a map or number. | Can reach a machine-readable receipt and regenerate or independently challenge the result. |
| Educator or science communicator | Reuse clear visual explanations without losing the difference between observation, model diagnostic, and hypothesis. | Can point learners to an accessible figure plus adjacent caveats and sources. |
| Cartographer or information designer | Explore ocean-first projections and hierarchy without making schematic regions look physically exact. | Can identify projection, scale, boundary class, missing support, and non-color encodings. |
| OSW maintainer or contributor | Extend the atlas without drifting claims, generated artifacts, source records, tests, or release status apart. | Has an ordered product roadmap, explicit contracts, offline checks, and role-owned review gates. |
| External reviewer | Give bounded scientific, data, cartographic, accessibility, or reproducibility feedback without being treated as an endorser. | Can identify the exact artifact and claim under review and see how the finding is dispositioned. |

## Operating context

OSW is a static, browser-based public atlas paired with repository-local Python
analysis, generated SVG/JSON/data artifacts, source registers, field guides,
and review evidence. The public site must work without a live scientific data
provider. Network acquisition and refresh are explicit maintainer operations;
derived products are checked offline against committed fixtures, receipts, and
contracts.

The atlas spans four related but non-interchangeable contexts:

1. conceptual ocean geography and classification;
2. observed or objectively analyzed fields;
3. model/reanalysis motion and heat-budget diagnostics; and
4. cross-planetary mechanism comparison.

The site is explanatory and exploratory. Researchers retain responsibility for
independent scientific review; institutions and operational services retain
forecast, hazard, policy, navigation, and intervention authority.

## Constraints

| ID | Constraint | Rationale | Status |
|---|---|---|---|
| CON-OSW-001 | Every view declares whether it is conceptual, observed, derived, model/reanalysis diagnostic, sensitivity result, or unresolved. | Prevents presentation from silently promoting evidence. | accepted |
| CON-OSW-002 | Quantitative claims declare variable, units, sign convention, time, depth/layer, spatial support, reference/baseline, and missing-data treatment as applicable. | Makes physically different quantities interpretable and comparable. | accepted |
| CON-OSW-003 | Temperature, heat content, volume transport, reference-relative heat transport, convergence, storage, transformation, and causal attribution remain distinct. | Prevents attractive but invalid mechanism stories. | accepted |
| CON-OSW-004 | A residual remains unresolved until independently supported terms account for it; numerical proximity is not closure. | Prevents remainder-as-process and cross-system closure errors. | accepted |
| CON-OSW-005 | Conceptual and organizational boundaries are visibly distinguished from diagnosed, thresholded, modeled, or published boundaries. | Prevents schematic regions from becoming false natural borders. | accepted |
| CON-OSW-006 | Projection, seam, land, sea ice, missing support, and out-of-domain treatment remain explicit; land may provide subdued geographic orientation but cannot obscure ocean evidence. | Prevents cartographic geometry from manufacturing scientific structure while retaining recognizable coast context. | accepted |
| CON-OSW-007 | Meaning and operation cannot depend on color, hover, fine pointer control, animation, or a wide viewport. | Makes accessibility part of scientific correctness. | accepted |
| CON-OSW-008 | Source identity, license/citation, acquisition request, transformation, checksum, and redistribution posture are retained at the appropriate evidence level. | Preserves provenance and lawful reuse. | accepted |
| CON-OSW-009 | Default validation is deterministic and offline; mutable-source refreshes are separate, explicit operations. | Keeps ordinary review reproducible. | accepted |
| CON-OSW-010 | Public release, review preview, experiment, and unvalidated research states cannot be represented as equivalent. | Keeps repository and hosted-site claims aligned with evidence and approval. | accepted |
| CON-OSW-011 | Proposed region counts and boundaries remain revisable under persistence, exchange, retention, convergence, vertical, and gate-dependence tests. | Prevents sunk-cost preservation of a satisfying partition. | accepted |
| CON-OSW-012 | Earth/gas-giant comparisons declare forcing, stratification, rotation, depth, compressibility, boundaries, and observation differences. | Prevents visual resemblance from becoming claimed equivalence. | accepted |
| CON-OSW-013 | VTRACE and role-review machinery remain internal controls rather than ocean objects, evidence classes, or visitor-facing product concepts. | Protects the product from process leakage. | accepted |
| CON-OSW-014 | Public web payloads remain usable on ordinary connections while heavyweight reproducibility inputs retain a documented custody path. | Prevents scientific custody from making the atlas practically inaccessible. | accepted |

## Non-goals

- live ocean forecasting, hazard warning, navigation, routing, or operational
  decision support;
- declaring a uniquely correct, permanent, impermeable, or legally meaningful
  partition of the ocean;
- inferring full heat content, transport, transformation, or causation from a
  surface temperature map or current arrow;
- treating a pathway ensemble, correlation, residual, or one-year/model screen
  as probability, climatology, mechanism attribution, or universal behavior;
- predicting a single deterministic outcome from blocking a gateway, moving a
  continent, changing a pole, or another deep-time counterfactual;
- treating Earth oceans and gas-giant atmospheres as materially equivalent;
- replacing primary datasets, operational services, formal scientific peer
  review, or institutional authority;
- exposing VTRACE stages, work packages, readiness, reviews, or proof records
  as atlas features merely because they govern development.

## First validation scenarios

| ID | Scenario | Mission question |
|---|---|---|
| VAL-SCN-OSW-001 | A curious reader enters the guided D1-D14 North Atlantic marine-heatwave story and moves from event footprint through surface forcing, 0-50 m storage, horizontal advection, and the unresolved remainder. | Can the reader understand the emerging mechanism without repeating that the partial crossed-system budget is closed or causal? |
| VAL-SCN-OSW-002 | A researcher opens any quantitative scene, follows its receipt, checks source/variable/time/depth/support/transformation, and runs the documented offline analysis test. | Can the exact claim be audited without reverse-engineering the prose or relying on a live provider? |
| VAL-SCN-OSW-003 | A keyboard and screen-reader user selects an ocean state, changes evidence/depth mode, reaches the scene's text alternative, and follows a direct URL. | Can the same scientific finding and limitation be recovered without color, hover, pointer-only control, or forced focus? |
| VAL-SCN-OSW-004 | A cartographic reviewer compares Oceanic Mollweide, a province view, and a local event view at the antimeridian and polar/land edges. | Are projection, seam, boundary class, scale, and missing support visible enough to prevent false geometry? |
| VAL-SCN-OSW-005 | A zoning reviewer scores a candidate border that looks clean but has strong cross-boundary exchange or inconsistent depth behavior. | Can the evidence reject or demote the border without preserving the current region count? |
| VAL-SCN-OSW-006 | A maintainer checks out the repository without network access, runs the complete default gate, regenerates a supported artifact, and compares public/preview status. | Does the repo expose deterministic evidence and truthful release state? |
| VAL-SCN-OSW-007 | A reader compares an Earth current or vortex with a gas-giant jet or storm. | Does the comparison preserve the shared rotating-fluid mechanism while making non-analogous physics and observability explicit? |
| VAL-SCN-OSW-008 | A scientist challenges the apparent heat balance with a different depth, time window, product, or missing vertical term. | Does OSW present sensitivity or non-closure as useful evidence rather than defend a preferred story? |

## Success criteria

| ID | Criterion | Validation method | Evidence pointer |
|---|---|---|---|
| MSC-OSW-001 | Mission needs become stable parents for later product requirements. | Requirements-stage inspection maps every accepted requirement to at least one `NEED-OSW-*` or `CON-OSW-*`. | future `REQUIREMENTS.md` and `TRACE.md` |
| MSC-OSW-002 | The atlas supports one continuous place-to-evidence journey for non-specialists. | Moderated or owner-observed completion of `VAL-SCN-OSW-001` with finding-and-limitation recall. | future `VALIDATION.md`; current `ROADMAP.md` |
| MSC-OSW-003 | Quantitative claims remain independently auditable. | Execute `VAL-SCN-OSW-002`; inspect receipt completeness and reproducibility. | `SOURCE-REGISTER.md`; `research/ocean-object-evidence-receipts.json`; future `VERIFICATION.md` |
| MSC-OSW-004 | Accessibility preserves scientific meaning. | Keyboard, screen-reader, non-color, reduced-motion, zoom, and narrow-viewport execution of `VAL-SCN-OSW-003`. | future `VALIDATION.md`; current atlas tests |
| MSC-OSW-005 | Maps do not promote schematic geometry or conceal unsupported locations. | Cartographic execution of `VAL-SCN-OSW-004` across declared projections and scales. | projection/atlas artifacts; future validation evidence |
| MSC-OSW-006 | Motion and heat claims remain budget-disciplined under challenge. | CURRENT/SOUNDER review plus sensitivity and conservation tests for `VAL-SCN-OSW-008`. | `MOTION.md`; D-series receipts; analysis tests |
| MSC-OSW-007 | Release and reproduction claims match repository and hosted reality. | Clean-checkout offline gate, link/status audit, source-custody inspection, and owner release decision. | CI; `PREVIEW-STATUS.md`; `PUBLICATION-CHECKLIST.md`; future `REVIEW.md` |
| MSC-OSW-008 | OSW remains usable as the evidence corpus grows. | Measure the hosted critical path and require research payloads not needed for the selected view to load on demand. | future performance baseline and release evidence |
| MSC-OSW-009 | Planetary comparison transfers mechanism without false equivalence. | Execute `VAL-SCN-OSW-007`; require the shared property, non-analogous conditions, and an observation or simulation outcome that would falsify the comparison. | future `VALIDATION.md`; ORBIT role review |

## Mission-stage verification

```powershell
python -m pytest analysis -q
python -m unittest discover -s analysis -p "test_*.py"
python -m compileall -q analysis
node --check atlas/app.js
git diff --check
```

The native-role review is recorded in
[`mission-and-pitfall-foundation-roles-check-2026-09-06.md`](../../signals/roles/check/mission-and-pitfall-foundation-roles-check-2026-09-06.md).
These commands verify repository integrity and current behavior; later
Requirements and Validation stages must define product-level acceptance for
each mission criterion.

## Source links

- [Central roadmap](../../ROADMAP.md)
- [Project history](../../HISTORY.md)
- [Motion and heat-delivery study](../../MOTION.md)
- [Ocean-object classification](../../CLASSIFICATION.md)
- [Atlas method](../../atlas/README.md)
- [Source register](../../SOURCE-REGISTER.md)
- [Preview status](../../PREVIEW-STATUS.md)
- [Publication checklist](../../PUBLICATION-CHECKLIST.md)
- [Native review roles](../../.roles/ROLE.md)
- [Initial pitfall register](../../design/pitfalls/README.md)
