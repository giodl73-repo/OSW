# Prepared Indian current query admissions and provenance projection

Same existing branch and draft PR83; no main merge. These adapters prepare
the combined data update without rebuilding or changing the active query
packet, dashboard, engine manifest, WASM binary or current inventory counts.

## Prepared identities

`analysis/indian_current_identity_query.py` verifies the frozen identity
review, naming candidates, protocol, original and acquisition receipt, then
builds/checks `research/indian-current-identity-query-contract-v1.json`.

The contract prepares four entities, ten preferred/abbreviated/spelling names,
two source references, four unmeasured length assessments, four separately
gated identity admissions and four unlocated object records:28 rows total.
It adds WICC, EICC, EACC and South Java as separate identities; EGC remains
unresolved. The two source references do not imply two new independent
datasets or observation campaigns.

Each object retains a direct identity/scope query and source query, an unknown
length, no route, width, measurement, state intersection or observation date,
and no measured capabilities. EICC preserves the source's seasonal and
intraseasonal qualification; it is not assigned a uniform annual reversal.
Fingerprints support future changed-record indication using the existing
dashboard hash convention. The contract status explicitly remains prepared;
it is not proof of canonical delivery.

The caller obtains the source-verified contract through `evidence()` and
applies it through `append()`. Every collision, name reconciliation and source
check precedes mutation. A pre-existing spelling or abbreviation requires
explicit identity reconciliation. Existing Monsoon/Somali/Throughflow IDs must
resolve; shared water or forcing never creates an alias or parent relation.
All older rows and unrelated collections remain exact.

## Inventory-wide source projection

`analysis/inventory_source_links.py` wraps the already prepared pure
`object_source_links.project()` helper. It indexes owner associations once
across the supplied final collections, including provider-specific rows.
Required entity/measurement/claim/geometry/media/route collections must all be
present. The source registry and object IDs must be unique.

Explicit source, method and snapshot references resolve through the registry;
each owner receives the unique ID list and its matching reference count.
Nested supporting prose dictionaries are not counted as sources. A failed
late owner leaves every earlier owner unchanged. An unchanged second
projection is idempotent. All physical quantities and rights remain exact.
The result does not claim that all external evidence has been discovered or
that registered references are independent publications or observations.

This prepares the correction for the117 count/list inconsistencies in the
captured runtime audit, including99 current-prefixed objects. It has not yet
corrected the live dashboard or reproduced that full audit after integration.
The known dashboard source-group list alias must also be removed in the same
coherent build; merely replacing its inflated count would hide lost refs.

## Checks and integration order

Contract build and read-only check passed. All36 focused tests passed:
15 identity-extension checks,13 inventory-projection checks and8 underlying
reference-projection checks. The identity tests include the actual historical
base plus its existing Southern East Madagascar extension, old-row preservation,
all six collision locations, normalized name collisions, missing distinguished
identities, immutable review/original failures and dimension/geometry promotion.

```powershell
python analysis/indian_current_identity_query.py check
python -m pytest -q analysis/test_indian_current_identity_query.py analysis/test_inventory_source_links.py analysis/test_object_source_links.py
```

The lightweight check joins the existing conformance job. No new CI job, PR,
local build or browser session was created for this preparation.

Remaining integration order:

1. Prepare the compatible calendar, dated regime, reported-width and offshore
   context records with explicit source grades and non-measurement counts.
2. Stage the four entities before building dashboard, taxonomy and seasonal
   inventories. Preserve existing identity/source records and route IDs.
3. Remove the dashboard source-group alias, retain complete explicit source
   IDs and append the Brazil reach and compatible Indian evidence.
4. Apply final source projection after all provider appenders. Recompute
   fingerprints and indexes from the same completed data revision.
5. Generate one coherent packet/index/native/WASM revision. Verify all old
   rows, exact sources, owner counts, new queries, unlocated-current selection,
   changed-record indication, qualified cards and keyboard/mobile delivery.
6. Complete physical length/width/seasonal evidence and geometry/state gaps;
   these name and provenance adapters do not close them. Full regression is
   still a separate final gate.

Local preparation and checks used one logical CPU BelowNormal, worker1.
The existing native/WASM free-space preflight remains in force; no active
engine input was modified to leave a partly rebuilt publication.

At commit`4d9f5347d234b173b6cade9d8296bb097592751e`, the actual log of
[conformance job120707825042](https://github.com/giodl73-repo/OSW/actions/runs/40039766625/job/120707825042)
was retrieved and inspected: the prepared identity contract check passed and
all36 identity/provenance checks passed. This is not canonical-delivery proof.
The same run's offline job120707825255 failed during original acquisition:
Rotschi1972 still returned HTTP403 before the full suite. No guard was skipped.
