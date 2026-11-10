---
skill: roles-check
topic: caribbean-dated-width
date: 2026-10-13
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Caribbean dated width review

Internal role-lens review of source extraction, compiled scope binding and
existing card presentation. All seven roles apply because this is scientific
data exposed in the atlas. It is not independent scientific verification.

| Role | Finding | Severity | Section | Resolution |
|---|---|---|---|---|
| CURRENT | 410 km is a historical section span with a geographic southern limit. | P3 | Boundary rule | Preserve region and operator; no whole-current admission. |
| CURRENT | 1600 dbar is reference pressure, not width layer. | P3 | Layer | Null depth slab; native/WASM negative cases pass. |
| CURRENT | One October description cannot supply annual extrema. | P3 | Time | Preserve 1974-10; calendar/playback disabled. |
| SOUNDER | Original bytes and provenance are reproducible. | P3 | Acquisition | Pin SHA, size/pages and original URL. |
| SOUNDER | The historical upper mile unit is unqualified. | P3 | Range context | Raw endpoints retained; normalized range null. |
| SOUNDER | July 1982 publication differs from archive upload. | P3 | Citation | Confirmed original header; both dates recorded separately. |
| CHART | Width does not locate paired boundaries. | P3 | Geometry | Keep geometry null and buffer eligibility false. |
| CHART | Meridional span is not a reproduced perpendicular width. | P3 | Orientation | No rotation or inferred axis. |
| CHART | A point must not imply an error interval. | P3 | Chart | One approximate point; uncertainty explicitly unknown. |
| BEACON | Headline needs the historical date and section. | P3 | Caption | October 1974 and 67 W displayed beside value. |
| BEACON | Speed context must retain geostrophic method. | P3 | Caption | 0.66 m/s labelled surface geostrophy. |
| BEACON | Gap closure needs a scoped meaning. | P3 | Coverage | One evidence-owner gap closed; annual gaps remain. |
| HARBOR | Point color cannot carry the numerical claim alone. | P3 | Chart | Numeric label, dated caption and SVG description present. |
| HARBOR | Evidence must be reachable without map interaction. | P3 | Links | Static inspector and source query available. |
| HARBOR | Narrow layout must retain caveats. | P3 | Mobile | 320-pixel browser gate and screenshot inspection pass. |
| KEEL | Editable receipts could coherently promote dimensions. | P3 | Admission | Eight native and two WASM mutations rejected. |
| KEEL | New fixture must keep existing exact-byte policy. | P3 | Hydration | Registered original; PDF remains outside Git. |
| KEEL | Global inventory checksum changes affect seasonal dependencies. | P3 | Regeneration | Reviewed checksum refresh; route values unchanged. |
| LOGBOOK | Canonical physical claims are unchanged. | P3 | Status | Record source-extraction class; no official physical approval. |
| LOGBOOK | Unrelated records must retain their prior evidence. | P3 | Comparison | All 127 records/99 decisions and 239 other fingerprints unchanged. |
| LOGBOOK | Local gates cannot imply hosted success. | P3 | Publication | Full local result and hosted handles recorded separately. |

Roles reviewed: 7. P1: 0; P2: 0; P3 notes: 21.
Verdict: APPROVED-WITH-CONDITIONS for attributed editorial extraction only.
Top finding: retain dated section support and unresolved historical units.
CURRENT, CHART and SOUNDER agree that this cannot define physical boundaries
or annual dimension margins.

Amendments: (1) preserve unresolved units and reference pressure; implemented;
(2) expose date/method/null uncertainty beside the value; browser verified;
(3) retain full-suite/hosted status and scientific admission limits in the
publication receipt; full suite passes 1,293 tests and 925 subtests.
