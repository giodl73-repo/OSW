# Indian SECC band readback and comparison repair

Baseline4709940/run39715841797. The previous goal turn made progress by
publishing longitudinal bands and source-domain comparisons. Its first Linux
reconstruction exposed a reproducibility defect, so repairing that defect
precedes additional axis/width calculations. Same continuing draft PR83.

## Failure and correction

Twenty-four previous reports reconstructed byte exactly. The new band report
did not: geodesic span differences up to3.410605131648481e-13km also changed
eleven raw-float comparisons, incorrectly increasing the domain-difference
count from9 to20. NetCDF passed; offline failed before tests on retained IRD
Rotschi1972 HTTP403. This is a real failed gate, not an overall CI pass.

The new, separately pinned readback protocol applies six decimal kilometres
only to newly calculated geodesic spans and bracket distances. Original
historical stored numbers and source vectors remain unchanged. Version2 now
compares boundary coordinates/status exactly, reports span-readback agreement
separately, and counts recovered northern crossings from changed edge support.
Rounding cannot create a domain extension or hide a changed boundary/status.

## Verified impact

- Fifteen focused tests pass, including tiny arithmetic drift, real distance
  changes, changed boundary/status, original bracket preservation, independent
  native-cell flood fill and all nine actual northern domain extensions.
- Reviewed13,534 derived distance leaves;13,439 change readback. Maximum
  rounding displacement4.999648126613465e-7km, under0.5mm. This is numerical
  readback, not source resolution, physical error or a confidence interval.
- All2,187 bands, topology, source brackets and peak metadata remain exact.
  All72 historical compact values and the original historical report remain
  exact; twelve monthly summaries change only distance readback.63 boundary/
  status comparisons agree and nine northern crossings remain recovered.
- All24 earlier reports and24 producers remain byte exact. All59,828 main
  typed rows remain exact except the SECC object fingerprint; links,
  capabilities and observation-date evidence are unchanged.426 previous
  indexed originals are exact; only the corrected report/figure manifest
  change, with428 total original-file hashes verifying.
- Final figures are byte-identical to the already visually inspected SVG/PNG.
  The corrected source binding is regenerated; no map geometry changes.
- Dashboard/index/packet/native atlas/WASM builds and109 Rust tests pass.
  Packet139,751,143 bytes/nine verified parts; WASM49,476,495 bytes. Source
  corpus311,336,274 original bytes/47,225,371 compressed bytes.

Actual Chrome passes all12 monthly graphs,12 summary rows and72 comparisons
exactly against native queries, plus keyboard card/figure navigation,320px
reflow and zero automatic original requests. All396 staged engine dependency
hashes match. Fresh Linux reconstruction is pending. The repair must
not be called cross-platform verified until the new Linux reconstruction
actually passes. The separate complete-suite IRD403/local4GiB disk guard stays
open. Retire only verified superseded generated parts; source originals stay.

## Continuing measurement work

The local candidate-axis/normal-section protocol was declared before any such
calculation. No new normal measurements have been produced in this repair.
It specifies local velocity normals, five flow-following stations, explicit
flat/tied/unsupported failures and separate threshold/step/seed sensitivities.
Proceed after the corrected band report passes Linux reconstruction. The
101-name catalogue,12 ranked/89 unranked lengths and158 scoped widths/83 owners
with18 uncovered owners remain unchanged; the full goal remains incomplete.
