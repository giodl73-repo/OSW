# Published regional reaches gap batch

Continue on `codex/current-measurement-gaps` and draft PR83. No main merge.
Batch compatible source facts before the next native/WASM and browser cycle.
One heavy local job at a time, BelowNormal on one logical CPU; numerical and
Cargo workers remain one. Full regression remains a separate final batch gate.

## Algerian Current: original-reviewed dated regional constraint

Arnone, Wiesenburg and Saunders (1990), DOI10.1029/JC095iC02p01587,
reports a near-coastal reach **over300km between Oran and Algiers** during
combined ship/satellite work1–22May1986. The ship-only cruise ends21May.
The nearby30km value is coast proximity, not current width.

The retained DTIC original is853466 bytes, provider MD5/SHA1 verified and
local SHA256 pinned. It has11 PDF pages including its cover; printed journal
pages1596–1597 are missing. The abstract on printed1587 and supporting results
on printed1590 were visually inspected. No full-paper review is asserted.
The original permits public release and states the paper is not subject to
US copyright; attribution and its incomplete state are retained.

Prospective method/source/test/protocol/preflight were frozen in commit
`c2adb97` before report execution. No distance calculation or digitization
was performed. First report/figure execution passed; exact read-only replay
also passed. Twenty-five synthetic checks and two independent original/product
checks passed. The SVG was rendered with PyMuPDF and visually inspected,
without starting Chromium. No layout collisions were observed at native size.

Products:

- `research/algerian-arnone-1990-reported-reach-v1.json`
- `figures/algerian-arnone-1990-reported-reach-v1.svg`
- Source custody in `research/source-data/arnone-algerian-1990/`.

Retain the strict `gt` comparator, absent upper endpoint and absent numerical
uncertainty. Whole-current centreline length, physical length lower bound,
width, annual/seasonal range, geometry and ranking eligibility stay null/false.
This fills a dated regional-reach evidence gap; it does not close the
whole-current measurement gap or change the canonical current count.

## Remaining delivery and source work

The report and diagram are ready for batched canonical query/card admission;
they have not yet been wired into the shipped WASM or atlas navigation.
Add regional-reach support as a distinct quantity rather than changing the
whole-current length ranking. Preserve all existing rows and source custody.
Register source documents, expose evidence links and verify the exact native
and WASM rows plus the rendered current card in the later serial delivery cycle.

The next source hunt checked Mindanao, Antilles, Alaska, Baffin, Guinea and
Ligurian candidates. No additional along-current length was admitted:
Antilles520 nautical miles refers to an offshore survey section; Mindanao80km
is an objective-mapping scale; Baffin1000km describes the bay; Guinea7600km
is regional coastline. Keep these exclusions when extending source coverage.
Other measurement, seasonal, eddy inventory and state-intersection gaps remain.
