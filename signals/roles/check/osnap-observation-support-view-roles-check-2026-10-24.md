---
skill: roles-check
topic: osnap-observation-support-view
date: 2026-10-24
source_commit: 00d8a759736568f0a906105435aebdad8937226c
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 7
p3_count: 14
verdict: APPROVED-WITH-CONDITIONS
---

# Observation-support viewer: prospective functional review

One assistant applies the seven relevant repository lenses to the new
`almanac/osnap-support.*`, browser checker, workflow and retained audit evidence.
The source commit identifies the working-tree base; the actual scientific
support case executed at `7b92bfdf3222070e996a8e80bd8bb3e80e75433f` in successful
run `40093031002`. No independent review or current-measurement approval is
claimed. ORBIT is excluded because no planetary analogy is involved.

## Findings

| # | Lens | Severity | Evidence / finding | Action |
|---|---|---|---|---|
| 1 | CURRENT | P3 | Four separate stages distinguish custody, headers, paired availability and current dimensions. | Preserve these stages in dashboard integration. |
| 2 | CURRENT | P3 | ADCP moving-depth extrema and point-meter pressure proxies are kept separate; no pressure-to-depth conversion or width is displayed. | Retain unit and layer qualifiers. |
| 3 | CURRENT | P2 | A finite velocity pair is not physical QC, common-layer support or coverage of both edges. | Keep explicit nonapproval text; freeze a later dimension method after support review. |
| 4 | SOUNDER | P3 | Both header and support JSON bytes are checked against their exact execution review hashes before rendering. | Reject mismatches without showing a partial verified inventory. |
| 5 | SOUNDER | P3 | Support records join to original member name and SHA, including both extensionless files. | Assert all 78 exact member identities in cloud. |
| 6 | SOUNDER | P2 | Instrument license text and the repository license link differ; exact timing contains float64 boundary offsets. | Preserve both license statements and original times; do not infer permission or snap timestamps in the viewer. |
| 7 | CHART | P3 | Timeline shows header spans separately from monthly paired-cell fractions. | Keep visible text and a monthly count table equivalent. |
| 8 | CHART | P3 | No mooring point is turned into a current boundary or state intersection. | Add any later observation map only after position consistency and footprint review. |
| 9 | CHART | P2 | Monthly marks encode counts aggregated across moving bins, not a fixed water layer. | Retain the denominator and moving-depth explanation; do not reuse this mark as seasonal width. |
| 10 | BEACON | P3 | Source dates explicitly do not establish continuous velocity observations. | Preserve that sentence beside the timeline. |
| 11 | BEACON | P3 | All 78 complete time arrays are distinguished from 48.4%–73.1% ADCP paired-cell availability. | Keep both facts together in summaries. |
| 12 | BEACON | P2 | Detailed count tables require a clear path back to the original study and processing. | Keep DOI, original headers, custody, audit and method links visible. |
| 13 | HARBOR | P3 | Native selects, search, buttons and details provide keyboard controls; monthly tables expose exact counts. | Exercise these actual controls in cloud. |
| 14 | HARBOR | P3 | SVG/canvas is unnecessary; decorative bars have hidden semantics and full text equivalents. | Retain zero/missing cases as explicit text. |
| 15 | HARBOR | P2 | Actual 320/390-pixel reflow, focus and contrast have not been inspected yet. | Require cloud browser screenshots and inspect them before public navigation integration. |
| 16 | KEEL | P3 | Browser gate runs in the shared serialized cloud queue with no source download or native/WASM build. | Run after the completed sample audit; do not run a local browser. |
| 17 | KEEL | P3 | Checker covers counts, source names, extensionless files, filters, empty search, keyboard, phone overflow and checksum corruption. | Retain receipts and screenshots from the actual run. |
| 18 | KEEL | P2 | JavaScript and Python syntax checks do not establish runtime correctness. | Complete the cloud browser gate; fix operational viewer defects without changing executed scientific v1 files. |
| 19 | LOGBOOK | P3 | Actual sample report and new execution review are retained without rewriting the original prospective records. | Keep all 17 scientific freeze inputs unchanged. |
| 20 | LOGBOOK | P3 | No query packet, current dimensions, seasonal physical ranges or scientific release is changed here. | Batch later query-index and public-navigation integration after the viewer gate. |
| 21 | LOGBOOK | P2 | This is one source deployment; the overall catalogue still has substantial current/eddy gaps. | Continue prioritized physical measurement work and keep the full goal active. |

## Synthesis

Roles: 7. P1: 0. P2: 7. P3: 14. **APPROVED-WITH-CONDITIONS for cloud
viewer validation**, not public UI admission or scientific release.

CURRENT, SOUNDER and CHART agree that availability cannot be promoted to
physical validity or width. BEACON and HARBOR agree that monthly exact counts
and stage labels must accompany visual marks.

Three amendments incorporated: exact source/member hash parity before display;
header-date and monthly-availability separation with count tables; and a
separate cloud browser/corruption/reflow gate after the source audit. Public
dashboard links remain pending that gate and screenshot review.
