# NAVO FREDDIES polygon reuse decision packet

Status: open for the 2026-09-25 candidate observation; no external request sent.

## Material in the candidate

- Provider: Naval Oceanographic Office (NAVO), distributed by NOAA NCEI as
  [North Atlantic FREDDIES geospatial data](https://www.ncei.noaa.gov/products/coastal-surface-analysis-products).
- Exact source URL: `https://www.ncei.noaa.gov/jag/navy/data/satellite_analysis/nafreddy.zip`.
- Source ZIP SHA-256: `94e371a68f6e7d1dde35273046e37c13daab57a72dea2ff5c7757d8dec9d6e0c`.
- Four dated operational eddy polygons are preserved in
  `research/navo-freddies-eddy-snapshot-20260925.json`; four derived state
  containment rows and simplified map outlines are in the atlas candidate.
- The ZIP's `release.txt` says the fronts and eddies are unclassified and
  approved for public release. The ZIP has no `.prj` or license member.

## Evidence and unresolved decision

[NCEI's current data-licensing page](https://www.ncei.noaa.gov/data-submission/data-licensing)
quotes its open-data policy: environmental data produced by NOAA or another
federal agency are fully open unless an explicit legal or policy exemption
applies, and are in the U.S. public domain. It says NCEI will work to apply
CC0 for international use. The earlier `/archive` URL now redirects to a
submission page; it is no longer the precise policy citation. Together with
the ZIP's approved-public-release text, this supports access, but the item has
no stated CC0 grant, specific worldwide reuse statement, preferred citation,
or coordinate datum. The candidate therefore keeps the polygon redistribution
decision open rather than treating a general policy as a file-specific license.

Before depositing the candidate as a public dataset, record the provider's
answer or authoritative metadata for: (1) polygon redistribution and derived
state metrics; (2) the exact license or public-domain declaration; (3) required
NAVO/NCEI credit and citation; (4) the shapefile coordinate reference system;
and (5) the interpretation and lifetime of `W26001`-style operational codes.
If those cannot be established, publish only links and factual state summaries
after a source-specific review, and omit the original polygon coordinates from
the deposited package. The present candidate keeps the rights status pending.
