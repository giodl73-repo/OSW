# Regional REDSOX conditional depth anchors

Use the four existing supported RSX1 source cases, in their original order,
without new ocean retrieval or archive decoding. Bind every input by SHA256.
Preserve station coordinates, distinct LADCP-header/CTD-start clock roles,
component convention, source pointers and all original qualifications.

Represent each case as a GeoJSON Point at its provider-reported longitude and
latitude. Vertical quantities belong in properties; do not encode positive-down
depth as GeoJSON altitude. Do not draw a geographic route between the points.

The resolved upper joint crossing and deepest connected native velocity sample
provide a minimum vertical extent of the reconstructed q>0.2m/s and practical
salinity>=38 support. Subtract upper-crossing depth from deepest supported depth.
The resulting nonnegative value is an inclusive lower bound on conditional
support extent. It is not a physical current-thickness estimate, uncertainty,
annual range, new independent observation or an additional primary measurement.
The crossing is not a physical flow top; the censored lower end is not seabed or
current bottom. No layer is inferred around the core or from surface zero.

Keep fixed-southward and section-normal groups separate. No between-point
interpolation, common instantaneous time, along-current coordinate, width join,
area, volume, annual envelope or whole-current profile is admitted. Existing
reference and projection inventories remain unchanged. This separate collection
is a research adapter for later atlas/query integration, not a deployed UI.

Execute tests and construction only in cloud, sequentially on one idle CPU.
Reuse frozen reports; no provider reads. Output <=2.4MB, each file <=2.5MB.
Retain exact successful artifact once, pin cloud run and output hash, preserve
all old references, eddy registers and source review inputs.
