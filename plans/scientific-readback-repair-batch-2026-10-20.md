# Scientific reconstruction consistency repair

Baseline3a49c092588bc7a081a1292cf266845a3ffd3ba6. Same branch
codex/current-measurement-gaps and continuing draftPR83. No main merge.

## Implemented policy

The original read-only Linux probe identified only small numerical readback
differences and one Windows dependency-key separator. Counts and outcomes
agreed. The field-group probe further located the changed fields; it did not
establish a source-data error or physical uncertainty interval.

[Readback protocol](scientific-calculation-readback-protocol-v1.md) and
`analysis/scientific_readback.py` now define explicit per-schema pointer
whitelists for derived geometry/interpolation fields. Distances use1mm
readbacks, bearings1e−6degree, calculated midpoint coordinates1e−8degree,
interpolated vectors/speeds1e−8m/s and calculated weights/ratios1e−8. These are
serialization increments. Public current estimates retain their prior rounding.

The producer computes support, thresholds and outcomes at its original
precision, then normalizes only declared readback fields. Original velocities,
corner arrays, coordinates, masks, QC, clocks and indices remain untouched.
Unlisted values remain exact; unknown schemas and invalid selected values fail.
Reports pin the protocol and implementation. Source/retained/rebuilt byte and
checksum checks remain strict; no blanket tolerance or skipped assertion.

The NorKyst pilot producer now writes the actual dependency key with POSIX
separators. Its JSON and derived NPZ distance coordinate use the same1mm
calculation readback. Every original hourly field/filter result remains exact.

## Dependency rebuild

Rebuilt observed/hydrography/component/native/underway/composite Aleutian
reports; NECC inventory/paired evidence; NorKyst pilot, twelve monthly assets
and annual/regional reports; and all Loop contour cases. Corresponding figures,
provenance records, shared research registry, dashboard, query/index and native/
WASM engine are regenerated. Rebinding uses each explicit dependency key in
producer dictionaries and the actual regenerated file hash. An intermediate
pin mismatch was caught during the second build and resolved by keyed updates;
no source was changed to match a desired checksum.

Shared evidence notes distinguish calculation precision from observational
uncertainty and annual ranges. No new width, current length, rank, route,
seasonal geometry or physical state intersection is admitted by this repair.

## Verification

- Four new precision tests preserve original floats/signed zero and native
  corner vectors, reject unknown schemas/invalid derived values and protect
  the protocol pin. Existing corruption checks remain; two new browser cases
  reject changed readback implementation/protocol bindings.
- Focused source suite:85tests/115subtests PASS219.41s; one existing NumPy
  binary-size warning. All79Rust tests, locked native/WASM builds and actual
  native atlas loading pass.
- Source preservation compares report payloads after only the declared
  readbacks and provenance rebinding. Original-source files stay unchanged.
  All124NPZ arrays agree exactly except the explicitly rounded distance
  coordinate. Counts, outcomes and public rounded values remain unchanged.
- Independent geodesic checks retain all54Loop cases. Stored-piece summation
  uses the mathematically required N×0.5mm bound; original route-vertex
  geodesic calculations remain independent. Reconstructed interpolated vectors
  must satisfy the four weight-readback plus velocity-readback error bound.
- Index378documents:274,397,320original /43,342,970compressed bytes. Registry
  remains52documents/6scenes. Main packet90,251,097bytes; WASM16,853,132bytes.

Actual browser and independent Linux byte reconstruction are required gates;
their running/terminal evidence is recorded separately from focused passes.
The read-only Linux job now also rebuilds hydrography/component/underway/run
reports, using pinned GSW as well as the original reconstruction packages.

Independent Linux run39517382843/job118952707192 at ca35472 PASSED:all nine
targeted reports rebuild byte-for-byte, matching the Windows reconstruction.
The general browser check caught an older fallback that treated the newly
added Loop scene as NECC. That test now has an explicit Loop branch, preserves
every NECC assertion and fails on any future unhandled owner. This is a test
coverage repair; the scientific source/atlas artifacts are unchanged by it.

The isolated ece1c14 full suite finished with clean start/end:1843tests and
1164subtests PASS3643.33s, terminal23:45:42UTC20October2026. It predates contour
and readback changes, so its result cannot certify this repair. A clean
successor must cover the final repaired commit. Keep PR83 draft until
its required final gates are satisfied. The wider current-data gaps remain.
