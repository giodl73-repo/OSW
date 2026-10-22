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

- Seventeen focused offline tests pass, including exact original-source reconstruction
  of NPZ, lossless JSON and quality outputs with network access forbidden.
- A Windows ZIP fixture initially expected the wrong rejection message after
  separator normalization; it now accepts either valid rejection stage.
- All 82 responses validated after six timeout retries; 363 daily fields contain
  6,851,625 paired native vector positions. Original responses/receipts occupy
  a 22,715,226-byte retained ZIP. Twelve monthly means contain 226,500 paired
  native vectors, with full Float64 JSON/NPZ agreement and explicit date gaps.
- All 144 declared candidate tests calculated. Two individual attempts (the
  same May primary seed at 5/10km sampling) pass five-station axis checks.
  One seed therefore passes both steps, compared with zero in OSCAR. Zero
  pass the stronger all-station edge/resolution/hemisphere gate: two upstream
  sections encounter the equatorial source limit without resolving their
  northern half-peak edges. This discrete result does not rule out a crossing
  in the last unsampled boundary interval. Do not turn it into a current width
  or assume a larger viewport establishes a south-of-equator edge. Product
  differences remain.
- All twelve monthly maps render. Actual Chrome passes exact image checksums,
  keyboard selection, 320px reflow, local links and zero automatic original
  downloads. Visual inspection found/fixed an overlapping arrow legend,
  widened the phone image and added a full-size map link. The repaired view
  and all standalone browser checks pass. A separate real Chrome gate passes
  exact native/WASM readback of all 144 attempts, twelve monthly outcomes,
  72 step comparisons and complete native-grid frames for January, August
  and December. Keyboard current-card-to-map navigation and 320px reflow
  pass, with zero automatic original downloads.
- All previously published lengths, widths, routes, data packets, WASM and
  source descriptors are unchanged. Existing counts remain 13 ranked lengths,
  89 unranked lengths and 170 scoped widths across 85 of 102 current owners.
- Current native/WASM builds, 132 Rust tests and complete native atlas
  ingestion pass. All 480 engine pins verify. The main packet remains nine
  parts, 140,086,818 bytes; WASM is 56,105,321 bytes. The separate source index
  contains 458 documents, 338,514,172 original bytes and 53,512,094 compressed
  bytes. All 450 preceding source descriptors, 32 prior reports/producers,
  170 width rows, 78 reference rows and every object geometry remain exact.
  Only the Indian SECC object changes, adding source-evidence navigation.
  All807 unique staged source/engine blobs verify against479 engine pins
  and458 lossless source descriptors. The initial staged-byte check caught
  the repository-wide PNG ignore rule; all twelve required generated maps
  were then explicitly staged and the complete check passed.
- Fresh Linux scientific reproduction now includes this 33rd report and a
  separate reconstruction of monthly products from retained originals. That
  remote gate is pending publication/execution. The full 137-check browser
  matrix/default local suite are unrun under the existing 4GiB guard. Prior
  Linux offline failure at the Rotschi primary-PDF HTTP403 remains separate;
  no new overall green gate or external scientific approval is claimed.

Next: publish this verified source/query/view batch in the same PR, collect the
fresh Linux scientific/source reconstruction gates, then continue the remaining
current measurement gaps. The May boundary failure warrants an explicit source
edge audit before any expanded-domain experiment, not an automatic width claim.
Keep scalar width, axis, annual ranges, state joins and seasonal playback closed
until their distinct evidence requirements are met.

## Cross-platform serialization repair

The6ade3c4 Linux job119777987969 passed all33 report-byte rebuilds but failed
original-response reconstruction at quality.json. Read-only diagnostic
commit9e537b9/job119781185013 proved all seven decoded arrays, every NPY
member and the full native-grid JSON exact; only deflated NPZ bytes and its
quality-record size/hash differed. Linuxzlib1.3 and Windowszlib-ng1.3.1
produce2,000,063 versus2,025,722-byte containers for identical member bytes.

The new array-serialization protocol uses fixed ZIP_STORED/NPY1.0 metadata.
Canonical NPZ is4,080,818 bytes, SHAdcd18afbc1b25ab4a0ca4fd5f09bf9d6c45126949b0289a3921758f21869a5af.
Independent Python3.13 and3.14 local writers reproduce those complete bytes.
All source arrays/NPY members, provider-response ZIP, selection, full-field
JSON and all144case/72comparison/12monthly scientific values remain exact.
Only the report source-quality binding changes. Seventeen focused tests pass.
Fresh canonical Linux and refreshed native/WASM provenance gates remain
pending while regenerated assets are built. The byte-exact gate is retained.

The first canonical engine build stopped at MSVCLNK1201 with243MB free.
After the consumer was terminal, nine superseded hash/length-checked packet
parts and four explicitly selected rebuildable compiler artifacts were
retired; no provider originals were removed. The engine then passes132Rust
tests, native/WASM builds and full native ingestion with one build job. The
consumer now defaults to one job and a512MiB disk preflight, retaining every
test gate. Canonical actual-Chrome source-query/browser verification passes:144cases,
12monthly outcomes,72comparisons, three complete native frames and keyboard
320px current-card-to-map navigation, with zero automatic originals.

## Fresh Linux receipt: canonical source commit c2318a3

Run39769117064, scientific job119791896565 SUCCESS:
https://github.com/giodl73-repo/OSW/actions/runs/39769117064/job/119791896565
All33 reports rebuild byte exactly. Read-only source inspection and strict
original-response reconstruction both PASS: all7array/NPY member bytes,
quality.json, monthly-fields.json and the complete4,080,818-byte stored NPZ
match the retained Windows artifacts. Canonical NPZ SHAdcd18afbc1b25ab4a0ca4fd5f09bf9d6c45126949b0289a3921758f21869a5af
is identical on LinuxPython3.13.16/NumPy2.4.1/zlib1.3 and WindowsPython3.14.7.
There are173verified archive members,82velocity responses and0network
requests during reconstruction. The portability failure is resolved without
changing a scientific value or weakening the byte-exact gate.

NetCDF job119791897217 SUCCESS. Offline job119791897073 FAILS before tests
at Stramma1992 primary/institutional PDF HTTP403:
https://oceanrep.geomar.de/id/eprint/32119/1/1520-0485%281992%29022_0421_tsioc_2.0.co%3B2.pdf
The verified institutional URL spelling also fails. Earlier source6ade3c4
failed later at the separately logged Rotschi1972 IRD PDF HTTP403; do not
report that historical failure as the first blocker in this current run.
The full default suite/137-browser matrix remain unverified on this head.
This receipt changes only batch/review prose; the data/code test source is
c2318a3991bba0aaa54fe3470126c37691222c5c. The full gap-filling goal remains open.
