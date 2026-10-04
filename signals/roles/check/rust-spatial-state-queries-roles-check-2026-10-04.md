---
skill: roles-check
topic: rust-spatial-state-queries
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 0
p3_count: 17
verdict: APPROVED-WITH-CONDITIONS
---

# Rust spatial state query review

Artifacts: state geometry import, pinned geo topology, Rust result/map scene,
query modes, source relation metadata and native/browser/oracle tests. Role selection:
CURRENT physical meaning; SOUNDER source custody; CHART geometry/encoding; BEACON
wording; HARBOR equivalent access; KEEL reproducibility; LOGBOOK status. Role
definitions were read in this conversation. ORBIT is inapplicable. This is internal
review using role lenses, not independent scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Polygon coverage could be mistaken for containment of an entire named current or eddy family. | P3 | Predicates | Use whole stored polygon covered by display state; point locators/gateways have separate modes. |
| 2 | A route length convention must survive spatial migration. | P3 | Reference lines | Use existing WGS84 legs densified at <=10 km; topology is planar and never supplies metric dimensions. |
| 3 | Dated proxy polygons and datum-unspecified provider shapes carry different physical uncertainty. | P3 | Evidence | Retain role, observation date, datum status, source IDs and positional uncertainty in computed relation records. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New state geometry could omit the established land subtraction or holes. | P2 | Import | Use original SVG shapes and existing masked-state loader; preserve components and holes. Independent source-coordinate oracle agrees. Addressed. |
| 2 | A geometric contact could undo the source semantic exclusion of Black Sea routes. | P2 | Classification | Default queries honor exclusions; include_excluded exposes raw contact with explicit reason. Both cases tested. Addressed. |
| 3 | Densification and masked-state imports add transformation dependencies. | P3 | Custody | Pin SVG, route candidates, helper hashes, Shapely and pyproj versions in bundle manifest; candidate hashes must match. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Longitude seam handling could produce false intersections in distant states. | P3 | Topology | Unwrap feature longitudes and evaluate adjacent periods; hole, edge and seam unit fixtures pass. |
| 2 | The map could imply every geometry of a matching object met the state predicate. | P2 | Encoding | Brighten matched features, dim other geometry as context and outline the selected state. Browser assertions and screenshot pass. Addressed. |
| 3 | Intersects includes touching boundaries; within uses coverage including boundary. | P3 | Definition | Declare DE-9IM meaning, expose boundary_touch_only, and keep source precision limits. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Recorded state links and computed geometry are different operations. | P3 | Controls | Separate recorded mode from four spatial predicates; structured queries may combine them explicitly. |
| 2 | A stale hover caption from a previous query could name an object absent from results. | P2 | Map caption | Reset hover text on each rendered scene. Addressed. |
| 3 | No spatial match is not evidence that a current never passes through the state. | P3 | Scope | Missing geometry and editorial support cannot establish physical absence; retain scope near controls and in relations. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | New state mode needs keyboard, visible labels and disabled behavior outside motion objects. | P3 | Access | Label native select, preserve keyboard controls and disable spatial modes for other collections. |
| 2 | Highlight color alone could hide the predicate match. | P3 | Alternatives | Result rows name computed geometry roles; inspector provides relation records and map labels say matches/context only. |
| 3 | New fieldset row could regress mobile reflow. | P3 | Layout | Repeat 320 px overflow verification and screenshots after adding controls; human accessibility review remains pending. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Native/WASM parity alone cannot detect a shared geometry bug. | P3 | Oracle | Compare 20 actual-state queries to original SVG/Shapely display-coordinate topology plus default/raw exclusion checks. |
| 2 | Offline resolver selected an unextracted transitive dependency. | P3 | Build | Pin Cargo.lock smallvec 1.15.1 from existing cache; offline native/WASM builds pass without escalation. |
| 3 | Geometry changes could invalidate prior inventory behavior. | P3 | Regression | Repeat existing query, 100/240 map inventory, scoped evidence, share/export, pagination, invalid-load and mobile checks. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Earlier contract says spatial predicates are future work. | P3 | Status | Update contract/README with implemented modes and leave revisioned writes, native image export and shared renderer pending. |
| 2 | Canonical admission must remain unchanged during a Rust import. | P3 | Release | Preserve canonical almanac checksum; imported/derived queries remain local working evidence. |
| 3 | Focused local validation does not establish a full public release. | P3 | Gates | Keep independent science, human accessibility and clean-checkout/publication gates separate. |

## Synthesis

Seven roles, 21 findings: zero P1, four addressed P2, seventeen P3. Approved with
conditions for local display-geometry querying. Top finding: computed spatial
contact must retain land masks, holes and source semantic exclusions. CURRENT,
SOUNDER and CHART agree that topology on approximate state shapes is not physical
passage or confidence in occupancy.

## Three amendments

1. Import original masked state polygons and retain holes; verify Rust independently
   against Shapely on original SVG coordinates rather than only the imported bundle.
2. Preserve route semantic exclusions and dated geometry custody fields in computed
   relations; raw excluded contact is explicit and opt-in.
3. Separate recorded and spatial modes, show the selected state/matching geometry,
   and reset captions when query results change.

## Evidence and conditions

Seven Rust tests pass, including holes, boundary coverage, separate point/gateway
modes, periodic seam contact and invalid coordinates. Twenty actual-state topology
queries plus two exclusion modes agree with the original SVG/Shapely oracle.
Native/WASM parity and UI controls/inspection/state highlights, existing 100/240
inventory behavior, shared query/download, errors/pagination/mobile and rejected
integrity load pass. Source dates, datum uncertainty and source/geometry IDs are
preserved for covered NADR NAVO polygons. Spatial-map screenshot was inspected;
final browser run regenerates it after the stale caption repair.

Canonical almanac SHA256 remains
`6c8a143208c0953512875f222154a819d5f56b7326daa6816f0609e61b4f261e`.
Revisioned writes, graph traversal, spatial indexing for scale, seam polygon
rendering, shared map library and image export remain open. Independent science,
human accessibility and full clean-checkout/public release are separate gates.
