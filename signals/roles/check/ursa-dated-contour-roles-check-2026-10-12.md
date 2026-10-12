---
skill: roles-check
topic: ursa-dated-contour
date: 2026-10-12
roles_used: [current, sounder, chart, beacon, harbor, keel, logbook]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Ursa dated contour: internal role review

Artifact: Figure 3 digitization protocol and audit, canonical release, Rust/WASM
proof checks, source overlay, atlas/object cards and OSW display-state joins.
This is an internal implementation review, not independent scientific admission.
CURRENT checks physical interpretation; SOUNDER provenance; CHART cartography;
BEACON explanation; HARBOR access; KEEL reproduction; LOGBOOK repository status.
ORBIT is inapplicable because no planetary analogy is used.

| ID | Role | Finding | Severity | Evidence and disposition |
|---|---|---|---|---|
| 1 | CURRENT | Closed pixels do not establish a verified whole-ring physical boundary. | P2 | Resolved for candidate use: publication-scoped attribution is unverified; physical admission is false and whole-eddy state relations stay unresolved. |
| 2 | CURRENT | The paper prints 0.65 cm; changing it to meters would invent a numerical contour. | P2 | Literal retained, normalization null; no numerical altimetry field reconstructed. Scientific unit resolution remains a condition of physical admission. |
| 3 | CURRENT | A single event date cannot establish annual extrema or recurring seasonality. | P2 | Resolved: 2021-03-07 support only, seasonal/annual eligibility false; no center, radius, physical area, width or current length admitted. |
| 4 | SOUNDER | Original images and exact transformation rules must remain recoverable. | P2 | Resolved: original XML/image/acquisition pins; frozen audit with source pixels, thresholds, axes and protocol hash; test environment pins OpenCV, NumPy and Shapely. |
| 5 | SOUNDER | Failed threshold cases must not disappear from an apparently successful uncertainty envelope. | P2 | Resolved: two threshold-100 non-simple pixel rings retained with reasons and null geographic geometry; 102 planned versus 68 valid geographic scenarios explicitly reported. |
| 6 | SOUNDER | Image adaptation requires source credit and truthful redistribution metadata. | P2 | Resolved: CC BY 4.0, original authors, DOI, source access and transformation notice; source-use registry now records original-figure redistribution and digitization. |
| 7 | CHART | The lower crop frame is not the latitude-25 calibration tick. | P2 | Resolved: common source axes [1121,1383,674,894], geographic values [-89,-85,28,25]; independent vertex calibration test. |
| 8 | CHART | Crisp geographic output and seven decimals could imply survey accuracy or a known datum. | P2 | Resolved: inferred linear figure-axis coordinates, unspecified datum/projection, display precision only; overlap uses approximate coast-masked OSW geometry. |
| 9 | CHART | Source tracing needs visible comparison with the original curve. | P2 | Resolved: Rust source-pixel SVG path over unchanged source Figure 3; cyan overlay inspected at 320 pixels, with full original figure available. No smoothing or frame closure. |
| 10 | BEACON | Existing Kraken-specific prose could assign the wrong date, authors or method to Ursa. | P2 | Resolved: source-specific credit and generic checksums; Ursa state claims use March 7 method/date and precise internal audit pointers. |
| 11 | BEACON | Geographic NASA crop overlap could be mistaken for event identification. | P2 | Resolved: 2021 is within declared 2021–2023 model years, individual-event alignment remains unresolved; ten navigation crops establish no NASA identity. |
| 12 | BEACON | Tested ranges could be described as statistical or physical uncertainty. | P2 | Resolved: scenario ranges explicitly exclude field error, unknown datum/projection, instrument artifacts and OSW boundary uncertainty; no probability or confidence claim. |
| 13 | HARBOR | Color alone cannot convey the source overlay's scientific meaning. | P2 | Resolved: SVG description and text provide date, tracing method, accepted/rejected cases and limits; state assessments are semantic text links. |
| 14 | HARBOR | Source-image widths may break narrow reflow. | P2 | Resolved: responsive overlay and locally scrollable full original; browser checks pass 320-pixel document containment for atlas and object. |
| 15 | HARBOR | Pixel-path previews may truncate away status fields. | P2 | Resolved: visible self-intersection reason, complete source-query records/downloads; browser checks returned rejection status and keyboard source navigation. Human assistive-technology review remains a follow-up. |
| 16 | KEEL | Re-signed receipts could promote physical boundaries or erase failed cases. | P2 | Resolved in native checks: frozen audit SHA, dependency pins and exact canonical candidate/geometry projections; eleven native mutation cases pass. All eleven shipped WASM rejection cases pass. |
| 17 | KEEL | Separate atlas/object geometry construction could diverge. | P2 | Resolved in native parity: shared plot scene and source overlay; browser parity and original-image decoding pass. No frontend geographic reconstruction introduced. |
| 18 | KEEL | Generated release, index and engine artifacts require complete regression gates. | P2 | Resolved: 1,280 Python tests and 923 subtests pass; new and existing atlas/object/screened/source-panel browser gates pass. Release/screened validators, 45 Rust tests and serialized engine build pass. |
| 19 | LOGBOOK | Candidate counts must not inflate verified scientific coverage. | P2 | Resolved: two editorial named footprint candidates, zero new verified physical footprints; current lengths, widths, routes and operational observations unchanged. |
| 20 | LOGBOOK | Shared source counters can mark unrelated eddy records as source updates. | P3 | Retained limitation: 136 object fingerprints change; all except Ursa reflect source metadata/count changes rather than new local geometry or dimensions. Record the exact collection diff. |
| 21 | LOGBOOK | Draft work and local validation are not mainline publication or hosted CI success. | P2 | Resolved status discipline: stacked branch; no merge/publication claim. Parent hosted run 37959985435 failed acquiring Qiu/Chen PDF after timeout; subsequent gates skipped. New hosted results must be recorded separately. |

## Synthesis and amendments

Seven roles, 21 findings. No P1 blockers. Editorial implementation is APPROVED-WITH-CONDITIONS for the declared
candidate scope; all required local regression gates pass. Scientific admission
remains pending regardless of local software checks.

Cross-role consensus: CURRENT, CHART and BEACON require the depicted contour,
its calibrated display geometry and a verified physical ring to remain distinct.
SOUNDER and KEEL require failed cases and original source hashes to survive.

Three amendments implemented during review:

1. Preserve the two invalid threshold-100 paths rather than repairing or dropping them.
2. Replace inherited Kraken claim prose with Ursa's date/method and exact audit pointers;
   correct the NASA year-range check without claiming event identity.
3. Bind audit, candidate, geometry and state scope in Rust; show the source trace
   beside the display map and test native/WASM mutations and atlas/object parity.

Evidence: `plans/ursa-dated-contour-digitization-protocol-v1.md`,
`research/ursa-2021-0307-figure-contour-audit.json`,
`analysis/test_ursa_contour_candidate.py`,
`analysis/test_ursa_contour_candidate_browser.py`,
`plans/ursa-dated-contour-batch-2026-10-12.md`.

Implementation: `961dcfe556a602b923613e79e7a273980a708ec2`; draft PR 81,
https://github.com/giodl73-repo/OSW/pull/81. Frozen committed source/dependency
bytes verified; hosted implementation gates are still in progress.
