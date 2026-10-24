---
skill: roles-check
topic: south-java-layer-evidence-v1
date: 2026-10-24
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# South Java layer evidence and derived diagram

Artifact: primary-publisher prose annotations, typed model quantities and a
derived diagram. These seven internal review lenses are not independent peer
review. CURRENT covers physical class; SOUNDER source identity; CHART numerical
encoding; BEACON interpretation; HARBOR equivalent access/resource use; KEEL
generation; LOGBOOK working-versus-published state. ORBIT is excluded: no analogy.
Approval covers retained source facts/diagram, not new physical dimensions or
query-packet admission. Query integration remains a separate pending step.

| # | Role | Finding | Severity | Section | Disposition |
|---|---|---|---|---|---|
| 1 | CURRENT | Analysis layer bounds can look like measured thickness. | P2 | Layer definitions | Distinct analysis-layer quantity and explicit non-thickness labels on both facts and diagram. |
| 2 | CURRENT | Surface and undercurrent evidence must remain separate. | P2 | Records | SJCU context is not assigned to the surface current; no new current identity admitted. |
| 3 | CURRENT | The100m threshold-depth cap is not an exact current edge. | P2 | Threshold record | Strict5cm/s criterion, null exact edge and an upward cap arrow retained. |
| 4 | SOUNDER | Full-text prose is available without original-file custody. | P2 | Source | Publisher URL/DOI, reviewed paragraphs and access mode recorded; no invented checksum. |
| 5 | SOUNDER | Model mean context must not become observed seasonal data. | P2 | Support | OFES, analysis years, zonal component and four section meridians are explicit. |
| 6 | SOUNDER | Approximate source depths lack numerical uncertainty. | P2 | Depth records | Approximation flags retained; errors and annual ranges remain null. |
| 7 | CHART | Colored bands might be read as physical flow footprints. | P2 | Left panel | Panel title identifies author-defined analysis bands; scope caveat remains above and below. |
| 8 | CHART | Markers could imply horizontal locations or widths. | P2 | Right panel | Horizontal positions are schematic; no horizontal distance axis. |
| 9 | CHART | A depth cap could be confused with an exact boundary. | P2 | Right panel | Dashed cap plus upward arrow and explicit upper-limit wording; no reconstructed contour. |
| 10 | BEACON | SJCC/SJCU abbreviations need explanation. | P3 | Band labels | Expanded surface-current and undercurrent labels in the inspected diagram. |
| 11 | BEACON | A later100–200km mention could inherit a misleading primary citation. | P2 | Exclusions | Width remains unverified from reviewed primary prose; no width value admitted. |
| 12 | BEACON | Definitions, summaries and physical quantities need plain distinctions. | P3 | Titles/caption | Model-study classification is separated from core depths and threshold limit. |
| 13 | HARBOR | Palette alone cannot distinguish layers and quantities. | P2 | Diagram | Text labels, approximate markers and dashed/arrow cap provide redundant encoding. |
| 14 | HARBOR | Standalone SVG needs accessible meaning. | P2 | SVG root | Root title/description and retained machine-readable source facts accompany visible labels. |
| 15 | HARBOR | Plotting must honor the resource constraint. | P2 | Execution | One BelowNormal CPU, one numerical worker; no original fields, browser or build job. |
| 16 | KEEL | Unseen original figures cannot support digitized edges. | P2 | Extraction | Only explicit primary prose is annotated; no figure extraction or new distances. |
| 17 | KEEL | Figure/data provenance must be reproducible. | P2 | Manifest | Source/renderer/SVG hashes, plotting environment and fixed SVG IDs recorded. |
| 18 | KEEL | A derived diagram needs actual visual inspection. | P2 | QA | Raster inspected; band labels, caps and source text are legible. Metadata-only SVG amendment preserves the inspected raster. |
| 19 | LOGBOOK | Local source inventories trail the delivered packet. | P2 | Plan | Local102-name/100-decision ledger distinguished from delivered106-current metadata. |
| 20 | LOGBOOK | New annotations must not rewrite executed science/UI inputs. | P2 | Checkpoint | Preserve83 scientific,23 runtime and20 verified UI inputs; separate source files and figure. |
| 21 | LOGBOOK | More contextual facts do not close the physical width gap. | P2 | Status | Width/depth envelope/state eligibility remains absent; working query records still pending. |

Roles reviewed:7. P1 blockers:0. P2 issues:19; P3 notes:2. All source/diagram
dispositions are reflected in the artifact. Cross-role consensus from
CURRENT/SOUNDER/CHART: model-layer definitions are not observed dimensions.
HARBOR/KEEL require the small serial render and actual inspection. Three
amendments completed: expanded abbreviations; accessible root SVG description;
fixed SVG IDs/environment provenance. Condition: retain evidence class and
unknown fields during later query integration; no width or physical thickness
admission is authorized by this source review.
