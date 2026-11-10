# Speed-contour development contract, version 1

This implements the requirements in `eddy-speed-contour-pilot-v1.md`.
Deviant is an already-inspected development case. Kraken is a transfer
check using its independently documented source-map interior point, not
a blind benchmark or a numerical calibration target.

Use the native daily ADT grid from the pinned DUACS 202411 Gulf subset.
Use a 6,371,000 m spherical Earth, gravitational acceleration 9.80665 m/s²,
Earth rotation 7.292115e-5 rad/s and f = 2 Omega sin(latitude). This pilot
supports northern latitudes strictly between 5 and 75 degrees only.

Compute central finite differences with the actual coordinate spacing:
north distance is R times latitude in radians; east derivatives use R
times longitude in radians divided by cosine(latitude). Set the first and
last grid rows/columns unsupported. A derivative needs its center and
four axial neighbors finite. Calculate u = -g/f times the north gradient
and v = g/f times the east gradient. Never substitute zero at missing data.

Require exactly one strict eight-neighbor height maximum within 150 km of
the independent source point. Reject multiple maxima and local maximum
plateaus/ties; do not break ties by array order or nearest distance. The
150 km search radius is an OSW association tolerance, not a statement of
source position error. An interior map probe is not a measured eddy center.

Sweep downward from that grid maximum by 0.005 m and, separately, 0.0025 m,
to a fixed maximum drop of 0.60 m. Reuse the frozen contour geometry
operator with no area review screen. Accept a contour only if it closes
without clipping/repair, has a finite sampled interior, encloses exactly
the selected strict maximum and no maximum plateau, and has at least 12
sampled interior gridpoints. Twelve is an OSW review-support rule, not an
effective-resolution claim. Missing data or additional enclosed maxima
exclude the contour. A failed detection is not an absent or zero-size eddy.

At each geographic contour-segment midpoint, bilinearly interpolate both
velocity components from four finite corners. Average the magnitude of
that interpolated vector, weighted by each segment's spherical geodesic
length. This is mean speed, not signed tangential velocity, the largest
local speed or a direct ADCP measurement. Reject the whole average when
any required velocity corner is unsupported; do not average only a
convenient subset of segments.

Require at least three supported contours. Select the unique greatest
mean speed; reject if it is the first/last supported contour or ties
another maximum within relative 1e-10 / absolute 1e-12 m/s tolerance.
Thus a censored or support-limited speed maximum is not reported as a core.

The finer sweep is the numerical reference. Require relative differences
no larger than 10% for area and bounding arcs, 5% for equivalent radius and
mean speed. These are declared numerical review gates, not statistical
confidence or physical measurement uncertainty. Preserve both sweeps.
Subtracting a constant ADT offset is an invariance test, not an independent
uncertainty scenario. Do not combine nested contour sizes into an annual
range or pretend the two level steps are independent observations.

Preserve spherical area, planar area-equivalent radius sqrt(area/pi),
separate east-west/north-south bounding arcs, selected level and mean speed.
Do not relabel the speed core as an outer eddy diameter, principal width,
material boundary, whole-lifetime extent or state-containment polygon.
No physical identity or release-rights eligibility follows from a pass.

Cloud gate: seven frozen geometry tests plus the new analytic/negative
controls in `test_eddy_speed_contours_v1.py`; one low-priority CPU; one
download of the immutable source; one daily slice at a time; no native,
WASM, runtime or index processing. Keep bounded diagnostic JSON and images
only; delete the cloud raw source and do not download it locally. A passed
pilot still requires a separate source-case and measurement-admission review.
