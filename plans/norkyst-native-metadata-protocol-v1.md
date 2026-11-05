# Native NorKyst vertical metadata discovery

The existing25fixed-z Jutland sections have12censored primary lower boundaries.
Locate native-layer data before declaring new fields or depth operators. Primary
model documentation: Christensen etal2026,doi10.5194/gmd-19-2785-2026, sections2/5.2
and data availability. Native ROMS has40stretched layers; provider fixed-z has25.
Do not replay any prior Ingoy or Jutland successful field/metadata responses.

Start at the official THREDDS native-product root catalogue in XML form:
https://thredds.met.no/thredds/catalog/romshindcast/norkyst_v3/catalog.xml
This catalogue has not previously been captured in this programme. Follow only
observed same-provider catalogue references within that product subtree, preferring
native/sigma/sdepth/original/3D/hourly/ROMS names. Exclude zdepth and named temporal
mean products. Target year2024,month03,date20240315; no arbitrary fallback date or
guessed dataset path. Preserve unmatched references for review rather than force
selection. Fetch a DDS/DAS pair only if exactly one observed dated dataset and one
observed OPENDAP service base identify it unambiguously.

At most4catalogues plus2DDS/DASrequests, one attempt each,25s timeout,250000bodybytes
per response, no redirects/retries/fallback. Output<=2.4MB, report<=500kB. Retain
exact metadata bytes/hashes and failed transport receipts. No nc/ASCII/DODS field
endpoints, velocity/depth/bathymetry arrays or ocean values decoded. Metadata can
reveal dimensions, variable names/attributes and CF conventions, not current depths.

Review actual native depth coordinates, Vtransform/Cs/hc/h/zeta, velocity rotation/
staggering, units and source time before a separately declared bounded field read.
Use the same original Jutland source positions and preserve all fixed-z censors;
native and fixed-z products are not independent observations. No old method or
eligibility relaxation, measurement/ranking/volume/UI/whole-current promotion.
Metadata acquisition/parsing/tests cloud only, sequentialoneidleCPU. Local static
editing/AST,primarydocument/metadatareview, hashes/exactretention only.
