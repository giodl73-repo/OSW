# Offshore West Australian source gap: surrounding velocity fields

Same branch `codex/current-measurement-gaps`, same draft PR #83. No new PR or
main merge. This fills the missing surrounding two-dimensional source data
identified by the existing naming/route audit; current dimensions remain open.

## Original source and declared selection

Before acquisition, the protocol fixed OSCAR version2017.0, nominal15m, all
2013 timestamps,28–36S and60–116E on the native one-third-degree grid. This
extends the existing32S section's exact longitude range by four degrees on
each side. It is a source viewport, not a whole-current boundary or endpoints.
Source arrays were not inspected before choosing that extension. The existing
section and earlier diagnostics were already known; this is exploratory work.

NOAA OceanWatch returned304,200vector positions:72times ×25latitudes ×169
longitudes.299,088pairs are finite and5,112positions have both components
missing; no position has only one component missing. Every one of the12,168
central-section vector positions reproduces the earlier finite float64 bits,
signed-zero semantics, masks, coordinates and clocks exactly. The metadata
response also reproduces the earlier provider metadata hash.

The exact original CSV byte count is **28,973,155**. SHA256:
`0f0c8bdb4a4bf33a89c6ffe8646c56a51628493515ecec878b43389cd5f9137a`.
Metadata is8,889bytes. A deterministic7,176,104-byte ZIP retains both original
responses, with member and archive hashes, requested/resolved URLs, HTTP200,
UTC times, exact preflight/collector pins and source attribution. The archived
metadata explicitly permits free use and redistribution, retaining its accuracy
and use disclaimers. No source publication pages or maps are redistributed.

An initial collector interface error treated the old parser's `(attributes,
frames)` result as frames alone. That attempt failed before parsing new vector
values and did not publish an archive. The interface was corrected, and the
successful responses and complete validation are receipted. Retained download
bytes are saved before subsequent validation so a failure cannot silently
replace them with a fresh response.

## Derived data and visual comparison

Twelve monthly source fields retain both mean components and paired counts
at every cell, original source indices/timestamps and the fixed minimum of
five finite pairs. All12months have4,154eligible cells of4,225. They preserve
all source times: January has7, February5, and the other months6 each.
The original time gaps, including four six-day gaps, are not regularized.

The complete central row's monthly finite bits, masks and paired counts also
match the earlier operator. An initial NumPy running sum differed by one ULP
from Python's compensated `sum`; the new operator now uses the existing
Python summation method uniformly for every cell. No central-row-only patch,
source rounding or changed threshold was used. Independent sum validation
uses a forward roundoff bound based on machine epsilon, count and sum of
absolute inputs. That numerical bound is not velocity or width uncertainty.

An independently drawn twelve-panel SVG/PNG shows fixed-scale signed
northward-component colors, east/north vector directions and the existing32S
section. Native-grid display thinning is explicit. Both components, counts
and original clocks remain available in exact source queries. Blank cells
mean insufficient paired support; they are not diagnosed current boundaries.

The dashboard West Australian entry links to the figure and source query.
The map-card evidence disclosure makes existing per-current evidence links
accessible without assigning their source geometry to the route map. Its
keyboard/mobile behavior is checked for both West Australian and EAC entries.
No new current polygon, route, width, state membership or seasonal footprint
is admitted by this source extension.

## Validation and publication status

- Ten source/mean tests pass: exact archive/cross-section reconstruction,
  independent monthly support and summation checks, paired-only missingness,
  and eight altered-header/unit/time/grid/value/mask rejection cases.
- The independent source figure was visually inspected after improving arrow
  legibility and separating the color legend from its caption.
- Both the EAC calendar and West Australian source reports rebuild byte-exact
  locally. The independent Linux reconstruction job now includes these two
  additional producers; its11-target result must be tracked at publication.
- The prior4744a77 remote scientific reconstruction passed all nine preceding
  producers. Its offline job failed before testing, at the existing Stramma1992
  institutional PDF download returning HTTP403. This is not a green full CI
  result and has not been waived or replaced by a different PDF.

- 21 focused tests / 2 subtests PASS in13.39s, including the prior EAC calendar
  data and browser-runner environment checks.79Rust tests and locked native/WASM
  builds pass; actual native atlas loading passes.
- The383-document index has277,690,423original /44,313,546compressed bytes.
  Main packet90,255,288bytes;WASM16,854,812bytes. All380earlier indexed document
  descriptors remain exact.
- The actual browser passes all12complete monthly source fields/counts with
 exact native Rust/browser WASM equality, source export and320px reflow.
 West Australian and EAC map-card evidence links pass keyboard/mobile checks.
 No source originals are automatically requested and no page errors occur.
- Against4744a77, all44other query collections and239other object rows remain
 identical. Old32S source bytes/diagnostics, width inventory and reference
 paths are unchanged:155widths,463samples,76routes,28series.
- All661unique inspected source/build blobs match staged dependency pins,
  including133engine inputs,383indexed documents, the source ZIP and complete
  new EAC/West Australian figure graphs.

The isolated full suite at8399af0 is still running and
predates both this addition and the EAC calendar batch. Preserve its checkout,
native executable and live process; do not restart it on an observation timeout.

## Next measurement work

Declare and evaluate a source-supported offshore corridor/axis method against
the actual vector field, with explicit time/layer support, regional gates,
alternative branches, directional alignment and failed cases. The broad modern
offshore gyre flow, coastally southward Leeuwin, deeper undercurrents and
Andrews1977 cyclonic-stream naming remain distinct. Do not inherit coastal
lengths or identify every northward eddy flank as the West Australian Current.
The source viewport and old peak-search bounds are not physical current edges.

Reproduce with `analysis/acquire_west_australian_oscar_2d.py` (offline by
default), `analysis/build_west_australian_oscar_2d_source.py` and
`analysis/build_west_australian_oscar_2d_source_figure.py`. Source acquisition
is explicit `--acquire` and refuses to overwrite an existing retained archive.
