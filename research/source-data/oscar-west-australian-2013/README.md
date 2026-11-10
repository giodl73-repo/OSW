# Original offshore OSCAR section responses

Provider: Earth & Space Research, mirrored by NOAA PIFSC ERDDAP.
Dataset `yearly_336c_0b32_9cd3`, OSCAR version 2017.0.
Original `section.csv` and `metadata.json` bytes are preserved; the exact
queries, acquisition timestamp, sizes and SHA256 values are in acquisition.json.

The original metadata license explicitly permits free use and redistribution.
It does not establish a CC0 license. Cite the provider and OSCAR product.
The metadata's nominal depth coordinate is 15 m; this is a satellite-derived
near-surface velocity product, not a direct instrument measurement at 15 m.

Section: 32 S, 60–116 E, both eastward u and northward v, 72 archived 2013
times, 169 cells per time. Retain the source's four six-day intervals and
144 missing vector pairs. Metadata missingness is not a geographic land mask.
The derived report preserves paired monthly support and exact source times.

These responses do not establish West Australian Current identity or width.
The predeclared offshore section and peak-search window are OSW choices.
Reproduce with `python analysis/build_west_australian_oscar_spans.py`; source
refresh is explicit (`--acquire`) and refuses to overwrite this directory.
