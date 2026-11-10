# Loop Current composite contour measurements and atlas delivery

Baseline ece1c14a0b3a7fce7a365164dc0034ccdab1e2b7. Same continuing draftPR83
and branch codex/current-measurement-gaps; no new PR or main merge.

## Measurement result

The previously recovered original author surface composites now support a
declared, reproducible geometric measurement. All54predeclared combinations
of phase, ADT level and regional gateway shifts produce a single supported
open contour arc. Eighteen clipped closed-ring components remain rejected.
They are not appended, assigned new eddy identities or counted as route length.

| Conditional source configuration | Nominal0.55m arc, calculation readback | Public approximate path | All27sensitivity cases, calculation min/max |
|---|---:|---:|---:|
| Positive composite | 1,379.7km | 1,400km | 1,324.1–1,439.0km |
| Negative composite | 629.2km | 600km | 582.6–676.4km |

These are distances along absolute ADT contours between explicit editorial
gateways in conditional mean fields. They are not mean daily path lengths,
ranked whole-current lengths, annual extrema, confidence intervals, physical
widths or occupied-current polygons. Composites are not seasons or forecasts.
The experiment envelope does not establish all possible flow configurations.
The source pointwise coordinate means remain incomplete and are never joined.

## Declared rules and retained evidence

The protocol was written after source/speed-map inspection and before tracing
contours or calculating distances. This is exploratory, not blinded. The author
plots0.55m absolute ADT; OSW adds fixed0.50/0.60m sensitivity levels. Independent
±0.125degree shifts of each regional gateway produce27cases per phase. The
nominal gates match the older OSW Loop experiments, whose physical endpoint
and bathymetric interpretation remain unresolved. No post-result gate tuning.

Native missing-ADT quadrilaterals are excluded with contourpy serial,
corner_mask=False. Every clipped part remains recorded, including disconnected
or closed parts. Strict four-corner U/V sampling checks both endpoints and
every≤10kmgeodesic midpoint. Missing and opposing samples are retained as
reasons for failure. Entry must be northward, exit eastward, all sampled
along-path components positive and length-weighted vector speed≥0.10m/s.
Original mean C is a separate source quantity, not hypot(mean U,mean V).

Lengths use WGS84 legs through exactly the stored six-decimal coordinates.
The same densified paths avoid the coarse OSW land mask. That does not verify
fine coastal, bathymetric or effective observational resolution. Complete
source-cell indices, four native corner vectors, interpolation weights, leg
midpoints and tangential velocities remain in the source-queryable report.
All paths, failures, raw contours, parameters, protocol/generator/source/mask
hashes and rounding rules are retained. No upstream source was reacquired.

## Atlas

The Loop card, seasons page and diagnostic query share the six-panel scientific
map, nominal approximate values and a table of all54cases. Original source
coverage remains visible. Full data and figure provenance join the checked
index; the large sample arrays are not embedded in the main diagnostic packet.
The source query exposes every case and original contour. Support-only Rust
validation blocks promotion of this report into physical-width, admitted-route
or length-assessment records.

The scientific sheet was rendered and inspected. The initial legend overlap
was corrected before publication. Black central paths have white outlines,
other gateway shifts are white, rejected components dashed red and gateways
orange; text/tables retain equivalent outcomes and scope. Full-size SVG is
explicitly linked for narrow screens.

## Verification and remaining gates

Focused source/geometry/shared checks:33tests and58subtests passed in44.77s;
one existing NumPy binary-size warning remains. All79Rust tests, locked native
and WASM builds, and actual native atlas loading passed. The54cases retain
72clipped components and8,532complete midpoint samples. Existing48other
diagnostics,239other owners/dashboard entries,5other research scenes, original
Loop intake/view bytes and every observation date remain unchanged. Widths155,
width samples463, routes76 and series28 remain unchanged by value.

Checked index:378documents,275,254,992original bytes /43,789,570compressed bytes.
Research registry:52documents/6scenes. Main packet:90,267,341bytes;
WASM:16,865,148bytes. Full sample records remain in the checked index.

Synthetic tests check strict missing-corner behavior even at zero weight,
bilinear vector reconstruction, reversed orientation, closed/wrong gateways,
retained missing/opposing samples, multiple supported-path ambiguity and coarse
land intersections. Every real supported path is independently recomputed with
Geod.line_length and complete midpoint weights; all54case IDs occur in the figure.
Changed protocol/figure/source pins must fail verification. Existing shared
source tests remain required. Browser verification checks all three actual
shipped-WASM views, every case against native/source records, phone/keyboard
use and packet/index corruption rejection before draft delivery.
The initial browser attempt incorrectly expected two image elements; the
existing analysis-view selector reuses one image. The test now exercises that
selector, and its default monthly-map label is replaced for these composites.
Final actual shipped-WASM browser PASS:all3views, every54case exact against
native/source, complete original phase/clock/scalar rows, keyboard320px,
11packet and2index corruption rejections, no automatic original downloads.
Phone screenshot inspected. All641unique staged source/build pins match;
staged whitespace check passes without modifying original source bytes.

The clean combined full suite is already running at ece1c14 in its separate
checkout. It predates this measurement batch. Leave its process, checkout and
native CLI undisturbed; after terminal state, a successor gate must cover the
latest combined work. Prior clean ce3cb2c full pass:1826tests/1164subtests.
Neither is a latest-contour full-suite pass. RemoteCI status stays separate.

Whole-current admission still needs independently reviewed physical endpoints,
daily-source/member correspondence and algorithm/source-use validation. The
other current length, route, width and seasonal gaps remain active. This
experiment supplies real, reviewable approximate contour distances without
relabeling them to inflate catalog coverage.
