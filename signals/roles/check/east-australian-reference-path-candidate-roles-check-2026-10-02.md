---
skill: roles-check
topic: east-australian-reference-path-candidate
date: 2026-10-02
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# East Australian Current reference-route candidate

Scope: source-linked editorial inputs, route measurement/scenarios, figure,
state and NASA display joins. Seven installed roles selected for physical
scope, provenance, cartography, explanation, accessibility, computation and
repository status. ORBIT omitted because this artifact has no planetary analogy.
This is an internal role-lens review, not independent scientific approval.

| Role | Finding | Severity | Amendment or condition |
| --- | --- | --- | --- |
| CURRENT | The coherent jet ends at usual separation; the downstream EAC system is longer and differently scoped. | P3 | Input and figure restrict scope to about 15–32 degrees S; exclude Tasman Front and eddy/extension routes. |
| CURRENT | Geodesic polyline length is not a measured current axis or water-parcel travel distance. | P3 | Method and figure identify the editorial reference-route interpretation. |
| CURRENT | Physical correspondence of offshore waypoints with the shelf-break jet remains unreviewed. | P2 | Require independent physical-oceanography review before canonical admission as an estimated current route. |
| SOUNDER | Source supplies latitude gates and flow description, not chosen longitudes or intermediate vertices. | P3 | Explicit coordinate-selection statement distinguishes every OSW vertex from published data. |
| SOUNDER | Offsets are finite editorial scenarios, not empirical positional error. | P3 | Preserve scenario coordinates and exact lengths, with rounded interpretation and no confidence-interval claim. |
| SOUNDER | Model period and layer are not determined from Figure 1. | P3 | Figure used only for regional orientation; candidate is not its instantaneous model field or a diagnosed velocity layer. |
| CHART | A preliminary westward route crosses the coarse map land mask. | P3 | Reject the preliminary offset and document the retained smaller longitude-offset choice. |
| CHART | Passing the coarse mask cannot verify reefs, bathymetry or shelf-break correspondence. | P2 | Keep this limitation beside the check; obtain a suitable bathymetric corridor before strengthening geometry support. |
| CHART | Length and displayed/joined geometry must describe the same route. | P3 | Geodesic legs are densified at no more than 10 km for display and spatial joins. |
| BEACON | Apparent precision of 2110.298 km could imply accuracy unsupported by the sketch. | P3 | Main reported value is approximately 2,100 km; exact computation remains in the reproducibility record. |
| BEACON | Rounded 2,000–2,300 km range is a scenario envelope, not a likely distribution. | P3 | Plain limitations supplied in candidate, plan and figure. |
| BEACON | The first candidate does not resolve all remaining 89 lengths. | P3 | Plan states one first-batch candidate and retains the full remaining scope. |
| HARBOR | Figure meaning must be recoverable without perceiving colour. | P3 | Dashed nominal route, endpoint text, numerical range and descriptive SVG title/description provided. |
| HARBOR | Scientific review status must accompany the visual. | P3 | Figure explicitly says candidate and scientific review pending. |
| HARBOR | The graphic alone cannot expose the full scenario table. | P3 | Linked JSON retains all 27 coordinate/length/join records; broad assistive-technology review remains open. |
| KEEL | Curve length needs numerical verification beyond a successful build. | P3 | Tests cover an analytic equatorial arc, return path, detour/reversal, invalid coordinates and ambiguous seam. |
| KEEL | Projected geodesic curvature must survive display interpolation. | P3 | Test verifies poleward curvature of a high-latitude geodesic; figure uses the same interpolation. |
| KEEL | Reproduction depends on atlas geometry and NASA crop inputs. | P3 | Candidate pins input, atlas and tile-file hashes; generator acquires no live data. |
| LOGBOOK | Candidate must not enter the published-estimate ranking silently. | P3 | Published rank eligibility remains false; canonical measurements and eleven-value ranking unchanged. |
| LOGBOOK | Geography context must not become a NASA identification claim. | P3 | Crop fractions explicitly measure display line overlap; recommendation is a deterministic navigation choice. |
| LOGBOOK | Candidate still needs canonical schema, claim and interface integration. | P2 | Retain as a review artifact; integrate its separate measurement/geometry role with provenance before public admission. |

Roles reviewed: 7. P1: 0. P2: 3. P3: 18.
Verdict: APPROVED-WITH-CONDITIONS for review use. Conditions are scientific
route review, bathymetric correspondence and canonical integration.
CURRENT, CHART and BEACON agree that scope and editorial status must stay visible.

Completed amendments: reject land-crossing scenario; densify the measured
geodesics for joins/rendering; round public-facing numbers while retaining all
calculation inputs. Verification: generator and four numerical/geometry tests
pass; candidate figure inspected in Chromium. No publication or scientific
claim approval is asserted.
