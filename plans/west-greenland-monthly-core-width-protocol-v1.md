# West Greenland regional core diagnostic v1: prospective numerical protocol

**Prepared, not frozen or executed on original observations.** Bind the future
operator, tests, this protocol, source reviews, dependencies and workflow in a
committed preflight before any original dimension calculation. Corrections
after original execution require a new version.

## Target

An OSW regional upper-slope velocity-core **transverse section projection**,
linked to the West Greenland Current, at a declared 50–100 m physical layer.
This is not a published measurement, full-current width, coastal-current width,
axis-normal width, occupied polygon or scientific approval. The LS4/LS5 peak
anchors follow the visually reviewed mean-core identity; they are tested anew
in each monthly profile. The source does not bracket the full coastal current.

## Fixed choices made before original results

| Component | Rule |
|---|---|
| Inputs | Only the eight ADCP instruments; supplied moving DEPTH and paired UCUR/VCUR. No nominal-depth point meters are inserted into the layer. |
| Flow reference | 318.1° true, fixed from the reviewed source reference. Along = east·sin(bearing) + north·cos(bearing). Positive transverse points left/offshore, toward 228.1° true. |
| Time | Round decoded days-since-1950 to nearest UTC hour only within 2 seconds; retain signed offsets. Reject duplicate/reversed aligned hours. Expand gaps to explicit missing hourly slots. |
| Layer | Trapezoidal average of piecewise-linearly interpolated east/north velocity from 50 to 100 m. Require available paired components and supplied depth at both bracketing levels. No vertical extrapolation. |
| Vertical gaps | At least three usable source depth cells, strictly distinct supplied depths, with no gap over 30 m between brackets through the layer. Preserve rejection reason per profile. |
| Filter | SciPy 1.17.1, `butter(2, 1/36, fs=1, output='sos')` and forward/backward `sosfiltfilt`, odd padding of 108 hours. Filter each contiguous available segment separately. |
| Filter support | Segment must contain at least 240 hours. Trim 108 hours from each end; retain no samples across gaps. The 36-hour critical period is the single-pass −3 dB point; forward/backward gain is squared. This is OSW filtering, not reproduced harmonic detiding. |
| Monthly synchronization | All eight station means use the exact same hours with available filtered layer velocities. No station is averaged over a different subset. |
| Monthly eligibility | Full calendar month in the grid; at least 70% of its UTC hours available jointly, at least 15 distinct days, and no unsupported run over 168 hours. Report partial and failed months without widths. |
| Core | Unique positive monthly peak at LS4 or LS5 and at least 0.10 m/s. This floor is a prospective diagnostic choice, not a source uncertainty estimate. |
| Span | Find the connected threshold component containing that peak. Nominal fraction 0.5; sensitivity fractions 0.4 and 0.6, all retained. |
| Edges | Both threshold brackets must lie within the observed section. Linearly interpolate only between adjacent complete station means. An exact threshold station also requires a farther observed station strictly below threshold: a plateau, touch without exit, or exact threshold at the section endpoint is censored. Never fill a missing station or double a one-sided span. |
| Multiple cores | Reject a second local maximum, including a flat maximum, above the threshold outside LS4/LS5 within the connected component. Preserve an explicit merged-core outcome. |

Every number in this table is a source reference or an explicit OSW method
choice. The numerical choices are not universal current-measurement standards.

## Geography and outputs needed in the future operator

Verify the original archive, all eight member hashes, exact headers and first
custody before reading arrays. Read actual surveyed coordinates, check station
consistency and preserve source datum/uncertainty. Use WGS84 inverse distances
and azimuths relative to LS4; project onto the declared transverse reference.
Require station order LS1 through LS8 to increase offshore; retain the along
reference offsets so the section's orientation limitations remain visible.
Record both edge bracket identities/coordinates and their separation; do not
turn the interpolated endpoints into accepted current geometry.

Preserve all 26 calendar months, including partial boundary months, per-station
profile/layer/filter losses, synchronized hours, monthly conditional means and
all threshold outcomes. Keep raw computation precision distinct from any later
display rounding. Plot support and censoring alongside computed spans.

No annual instantaneous-width range follows. Any later min/max of monthly
mean regional spans must retain that exact meaning and complete-year coverage.
Threshold sensitivity is not measurement error or a confidence interval.
Blowdown can make missingness depend on flow strength; accepted conditional
means do not become an unbiased seasonal climatology through a coverage rule.

## Execution and admission gates

The numerical module has no source reader or network access. Test synthetic
analytic layer profiles, rotation signs, timestamp offsets, missing segments,
monthly denominators, paired edges, censoring, ties and merged cores first.
The original-data operator and serialized cloud workflow remain to be written,
reviewed and frozen with exact dependency hashes. No original calculation is
authorized by this prepared file alone. No query packet or current dimensions
are admitted until actual source traces and diagnostic figures are reviewed.
