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

## Marine Regions Gazetteer in the motion almanac

The ocean motion current crosswalk links to Marine Regions Gazetteer records
for name context. OSW publishes its source-specific matching decisions, not a
copy of the provider's gazetteer or geometry. Marine Regions states that its
products are available under [CC BY terms and its terms of use](https://www.marineregions.org/disclaimer.php)
and requests that users link to its current service.

Provider citation: Flanders Marine Institute (2026). *MarineRegions.org*.
Available online at <https://www.marineregions.org/>. Consulted 2026-09-29.
The Gazetteer name-context use was reviewed for this candidate on 2026-09-29;
the provider's CC BY attribution and service-link request are recorded here.

## NOAA current glossary and marine guide

OSW links and paraphrases current names and factual descriptions from NOAA's
[Tides and Currents Glossary](https://www.tidesandcurrents.noaa.gov/glossary.html)
and the NOAA Voluntary Observing Ship Program's [*Marine Weather Information
Guide*, July 2017](https://www.vos.noaa.gov/docs/marine_info_guide.pdf).
Consulted 2026-09-29. NOAA is credited as the source. The guide PDF and its
embedded ocean-current map are not reproduced in the candidate; copying or
digitizing that artwork requires a separate source-specific review. NOAA's
[use guidance](https://oceanservice.noaa.gov/about/faq.html) says most agency
information is public domain unless otherwise noted and asks for NOAA credit.

## Cartographic ocean-current arrow layer

The motion almanac uses source arrow IDs and derived map intersections from
the [Major Ocean Currents arrow polygon layer](https://services3.arcgis.com/o98K21Ga5N91Ugjw/ArcGIS/rest/services/Hurricane%20TracksAA/FeatureServer/11).
The layer describes four drawing widths for each arrow and credits NOAA,
National Weather Service, US Army, and Maps.com. OSW's illustrated-span proxy
measures these drawn symbols; it is not a measured current length. The raw
polygon layer is not redistributed in the ocean motion candidate package.
The reviewed layer metadata does not state a reuse license, so geometry
redistribution remains outside the current release candidate.

## NAVO operational eddies via NOAA NCEI

The separate [NAVO/NCEI North Atlantic FREDDIES shapefile](https://www.ncei.noaa.gov/products/coastal-surface-analysis-products)
provided four dated operational eddy polygons for 2026-09-25. Its ZIP states
that the material is approved for public release. OSW preserves polygon
coordinates and source hashes in a candidate research ledger; the package
does not declare a particular international reuse license for this source.
[NCEI's data-licensing policy](https://www.ncei.noaa.gov/data-submission/data-licensing)
describes federal environmental data as open and in the U.S. public domain
unless exempt, while stating that NCEI works to apply CC0 for international
use. The FREDDIES ZIP has no item-specific CC0 declaration or coordinate
reference file, so the candidate's polygon redistribution review remains open.

## NAVO Gulf Stream surface fronts via NOAA OPC

The candidate includes coordinate lines from the [NOAA Ocean Prediction
Center Gulf Stream ASCII bulletin](https://ocean.weather.gov/gulf_stream_text.php),
which credits the Naval Oceanographic Office as data provider. The pinned
2026-09-28 bulletin supplied 306 north-wall and 204 south-wall points. OSW
uses them as dated analyzed surface fronts and derives eight approximate
state intersections. The [NWS disclaimer](https://www.weather.gov/disclaimer/)
states that page information is generally public domain unless noted, but
the NAVO-provided coordinates' item-specific status is not established by
that general policy. Coordinate redistribution and required provider
attribution remain a release gate; these lines are not a current axis or full
current footprint.

## NOAA LSA geostrophic current analysis

The [NOAA Laboratory for Satellite Altimetry daily product](https://coastwatch.noaa.gov/cwn/products/sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html)
provides 0.25-degree surface geostrophic velocity. OSW pins a 2026-09-25
regional velocity subset and derives one dated, partial Gulf Stream streamline.
Four additional regional subsets dated 18, 24, 26, and 27 September 2026 are
pinned in the research workspace for a repeat-date audit; they are outside the
dataset candidate but would still be redistributed by a public repository.
The NOAA product page requests acknowledgment of the NOAA Laboratory for
Satellite Altimetry and NOAA CoastWatch. The source file digest and precise
data URL are in the candidate ledger, and the repeat receipt records its four
additional source files. Product-specific reuse and citation review remains
open for public repository publication and dataset deposition.

## NASA Perpetual Ocean media

The motion almanac links to NASA Scientific Visualization Studio releases and
70 regional Perpetual Ocean 2 movie crops. OSW does not redistribute movie
files or claim NASA endorsement of its names, taxonomy, state boundaries, or
crosswalk. The seven source-page titles, dates, credits, and API response
digests are recorded in `research/ocean-motion-nasa-svs-metadata.json`.
[NASA SVS's usage guidance](https://svs.gsfc.nasa.gov/help/) says its content
is generally public domain unless an item notes an exception; individual
media and audio still require item-specific review before redistribution.
The [Perpetual Ocean 2 release 5505](https://svs.gsfc.nasa.gov/5505) source
links and factual descriptions were reviewed for this candidate on
2026-09-29. The other nine used SVS page, transcript, and media-group URLs
were reviewed for the same link and factual-description use. All ten now have
page citations with NASA's item-specific credit in the source registry. The
[narrated 2025 release](https://svs.gsfc.nasa.gov/14745) also provides DOI
10.5281/zenodo.16782525. These decisions do not cover copying media.

The [NASA JPL ACC article](https://www.nasa.gov/centers-and-facilities/jpl/seal-takes-ocean-heat-transport-data-to-new-depths/)
by the NASA Earth Science News team, dated December 4, 2019, supplies an
alternate approximate 21,000 km extent retained outside the current-length
ranking. OSW links to this factual statement and does not copy article text or
imagery.

## Horizon Marine Loop Current eddy register

The candidate named-eddy inventory includes names and dates attributed to
the [Horizon Marine Loop Current Eddies register](https://www.horizonmarine.com/loop-current-eddies).
The live page bears a 2026 Woods Hole Group, Inc. copyright notice. The
candidate exports 96 name/date records from this compilation, even though it
does not copy the page HTML or charts. It does not claim permission to
republish the register. Compilation reuse terms remain unresolved before
public repository publication or dataset deposition.

## Published Kraken, Thor, Ursa, Cameron, and Darwin observations

The candidate links brief factual observations and figure windows for Kraken
from Beron-Vera et al. (2018), [*Scientific Reports* 8, 11275](https://www.nature.com/articles/s41598-018-29582-5),
DOI 10.1038/s41598-018-29582-5, and for Thor and Ursa from Johnson Exley et
al. (2022), [*Frontiers in Marine Science* 9, 1049645](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645/full),
DOI 10.3389/fmars.2022.1049645. It also records dated Thor and Ursa event
statements from Thoppil et al. (2025), [*Progress in Oceanography* 237,
103529](https://repository.library.noaa.gov/view/noaa/71031), DOI
10.1016/j.pocean.2025.103529. The NOAA repository lists that article under
CC BY 4.0; the other publishers state CC BY 4.0 and CC BY terms, respectively.
OSW does not reproduce their maps or eddy boundary
geometry. It adapts red pixels from Kraken Figure 2 into three dated,
georeferenced location envelopes and traces the 29 May closed blue SSH contour
as a dated footprint proxy. Both analyses include calibration sensitivity under
the article's CC BY 4.0 license. This is an OSW figure analysis, credited to the
authors and linked to the original figure; the source image is not packaged.
The names, dates, and derived footprint do not establish a NASA movie identity,
whole-ring lifetime footprint, or whole-eddy OSW state containment. The contour
crosses the approximate CAMR–CARB boundary in the nominal mapping; the CARB
intersection varies with figure axis calibration.

The Cameron and Darwin observation records cite Kolodziejczyk, Ochoa,
Candela, and Sheinbaum (2012), [*Journal of Geophysical Research: Oceans*
117, C09014](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2012JC007890),
DOI 10.1029/2012JC007890. The paper combines mooring measurements and
altimetry, and explicitly credits those two ring names to Horizon Marine.
OSW uses brief factual paraphrases, dated observations, approximate diameters,
and Cameron's source-reported center near mooring A. No text, figure, table,
contour, or altimetry field from the article is copied. Its mooring proximity
statements do not establish whole-ring state containment, initial separation
dates, or independent name origins. No article reuse license is asserted.

## NOAA Marine Weather Information Guide

Some named-current records cite the NOAA Voluntary Observing Ship Program's
[July 2017 Marine Weather Information Guide](https://www.vos.noaa.gov/docs/marine_info_guide.pdf).
The PDF's title, date, and source-file digest are recorded in the motion source
registry. Its embedded map credits and any item-specific terms still need
review before republishing that map.

## NOAA CoastWatch MUNSTER eddy products

The candidate's 12 dated eddy samples derive from NOAA CoastWatch's
[experimental MUNSTER v1.0 product](https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html).
The product page's data-credit phrases are: “Data courtesy of NOAA”,
“Sentinel Data courtesy of Copernicus Program”, and “Generated using AVISO+
Products”. It also asks users to acknowledge NOAA CoastWatch and cite the
product when a product citation is available.
OSW records the source NetCDF URLs and response digests and exports 92,891
dated detections carrying provider center coordinates and eddy properties,
alongside OSW state relations. The original NetCDF files are absent, but those
extracted values still require a redistribution decision. Product-specific
and upstream data terms remain under review for public repository publication
or dataset deposition. The [AVISO+ license, Issue 20](https://www.aviso.altimetry.fr/fileadmin/documents/data/License_Aviso.pdf)
allows sharing adapted material with attribution and restricts bulk platform
redistribution of unmodified AVISO products; NOAA's page does not identify the
particular AVISO+ input or show that this license governs the MUNSTER output.

## NOAA-hosted research papers

Some current names and measurements link to journal articles hosted on NOAA
PMEL pages. Hosting does not change the articles' own terms. In particular,
the [Johnson et al. tropical Pacific current article](https://www.pmel.noaa.gov/pubs/outstand/john2337/zonal_velocity.shtml)
states a 2002 Elsevier copyright and forbids further electronic distribution.
OSW's candidate links to the source and keeps source-scoped factual assertions;
it does not redistribute the article text, figures, or PDF.

## Other linked factual sources in the motion almanac

Eighty-one external source rows support attributed names, measurements, and
short paraphrased findings. The candidate packages those OSW assertions and
source links, without the papers' prose, tables, figures, files, or geometry.
The [current-use decision](plans/ocean-motion-linked-facts-use-decision.md)
records this narrow scope and the source-by-source review ledger. Sixty-four have
DOI metadata; the other seventeen have source-page, agency, or institutional
citations. The original WHOI KESS home URL returned HTTP 410
on 2026-09-30, so the atlas points to WHOI's surviving project summary.
This decision does not grant a license to redistribute the underlying works
or extract a provider's full compilation.

## Ranked current-length source passages

The ranked 1,200 km Florida Current segment and 2,500 km Gulf Stream proper
estimate cite Tomczak and Godfrey's [*Regional Oceanography: An Introduction*,
Chapter 14](https://incois.gov.in/Tutor/regoc/pdffiles/colour/single/14P-Atlantic.pdf),
PDF version 1.2 (September 2002), printed page 239. The source PDF digest is
recorded in the motion source registry. OSW links the chapter and retains the
two short numerical facts with their distinct segment scopes; it does not
reproduce the chapter, figures, or tables.

The 3,000 km California Current System estimate cites the [2004 PICES North
Pacific Ecosystem Status Report, California Current section](https://meetings.pices.int/publications/special-publications/NPESR/2004/File_10_pp_177_192.pdf),
page 179. OSW records only the approximate regional extent and source link;
it does not reproduce the report, tables, or figures. The number is not a
measured California Current core axis.

The 3,000 km Kuroshio estimate cites Yang et al. (2015), [*Oceanography*
28(4), 74–83](https://tos.org/oceanography/article/mean-structure-and-fluctuations-of-the-kuroshio-east-of-taiwan-from-in-situ),
DOI 10.5670/oceanog.2015.83. The publisher identifies the article as
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and requires
citation, a license link, and notice of changes when its
content is reused. OSW records a short factual route estimate and links to
the article; it does not copy article prose, figures, or data. The estimate
is introductory geography rather than a traced path.

## Atlantic named-current latitude sections

Caínzos et al. (2023), [*Ocean Science* 19, 1009–1045](https://os.copernicus.org/articles/19/1009/2023/),
DOI 10.5194/os-19-1009-2023, identifies the Benguela Current system,
Brazil Current, and deep western boundary current at multiple latitude
sections. The article is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
OSW computes conservative geographic separation floors from those section
latitudes and labels them as unranked; the article supplies no measured
along-current centerline for these floors. No article figure or model field is
reproduced.

## Northern Current source

Berta et al. (2018), [*Ocean Science* 14, 689–710](https://os.copernicus.org/articles/14/689/2018/),
DOI 10.5194/os-14-689-2018, identifies Northern Current as a name for the
Liguro-Provençal-Catalan flow and describes its regional reach. The publisher
states CC BY 4.0. OSW uses these source-linked facts to distinguish the broad
current from its Ligurian regional segment and to record a December 2011 local
study off Toulon; no paper figure or measured path is reproduced.

## ORCA 2009 named-current sections

[Comas-Rodríguez et al. (2011)](https://doi.org/10.1029/2011JC007129)
reports the Azores Current and Azores Countercurrent along a meridional
24.5°W section. [Pérez-Hernández et al. (2013)](https://doi.org/10.1002/jgrc.20227)
reports Canary and Portugal Current bands along the 29°N and 37°N sections.
The motion candidate records factual section bounds, survey windows, and
citations; it does not redistribute paper text, figures, or PDFs. Reuse
rights for the articles remain source-specific review items.

## Independent names for three ocean currents

The Caribbean Current name is supported by the Caribbean Fishery Management
Council and NOAA Fisheries (2013), Regulatory Amendment 4 for the reef fish
fishery of Puerto Rico and the U.S. Virgin Islands, section 3.1.2, p. 13:
https://repository.library.noaa.gov/view/noaa/4711/noaa_4711_DS1.pdf.
The South Atlantic Current name is supported by Boebel, Schmid, and Zenk
(1999), Kinematic elements of Antarctic Intermediate Water in the western
South Atlantic, Deep-Sea Research II 46, 355-392, section 3.5:
https://www.aoml.noaa.gov/phod/docs/boebel_et_al1999a.pdf.
The South Indian Current name is supported by Grand et al. (2015), Dust
deposition in the eastern Indian Ocean: The ocean perspective from Antarctica
to the Bay of Bengal, Global Biogeochemical Cycles 29, 357-374, section 3.2,
https://doi.org/10.1002/2014GB004898.
OSW records these factual names and short paraphrased context with source
links. No source prose, figures, tracks, geometry, or PDFs are packaged under
these source rows. These citations establish naming evidence; ArcGIS arrow
measurements retain their separate pending source review.

## GEBCO 2026

The paired bathymetry and Type Identifier values derive from the GEBCO_2026
Grid, DOI `10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa`. GEBCO makes its grid
available in the public domain and requests acknowledgement. It combines
heterogeneous source types, carries vertical-datum limitations, and must not be
used for navigation. Exact OPeNDAP requests and response hashes are recorded in
the source receipt; the full responses are not redistributed in this stage.

### Alaska Coastal Current source-defined extent

Stabeno et al. (2016), *Long-term observations of Alaska Coastal Current in
the northern Gulf of Alaska*, Deep-Sea Research Part II 132, 24-40,
[DOI](https://doi.org/10.1016/j.dsr2.2015.12.016), supplies the name and
approximate Seward-to-Samalga extent and the separately dated 1989 Shelikof
Sea Valley local-observation interval. OSW exports those linked facts and its
own scope notes and editorial navigation points. No manuscript prose, PDF,
figure, drifter tracks, mooring data, or source geometry is redistributed.
The [NOAA repository](https://repository.library.noaa.gov/view/noaa/13254)
provides access and states that copyright-owner reuse rights still apply.
This narrow use decision grants no license to the article or underlying data.

### Antarctic Slope Current extent

Thompson et al. (2018), *The Antarctic Slope Current in a Changing Climate*,
[doi:10.1029/2018RG000624](https://doi.org/10.1029/2018RG000624), supplies the
source-scoped name, distinctions, and ranked system-span estimate. OSW
retains factual metadata and links with continuity limits. No article prose,
figure, PDF, source geometry, tables, or fields are redistributed. Regional
regime definitions are admitted as a cited vocabulary without state or observed feature assignments.

### Kuroshio local mooring observation facts

Wang, F., Zhang, L., Feng, J., Wang, Q., and Hu, D. (2025),
[Atypical seasonal variability of the Kuroshio Current in 2018](https://doi.org/10.3389/fmars.2025.1675413),
Frontiers in Marine Science 12:1675413. Copyright 2025 the authors; publisher
notice links [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
OSW paraphrases the study interval, three instrument positions and depth
limitations, and computes a point-to-approximate-state lookup. This local
CHIN observation does not establish a current axis or whole-current footprint.
No figure, instrument series or model field is reproduced.

The Kraken Figure 2 adaptation also exports the nominal 29 May 2013 closed
SSH-contour proxy coordinates and source-pixel calibration metadata. This
is an OSW digitization, not author-supplied boundary data. The original
figure and PDF are not packaged. Attribution remains Beron-Vera et al. (2018),
Scientific Reports 8:11275, DOI 10.1038/s41598-018-29582-5, copyright the
authors, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The figure supplies no explicit geodetic datum; scientific interpretation
and whole-ring containment remain unverified.


### Malvinas Current conference extent

Spadone, A., Provost, C., and Sennechael, N. (2009), *Origins of low-frequency
variations in the Malvinas Current volume transport since 1992*, Geophysical
Research Abstracts 11, EGU2009-12242, EGU General Assembly 2009.
[Source abstract](https://meetingorganizer.copernicus.org/EGU2009/EGU2009-12242.pdf).
The source marks copyright Author(s) 2009. OSW packages only the attributed
2,000 km fact, citation, and paraphrased scope/limits; no open license is
inferred and the PDF, prose, figures and source geometry are not copied.
Conference provenance is displayed beside the estimate. Individual scientific
claim review is pending; the source supplies no reference-path geometry.


### North Cape Northern-branch profile study

Morozov et al. (2017), Physical Oceanography 2, 36–50,
doi:10.22449/1573-160X-2017-2-36-50. The
[primary PDF](https://physical-oceanography.ru/repository/issues/2017/02/05/20170205.pdf)
marks copyright 2017 authors and Physical Oceanography. OSW retains attributed
numerical facts, formula parameters and paraphrased scope; source prose, figures,
PDF and velocity profiles are not redistributed. No open license or independent
scientific approval is inferred.


### Atlantic EUC island interaction and section context

Napolitano et al. (2022), doi:10.1029/2021JC017999, primary IRD-hosted PDF states
Creative Commons Attribution license, copyright authors. Hormann and Brandt
(2007), doi:10.1029/2006JC003931, supplies western section context. OSW retains
attributed facts and paraphrased scope with original citations; neither figures,
model fields nor observed current profiles are redistributed in this candidate.
New reference-route vertices are explicitly OSW editorial choices.


## NOAA/AOML AB0505 LADCP data

Original final ASCII profile products and quality assessment were obtained
from NOAA/AOML's public Western Boundary Time Series data service. Provider
headers attribute NOAA/OAR/AOML/PhOD and UM/RSMAS/MPO, WBTS/MOCHA/RAPID,
R/V Knorr, May 2005. Original headers and bytes are retained in
`research/source-data/noaa-wbts-ab0505/`; source URLs/checksums are in its
acquisition manifest. Provider cautions and processing metadata are preserved.
Access/citation: https://www.aoml.noaa.gov/phod/wbts/data.php;
Meinen et al. (2019), doi:10.1029/2018JC014836 for regional scientific context.
No blanket license claim is made for every contributing institution's product.
The section plot and display page are OSW transformations; they are labeled
as local observations and a derived diagnostic, not NOAA-approved measurements.

## Pacific NECC archived OSCAR subset — 2026-10-04

ESR OSCAR third-degree version 2017.0 zonal-velocity subset is served by NOAA
PIFSC ERDDAP dataset `yearly_336c_0b32_9cd3`. Provider metadata and its free-use/
redistribution license are preserved in
`research/source-data/oscar-necc-2013-140w/metadata.json`. The source acquisition
contains the exact public query and checksums. OSW monthly profiles, boundary
calculations and visual figure are derived artifacts; the figure is not a copy
of a publication image. Cite ESR/OSCAR and Bonjean and Lagerloef (2002) as recorded
by the archive. This saved third-degree subset is distinct from current OSCAR
version 2.0 products and the Hsin and Qiu (2012) one-degree climatology.

