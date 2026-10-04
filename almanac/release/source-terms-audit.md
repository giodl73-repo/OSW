# Ocean motion candidate: source terms audit

Status: partial review, 2026-09-30. This is a release gate record, not a
blanket license for the package. The generated source registry marks each
external source as pending until its specific use is reviewed. Reviewed
decisions are pinned in `research/ocean-motion-source-use-reviews.json`;
citation and media reuse can remain separate open items.
The generated [review queue](v0.1.0/source-review-queue.csv) ranks all 102 used
external sources by packaged rows they support and lists the affected entity
IDs. For NOAA MUNSTER files it counts both the observation-set row and every
derived dated detection row; the 12 files collectively support 92,891
detections. The Horizon register remains the largest compiled name-and-date
source, supporting 96 named-eddy entities and 192 direct package rows.
The queue now records a material-use class and whether provider record values
are packaged. Sixteen pending external source rows carry provider values:
the Horizon name/date compilation, 12 NOAA MUNSTER daily eddy-identification
files' extracted center/property values, the NAVO front coordinates, NAVO/NCEI
FREDDIES polygons, and a NOAA LSA packed velocity subset. The original source
files and page HTML are absent; absence of those files does not remove the
redistribution question. Eighty-five used sources have explicit current-use decisions as of
2026-09-30: one Marine Regions Gazetteer crosswalk source, ten NASA SVS links
and descriptions, and 74 narrowly reviewed linked-factual sources (including
research papers, the NASA JPL ACC variant, and NOAA descriptions). Seventeen used external
sources retain rights questions: the 16 provider-value rows and the credited
cartographic service. The ten used SVS links have item-credit and page
citations recorded; any future movie-file redistribution still requires
item-specific review.
No original external video, paper, full raw NetCDF file, gazetteer, or
arrow polygon is packaged. The candidate nevertheless carries 96 named-eddy
records from Horizon's compilation, 92,891 NOAA MUNSTER eddy detections with
source centers and properties, the dated NAVO Gulf Stream frontal bulletin's
510 reported wall coordinates, four NAVO/NCEI FREDDIES polygons, and a packed
regional subset of NOAA LSA geostrophic velocities. Each family needs a
specific redistribution decision before external deposition. The candidate
also exports OSW-derived joins and geometric decisions whose source terms
still need review.

| Source family | Material in candidate | Primary policy or source | Review result |
| --- | --- | --- | --- |
| NASA Scientific Visualization Studio | Ten source URLs for release descriptions, transcript or media-group anchors, and links to videos; movie files are not copied into the package | [SVS help](https://svs.gsfc.nasa.gov/help/), [NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) | Each used SVS URL has a reviewed current-use decision for links and factual descriptions, plus a page citation using its exact item credit. NASA says SVS content is generally public domain unless noted; NASA requests acknowledgement and prohibits implied endorsement. Future media redistribution requires item-specific review. |
| NASA JPL news article | An unranked, source-reported approximate ACC extent of 21,000 km | [NASA article](https://www.nasa.gov/centers-and-facilities/jpl/seal-takes-ocean-heat-transport-data-to-new-depths/) | The title, December 2019 date, writing credit, and factual length variant were reviewed. No article text or imagery is packaged. |
| NOAA National Ocean Service and VOS guide | Names, short paraphrased definitions, factual map context, and source links | [NOS use guidance](https://oceanservice.noaa.gov/about/faq.html), [current glossary](https://www.tidesandcurrents.noaa.gov/glossary.html), [July 2017 VOS guide](https://www.vos.noaa.gov/docs/marine_info_guide.pdf) | Both used glossary URL forms and the NOAA guide have reviewed current-use decisions for facts and links. NOAA requests credit. The guide PDF and its embedded ocean-current map are not packaged; map-asset reuse requires separate review. |
| NOAA CoastWatch MUNSTER | Twelve dated NetCDF eddy-identification files and 92,891 exported center/property detections with OSW state joins | [NOAA experimental eddy products](https://coastwatch.noaa.gov/cwn/products/experimental-eddy-products.html) | NOAA labels MUNSTER v1.0 experimental and supplies three data-credit phrases for NOAA, Sentinel/Copernicus, and AVISO+. The source registry records each file's date, product identity, and derived detection count. The extracted provider values are redistribution, even though the original NetCDF files are absent; verify applicable upstream terms before deposition. |
| NOAA CoastWatch LSA geostrophic currents | Packed 2026-09-25 regional velocity subset, one unranked partial Gulf Stream streamline, and two approximate state intersections | [NOAA LSA product page](https://coastwatch.noaa.gov/cwn/products/sea-level-anomaly-and-geostrophic-currents-multi-mission-global-optimal-interpolation.html) | The product is experimental; NOAA asks for LSA and CoastWatch acknowledgment. Regional subset redistribution, upstream contributor terms, and preferred citation remain pending; see the [decision packet](../../plans/ocean-motion-noaa-lsa-geostrophic-reuse-decision.md). |
| NAVO frontal bulletin via NOAA OPC | Reported Gulf Stream north/south wall coordinates dated 2026-09-28, with eight approximate OSW state front intersections | [NOAA OPC Gulf Stream ASCII Data](https://ocean.weather.gov/gulf_stream_text.php), [NWS disclaimer](https://www.weather.gov/disclaimer/) | The page credits Naval Oceanographic Office and describes an infrared-satellite frontal analysis. NWS states page information is generally public domain unless noted, but the provider-specific status of NAVO coordinates has not been established. The candidate redistributes them as dated lines; confirm their terms and credit both providers before deposition. A front is not the full current footprint. |
| NAVO FREDDIES via NOAA NCEI | Four operational eddy polygons dated 2026-09-25 and four state containment observations | [NCEI coastal surface analysis products](https://www.ncei.noaa.gov/products/coastal-surface-analysis-products) | The ZIP says approved for public release but supplies neither a `.prj` nor an item-level reuse license. Polygon redistribution, datum, credit, and code lifetime remain pending; see the [decision packet](../../plans/ocean-motion-navo-freddies-reuse-decision.md). |
| NOAA-hosted papers and other government archives | Source-scoped claims and links | [NOAA digital media guidance](https://sos.noaa.gov/copyright/), [linked-facts decision](../../plans/ocean-motion-linked-facts-use-decision.md) | Agency hosting does not establish that a paper or embedded figure is public domain. The present linked factual uses are reviewed narrowly; article text and figures still need separate terms before copying. |
| Marine Regions | Gazetteer name context and links | [Marine Regions license, terms, and citation](https://www.marineregions.org/disclaimer.php) | The provider states CC BY terms for Marine Regions products, requests a current marineregions.org link, and gives a database citation. The package stores source-linked name context; provider geometry is not redistributed. |
| Horizon Marine Loop Current register | 96 named labels and source event dates in the OSW eddy inventory | [Horizon public register](https://www.horizonmarine.com/loop-current-eddies) | The live page bears a 2026 Woods Hole Group, Inc. copyright notice. The compilation is materially carried into OSW records despite the source page HTML being absent. Redistribution/database terms were not found in this review. Keep the name/date compilation in candidate status pending a terms decision. |
| Cartographic ocean-current arrows | Source arrow IDs, source-labelled intersections, and an illustrated-span proxy; raw polygons are not in the package | [ArcGIS layer 11 description and credits](https://services3.arcgis.com/o98K21Ga5N91Ugjw/ArcGIS/rest/services/Hurricane%20TracksAA/FeatureServer/11) | The layer describes four drawing widths per arrow and credits NOAA, National Weather Service, US Army, and Maps.com. It does not state a reuse license in the reviewed layer metadata. Keep raw polygon redistribution out of this candidate and retain the source link. |
| Research papers, textbook chapters, and theses | Short source-scoped numerical claims, names, attribution, and links; no source PDFs copied into the release package | URLs in `v0.1.0/sources.json`, source ledgers, and the [linked-facts decision](../../plans/ocean-motion-linked-facts-use-decision.md) | Seventy-four linked factual-source rows have current-use decisions, without licensing source text or figures. Fifty-nine have DOI metadata; fifteen have source-page, agency, or institutional citations. The California system estimate cites the PICES review, the Kuroshio estimate cites the CC BY 4.0 *Oceanography* article, and the Florida/Gulf Stream segment estimates cite Tomczak and Godfrey's Chapter 14. NOAA PMEL's hosted Johnson et al. (2002) page forbids further electronic distribution of the Elsevier article; the candidate stores links and factual name decisions, not article text. |

The [Horizon reuse decision packet](../../plans/ocean-motion-horizon-reuse-decision.md)
and [alternative-source audit](../../plans/ocean-motion-horizon-alternative-source-audit.md)
set out the exact public-site and dataset-deposition scope to resolve with the
provider, plus the rule for an explicitly partial release if that use is not
available. No provider inquiry has been sent.
The [MUNSTER detection packet](../../plans/ocean-motion-munster-reuse-decision.md)
and [NAVO front packet](../../plans/ocean-motion-navo-front-reuse-decision.md)
likewise scope the extracted data values and fallback release if redistribution
is not confirmed.
The [provider inquiry drafts](../../plans/ocean-motion-provider-outreach-drafts.md)
state the exact proposed public website, repository, and dataset uses; none
has been sent.

The [AVISO+ license, Issue 20](https://www.aviso.altimetry.fr/fileadmin/documents/data/License_Aviso.pdf)
permits sharing adapted material under attribution conditions while restricting
bulk distribution of original, unmodified AVISO products through an operational
platform. This is useful upstream context, but the NOAA product page does not
identify which AVISO+ inputs its MUNSTER output uses or prove which AVISO+
terms attach to those inputs. The 12 MUNSTER source rows therefore remain
pending for the current exported detection data. The package contains no
original AVISO product or raw MUNSTER NetCDF file.

The [2018 Northern Current paper](https://os.copernicus.org/articles/14/689/2018/os-14-689-2018.html)
is marked CC BY 4.0 on its publisher page. Its title, DOI, date, and credit are
pinned in the source registry. This item-level finding does not set terms for
other papers in the source set.
The [2018 Kraken article](https://www.nature.com/articles/s41598-018-29582-5)
states CC BY 4.0, and the [2022 Thor/Ursa article](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645/full)
states CC BY. The Kraken source has a separately attributed figure-derived
candidate and sensitivity audit under its CC BY 4.0 terms; the original figure
is not packaged. The Thor/Ursa use records linked factual summaries. These
decisions apply only to the material recorded in the source-use registry.

All 63 DOI-bearing used-source records now have a matched response digest from
[Crossref's REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).
The 62 DOI-bearing linked-factual sources have author, title, publisher, and
publication year metadata; several source URLs are repository or publisher
pages rather than DOI redirects.
The pinned receipt is `research/ocean-motion-crossref-metadata.json`; the
normal package build reads that file offline. Crossref bibliographic metadata
and any deposited license links do not themselves settle the rights to
republish source material. Bibliographic coverage does not resolve
source-specific terms.
The seven NASA SVS release pages have pinned title, release date, update date,
credits, and API response digests from the [official SVS page API](https://svs.gsfc.nasa.gov/help/).
The receipt is `research/ocean-motion-nasa-svs-metadata.json`. NASA's general
SVS reuse guidance still directs item-specific media exceptions to be checked.
Sixty source URL records now have verified source-page, PDF, or DOI registry titles and
available publisher or credit metadata in `research/ocean-motion-source-metadata-overrides.json`, including
the Horizon register, two NASA releases, NOAA's July 2017 *Marine Weather Information Guide*, both NOAA glossary URLs, and Marine
Regions' Gazetteer service and the credited ArcGIS arrow layer. The layer's
publisher is deliberately left unknown. Together with NASA titles pinned from
the SVS API, three additional SVS media-group references, and 12 date-labelled
NOAA MUNSTER files, and the two newly pinned NAVO FREDDIES and NOAA LSA source
records, all 102 of the 102 used external sources now have a title in the
generated review queue.

The package includes copies of OSW's own source ledgers and generated join
tables. NASA video files, research PDFs, and the published arrow layer's raw
polygons are not packaged. This limits redistribution exposure but does not
settle compilation rights or citation requirements for every source.

Marine Regions' current database citation is: Flanders Marine Institute
(2026), *MarineRegions.org*, available at
<https://www.marineregions.org/>, consulted 2026-09-29. The provider asks
users not to mirror its products elsewhere; this release candidate contains
only OSW's crosswalk and source links, not a copy of its gazetteer or geometry.

Before deposition: resolve the 17 remaining rights questions among 102 used
external source rows (out of 149 source registry rows), finish open citation
reviews, and record any provider terms, title, publisher, date/version,
preferred citation, and review date; resolve
the Horizon register and credited cartographic layer explicitly. Then update
`THIRD-PARTY-NOTICES.md` and the dataset citation record.
