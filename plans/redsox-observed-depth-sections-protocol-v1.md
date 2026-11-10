# Observed REDSOX vertical depth support at two winter sections

Use ONLY retained NCEI0146147v1.2 original ASCII archives. No new download.
Keep ALL17 winter RSX1 cases: lower Northern Channel7,8,9,10,11 and original
cruise Figure7a Section3 order76,75,74,73,72,71,70,59,60,61,62,63. These are two
dated non-synoptic cross-current sections, not an along-current axis or annual
mean. Prior archive/width calculations and source figures were inspected; this
new depth protocol is exploratory, not blinded. Earlier outputs stay frozen.

Reuse original source parsers, original Section3 WGS84 geometry/component and
existing bounded layer interpolation. LowerNC uses fixed southward minusv;
Section3 uses original right normal to its bent source-order section. No frame
change to improve a result. Preserve source positions, times, references, header
issues, provider associations and raw archive-member hashes. Reject uninterpretable
reference m and unverified rejected-downcast treatment at10/63;61/63 reference m
remain excluded.74 has no CTD companion. Provider station-field consistency is
required, but never relabelled independently verified cast identity or sample
synchronization. No source time shift, header repair, tides or quality correction.

New declared velocity-core window20-200m ABOVE BOTTOM. Require complete frozen
velocity_layer support, at least3 original samples, original20m maximum gap and
positive signed interval mean. Choose greatest native signed component within
that height window, ties to first increasing-depth sample. Only afterwards apply
q>0.2m/s and practicalS>=38 at SAME core. Do not replace a failed saline core by a
weaker or saltier peak. This is a conditional OSW component/salinity diagnostic,
not reproduction of author plume boundaries or independently verified identity.
The existing38/.2 editorial association screen motivates thresholds; the new
20-200m core window is not a measured plume thickness or a modified old window.

Use native LADCP zz metres as the tracing axis. CTD explicit z metres is used
when available, retaining documented source unit-key typo. Otherwise use
-gsw.z_from_p(p,source_latitude), GSW3.6.23, zero optional dynamic-height and
geopotential terms. Native p remains dbar; pressure never becomes metres by
renaming. Require complete increasing hydrography depth coordinates. Salinity
is remapped to each native velocity depth ONLY from its exact CTD point or two
adjacent finite source samples with gap<=5m. No extrapolation or filling missing
brackets. Retain every source index/depth bracket/mapping status.5m is a new
declared sampling guard, not observed error. Do not reuse interpolated widths.

Trace full native q>.2 AND S>=38 support from the unchanged velocity core.
This new saline predicate is analogous to frozen NCC fresh tracing but differs
explicitly in salinity direction, inclusive cutoff and velocity threshold; no
old helper is modified. Stop before missing input or LADCP gap>20m. At adjacent
finite predicate failure calculate separate linear velocity/salinity crossings
and retain whichever is reached first from inside, with both candidate crossings.
Sampling ends remain censored; bed/header or nearest missing observation cannot
close a boundary. Retain joint span only if both crossings resolve, label it
conditional support span, never physical layer thickness. No width/area/volume
join, whole-current depth, annualrange, or confidence interval. Retain every
excluded/unresolved outcome and source-array provenance.

Preflight all17 against existing inventory counts before member decode. Joint
native scalar values<=250000, conservative8bytes/value<=7MB. Bound LADCP<=300
rows and CTD<=2000rows/case; archive member shapes/hashes reproduce. Fixed output
<2.4MB, individual files<2.5MB, publication<3MB. No new scalar reference admission
until separate scientific review. Existing810refs/nativecoveragev14/routeinventory48,
all102eddyrefs, main/runtime/UI stay unchanged.

ALL parsing, pressure conversion, geometry, remapping, selection, tracing and
tests/cloud build sequentially one idleCPU. Local static editing/AST, primary
document/metadata review, hashes and exact artifact retention only. No local
scientific imports/tests or live UI/server/native/WASM work.
