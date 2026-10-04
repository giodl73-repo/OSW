---
skill: roles-check
topic: tsuchiya-angular-width
date: 2026-10-04
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Tsuchiya general angular width review

Artifact: two current-linked editorial width records, existing source audits,
width protocol v1.14, validator, explorer, inventory table and dashboard.
Seven installed roles cover physical meaning, provenance, cartography, public
explanation, access, reproducibility and repository status. ORBIT is inapplicable.
Internal role lenses do not provide independent scientific measurement approval.

| Role | Finding | Severity | Artifact | Resolution / condition |
| --- | --- | --- | --- | --- |
| CURRENT | Core migration cannot supply annual width extrema | P2 | Width records | Addressed: width range null; annual and seasonal inference flags false. |
| CURRENT | Main and secondary southern jets need separate support | P3 | Branch assignment | General summary applies to main southern flow only; no secondary width or aggregated envelope. |
| CURRENT | Neutral-layer boundaries differ where eastward currents blend | P3 | Boundary rule | Zero-transition and subjective-minimum conventions retained; no universal threshold or fixed-depth interpretation. |
| SOUNDER | Two linked identities could inflate independent evidence count | P2 | Shared claim | Addressed: same source claim ID and independent-measurement flag false; text explains shared statement. |
| SOUNDER | General angular scale lacks a measured geographic center | P3 | Conversion | Source center/longitude/geometry remain null; equator explicitly computational. |
| SOUNDER | Extraction needs source locator and change detection | P3 | Audit provenance | Rowe section 3b/printed 1179 retained, publisher confirms angular unit; audit checksums enforced. |
| CHART | Computational limits must not appear as observed edges | P2 | Explorer | Addressed: width bar and section-edge locator omitted; no width polygon fabricated. |
| CHART | Static studied reach is separate from ensemble width geography | P3 | Route context | Map retains static route-context label; no seasonal geometry claim. |
| CHART | PV-front scale is not the whole jet width | P3 | Scope notes | Front remains separate physical metric; validator rejects substituted numeric width. |
| BEACON | Original angular unit helps explain rounded conversion | P3 | Value label | Both 2 degrees and approximately 220 km visible. |
| BEACON | Northern Tsuchiya and western Pacific NEUC are separate identities | P3 | Evidence applicability | Width attached only to northern/main southern subsurface IDs; no transfer to NEUC. |
| BEACON | Regional narrowing limits generality | P3 | Source quality | Southern downstream narrowing retained; no uniform along-route width claim. |
| HARBOR | Evidence needs a textual alternative to the map | P3 | Explorer | Metric, original units, interpretation and source available as text. |
| HARBOR | Nonseasonal evidence must not run as a movie | P3 | Controls | Playback disabled; comparability restriction is explicit text. |
| HARBOR | Saved links and small screens need equal access | P3 | Navigation | Both current/record URLs reload; atlas round trip and 320 px reflow pass. |
| KEEL | Angular conversions require reproducible arithmetic | P3 | Validator | WGS84 meridional distance recomputed; 10 km rounding verified. |
| KEEL | Unsupported dates, edges and independence need mutation tests | P3 | Width tests | New test rejects fabricated support, changed audit pins, altered source span and annual range. |
| KEEL | UI class must survive generated snapshot updates | P3 | Browser/dashboard | Both current widths counted; no reported-length admission; labels/table/reload verified. |
| LOGBOOK | Current status must distinguish linked records from observations | P3 | README/coverage | 27 records for 18 identities with shared-claim qualification documented. |
| LOGBOOK | Protocol provenance must match the saved rules | P3 | Inventory pin | v1.14 checksum regenerated; offline provenance checker passes. |
| LOGBOOK | Focused checks are not publication approval | P3 | Review/status | Canonical ledger and release unchanged; no full-suite, clean-checkout or publishing claim. |

## Synthesis

Roles reviewed: 7. P1: 0. P2: 3 addressed. P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for scoped editorial evidence.
Top finding: a general source scale must not become independent observations,
measured edges or annual extrema. CURRENT, SOUNDER and CHART agree on these
limits. Individual branch-, region- and layer-specific widths remain unresolved.

## Three amendments

1. Preserve one shared source-claim ID across the northern/main southern records,
   with explicit nonindependence, original angular units and pinned audit support.
2. Separate the equatorial unit conversion from source coordinates; omit bars and
   section-edge locators and test null center, longitude, dates and fixed depth.
3. Retain neutral-layer boundary ambiguity, regional narrowing and separate
   core-displacement/PV-front metrics; disallow width ranges and seasonal playback.

## Verification and remaining gates

Offline width provenance check, 19 width tests and 17 dashboard tests pass.
Both-current browser checks cover labels, hidden bar/locator, disabled playback,
static route context, saved record reload, atlas return, 27-row inventory and
320 px reflow. Screenshot inspected. Canonical SHA256 unchanged:
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.

Open: extract region/branch/neutral-layer edges and matched occupation support;
resolve source-general scale applicability before scientific admission. No
secondary southern jet width or annual extrema admitted. No full default suite,
clean checkout, commit, release or publication gate run.
