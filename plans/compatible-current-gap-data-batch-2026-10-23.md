# Compatible current data batch: identity, source evidence and provenance

Same existing branch and draft PR83. This prepares one coordinated data update
without changing the active dashboard/query/native/WASM publication.

## Prepared records

`analysis/indian_current_evidence_query.py` verifies the frozen source reports,
originals and figures and prepares40 records. The underlying source products,
protocols, scientific producers, tests and traces remain unchanged.

| Collection | New rows | Meaning |
|---|---:|---|
| `current_direction_calendars` |2 | Source profiles and access grades; qualitative month highlighting only. |
| `current_direction_descriptions` |24 | Month/direction descriptions, zero independent observations. |
| `current_reported_width_evidence` |3 | EICC100/200/250km statements with different support; zero canonical width samples. |
| `current_cross_shore_context` |4 | EACC offshore extent, core position, eastern boundary distance and transport concentration; not width intervals. |
| `current_regime_context` |1 | Abstract-qualified6-21March1994 WICC episode, not March climatology or named eddies. |
| `sources` |6 | Four scoped publication references and two internal methods; not six independent datasets. |

The identity extension with four explicit route gaps adds32 rows and the Brazil initial
reach adds4. The compatible source batch therefore stages76 new records, including
four unlocated current identities. No new whole-current length, measured
width sample, annual range, footprint, state intersection or physical seasonal
animation is inferred. Existing independently admitted dimensions stay exact.

The new collection names keep reported context queryable without mixing it
into physical measurement/sample statistics. Month descriptions retain null
observation years and velocities. WICC March/October remain unspecified even
though a separately dated March1994 episode is indexed. The altimeter subset
window stays unknown. Widths retain the T24 two-day support and21m source
context separately from the broader observational and combined model/discussion
statements. EACC coast-referenced distances are not paired width edges.

Sources retain abstract/full-original distinctions, document hashes where
known, selected-page review scope and redistribution boundaries. The1998/2022
WICC sources do not acquire full-paper verification. The2015 original remains
ignored, and the2020 review retains its printed CC BY4.0 basis. Every new owner
context reference resolves; links point to exact source queries and existing
qualified SVGs. Native/browser presentation of these collections is pending.

## Atomic preparation

`analysis/current_gap_admission_batch.py` stages identity, Indian source
context, complete registered provenance and the Brazil reach, then runs final
provenance projection. It copies affected collection lists, creates new owners
and detaches existing owners through pure projection before updating Brazil.
It shares large scientific/source-array payloads read-only. A late Brazil or
provider error leaves all original collections unchanged.

The known omitted media reference is restored before the Brazil adapter's
strict owner checks. Final counts match complete registered ID lists and do
not count metadata dictionaries. Source and object fingerprints are recomputed
for future changed-record display. Registered references are not counted as
independent publications or observations.

The staged Brazil owner also carries the three reviewed card links, initial
reach scope note and separately named regional-reach capability. Its claim
count/review metadata are updated from the final associated claims. The1500km
reach is not copied into its whole-current published-length field, and older
physical capabilities are preserved.

## Verification

The evidence contract built and reproduced exactly. All19 focused batch tests
passed. They cover76-row staging, original physical/source-array object sharing,
old-row preservation, dated/qualitative distinctions, scope and rights retention,
all six evidence-collection collision cases, late Brazil failure, unresolved
provider references, duplicate commits, changed frozen source rejection and
five prohibited promotions. The37 identity/provenance
checks remain separate coverage.

```powershell
python analysis/indian_current_evidence_query.py check
python -m pytest -q analysis/test_current_gap_admission_batch.py
python analysis/check_current_gap_batch_delivery.py
```

The read-only delivery driver requires the exact local originals and never
downloads them implicitly. The existing advisory source CI job runs it after
the explicit Brazil/EICC acquisitions and retains receipts/logs only. Missing
originals still fail; no guard is skipped. The Linux batch pass is recorded
below. These preparation checks are not a full-runtime or full-regression
pass.

The local read-only replay driver passed: both prepared contract checks and
all19 batch checks completed without skips or acquisition. Receipt:
`.pytest_cache/current-gap-batch-replay/result.json`. The active722-input
engine publication remains unchanged; these are source/admission preparation
results, not a new canonical runtime snapshot.

At commit`df56453003d701024d883d6bdcbe2a5c96ec1f53`, the actual log from
[source job120711354997](https://github.com/giodl73-repo/OSW/actions/runs/40040860222/job/120711354997)
was retrieved and inspected. Its batch receipt reports both contract checks
and all19 batch tests passing. The same job had explicitly acquired the
originals earlier; the batch driver did not download them implicitly.
This prior commit predates the four added route-gap decisions and exercised
the then72-row preparation. Canonical delivery and the complete runtime audit
remain false in that receipt.
Private proof:
`.pytest_cache/current-gap-priority-20261023/current-gap-batch-execution/linux-source-batch-proof.json`.

## Remaining coordinated delivery

1. Integrate the new identities into dashboard, taxonomy, seasonal and atlas
   inventories before their completeness checks. Unlocated identities need
   selectable records, not invented routes.
2. Remove the dashboard source-group list alias and retain complete explicit
   source IDs. Apply this prepared batch after provider records exist and
   refresh all fingerprints/indexes from the same complete data revision.
3. Add typed native/WASM guards and source-qualified object/inspector/card
   sections for the five collections. Preserve null dates/layers/edges, source
   support categories and physical capability counts.
4. Generate one coherent data packet/index/engine revision, run old-row and
   full reference audits, and verify exact queries, changed-record indication,
   map-to-card selection, seasonal descriptions, keyboard/mobile access and
   source/figure rendering. The native SVG renderer's omitted linked citation
   text still needs actual browser verification.
5. Continue the remaining physical measurement, geometry, eddy and state gaps.
   Full regression remains a separate final gate.

The next quantitative admission candidate is the about100km T24 width: its
primary full text, source-associated21m level and23-24December2013 transect
bounds are now available. Assess it for a separately admitted scoped published
width under the existing prose protocol after identity admission; do not stop
at this source-context projection as the final width deliverable. It would
remain distinct from raw width samples, whole-current width and annual ranges.
The broader200/250km statements require their own support/scope decisions.

Local work uses one logical CPU BelowNormal, worker1 and sequential source
checks. Native/WASM builds remain held by the existing disk preflight.
