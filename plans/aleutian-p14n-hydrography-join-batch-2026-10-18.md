# P14N hydrography and observed velocity correspondence

Continue branch `codex/current-measurement-gaps` and draft PR #83. Parent: `4267da6690a5f9d00fadd0bcf15c56a2859c4c58`. No additional PR or main merge.

## Source and declaration

Official CCHDO P14N cruise325023_1 supplies the CF-NetCDF, original station summary, original text report and current cruise-page history. Acquisition retained6,776,309bytes across four original files. The original receipt is preserved locally; its public version omits expiring redirect queries and records that transformation, generator and original-receipt hash. Original data bytes, acquisition producer, retrieval time and stable source request URLs are unchanged. The acquisition producer remains checksum-bound and refuses replacement of originals.

The join preflight was written after viewing the SADCP velocities but before inspecting the acquired temperature/salinity values. Metadata clarifications fixed the pressure conversion, QC rule, nominal-bottom-time interpretation and upper-ocean display support before property inspection. No blinded or externally timestamped preregistration is claimed.

## Measured support and fixed join

- The archive contains198profiles; do not equate these with independent stations. Selection40–48N,178–180E,7–18July1993 retains17CTDcasts from the northern leg. Repeat-cast identity is preserved, including41:3 and42:2.
- All17CFtimestamps and original profile headers agree with unique BO events in the station summary. BO is cast-bottom time. BE/EN events and original line numbers remain available; no exact time of passage through100–300m is invented.
- Retain3,009source cells at converted depth0–350m, all component-specific flags and raw finite values. Only2,525cells meet joint WOCECTD2. The482cells involving edited/despiked code7 and two questionable-salinity code3 cells are retained separately, rather than relabeled missing or primary acceptable data.
- Keep pressure in dbar beside `-gsw.z_from_p(p,latitude,0,0)` depth using pinnedGSW3.6.23. Temperature is in-situ ITS-90; salinity is practical PSS-78. No hydrographic layer means or interpolation are introduced.
- Preserve every pair satisfying absolute nominal-bottom-time offset≤3hours AND WGS84 position separation≤15km. There are84pairs involving all17casts and84of132hourly velocity profiles. All17casts have multiple qualifying hourly profiles; no hourly profile has multiple qualifying casts in this source selection. The algorithm retains all qualifying pairs, including synthetic ambiguous cases in tests.
- Preserve the complete earlier velocity section as a nested object equal to its original published record. Earlier raw velocities, masks, layer means, spacing, bearings, source custody and figures remain unchanged.

The2001temperature-correction notice remains unresolved; a later exchange-conversion date is not proof it was applied. Do not silently correct the archive or claim independent validation. Physical named-current association, transverse edges, whole-current width, annual range and seasonal playback remain unadmitted.

## Shared atlas and query delivery

The existing Aleutian research diagnostic now carries the joined record. Its existing velocity plot remains the initial view; a selector adds the measured water-property/QC and pairing-offset figure. Source queries expose all17casts and84pairs, while original velocity and source links remain available. No new page or collection is needed.

Counts remain155scoped width records across81owners,43diagnostics and45collections. Indexed JSON documents increase321→324; shared research documents33→36; engine dependency pins89→90. There are143research dependency pins. Four earlier research scenes and42other diagnostics remain equal. Query collection changes are confined to Aleutian's object and diagnostic. Width inventory, seasonal frames and original JASADCP document/receipt bytes are unchanged.

## Focused verification and remaining conditions

- Joined source/registry:10tests with10subtests PASS11.06s. Final source-only6tests with10subtests PASS3.71s. Existing NumPy binary-size warning remains visible.
- Reference conversion test uses the TEOS-10 published pressure/depth example. Matching tests cover both time limits, the distance limit and multiple qualifying casts; every frozen input is corruption-checked.
- All60Rust tests PASS2.14s; locked native and actual WASM builds pass. Query bundle80,912,050bytes; WASM17,332,535bytes.
- Dashboard scope/name/route check:one test withfive subtests PASS79.33s. No width or proposed-current promotion occurs.
- Preservation proof passes for155width rows,42other diagnostics,four other scenes and every original velocity record field;90engine and143research working-file pins match.
- Original OSW figure inspected visually: units, quality distinctions, offsets, selection limits and caveats are readable. No source panel is copied and no current edge is drawn.
- Actual browser gate is running for allfiveowners,37source documents and42native/WASM corruption cases. Do not claim its final pass before completion; new cases include property/QC/depth, BO time, matching limits/offsets, interpolation, temperature-correction claim, units and raw-CTD binding.

The clean full suite at4267da6 is a separate predecessor gate and remains running. Its terminal result must be inspected, not inferred. A new clean combined gate is required after this batch is committed. Earlier aec3c7f failed solely on three disk-exhausted fixture writes; all three targeted repairs passed, and all28native cases remain in the streamed fixture helpers. Completed build caches were cleared only after verifying their prior gates were terminal and their PIDs gone; no original data were removed.
