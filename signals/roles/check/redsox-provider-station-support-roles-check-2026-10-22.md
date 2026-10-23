---
skill: roles-check
topic: redsox-provider-station-support
date: 2026-10-22
source_commit: 26e87ec
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
verdict: APPROVED-WITH-CONDITIONS
---

# REDSOX provider-record support review

Internal application of installed project lenses, not independent scientific
approval. Source commit26e87ec freezes the method before full classification;
actual report, view and main delivery follow it. Selected records/methods were
already visible, so this is exploratory. ORBIT excluded: no planetary analogy.

| Role | Finding | Severity | Evidence and action |
|---|---|---|---|
| CURRENT | Matching metadata do not prove synchronized or independently verified physical casts. | P3 | Every such flag stays false; source review, view notice and typed diagnostic state the limit. |
| CURRENT | Summer packet-loss context must not be asserted as a known winter failure. | P3 | Separate campaign clock context preserves summer limitation and winter nonverification. |
| CURRENT | Archive membership is not current/plume membership. | P3 | Transit/far-field notice, unchanged source membership flags and no new observation set/geometry. |
| SOUNDER | New agreement fields must not repair old raw headers silently. | P3 | All original metadata,444 joins and reviewed-support fields preserved; no nearest-neighbor or reviewed-field substitution. |
| SOUNDER | Signed timestamp differences can be mistaken for duration or a shift. | P3 | Roles retained; both signs allowed; eight tests include inverse agreement with original offsets and explicit missingness. |
| SOUNDER | Original methods/custody should be reproducible and rights-preserving. | P3 | Five NCEI originals match old hashes; ignored cruise PDFs restored, original imagery/text private, source review attributed. |
| CHART | A compact matrix can imply a quality grade. | P3 | Blue/amber/grey encode station-field states only; symbols/legend explicitly exclude velocity-processing quality. |
| CHART | Reported positions cannot become a current map or footprint. | P3 | Metadata diagram only; all old map features/routes/state relations preserved by complete comparison. |
| CHART | Empty filters could imply no observed current. | P3 | Empty states refer to metadata records; all445/461 records remain and source scope is explicit. |
| BEACON | Literal time-role enums and long checksums were hard to read on phones. | P3 | Replaced by plain-language roles and labelled checksum prefixes; full unchanged record remains accessible; final browser passes. |
| BEACON |431 positive labels could overstate what has been verified. | P3 | Wording says provider fields agree, not verified measurements; raw/clock/processing limitations remain adjacent. |
| BEACON | A404 alone is weak evidence of global data absence. | P3 | Four documented version/format directories and positive controls checked; explicit point-in-time/non-global limitation retained. |
| HARBOR | Data meaning needs equivalent noncolor access. | P3 | Prefix symbols, labelled controls, text checks, full source records and unmatched-record table. |
| HARBOR | All station states and empty/missing cases need real interaction coverage. | P3 | All445 selections and12 campaign/status combinations,17 CTD-only rows, keyboard/history/fallback and320px pass. |
| HARBOR | Current-card-to-source path must preserve selection. | P3 | Actual mobile keyboard card→view→station73 query returns the exact complete source row. |
| KEEL | Source numeric equality diverged from collection semantics. | P3 | Red test reproduces−919.0≠−919; precise shared scalar comparator repairs eq/ne without bigint rounding or null/missing changes. |
| KEEL | Source transport equality needs full, not sampled, verification. | P3 | Native/WASM exact comparison covers all445/461 metadata,13 reviews, missing/extra records, directory checks and3 numeric cases. |
| KEEL | Broad and fresh remote coverage remain separate conditions. | P2 |134 Rust/8 focused tests and587 engine pins pass locally; new36-report/UI CI awaits publication, old full1f4 suite is terminal:2250 tests/1248 subtests passed,16 failed; fixes and a fresh full gate remain outstanding. |
| LOGBOOK | A source-only stage must not be labelled main-atlas delivery prematurely. | P3 | Current batch now records actual501-document/card/query/native/WASM completion, with fresh CI explicitly pending. |
| LOGBOOK | Data augmentation must preserve prior scientific state. | P3 |106,814 prior rows checked; only one source metadata object changes. All495 source descriptors/bytes and144 protected files exact. |
| LOGBOOK | Continuing work should not create a PR per gap or imply release approval. | P3 | Same branch/draft PR83; no main merge, new physical measurement, canonical admission or original-publication upload. |

Roles reviewed:7. P1:0; P2:1; P3:20.
Verdict: APPROVED-WITH-CONDITIONS for local exploratory metadata/query delivery.
Broad regression diagnosis and fresh integrated remote checks remain open.
No physical width or synchronized-cast admission is approved.

Three amendments implemented: explicit separation of metadata agreement from
physical/sample proof; readable mobile roles with complete raw evidence;
precise source-query scalar equality with a demonstrated failing regression,
boundary tests and complete actual browser/native comparisons. Cross-role
consensus CURRENT/SOUNDER/BEACON: do not turn agreement into physical proof.

Follow-up2026-10-23: af7e317 published on the same PR83. Run39962292935 scientific job120443051226 passes all36 byte-exact report replays, and conformance job120443051274 passes69+4+8 tests. Full browser CI and repaired full local coverage remain pending; offline CI original-paper acquisition still returns HTTP403 before tests. The P2 overall-coverage condition remains open.
