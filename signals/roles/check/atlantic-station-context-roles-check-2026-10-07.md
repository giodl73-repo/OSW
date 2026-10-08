---
skill: roles-check
topic: atlantic-station-context
date: 2026-10-07
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Atlantic station context review

Internal application of the seven project role lenses to the archive parser,
source audit, checked Rust source integration, and cruise sampling map. This is
not independent scientific peer review or a canonical boundary admission.

## Selected roles

CURRENT: sampling support and physical meaning. SOUNDER: source custody and
identity. CHART: map interpretation. BEACON: reader understanding. HARBOR:
keyboard and textual access. KEEL: reproducibility and failure handling.
LOGBOOK: protected-main publication and honest status.

## Findings

| Role | Finding | Severity | Section | Recommendation / disposition |
|---|---|---|---|---|
| CURRENT | Cruise points do not identify inverse-model current boundary stations. | P2 | geometry scope | Resolved: retain unresolved pairing, draw unconnected points, reject footprint/state/annual eligibility. |
| CURRENT | ROS/CTD casts may sample other depths and flows. | P3 | map caption | State sampling support; do not infer the width record's density layer from map dots. Applied. |
| CURRENT | The 2018 nominal latitude resolution does not recover edge pairs. | P3 | source conflicts | Keep held-out width rows out of this audit's admissions. Applied. |
| SOUNDER | The 2007 archive prints dates from 2005. | P2 | source dates | Resolved: retain all 46 original dates and quarantine all three affected dated maps. |
| SOUNDER | Paper and provider cruise aliases differ. | P3 | archive identity | Preserve both labels, including 06M220130509 / 06MM20130509. Applied. |
| SOUNDER | Coordinate datum and uncertainty are not independently established. | P3 | positions | Retain null uncertainty/datum, raw degrees/minutes and navigation codes. Applied. |
| CHART | Connected points could suggest a current axis or current edges. | P3 | map grammar | Use dots only, with sampling-context caption. Applied. |
| CHART | Projection and point meaning need visible labels. | P3 | legend | Identify OSW equirectangular basemap and yellow sampling points. Applied. |
| CHART | Source rounding can produce exactly 60.00 minutes. | P3 | coordinate transform | Carry arithmetically, flag the source representation, reject larger minutes. Applied and tested. |
| BEACON | Cruise context could be mistaken for the paper's selected subset. | P3 | explanatory text | Explain that the inverse-model subset is unresolved beside the map. Applied. |
| BEACON | A zero-point map could look like absence of a current. | P3 | missing cases | Display source-date conflict or unrecovered-source message. Applied. |
| BEACON | Short provenance must retain access to the original archive. | P3 | receipt | Show source archive and checked exact-record inspection links. Applied. |
| HARBOR | Hover-only station details exclude keyboard readers. | P2 | station details | Resolved: add semantic collapsible station table, source lines, and horizontal keyboard scroll. |
| HARBOR | Changes must announce loading, errors and selected scope. | P3 | controls | Use labeled select and status region; clear stale context on current switch. Applied. |
| HARBOR | Narrow screens need a readable map without page overflow. | P3 | mobile | Fit SVG to width and contain the station table in a focusable scroll region. Tested at 320 px. |
| KEEL | An altered archive must not regenerate silently. | P3 | source custody | Verify SHA-256 and size of all 17 archives before parsing. Applied. |
| KEEL | Source corpus could become stale after parser changes. | P3 | bundle generation | Regenerate audit exactly before accepting it into the checked index. Applied. |
| KEEL | A changed browser corpus must not display source coordinates. | P3 | WASM load | Fail integrity checks and show no map; register this check in the full browser gate. Applied. |
| LOGBOOK | Protected-main publication is not complete. | P2 | publication | Open condition: pass required exact-head checks and land through protected main; retain draft status until then. |
| LOGBOOK | Archived text needs license and cruise citation context. | P3 | acquisition | Record CCHDO policies, source URLs, default license determination and cruise credits. Applied. |
| LOGBOOK | Validation evidence must distinguish local checks from CI. | P3 | batch receipt | Report local outcomes separately; no current-main coverage claim. Applied. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 4 (3 resolved, publication open). P3: 17.
Verdict: APPROVED-WITH-CONDITIONS.

CURRENT and CHART agree that sampling locations cannot establish current edges.
SOUNDER and KEEL agree that malformed or conflicting source metadata must remain
visible rather than being silently repaired.

## Amendments

1. Keep original station identity and quarantine conflicting dates before any dated mapping.
2. Add source-line station tables and adjacent projection/sampling-scope explanation.
3. Validate exact source regeneration and shipped-WASM failure handling before publication.
