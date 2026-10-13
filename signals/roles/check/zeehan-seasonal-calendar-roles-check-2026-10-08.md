---
skill: roles-check
topic: zeehan-seasonal-calendar
date: 2026-10-08
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Zeehan qualitative seasonal calendar review

Artifact: primary-source editorial extraction, Rust receipts, source queries,
atlas calendar and dashboard fingerprints. Selected CURRENT (physics), SOUNDER
(provenance), CHART (visual evidence), BEACON (public explanation), HARBOR
(access), KEEL (validation), LOGBOOK (publication). ORBIT excluded: no analogy.
Internal role review does not constitute independent scientific admission.

| Role | Finding | Severity | Location | Resolution |
|---|---|---|---|---|
| CURRENT | An equatorward anomaly cannot establish absolute current reversal. | P2 | Claim summer-anomaly | Separate reference state and explicit explanation. |
| CURRENT | Property fields cannot define a measured current axis. | P2 | Claim summer-indication | Indirect category; numeric edges and geometry null. |
| CURRENT | Persistence endpoint is qualified, not a disappearance date. | P2 | Claim winter-persistence | At-least qualifier and editorial interval assignment preserved. |
| SOUNDER | Sole author must not be conflated with the 2004 route authors. | P2 | Source and map context | K. R. Ridgway (2007); route Ridgway & Condie (2004). |
| SOUNDER | HTML review has no pinned original response. | P2 | Source access | Explicit unpinned bytes, null response hash/license; no copied original. |
| SOUNDER | Operators use different source periods. | P2 | Field context | Altimetry, CMDT, SST mean and historical CARS kept separate. |
| CHART | Calendar categories could imply quantitative strength. | P2 | Card introduction | No numeric scale; text categories and source locators. |
| CHART | Selecting a month could imply seasonal route morphing. | P2 | Map context | Static 2004 route retained; geometry playback ineligible. |
| CHART | Occupied seasonal geometry remains missing. | P3 | Unresolved list | Followup requires numerical compatible fields/sections. |
| BEACON | Reader needs a direct path from claim to original source. | P2 | Calendar | Per-claim locator, original paper link and six-claim query link. |
| BEACON | Peak should not become invented speed or dimensions. | P2 | Calendar scope | Values null; numerical strength explicitly unspecified. |
| BEACON | Repeated month entries may be mistaken for samples. | P2 | Protocol | Month indexes reference six claims; observation count unchanged. |
| HARBOR | Month controls need keyboard and screen-reader state. | P2 | Controls | Native buttons, pressed state, live text; tested keyboard activation. |
| HARBOR | Selected state must not rely on color. | P2 | Controls | Checkmark plus bold text and aria-pressed. |
| HARBOR | Narrow buttons initially wrapped month names. | P2 | Mobile controls | Reduced horizontal padding, nowrap, explicit overflow check; rechecked at 320 px. |
| KEEL | Coherent receipt changes must not admit invented measurements. | P2 | Rust guard | Full compiled audit binding, protocol receipt and planning-document agreement. |
| KEEL | Browser check must be discoverable in CI. | P2 | Browser runner | Registered calendar check; Python mutation checks reject changed scope. |
| KEEL | Remote fixture acquisition remains unreliable. | P3 | Parent PR57 | Both offline jobs failed; later log confirms existing Qiu/Chen timeout before tests. Gates preserved. |
| LOGBOOK | Source-derived evidence must remain explicitly editorial. | P2 | Audit status | Pending independent review status retained. |
| LOGBOOK | Dashboard must update only the intended owner. | P2 | Snapshot diff | Exactly Zeehan changed; sources/time-evidence fingerprints update, zero new observation samples. |
| LOGBOOK | Whole-project core gaps remain open. | P3 | Batch record | Width/length/occupied seasonal geometry unresolved; no project-complete claim. |

21 findings: 18 P2 addressed; three P3 followups; no P1.
Verdict: APPROVED-WITH-CONDITIONS, subject to recorded validation and independent
scientific review before any stronger admission. Cross-role consensus: retain
reference states, calendar qualifiers and static geography separately.

Amendments: (1) preserve anomaly/mean and indirect/direct distinctions;
(2) bind the reviewed source document through query and atlas receipts;
(3) make month controls readable at 320 px and selection perceivable without color.
