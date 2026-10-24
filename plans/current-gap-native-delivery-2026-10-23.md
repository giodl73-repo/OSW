# Native delivery of the current gap batch

## Verified parent application

The source job at commit `868ff2cdc462cacdcc921e93f995288357f6f969`
passed: [job 120722341232](https://github.com/giodl73-repo/OSW/actions/runs/40044299703/job/120722341232).
Its actual job log reports 108524 candidate rows, 246 objects, 106 named
currents, 171 scoped width records and zero source-count/reference mismatches.
All 108203 prior non-object rows and 242 prior physical objects were preserved.
The follow-up fingerprint check verified all 123 unchanged objects retained
their old fingerprints. These are cloud rehearsal results, not publication.

## Native changes

`rust/osw-query/src/current_gap_admissions.rs` binds the four delivery contracts
and route worklist by exact compiled bytes, checks their dependency digests,
and requires an explicit `current_gap_admission_version` of
`indian-coastal-brazil-t24-v1` when this cohort is present. It checks every
non-object addition exactly, including the separate later T24 admission link.
It checks new-owner physical limits, context ownership/capabilities and unique,
registered source references/counts. Existing guards remain enabled.

The current catalogue adds the four admitted identities only for this cohort.
Planning resolves their separate, still-unresolved route decisions. Seasonal
width validation and snapshot exports include the single scoped T24 width.
The shared identity-decision function now restricts the Madagascar admission
to Madagascar; other currents cannot inherit its width merely because the
old measurement collection exists. The EICC has its own scoped decision.

Three new guard tests exercise exact source semantics, tampered receipts,
missing descriptions and wrong width ownership. A catalogue regression test
exercises the Madagascar flag with an unrelated identity. Formatting parsed
the edited Rust successfully; compilation/tests are pending cloud execution.
No local native/WASM build or complete-packet parse was started.

The engine builder now pins the new Rust module and its five compiled JSON
inputs. It does not add ignored copyrighted originals to deployed assets.
The cloud atlas job waits for the source job before native/WASM compilation.

## Remaining publication gates

1. Compile and run native tests in the cloud; inspect actual results.
2. Prepare the complete candidate manifest with the explicit cohort version
   and all contract/dependency pins; refresh dashboard, taxonomy and index
   receipts coherently. The dashboard source-list alias still needs repair.
3. Validate the actual 79-row complete-parent candidate through the native
   store, object cards, query collections, route-gap lookup and seasonal views.
4. Rebuild/install coherent engine artifacts, then check shipped WASM and
   accessible cards/maps. The newly added currents still have no geographic
   route geometry; a naming source is not a route or state-join measurement.
5. Keep the full regression gate and its original-source availability blocker
   visible. The old Rotschi PDF failure is not waived by these narrower checks.

The checked-in packet still has 102 named currents. Until the gates above
pass, source changes and prepared records must not be described as live atlas
coverage. Engine artifacts need regeneration after these source edits.
