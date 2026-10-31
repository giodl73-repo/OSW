---
skill: roles-check
topic: asca-shared-measurement-inventory
date: 2026-10-20
source_commit: fba615abc3946e2310fe637af14d8e3c2cf9a657
roles_used: [CURRENT, SOUNDER, CHART, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# Shared ASCA measurement record review

Internal functional review using `.roles/ROLE.md`, not external peer review.
These five roles cover the record's physical meaning, provenance, atlas
interpretation, executable validation and repository status.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | 100 m depth cannot be treated as height above bottom. | P2 resolved | Explicit vertical references; complementary endpoints are null; Python/Rust tests reject frame edits. |
| CURRENT | The −v component is not a flow-normal width. | P2 resolved | Separate metric and component-frame codes; table scope and protocol retain fixed-array interpretation. |
| CURRENT | Three thresholds do not add observations. | P2 resolved | Protocol declares 931 source profiles, 2,793 cases; primary flag includes all 601 unresolved cases. |
| SOUNDER | A normalized row could lose its exact source context. | P2 resolved | Stable timestamp/fraction ID, source profile ID/index, UTC, exact source hash and per-case pointer retained. |
| SOUNDER | Source peaks and derived alignment have different origins. | P2 resolved | Copy the frozen report's peak fields and six-decimal derived indicator exactly; adapter performs no calculation or reinterpretation. |
| SOUNDER | Filtering does not identify a tidal correction method. | P2 resolved | ASCA tidal removal is null; full physical association and dimensional admission remain false. |
| CHART | Shared query rows could hide incompatible frames. | P2 resolved | The table names the source frame and depth; existing monthly source plots and failure panels remain unchanged. |
| CHART | New data needs a direct atlas entry point. | P2 resolved | Rust scene supplies a current-filtered query link on the Agulhas card; record detail links to source and atlas. |
| CHART | Narrow layouts and source links need runtime evidence. | P2 resolved | Actual-WASM test passes all 2,793 cases, source-case navigation, export and 320 px layout. |
| KEEL | Python-only adaptation could permit forged bundles. | P2 resolved | Rust independently reconstructs all 2,853 cases and validates each owner's exact ID list and provider pins. |
| KEEL | Large JSON macros exceeded the compiler limit. | P2 resolved | Build base and peak metadata objects separately; no global recursion-limit relaxation. Focused Rust tests pass. |
| KEEL | New paths need a standing integration gate. | P2 resolved | Register the new inventory and existing REDSOX repeat checks in the shipped browser runner; pin the changed ASCA frontend module. |
| LOGBOOK | Added rows could be described as newly measured widths. | P2 resolved | Batch identifies this as exposing existing cases; source reports and width admissions are preserved. |
| LOGBOOK | Same-PR accumulation must continue. | P3 confirmed | All work stays on codex/current-measurement-gaps / draft PR83. |
| LOGBOOK | Older gates cannot be attributed to this extension. | P2 condition | Keep base774 full pass, fba EAC/Linux results and this extension's focused/browser proof separately identified. |

Five roles; no P1; one remaining P2 integration-status condition. Verdict:
APPROVED-WITH-CONDITIONS for continued draft work. Required amendments:
make vertical/component/time semantics explicit, independently validate
all cases and owner lists, and prove actual query/source/card navigation.
