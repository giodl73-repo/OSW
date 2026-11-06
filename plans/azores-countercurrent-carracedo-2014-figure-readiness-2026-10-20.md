# Azores Countercurrent: Figure 2 measurement readiness

Continues branch `codex/current-measurement-gaps` and draft PR #83. This is
a source inspection result, not a new width measurement or a closed gap.

## Original checked

Carracedo et al. (2014), doi:10.1016/j.pocean.2013.12.005, Figure 2,
printed page 120 / PDF page 5. The retained original is 3,967,121 bytes,
SHA256 `ea9ca0c5f5fde1b3234518aca1810a2421c556090aee9531ff46797f37eec7e8`.
Its embedded image (PDF xref 175) is 1747 by 1360 native pixels, SHA256
`bb1df50a710bab369f4abad899c22508f33be14598de30c687f39c505123b33f`.
The analysis image was checked byte-for-byte against the PDF extraction.
Original PDF, image, crops and inspection overlays remain excluded from Git.
Nearest-neighbour enlargement adds no resolution. Publisher high-resolution
Figure 2 access returned HTTP 403; no replacement image was obtained.

## What the inspection establishes

The western-section latitude axis has labelled 31, 33, 35, 37, 39 and 41 N
ticks. This provides horizontal calibration support; it does not resolve the
vertical coordinate or identify unlabelled contour levels.

The spring and autumn panels have legible negative 0.5 cm/s labels. Annual,
winter and summer contain thin interior contours whose levels have not been
established from readable labels. Their position inside grey westward flow
does not establish that they are the selected negative 0.5 cm/s contour.
The adjacent bold zero contours and reference-level lines are different
features and cannot substitute for the selected boundary.

The labelled vertical positions do not support one global linear metres-to-
pixel transform. In the autumn panel, the surface, 1000, 2000, 4000 and 6000 m
label glyphs are centred at approximately native rows 1040.5, 1073, 1113.5,
1151.5 and 1192. These are **text glyph locations**, not calibrated tick
coordinates. In particular, they must not be treated as measured ordinates.
The source coordinate transformation between ticks has not been established.
Piecewise interpolation would introduce an unverified transformation model;
it has not been used to claim exact 800, 1200 or 1600 m crossings.

The spring labelled lobe also requires a complete geographic-context check:
its western extent appears south of the preflight's 36 N context. No lobe
has been clipped to a latitude window to make it pass. Autumn's westernmost
edge is close to that context boundary and needs explicit pixel bounds.
These are inspection flags, not accepted endpoint coordinates or distances.

## All fixed cases remain unresolved

The protocol remains
[the original 15-case preflight](azores-countercurrent-carracedo-2014-contour-span-preflight-v1.md).
No threshold, depth, panel, naming window or acceptance rule was changed.

| Source panel | 800 m | 1200 m | 1600 m | Unresolved requirements |
| --- | --- | --- | --- | --- |
| Annual | Unmeasured | Unmeasured | Unmeasured | Contour-level identity; vertical calibration; paired crossings |
| Winter | Unmeasured | Unmeasured | Unmeasured | Contour-level identity; vertical calibration; paired crossings |
| Spring | Unmeasured | Unmeasured | Unmeasured | Vertical calibration; lobe containment; paired crossings |
| Summer | Unmeasured | Unmeasured | Unmeasured | Contour-level identity; vertical calibration; paired crossings |
| Autumn | Unmeasured | Unmeasured | Unmeasured | Vertical calibration; context-edge reading bounds; paired crossings |

These entries mean the proposed reading has not passed its gates. They do
not mean that the current or contour is absent at any of those depths.
No zero-width values, numerical uncertainty intervals, monthly interpolation,
ranked dimensions or canonical width rows follow from this inspection.

## Next useful source input

Recover an author-provided section field with its depth coordinate and
contour specification, or a source figure/plot specification that establishes
the vertical transformation and missing contour labels. Then calibrate each
panel and retain all 15 outcomes, including any genuine absent crossings.
Do not spend further effort estimating dimensions from unverified glyph
centres. The whole-current physical width gap remains open.

The published transport integration over 36–40 N and the first 1800 dbar is
separate context; it supplies neither a metre-axis conversion nor paired
velocity boundaries. The earlier 2009 110 km section evidence and the Azores
Current's 240/400 km seasonal model-core summaries remain distinct records.
