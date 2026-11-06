# Western Pacific NECC: published model scale batch

Continue branch `codex/current-measurement-gaps` and draft PR #83. No additional PR or main merge. Parent: `ab0a5a8d05fdf078a830ae6f4fa089a0ed0f81ab`.

## Evidence and scope

Chen et al. (2016), doi:10.1002/2016JC012190, report approximately 100 then 130 km for a western Pacific NECC model axis-distance scale. Original university-hosted PDF: <https://www.soest.hawaii.edu/oceanography/bo/Chen_etal_JGR2016.pdf>. The acquisition receipt retains 8,585,355 bytes and SHA256 `89af9045ed11f2bf18903b405f6beae14fbe83a3c9ca0202d6cb25122b7d381e`. Original pages 2, 6, 7, 9 and 15 were visually inspected. Copyright is not a redistribution grant; the PDF and source panel images remain ignored local inputs.

The two kilometre values come from the authors' conclusion, not OSW conversion of Figure 8's latitude-degree axis. W is transport-weighted mean absolute axis distance, using positive zonal transport integrated over 0–150 m. Latitude support is 0–10 N; longitude averaging is 135–155 E. OFES monthly analysis covers 1960–2014 with a 13-month running mean for the figure. Exact state dates, raw model fields and width series were not acquired. No RMS, full-width multiplier, annual bounding range, confidence interval, geographic edges, seasonal playback or independent observed width trend is admitted.

## Delivery

- Two independently stored approximate source summary states with full operator and model context.
- Shared card, seasons and query renderer with independent scalar bars, numeric table, source query and record inspectors.
- Rust validates the original extraction and its five source inputs. A single-row query retains the two-state comparison context and identifies matching IDs explicitly.
- The separate 2013, 140 W OSCAR component-span candidate remains pending review and linked from the coverage row.
- Inventory: 153 to 155 scoped records; 80 to 81 owners. Indexed documents: 316 to 318. Collections remain 45, diagnostic rows remain 42, engine dependencies become 88.
- Exclusive coverage categories count current decisions; retained candidate sources may coexist with published scoped evidence.

## Verification receipts before commit

- 30 source/TLS tests passed in 1.30 seconds. Standard trusted-root certificate verification remains enabled; no partial-chain trust or verification bypass.
- 59 Rust tests passed in 2.36 seconds; locked native/WASM build passed.
- Combined scene comparison and retained NECC diagnostic dashboard: 2 tests passed in 23.98 seconds. Existing NumPy binary-size warning remains visible.
- Actual native/WASM browser checks passed for card, seasons, query, source query, inspector, filtered comparison, 320 px layout, keyboard and reduced motion. Existing candidate navigation resolves its 12 profiles. Eleven scientific/source corruption cases rejected by both engines. No direct research reads or automatic original downloads.
- All 153 earlier measurement rows, both derived candidate records, historical reviews and section diagnostics compare equal. Seasonal frames differ only in the inventory parent checksum. Query changes are confined to widths, objects and seasonal route parent receipts. All 88 working engine dependency pins match.

## Combined gate history and remaining gate

Earlier paired-vector head f3a6bce passed 1,656 tests and 1,099 subtests. Later Antilles head 01b9a55 completed with 1 failure, 1,661 passes and 1,094 passing subtests: a stale dashboard assertion expected zero scoped records instead of three. Parent ab0a5a8 repairs that assertion; its targeted test and five subtests pass. Neither historical run certifies this new batch. Run the full offline suite from a clean committed combined head and record its actual terminal result separately. A running gate is not a passing gate.

Review: `signals/roles/check/pacific-necc-model-axis-spread-roles-check-2026-10-18.md`.
