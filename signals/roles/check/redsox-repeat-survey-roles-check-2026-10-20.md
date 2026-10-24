---
skill: roles-check
topic: redsox-repeat-survey
date: 2026-10-20
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Repeat-survey observations review

Source base720135e593403fcb8d691b92531f1560bae569de; reviewed the working
repeat-survey batch and its v1 preflight. Internal functional review, not
external scientific peer review. CURRENT/SOUNDER cover physical meaning and
custody; CHART/BEACON/HARBOR cover figures, claims and access; KEEL/LOGBOOK
cover reproduction, preservation and the same continuing draft PR. ORBIT is
not selected: no planetary comparison is made.

| Role | Finding | Severity | Action/evidence |
|---|---|---|---|
| CURRENT | Different winter/summer branches cannot define one width change. | P2 | Addressed: six same-branch comparisons; all differences null. Positive and failed comparison paths tested separately. |
| CURRENT | Summer candidate fails the existing38psu screen. | P2 | Addressed: no lower replacement threshold; failed screen beside3.1km in figure, card, table and source records. No current-absence inference. |
| CURRENT | Candidate is only slightly above the speed floor and loses eligibility under−0.04m/s. | P3 | Retain all finite scenarios and the failed case; no confidence interval or physical-width admission. |
| SOUNDER | Source text-object order can misidentify the transect panel. | P2 | Addressed: visually checked Figure7 top title/stations on page19; source receipt pins original PDF. |
| SOUNDER | Summer22 has authored bad-upcast treatment uncertainty. | P3 | Exclude from peak and crossing support; preserve tag/note and do not infer treatment from downf. |
| SOUNDER | Repeated stations are nearby, not identical or simultaneous. | P3 | All twelve original position pairs/separations and clocks retained; no cross-date resampling. |
| CHART | Preliminary component axis clipped negative summer observations. | P2 | Corrected before publication: common limits derive from all retained layer values, including exclusions. |
| CHART | A legend obscured the winter peak. | P2 | Corrected: shared component legend occupies clear summer upper-left space. Final rendered figure inspected. |
| CHART | Lines could visually bridge excluded velocities or missing CTD. | P3 | NaN gaps; excluded layer values use crosses, not joining lines; salinity74 remains missing. |
| BEACON | A two-date plot could be read as seasonal climatology. | P2 | Addressed in title/caption and card note: dated surveys, no annual margins or climatology. |
| BEACON | The roughly3.1km candidate could be retold as verified current breadth. | P3 | Candidate/failed-screen label accompanies every public summary; whole-current width remains null. |
| BEACON | Scientific screen failure could be read as absent flow. | P3 | Explicit note: no absence inference; association/tides remain unresolved. |
| HARBOR | Palette alone cannot identify layers or excluded data. | P3 | Distinct markers/line styles/crosses; SVG title/description and branch-separated table. |
| HARBOR | New analysis view needs keyboard access. | P3 | Dedicated browser gate must select both winter/repeat views from the existing native control. |
| HARBOR | Table and queries need narrow-screen/data access. | P3 | Browser gate covers320px, source export, all30cases and six comparison records. |
| KEEL | A method refactor could silently rewrite winter evidence. | P3 | Frozen generator/report unchanged; explicit station-renaming parity regression covers30cases. |
| KEEL | Report/figure changes must invalidate the research graph. | P3 | Frozen pins, rebuilt report equality, asset byte/hash verification and corruption checks. |
| KEEL | Current-head reproduction cannot be inferred from base14target success. | P3 | New target15; keep its Linux and complete-suite statuses separate. |
| LOGBOOK | Existing source inputs and official measurements must remain unchanged. | P3 | Preserve old REDSOX reports and canonical inventories; compare all unrelated objects/collections before publication. |
| LOGBOOK | User rejected a PR per gap. | P3 | Same draft PR83; no main merge or new PR. |
| LOGBOOK | Remaining gaps must remain visible despite added observations. | P3 | No whole-current/annual/physical state admission; running full predates new batch and is not relabeled. |

Seven roles; zero P1, nine P2 addressed, sixteen P3 notes. Verdict:
APPROVED-WITH-CONDITIONS. Complete focused, locked native/WASM, actual-browser,
preservation and committed-pin checks before publishing the draft update.
Final clean full/remote gates remain conditions for any later merge/admission.

Amendments: preserve branch identity and failed screens; correct clipping and
legend placement; keep frozen winter bytes and actual gate scope explicit.

## Structured inventory follow-up

| Role | Finding | Severity | Action/evidence |
|---|---|---|---|
| CURRENT | Typed records could relabel local component spans as physical widths. | P2 | Explicit local metric; whole-current/annual fields null and admission/association/ranking false. All failures remain records. |
| KEEL | Source-document integrity alone does not protect normalized query records. | P2 | Independent Rust reconstruction of all60cases, source/schema/adapter pins and exact current-owner ID binding; edits, deletion, duplication, orphaning and promotion reject. |
| HARBOR | A generic table could omit the numeric value and its failed screen. | P2 | Explicit value/scope formatter, main query link, primary filter, keyboard and320px browser gate. |
| LOGBOOK | Reusing the existing Antilles-specific collection would change its contract. | P3 | Separate shared schema and unchanged Antilles data; preservation includes the original collection. |

Terminal follow-up: 29 focused checks and 81 Rust tests pass; locked builds
and native atlas pass. Actual browser/native results agree on all 30 summer
cases, six null comparisons, twelve pairs and 60 typed records. The primary
filter returns four cases; source/atlas links, table values, both analysis
views, export and 320px reflow pass without original requests or page errors.
701 staged pins verify. All fourteen prior scientific reports and unrelated
data collections remain exact. Linux target15/full-suite status is retained
separately; this remains internal review for a draft update.
