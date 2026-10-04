---
skill: roles-check
topic: ocean-motion-state-passport-evidence
date: 2026-09-30
roles_used: 5
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# State passport evidence display: role review

Artifact: the 56-state screened review atlas passports, with dated current
observations, named-eddy location candidates, NASA crop links, and per-state
download packets. CURRENT reviews physical meaning; SOUNDER provenance; CHART
cartography; HARBOR access; KEEL verification.

| Role | Finding | Severity | Section | Recommendation |
| --- | --- | --- | --- | --- |
| CURRENT | A local section observation cannot prove a current's whole path through a state. | P2 | Current list | Say local observation and whole-path unresolved beside dated rows. Done. |
| CURRENT | A center point cannot prove whole-eddy footprint intersection or containment. | P2 | Eddy list | Show the point-only limit beside Cameron's dated candidate. Done. |
| CURRENT | NASA regional crop overlap is geographic navigation rather than current or eddy identification. | P2 | Crop list | Keep the existing crop caveat. Done. |
| SOUNDER | Supported current rows need observation dates and reported locality. | P2 | Local presence | Expose the source fields in the passport. Done. |
| SOUNDER | A source citation must remain available from each supported local row. | P2 | Local presence | Link the paper's source record. Done. |
| SOUNDER | The downloadable state packet should contain the detailed source observation row. | P3 | Packet | Validate the MEDI packet includes its Toulon observation. Done. |
| CHART | The 56-state regions are approximate atlas shapes. | P2 | State heading | State that the polygon is approximate and distinguish point/line evidence. Done. |
| CHART | CAMR's Cameron candidate has a known date but no footprint. | P2 | Candidate list | Display the date and point-only qualifier. Done. |
| CHART | Movie crops may overlap several states. | P3 | Crop list | Present display overlap percentage and NASA link, without physical attribution. Done. |
| HARBOR | A state should have a direct route to its underlying rows. | P2 | Passport heading | Add a keyboard-accessible JSON packet link. Done. |
| HARBOR | Evidence groups should be readable without the map palette. | P3 | Details groups | Keep text group headings and counts. Done. |
| HARBOR | Deep links and narrow-screen layout must remain usable. | P3 | Browser checks | Exercise both MEDI and CAMR passport states. Done. |
| KEEL | The state packet must match the screened rows and claims. | P2 | Packet checker | Validate all 213 packets and source closure. Done. |
| KEEL | Browser tests should fail if dated evidence disappears. | P2 | Browser checks | Assert Toulon locality and Cameron date/point text. Done. |
| KEEL | The review-site file manifest must track interface changes. | P3 | Site build | Rebuild and validate the 263-file bundle. Done. |

Roles reviewed: 5. P1 blockers: 0; P2 issues: 10; P3 notes: 5.
Verdict: **APPROVED-WITH-CONDITIONS** for internal review. The passports remain
an incomplete source-set atlas and do not authorize a physical passage claim
for unresolved rows or public release. Top finding: observation locality and
whole-feature path are different claims. CURRENT, SOUNDER, and CHART agree.

Amendments: (1) Show dated locality and paper citation for local current
observations; done. (2) Show dates and point-only limits for eddy candidates;
done. (3) Obtain dated feature geometry with source review before promoting a
whole-current or whole-eddy state crossing; open.
