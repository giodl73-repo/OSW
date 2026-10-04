# Loop Current named-eddy alternative-source audit

Status: source search, 2026-09-30. This does not change the rights decision for
the Horizon register or authorize a full named-event export.

## Question

Can an independently reusable source restore the 96 Horizon-derived names and
dates excluded from the rights-screened atlas?

| Source | What it supports | Limit for the OSW export |
| --- | --- | --- |
| [NOAA NOS eddy explainer](https://oceanservice.noaa.gov/facts/eddy.html) | NOAA identifies Horizon Marine as the U.S. naming organization and independently mentions Eddy Franklin. | It is an explanation, not a complete event register or date table. It also confirms that the naming authority is Horizon. |
| [Chassignet, BOEM OCS Study 2025-008, Table 4](https://www.govinfo.gov/content/pkg/GOVPUB-I-0db9388401649f9f0178e811ec527482/pdf/GOVPUB-I-0db9388401649f9f0178e811ec527482.pdf) | The table mentions Poseidon, Galileo, Hadal, Icarus, Jumbo, and Franklin in sample station/frontal-analysis intervals. | Station intervals are not each eddy's separation or dissipation date. The report says Woods Hole Group frontal analyses are a primary source for tracking named eddies, so the table is not an independent replacement for the Horizon event compilation. |
| [Kraken observational paper](https://www.nature.com/articles/s41598-018-29582-5) and [Thor/Ursa event paper](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2022.1049645/full) | Three already recorded named events have paper-specific observation windows in `research/named-loop-eddy-published-observations.json`. | The windows are study periods, not a substitute for the Horizon event register or its 96 names and dates. The current canonical entity IDs and primary names still descend from that register. |
| [GOMED dataset record](https://zenodo.org/records/3978804) | An independent drifter-derived Gulf eddy dataset exists. | Its files are access restricted; the record prohibits third-party sharing and limits use to noncommercial academia. Its tracked eddies are not the Horizon named-event register. |

The BOEM cover identifies this copy as OCS Study **2025-008** (February 2025),
while its report-availability paragraph points to a differently numbered BOEM
PDF path. Cite the cover identifier and this exact govinfo URL until the
publisher reconciles the metadata. No PDF bytes or figures are copied here.

## Decision for this candidate

No searched source supplies a complete, independently licensed equivalent to
the 96-name Horizon event compilation. Keep those records in the full research
candidate and excluded from the screened atlas. Do not relabel the BOEM
station intervals as separation dates or treat a drifter detection ID as a
Horizon name. Continue the scoped provider inquiry in
`plans/ocean-motion-provider-outreach-drafts.md`; any affirmative reply must
identify the exact fields and publication destinations it covers.

The paper-specific Kraken, Thor, and Ursa observations may support future
source-scoped *observation* records independently; the papers do not establish
that the names originated independently of Horizon. The current release graph does not
yet separate their published identities from the Horizon-derived primary
records. Re-sourcing a subset requires new IDs or an explicit provenance
migration and a re-run of claim and rights screening.
