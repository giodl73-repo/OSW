# EAC array-distance readback repair

Continue current measurement work on draft PR83. No new gap-specific PR.

The complete local suite at774e466 passed 1,910 tests and 1,222 subtests.
Independent Linux run39546781976/job119046629288 at7a8d7dc then isolated
the remaining EAC source-quality failure to 124 numeric leaves in three
derived fixed-array distance fields. All other quality fields were exact.
Maximum difference: 4.234607331454754e-9 metres. The preceding sixteen
scientific reports also reconstructed exactly.

Implement `plans/eac-fixed-array-distance-readback-v1.md`: final calculated
metre distances have three decimal places; kilometre array length has six.
Keep exact validation, full-precision section-core calculations and source
bits. Renew dependent source contracts, report pins, summaries, calendar
pins, figure manifests, source index, dashboard and native/WASM bindings.

Verified against7a8d7dc:

- All other source-quality fields are exact after removing only renewed
  provenance metadata and the three declared distance fields.
- All 3,770 core profiles, 33,930 cases, core geometry and summaries are exact.
- Calendar values are exact; original source-profile JSON and selected NPZ
  bytes are exact.
- All six source/core/calendar SVG and PNG assets are byte-identical.
- 31 focused Python tests and 81 Rust tests pass. Actual browser checks and
  independent Linux reconstruction remain separate publication gates.

No new physical-width, length, annual-range, verified association or state
intersection admission. Those current data gaps remain active work. Review:
`signals/roles/check/eac-array-distance-readback-roles-check-2026-10-20.md`.
