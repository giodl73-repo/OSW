# Southern East Madagascar: a sourced coastal reference for atlas navigation

Baseline191606b; continue the same branch and draft PR83. The full core-data
goal remains active. This batch supplies one missing geographic reference,
its method, state/crop links and visualization. It does not establish the
current's physical axis, full width or annual geometry.

## Source acquisition and the rejected hypothesis

Retain the official Natural Earth1:10 million land5.1.1 original ZIP,3,269,070
bytes, SHA256e547d749445eaa0964aba76738090ec88f5e63c4585122170f98c67a7ea922dc.
The acquisition receipt includes the exact URL, UTC retrieval, package edition,
all seven member checksums, WGS84 PRJ and public-domain terms. Source metadata
distinguishes map scale from metre accuracy. The original archive is retained
unchanged. `python analysis/acquire_natural_earth_land.py --check` is read-only;
network recovery is explicit with `--acquire`, never a build side effect.

The predeclared paired comparison tested all54 existing route scenarios
without moving vertices. All27 first coastal routes contact both land masks;
all27 farther-offshore alternatives clear both. The coarse coast was not the
cause of the first failure. Original experiments and their rejection evidence
remain unchanged, with a linked side-by-side comparison and exact query.

## New construction and measurement meaning

The separate coastal-curve protocol fixed10/25/50km projected offshore offsets,
19.9/20.0/20.1S starting gates and45.2/45.3/45.4E Cape-approach gates before
calculation. It selects the eastern/southeastern contour arc in a declared
local WGS84 AEQD projection, simplifies250m, measures WGS84 geodesic legs and
checks all full/exported curves against finer land at1km maximum densification.
Exported curves are also checked against the original coarse land. All27 pass.

Nominal computational length819.935km; public approximation800km, with a
700–900km outward-rounded convention envelope. Simplification changes a full
contour length by at most0.460km in these cases. These are geometric controls,
not measured offshore core positions, current width, confidence limits or
seasonal excursions. A separate comparison class excludes coast-offset curves
from both published-length rankings and existing waypoint-route ordering.

The source-reported650km contextual branch extent remains rank12. Its169.935km
difference from the new nominal curve reflects different definitions, selected
gates and a coast-offset construction; it is not an inferred source error or
calibration. April2001 near-surface width120km remains independently scoped.
Neither report supplies the undated curve's depth, date or physical boundaries.

## Working data and atlas joins

The versioned working catalogue adds one curve to76 unchanged historical route
rows; it preserves every old ordering field and comparison entry.77 candidates
now serve71 of101 accepted currents.30 currents still lack a reference card;
19 of these are in the remaining-length worklist.28 name proposals remain
pending. This batch adds no name or ranked source measurement.

The working state inventory adds one EAFR geographic relationship, present
in all27 declared conventions.151 candidate/state pairs are navigation, not
physical passage, probability or seasonal occupancy. The highest-zoom complete
NASA geographic context is level2_D_5; no model-current association is inferred.

The global atlas displays this current, opens its mapped card and exact query,
and returns to the selected map. There are100 stored current point locators
and one render-only navigation marker at a curve vertex. This marker creates
no observed point, current core or dated source observation. All101 names are
now mappable. Beck placement follows the existing editorial-route convention.

The current's source links include both Nauw's factual branch description and
the public-domain shoreline. The current source row refines uses/notes only;
the original paper and figures are not redistributed. The dataset's original
ZIP is openly redistributed under Natural Earth's terms. Quantity admission
and identity records retain their original immutable snapshots.

The seasonal page retains one inspectable April2001 width state with playback
disabled and its geographic width bar hidden. The new undated reference is
not an April2001 observed axis. Length rankings12, scoped widths157/83 owners,
raw width samples463 and section cases2853 remain unchanged.

## Verification and remaining work

Synthetic checks cover wrapped contour arcs, geographic gate selection, missing
and coincident gates, strict point contact, source polygon holes, source-byte
mutation,1km densification and independent prior-record preservation. Native
Rust checks bind the complete dependency/catalogue/state/source projections,
reject dimensional or dated-axis promotion and preserve prior bundles.

The independent reconstruction gate now includes these two geographic reports
alongside19 unchanged prior reports. Report its new-head result separately.
Last complete local Python baseline remains774e466:1910 tests/1222 subtests.
No new complete suite is claimed under the current disk guard. The prior
191606b scientific job119214746853 and NetCDF fixture119214746809 passed;
offline job119214746522 failed before tests on the existing Rotschi1972 IRD
paper download with HTTP403.

Required local publication gates: focused numeric/source tests, native/WASM
and native atlas, exact new-current browser flow, existing map/query/dashboard
regressions, desktop/phone visual review, preservation and staged dependency
pins. Record actual terminal results below. No main merge or complete-core-data
claim follows. Continue other current dimensions, uncertainty, temporal support,
routes and scientifically supported state associations.

## Terminal local publication results

- Focused source/numeric/navigation Python checks:25 tests passed.
- Rust:94 tests passed; native/WASM engines and native atlas checks passed.
- Exact new-current flow, six catalogue entrances, full atlas, general query,
  all151 reference/state associations and snapshot browser checks passed.
  Snapshot checks cover105 exact atlas source documents, eighteen rejected
  corruptions, mobile layout and unavailable/optional-data behavior.
- Browser packet fixtures retain every record and assertion, using local HTTP
  rather than injecting the full packet through the browser control channel.
- Desktop/320px reference figures and the paired shoreline comparison were
  rendered and inspected.65 JavaScript files pass syntax checking;14 pages
  have validation assignments. No full14-page browser run is claimed.
- Preservation against191606b passed:42 query collections,19 previous reports,
  all76 historical routes/order,240 other objects, all101 phase plans and four
  historical seasonal source documents exact. Prior bundles remain readable.
- Retained original archive verification passed.903 unique staged dependency
  blobs match their declared SHA256 pins; staged whitespace check passed.

These focused results authorize draft-branch publication. Complete new-head
suite and independent21-report reconstruction remain separate pre-merge gates.
The full current/eddy data goal remains active and incomplete.

Dashboard browser terminal result: PASS for native/WASM parity, four integrity
rejections, keyboard/map selection,241 records, coverage/update lights, refresh,
outage retention and320px reflow.
