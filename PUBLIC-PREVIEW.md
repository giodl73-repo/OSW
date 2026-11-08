# OSW public preview readiness

Updated 2026-11-08.

OSW has enough material for a useful public research preview. The next milestone is a coherent, source-screened atlas people can explore and question. Completing every current depth and volume estimate is a separate research milestone.

## What visitors can explore

The working atlas connects ocean states, named currents and eddies, route maps, measurement evidence, NASA animation navigation, and a Rust and WebAssembly query interface. Route conventions, source-reported measurements, model results, and dated observations have different meanings and must retain their labels.

The [home page](index.html) introduces the project and its three exploration routes without loading the research store. The [home page browser review](research/public-preview-ui-review-v4.json) passed its desktop and narrow-layout checks, primary entrance checks, and loaded-image check. It does not load the research runtime. Continue to the [fast current and eddy map](almanac/public-map.html), the [coverage dashboard](almanac/dashboard.html), and the [query workbench](almanac/query.html). These are working review surfaces; their presence here does not establish approval for public deployment.

## Fast map review

The [fast map browser review](research/public-map-browser-review-v1.json) passed current lookup, map-to-card zoom, return to the world, keyboard Home, focus transfer, browser Back, reload, empty-search recovery, and desktop and narrow-layout checks. All 111 current names, 136 named-eddy records, and four dated detections remain in this internal candidate. The first map and Agulhas card rendered in about 0.26 seconds on the cloud runner's loopback server; this is not a public-network performance result.

The first map inventory is 975,737 bytes, with individual evidence records loaded on selection. The [Rust display export](research/public-display-build-v1.json) reuses the existing projection code and preserves the pinned identity inventory. It copies source-scoped rows without recomputing measurements. The [installed package](research/public-display-package-installation-v1.json) has exact export receipts. The large query store and detailed research cards remain separate; this review does not certify their startup performance or every advanced plot.

Source-use review remains open for the candidate's complete source set. This faster map is not authorization to publish its pending provider records. Scientific and temporal scope labels, public source screening, and the selected deployment bundle still govern release.

The [first-visitor usability review](research/public-map-usability-review-v1.json), at source `499f60f070aa811788efa74b139d15f20290a313`, also passed the first-visit guide, plain-language map explanation, expandable evidence, inline source links, copy-view action, and announced search recovery. Desktop and narrow-card screenshots were inspected. No browser errors, failed HTTP requests, or large research-store requests were recorded. Later small text amendments clarify source-record counts, frozen-snapshot status, stored identity scope, and map projection; they do not add measurements. The [seven-role review](signals/roles/check/public-map-first-visitor-roles-check-2026-11-08.md) still requires the selected source-screened public package before publication. Browser task success does not establish a new visitor's comprehension or screen-reader speech output.

## Research status

The latest depth research inventory is [version 57](research/current-depth-reference-inventory-v57.json), with 941 depth references across a catalog of 111 current identities. References include different metrics and scopes; this is not 941 complete current profiles. The catalog has 101 scoped identities and 10 unassessed family or system entries. Eddy work has size references for 102 entries; that does not establish dated footprints or verified state containment for every eddy.

Whole-route current depth profiles and physical volume estimates remain unfinished. Core depth, instrument depth, water-mass thickness, transport integration limits, and the bottom of a current cannot be substituted for one another. Length, width, and depth need compatible locations, dates, and definitions before they support physical volume estimates.

The public pages, compiled query data, research inventories, and generated release packages use different pinned snapshots. The latest research counts must not be advertised as already available throughout the interface. The [depth readiness protocol](plans/current-depth-readiness-protocol-v3.md) and its older pinned snapshot remain separate from the latest inventory.

### Integrated data candidate

The [separate preview projection](research/preview-data-projection-v1.json) was built successfully in cloud run `42527107981` from frozen descriptors, without new provider requests or measurement calculations. It preserves all 111 current identities and joins all 941 admitted depth references, retaining 937 metre references and four pressure references in dbar. It also retains 331 eddy evidence references, including all 203 size references, in a source-reference collection separate from canonical named-eddy identities. These are evidence counts, not counts of complete profiles or distinct physical eddies.

The candidate has 40 retained named-eddy records; 96 held registry-only identities and four dated provider detections are excluded. This is not a return to only the older 40-record almanac: the separately retained source references preserve the newer size work without asserting unverified registry joins. The projection also carries qualified state-association metadata and the existing 70 NASA navigation tiles and 56 OSW state names. Their presence does not establish verified eddy containment or NASA identification of a named feature.

The installed UTF-8 transport files match the exact cloud artifact receipts. Records use small, individually checked compressed envelopes; the entire encoded data package is 1,478,906 bytes. The new loader and depth-card integration are prepared behind the explicit `atlas-edition=preview-candidate` review parameter. They have a JavaScript syntax check, but no browser verification yet; the default map snapshot is unchanged.

This candidate is **not approved for public publication**. Its original projection recorded 30 contexts with no extracted bibliography. A [separate supplement](almanac/preview-review-v1/contexts.json) now supplies a pinned OSW admission-method citation for each, plus retained primary bibliographic metadata where available. Method citations explain admission; they are not independent measurements and do not replace primary attribution on the references. The cards are prepared to display both kinds of citation. The [225 added source-use decisions](almanac/preview-review-v1/source-use.json) define narrow factual-use scopes, with original source assets, raw datasets, provider geometry, and unresolved registry joins excluded.

The [actual asset-scope screen](research/preview-asset-scope-review-v1.json) passed in cloud run `42529706452`. It found no unreviewed or held provider URLs and no prohibited asset fields after the scoped edits. One observed-center state assertion and structured registry names, dates, and identifiers were withheld. Numerical reference values and source-association/eligibility flags remain unchanged. The [309 deeper-link decisions](almanac/preview-review-v1/link-use.json) distinguish citation metadata, NASA navigation, policy references, and scoped factual references; they grant no rights to underlying assets or datasets.

The resulting data is retained separately in `almanac/preview-data-screened-v1/`, with exact cloud file receipts. The explicit `atlas-edition=preview-screened` review option is prepared to use it. No new browser validation is claimed for that adapter. The browser-tested default map and the screened integrated candidate must not be confused. A selected public bundle, matching query/download/NASA/state surfaces, and final verification remain required.

Earthdata access is needed for the planned protected three-dimensional data work. The [secure access setup](plans/earthdata-cloud-access-setup-v1.md) enables that research to proceed; it is not a prerequisite for sharing a properly scoped preview.

## Publication boundary

The [rights-screened package](almanac/release/v0.1.0-rights-screened-preview/README.md) is an internal review artifact with narrower coverage than the full research candidate. It is not yet a released dataset. The retained [publication boundary audit](almanac/release/publication-boundary-audit.json) identifies pending source uses and references from the working site into research material. Its findings describe that audit snapshot, not a fresh audit of every newer page.

Publish an explicitly selected site bundle whose assets, data, and links have been reconciled with source-use decisions. A screened download does not make every page in the surrounding repository ready for public hosting. Keep the source histories and research receipts available for review without treating them as a deployable site bundle.

## First visitor review

The [screened atlas introduction](site-review/ocean-motion-screened/index.html) offers three starting points: find a current or eddy, follow a NASA movie link, or compare reported lengths. It explains ocean states, map points, missing values, and model animations before asking visitors to interpret the directory.

Before sharing the preview with a new visitor, check whether they can do the following without coaching:

- Explain what OSW is and distinguish a current from an eddy after reading the introduction.
- Find a familiar current, open its record, and return to exploration.
- Explain what a map point and a length estimate do and do not represent.
- Follow a regional NASA movie link and understand that it shows modeled motion.
- Use the same route on a phone and with a keyboard, without relying on hover.

Cloud browser checks confirm that the screened atlas supports current search, a shareable record address, reload, and focus transfer. The [focused mobile review](research/public-preview-ui-review-v3.json) passed after the directory was changed to stacked records with larger link targets. The checked introduction and directory belong to the older screened snapshot; these results do not certify the main atlas or the new home page. The main atlas, dashboard, and query workbench did not render their content within the tested startup windows and need further loading work. See the [retained UI diagnostic](research/public-preview-ui-review-v2.json).

Record a first visitor's own words and where they hesitate; that observed session remains open. A shareable hosted URL must refer to the selected and validated preview bundle, not a local development address or the unreviewed full research site.

## Remaining launch work

1. Select the pages and data snapshot for the preview. Record the included assets and source-use decisions, withholding unresolved provider material from the public bundle.
2. Reconcile the chosen snapshot with the map, cards, dashboard, query interface, downloads, and displayed counts. Give visitors one clear entry route and visible evidence labels.
3. Check the selected bundle on desktop and mobile, including keyboard navigation, focus, hover alternatives, reduced motion, deep links, and loading failures. Run the applicable cloud validation against that exact candidate.
4. Review the concrete bundle, then set the public target and version and update citation and release metadata together. The [publication checklist](PUBLICATION-CHECKLIST.md) records the remaining release gate.

These are release tasks. Further depth acquisition, seasonal profiles, compatible volume estimates, and additional eddy geometry can continue after a preview launches.

## Suggested public description

> Ocean States of the World is an evolving atlas of ocean currents, eddies, and ocean states. Explore mapped routes and source-backed measurements, inspect how each estimate was made, and see where evidence is still missing. Routes and measurements retain their geographic, temporal, and methodological limits.

## Snapshot history

Earlier release READMEs and review records describe their own snapshots. Their smaller counts and earlier branch names are historical context, not the current research inventory. Preserve those records rather than rewriting frozen exports to appear current. This readiness note does not certify a deployment, source-use clearance, browser review, or a published dataset.
