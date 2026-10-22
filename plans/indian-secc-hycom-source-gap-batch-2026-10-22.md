# Indian SECC finer-grid source and candidate checks

Baseline: `83e89672d9e5e1df809df35ab2a34edfd268900b`.
Continue branch `codex/current-measurement-gaps` and existing draft PR #83.
No new PR or main merge. This is source preparation for a remaining individual
current width gap; it adds no catalog measurement.

## Why this source

The retained 2013 OSCAR local-normal analysis has zero primary seeds passing
all five axis checks at both profile sampling steps. It requests a finer
source while preserving identity and source-support gates. HYCOM GOFS3.1
GLBv0.08 expt53.X provides Earth east/north velocity at an exact provider 15m
z-level. Model product, forcing, depth interpretation and sampled times differ
from OSCAR; this is not an experiment isolating resolution.

DDS/DAS and the complete coordinate-only response were acquired and checked
before new velocity requests. Original metadata permits public distribution.
The source has 2,884 three-hour coordinates rather than the nominal 2,920.
Exact daily 00Z selection retains 363 dates, explicitly missing August 14 and
December 25. A fixed 75–85E, 12S–equator viewport selects 151 native latitude
and 125 longitude nodes. No synthetic boundary cells or depth substitution.

After one validated six-day response, a 24-day request timed out before
headers. A documented acquisition-only amendment splits regular index runs
into at most six samples and two concurrent requests. Original selection,
original protocol bytes, the failure and successful response remain retained.
The resulting 82 requests preserve exactly the same dates and estimator.

## Rules and execution

Source selection: `plans/indian-secc-hycom-2013-source-protocol-v1.md`.
Candidate test: `plans/indian-secc-hycom-local-normal-protocol-v1.md`.
Both have machine-readable preflight records. Candidate dependencies are
frozen before any new peak or span calculation. All original OSCAR sources,
operators and results remain unchanged.

Explicit acquisition, after placing retained provider DDS/DAS/coordinate
responses and their receipts in a working directory:

```powershell
python analysis/acquire_indian_secc_hycom_2013.py plan --directory WORK
python analysis/acquire_indian_secc_hycom_2013.py acquire --directory WORK
python analysis/package_indian_secc_hycom_2013.py package --directory WORK
python analysis/package_indian_secc_hycom_2013.py reproduce
python analysis/indian_secc_hycom_local_normals.py --directory WORK
python analysis/build_indian_secc_hycom_view.py --directory WORK
python analysis/test_indian_secc_hycom_view_browser.py
```

`WORK` is an explicit source working directory, not a literal argument.
Only `acquire` needs velocity-network access. It retains successful validated
responses and resumes against exact URLs and checksums. Failures remain
recorded; source completeness must be checked before compilation/publication.
Metadata acquisition is a separate prerequisite, not a hidden default test.

Paired valid samples share an identical temporal mask for both components.
Monthly means require at least ceil(80% of calendar days) pairs per cell.
The Float32 packing scale is interpreted as its exact binary value promoted
to Float64. Integer sums use Int64. Unrounded means, counts, native coordinates
and original packed response bytes remain available. These are monthly means
of daily 00Z model samples, not full three-hourly means or observations.

The unchanged local-normal operator retains all 144 seed/offset/step attempts,
five-station axis tests, threshold crossings and failures. A separate stronger
candidate gate also checks both steps, all paired nominal edges, four native
spacings and southern-hemisphere edges. It still does not verify current identity.

## Verification and publication status

- Fourteen focused offline unit tests pass. Syntax compilation passes.
- A Windows ZIP fixture initially expected the wrong rejection message after
  separator normalization; it now accepts either valid rejection stage.
- Source acquisition is in progress. There is no completed retained archive,
  reconstructed source, HYCOM candidate report or rendered monthly view yet.
- The map generator and browser gate are prepared, **not yet executed**.
- All previously published lengths, widths, routes, data packets, WASM and
  source descriptors are unchanged. Existing counts remain 13 ranked lengths,
  89 unranked lengths and 170 scoped widths across 85 of 102 current owners.
- This source foundation does not rerun or supersede the prior Rust/browser
  gates. The prior full Linux offline gate remains blocked by the recorded
  Rotschi primary-PDF HTTP 403; no new overall green gate is claimed.

Next: finish/resume all 82 requests, reconstruct source bytes offline, calculate
all declared cases, inspect the rendered view, then integrate validated evidence
into the existing Rust/WASM query and current-card surfaces in this same PR.
Keep scalar width, axis, annual ranges, state joins and seasonal playback closed
until their distinct evidence requirements are met.
