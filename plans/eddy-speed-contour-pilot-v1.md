# Source-centered speed-contour pilot

The fixed 0.15/0.17/0.19 m Gulf-demeaned contour method finds no eligible
loop on the 24 March 1997 Deviant source date. A separately declared local
level scan finds a nested family near the reported SST center. This explains
why the fixed levels can miss a feature; it does not select an eddy boundary.
Keep both results and the size gap. Do not pool the scanned contour sizes.

The next pilot should estimate a speed contour: the closed SSH contour on
which mean geostrophic speed around the contour is greatest. Its area gives
a speed-based equivalent radius, distinct from an outer/effective radius,
principal width, SST extent or coherent material boundary. This definition
is used in the primary literature and documented by py-eddy-tracker:

- Gaube et al. (2015), Satellite Observations of Mesoscale Eddy-Induced Ekman
  Pumping, https://doi.org/10.1175/JPO-D-14-0032.1.
- py-eddy-tracker storage definitions, including speed radius, speed contour
  and maximum circum-averaged speed:
  https://py-eddy-tracker.readthedocs.io/en/stable/python_module/01_general_things/pet_storage.html.
- AVISO META product definitions:
  https://www.aviso.altimetry.fr/en/data/products/value-added-products/global-mesoscale-eddy-trajectory-product.html.

Implement this in a new module. Preserve the frozen contour geometry
operator, fixed-level pilot and historical reports byte-for-byte. Do not
claim the new implementation reproduces py-eddy-tracker or an AVISO atlas.

The implementation contract must specify before its first numerical run:

1. Native source grid, finite differences in metres, Coriolis/gravity
   constants, latitude dependence and masked derivative handling. No invented
   zero velocities at coastlines. No derivative across a missing neighbor.
2. How one local maximum is selected from the independently dated source
   location; explicit search distance, plateaus, ties and competing maxima.
   Search tolerance is an OSW association rule, not source position accuracy.
3. A closed-contour level sweep relative to that maximum, a fixed step and
   a finer-step convergence check. Reject a maximum at a sweep endpoint;
   extend only through a documented new diagnostic, not silent tuning.
4. Exact closure and valid-interior rules, handling of multiple enclosed
   maxima, a declared minimum sampled support and no repaired gaps. Grid
   spacing and sampled support do not establish effective ocean resolution.
5. Interpolation of speed at contour-segment midpoints, finite sample checks
   and perimeter-weighted averaging. Keep speed magnitude versus signed
   tangential velocity explicit. A local current maximum is a different
   quantity from maximum circum-averaged speed.
6. Preserve the selected contour area, equivalent radius, separate bounding
   spans, mean speed and their operators. No conversion of a speed-core
   radius into a full outer diameter. No annual envelope from one date.
7. Subtracting a constant ADT offset must not change gradients or a
   peak-relative contour family. Arithmetic versus cosine demeaning is an
   invariance check here, not two independent uncertainty scenarios.

Required validation: analytic Gaussian height mound with known maximum-speed
radius and speed; constant-height-offset invariance; refinement convergence;
open/domain-clipped contours; missing derivative samples; competing peaks;
plateaus/ties; insufficient sampled support; and sweep-end censoring. Run
tests and real fields sequentially in the cloud on one low-priority CPU.

Deviant is a development case already inspected. Do not describe it as an
independent or held-out validation. A second independently located named
case is needed to assess behavior beyond this example. Existing published
radii with different definitions are context, not calibration targets.

Admission requires reviewing the resulting source-case association and
method diagnostics. A successful numeric run does not itself establish
physical registry identity, a physical footprint, state containment,
release rights or seasonal playback. Retain ambiguous or unresolved cases
as gaps; record why so the next pass does not repeat the same failed gate.

Raw ocean fields stay cloud-only and are deleted after each job. Retain
only bounded diagnostic JSON and review images locally. Do not install or
merge runtime changes as part of this pilot.
