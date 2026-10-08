# Object-view editorial coverage: publication fix

2026-10-08. Goal remains active; data gaps and protected-main landing incomplete.

## Verified failure

Consolidated PR30 exact head f0c3f406b4fcbad157519b2b9d6d0716822beec0:
push runs 37743176988 / job 113198411957 and 37743177369 /
job 113198413657 both failed in test_rust_object_view_browser.py line 24.
The test demanded precisely the 20 canonical collections. Object views also
correctly carry the editorial eddy_recurrence collection introduced previously.
Native inspection of current:acc confirmed no missing canonical collection and
exactly one additional collection: eddy_recurrence. Canonical rows are unchanged.
A separate PR run 37743183053 failed during Qiu/Chen primary PDF acquisition.
These are distinct failures; no single explanation is assigned to all jobs.

## Correction

Assert exactly the canonical set plus eddy_recurrence, assert its declaration
as editorial and require every selected recurrence row to match the selected
entity. Include an actual recurrence owner in the object cases (10 objects).
Keep exact canonical import checks, row identity/order checks, full native/WASM
object equality, footprints, detection packets, unavailable first load and
320 px reflow. The extra collection is not admitted to the frozen release.

## Verification scope

Corrected object check passed. Dedicated nine-card recurrence check passed.
Shared runner resumed at the actual failing check:

```powershell
python analysis/run_rust_query_browser_checks.py --from-check test_rust_object_view_browser.py
```

This runs the final 27 of 52 checks, preserving the explicit installed Chrome
override locally. The previous exact scientific head 1b3ea53 has 821 tests /
647 subtests and 38 Rust tests passing; this change edits only browser assertions.
Do not claim a complete final-head suite from that earlier result. The resumed
runner result will be recorded when terminal; neither an observation timeout nor
an unchanged job implies failure or completion.

## Publication

Fresh fetch confirmed main e9c9d2083dfa43f407dd54416b43166bf65455cb;
both publication branches were f0c3f40 and ancestors of this checkout.
Advancing the existing protected-main PR will consolidate Aleutian, Gulf coastal
and Mindanao batches, along with this coverage fix. No force push or direct
protected-main write is required. Existing review PRs retain their history.
Coverage becomes 74 scoped records / 38 current owners; 55 remain unassessed;
63 route candidates / 60 unranked owners; 80 indexed source documents.
The exact-head CI and scientific admission remain distinct gates.

## Subsequent source-index assertion

The resumed runner passed its first 16 checks, then stopped at
`test_rust_index_store_browser.py`: it hard-coded 68 documents, whereas the
registered source corpus now contains 80. The store check now derives expected
addresses independently from the registry, seasonal snapshot manifest and the
two required standalone timelines. It requires exact address sets, no duplicate
registrations/descriptors, exact source bytes and every checksum. The page check
uses that independently checked expected count for both root and /OSW/ URLs.
The runner resumes at this specific failure; earlier passing checks are retained.
