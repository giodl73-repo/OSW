# OSW public preview readiness

Updated 2026-11-08.

OSW has enough material for a useful public research preview. The next milestone is a coherent, source-screened atlas people can explore and question. Completing every current depth and volume estimate is a separate research milestone.

## What visitors can explore

The working atlas connects ocean states, named currents and eddies, route maps, measurement evidence, NASA animation navigation, and a Rust and WebAssembly query interface. Route conventions, source-reported measurements, model results, and dated observations have different meanings and must retain their labels.

The [home page](index.html) introduces the project and its three exploration routes without loading the research store. The [home page browser review](research/public-preview-ui-review-v4.json) passed its desktop and narrow-layout checks, primary entrance checks, and loaded-image check. It does not load the research runtime. Continue to the [current and eddy atlas](almanac/reference-routes.html#route-atlas), the [coverage dashboard](almanac/dashboard.html), and the [query workbench](almanac/query.html). These are working review surfaces; their presence here does not establish approval for public deployment.

## Research status

The latest depth research inventory is [version 57](research/current-depth-reference-inventory-v57.json), with 941 depth references across a catalog of 111 current identities. References include different metrics and scopes; this is not 941 complete current profiles. The catalog has 101 scoped identities and 10 unassessed family or system entries. Eddy work has size references for 102 entries; that does not establish dated footprints or verified state containment for every eddy.

Whole-route current depth profiles and physical volume estimates remain unfinished. Core depth, instrument depth, water-mass thickness, transport integration limits, and the bottom of a current cannot be substituted for one another. Length, width, and depth need compatible locations, dates, and definitions before they support physical volume estimates.

The public pages, compiled query data, research inventories, and generated release packages use different pinned snapshots. The latest research counts must not be advertised as already available throughout the interface. The [depth readiness protocol](plans/current-depth-readiness-protocol-v3.md) and its older pinned snapshot remain separate from the latest inventory.

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
