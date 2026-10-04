# Ocean motion atlas publication boundary

Status: **closed for public dataset promotion**, 2026-09-30.

The local main almanac and object pages use the full research candidate. The
movie-crop directory now reads the rights-screened preview, but its object
links still lead to full candidate pages. The full `release/v0.1.0` directory
and research JSON files are also inside the local static site tree. Serving
that entire tree would expose the working data regardless of which page links
to it.

Run `py analysis/audit_ocean_motion_publication_boundary.py` to refresh the
[machine-readable audit](publication-boundary-audit.json). The 2026-09-30 audit
found 49 static research references, 22 full-candidate references, and 17
used external sources with open reuse decisions. It identifies direct site
routes to Horizon names, NOAA MUNSTER detections, NAVO observations, NOAA LSA
derived paths, and ArcGIS arrow-derived joins. Runtime paths loaded through a
manifest are represented by that manifest and are not individually enumerated
in the static reference count.

`py analysis/audit_ocean_motion_publication_boundary.py --gate` is the
source-use publication gate. It fails while the served full candidate contains
used external sources with pending rights decisions, or while the screened
preview has not been rebuilt against the current source review. This gate
does not approve scientific claims, accessibility, citation metadata, or the
owner's publication decision.

Two routes can close the source-use boundary: resolve and record the terms for
the pending uses, then rebuild and recheck the full package; or build a static
site bundle that contains only the screened collections and compatible pages,
excluding the full candidate and unscreened research JSON from its served
directory. The second route is a partial source-set publication and must say
so wherever counts or search results appear.

An isolated **review bundle** now exists at `site-review/ocean-motion-screened/`.
Build it with `py analysis/build_ocean_motion_screened_site.py`, check its data
and file boundary with `py analysis/check_ocean_motion_screened_site.py`, and
exercise search, map, state passports, and deep links with
`py analysis/test_ocean_motion_screened_site_browser.py`. Serve that directory
alone for review. It contains 217 screened objects and all 70 NASA crop links,
plus the OSW 56-state map ground with its credited public-domain Natural Earth
land. It includes neither the full candidate nor unscreened research files.
Each state passport has a shareable `?state=` address and separate lists for
source-reported local current presence, schematic crossings, editorial
locators, unresolved current crossings, named-eddy locator candidates, and
unresolved named-eddy intersections. These evidence classes do not assert a
whole-current passage or a dated eddy footprint without supporting geometry.
Where the source gives a local current observation, the state passport shows
its date, locality, and citation. A dated eddy-center candidate shows its
date and point-only limit. Each state passport links to its screened JSON
packet for the complete row and claim set.
The length section also lists every screened named current: nine source-reported
ranked estimates, seven OSW geographic floors, one published lower bound, one
proposed system length, and 81 records without an admitted whole-current
number. It orders values only within their evidence class.
It is not an authorized or scientifically approved dataset release.
Each screened object has a downloadable JSON review packet containing its
screened records, claim rows, related-object labels, and source citations.
The packet index and each packet are covered by the preview and site manifests.
