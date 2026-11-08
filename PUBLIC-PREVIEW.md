# OSW public research preview

Updated 2026-11-08. Version **2026.11.1-preview** is public:

**[Open Ocean States of the World](https://osw-ocean-atlas-preview-202611.sweet-jam-8851.chatgpt.site)**

Start with the Agulhas example, select a current on the global map, then follow its card into the evidence explorer. The introduction explains currents, eddies, map symbols, and the limits of source-reported measurements. Names can be reached by keyboard and selector as well as hover. Shareable views, direct record links, and scoped JSON downloads preserve the selected evidence context.

## Included in this edition

- 111 current identities, with routes or qualified locators and source-scoped length, width, and depth evidence.
- 941 current depth references: 937 in metres and four in dbar. These are references with differing definitions, places, and periods, not 941 complete current profiles.
- 40 retained named-eddy records, plus a separate collection of 331 eddy evidence references including all 203 size references. Evidence counts are not counts of distinct physical eddies; unresolved registry joins are withheld.
- 70 NASA-hosted navigation links and 56 OSW state names, with qualified state-association lookup. A point or reference-curve intersection does not establish whole-feature containment. NASA animations show modeled motion and do not establish NASA identification or endorsement of a named feature.
- Evidence search, metric and unit filters, pagination, source links, methods, and downloads from the same screened edition. Comparisons sort stated scalar values; ranges are not silently replaced by midpoints.

The map uses the existing Rust cartographic export. This lightweight public edition avoids loading the large research store. The advanced WebAssembly research workbench remains a separate repository surface; the preview does not claim complete parity with it.

## What was verified

The [bundle review](research/public-preview-bundle-review-v1.json) records cloud run `42533045767`, source `21ac7584326013f89f413d27e0d9a9b211026e8c`: 180 selected files, 2,323,964 bytes, and 56 checked local links. Functional checks passed the home entrance, map/cards, current queries, all 331 eddy references, NASA navigation, state choices, deep links, share links, scoped download, keyboard return and focus transfer, reduced-motion context, and a narrow mobile layout. No browser errors, failed HTTP requests, or unreviewed data requests were recorded. Screenshots were inspected.

The [asset-scope review](research/preview-asset-scope-review-v1.json) binds the screened dataset and field-specific source-use decisions. Held provider identities, raw datasets, provider geometry, and unresolved structured registry metadata are excluded. Source citations and method supplements remain distinguishable; an admission-method citation is not an independent measurement. No new scientific measurements were calculated for publication.

The [final repository role review](signals/roles/check/public-preview-release-roles-check-2026-11-08.md) records the eight installed lenses and resolves the earlier source-context, selected-package, and deployment gates. This is internal review, not external scientific peer review.

The [publication receipt](research/public-preview-publication-v1.json) records successful deployment, Site version 1, public access, source commit, and artifact custody. All served application and scientific asset bytes match the reviewed bundle; only the edition's publication-status and URL metadata changed for hosting. The existing GitHub Pages site, repository main branch, and older citation release remain unchanged. The new edition has its own author, version, source, and URL metadata in `preview-edition.json` on the public site.

## Continuing research and feedback

This is a research preview, not a complete census or a set of whole-current depth profiles. Core depth, instrument depth, water-mass thickness, transport integration limits, and current bottom are different quantities. Pressure remains in dbar. Compatible locations, periods, and definitions are needed before length, width, and depth can support physical volume estimates. Seasonal profiles and physical volumes remain research work.

The browser evidence covers Chromium desktop and an emulated narrow viewport. A new reader's comprehension, screen-reader speech, and every browser are not established by those checks. A useful next feedback session is to ask someone to find a familiar current, explain what its route and number mean, follow a citation, and return to the world map. Record their own words and hesitation without coaching.

Older candidate reports and failed or narrower checks remain frozen historical evidence. Their pending status and smaller inventories describe those snapshots, not this deployed edition. Protected Earthdata acquisition and additional eddy identity work can continue separately.

Suggested description to accompany the link:

> Ocean States of the World is an evolving atlas of currents and eddies. Explore the map, open a current card, and follow source-backed measurements into their evidence. Estimates retain their geographic, temporal, and methodological limits; missing evidence stays visible.
