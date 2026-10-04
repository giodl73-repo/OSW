# Ocean motion atlas: source-use inquiry drafts

Status: prepared drafts, 2026-09-30. **No message has been sent.** These are
scoped to the current OSW candidate and should be updated if its exported
fields, provider files, or publication destination change.

## NOAA CoastWatch: MUNSTER and LSA

Route: [CoastWatch help desk](https://coastwatch.noaa.gov/cwn/about/contact-us.html),
which lists `coastwatch.info@noaa.gov` for product questions. Request routing
to the MUNSTER and Laboratory for Satellite Altimetry product stewards.

Subject: Reuse and citation of NOAA MUNSTER eddy records and LSA velocity subsets in an OSW atlas

> Hello CoastWatch team,
>
> We are preparing an OSW ocean-motion atlas and versioned downloadable data
> candidate. Please route these two product-specific reuse questions to the
> appropriate stewards.
>
> **MUNSTER v1.0:** We sampled 12 daily eddy-identification files dated March
> 2021–December 2023. We would publish 92,891 extracted detection records with
> center coordinates, polarity, radius, area, amplitude, source ordinal, and
> our approximate atlas-state joins. We would link each exact source file and
> retain its digest; we would not republish the original NetCDF files or full
> contours. Does the product's “Data license” section cover downloadable CSV
> and JSON redistribution of these values? What license label, preferred
> product citation, and NOAA, Copernicus/Sentinel, AVISO+, or other credits
> should accompany this use? Do any upstream terms limit publication?
>
> **LSA geostrophic currents:** We pinned five daily 0.25° files dated 18 and
> 24–27 September 2026. Our research repository contains packed `ugos` and
> `vgos` subsets for 30–45°N, 80–45°W. The atlas candidate includes the
> 25 September subset and a derived, explicitly partial frozen-time Gulf Stream
> streamline with approximate state intersections. May we make the five
> regional packed subsets and derived line publicly downloadable, including
> in a versioned dataset archive? What exact license, citation, contributor
> credits, and experimental-product cautions should we use?
>
> We will label these as NOAA-derived source observations, not as NOAA
> endorsement of OSW classifications. If a use differs between a public
> website, a source-code repository, and a DOI dataset archive, please specify
> the permitted scope for each. Thank you.

Decision records: [MUNSTER](ocean-motion-munster-reuse-decision.md) and
[LSA](ocean-motion-noaa-lsa-geostrophic-reuse-decision.md).

## Horizon Marine / Woods Hole Group: Loop Current register

Route: [Horizon contact page](https://www.horizonmarine.com/contact-us),
which lists an EddyWatch support route. Use the owner's current contact route
rather than assuming the public register itself grants reuse.

Subject: Permission terms for OSW atlas use of Loop Current eddy register names and dates

> Hello Horizon Marine team,
>
> We are preparing an OSW ocean-motion atlas with a versioned downloadable
> dataset. Our candidate transcribes 96 named Loop Current eddy records from
> your public register, including primary and secondary names, event numbers,
> separation dates, and dissipation dates where supplied. It links back to
> your register and adds OSW classifications and source distinctions; it does
> not copy your charts, images, forecasts, or page HTML.
>
> Please tell us whether we may publish these records in a searchable website,
> public source repository, and downloadable CSV/JSON dataset archive with a
> persistent DOI. If permitted, what credit, citation, license or written
> attribution wording, field exclusions, and update conditions apply? If only
> a narrower use is allowed, please specify which fields and destinations.
>
> We will keep the register attributed to Horizon and will not present these
> names as NASA identifications or independent geometry observations. Thank you.

Decision record: [Horizon packet](ocean-motion-horizon-reuse-decision.md).

## NAVO data via NOAA NCEI and OPC

Route: [NCEI contact](https://www.ncei.noaa.gov/contact) for the
[FREDDIES shapefile](https://www.ncei.noaa.gov/products/coastal-surface-analysis-products);
ask NCEI to route provider-specific questions to NAVO. For the separate
[OPC frontal bulletin](https://ocean.weather.gov/gulf_stream_text.php), ask
for the correct NAVO/OPC steward if NCEI cannot answer it.

Subject: NAVO FREDDIES polygons and Gulf Stream frontal bulletin reuse and datum

> Hello NCEI team,
>
> We are preparing an OSW ocean-motion atlas and versioned downloadable data
> candidate using two NAVO products. Please route these questions to the NAVO
> or OPC stewards where needed.
>
> From the 25 September 2026 North Atlantic FREDDIES ZIP we retain four
> operational eddy polygons and derive approximate atlas-state containment.
> From the 28 September 2026 Gulf Stream frontal bulletin distributed through
> OPC we retain 510 reported north/south wall coordinates, two dated lines,
> geodesic lengths, and approximate state intersections. The FREDDIES ZIP says
> approved for public release, but we did not find a `.prj` or item-level
> license statement.
> NCEI's current data-licensing page describes federal environmental data as
> open and in the U.S. public domain unless exempt, and says NCEI works to
> apply CC0 for international use. Does that policy apply to this specific
> NAVO FREDDIES ZIP and to the separate NAVO bulletin coordinates, including
> redistribution to readers outside the United States? Is either item
> explicitly assigned CC0 or another worldwide reuse statement?
>
> May we publish these exact coordinates and polygons, derived state metrics,
> and source-linked metadata on a public website, in a source repository, and
> in a versioned downloadable dataset archive? What datum/CRS, required
> NAVO/NCEI/OPC credit, preferred citation, and license or redistribution
> statement should accompany each product? Do the operational eddy codes have
> a stated lifetime or interpretation beyond one bulletin date? Thank you.

Decision records: [FREDDIES](ocean-motion-navo-freddies-reuse-decision.md)
and [Gulf Stream front](ocean-motion-navo-front-reuse-decision.md).

## Recording a reply

Record the respondent and role, reply date, exact reviewed material and public
destinations, license/citation text, and any exclusions. Preserve the reply as
an external decision record outside the generated package, then update
`research/ocean-motion-source-use-reviews.json` only for the source URLs whose
use the reply actually covers. Rebuild and validate the package after a
decision; a general NOAA statement does not automatically settle NAVO,
Copernicus, AVISO+, or Horizon material.
