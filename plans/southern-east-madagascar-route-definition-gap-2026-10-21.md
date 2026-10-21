# Southern East Madagascar: route-definition experiment

Continue PR83 from711e22d. Goal remains filling all core data and visualization
gaps, with currents prioritized. This batch investigates the accepted current's
unlocated atlas state; it does not declare that geometry gap closed.

## Source and predeclared experiments

Nauw et al.2008, doi:10.1029/2007JC004639, Introduction2, describes the southern
branch from approximately20S along eastern Madagascar to Cape Sainte Marie
near25deg30minS. Introduction6 leaves downstream alternatives unresolved.
Original publisher HTML was read. No original source figure, bathymetric
section, observed axis or source-file checksum was recovered.

The v1 protocol fixed seven offshore vertices,27 longitude/endpoint sensitivity
scenarios, WGS84 geodesic summation,100km public rounding and an all-or-nothing
coarse atlas land gate. All27 intersect land. Retain the original input and all
failed scenarios; do not silently move a bend or drop failed alternatives.

V2 separately declared eight farther-offshore vertices, keeping all other
conventions. All27 alternatives clear the coarse mask. The nominal polyline
is868.574km, publicly about900km; rounded cartographic sensitivity800–900km.
The source's approximate650km contextual extent remains a separate quantity.
The chosen offshore Cape approach at26.1S is not the source coastal point near
25.5S. The difference218.574km is arithmetic between different definitions,
not a measured source error, current extension, uncertainty or calibration.

## Admission decision and next evidence

Retain v2 as a route-definition diagnostic. No reference route, map feature,
ranked length, current footprint, physical state passage, width, April2001 axis
or annual geometry is admitted. Neither coarse land clearance nor proximity
to the source coast establishes a named-current axis. The existing76 reference
routes and650km reported-length rank12 remain unchanged.

The new current-card comparison figure and exact diagnostic query expose all
attempts and their definitions. Original protocols, inputs, rejection records,
output, figures and operator are pinned. Keep the generic reference-route
catalogue's glob free of the unadmitted offshore experiment. Source-query
indexing includes the diagnostic and four input/output/rejection documents.

Next: obtain source-supported coastal/slope gates and dated axes at a declared
layer, reconcile offshore-versus-coastal endpoints, and review against suitable
bathymetry before admitting a route. Source dimensional reports and current
identity remain accepted independently. Other currents' length, width and
annual-variability gaps remain active.

## Validation scope

Focused checks must reproduce all54 retained outcomes, reject failure/success
erasure and changed lengths/scope, verify native/WASM exact-query parity,
preserve other rows/reports and show the linked figure at desktop/320px with
keyboard access. Record actual terminal results below. The last complete local
Python suite remains774e466 (1910 tests/1222 subtests); this batch does not
substitute focused checks for a complete new-head suite or independent CI.

### Executed publication gates

10 Python tests pass, including tiny display-coordinate drift versus material
geometry changes, owner reassignment, omitted cases and scope promotion.
91 Rust tests, native/WASM builds and native atlas loading pass. The actual
browser returns the exact diagnostic through native and WASM queries, retains
all54 cases, keeps the route catalogue76 and this current unlocated, and passes
keyboard navigation/320px reflow. Desktop and phone figures were visually
reviewed; a full-size figure link supplies zoomable access.

Against711e22d, all50 earlier diagnostic rows,46 other query collections,
all19 scientific reports and the historical release are unchanged. Only this
current's diagnostic link is added. All101 seasonal plans and other seasonal
content match, excluding the expected bundle hash change. The prior bundle is
readable.407 source documents indexed;65-file JS syntax and14 page validation
assignments pass.818 staged dependency blobs pass, including the complete
diagnostic protocol/figure graph; staged whitespace is clean.

Prior711e22d independent scientific job119204581400 and NetCDF fixture job
119204581872 succeeded. Its offline job119204581614 failed before tests when
both Hawaii-hosted Qiu–Chen2010 PDF URLs timed out. New-head CI is separate.
The full current measurement program remains active; the route gap stays open.
