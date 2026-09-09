---
skill: roles-check
topic: atlas-10-argo-depth-ladder
date: 2026-08-28
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook, orbit]
p1_count: 0
verdict: APPROVED
---

# Atlas 10 Argo depth-ladder role review

Source commit: `2756f1e` (`Add Atlas 10 Argo depth ladder`)

## Artifact identification

- Type: multi-layer observational-data pipeline, generated artifacts,
  interactive pressure control, coordinate profile, documentation, and tests.
- Domain: physical oceanography, Argo stewardship, comparative cartography,
  accessibility, reproducibility, and release-state governance.
- Scope: July 2026 Scripps RG Argo potential-temperature anomalies at 10, 300,
  700, and 1000 dbar, extending the approved Atlas 09 single layer.

## Role selection

All eight installed roles are selected because this is an atlas increment.
CURRENT checks the vertical inference; SOUNDER the shared source contract;
CHART the cross-depth visual comparison; BEACON the reader's likely takeaway;
HARBOR the pressure controls and textual profile; KEEL the parser, fixtures, and
artifact locks; LOGBOOK the Atlas 09/10 boundary; and ORBIT the absence of an
unsupported transfer to gas-giant pressure levels.

## CURRENT — physical oceanography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | All four maps are anomalies from the same monthly RG product and depth-specific seasonal climatology, allowing comparison of anomaly persistence without implying equal absolute temperature. | P3 | artifacts and method | Keep “anomaly” in every pressure label. |
| 2 | The interface states that no individual pressure level or collection of four levels is vertically integrated heat content or transport. | P3 | insight, boundary, footer | Require explicit layer thickness and thermodynamics before any integration. |
| 3 | The selected levels give a defensible shallow-to-deep diagnostic ladder but are not presented as a complete water-column profile. | P3 | pressure controls and quantitative path | Call later interpolation a new derived product with its own validation. |

## SOUNDER — climate-data stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The four artifacts share an identical source URL, SHA-256, month, baseline, grid, stride, units, and retrieval timestamp. | P3 | committed artifacts | Preserve the shared-contract test as levels are added. |
| 2 | Exact pressure selection is encoded in both metadata and pressure-specific browser variable names. | P3 | generator and artifacts | Continue rejecting non-exact or unavailable pressure requests. |
| 3 | Each artifact independently preserves missing values, full sampled ranges, citation requirements, and the lack of per-cell uncertainty. | P3 | artifact metadata | Do not summarize uncertainty from cross-level agreement alone. |

## CHART — ocean cartography

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | One fixed zero-centered ±5°C scale across all four levels preserves honest magnitude comparison; the quieter 1000 dbar map is not contrast-stretched. | P3 | legend and Edge render | Keep the common scale unless a clearly labeled alternate normalization is added. |
| 2 | Pressure selection is redundantly visible in the selected control, map stamp, title, fact panel, canvas label, and map note. | P3 | atlas UI | Retain redundant labeling when exporting static frames. |
| 3 | The same projection, footprint, missing-value treatment, and out-of-domain encoding are used at every level. | P3 | renderer | Add a small-multiple export only if identical scale and domain remain locked. |

## BEACON — public-science editing

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | “Test whether an anomaly is shallow or persists deeper” accurately describes what the ladder permits. | P3 | map insight | Avoid upgrading visual persistence to a mechanism or moving water parcel. |
| 2 | Near-surface, upper-thermocline, intermediate, and deep helper labels orient readers without replacing the numeric pressure. | P3 | pressure controls | Keep the numeric dbar value primary. |
| 3 | The surface OISST and Argo baseline difference is explicit in the method and multi-product probe. | P3 | method and probe | Repeat this warning in any side-by-side surface/depth export. |

## HARBOR — accessibility

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | The pressure ladder is a named button group with pressed states, keyboard operation, visible focus, and mobile reflow. | P3 | HTML and CSS | Add automated keyboard traversal when browser testing is introduced. |
| 2 | Mode-specific canvas labels and latitude summaries update with the selected pressure. | P3 | `setMapMode`, `renderTextSummary` | Preserve pressure and baseline in every non-color equivalent. |
| 3 | The coordinate probe reports all four pressure anomalies in text and explicitly returns “outside source domain” when appropriate. | P3 | probe | Consider a semantic list if more pressure levels make the sentence unwieldy. |

## KEEL — reproducibility engineering

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A seven-test Argo suite locks pressure-specific window names and the shared month, baseline, hash, shape, and coordinates across four artifacts. | P3 | `test_argo_snapshot.py` | Add locked geographic profile values before a public promotion. |
| 2 | The complete offline suite passes 62 tests; JavaScript syntax and Python compilation pass without network access. | P3 | local gate | Keep source refresh outside the default CI job. |
| 3 | Edge rendered the 1000 dbar bookmark with the correct selected control and dynamic evidence text. | P3 | manual browser check | Add headless URL-state assertions when adopting a browser harness. |

## LOGBOOK — repository stewardship

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | README and status distinguish approved Atlas 09 from unreviewed Atlas 10 before this review record. | P3 | repository status | Replace the draft marker only in the review follow-up commit. |
| 2 | Source register, atlas method, analysis commands, researcher receipts, and all four downloadable artifacts agree. | P3 | documentation | Keep the receipt table synchronized through static tests. |
| 3 | Only compact transformed artifacts are committed; the downloaded 6.6 MB source file and local Edge screenshots remain outside the repository. | P3 | Git boundary | Preserve this public/private and source/derivative boundary. |

## ORBIT — planetary comparison

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Atlas 10 makes no equivalence between ocean dbar levels and gas-giant atmospheric pressure levels. | P3 | scope | Require an explicit thermodynamic and dynamical mapping before comparison. |
| 2 | The ladder strengthens the general lesson that a visible surface pattern can differ from structure at depth. | P3 | measurement firewall | Transfer only that measurement lesson, not the specific ocean profiles. |
| 3 | No Jupiter or Saturn claim, artifact, or source was changed. | P3 | repository diff | Review future planetary use as a separate artifact. |

## Synthesis

Roles reviewed: 8  
P1 blockers: 0 | P2 issues: 0 | P3 notes: 24

Verdict: **APPROVED**

Top finding: Atlas 10 creates a valid same-product pressure comparison while
maintaining the boundary between depth-specific anomalies and a vertically
integrated heat or transport calculation.

Cross-role consensus: CURRENT, SOUNDER, CHART, BEACON, HARBOR, and KEEL agree
that the common source contract and fixed anomaly scale are what make the four
maps comparable; those controls must not be relaxed for visual drama.

## Amend

The highest-severity findings are non-blocking P3 hardening opportunities:

1. Lock representative four-level geographic profile values before public
   promotion so a coordinate or longitude-convention regression fails loudly.
2. Add headless interaction coverage for pressure buttons, URL restoration,
   canvas labels, and probe updates when a browser dependency is accepted.
3. Treat any full-profile interpolation, salinity addition, or heat-content
   integration as a separately specified derived product—not an automatic
   extension of this approval.
