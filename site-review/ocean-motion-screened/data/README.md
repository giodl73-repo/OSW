# Ocean motion rights-screened preview

Status: internal review artifact. **Do not cite or deposit this as a released
dataset.** It is derived from the full `v0.1.0` research candidate by
`py analysis/build_ocean_motion_safe_preview.py`; validate with
`py analysis/check_ocean_motion_safe_preview.py`.

The preview preserves the eight source-reported ranked length estimates, 95
named-current entities, 40 named-eddy entities, 22 NASA-described motion
entities, and 56 OSW states. The full candidate contains 98 named currents and
136 named eddy source records. The five paper-sourced records for Kraken,
Thor, Ursa, Cameron, and Darwin survive screening with their paper citations
and observation windows; their possible Horizon counterparts do not. Cameron
and Darwin use independently measured events but names attributed by the
observing paper to Horizon Marine. Cameron's CAMR link is a dated center-point
candidate, not a whole-ring containment claim. The smaller
preview counts reflect source-use screening,
not a scientific retraction or a claim of global completeness. See the
[ranked-length source-passage audit](RANKED-LENGTH-EVIDENCE-AUDIT.md) before
interpreting the length order.
The preview includes one downloadable `entity-packets/` JSON excerpt for each
of its 213 entities. Each packet groups that entity's screened records,
claims, related-object labels, and cited source metadata. The path index is
`entity-packets-index.json`. These are review copies, not independently
published datasets or a claim of global completeness.
The [fingerprint-bound editorial index](ranked-length-editorial-reviews.json)
connects those eight audit findings to the exact measurement claims, without
marking them scientifically reviewed.
The Kraken entry also carries a Figure 2 red-curve location candidate for
`CAMR`, with source PDF and embedded-image hashes, three dated panel envelopes,
and ±3-pixel axis calibration sensitivity. It is not a whole-ring footprint or
a verified containment decision.

The screening removes all 23 pending external source rows, including 17 used
sources (16 exported provider-value sources and one credited cartographic
service) and six catalog-only NASA rows. It removes Horizon-derived Loop eddy
names and dates, the 12 sampled NOAA MUNSTER observation sets, NAVO and NOAA
dated observation rows, and ArcGIS-derived arrow relations and illustrated
spans. It does not substitute missing rows with false or zero. The remaining
geometry records are editorial locators, not observed footprints.

This preview includes screened excerpts for the five internal source ledgers
reached by retained claim pointers. Each pointer resolves to the exact retained
record; excluded array positions are `null`. These excerpts are not full
source ledgers or an acquisition workflow. Every retained scientific claim remains
`not_individually_reviewed`. No DOI or publication authority is asserted.
The public atlas and repository still need a separate source-use and
accessibility reconciliation before publication.

`screening-report.json` gives exact retained and removed row counts;
`manifest.json` pins the source candidate manifest and every preview file.
JSON and CSV collections share stable IDs and are checked for closed claim
references and pending source URLs. The report separates direct pending-source
references from 118 ArcGIS-arrow state relations whose primary `source_id`
points to an OSW ledger, and source usage counts are recomputed for the
screened export.
