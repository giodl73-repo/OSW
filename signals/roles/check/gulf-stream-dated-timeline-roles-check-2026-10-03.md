---
skill: roles-check
topic: gulf-stream-dated-timeline
date: 2026-10-03
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Dated Gulf Stream diagnostic timeline

Internal seven-role review of generator, series, maps, validator, browser UI,
tests and annual-atlas plan. Roles cover physical meaning, source stewardship,
cartography, public communication, accessibility, engineering and publication.
ORBIT excluded without planetary analogy. Not independent scientific approval.

| Role | Finding | Severity | Amendment or condition |
| --- | --- | --- | --- |
| CURRENT | Frozen-field line is not a physical current axis | P2 | Diagnostic role and explicit explanation retained. |
| CURRENT | Truncated trace cannot imply current shortening | P2 | 18 September stop displayed beside the map. |
| CURRENT | Surface geostrophy omits depth and ageostrophic flow | P3 | Layer/product limitations and unknown width retained. |
| SOUNDER | Frames need source dates and pinned response identities | P3 | Subset/source hashes and exclusive daily intervals retained. |
| SOUNDER | Experimental product status and version matter | P3 | RADS 4.8.1 and experimental status displayed. |
| SOUNDER | Five dates cannot provide annual extrema | P3 | Annual eligibility false; ranges null; no seasonal claim. |
| CHART | Centerline intersections differ from footprints | P2 | Diagnostic predicate and contextual state links only. |
| CHART | Map needs consistent geometry and projection | P3 | Common equirectangular regional frame, grid, land and state context. |
| CHART | Line thickness and endpoint must not imply width | P3 | Display thickness stated; seed/end marks and gate shown. |
| BEACON | Unsampled dates may disappear during playback | P3 | Date gaps and five missing intervening days explicitly displayed. |
| BEACON | Length needs an immediate scope label | P3 | Gate-reaching or truncated diagnostic beside number. |
| BEACON | Source and method must remain reachable | P3 | Per-frame NOAA file, method and downloadable series linked. |
| HARBOR | Animation must be user controlled | P3 | Play/pause and manual date selection; stops on hidden page. |
| HARBOR | Map needs text equivalent | P3 | Alt text, date, length, stop and state list provided. |
| HARBOR | Narrow screens must reflow | P3 | Browser checks 320 px and desktop screenshot inspected. |
| KEEL | Regeneration must preserve prior repeat audit | P3 | Source checksums and trace lengths/stops match original audit. |
| KEEL | False completion and modified geometry need rejection | P3 | Negative tests reject fake gate success and changed coordinates. |
| KEEL | State joins require frame-by-frame recomputation | P3 | Validator rebuilds all joins from pinned map. |
| LOGBOOK | Research pilot cannot silently enter canonical rankings | P3 | Separate research artifact; no release edits. |
| LOGBOOK | Annual objective remains incomplete | P3 | Plan retains full-year data and footprint requirements. |
| LOGBOOK | Internal review is not independent scientific approval | P3 | Source/axis/science/admission gates remain open. |


Seven roles, 21 findings: zero P1, three P2, eighteen P3.
APPROVED-WITH-CONDITIONS for local research playback. Top finding: early trace
termination cannot establish current shortening. CURRENT and BEACON agree
that displayed length needs immediate diagnostic scope. CURRENT and CHART
agree that the derived line is not an occupied footprint.

Three amendments: display truncation beside numerical length; preserve missing
calendar intervals; recompute and label diagnostic state intersections. These
are implemented. Physical-axis validation, full-year sampling and scientific
canonical admission remain outstanding. No annual atlas completion claimed.

Verification: five-frame validator, 27 focused tests and full Chromium almanac
browser suite pass. Desktop screenshot inspected. Source product page checked;
no external refresh needed for deterministic reproduction from pinned subsets.


## Twelve-sample 2025 extension

Same seven role lenses applied to the new acquisition, series selector and
annual-spaced frames. Key conditions remain: derived line is not a current axis;
tracing failures and unsampled days stay visible; no annual extrema or width.

| Role | Extension finding | Severity | Amendment or condition |
| --- | --- | --- | --- |
| CURRENT | Four of twelve traces fail to reach the gate. | P2 | All retained with stop explanation; no full-current comparison. |
| CURRENT | December circulation inflates accumulated distance. | P3 | Cap/circulation explanation beside selected frame. |
| CURRENT | One daily sample cannot represent a month. | P3 | Daily snapshot labels, not means or climatology. |
| SOUNDER | Processing changes in August. | P2 | Per-frame 4.7.0/4.7.1 and experimental status; physical attribution caution. |
| SOUNDER | Date selection must precede results. | P3 | Fixed fifteenth-day request manifest retains all twelve dates. |
| SOUNDER | Retrieval and byte identity must be preserved. | P3 | Existing subset schema, response hashes and acquisition manifest. |
| CHART | Every map needs common framing. | P3 | Common geographic view; all sampled coordinates remain inside it. |
| CHART | State crossing can change with derived line. | P3 | Joins recomputed per frame and explicitly diagnostic. |
| CHART | Recirculation cannot become a width polygon. | P3 | No footprint or new width inferred. |
| BEACON | A year selector can imply annual completeness. | P2 | Twelve daily snapshots stated beside selector; annual extrema null. |
| BEACON | Source version break needs a reader-facing explanation. | P3 | Differences not assigned wholly to ocean change. |
| BEACON | Gaps must remain visible at monthly scale. | P3 | Calendar interval and unsampled-day count update per frame. |
| HARBOR | Series switch must stop playback. | P3 | Timer stops before fetch; date/play controls disabled during loading. |
| HARBOR | Stale fetches can overwrite selection. | P3 | Load token rejects late prior responses. |
| HARBOR | More controls must reflow. | P3 | 320 px browser check and desktop review pass. |
| KEEL | All twelve dates and failures need validation. | P3 | Predetermined date grid, per-frame recomputation, failure count test. |
| KEEL | Source version cannot be relabelled. | P3 | Negative test rejects changed per-frame version. |
| KEEL | Existing tracer cap permits one final step beyond 4000 km. | P3 | Algorithm output recorded 4010 km, documented, never ranked as current length. |
| LOGBOOK | Acquisition should be explicit and resumable. | P3 | Dedicated fetch command; offline normal builds; existing receipts preserved. |
| LOGBOOK | Canonical boundary must remain intact. | P3 | Research-only output and no release measurement edits. |
| LOGBOOK | Annual sampling is progress, not completion of the atlas. | P3 | Seed/axis/boundary validation and inventory coverage remain open. |

Extension: 21 findings, zero P1, three P2, eighteen P3;
APPROVED-WITH-CONDITIONS for local diagnostic playback. Three amendments:
preserve failed traces; expose processing breakpoint; distinguish daily samples
from month means. Implemented and browser verified. Internal review only.
Both series validators, 28 focused tests and full browser suite pass.


## Finite sensitivity grid and cap correction

Seven-role extension review: 21 findings, zero P1, three P2, eighteen P3.
APPROVED-WITH-CONDITIONS for research diagnostics; no scientific axis approval.

| Role | Finding | Severity | Amendment or condition |
| --- | --- | --- | --- |
| CURRENT | Nearby seeds can select different branches. | P2 | Scenario span is methodological sensitivity; axis diagnosis still open. |
| CURRENT | Successful-only span can exclude failed selected trace. | P3 | Explicit selected-stop warning; failures remain in table. |
| CURRENT | Seed latitude spread cannot establish width. | P3 | Width inference prohibited in data and text. |
| SOUNDER | Finite scenarios do not yield statistical confidence. | P2 | Range kind and false confidence flag validated. |
| SOUNDER | No successful scenarios must remain null. | P3 | December null span; zero of nine displayed. |
| SOUNDER | Outward rounding needs a reproducible rule. | P3 | 10 km outward rounding, recomputed from successful cases. |
| CHART | No geometric corridor follows from a length span. | P3 | Main diagnostic map unchanged; no buffered corridor added. |
| CHART | State joins belong to the selected plotted line. | P3 | Frame joins remain main-trace intersections. |
| CHART | Alternative curves are not occupied boundaries. | P3 | Numerical scenario table; no width/footprint polygon. |
| BEACON | Calling this a margin can imply measurement error. | P2 | UI uses finite scenario sensitivity and specific exclusions. |
| BEACON | Failure count must accompany successful span. | P3 | Count out of nine precedes span. |
| BEACON | Data precision must not imply axis accuracy. | P3 | Raw 0.1 km diagnostic distances; coarse summary and scope caveats. |
| HARBOR | Expanded table must remain accessible on mobile. | P3 | Native details, column headers and contained horizontal scroll. |
| HARBOR | Changing phases must update the whole sensitivity view. | P3 | Text and nine rows rebuild with each selected frame. |
| HARBOR | Zero-success meaning cannot depend on colour. | P3 | Explicit null-span sentence. |
| KEEL | Cartesian scenario coverage can silently shrink. | P3 | All nine tuples reconstructed and compared by validator. |
| KEEL | Trace exceeded declared distance cap. | P3 | Fixed remaining-step limit; nondivisible-cap and invalid-step tests. |
| KEEL | Algorithm change requires regeneration. | P3 | Both series rebuilt and provenance refreshed; legacy trace/repeat checks pass. |
| LOGBOOK | Previous cap observation must remain historically legible. | P3 | Chronological plan adds correction rather than erasing earlier diagnosis. |
| LOGBOOK | Diagnostics remain outside official rankings. | P3 | No canonical measurement or release edits. |
| LOGBOOK | Verification must include interpretation failures. | P3 | Negative confidence/width/span/scenario tests and browser zero/success checks. |

Three amendments: prohibit statistical/width interpretations; preserve all failed
scenarios beside the successful span; enforce exact hard cap and refresh
provenance. Implemented. 31 focused tests, both validators, full Chromium browser
suite and original Gulf Stream trace/repeat checks pass. July expanded-table
screenshot visually inspected. Physical axis/boundary validation remains open.
