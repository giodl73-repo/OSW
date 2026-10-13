# Agulhas ring radius evidence batch

2026-10-08. Editorial original-source extraction; independent scientific and canonical admission pending.

## Source and coverage

Guerra, Mill and Paiva (2022), *Observing the spread of Agulhas Leakage into the Western South Atlantic by tracking mode waters within ocean rings*, Frontiers in Marine Science 9:958733, DOI 10.3389/fmars.2022.958733. The unchanged publisher PDF has 16,034,257 bytes and SHA-256 `150734e346134f4a252d7f76b46229a9f30dfd1e5bdaa2f53f039dcaae84dff1`. Its copyright notice states CC BY; the publisher's Copyright section links to CC BY 4.0. Acquisition attribution and license link accompany the tracked original. Printed figures on pages 11, 12 and 14 and Table 1 on page 16 were visually inspected alongside the methods and body text.

| Existing named ring | Source section | Radius evidence (km) |
|---|---|---|
| Ana | May 2005 | 67 |
| Eliza | February 2009 | Table 88; caption 93; unresolved |
| Eliza | July 2009 | 95 |
| Eliza | January section | Table 93 in January 2010; caption 88 in January 2019; unresolved |
| Jeannette | May 2013 | 74 |
| Jeannette | November 2015 | 72 |

These are six section slots containing eleven raw source claims, with four consistent radii, two radius conflicts and one year conflict. Figure 10's panel label and body/table support 2010, but the original caption disagreement remains explicit. A normalized month and radius for that January slot remain null. Figure panel days are context, not exact radius observation dates.

## Measurement convention and remaining gaps

Preserve the source-described altimetric area-equivalent radius and diagnostic model radius L. Preserve the source's maximum radial velocity terminology. Table 1's thermocline fit RMSE is not radius uncertainty; XBT section depth and deployment spacing do not supply radius geometry. No preferred table or caption value, midpoint, uncertainty interval or corrected date is selected.

No contour coordinates, occupied polygon, full-depth extent, diameter, area, radius ranking, annual extrema, monthly interpolation, seasonal animation or NASA individual identification is added. Existing locator geometry and state joins are unchanged. Jeannette's merger-dependent identity remains in the geography ledger. The single named closed footprint candidate remains Kraken.

## Data and presentation

The deterministic extraction binds original PDF, acquisition, protocol and generator hashes. Geography records retain the complete per-owner evidence and audit hash. Atlas and source-index builders validate that binding. Compiled Rust rejects coherently rewritten audit claims and admission flags; the source index pins original document bytes in its compiled catalog.

The main index and mapped atlas cards show separate section rows. Filled points indicate consistent radii, hollow points conflicting source claims. The chart has no connecting time-series line or interval caps. Text lists every source claim and locator, and a direct query preserves nulls and conflicts.

The dashboard and object query expose `radius_evidence`: four existing owners have this capability, including Astrid's two differently defined model scales. Eight scoped records across these owners include two unresolved slots; this count is not eight resolved or comparable radius observations. Current width, length, reference-route and seasonal coverage is unchanged: 91 scoped width records for 47 owners, 45 unassessed width owners, 11 published-length owners and 89 length gaps.

## Reproduction and publication gates

When intentionally regenerating the audit, refresh geography's per-owner copies and audit hash before downstream builds. Rebuild in order: `python analysis/build_motion_dashboard.py`, `python analysis/build_rust_query_bundle.py`, `python analysis/build_almanac_index_bundle.py`, `python analysis/build_rust_query_engine.py`. The index contains 100 original JSON documents. The licensed PDF is tracked, so the existing ignored-paper hydrator remains unchanged.

Default validation: `python -m pytest -q`. Registered affected browser check: `python analysis/test_rust_index_eddies_browser.py`, covering source records, native/WASM parity, index and atlas charts, source navigation, mobile labels, dashboard lights and compiled scope rejection. Shared query check: `python analysis/test_rust_query_browser.py`. Publication remains subject to protected remote checks; draft publication does not establish mainline coverage.

Confirmed locally: 838 Python tests and 918 subtests passed in 301.17 seconds; 40 Rust tests and both engine builds passed. The registered eddy browser and shared query browser passed. The 320 px Eliza diagram was visually inspected, all 100 indexed original JSON bytes and engine receipts verified, and prior current width/length/seasonal sources and eddy geography fields compared unchanged. All 45 JavaScript modules pass syntax checks; all 14 pages retain validation assignments.

The previous Alaska stack's remote push run reached the browser gate and failed a stale `88` width-inventory count in `test_black_sea_regional_width_browser.py`; it is replaced here by exact inventory/query identity and total comparison. Its sibling pull-request run failed the existing Qiu/Chen original-source download timeout. Neither failure is described as a passing mainline gate, and source checksums remain strict.

The repaired regional-width browser check also passes locally; its inventory comparison paginates so future data additions do not reintroduce a fixed-count ceiling.
