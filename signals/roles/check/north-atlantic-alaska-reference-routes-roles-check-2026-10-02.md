---
skill: roles-check
topic: north-atlantic-alaska-reference-routes
date: 2026-10-02
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# North Atlantic approaches and northward Alaska branch

Internal review of two regional reference inputs/outputs, maps, catalog,
browser checks and documentation. Seven roles selected for science scope,
provenance, mapping, communication, access, reproducibility and repository
status. ORBIT excluded because no planetary analogy is present. This is an
internal role-lens audit, not independent scientific approval.

| Role | Finding | Severity | Amendment/condition |
| --- | --- | --- | --- |
| CURRENT | North Atlantic destination is a broad region, not a unique endpoint. | P3 | Three approach conventions retained and described as editorial. |
| CURRENT | Alaska Current, Alaskan Stream and Alaska Coastal Current differ. | P3 | Use primary report's northward branch convention and explicit exclusions. |
| CURRENT | Sources do not diagnose these intermediate axes. | P2 | Independent gate/route review before scientific admission. |
| SOUNDER | NOAA glossary supplies North Atlantic start region and destination. | P3 | Entry locator and source citation travel with coordinates. |
| SOUNDER | Alaska primary paper's 1977 observations are local to Kodiak. | P3 | Do not label full candidate as a 1977 observed route. |
| SOUNDER | Regional gate scenarios are not measured errors. | P3 | Preserve assumptions and all 81 scenarios for each candidate. |
| CHART | Densified chords must avoid land for every retained scenario. | P3 | All candidate scenarios pass coarse display-land mask. |
| CHART | Display clearance cannot prove slope/front correspondence. | P2 | Reproducible physical geographic correspondence remains an admission gate. |
| CHART | Regional maps must show complete routes and endpoint conventions. | P3 | Both SVGs visually inspected with source and labeled gates. |
| BEACON | North Atlantic regional route is not the Gulf Stream System length. | P3 | Scope explicitly excludes upstream/onward components and system total. |
| BEACON | Alaska regional sketch is not a whole Gulf of Alaska circuit. | P3 | Exclude northwestern arm and whole-gyre interpretation. |
| BEACON | Broad Alaska range can change nominal ordering materially. | P3 | Range, overlapping routes and conservative position bounds remain visible. |
| HARBOR | Route meaning must be available without relying on line colour. | P3 | Endpoint text, adjacent scope/method and downloadable JSON retained. |
| HARBOR | New source links need accessible equivalents. | P3 | Primary report link and glossary support link rendered as text. |
| HARBOR | Expanded inventory must remain usable at narrow widths. | P3 | Existing labeled filters and 320 px reflow included in browser checks. |
| KEEL | New estimates must not enter source-published ranking. | P3 | Published eligibility stays false; canonical ranking untouched. |
| KEEL | Equal numbers across evidence classes can break exclusion checks. | P3 | Test studied-reach exclusion by stable route ID, not absence of 3,300 km anywhere. |
| KEEL | Candidate/catalog files need current generator/input provenance. | P3 | Hash checks for all candidates; byte-identical rebuild for this increment. |
| LOGBOOK | Route and current coverage differ by one studied-reach alternative. | P3 | Document fifteen candidates, fourteen currents and 75 unbuilt records. |
| LOGBOOK | Prior progress counts are historical rather than current. | P3 | Update current plan header and README; keep chronological entries. |
| LOGBOOK | Internal checks cannot complete canonical publication review. | P2 | Scientific review, canonical integration and publication review remain open. |

Roles reviewed: 7. Findings: 21. P1: 0; P2: 3; P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for internal review. Top condition: route
identity and gate review. CURRENT, SOUNDER and BEACON agree that the source's
regional naming cannot be presented as observed full-current geometry. Three
amendments: distinguish Alaska names, retain North Atlantic approach variants,
and test studied-reach exclusion by identity rather than a coincident number.

Verification: candidate and catalog builds, seven geodesic tests, four
ordering/provenance tests, independent recomputation of all 1,026 scenarios,
generator/input hashes and deterministic rebuild. Both SVGs inspected. Full
browser checks cover new values, exclusions, crop links, filters, image loading
and 320 px reflow. These checks do not approve physical current axes.
