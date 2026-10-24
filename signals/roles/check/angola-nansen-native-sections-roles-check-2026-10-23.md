---
skill: roles-check
topic: angola-nansen-native-sections
date: 2026-10-23
roles_used: 7
p1_count: 0
p2_count: 1
verdict: APPROVED-WITH-CONDITIONS
---
# Angola native source sections: role review

Artifact: licensed original data, frozen source-array compiler/protocol/preflight,
source inventory and native-array visual/query delivery. Seven installed roles
selected: CURRENT (physical meaning), SOUNDER (custody/masks), CHART (visual
encoding), BEACON (scientific explanation), HARBOR (equivalent access), KEEL
(reproduction and testing), LOGBOOK (publication boundary). ORBIT is not relevant.
This is one agent applying the seven installed role lenses, not seven independent
reviewers, external scientific review or a release approval.

| Role | Finding | Severity | Resolution / remaining action |
|---|---|---|---|
| CURRENT | The13-section transport reconstruction includes model-assisted filling and bathymetric relocation. | P3 | Preserve only the11 native Nansen sections; no reconstruction or filled physical edges. |
| CURRENT | A15–90km transport box is not a75km current width. | P3 | Widths, boundaries, annual ranges and current geometry remain null/unadmitted. |
| CURRENT | Nominal12S ship sections and near11S moorings/Meteor sections have different support. | P3 | Explicit separation in protocol, source report and view. No borrowed observations. |
| SOUNDER | Preserve every cell and missing value rather than dropping incomplete rows. | P3 | Every native coordinate/U/V array matches original NetCDF, with NaN masks and signed zeros checked. |
| SOUNDER | No independent quality flags or explicit time zone/calendar are supplied. | P3 | No invented QC approval or UTC/calendar conversion. Raw TIME epoch and absent metadata are visible. |
| SOUNDER | Provider originals and transformed fields must be distinguishable. | P3 | Original CC-BY-3.0 archive/index and acquisition hashes retained; separately labelled deterministic JSON/gzip fields and methods review. |
| CHART | Profile index cannot be read as distance offshore or a current path. | P3 | Axis labels state native profile/bin indices; selected cell shows reported coordinates and metres. No inferred map boundary. |
| CHART | Missing cells cannot share the zero-velocity encoding. | P3 | Patterned missing cells; diverging signed palette centred on zero, common range across sections for each native variable. |
| CHART | Source-file labels overflowed the phone view. | P3 | Short exact section IDs plus wrapped full filenames; final320px browser check passes. |
| BEACON | Large cell counts include missing cells and are not independent current observations. | P3 | Totals explicitly include missing cells; per-variable finite/missing counts and QC limitations accompany plots. |
| BEACON | Native U/V must not be called rotated alongshore flow. | P3 | Original variable names and m/s retained; no rotation applied. |
| BEACON | Original publisher custody and full-thesis review are unsupported. | P3 | Factual source review identifies the author-hosted151-page thesis, exact checksum and only selected inspected pages36/37/39. |
| HARBOR | Colour cannot be the only access to sign and missingness. | P3 | Exact cell table/record, numeric controls, source downloads and explicit missing text. |
| HARBOR | Every native cell needs pointer-free navigation. | P3 | Profile/bin numeric inputs, arrow-key canvas navigation and cell permalink verified. |
| HARBOR | An integrity error must not leave another section's stale data visible. | P3 | Clear field/table, disable cell controls during load; corrupt gzip checksum test verifies cleared state. |
| KEEL | Test the complete matrices rather than sampled pixels only. | P3 | Independent original-source equality covers2044320 U/V cells; browser compares all11 complete field objects and22 variable cases. |
| KEEL | A method altered after seeing results would invalidate the declaration. | P3 | Commit469160f freezes source/protocol/operator/12 synthetic checks/preflight before actual arrays. No frozen method changed. |
| KEEL | Fresh main integration, remote replay/UI and full successor coverage remain gates. | P2 | Source13 focused tests and complete source-view browser pass. Main integration/preservation/native-WASM checks pending at this review checkpoint;37-report/UI CI and a full successor offline gate remain required. |
| LOGBOOK | Proposed source ownership cannot silently create an accepted current. | P3 | Main diagnostic uses proposed_current_id with null current/entity IDs; pending-source dashboard list is separate. Verify absent canonical Angola object. |
| LOGBOOK | Copyrighted institutional thesis is not automatically redistributable. | P3 | Original/renderings private; only checksum, locator and factual review public. Licensed provider archive retains attribution. |
| LOGBOOK | Same-PR delivery and failed checks must remain visible. | P3 | Continue PR83. Retain missing-server, text-accessor, phone-overflow and intentionally cancelled delivery-build logs. No main merge or overall-green claim. |

Roles reviewed:7. P1:0; P2:1; P3:20. Verdict: APPROVED-WITH-CONDITIONS
for exploratory source-array delivery to the continuing draft. The top remaining
condition is broad/fresh coverage, not permission to infer widths. CURRENT,
CHART and SOUNDER agree that observed samples, model-filled reconstruction and
physical current boundaries must remain distinct.

## Amendments

1. Preserve native arrays and explicit NaNs, retain separate sampling supports,
   and prevent any transport-box-to-width promotion.
2. Replace overflowing file labels, preserve complete filename access, and clear
   stale data on failed source checksums; verify keyboard and phone behavior.
3. Complete main native/WASM/source/preservation checks, publish on PR83, collect
   fresh37-report/UI CI, and retain the full offline gate as an open condition.
