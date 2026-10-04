# Named eddies: next atlas join

Status: five paper-sourced records implemented on 2026-09-30; dated footprint work remains. This document does not authorize publication.

Kraken Figure 2 now has a reproducible red-pixel state-location audit in
`research/kraken-2013-figure2-state-audit.json`. The three dated panels support
a `CAMR` location candidate for the depicted coherent-core and shielding
curves. They do not provide a closed georeferenced polygon for the whole ring.
To regenerate it, install `requirements-figures.txt`, download the exact
[NOAA-hosted PDF](https://repository.library.noaa.gov/view/noaa/18748/noaa_18748_DS1.pdf),
and run `python analysis/build_published_kraken_figure_state_join.py --pdf PATH`.
The script checks the source SHA-256 before writing the audit.

## Finding

The full candidate now has 136 source-scoped named-eddy records, including five paper-sourced Loop Current ring records. The rights-screened preview retains 40 named eddies, including those five paper-sourced records and their observation rows. The Horizon-sourced records remain excluded. Paper and register records for a name are a possible same-ring crosswalk, not two confirmed physical eddies.

The [Kraken study](https://www.nature.com/articles/s41598-018-29582-5) identifies the ring and analyzes a coherent material core from 29 May to 15 December 2013. Its approximately 100 km core radius is not an outer ring footprint. The [Thor and Ursa study](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645/full) names both events and shows dated Loop Current contours in Figures 2 and 3. Its 89–86°W, 25–27.5°N instrument array is a study area, not either eddy's boundary. Neither paper's text supplies a reusable coordinate polygon or a complete track for an OSW state containment claim.

## Implementation and remaining work

The [2012 mooring and altimetry study](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890)
adds dated western Gulf evidence for Cameron (20 January 2009, center near
22.5°N, 95°W) and Darwin (25 July and 5 August 2009). The authors explicitly
credit both names to Horizon Marine. The observations are independent
measurements, while the names are source-attributed. Their dates do not resolve
the conflicting 2019 simulated formation chronology. The structured audit is
`research/loop-eddy-cameron-darwin-name-date-conflict.json`. Both are now
source-scoped observation records in the review package. Cameron's reported
center projects to a `CAMR` point candidate; no whole-ring state containment
relation is asserted for either ring.

1. Done: create five publication-sourced individual records with distinct IDs, names, paper citations, and the paper's *observation window*. The full research ledger carries the separately labeled possible-identity crosswalk to Horizon records. The screened export contains no Horizon URL, event number, separation date, or copied Horizon source-ledger row for these records. Its attribution text states that the 2012 paper credits the Cameron and Darwin names to Horizon.
2. Done: attach paper observation claims to the publication-sourced IDs and rebuild the full release, screened preview, and review atlas. Cameron has a source-reported dated center point projected into approximate `CAMR`; Darwin has no exact center or state locator.
3. Keep every named-eddy × state whole-feature physical decision unresolved. A central or eastern Gulf phrase, array box, map gateway, single center point, or figure-derived coherent-core curve may support a narrower location candidate; none proves whole-eddy containment or intersection.
4. For a physical state claim, obtain a dated, provider-defined ring contour or a defensible digitization of the paper's boundary, pin the figure/data version and method, preserve the observation date, and intersect it with the coast-masked OSW polygons. Mark an observed-center join separately from polygon containment. Seek scientific review of the contour interpretation before showing it as a physical relation.

## Source and release gates

The next geographic increment is a dated contour or defensible figure
digitization with source rights and scientific review. The present Cameron
center-to-state lookup is a point candidate only; it cannot set `contained`
or `intersects` for the whole eddy.

- Review the articles' figure/data reuse terms before packaging a copied figure or digitized contour. A citation and URL alone can be kept as paper provenance.
- Keep NASA Perpetual Ocean links as geographic film context. These papers do not identify these individual rings in a NASA frame, and Thor lies outside the NASA model years used by the current crop ledger.
- Continue the broader release gate: 17 used rights-pending source rows, eight ranked lengths awaiting scientific review, human accessibility review, and an owner publication decision.

## Acceptance checks

- Five paper-sourced eddy entities and five primary linked observation claims survive screening; zero pending external source IDs or URLs survive.
- Full and screened counts, source-use summaries, claim pointers, CSV/JSON exports, site manifest, and browser object search reconcile.
- No named-eddy state row changes to `contained` or `intersects` without dated footprint geometry and a cited method.
