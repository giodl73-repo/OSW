# Horizon Loop Current register: reuse decision packet

Status: candidate release gate, 2026-09-29. No external request has been sent.

## Material at issue

The [Horizon Marine Loop Current Eddies register](https://www.horizonmarine.com/loop-current-eddies)
lists 81 numbered primary events and some secondary names, with separation and
dissipation dates and other fields. The OSW v0.1.0 candidate uses 96 named-eddy
entities from that register. The generated
[`source-review-queue.json`](../almanac/release/v0.1.0/source-review-queue.json)
attributes 192 `entities` and `names` rows to this source. The candidate does
not package Horizon charts, maps, photos, forecasts, or its web page HTML.

The live page carries a 2026 Woods Hole Group, Inc. copyright notice. A public
page is evidence of the register's contents, but the review found no explicit
permission to redistribute the compilation. Horizon describes EddyWatch as a
commercial monitoring service whose data are compiled from several inputs.
The rights status of an individual name or date is a different question from
the terms for republishing most of this compiled register. Neither question is
resolved here.

## Decision needed for public deposition

Ask the register's owner for written terms covering the exact OSW use:

- Transcribe the register's primary and secondary eddy names, event identifiers,
  initial separation dates, and dissipation dates into versioned CSV and JSON.
- Display those records on an OSW searchable atlas, alongside independent
  source links and OSW editorial classifications.
- Deposit the same records in a public dataset archive, with a persistent DOI,
  downloadable files, and versioned corrections.
- State the required credit and citation, any excluded fields, any license or
  redistribution limits, and whether later updates need a new review.

The source page is [here](https://www.horizonmarine.com/loop-current-eddies);
Horizon provides a [contact route](https://www.horizonmarine.com/contact-us).
This packet is a prepared scope for an owner inquiry, not an authorization to
send one or a claim that permission will be granted.

## Release handling

Keep the full 96-entity register in the clearly marked local candidate while
the decision is open. Do not depict these as independently verified named-eddy
observations or as NASA-named objects. Kraken, Thor, and Ursa have separate
published observation citations, but those citations do not independently
reconstruct the full 96-record register. The
[alternative-source audit](ocean-motion-horizon-alternative-source-audit.md)
also checks NOAA's naming description, a BOEM report's sample named-eddy
mentions, and the restricted GOMED dataset; none replaces the compilation.

If the provider permits the proposed use, record its exact terms, credit,
review date, and evidence in `research/ocean-motion-source-use-reviews.json`,
then regenerate and validate the package. If the provider limits or declines
reuse, prepare a separate public subset from independently supported records
and label its scope and count explicitly. Preserve the full candidate internally
for source review; do not describe a partial subset as the full named-eddy
inventory. A public subset needs a new manifest, coverage report, and review.

This source decision is one publication gate. The NAVO coordinate use,
cartographic arrow derivation, other pending source reviews, dataset citation,
and final release reconciliation still need their own decisions.
