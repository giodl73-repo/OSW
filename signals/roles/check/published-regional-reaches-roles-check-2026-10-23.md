---
skill: roles-check
topic: published-regional-reaches
date: 2026-10-23
roles_used: 7
p1_count: 0
p2_count: 3
verdict: APPROVED-WITH-CONDITIONS
---

# Published regional reaches: internal role review

Artifact: original-reviewed Algerian coastal-reach report and schematic,
query adapter, proposed canonical builder wiring, Rust guard and browser check.
This is an internal review using installed role lenses, not external scientific
review. Publication target remains the existing draft PR83; no main merge.

Selected CURRENT for physical quantity and observation support; SOUNDER for
original custody and uncertainty; CHART for schematic/map distinction;
BEACON for public meaning; HARBOR for equivalent access; KEEL for deterministic
admission; LOGBOOK for accurate repository and gate status. ORBIT is not
selected because the artifact contains no extraterrestrial comparison.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| C1 | The strict greater-than threshold describes a regional coastal reach; it does not identify a whole-current centreline or physical minimum centreline length. | P3 | Frozen report constraint and protocol | Retain separate quantity, unknown upper endpoint and unranked/null whole-current fields. Existing source checks verify these distinctions. |
| C2 | Combined satellite/ship support ends22May1986; ship-only methods end21May. Neither endpoint dates every sample. | P3 | Report source and time support | Keep both windows and the support-kind label. Do not interpolate a seasonal record. |
| C3 | Coast proximity30km and upper-current descriptions elsewhere in the paper do not define paired current edges or a homogeneous fixed-layer length. | P3 | Source context | Keep physical width false and do not transfer a fixed layer, width interval or seasonal margin. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| S1 | The exact853466-byte DTIC original is pinned against provider size/MD5/SHA1 and local SHA256, with an acquisition receipt. | P3 | Source custody | Preserve the original and provider receipt; do not substitute an unverified download. |
| S2 | The archive lacks printed1596–1597; verified abstract/results pages support this claim, without a full-paper review. | P3 | Source record and diagram | Keep incomplete-copy status and the selected locators visible through the source query. |
| S3 | Numerical uncertainty and a finite upper endpoint are absent, rather than zero. | P3 | Constraint fields | Retain nulls and strict comparator. Exact Linux reproduction of the frozen report and SVG is verified in CI for commit cfff6f1. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| T1 | The open circle and right arrow are a schematic constraint, with no geographic projection or scale. | P3 | Frozen SVG | Preserve the explicit non-geographic caption; do not turn it into a route or buffer. |
| T2 | Atlas geometry remains the existing reference geography, rather than a new measured path associated with the reach. | P3 | Builder wiring | Preserve route/geometry rows exactly in the before/after comparison. |
| T3 | Regional labels, dates, source and unknown upper endpoint appear beside the displayed threshold. | P3 | SVG and card labels | Keep these qualifications when reusing the visual in other atlas surfaces. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| B1 | A reader could repeat300km as an exact whole-current length if the operator or regional label is shortened. | P3 | Card link and query row | Retain the visible greater-than sign, dated regional label and separate collection. |
| B2 | The evidence path prepares a short chain from current card to diagram, query record and source custody. | P3 | Adapter card links | Verify the actual links after the engine rebuild; prepared links alone establish no runtime result. |
| B3 | The primary paper remains distinct from the internal extraction method. | P3 | Two provenance records | Keep both labels and avoid implying that OSW measured the published reach. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| H1 | SVG title/description and full text communicate the threshold without depending on color. | P3 | Frozen SVG | Preserve the textual alternative and non-geographic explanation. The static render was inspected. |
| H2 | Mobile and keyboard navigation into the new query record has not yet run against rebuilt WASM. | P2 | New registered browser check | Complete the320px keyboard disclosure/link check and inspect screenshots before claiming atlas delivery. |
| H3 | The diagram is static and introduces no new motion controls or seasonal playback. | P3 | Evidence links | Do not enable annual animation for a single dated source statement. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| K1 | First data preservation caught a displayed source count of 6 for 4 registered references, caused by supporting metadata being counted. | P2 | Algerian dashboard card and adapter | Count actual registered IDs using linked_source_count. The corrected adapter's13 focused checks pass; native validation now checks count, uniqueness and reference resolution. Final generated-data preservation remains pending. |
| K2 | The native guard and builder wiring have not yet been compiled or exercised against the corrected complete corpus. | P2 | Canonical integration | Finish preservation, native tests/atlas, WASM and the registered browser check serially. No runtime completion claim is justified yet. |
| K3 | The current offline CI failure occurs during Rotschi (1972) original acquisition with HTTP403, before the complete offline suite. | P3 | CI source acquisition | Preserve the failing gate and address source availability separately; do not skip source verification. User resource instructions defer the full local regression to the final batch gate. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| L1 | Scientific method/source inputs were frozen at c2adb97 before actual report execution, and the original products remain unchanged. | P3 | Protocol/preflight/history | Preserve that history and every failure diagnostic. Delivery-glue corrections do not revise scientific products. |
| L2 | Runtime preparation and actual admission are different milestones. At review time, corrected data generation is live and native/browser gates are pending. | P3 | Batch plan and progress receipts | Update the public plan with actual final receipts; keep the overall core-gap goal active. |
| L3 | This closes a dated regional evidence gap while whole-current lengths, widths, seasonal envelopes, eddies and state joins remain broader outstanding work. | P3 | Coverage statements | Do not report a new ranked length, annual envelope, official eddy inventory or complete atlas coverage from this batch. |

## Initial synthesis

Roles reviewed: 7. P1 blockers: 0. P2 issues: 3. P3 notes: 18.

Initial verdict: **NEEDS-WORK** until the already authorized runtime gates pass.
Top finding: generated source counts must represent registered source records,
and the prepared integration still needs actual native/WASM/mobile evidence.
HARBOR, KEEL and LOGBOOK agree that preparation is not proof of delivery.

Three amendments:

1. Fix the actual source-count field and validate unique, resolvable provenance
   references; correction implemented, final data comparison pending.
2. Complete the native guard, complete-atlas validation, WASM build and mobile
   keyboard test sequentially, with the user-requested one-CPU/BelowNormal limit.
3. Align the plan and draft-PR status with those actual receipts, while preserving
   the separate acquisition403 and incomplete full-regression status.

This review does not ask the user for approval or stop the work. Verification
continued in the existing serial workflow.

## Final gate update

All three initial P2 findings are resolved for this working-atlas batch:

- **K1:** Data preservation passed with 108,440 old rows exact, only the Algerian
  card changed and four added records. The card has five actual registered
  references. An existing OSW-authored NASA-crosswalk ledger reference is
  restored; its source metadata and rights were not upgraded to NASA data.
  Native validation checks reference resolution, uniqueness and source count.
- **K2:** All 150 Rust tests passed. Cargo confirmed unchanged compiled native
  code after the query-only reference correction; the complete native atlas
  passed against that corrected packet. The 49,316,863-byte WASM matches the
  compiled output, and all 722 engine input hashes verify. Only two presentation
  hashes changed later, with compiled dependencies and binary unchanged.
- **H2:** Four exact records passed native/WASM parity. The mobile atlas link
  and inspector work with the keyboard at 320 px; the source diagram loads and
  reflows without root horizontal overflow. Table and inspector text show the
  strict threshold and unknown upper bound/uncertainty. All four final desktop
  and mobile screenshots were visually inspected. No original data downloads
  or page errors occurred in the passing run.

Visual review also found and corrected an undefined collection caption and a
table value shown merely as a generic record. The existing query inspector now
embeds the frozen source schematic with an equivalent textual explanation.
The first combined-browser mobile reload timed out; a serial desktop/mobile
browser check, with explicit error diagnostics and reduced concurrent workspace
memory, passed. No timeout was increased and no admission check was removed.

Current verdict: **APPROVED-WITH-CONDITIONS for internal draft delivery**.
P1 open: 0. P2 open: 0. Historical P2 findings: 3, resolved above. The P3 conditions
retain the unmeasured whole-current dimensions, incomplete-original notice,
external scientific-review limits, broader source-reference audit, incomplete
full local regression and the separate remote acquisition403. The overall
core-gap goal remains active; this verdict is not main-merge approval or
evidence that every current/eddy is measured or every UI mode was retested.
