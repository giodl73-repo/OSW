# Thor and Ursa dated source panels — protocol v1

Status: editorial original-source extraction; scientific admission pending.

1. Own the panels only by `eddy:published:thor-2020` and
   `eddy:published:ursa-2021`, as named in Johnson Exley et al. (2022),
   doi:10.3389/fmars.2022.1049645. Do not resolve other registers' identities.
2. Preserve all 25 dates printed in Figure 2 and all 25 in Figure 3, in
   row-major order. Dates describe the displayed regional field during the
   named shedding event; they are not 50 confirmed independent ring positions.
3. Pin the complete publisher JATS XML and the unchanged publisher WebP
   figures by SHA-256 and byte size. Credit the authors, publication and
   CC BY 4.0 license. A displayed panel is a cropped view; retain access to
   the unchanged complete figure, including axes and color legend.
4. Crop rectangles use source-image pixels. They are presentation coordinates,
   not longitude/latitude, map bounds, current routes or footprints.
5. The colors show mapped deep reference pressure expressed as sea surface
   height, SSH_ref; black bold curves show the surface Loop Current contour.
   Colored patches are not Thor/Ursa perimeter definitions. Preserve the
   original color-bar units; do not rescale the field.
6. The Methods text prints a `0.65 cm` contour. Preserve that wording and
   leave its physical unit unresolved; do not silently substitute meters or
   compute a numerical contour from it. The provider product is the historical
   daily near-real-time mapped altimeter product with reported 25 km resolution.
7. A curve meeting a frame edge is incomplete. Never close it along the frame,
   assume a circle, use the instrument-array box or fill a colored patch.
   The 2021-03-07 Ursa-event panel is a candidate for subsequent contour review;
   no numerical polygon is digitized or admitted by this inventory.
8. Detached small loops are not automatically the named ring. Preserve the
   paper's detachment/reattachment narrative separately from panel appearance.
9. Use manual date selection and previous/next controls. This irregular,
   event-specific sequence is not a recurring seasonal climatology. Do not
   interpolate positions, animate annual playback or calculate annual margins.
10. Leave geometry, center, radius, area, width, length, uncertainty and
    physical OSW state relations unresolved. NASA links remain geographic
    context unless independent event identification and temporal alignment
    are established.
11. Validate the same pinned source, owner, dates, crop coordinates and claim
    limits in Python, native Rust and shipped WASM. Re-signed mutated receipts
    must fail. Source-index inspection must recover each original audit row.
