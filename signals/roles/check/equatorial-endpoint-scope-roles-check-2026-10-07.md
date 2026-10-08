---
skill: roles-check
topic: equatorial-endpoint-scope
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, KEEL, LOGBOOK]
p1_count: 0
p2_remaining: 1
implementation_p2_remaining: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Equatorial endpoint context — internal role review

Artifact: source-context audit, checked index registration, scope test and reproduction plan. CURRENT reviews scientific scope; SOUNDER reviews provenance/ranges; KEEL reviews checked-store integration; LOGBOOK reviews publication status. No new map/control design or planetary analogy is introduced, so CHART, HARBOR and ORBIT do not need a new design review. The new source is available through the existing text-oriented source query interface.

| Role / finding | Severity | Evidence and disposition |
|---|---|---|
| CURRENT: branching latitude is not a whole-current dimension | P2 resolved | Metric and degree units are explicit; geometry, length and width remain null. Negative tests reject promotion. |
| CURRENT: surface and layer means describe different gates | P2 resolved | Each Madagascar reported mean has its own layer/method; no blended value admitted. |
| CURRENT: seasonal timing cannot define monthly route geometry | P2 resolved | False annual-geometry support is preserved and tested; axes and upstream gates remain missing. |
| SOUNDER: PDF text extraction corrupts degree symbols | P2 resolved | Printed pages 2527 and 620–621 rendered with Poppler and visually inspected before numeric transcription. No curve digitization performed. |
| SOUNDER: annual and filtered multiyear ranges must stay distinct | P2 resolved | Two Pacific ranges have different roles; Gaussian filter support remains explicit. Confidence-interval relabelling is rejected. |
| SOUNDER: model layer and source access differ between references | P2 resolved | 400/415-m caption/prose distinction recorded; failed author-link retrieval and replacement university URL preserved with PDF byte checksum. |
| KEEL: source context should be queryable through checked Rust | P2 resolved | Audit registered in 66-document corpus; regenerated catalog, gzip and engine manifest. Native/WASM query checks cover the two entries. |
| KEEL: stale dependencies could hide a changed identity basis | P2 resolved | Test validates three exact local input hashes and rejects a stale pin. |
| KEEL: original source-byte and current-directory checks must remain | P2 resolved | Source-store test retains all original-byte checks, NOAA oracle and input-failure cases; page check retains 100 currents and 12 dated NOAA maps. Both pass. |
| LOGBOOK: retrieved PDFs should not silently become shipped assets | P2 resolved | PDFs/renders stay in ignored review cache; audit names retrieval URLs/checksums and states cache is not a shipped dependency. |
| LOGBOOK: measurement rules should be recorded without rewriting frozen protocol evidence | P2 resolved | E01–E05 are explicit scope supplements; existing M01–M13 protocol and frozen release files are unchanged. |
| LOGBOOK: source context must not be described as published or canonical | P2 publication condition | Plan labels local candidate. Required remote gate and reviewed publication remain pending; no scientific admission claimed. |

## Synthesis and amendments

Four roles reviewed, zero P1 blockers, zero remaining implementation P2 issues. Publication remains conditional on required CI. This is an internal review of source handling, not independent scientific approval.

1. Preserve metric-specific range types and distinct source layers instead of a generic current margin.
2. Verify numeric claims on rendered pages and preserve access/checksum history without shipping source PDFs.
3. Add exact checked-index access and tests for scope promotion and stale identity basis.

## Verification

Endpoint scope test passes, including eight rejected mutations. All 36 Rust tests and native/WASM builds pass. Checked source-store/browser parity passes for 66 exact documents and the new two-entry audit. Index-page checks pass for all 12 dated NOAA inventories and 100 admitted currents, saved state, links, mobile layout and missing-corpus handling. Whitespace is clean. The full Python suite receipt belongs to the preceding inventory revision; it is not reused as a complete test claim for this source-context candidate. Required CI has not yet run for this candidate.
