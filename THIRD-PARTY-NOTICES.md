# Third-party data notices

OSW software, original documentation, and original artwork are distributed
under the repository's MIT License. Third-party scientific data remain under
their source terms and are not relicensed by OSW.

## Marine Regions Longhurst Provinces

`research/longhurst-2007-gebco-2026-depths.json` and
`column/province-footprints.js` contain a transformed 0.25° raster assignment
derived from **Longhurst Provinces Version 4, March 2010**, distributed by the
Flanders Marine Institute (VLIZ), Marine Regions. Marine Regions states that its
products are available under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

Preferred source citation: Flanders Marine Institute (2009). Longhurst
Provinces. Available online at <https://www.marineregions.org/>.

OSW modifications: code crosswalk to the older 56-name directory; GEOS validity
repair of three invalid source rings; 0.25° cell-center rasterization; spherical
area weighting; GEBCO intersection; run-length encoding; summaries; and
Oceanic Mollweide display. The complete provider geometry response is not
redistributed. Its exact WFS URL, response byte count, and SHA-256 are retained
in `research/longhurst-2007-gebco-2026-source-receipt.json`.

## GEBCO 2026

The paired bathymetry and Type Identifier values derive from the GEBCO_2026
Grid, DOI `10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa`. GEBCO makes its grid
available in the public domain and requests acknowledgement. It combines
heterogeneous source types, carries vertical-datum limitations, and must not be
used for navigation. Exact OPeNDAP requests and response hashes are recorded in
the source receipt; the full responses are not redistributed in this stage.
