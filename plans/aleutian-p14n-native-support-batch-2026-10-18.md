# Native P14N support batch

Baseline `9092076b12ba488e094a29f75d15efa6e73e3f52`; same branch and draft PR83.
This batch fills missing native quality, ship-motion and station-event context
needed to evaluate the earlier exploratory component spans.

## Source and declared extraction

Two original JASADCP NetCDF products total 59,505,868 bytes, each with 11,455 time
records and 120 depth cells for the entire cruise. Acquisition and header audit
precede inspection of native velocity arrays; the field protocol then fixes
regional selection, masks, layer support, all three speed cutoffs and event
overlap semantics. Earlier hourly fields were known, so no blinded
preregistration is claimed. Exact producers, declarations, originals and
derived data retain hashes. Source acquisition/header-only flags describe
those earlier operators; the separate field audit explicitly records that
native arrays have now been inspected.

The regional selection is unchanged:40–48N,178–180E,7–18July1993. Longitude
is normalized only for selection; original unwrapped source longitude remains
available. All selected nominal ensembles are300seconds, with UTC times and
GPS positions at ensemble end. Their source end-time steps range298–5100s;
there is no invented exact five-minute grid. Depth centres are nominal metres
without sound-speed-profile correction, retained as a time-by-cell variable.

## Actual support

| Quantity | Result |
|---|---:|
| Regional native profiles | 1,585 |
| Native depth-cell positions | 190,200 |
| Joint finite, unflagged u/v cells | 182,081 |
| Supported100–300m means | 1,582 |
| Source flag0 / flag1 cells | 182,388 /7,812 |
| Profiles overlapping nominal CTD BE–EN events | 685 |
| ≥2m/s profiles overlapping those events | 0 |

Three profiles lack the required160m joint layer support; their means remain
null. CODAS bits1/2/4 mean bad-bin/bad-percent-good/below-bottom and are not
WOCE CTD quality numbers. The short product has already masked flagged
velocities; short/long flag arrays agree in the selected reach. Raw cells and all original masks
remain recoverable from unchanged source NetCDF, without duplicating every
native cell in the UI packet.

Short-product ocean velocities correspond to long relative-water velocities
plus long absolute ship motion within the declared1e-5m/s representation
tolerance over182,081joint unflagged cells; maximum component differences
are2.98e-8m/s. This checks frame representation, not instrument accuracy.
Ship motion is not added to short-product ocean velocities a second time.

## Motion and contiguous-run sensitivity

| Fixed ship-speed cutoff | Eligible profiles | Retained runs |
|---|---:|---:|
| ≥1m/s | 623 | 42 |
| ≥2m/s | 568 | 19 |
| ≥3m/s | 532 | 19 |

Every run is retained, including short runs. Source-index discontinuities,
unsupported layers, invalid durations, ineligible observations and end-time
gaps>7.5minutes break runs. No latitude sorting, station-gap bridging or new
OSW temporal ocean-velocity averaging is applied. Run distance/duration
describe sampling, not current dimensions. Agreement with nominal CTD events
does not prove ship activity, depth-specific simultaneity or wire interference.
GPS uncertainty can affect both speed eligibility and current velocity.

## Presentation and next scientific decision

The existing Aleutian research panel gains a native vector/ship-motion view,
actual time/latitude, ship-speed and u/v plots, and numeric source queries for
all selected profiles, all three run scenarios, nominal event intervals,
frame correspondence, original metadata and acquisition/figure provenance.
Provider processing remains explicit; OSW does not claim unprocessed samples.

All155earlier scoped widths, all earlier scientific reports/figures, four
other research scenes,42other diagnostics and seasonal route frames remain
unchanged. The primary component-span report stays unchanged. This batch
does not admit a width, physical edge, annual range or mapped ribbon.

Next: declare time averaging and spatial/transverse support for the recovered
underway runs, retaining uncertainty, station-time gaps and branch/eddy
attribution. Do not fit a preferred cutoff or broaden the original branch
windows after viewing the new results. The source paper's five-minute GPS
uncertainty is not a native-profile or width confidence interval.

## Gate continuity

The baseline's first fresh-checkout full attempt was intentionally stopped
after confirming a missing native CLI prerequisite. A targeted test fails
with FileNotFoundError there and passes with the built root CLI. All60Rust
tests subsequently pass in the same clean baseline checkout; the required
native executable is built before attempt2 starts. No scientific predicate
or case is removed. Observe the exact attempt2 receipt/handle; its result
does not certify this successor batch. Hosted CI still has an independently
inspected Reading paper-host connection failure before tests.

That component-stage attempt subsequently passes **1,703 tests and 1,127
subtests in 2,250.30 seconds**, with clean start/end, at baseline9092076.

## Display and freshness corrections

Visual review found that the ship-speed curve connected an85minute source
gap. Its final generator inserts a break at the same7.5minute source-gap
limit; native vector scatter, underlying measurements and all run results
stay unchanged. The full five-owner/43document/54corruption browser gate
passed before this display-only correction; final focused acceptance checks
the corrected native view across card/seasons/query, its two changed indexed
documents,320px/reduced-motion/keyboard access and three figure-provenance
rebindings. These scopes remain distinct.

An acceptance check also found that research evidence affected source-section
hashes without affecting the tile's main hash. Research evidence content and
source-document hashes now participate in the main fingerprint for allfive
research owners. Four existing owners receive a one-time fingerprint repair
with no scientific-content or capability changes. A counterfactual regression
test changes only native support provenance and proves that subsequent updates
change Aleutian alone, preserving every other entry and all observation dates.
An actual dashboard browser gate verifies the rendering/update path.

Supported native ensemble-end dates now populate the dashboard time ledger:
1993-07-13T07:16:22Z through1993-07-18T20:40:20Z, with latest observation
date1993-07-18. Acquisition/publication dates remain separate. The final
date/provenance regression passes, including the explicit1993source date.

The broad dashboard gate's DevTools100MiB fixture-transfer failure is fixed
by serving the same full packet over HTTP. Both existing callers preserve
their assertions and pass. Final focused native acceptance also passes after
the plot/date/freshness corrections. A clean successor combined suite remains
required; the earlier component-stage pass does not certify this batch.
