# South Java reference map presentation correction

The source geography run40558983064 attempt2 passed all27 cases with both
coast masks at no more than1km geodesic spacing (30,621 points). Its detailed
fine-coastline image was actually inspected and is correct. Its first OSW
card image omitted the route because the chosen view origin did not include
the OSW projection's60/90 display offsets. Preserve this visual HOLD and the
exact executed SVG in the presentation-history directory.

The v2 renderer fixes the view origin and legend/gate label placement. It
also produces a compact drawing with readable labels at320px and390px.
All28 route polylines, both gate-circle attributes and the complete coast
path are unchanged. A private display transform and clipped viewport are
used only for compact presentation. Heading/footer backgrounds keep text
readable in SVG readers that do not implement clipping.

The v2 candidate changes only the figure pointer and view box, and adds an
explicit presentation revision with original and derived hashes. Every
other field, including every scenario coordinate, distance, state/crop
display relationship and scientific exclusion, is unchanged. It does not
rerun a source calculation or add a measurement.

Inspect the actual detailed PNG and both actual compact-width PNGs after
the final renderer change. These standalone SVG checks do not replace the
eventual browser support/card navigation and native/WASM delivery checks.
Keep the installed81-route checkpoint unchanged until query admission and
installation are independently verified.
