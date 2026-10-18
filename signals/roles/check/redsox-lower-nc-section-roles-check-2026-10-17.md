---
skill: roles-check
topic: redsox-lower-nc-section
date: 2026-10-17
roles_used: 7
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Red Sea local section calculation review

Artifact: original-source numerical calculation, declarations, conditional
and supported-local-core results, alternate-format probe, scientific figure,
tests and plan. Seven installed role lenses were applied directly by the
implementing agent. No independent expert or sub-agent review is claimed.

| Role | ID | Severity | Finding and disposition |
|---|---|---|---|
| CURRENT | C1 | P2 |6km belongs to the40–80m secondary layer/local-core follow-up. Primary20–60m remains unknown; no substitution or whole-current width admission. |
| CURRENT | C2 | P2 | Peak obliquity15.7° and only1.67 station spacings limit physical interpretation. Retain both; apply no cosine correction or rank. |
| CURRENT | C3 | P2 | Summer missing support is not a zero/absent plume. Preserve nulls and keep the known weak observations separate from missing profiles. |
| SOUNDER | S1 | P2 | Pressure and alternate formats cannot be silently substituted. Label TEOS-10 conversion and retain two non-equivalent MATLAB originals separately. |
| SOUNDER | S2 | P2 | Timing claims need qualification: prior format inspection exposed three cast10 tail rows. Preserve original declarations with an explicit history note; distinguish declared-before-calculation rules from the later local-core follow-up. No fully blinded preregistration claimed. |
| SOUNDER | S3 | P3 | Velocity perturbations are not per-cast confidence limits. Keep±0.03/0.04m/s finite scenarios apart from other sensitivities. |
| CHART | M1 | P2 | Connecting an excluded profile would invent support. Velocity lines use gaps; conditional source values use crosses. |
| CHART | M2 | P3 | Color cannot identify layers alone. Distinct markers and solid/dashed styles repeat layer identity. |
| CHART | M3 | P3 | Salinity is context with different units. Use separate panels and explicit sourcepsu label, not a velocity color scale. |
| BEACON | B1 | P2 |7.3km is conditional on excluded cast10. Never replace the primary null or headline it as an admitted current width. |
| BEACON | B2 | P3 | Two non-synoptic surveys do not supply annual extrema. Keep annual ranges null. |
| BEACON | B3 | P3 | A calculated local diagnostic does not increase source-width coverage. Retain149/79 published coverage and unregistered status. |
| HARBOR | H1 | P2 | Readers need equivalent meaning without color. SVG title/description, plan/table and complete numerical JSON provide it. |
| HARBOR | H2 | P3 | Four scientific panels are dense on narrow screens. Provide scalable SVG and numerical alternative; no interactive/mobile UI pass claimed. |
| HARBOR | H3 | P3 | Motion would not establish seasonal continuity. Keep the plot static; no physical playback introduced. |
| KEEL | K1 | P2 | Layer integration can accidentally bridge missing observations. Test actual-coordinate integration, missing support, maximum gaps and no extrapolation. |
| KEEL | K2 | P2 | Missing-before-crossing and any-missing rules differ. Separate their outputs and test missing points both inside and outside crossing brackets. |
| KEEL | K3 | P2 | Incomplete40% sensitivity cannot produce a complete error range. Preserve nulls; numerical regression tests require them. |
| LOGBOOK | L1 | P2 | Active1606-test baseline predates this candidate. Develop in isolation; no completed combined gate or remote green claimed. |
| LOGBOOK | L2 | P3 | Compiled/query assets are unchanged. Label this research preparation, not a newly indexed product measurement. |
| LOGBOOK | L3 | P3 | Optional format review must not add default network/dependency gates. Retain numerical originals; SciPy probe is explicitly optional. |

Roles reviewed:7. Original findings:0 P1,12 P2,9 P3. All12 P2 findings have
concrete amendments applied. Verdict: **APPROVED-WITH-CONDITIONS** for the
reproducible diagnostic, not physical width admission.

Top finding: preserve the primary unknown while showing what the observed
secondary layer can support. CURRENT, SOUNDER, BEACON and KEEL agree.

Three amendments applied:

1. Keep strict primary, later supported-local-core and unresolved-source
   conditional calculations separate, with original declaration hashes.
2. Preserve excluded profiles, all null scenarios, actual vertical axes,
   source join offsets and non-equivalent alternate products.
3. Add failure-oriented numerical tests, the official TEOS-10 example,
   separate velocity/salinity panels and non-color numerical alternatives.

Executed:9 tests pass in2.15s; optional alternate-format probe executes;
final scientific figure visually inspected. The1606-test run at24cc05e is
still active and is not attributed to this later candidate. Final combined
focused and staging results are recorded after execution.

Final combined focused result: **42 tests pass in10.57s** across this section
calculation and the three previously added research modules. All original
declaration claims retain the explicit prior-exposure qualification. No
physical measurement or compiled-store count changes are implied.

Staging verifies16 exact files, with no source/publisher PDFs. The final SVG
repeats SHA256
`f56167fb865d8a8eca58b00cbc8a496a7414097dabcbf2487f56c490d356c8b7`
on consecutive builds. The alternate-format probe also rejects a coherently
changed receipt through its separate frozen receipt hash. Scientific inputs
remain the original pinned ASCII products.
