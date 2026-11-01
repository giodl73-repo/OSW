# Current and eddy depth and volume work programme

User request: after the eddy measurement work, project a depth for each current,
allowing depth to change along the current. Combine compatible length, width and
depth estimates into volume estimates, and do the same for eddies. Seasonal
variation and ranges remain part of the measurement programme.

This is the queued work programme, not an executed measurement method. Continue
the active eddy work first. Preserve unresolved eddy gaps rather than treating
coverage of one scalar size reference as complete three-dimensional coverage.
Current depth collection follows that eddy pass; the depth representation and
volume rules must support both feature types.

## Depth representation

For currents, retain upper and lower flow boundaries, vertical thickness, location
along the reference route, section orientation, branch, date/season, source and
boundary definition. Depth below the surface and vertical thickness are different
quantities, especially for subsurface currents. Retain sampled profiles separately
from source-reported summaries and projected profiles.

For individual eddies, retain a dated horizontal boundary and a thickness field
or supported vertical shape. Separate kinematic, thermal, density and coherent
core definitions. A temperature-surface depth or one sampled profile does not by
itself establish whole-eddy thickness. Recurrent regions and families require
individual dated cases before individual eddy volumes can be estimated.

Do not assign one universal velocity, temperature or density threshold to every
feature. Select and document an object-appropriate operator from evidence, then
apply it consistently within each estimate and comparison series. Missing depth
support remains unknown, never zero or the seabed depth by default.

## Volume estimates

Current volume at a stated time is the along-route integral of cross-sectional
area: V(t) = integral A(s,t) ds. Estimate section area from the supported lateral
and vertical shape, then integrate along the route. A single length times width
times depth is a box approximation and must be labeled with its shape assumptions;
it is not the default calculation for a changing current.

Eddy volume at a stated time is the integral of vertical thickness over the chosen
horizontal footprint: V(t) = integral h(x,y,t) dA. A scalar contour area may support
an explicitly modeled proxy only with compatible vertical evidence and declared
shape assumptions. Do not turn illustration spans or a radius of another kind
into a physical footprint or silently assume a cylindrical eddy.

Water volume is reported in cubic kilometres. Transport is a separate velocity
integral through a section, with units of volume per time; Sverdrups are not a
unit of stored water volume. Preserve that distinction in the query schema and UI.

## Uncertainty, compatibility and presentation

Retain spatial, temporal, numerical, source and boundary-definition uncertainty
separately where available. Use explicit lower/central/upper scenarios when the
evidence supports them; do not call an assumed scenario range a confidence
interval. Propagate compatible joint width/depth/route cases rather than presenting
products of unrelated marginal bounds as statistical uncertainty.

Check source case identity, observation period, vertical datum, horizontal
coordinates and boundary definitions before combining dimensions. Preserve
measured, source-reported, model-derived and assumed inputs in the result.
Do not mix noncontemporaneous extrema into an apparently observed volume.

Per-feature volumes may overlap. A global total requires a declared union or
allocation rule for intersecting currents, branches and embedded eddies; summing
all named-feature volumes would double-count shared water. OSW state partitions
must use compatible three-dimensional geometry and a declared allocation rule.

Present route/season depth profiles and dated eddy thickness cases alongside the
volume estimate, assumptions, source links and coverage gaps. Annual minima,
maxima and animations require appropriate time coverage; three snapshots do not
establish a seasonal envelope. Keep physical-volume estimates separate from
explicitly labeled proxy or scenario volumes in queries and rankings.

## Completion evidence

The programme needs source inventory and coverage for every current; versioned
depth operators; compatible horizontal/vertical cases; reproducible volume
integration with units and scenario propagation; dated/seasonal UI views; and
verification of overlap handling before any global aggregate is presented.
No depth or volume values are admitted by this planning document.
