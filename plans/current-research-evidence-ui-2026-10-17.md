# Current research evidence in the atlas and query UI

## Purpose

Expose the retained Indian countercurrent EOF experiment and REDSOX section calculation through the shared Rust/WASM store, current cards, seasonal pages and query charts. Continue on `codex/current-measurement-gaps` and draft PR 83.

## Scientific contract

- The Indian experiment concerns statistical patterns in two native OSCAR columns over 1995–2016. It does not independently establish a named-current association, physical boundaries or width. Missing northern coverage remains explicit.
- REDSOX's roughly 6 km result is a local half-peak southward-component span on 18 February 2001, 40–80 m above bottom, from a separately described follow-up. Its primary 20–60 m result remains unresolved. Conditional cast-10 results cannot replace it.
- Summer support is unresolved. Missing support does not mean zero width or an absent current. Neither study supplies annual extrema or whole-current width.
- Preserve the declaration-history qualification: three winter cast-10 tail rows were incidentally exposed before the calculation rules were declared. No fully blinded preregistration is claimed.
- Preserve original ASCII/CTD/alternate-format distinctions. Sample locations do not become a current axis or a physical footprint.

## Implementation

1. A generated, checksum-bound registry describes two compact evidence scenes and their 17 retained research documents. Index those documents and the registry in the source inspector.
2. Append two diagnostics to the existing collection. Bind each to its current object. Keep the other 43 collections, all 38 earlier diagnostics and all map features equal to the parent.
3. Validate the registry, research records, scientific dependencies and owner links in native Rust and WASM. Reject changed scientific claims and attempted width promotion.
4. Return the same scenes in atlas and seasonal snapshots and diagnostics query results. A shared semantic HTML renderer provides the summary, expandable figure, methods, accessible table, source links and record inspector.
5. Preserve old source-review charts and support a mixed diagnostics result containing both kinds of evidence.

## Verification and release

- Regenerate: `python analysis/current_research_evidence.py`, then the motion dashboard, source index, query bundle and Rust engine builders.
- Focused scientific/source checks: the four existing EOF/REDSOX modules plus `analysis/test_current_research_evidence.py`.
- Actual UI: `python analysis/test_current_research_evidence_browser.py`. Use the documented local test server and installed Playwright browser. The shared runner includes this check.
- Compatibility: existing source-review browser, all 45 collection queries and all 100 current cards/149 retained width records.
- Broad gate: `python -m pytest analysis -q` from a clean candidate checkout. Record its actual terminal result separately from focused checks and earlier baseline passes.
- Publish to the existing draft PR. Do not merge main without authorization. A source/provider CI outage is not permission to weaken byte pins or to claim a green remote gate.

## Counts and remaining work

Expected candidate: 296 indexed documents, 45 collections and 40 diagnostics. The 149 scoped width records, 79 owners with scoped evidence, 25 series, 271 width samples and 75 reference routes remain unchanged. These are research and presentation additions; they do not close the unresolved physical measurement gaps.
