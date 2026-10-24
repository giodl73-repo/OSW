# Scientific calculation readback consistency repair

Status: diagnosis established; repair not yet implemented.20October2026.
Same continuing branch and draftPR83. No source originals overwritten and no
scientific test, pin, comparison or CI stage skipped or relaxed.

## Evidence

The ece1c14 Linux run39510524765 reached734unittest tests, failing15tests and
31errors. Earlier provider-acquisition failures no longer describe that run.
The read-only job118939946686 in run39513488424 rebuilt five reports on Linux
with the same pinned scientific package versions used locally. Local Windows
rebuilds reproduce all five retained reports byte-for-byte. Linux comparison:

| Report | Changed numerical leaves | Changed other leaves | Largest absolute readback difference, mixed field units |
|---|---:|---:|---:|
| Observed Aleutian section | 173 | 0 | 3.69e−10 |
| Native Aleutian support | 105 | 0 | 6.02e−12 |
| Loop composite contour paths | 52,202 | 0 | 1.42e−9 |
| NECC paired-vector evidence | 29 | 0 | 2.28e−13 |
| NorKyst continuous pilot | 33 | 1 | 3.70e−13 |

The maxima above combine different field units and are diagnostic sizes,
not physical uncertainties. No integer count or outcome classification differs
in this comparison. The sole nonnumeric discrepancy is a retained NorKyst
input_sha256 key with Windows path separators, versus POSIX on Linux. First
changed numerical fields include geodesic distances/bearings and interpolated
Loop sample values. The exact libm/PROJ/compiler contributions are not yet
isolated; do not attribute every change to BLAS or source corruption.

Probe command: `python analysis/inspect_scientific_reproduction.py`. It computes
without writing source/derived products, prints bounded field differences,
binary-float hexadecimal representations and byte hashes, and fails on any
different rebuilt bytes. The independent CI job avoids paper hydration and
tests the original pinned artifacts. Source hashes and prior failures remain.

## Intended repair

1. Separate exact original data from computed readback precision. Original
   array bits, raw source coordinates, dates, masks, QC, units, source/index
   ordering, categorical outcomes and all source/metadata hashes remain exact.
2. Canonicalize repository-relative paths with POSIX separators at producers.
   Repair the actual NorKyst key; do not merely ignore it in the comparison.
3. Declare field-specific calculation precision before regenerating outputs.
   Candidate readback conventions: derived geodesic distances to1mm, bearings
   to1e−6degree, calculated interpolation locations to1e−8degree, interpolated
   velocities to1e−8m/s and dimensionless weights with explicitly declared
   decimal precision. These choices are proposals pending field-by-field
   review and both-platform reconstruction; they are not physical error bars.
   Keep raw corner velocities/source values unchanged. Preserve exact stored
   path vertices and100km public rounding of the Loop contour experiment.
4. Normalize at the declared calculation/output stage. If midpoint inputs must
   be canonicalized for consistent interpolation, record the operator change
   and demonstrate unchanged support, masks, gateways, counts, outcomes and
   public values. Do not hide changes behind a broad JSON tolerance, ignore
   arbitrary metadata or select a preferred platform as scientific truth.
5. Rebuild the complete affected dependency graph in order: source-derived
   section/support reports, companion calculations and figures, source/method
   bindings, shared research registry, dashboard, query/index and Rust/WASM.
   Record every changed pin and preserve originals. Avoid hand-editing a saved
   result merely to satisfy its current checksum.
6. Preserve meaningful negative/corruption tests. Exact retained-source and
   artifact integrity remains required alongside actual scientific rebuilding.
   Source/index/shape/branch/case counts must stay exact. Public values and
   status differences need explicit investigation, not automatic acceptance.
7. Require Windows and Linux independent byte reconstruction at the declared
   precision, followed by shared UI and native/WASM parity checks. Keep the
   diagnostic job so future platform changes expose their first changed fields.
8. Keep the existing clean ece1c14 full job69176/wrapper2116 running in its
   separate checkout. Do not mutate its checkout/native CLI or restart it on
   observation timeout. After terminal state, a clean successor must cover the
   actual final repair. PR83 remains draft; whole-program completion is open.

This repair is a consistency requirement for the same current-data program.
It does not add current measurements, fill source-reported length fields or
convert conditional contour distances into canonical whole-current lengths.
