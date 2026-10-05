---
skill: roles-check
topic: loop-current-adt-query-comparison
date: 2026-10-04
source_commit: dcd9a61bfbcd7a24022ff5e6250919f799f64dfc
working_branch: codex/loop-current-dated-path
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Loop Current ADT comparison and query integration review

Internal functional review of acquisition, finite ADT contour search, protocols,
source audit, Rust imports/validation and map-to-card navigation. CURRENT checks
physical meaning; SOUNDER source identity; CHART map semantics; BEACON explanation;
HARBOR equivalent access; KEEL reproducibility; LOGBOOK delivery. ORBIT is excluded
without a planetary comparison. This is not independent scientific peer review.

| # | Role | Finding | Severity/status | Evidence and recommendation |
|---|---|---|---|---|
| 1 | CURRENT | Different products can share observations. | P2, resolved | Comparison explicitly distinguishes product/method agreement from independent observational confirmation; shared satellite inputs disclosed. |
| 2 | CURRENT | ADT contour selection needs a physical criterion. | P3, verified | Greatest length-weighted mean geostrophic speed among eligible connected contours; no shortest-path or desired-length selection. |
| 3 | CURRENT | One date and a scan do not yield physical ranges. | P3, verified | Width, annual range, confidence interval and whole-current length null; ranking false. Scanned levels and seed failures retain their actual meaning. |
| 4 | SOUNDER | All three fields and masks need original readback. | P3, verified | Every ADT/ugos/vgos value and missing cell matched the acquired GCOOS response. Dataset/product version, units, license URL, history and response SHA retained. |
| 5 | SOUNDER | Same labelled date is not proof of identical averaging support. | P3, verified | DUACS response lacks time_bnds; no exact support fabricated. Comparison declares same labelled date. |
| 6 | SOUNDER | Source JSON strings must preserve original bytes. | P2, resolved | Bundle uses read_bytes().decode to preserve CRLF. Rust verifies SHA and parsed document equality against original JSON. Native/WASM load passed. |
| 7 | CHART | A ring cannot be appended to complete an open current. | P3, verified | Clipped segments require both gateway endpoints and flow direction; closed, reversed and wrong-gateway cases tested. No named-eddy identity inferred. |
| 8 | CHART | Missing corners could produce invented connections. | P3, verified | corner_mask=False; strict four-wet-cell interpolation; any missing velocity sample rejects the candidate. |
| 9 | CHART | Map lines must distinguish methods and failures. | P3, verified | Solid NOAA, long-dashed ADT and short-dashed failed traces; gateway lines and text legend; screenshot inspected. |
| 10 | BEACON | Close numbers can imply unwarranted validation. | P3, verified | Raw 55.9 km disagreement described as method/product difference. No uncertainty interval or independent confirmation claimed. |
| 11 | BEACON | Readers need queryable method identity. | P3, verified | Two separately named diagnostic records, source audit and dated frame joins; query values label unranked diagnostics. |
| 12 | BEACON | Finite algorithm is not an exact source reproduction. | P3, verified | Protocol and cards declare finite OSW approximation; original supplement and gateway details remain open. |
| 13 | HARBOR | Color is insufficient to convey method identity. | P3, verified | Distinct line patterns, SVG description, comparison prose and retained outcome table. |
| 14 | HARBOR | Map selection must work without a pointer. | P3, verified | Keyboard map focus/Enter opens the current and its two diagnostic records; mapped comparison links work. |
| 15 | HARBOR | New evidence must reflow on narrow screens. | P3, verified | Comparison tested at 320 px; table has its own overflow region; no page-wide horizontal scroll. |
| 16 | KEEL | Scientific mutation must fail loading. | P3, verified | Eight rejection cases cover original JSON, altered numbers, ranks, receipts, dates, frames, owner joins and comparison source. |
| 17 | KEEL | Additional frames must not break older source tests. | P3, verified | 19 total frames; Gulf source test explicitly covers its 17 frames and five retained failures. Existing time/state selection and playback checks passed. |
| 18 | KEEL | Contour execution must be reproducible offline. | P3, verified | Pinned contourpy 1.3.3, explicit serial/corner settings, original snapshots and generator/protocol hashes; reconstructions and native/WASM parity passed. |
| 19 | LOGBOOK | New snapshots require source-use review before publication. | P3, open | License URLs and pending status retained; branch remains local and unpushed. Original ERDDAP binary is temporary, not silently added to release. |
| 20 | LOGBOOK | New diagnostics do not change reference-route admission. | P3, verified | Published lengths 11, remaining names 89, editorial candidates 62/59 names and 30 unbuilt unchanged; canonical release diff empty. |
| 21 | LOGBOOK | Scientific and full release gates remain outstanding. | P3, open | Full CI, original methodological details, gateway/effective-resolution review and multi-date regime comparison remain required. |

## Synthesis

Roles reviewed: 7. Open P1/P2: 0. P3 notes: 19, with source-use and release/science
conditions open. Verdict: APPROVED-WITH-CONDITIONS for local comparison and query
integration. Top finding: agreement between shared-altimetry products does not
establish observational independence or a physical range. CURRENT, SOUNDER and
BEACON agree this qualification must remain alongside results.

## Amendments applied

1. Declare shared satellite inputs and unresolved exact averaging support.
2. Bind original JSON bytes, documents, receipts, owners and map frames in Rust.
3. Expose both methods through keyboard map/card navigation with distinct patterns
   and an explicit unranked diagnostic value.

## Verification

33 focused Python tests and 29 subtests; 22 Rust tests; all acquired field/mask
readbacks; eight native loader rejection cases; native/WASM Loop query parity;
keyboard selection/card navigation/mobile; Gulf frame/playback, recorded-day,
generic query and route-decision browser regressions; rendered screenshots inspected.
Full publication CI and independent scientific admission were not run or claimed.
