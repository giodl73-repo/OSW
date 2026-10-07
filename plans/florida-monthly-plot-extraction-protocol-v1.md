# Florida monthly width graph extraction v1

Read Figure 9b, printed page 9199, from the checksum-pinned NOAA original of
Archer, Shay and Johns (2017). Inspect the rendered page and embedded image
before selecting the gray overall-average curve. Keep the red 2006 and blue
2005 curves distinct. Do not infer a pooled daily mean, missing observations,
year-specific monthly values, or equal sample weights from the gray curve.

Use embedded CMYK image object 160 converted to RGB with PyMuPDF. Pin dimensions,
RGB checksum, calibrated 65/50 km horizontal grid lines and the twelve month
ticks. At each tick use a seven-pixel strip. January and December strips move
eight pixels inward to avoid the axes; record both tick and sample locations.
Within the configured width-panel y window, select near-neutral pixels with
channel spread below 12 and mean intensity strictly between 80 and 170. Split
contiguous y bands and select the band with the largest matching pixel count.
Require at least seven matching pixels spanning at least three rows. This
separates the thick gray curve from light shading/grid and colored curves.

Convert the selected median y using a linear pixel-to-km calibration, round
to the nearest kilometre (positive half up), and retain raw value and pixel
band. Give each reading a conservative +/-1 km editorial graph-reading
allowance, covering rounding, stroke thickness, calibration and the small
endpoint shift. It is not measurement uncertainty, confidence on the mean,
within-month standard deviation, or a physical boundary margin.

Keep 2005-2006 year support, 25.42 N local jet-coordinate section, nominal
0.75 m HF radar sensing depth, half-core-speed boundary and 40 h metric filter.
The caption calls the light-gray envelope mean within-month standard deviation;
that envelope is not extracted here. These are monthly graph readings, not
dated samples or modern climatology. No annual physical extrema, full-current
width, fixed vertical layer, coordinates or geographic playback follow.
Chart playback may step through the twelve readings with source and reading
allowances visible. Never interpolate geographic boundaries from the curve.
