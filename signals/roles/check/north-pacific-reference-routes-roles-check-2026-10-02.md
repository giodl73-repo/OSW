---
skill: roles-check
topic: north-pacific-reference-routes
date: 2026-10-02
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# North Pacific source conventions and date-line handling

Artifact: two editorial route candidates, geodesic/map generator seam policy,
catalog, figures, browser checks and documentation. Relevant roles selected
for scientific scope, provenance, cartography, explanation, access, computation
and repository status. ORBIT omitted because no planetary analogy is involved.
Internal role-lens review, not independent scientific approval.

| Role | Finding | Severity | Amendment/condition |
| --- | --- | --- | --- |
| CURRENT | NOAA and AMS use different North Pacific western limits. | P3 | Declare NOAA convention and display the contrasting AMS source. |
| CURRENT | Latitude corridors and eastern terminal gates are editorial. | P3 | Preserve broad alternate corridors and OSW coordinate-selection statements. |
| CURRENT | Neither candidate supplies a measured axis or universal named-flow extent. | P2 | Independent scientific convention/axis review before canonical admission. |
| SOUNDER | Glossary identity is not velocity geometry. | P3 | Source entry locators, retrieval dates and factual-use scope retained. |
| SOUNDER | Finite ranges cannot become source errors. | P3 | Scenario rules explicitly name assumptions and downloadable coordinates. |
| SOUNDER | Seam transformation must remain reproducible. | P3 | Input declares supported policy; unsupported policies are rejected. |
| CHART | Projecting wrapped points directly creates a false world-spanning chord. | P3 | Densify geodesics, unwrap continuously and use matching endpoint locations. |
| CHART | Land/state geometry needs periodic copies across the seam. | P3 | Apply adjacent-world union for seam-policy candidates; retain periodic crop checks. |
| CHART | Clear display routes do not establish current-core geography. | P2 | Physical correspondence and current identity remain scientific admission gates. |
| BEACON | The date line is a map seam rather than a current boundary. | P3 | Mark seam on figure while maintaining continuous route. |
| BEACON | Kuroshio Extension limits vary across conventions. | P3 | Explicitly avoid treating NOAA's 160 E limit as universal termination. |
| BEACON | New long routes change ordering sensitivity. | P3 | Rebuild catalog and update browser position expectations. |
| HARBOR | Seam meaning must be available in text. | P3 | Method records normalization, unwrapping and periodic joins; source/scope text retained. |
| HARBOR | Maps need readable endpoints and downloadable route evidence. | P3 | Both figures inspected; full-size links, alt text and JSON remain available. |
| HARBOR | Expanded comparison must still reflow on mobile. | P3 | Full browser check includes image loading and 320 px page width. |
| KEEL | A seam policy can accidentally permit an ambiguous half-world leg. | P3 | Reject exactly 180-degree longitude legs and test the rejection. |
| KEEL | Seam joins could introduce unrelated ocean intersections. | P3 | Synthetic seam test verifies both Pacific edges and zero Atlantic intersection. |
| KEEL | Changing generator could leave older outputs silently accepted. | P3 | Pin generator SHA-256 in every candidate and reject stale/missing fingerprints; regenerate all records. |
| LOGBOOK | Coverage must reflect twelve currents rather than thirteen distinct currents. | P3 | Document thirteen routes for twelve currents; studied reaches stay separate. |
| LOGBOOK | Published measurements have a different admission status. | P3 | Existing canonical ranking and floors unchanged by this increment. |
| LOGBOOK | Role-lens approval does not complete scientific or publication review. | P2 | Keep internal candidate boundary; canonical integration and publication gates open. |

Roles reviewed: 7. Findings: 21. P1: 0; P2: 3; P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for internal review. Top condition: source
convention and physical-axis review. CURRENT, SOUNDER and BEACON agree that
NOAA naming limits must travel with the estimate. Three amendments: explicit
seam policy, periodic display joins and visible conflicting source convention.

Verification: both candidate/catalog builds; seven geodesic/geometry tests;
four ordering/provenance tests; independent numerical/input-hash checks for
all 864 scenarios. Initial all-candidate byte comparison found older output
differences; the second rebuild was byte-identical. Generator fingerprints
were then added and all candidates regenerated. Full Chromium atlas check
passed with new values, crop links, scope and ordering, image loading and
320 px reflow. Both figures visually inspected. These checks do not approve
scientific current axes.
