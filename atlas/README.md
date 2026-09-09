# Atlas 10 depth-ladder preview

**Researcher route:** begin with the concise [research note](../research/), then
use this document for transformations, thresholds, caveats, and rebuild commands.

Atlas 10 extends the native-role-approved Atlas 09 depth preview with a
four-level pressure ladder. All views now share a selectable, zoomable ground
of 56 approximate coast-owned ocean provinces. It separates five top-level views: the conceptual 36-feature
geography, absolute NOAA OISST v2.1 sea surface temperature, NOAA's published
SST anomaly, its time-matched estimated analysis error for 1 August 2026, and
the Scripps RG Argo July 2026 potential-temperature anomaly at selectable 10,
300, 700, and 1000 dbar pressure levels. Its coordinate probe samples each
product on its own nearest display-grid cell and reports the surface fields
plus the four-level anomaly profile. For the OISST surface modes, a paired
latitude-ring comparison exposes analyzed-water continuity north and south at
one requested latitude magnitude. A latitude ladder extends that surface-mask
comparison across 45 paired requests from 0° through 88°, while aligned
polar-cap mirrors show the active surface field in two dimensions.

Each depth layer is explicitly an anomaly relative to the RG 2019 mean and
annual cycle derived from 2004–2018 Argo data. It is not absolute subsurface
temperature or vertically integrated heat content. The source grid ends at
64.5°S and therefore does not reach the Antarctic shelf or ice cavities. The
four levels share one monthly file, baseline, grid, and source checksum, making
their anomaly patterns comparable with each other—but not directly comparable
to OISST's different surface baseline. Slate polar bands mark locations outside
the source domain; beige combines land and
missing cells within it. The anomaly palette is centered on zero and clamped
symmetrically at ±5°C while the text summary retains the sampled source range.

The preview adds geographic reference labels and a three-tick scale, states a
plain-language conclusion before the controls, keeps polar and full-latitude
diagnostics behind an explicit disclosure, separates nearby conceptual
features, and provides a text directory plus a full-size province map for
small screens. It does not change the underlying fields or evidence class.

The shared province ground uses Natural Earth 1:110m public-domain land geometry at
commit `ca96624a56bd078437bca8184e78163e5039ad19`. The coastline source response
has SHA-256
`9e0729ee253ca7d7a5c4ae9395fb1902264c5377c52e224d13dd85010e2835d9`.
Coastlines are geographic reference. The 56 classic identities are placed by
original approximate geographic seeds, then real land is removed so each
coastal province inherits the coast it reaches. Internal borders, areas,
contacts, and point membership are schematic—not published Longhurst geometry.
All fluid features remain schematic geographic shapes, not measured footprints.

The conceptual atlas offers three treatments of the same province ground.
**Ocean states** uses the strongest monochrome borders and labels. **Quiet
states**, the default, reduces their contrast so crossing feature shapes lead.
**Fluid shapes** removes province fills, borders, and codes while retaining a
low-contrast ocean field and ghost coastlines. The toggle
changes emphasis only; it does not change geometry, records, evidence, or
interpretation. Selecting a province by map or dropdown zooms the entire
geographic stack; the URL records that selection, and switching to SST,
anomaly, Argo, or error retains the same view.

## Read the relational map

The conceptual view compares all 36 feature shapes with all 56 ocean states in
a deterministic 2,016-pair matrix. This is **schematic rendered overlap**: the
browser samples both SVG layers in their shared `1600 × 1050` coordinate space
and reports `overlap`, resolution-dependent `near-contact`, or `none`. Catalog
anchors position labels only and can never create a positive relationship.
Selecting either a place or an object reveals the reciprocal list and a CSV
export records the algorithm version, tolerances, input checksums, and all
pairs. These display relationships are not observed membership, transport, or
published Longhurst boundaries.

Feature labels use reviewed names, deterministic displacement, and restrained
leaders; the text directory remains the complete narrow-screen route. Feature
zoom fits the selected rendered shape and stores a `feature=` URL parameter.
Province and feature frames are mutually exclusive, and Return to whole ocean
restores the shared view.

Rebuild the province ground after acquiring the exact Natural Earth response:

```powershell
python analysis/build_province_cartogram.py --land-geojson path/to/ne_110m_land.geojson
```

The older full fluid-geography figure remains a separate annotated design
study. Rebuild it with:

```powershell
python analysis/build_fluid_geography.py `
  --land-geojson path/to/ne_110m_land.geojson `
  --output figures/osw-fluid-geography.svg `
  --interactive-output figures/osw-fluid-geography-interactive.svg `
  --water-first-output figures/osw-fluid-geography-water-first.svg `
  --water-first-interactive-output figures/osw-fluid-geography-water-first-interactive.svg
```

Regenerate the 36 selectable atlas shapes with:

```powershell
python analysis/build_atlas_feature_overlay.py
```

The first twelve preserve and extend the established fluid-geography artwork;
HEATPLATES supplies the shape-first quality precedent. The rest follow the
feature-silhouette contract: water masses have source necks, cores, and
spreading tongues; gyres use asymmetric directional basin loops; fronts use
paired meandering seams; gates use section and passage marks; ridges, trenches,
and plateaus use distinct relief conventions; oxygen-minimum zones use hatched
coastal wedges. Shape, texture, and line construction carry meaning without
depending on color. Stable record numbers remain in the text directory but are
no longer drawn as map symbols.

These forms communicate object type, approximate placement, and geographic
character. They do not communicate an observed boundary, measured extent,
transport section, threshold contour, or water-mass analysis.

The generator extracts the exact `land-outline` path from the committed
interactive province ground and uses it as a negative SVG mask. Every feature
is therefore cut cleanly at the same checksum-receipted Natural Earth
coastline; the overlay does not maintain a second approximate land drawing.
The normal mask adds a fixed 10-SVG-unit offshore visual clearance. Drake
Passage, the Indonesian passages, Gibraltar, and Bab el-Mandeb use an explicit
gate exemption so their schematic sections may meet both banks. Circumpolar
and Pacific-spanning shapes carry matched continuation chevrons at the
antimeridian. That left/right cut is a projection seam, not a physical break.
Masking and clearance change display geometry only—they do not make the
remaining ocean footprint observational or define a physical buffer distance.

Future observed, diagnosed, or modeled feature geometry must enter through
`research/feature-geometry-register.csv`, which is checked offline with
`python analysis/validate_feature_geometry.py`. The contract requires source,
license decision, checksums, CRS, longitude convention, depth/time/baseline,
transform, and review status. The current 36 entries remain draft illustrative
geometry; the admission path is a gate, not an evidence promotion.
The relationship engine and evidence badge describe Earth features only. They
do not transfer province membership or evidentiary status to Jupiter, Saturn,
or any other planetary analogy; that would require a separately reviewed
mechanism-level correspondence contract.

Serve the repository root locally so relative links resolve:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000/atlas/`.

## Export researcher tables

The zone catalog and claims ledger are available as ordinary CSV files under
`research/`. Regenerate them from the Atlas catalog and reviewed claim contract:

```powershell
node analysis/export_research_tables.js
```

The export is deterministic and offline. The zone table is derived from the
interactive catalog; the four-row claims table is deliberately maintained as a
small reviewed contract rather than inferred from page prose.

## Evidence status

Every displayed feature shape in the conceptual view is schematic. A
zone record declares its role, depth, clock, evidence class, source, and
inferential boundary. The surface views are fixed daily analyses and the Argo
view is a fixed monthly objective analysis at one pressure level. None is a
live product or a full-depth heat-content map. The SST anomaly is
relative to NOAA's 1971–2000 climatology; it is not absolute temperature.
The anomaly palette is centered at zero and clamped symmetrically at ±5°C;
the details panel reports the unclamped sampled range.
The error layer is an OISST product field, not forecast error, a confidence
interval, or uncertainty in full-depth heat content.

Observed fields use an equirectangular display centered on 0° longitude, with
the antimeridian at the left/right seam. A non-color table reports mean, range,
and valid-cell count for five latitude bands. Those summaries are not
area-weighted and do not replace local inspection.

## Inspect a location

Click an observed map or enter latitude and longitude in the probe form. The
atlas snaps the request to the nearest two-degree display cell, marks that cell,
and reports absolute SST, referenced anomaly, and estimated analysis error
together. Land and missing values remain explicit.

Probe selections are bookmarkable:

```text
?mode=anomaly&lat=-63.875&lon=-59.875
```

The reported coordinates describe the sampled display cell, not the exact
pointer coordinate or NOAA's full native-resolution grid. All values remain
surface-product fields; the probe does not calculate heat content or transport.

## Compare polar rings

Choose a latitude magnitude to trace the active surface field across every
display longitude at both the northern and southern counterpart. Atlas 05
draws the two sampled rows on the map, renders longitude strips, and reports
valid SST-mask coverage, the number of separated water arcs, the longest
continuous water arc, and field statistics in text.

The default request of 64° snaps to the nearest available display rows:
64.125°N and 63.875°S. On the fixed snapshot, the northern row contains 46
ocean cells in seven arcs and the southern row contains 179 ocean cells in one
cyclic arc. The longest arcs are 28° and 358° of longitude respectively. These
are two-degree display-grid geometry diagnostics, not coast-resolution
estimates. The source mask combines land and missing values, so the atlas does
not assign a cause to every individual gap.

Ring selections are bookmarkable with `ring=64.000`. Analyzed-water continuity can
help explain why circumpolar geometry is possible in the south and interrupted
in the north, but this surface snapshot does not measure the ACC, frontal
barrier strength, heat content, or heat transport.

## Scan the latitude ladder

Atlas 06 plots canonical SST-mask coverage for every even requested latitude
magnitude from the equator through 88°. Northern rows use a solid line;
southern rows use a dashed line. The selected polar-ring request is marked on
the chart, and the complete 45-pair result is available as a semantic table.

For a declared diagnostic threshold of at least 95% analyzed-water coverage
and a longest cyclic water arc of at least 300° longitude, the first southern
scan match is the 48° request (47.875°S) and the first northern match is the 84°
request (84.125°N). The high-latitude northern result reflects the central
Arctic Ocean; the southern curve returns to zero over the Antarctic interior.
This threshold is not a coastline estimate, ACC edge, front, current boundary,
or transport diagnostic.

## Read the polar mirrors

Atlas 07 renders the active SST, anomaly, or estimated-error field from 40° to
each pole with radial azimuthal-equidistant sampling. Both panels intentionally
place 0° longitude at the top and 90°E at the right so corresponding longitudes
align. This reflects the southern cap relative to a conventional globe view;
it is a comparison mirror, not the usual south-polar orientation.

The selected northern and southern sampled rows appear as dashed amber circles
when they lie inside the caps. Latitude circles at 40°, 60°, and 80° and four
longitude spokes provide a common grid. Beige remains land or missing, not a
new categorical land mask.

The mirrors use the same fixed two-degree display values as the world map.
They are not native-resolution coastlines, bathymetry, sea-ice maps, current
vectors, full-depth heat content, or heat transport. The ring table and
latitude ladder remain the quantitative and non-color alternatives.

## Rebuild the observed layers

The committed layer is a 2-degree display sampling of NOAA's native 0.25-degree
final product. Temperatures retain 0.01°C precision; land and missing cells are
preserved. The artifact records its exact query and source-response checksum.

```powershell
python -m pip install -r requirements-observations.txt
python analysis/fetch_oisst_snapshot.py `
  --backend ncss `
  --variable sst `
  --date 2026-08-01 `
  --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output atlas/data/oisst-2026-08-01.js

python analysis/fetch_oisst_snapshot.py `
  --backend ncss `
  --variable anom `
  --date 2026-08-01 `
  --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output atlas/data/oisst-anomaly-2026-08-01.js

python analysis/fetch_oisst_snapshot.py `
  --backend ncss `
  --variable err `
  --date 2026-08-01 `
  --stride 8 `
  --retrieved-at 2026-08-21T14:00:00Z `
  --output atlas/data/oisst-error-2026-08-01.js

foreach ($pressure in 10, 300, 700, 1000) {
  python analysis/fetch_argo_snapshot.py `
    --month 2026-07 `
    --pressure-dbar $pressure `
    --stride 2 `
    --retrieved-at 2026-08-28T19:02:31Z `
    --output "atlas/data/argo-temperature-anomaly-${pressure}dbar-2026-07.js"
}
```

| Layer | Candidate source | What it may show | What it may not establish |
|---|---|---|---|
| surface temperature | NOAA OISST v2.1 | **implemented:** spatially complete daily SST field | full-depth heat content |
| surface anomaly | NOAA OISST v2.1 | **implemented:** departure from 1971–2000 daily climatology | absolute temperature, heat content, or cause |
| estimated analysis error | NOAA OISST v2.1 | **implemented:** spatial variation in time-matched surface analysis uncertainty | forecast error, confidence interval, or full-budget uncertainty |
| subsurface temperature anomaly | Scripps RG Argo Climatology | **implemented:** July 2026 departure at 10, 300, 700, and 1000 dbar relative to the RG seasonal climatology | absolute temperature, vertically integrated heat content, transport, fine-scale pathways, or Antarctic shelf delivery |
| surface current | NASA PO.DAAC OSCAR | mixed-layer velocity estimate | full-depth heat transport |
| dynamically consistent state | ECCO v4r4 | modeled/assimilated budgets and transports | observation-only truth |
| bathymetry and gates | GEBCO grid | geometric constraints and section context | circulation by itself |
| sea ice | NOAA/NSIDC CDR | polar ice concentration | subsurface ocean heat delivery |

Any observational release must name the product version, retrieval date,
temporal aggregation, depth support, baseline, transformation code, and license.
All three committed OISST artifacts conform to
`osw.oisst.snapshot.v2` and retain source-response SHA-256 checksums.
The four committed Argo artifacts conform to
`osw.argo.pressure-anomaly.v1`; each records the July 2026 product URL,
retrieval timestamp, exact pressure selection, 2-degree stride, and shared SHA-256 checksum
`5a19dc77aaccecfd7e6aec34e80e42e1cbd83642c3f08a94d98c7018f631bb5c`.
