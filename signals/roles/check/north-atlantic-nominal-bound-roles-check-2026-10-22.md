---
skill: roles-check
topic: north-atlantic-nominal-bound
date: 2026-10-22
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# North Atlantic nominal-section bound: internal review

Base commit: `8709da980941bcc985737f1fd42b41b1cf7c6029`; reviewed the new
protocol, producer, original XML, working admission, scalar figure, native
validator and mapped-card/query integration. This is an internal functional
review, not external scientific peer review. These seven roles apply to the
Earth current data, presentation and repository; ORBIT has no comparison to
review in this batch. Role definitions: `.roles/ROLE.md` and individual files.

| Role | Finding | Severity | Evidence / required action |
|---|---|---|---|
| CURRENT | Nominal latitudes are not actual flow endpoints. | P2 | Protocol, assessment, measurement and figure explicitly condition the floor on nominal gates; physical-minimum flag false. |
| CURRENT | Separate cruises and layers cannot establish a continuous simultaneous axis. | P2 | Scope retains these distinctions; geometry, actual endpoints, observation time and fixed layer remain null. |
| CURRENT | Gate sensitivity cannot become physical annual variability. | P2 | Nine finite scenarios retain editorial interpretation; annual range and measurement uncertainty remain null. |
| SOUNDER | Original source and extraction locator must survive. | P2 | Original licensed publisher XML, acquisition time/URL/SHA and section 2/3.1.10 checks retained. |
| SOUNDER | Northern 53°N+58°N composite could be misread. | P2 | Eastern 58°N NAC passage supplies the gate; composite-section and nominal-position warning explicit. |
| SOUNDER | Six-decimal arithmetic is not physical precision. | P2 | Rounded 1,200 km conditional floor is primary; exact arithmetic and source precision remain separate. |
| CHART | Abstract zero-longitude computation must not create a mapped route. | P2 | Accessible scalar figure only; no geographic endpoint or axis admitted. |
| CHART | Existing illustrated arrow must retain its evidentiary class. | P2 | All existing illustrated-span fields survive the working assessment override. |
| CHART | Figure must carry its own scope without surrounding page text. | P2 | Nominal sections, source, unranked status, cruise/layer caveats and scenario interpretation are visible. |
| BEACON | Readers might repeat 1,200 km as whole-current length. | P2 | Conditional geographic floor and unranked wording accompany the number in figure and records. |
| BEACON | A regional evidence addition must not inflate completed-current counts. | P2 | Still 12 qualified ranked lengths of 101; 89 unranked. Width counts unchanged. |
| BEACON | Evidence needs a short path from the mapped current. | P2 | Existing North Atlantic card receives direct figure, assessment and complete-admission links. |
| HARBOR | A standalone SVG needs a named description. | P2 | Image role, title, description and redundant text convey the scalar result without color or pointer. |
| HARBOR | Disclosure and destination must work by keyboard. | P2 | Dedicated actual-browser check exercises disclosure, figure focus and Enter navigation; actual Chrome execution passes. |
| HARBOR | Nested data needs a usable narrow-screen equivalent. | P2 | Dedicated test checks 320px reflow and export availability for all four relevant queries; actual Chrome execution passes. |
| KEEL | Geographic calculation needs an independent arithmetic check. | P2 | Eight focused tests pass; WGS84 meridional-curvature integration checks all nine scenarios to 0.000001 km. |
| KEEL | Admission must reject edited values and stripped receipts. | P2 | Native validator and corruption tests cover rank, value, owner, source, annual range, missing rows and duplicates; all 112 Rust tests and native/WASM builds pass. |
| KEEL | Complete-suite release gate remains separate from scoped gates. | P2 | Open: local 4 GiB free-space guard unmet; prior remote offline acquisition failed before tests. No overall green claim. |
| LOGBOOK | Historical release and earlier scientific calculations must survive. | P2 | Before-batch fingerprints retained for frozen release and 26 existing reports/producers; all 163 preservation fingerprints pass. |
| LOGBOOK | Fresh cross-platform reconstruction is required for the added producer. | P2 | Added as target 27 in scientific reproduction CI; fresh Linux receipt pending. |
| LOGBOOK | User cannot manage a PR per gap. | P2 | This batch continues branch `codex/current-measurement-gaps` and draft PR83; no new PR/main merge. |

No current P1; 19 of 21 scoped findings resolved. Fresh Linux reconstruction
and the complete-suite release gate remain open. Draft-only approval with
verification conditions. Local native/WASM, browser and preservation checks pass. Fresh target-27
Linux reconstruction remains pending publication. The complete-suite release gate remains open even after scoped
verification. Amendments: make the nominal-position warning explicit; separate
finite gate scenarios from physical uncertainty; expose data and scalar
presentation directly from the existing current card.
