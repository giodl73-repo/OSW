---
skill: roles-check
topic: kraken-canonical-proxy-geometry
date: 2026-10-02
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Kraken dated contour geometry admission

Artifact: the pinned Figure 2 audit, nominal source-pixel/coordinate export,
canonical geometry 0158 and separate footprint candidate claim, object/state
views and packets. Selected installed CURRENT (physical meaning), SOUNDER
(provenance), CHART (geometry), BEACON (reading), HARBOR (access), KEEL
(reproducibility), and LOGBOOK (release truth) lenses. No planetary comparison
is introduced, so ORBIT is omitted. This review is in-task engineering/editorial
review, not independent scientific or human accessibility approval.

| Role | Finding | Severity | Evidence and disposition |
| --- | --- | --- | --- |
| CURRENT | Only the initial blue curve is an instantaneous SSH boundary. | P3 | Verified Figure 2 caption in the pinned PDF; exported date is only 29 May 2013. August/October advected curves are excluded. |
| CURRENT | SSH contour and material core are different objects. | P3 | Candidate boundary type and UI keep the proxy distinct from red core/shielding curves and a three-dimensional ring volume. |
| CURRENT | Scientific interpretation remains independently unreviewed. | P2 | New claim is recorded_footprint_candidate_not_verified_boundary and not_individually_reviewed; no positive whole-ring containment assertion is admitted. |
| SOUNDER | Exact source and adaptation are identifiable. | P3 | PDF SHA bba7a3b04adcafdc3c78bbe80c72aa0f906fe358ca6047cf0b048180489ed438 and embedded image SHA b07f073dadda7d8bb8660184b43aa981a719d4944a647ac02bff84e28812015b checked. |
| SOUNDER | Decimal precision cannot substitute for positional accuracy. | P3 | Seven-decimal output is reproducibility detail; datum is unspecified and line width/calibration/segmentation uncertainty is explicit. |
| SOUNDER | Adaptation terms must cover the exported coordinates. | P3 | Pinned final PDF page states CC BY 4.0; Figure 2 has no different credit. Source-use row and notices now cover the nominal traced proxy coordinates. |
| CHART | CARB intersection depends on calibration. | P3 | Nominal display overlap is 1.1884%; tested threshold/calibration range 0-7.4167%. UI marks calibration-sensitive candidate, containment unresolved. |
| CHART | CAMR intersection is robust only over the tested scenarios. | P3 | Nominal overlap 98.8116%; tested range 92.5833-100%. No surveyed boundary, permanent extent or statistical confidence interval is implied. |
| CHART | Independent axis scaling distorted the displayed shape. | P2 | Fixed after narrow-screen visual review: common angular scale now preserves source longitude/latitude proportions. Plot declares projection and excludes coast/state boundaries. |
| BEACON | A polygon could imply authoritative footprint data. | P3 | Heading says figure-derived SSH contour candidate; nearby text names the OSW digitization, date and pending science review. |
| BEACON | State labels need codes to clarify atlas geography. | P3 | Both state links carry CAMR/CARB codes and source-set state labels; candidate text specifies approximate display geometry. |
| BEACON | Source and method should be readily accessible. | P3 | Article, CC BY license, attribution, source locator, method, disclosure of no original figure packaging, and checksum details accompany the plot. |
| HARBOR | The outline needs an equivalent textual description. | P3 | SVG has a date/extent/state-evidence accessible label; text lists bounds, date, both state assessments, uncertainty and source. |
| HARBOR | Evidence must survive a narrow viewport and download. | P3 | 320-pixel browser check and visual screenshot review; both eddy and state packets include candidate, polygon, bound claim and source closure. |
| HARBOR | Human assistive-technology review remains open. | P2 | Automated browser and visual checks do not substitute for full human accessibility review before publication. |
| KEEL | Geometry generation needs a pinned source and extraction method. | P3 | Optional extraction rerun against the exact PDF with pinned dependency path; all prior sensitivity results are unchanged. Pixel ring and axis ticks are exported. |
| KEEL | Checkers should independently test the spatial assertion. | P3 | Release check reconstructs all nominal coordinates from pixels and computes nominal overlaps plus all 16 middle-threshold calibration cases independently. Schema constrains roles, fractions and unresolved containment. |
| KEEL | New evidence must preserve prior canonical records. | P3 | All prior 14,306 claims, 5,761 relations, eight current observations, 7,616 named-eddy/state rows, 157 geometries, 330 names and 29 measurements retain identical record content. New geometry and claim append. |
| LOGBOOK | Unknown datum excludes this polygon from CRS84 export. | P3 | JSON/CSV retain geometry; both GeoJSON exports omit it. Full geometry count 158, screened 151; candidate has one new claim in each. |
| LOGBOOK | Candidate copies and reading surfaces must reconcile. | P3 | Full 14,307 claims, screened 8,698, 273 screened site files. Shared rendering code is pinned and copied to the standalone site. Docs and source notices updated. |
| LOGBOOK | Candidate admission does not complete publication gates. | P2 | Seventeen pending used-source decisions elsewhere, science review, human accessibility and owner publication gates remain open. No public release performed. |

Roles reviewed: 7. Findings: 21 (P1 0, P2 4, P3 17).
One P2 visual defect was corrected. Three P2 release conditions remain.
Verdict: APPROVED-WITH-CONDITIONS for local canonical proxy admission.
CURRENT/CHART agree on a dated SSH proxy versus whole-ring support;
SOUNDER/KEEL agree on exact inputs versus inferred positional precision.

Amendments completed:

1. Export the middle-threshold nominal ring, source pixel ring, axis ticks,
   source hashes, unknown datum and separately bound candidate support.
2. Carry it into Kraken and CAMR/CARB views and packets, retaining uncertainty,
   attribution, source links and unresolved whole-ring containment.
3. Correct angular scaling after visual review and validate nominal coordinates,
   tested overlap ranges, schema, screening and prior-record preservation.

Final verification passes after regeneration and plot-scale correction: full
release, screened preview/site and both browser suites. The motion almanac
check and syntax checks for all three changed JavaScript files also pass.
The final 320-pixel screenshot shows the corrected angular proportions.
Source images and paper PDF remain outside the candidate package.
