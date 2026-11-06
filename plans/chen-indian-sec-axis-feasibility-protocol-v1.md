# Indian SEC regional model-core feasibility protocol v1

Freeze before reading target velocity fields or extracting target routes. This is a bounded source-feasibility diagnostic, not measurement admission. No kilometres, widths, ranks, current-state joins or physical endpoints are calculated. The global heavy-work switch remains false; this separately scoped request permits one small source-file diagnostic on the cloud only.

## Source and scope

Use exactly the publicly listed HYCOM_CR_1993_2016.mat sample,5,816,818bytes, SHA256 ce174a089a2379cd8c5a79ede226982749d9102a7e7b7d2d0a9180c75ac23cb7. The provider describes upper100m SON fields. The original six variable headers and coordinate vectors have already been inspected on the cloud. The grid spans approximately40.905–124.95E,19.8S–4.95N, with variable longitude spacing. Preserve exact coordinates.

The source time vector admits a MATLAB serial-date interpretation yielding October15 in1993–2016. That encoding is inferred, not declared. Use provider-year labels, retain the inference and never call these observation dates or monthly samples. The original Figure4 surface-geostrophic routes remain unacquired and are not reproduced here. Component units are undocumented in the MAT file. The diagnostic assumes standard east/north component signs and uses no speed measurement or dimensional velocity threshold.

## Fixed regional operator

Use intended regional gates65E and105E, deliberately inside the model domain and away from the western boundary and Indonesian outlets. These are editorial comparison gates, not physical current ends. Select the nearest native longitude to each gate, breaking ties toward the smaller longitude, and retain the actual sampled meridians. Search only18S–6S, a declared diagnostic band around the provider-described SEC region. Reaching this band's edge is a failure, not evidence for a current boundary.

Read only lat, lon, time_year, uyear and vyear; never load hyear. Require the exact source and coordinate identity, increasing axes and76x212x24 field shapes. Refuse potentially unresolved finite fill values larger than1e10 in absolute magnitude. Nonfinite component pairs are missing support; zeros are not automatically land.

For every native longitude, choose the most negative zonal component within the band among finite westward cells. A tie selects the southmost cell. Evaluate three declared operators: raw field and3x3 and5x5 finite-neighbor arithmetic means. The3x3 operator is nominal. Smoothing requires at least80percent finite neighborhood support and never fills a missing center. These kernel differences are method sensitivity, not physical uncertainty.

Proceed from east to west without interpolation, branch bridging or numerical optimization. A longitude with no finite westward candidate stays a gap. A core on either search-band edge is flagged. A jump of more than three native latitude cells between adjacent selected columns is flagged and disconnected in the drawing. A trace passes this narrow feasibility screen only if it has no flags. Passing is not scientific approval or proof of a physical axis.

Evaluate every one of the24 source slices with all three operators. Also evaluate the field mean using only cells with paired finite components in all24 slices. The core of the mean field is not a mean path or mean length. Preserve all75 traces and every failure; do not select successful years to imply completeness or tune the frozen method to a desired result.

## Visual review and subsequent measurement

Render the mean field and provider-year1994,1997,2015,2016, each with all three operators, the actual native grid, gate context and flow directions. Use normalized westward component color and unit-direction arrows, not speed units. Show gaps and suppress jump connections. Preserve SVG and PNG views; retain all other trace geometries in the report. Figures are regional model diagnostics, not OSW physical atlas layers or NASA observations.

Before any kilometres are calculated, inspect actual maps and diagnostics for eddy selection, wrong branches, edge attraction, missing support, grid sensitivity and component semantics. A separately frozen WGS84 length protocol must specify admissible traces, gate treatment, resolution sensitivity, model attribution and required query/atlas delivery. Keep whole-current lengths, physical uncertainty, annual ranges and observed-date capabilities unmeasured. A later admission requires complete provenance, scientific review and verified native/WASM/visual delivery.

## Resources and custody

One cloud CPU, low scheduling priority, one job in osw-current-gap-delivery with cancel-in-progress false, one source file capped at8MiB. The command has180seconds and the workflow10minutes. No provider code execution, local source-field download, broad field processing, native/WASM build, browser work or installation. Temporary original and field arrays remain on the cloud and are discarded. Upload only the compact derived report and five map pairs. Retain any failure and version later method changes.
