# HYCOM South Australian section subset

Provider: Naval Oceanographic Office / Naval Research Laboratory / HYCOM.org.
Product: GOFS 3.0 HYCOM+NCODA Global 1/12° Reanalysis, GLBu0.08 experiment.

Original provider `section.ascii`, `metadata.das` and `metadata.dds` responses
are retained unchanged. `acquisition.json` records exact requests, original
byte counts, SHA256 hashes, acquisition time and attribution. The official
[catalog](https://tds.hycom.org/thredds/catalogs/GLBu0.08/reanalysis.html?dataset=GLBu0.08-reanalysis)
states the dataset is freely available; original metadata states approved for
public release and unlimited distribution. These provider bytes are source
data; OSW's derived diagnostics remain separate.

The subset includes daily 00Z u/v model velocity for every day of 2012,
at fixed 132°E and 100 m, on 76 native latitude cells over 38–32°S. Source
Int16 values use scale factor 0.001 m/s and missing flag -30000. Coordinate
maps are part of the original ASCII response. No current-width, observational
footprint, annual extrema or scientific approval is supplied by this cache.

Verify retained bytes with `python analysis/acquire_south_australian_hycom_section.py`.
Reconstruct the JSON inventory and monthly diagnostic with
`python analysis/build_south_australian_hycom_spans.py`. Acquisition requires
explicit `--acquire` and refuses to overwrite an existing cache.
