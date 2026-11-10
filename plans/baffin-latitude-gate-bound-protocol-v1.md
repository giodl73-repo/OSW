# Baffin Current described-latitude geographic bound v1

Prospective protocol. Selected source text and original pages have been
reviewed; no actual Baffin gate-distance calculation has been executed for
this proposed measurement. This is not blinded or externally preregistered
research. Existing editorial reference-route estimates are already known.

## Source and geographic support

Fissel, Lemon and Birch (1982), doi:10.14430/arctic2318, abstract on printed
page 180 / PDF page 1 describes summer near-surface Baffin Current observations
from Lady Ann Strait (76 degrees N) to Cape Dyer (67 degrees N), using at-least
wording. The Results opening paragraph on printed page 183 / PDF page 4
explicitly extends the historical name northward beyond eastern Baffin Island.
Retain that author convention rather than implying an invariant modern boundary.

The unchanged institutional original is 2,154,964 bytes, SHA-256
`23347326454aa485a98444d98ccd141fe73bc75bbcf9c6b6943f66e2d4e8e266`.
Only PDF pages 1 and 4 were reviewed for this length question, including rendered
page inspection. Existing width review covered other selected pages. Neither
constitutes full-paper review or raw-field reproduction. The original remains
private and ignored; distribute attributed facts and OSW annotations only.

Summer 1978 and 1979 are study context, not exact paired gate occupations.
Neither a common fixed layer nor a simultaneous connected centerline is
established. The Lancaster Sound excursion, meanders and eddies cannot be
reconstructed from two latitude values. Coastal confinement within 100 km
must not become a current-width measurement.

## Operator and sensitivity

Reuse `analysis/north_atlantic_gate_bound.py` without editing it. Compute the
WGS84 meridional separation of nominal 67 and 76 degrees N on abstract common
longitude zero, which is never a current location. Keep six decimal kilometres
for arithmetic reproduction and round down to a 100 km multiple for a
conditional nominal geographic floor.

Independently shift each gate by -0.5, 0 and +0.5 degrees and retain all nine
scenarios. This repeats the existing North Atlantic and Labrador convention.
It is editorial sensitivity, not source-reported position error, statistical
uncertainty, a confidence interval or seasonal variability. The central floor
need not fall below every scenario. Prose extent does not establish a guaranteed
physical minimum for a single connected current axis.

## Freeze before execution

Create a new Baffin operator and prospective synthetic tests. Test arbitrary
latitude pairs independently of the source-gate pair. Freeze those files,
this protocol, the source review and exact dependency hashes in Git before
the actual 67-to-76-degree calculation. Record the freeze commit and first
execution separately. Do not overwrite prior reports, scientific producers,
tests or source reviews. Corrections require new versions.

Arithmetic verification must independently integrate WGS84 meridional curvature
for the nominal case and all nine scenarios, verify floor rounding and reject
changed source support or dependency hashes. A local original-custody check
must match the exact retained PDF. Do not fetch it again merely for testing.

## Admission and visualization contract

Admit only an unranked regional geographic bound after arithmetic verification.
Retain any illustration-only arrow span, editorial reference route, existing
regional width records and all other current decisions. Whole-current length,
source-reported numeric length, physical endpoint coordinates, annual ranges,
fixed layer and measured uncertainty remain null. Do not increase the number
of qualified published length ranks or infer state intersections.

Provide an accessible scalar SVG with explicit geographic-bound wording,
historical naming scope, summer-study context and the sensitivity caveat.
Expose all scenarios, source custody and method through the Rust/WASM query
interface and link them from the mapped current card. A scalar diagram must
not appear as a measured route or a mapped width band.

Admission requires exact native/WASM row parity, rejection of owner/source/
value/rank transfers and missing or duplicate receipts, narrow-screen rendering,
keyboard access, original-source request checks and preservation of all prior
scientific inputs. Run one heavy cloud stage at a time. Local builds, browser
tests and bulk asset synchronization remain held while disk pressure persists.

## Current stage

Source review, prospective operator and synthetic tests only. No actual Baffin
gate calculation product, admission, new ranking or rendered measurement
figure has been produced at declaration. Finish the running Davidson integration
gate before publishing this next batch to the working branch.

## Commands after the prospective files are committed

Use the recorded exact freeze commit, not a moving branch name:

```text
python analysis/baffin_latitude_gate_bound_v1.py build --freeze-commit <40-character-commit>
python analysis/baffin_latitude_gate_bound_v1.py check --freeze-commit <same-commit>
python analysis/baffin_latitude_gate_bound_v1.py original --original-path research/source-data/fissel-baffin-1982/journal-article.pdf
```

Before that commit, run only the focused synthetic tests and `declare` action.
Keep first-execution time, source commit, interpreter and numerical-library
versions in a separate execution proof. All local commands use one logical CPU,
BelowNormal priority and one numerical worker; arithmetic is small and does
not trigger native builds, browser sessions or full-packet reads.
