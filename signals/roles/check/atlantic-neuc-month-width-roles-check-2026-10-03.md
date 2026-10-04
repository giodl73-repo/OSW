---
skill: roles-check
topic: atlantic-neuc-month-width
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---
# Historical NEUC angular section widths and protocol v1.4

Internal installed perspectives, not independent scientific approval.
CURRENT/SOUNDER assess measurement meaning; CHART/BEACON/HARBOR assess
presentation and access; KEEL/LOGBOOK assess consistency and custody. ORBIT
does not apply to a regional current section measurement.

| Role | Finding | Severity | Resolution / condition |
| --- | --- | --- | --- |
| CURRENT | Section span differs from whole-current width | P2 | Author-reported meridional metric retained; no full-width or representative admission. |
| CURRENT | Historical density core differs from central depth box | P3 | Historical sigma-theta 26.75 context retained; 65–270 m not assigned to width records. |
| CURRENT | Two surveys do not establish a seasonal cycle | P2 | Separate 1993-02 and 1996-04 records; playback and annual extrema explicitly ineligible. |
| SOUNDER | Month precision cannot imply first/last observation day | P2 | YYYY-MM field; day period null; validator rejects day strings or stored day periods. |
| SOUNDER | Angular-to-km conversion requires disclosed support | P3 | WGS84 normalization, 221.165643 km raw result and 10 km rounding recorded. |
| SOUNDER | Threshold remains unspecified in source prose | P3 | No invented zero crossing, contour threshold or exact paired-edge coordinates. |
| CHART | Normalization endpoints could be mistaken for geography | P3 | No section geometry stored; limits explicitly computation only. |
| CHART | Bar can imply constant route width | P3 | Section-span label, layer/scope text and no buffering retained. |
| CHART | Route image is static context for historical width | P3 | Existing static-map note retained; no historical axis or footprint claim. |
| BEACON | Historical months should not be headed Seasonal state | P3 | Dynamic Historical section observation heading added. |
| BEACON | Rounded 220 km should not sound source-reported in km | P3 | UI states converted from latitude degrees; angular source value retained. |
| BEACON | Equal values can imply persistence across years | P3 | Comparability note explicitly excludes persistence and annual-range inference. |
| HARBOR | Disabled play needs a visible signal | P3 | Disabled button appearance added; adjacent explanation describes missing seasonal support. |
| HARBOR | Both month records need independent selection | P3 | Browser selects each and verifies original month text and disabled play. |
| HARBOR | Narrow screen needs definition and image access | P3 | 320px browser checks no page overflow and retained static route/definition. |
| KEEL | Validator should catch doubling/units/geometry forgery | P3 | Mutation tests reject 440 km, altered raw/rounding/method, fabricated edges and seasonal flags. |
| KEEL | General protocol change invalidates derived-series metadata | P3 | General hash and inventory series digest refreshed; 17-frame checker passes. |
| KEEL | Integration checks must follow growing inventory | P3 | Width table count and nonnumeric review count checked against source inventory. |
| LOGBOOK | Numeric records differ from covered names | P3 | 11 scoped records / eight names; three nonnumeric reviews, one derived candidate, 88 unassessed. |
| LOGBOOK | Pending audit status must reflect resolved extraction | P3 | Scope audit and summary now point to two extracted records; physical/external review remains open. |
| LOGBOOK | Historical role receipt should retain original scope | P3 | Prior pending-review receipt retained; this dated follow-up documents changed admission. |

21 findings: 0 P1 / 3 P2 / 18 P3. APPROVED-WITH-CONDITIONS for local
inspection. Amendments: preserve month precision; retain section-span rather
than full-width meaning; prohibit seasonal inference from the two surveys.
CURRENT/SOUNDER/CHART agree that unit conversion does not diagnose observed
boundaries. Independent extraction review, physical edges, repeated time series
and canonical admission remain open.

Evidence: primary Bourles et al. (1999), section 4.8 p. 21163; protocol v1.4;
29 focused unit checks; NEUC route/width browser check; 17-frame derived width
checker. Explorer screenshot inspected; heading refined after visual review.
No complete repository suite or independent scientific approval claim.

Browser integration also passed: currents, named/dated eddies, NASA objects,
all 56 state views and map links. The first run exposed a stale two-review
count assertion; inventory-derived count verification now passes without
removing the scope check.
