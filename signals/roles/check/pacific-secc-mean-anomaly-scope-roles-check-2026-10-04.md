---
skill: roles-check
topic: pacific-secc-mean-anomaly-scope
date: 2026-10-04
source_commit: 759246d4fcab441a77eb965fbcea80bc91f08968
working_branch: codex/dated-section-maps
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Pacific SECC source and measurement-rule review

Internal functional review of the full-paper scope audit, worklist action,
protocol clarifications, downstream receipts and query card. CURRENT checks
physical definitions; SOUNDER checks source access/identity; CHART checks spatial
support; BEACON checks explanation; HARBOR checks access; KEEL checks reconstruction;
LOGBOOK checks admission/delivery. ORBIT excluded without a planetary comparison.
This is not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | A velocity-anomaly zero contour cannot define a total-flow edge. | P2, resolved | Figure 8 branch explicitly classified as band-passed anomaly; extraction admission false. Clarified both length and width protocols. |
| 2 | CURRENT | Surface and upper-layer mean geostrophy describe different support. | P3, verified | Figure 1a surface and 1b 0-200 m records remain separate. Preserve reference state and layer. |
| 3 | CURRENT | Modeled Sverdrup flow cannot become an observed current axis. | P3, verified | Figure 1c retains its assumed upper-layer allocation and model quantity. No geometry or width admitted. |
| 4 | SOUNDER | Actual full-paper access must differ from the newer preview. | P3, verified | University PDF acquired and SHA pinned; 2026 methods remain unacquired. Two separate source audits preserved. |
| 5 | SOUNDER | Climatology release labels are not observation periods. | P3, verified | WOA01 product named, exact combined observed period null. Figure 8 duration retained without invented dates. |
| 6 | SOUNDER | Referenced historical studies were not independently inspected. | P3, verified | Historical comparison labels underlying originals uninspected. No original-measurement extraction claimed. |
| 7 | CHART | Averaging-domain limits are not current endpoints or paired edges. | P3, verified | Figure 2 box retained solely as averaging support; dimensions/axis/edges null. Keep geometry absent. |
| 8 | CHART | Regional latitude descriptions cannot establish full width. | P3, verified | Paragraph 2 band labelled regional context. No envelope rectangle, midpoint axis or width assigned. |
| 9 | CHART | Different fields cannot be combined into a synthetic seasonal map. | P3, verified | Mean/reference/anomaly/model distinctions retained; compatibility review required before addition or tracing. |
| 10 | BEACON | Existing generic worklist wording omitted the newly known method distinction. | P2, resolved | Next action now requests compatible numerical total-flow axes/boundaries and retains unacquired 2026 methods. Card verified. |
| 11 | BEACON | Source audit links ran together visually. | P2, resolved | Source/audit links now use the existing spaced record-links container. Preserve short evidence access. |
| 12 | BEACON | A completed source read could imply completed dimensions. | P3, verified | No contour trace/numerical field acquisition claimed; null lengths/widths and explicit remaining gates. |
| 13 | HARBOR | Additional audits must remain keyboard-accessible. | P3, verified | Native details/summary opens the new full-paper audit; existing route query keyboard/mobile checks retained. |
| 14 | HARBOR | Source access and limitations must be available as text. | P3, verified | Card displays access level and field distinctions; complete original audit available independently of map/color. |
| 15 | HARBOR | New evidence must stay reachable from current and worklist cards. | P3, verified | Existing reciprocal query/card links preserve owner ID; two audits loaded into the same decision. |
| 16 | KEEL | Protocol clarification changes pinned provenance. | P3, verified | Stale provenance failed visibly; section diagnostic, width/season inventories, catalog/dashboard/bundle/engine regenerated. No checksum bypass. |
| 17 | KEEL | Receipt refresh could alter old measurements inadvertently. | P3, verified | Baseline comparison proves unchanged numeric widths, dates, seasonal geometries and admission flags; inventory changes only receipts. |
| 18 | KEEL | Old source-card expectation used stale prose. | P3, verified | Updated assertion checks numerical-flow next action, unresolved 2026 methods and new PDF-access disclosure. Native/WASM/source binding checks retained. |
| 19 | LOGBOOK | Source PDF is not a public redistribution artifact. | P3, verified | Stored under existing ignored source-data PDF rule; public audit contains URL, checksum and limited factual scope. |
| 20 | LOGBOOK | Counts must not imply new scientific admission. | P3, verified | 62 candidates/59 names, 30 unbuilt, 37 width records/24 names and 105 samples unchanged. Canonical release unchanged. |
| 21 | LOGBOOK | Local snapshot must remain separate from main. | P3, verified | Addition remains uncommitted with the local map/playback slices on codex/dated-section-maps. Full remote CI has not run for these additions. |

Synthesis: seven roles; zero open P1/P2 issues, 18 P3 notes. Conditional approval
for editorial source/worklist enrichment. CURRENT/CHART/SOUNDER agree that
total-flow, relative-reference and anomaly support must remain distinct.

Amendments: explicit mean/anomaly/model field taxonomy; consistent protocol
clarification with refreshed dependency receipts; source-specific next action
and spaced evidence links. Verification: 22 Rust tests, 66 focused Python checks
and 428 subtests, unchanged-value comparison, source/bundle/engine hashes,
source-card render/access inspection, worklist native/WASM/card checks and
recorded-section playback regression. No new length, width, annual extrema or
season calendar admitted. Full CI and independent scientific admission remain open.
