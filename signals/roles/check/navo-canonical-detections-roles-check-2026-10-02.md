---
skill: roles-check
topic: navo-canonical-detections
date: 2026-10-02
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# NAVO canonical dated detections: repository review

Artifact: canonical data and schema change, not publication approval. Reviewed
the release builder, checker, taxonomy, pinned NAVO receipt and state join,
methods, changelog, and screening behavior. Selected CURRENT for physical
identity, SOUNDER for provenance, CHART for coordinates/state geography,
BEACON for interpretation, HARBOR for equivalent evidence access, KEEL for
reproducibility, and LOGBOOK for release boundaries. Applied the installed
`.roles` verification lenses in this task; no independent human scientific
or accessibility approval is implied.

| Role | Finding | Severity | Evidence and recommendation |
| --- | --- | --- | --- |
| CURRENT | A designation in one receipt does not prove a persistent eddy identity. | P3 | IDs include provider/date/code; `dated_detection` explicitly excludes lifetime and historical-name equivalence. Retain that limit in future object pages. |
| CURRENT | Provider warm/cold and rotation fields remain source labels. | P3 | No density, depth, transport, or formation mechanism is inferred. Preserve the separate provider fields. |
| CURRENT | Snapshot support does not establish temporal behavior or depth. | P3 | Both are unresolved; the observation date is explicit. Do not classify an entire lifetime from one receipt. |
| SOUNDER | Geometry bytes are tied to the frozen package. | P3 | ZIP digest and receipt source ID accompany each unmodified polygon. Keep live downloads out of default builds. |
| SOUNDER | Coordinate datum is unspecified. | P2 | ZIP has no `.prj`; JSON/CSV retain the uncertain longitude/latitude interpretation. Obtain source metadata before declaring CRS84. |
| SOUNDER | Public-release text does not resolve the recorded reuse decision. | P2 | Source remains pending and is excluded from screening. Resolve the item-specific decision before public redistribution. |
| CHART | Full rings, not simplified outlines, support the state join. | P3 | Checker compares every polygon with the receipt and regenerates the existing join. Preserve the separate display simplification. |
| CHART | OSW states are approximate display geometry. | P3 | Existing relation limit and methods retain that fact. Containment is product/date/state-geometry specific. |
| CHART | Uncertain datum cannot silently become standard GeoJSON. | P3 | Only CRS84 records enter `geometries.geojson`; coverage lists four omitted IDs. Keep the omission explicit. |
| BEACON | Detection totals must remain separate from named-eddy totals. | P3 | Full candidate adds four `operational_eddy_detection` entities; 136 named-eddy records remain unchanged. Avoid summing these as a named inventory. |
| BEACON | No NASA event identification follows from the dated polygons. | P3 | No NASA identity edge or dated-media match is added. Any later movie link must state regional context and time mismatch. |
| BEACON | The documentation describes the scientific limit. | P3 | Methods separate designations, tracks, lifetime, footprint dates, and state approximations. Carry these limits into presentation. |
| HARBOR | Geometry meaning has a textual alternative. | P3 | JSON/CSV observations give state, date, relation and scope; the methods explain the polygon class. Preserve that alternative in future UI. |
| HARBOR | No interface controls were changed in this tranche. | P3 | Browser interaction behavior is outside this change; package/site checks cover generated data compatibility. Test controls when detection pages are introduced. |
| HARBOR | Human accessibility review remains a publication condition. | P2 | Canonical validation is not screen-reader review. Keep the existing release gate open. |
| KEEL | Detection references previously had no canonical entity. | P3 | Four entity rows and geometry references now close the graph. Claim subjects must resolve to entities or canonical tiles. |
| KEEL | Earlier identifiers must not shift. | P3 | New names/geometries are appended; comparison verified all 14,244 existing claim IDs and fingerprints unchanged. Retain append discipline until stable-ID redesign. |
| KEEL | Full polygon CSV cells exceed the default reader limit. | P3 | Checker uses a bounded 16 MiB field limit and verifies CSV/JSON parity. Keep full rings instead of substituting render outlines. |
| LOGBOOK | Full candidate and screened copy differ deliberately. | P3 | Full: 317 entities/154 geometries; screened: 217/147. Added detections and polygons remain excluded. Record both scopes. |
| LOGBOOK | No release or DOI has been published. | P2 | Candidate status, pending source decisions, science review, and publication authority remain open. Do not describe this as an official provider atlas. |
| LOGBOOK | Build documentation and canonical exports are aligned. | P3 | Methods/changelog are copied into the manifest-covered release. Rebuild downstream screening/site after changes. |

Roles reviewed: 7. P1 blockers: 0; P2 conditions: 4; P3 findings: 17.
Verdict: APPROVED-WITH-CONDITIONS for internal canonicalization. CURRENT and
SOUNDER agree that dated source identity is not continuous identity; CHART
and SOUNDER agree that longitude/latitude interpretation is not a known datum.

Three amendments implemented:
1. Add dated entities and unmodified geometry records, with explicit unknown
   depth/temporal behavior and no historical-name join.
2. Exclude uncertain-datum polygons from CRS84 GeoJSON, report their IDs, and
   validate source equality, closure, validity, bounds, and geometry references.
3. Preserve existing claim identities and retain pending-source screening;
   explicitly check that no NAVO detection/polygon reaches the screened copy.

Verification: full release check passes (317 entities, 5,702 relations).
All 14,244 prior claim IDs and fingerprints were compared and preserved.
The regenerated rights-screened preview check passes (217 entities, 8,635
claims), including explicit exclusion of all four detections and polygons.
The isolated screened-site check passes (267 files, 217 objects, 70 NASA
crops). No browser code was changed, so no new interaction test was required
for this data-only admission. Existing full-atlas rendering is not asserted
to consume the new canonical geometry table by these checks.
