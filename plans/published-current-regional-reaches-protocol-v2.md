# Published regional reaches: prospective protocol v2

## Scope and source

V2 retains the Brazil Current's **initial 1500 km reach** described in
Tomczak and Godfrey, chapter 14, printed p244 / retained PDF page254.
The current begins *near* 10 degrees south in the preceding sentence.
This is a textbook synthesis with no observation window supplied for that
reach. Its source observation campaign and uniform depth layer are unknown.
Adjacent transport values and layer descriptions do not establish either.

The chapter is PDF version1.2, September2002. The original printed edition
is1994; the retained compilation includes chapters revised at different times.
Neither date, nor the directory name containing2005, dates the reach.
PDF page255 supplies continuation and variable separation context; its dates
for particular front illustrations do not date the reach on page254.
Selected pages254 and255 were visually reviewed. The whole401-page compilation
has not undergone a page-by-page completeness review.

Reuse the original and acquisition receipt in
`research/source-data/tomczak-regional-2005/`. Its unchanged PDF is locally
retained and ignored because no redistribution grant has been established.
The source SHA256, bytes, page count, exact short passage, current identity,
version history and approximate upstream latitude must be independently checked.
The existing acquisition helper can recover this same pinned original.

## Quantity and exclusions

- `reported_initial_regional_reach`, `reported_value_km=1500`,
  `relation=source_reported_value`. Preserve the source's round number without
  declaring exact physical equality, adding an approximation sign absent from
  the passage, or turning the value into an inequality.
- Observation window, numerical uncertainty, upstream longitude, downstream
  coordinates and physical length floor remain null. Null is not zero.
- Approximate upstream latitude is context, not a precise geographic gate.
  Do not infer a downstream latitude from distance or add separation locations
  from the next page as measured endpoints of this reach.
- No current axis, coastline integration, segment sum, centreline calculation,
  confidence interval, physical width, seasonal envelope or state intersection.
- Whole-current length remains unmeasured; whole-current ranking is ineligible.
  A reported initial reach is a separate quantity, even if a reader expects
  the full current to be longer. This protocol establishes no physical bound.
- The frozen Algerian v1 method, facts, products, tests and preflight remain
  unchanged. Its strict greater-than constraint has different source semantics.

## Prospective checks and outputs

Freeze this producer, synthetic tests, source facts, protocol and pinned
preflight in Git **before** producing the actual report or SVG. The existing
ignored original is frozen by its checksum and acquisition receipt; do not
add its full contents to Git. Synthetic tests use their own facts, not the
actual report, and must cover invalid numbers, scope promotion, fabricated
dates/endpoints/errors, deep-copy independence and a textual figure alternative.

The report retains the source, selected-review limits, unspecified observation
time, semantic relation and every non-admission flag. The SVG is a schematic
segment with written endpoint limitations; screen positions do not encode
coordinates or recovered flow geometry. It must show dates and uncertainty as
unspecified, and distinguish chapter version from observation support.

First execution and read-only replay must match byte for byte. Preserve failed
attempts; any scientific correction after actual execution requires a new
version. Independently compare the products with the original afterward, and
render the saved SVG before accepting the layout. No Chromium is needed for
this source-stage check. Batch query/card/native/WASM admission and browser
validation with compatible subsequent evidence on the existing draft PR83.
