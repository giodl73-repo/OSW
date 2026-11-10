# Regional current length series: admission rules v1

## Evidence class and scope

`regional_plot_series` means that an identified published graphic supports a
reproducible numeric pathlength series over explicitly bounded regional gates.
The measurement quantity is `regional_plotted_length_range`; the range names
the retained graphic, including any analytic curve extrema. It does not name
the range of every underlying observation or physical annual extrema.

Retain current identity, regional gates, variable, units, source study period,
the graphic's time support, exact original custody, source locator, method,
raw factual geometry and every derived reading. Store reading allowances
separately from source-reported physical error and confidence intervals.
Retain the scope of both the published field and the graphical readback.

For a current with no admitted whole-current length or geographic lower bound, the assessment may
advance to this partial evidence class while keeping:

- `whole_current_evidence_status: unmeasured`;
- `published_length_km`, `published_rank` and `lower_bound_km`: null;
- `rank_eligible: false`;
- an explicit series identifier and `regional_plotted_length_range_km`;
- a named range kind and separately typed editorial reading allowances.

Retain any previously supported length result or geographic lower bound with
its own source and method; add a regional series alongside it. Do not replace
that evidence with this class.
Do not add regional pieces to construct a whole-current length unless a
separate declared method establishes connected, comparable spatial/time/layer
support. A graphic's minimum is not a guaranteed physical lower bound.

## Time and graphical records

An underlying daily dataset does not establish the plot's sampling schedule.
Fractional graph years, imprecise dates and line/cubic graphic knots are not
exact observation timestamps. Do not add them to observed-date capabilities.
Do not infer missing source samples or year-specific calendar-month extrema.
Seasonal aggregation/playback needs verified temporal support and a separately
qualified measurement rule; an axis-reading allowance of0.1year does not
establish a calendar month.

Keep original graphic knot records distinct from interpolated graphic readings,
cubic control points and observations. Count shared endpoint instances
explicitly. Preserve every selected command, reading and run break. Retain
small source-coordinate overlaps only under a declared graphics tolerance,
report them, and do not repair the source by moving/averaging/dropping points.
Use a stable reading ordinal for pagination rather than inventing exact time.

PDF coordinates are not longitude/latitude. A scalar length chart does not
recover geographic route geometry or physical cross-current width. A mapped
current card may link this evidence without changing its route's evidence class.

## Prospective source inspection and calculation

Before calculating target km/time readings, inspect the complete relevant
source graphic and its operator types, transforms, clipping, stroke widths,
run topology, axis labels and calibration support. Pin these source-feasibility
facts. Declare tolerances, reading allowances and their dimensional
justification, point retention, failure conditions and scope. Freeze the
producer, protocol, synthetic tests and preflight in Git before calculation.

Retain failures. If a frozen selector cannot represent the source, make the
technical correction explicit in a new version and preserve prior methods,
declarations and diagnostics. Do not tune a method to a desired length/rank.
Never edit a frozen scientific producer or product after actual calculation.
Default scientific replay must work offline from retained factual inputs;
exact-original replay is a separate, explicitly invoked custody check.

## Atlas delivery

Expose the complete header/provenance and every reading through the query
engine, plus the scoped measurement/claim, source records and current
assessment. Bind those records to the frozen numeric report and dependency
pins. Missing, duplicate, changed, reordered or misowned readings must reject.
Historical-table composition may replace only the exact assessment supported
by that complete validated admission. Every other prior row remains protected.

Provide chart, complete numeric table, provenance and qualified assessment
links on the mapped current card. Verify all pages through native and shipped
WASM, source access, keyboard navigation, phone reflow and textual equivalents.
Validate native records before starting Chromium. Source/catalogue coverage
and fresh scientific replay must cover the delivered head. A regional series
does not close the remaining whole-current/seasonal/width gaps.

The first implementation is the Qiu2023 upstream KE graphic, with frozen v4
method and separately bound query contract. Its individual reading allowances
are source-specific; later currents require their own justified values.
