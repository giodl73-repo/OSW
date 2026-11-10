---
skill: roles-check
topic: redsox-section3
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dated REDSOX observed-section review

Source base: `cefddd5261d6df7f2f63f053939a11d4d8f49716`; reviewed the working
batch described in `plans/redsox-section3-observed-width-batch-2026-10-20.md`.
Internal functional checks, not independent scientific peer review. Select
CURRENT for physical interpretation, SOUNDER for provenance, CHART for the
bent section map, BEACON for public meaning, HARBOR for equivalent access,
KEEL for reproduction and LOGBOOK for continuing-PR/gate status. ORBIT is
excluded: there is no planetary comparison.

Each row records the check, evidence and required action. P2 findings below
are addressed in the working artifacts; remaining gate conditions are explicit.

| Role | Finding and evidence | Severity | Action/status |
|---|---|---|---|
| CURRENT | Chainage along a bent section is not physical flow-normal breadth; local normals vary (`component`, protocol). | P2 | Addressed: retain u/v, normal and obliquity; name component spans and explain projection dependence in batch record. |
| CURRENT | Northern peak search would require casts 61/63 despite unresolved references and rejected-downcast treatment. | P2 | Addressed: all fifteen northern cases null; no available-cast replacement. |
| CURRENT | One winter section cannot establish seasonal margins; tides remain in observations. | P3 | Confirmed: annual range null, tides_removed false; retain date and no physical admission. |
| SOUNDER | Station order must originate in an identified section, rather than selecting velocity peaks first. | P2 | Addressed: Figure 7(a), page 21, all twelve casts and prospective operator declaration pinned; prior exposure disclosed. |
| SOUNDER | Cast 74 lacks CTD; missing salinity cannot pass an association screen. | P3 | Confirmed: same-cast missingness preserved, salinity-null test; actual peak 73 has independent water-property support. |
| SOUNDER | Original Earth-frame velocity interpretation needed primary documentation. | P3 | Confirmed: exact 301-byte README checksum and semantics retained; no inference about upf/up=0. |
| CHART | Report image reuse would obscure the distinction between author contours and OSW calculations. | P3 | Confirmed: new source-data station map; original image not redistributed. |
| CHART | Connecting across missing velocities/salinities would create unsupported continuity. | P3 | Confirmed: NaN gaps on component and salinity curves; excluded stations marked on map. |
| CHART | The 12.6 km deeper-layer 40% result must remain visible. | P2 | Addressed: every finite scenario plotted; increased plot headroom prevents annotation covering the extreme point. |
| BEACON | New 5 km span could be mistaken for the previously reviewed bathymetric breadth. | P2 | Addressed: batch differentiates threshold crossing and bathymetry; public finding names date, layer and local component span. |
| BEACON | New section should not replace the older unresolved primary result. | P3 | Confirmed: distinct additional figure/table; older report and outcomes retained. |
| BEACON | A narrow scenario range could be retold as annual uncertainty. | P3 | Confirmed: all threshold/layer outcomes retained; public note explicitly names finite sensitivity and null annual range. |
| HARBOR | Layer distinctions cannot depend on palette alone. | P3 | Confirmed: distinct circle/square/triangle markers and line styles, SVG description and textual layer table. |
| HARBOR | New figure must be reachable without hover or pointer. | P3 | Browser gate must exercise summary via Enter and existing analysis selector. |
| HARBOR | Thirty cases need a textual data alternative at narrow widths. | P3 | Source-query export and 320px reflow are included in the dedicated browser gate. |
| KEEL | Float readback should not silently modify original observations. | P3 | Confirmed: explicit derived rounding, source coordinates restored exactly, original archives untouched; independent crossing checks pass. |
| KEEL | Existing primary data must survive this added section. | P3 | Fifteen focused tests pass; compare other collections and old source hashes before publication. |
| KEEL | A prior green suite cannot validate new content. | P3 | Condition: base full continues untouched; add new report to independent reproduction and record focused/build/browser terminals separately. |
| LOGBOOK | One PR per small gap is not the authorized workflow. | P3 | Confirmed: same branch/draft PR83; no main merge or new PR. |
| LOGBOOK | Public custody records must avoid private machine paths and original images. | P3 | Confirmed: public URLs/checksums only; no cached-image redistribution. |
| LOGBOOK | Local evidence is progress, not complete inventory/measurement coverage. | P3 | Confirmed: current-wide dimensions/annual range unresolved; broader work remains active. |

Roles reviewed: 7. P1 blockers: 0. P2 findings: 5, addressed. P3 notes: 16.
Verdict: APPROVED-WITH-CONDITIONS. Complete current native/WASM, browser,
preservation and source-pin checks before publishing this batch; keep draft
until final clean full and remote gates meet their actual recorded scope.

Amendments: (1) distinguish bent-section component spans from physical widths;
(2) keep northern, shallow-layer and CTD missingness explicit; (3) show all
sensitivities and correct figure headroom, with exact source queries and
separate current-batch validation receipts.

Terminal follow-up: 18 focused checks and 79 Rust tests pass; locked builds
and native atlas pass. Dedicated actual-browser checks pass all 30 cases,
keyboard/figure switching, clarified earlier/new labels, export and 320px
reflow without page errors or automatic original requests. Other43
collections/239objects/48diagnostics/386source documents are preserved.
The clean full suite still covers the base commit, and current-head remote
reproduction remains a separate required observation. Publication is a draft
update; this review is not a main-merge or physical-measurement admission.
