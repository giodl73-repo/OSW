# Antilles-region shipboard component spans

These diagnostics use NOAA's final AB0505 CODAS3 shipboard ADCP product.
Source: https://www.aoml.noaa.gov/ftp/phod/pub/WBTS/Global_Class/GC_2005_05/FINAL_ADCP_PRODUCTS/sadcp_matfile/AB0505_codas3_sadcp.mat
The acquisition receipt pins the original MAT bytes; `--verify-original`
independently compares all 1,327 retained observations, times, coordinates,
depths and unit conversions against that original. The regional subset and
predeclared method are separately pinned. Original cm/s become m/s.

Two May 2005 occupation windows and ten exact exported depth centres give
20 configurations. Longitude bins contain medians of paired finite u/v
observations within the prescribed latitude strip. The peak search gate is
an OSW editorial selection, not a published current axis. The first connected
40%, 50% and 60% peak crossings are interpolated on each side; missing bins
and open domain edges stop the search. A coastline is never assigned zero.
WGS84 endpoint distance is rounded to the nearest 10 km. Threshold envelopes
are rounded outward, and exist only when all three scenarios resolve.

Seven half-peak spans resolve; six have complete sensitivity envelopes.
At 95 m, the two spans are approximately 50 and 80 km. The first envelope is
40–130 km; the repeat envelope remains unknown because its 40% boundary is
open. These ranges measure operator sensitivity, not errors or annual extrema.

These are local northward-component spans of occupation composites, not
verified flow-normal current widths. The current association, whole-current
width, annual range and measurement uncertainty remain unknown. No widths
are admitted to rankings or physical map bands. Native vertical bins are
16 m; the exported 10 m spacing does not improve native resolution. In
particular, 395 m is neither 400 m nor 400 dbar. Source clock timezone and
tidal correction are unspecified. The earlier LADCP caution is separate.

The dashboard opens the two 95 m profiles in the Rust/WASM query interface;
the collection exposes all depths, threshold failures and source pointers.

Reproduce: `python analysis/build_antilles_sadcp_layer_spans.py`.
With the retained original MAT, add `--verify-original` to check the extraction.
This verification is optional for offline users; the checked numerical subset
is shipped and its exact bytes are mandatory for normal reconstruction.
