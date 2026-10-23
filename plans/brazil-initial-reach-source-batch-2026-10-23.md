# Brazil Current: reviewed initial reach, source-stage batch

Continue on `codex/current-measurement-gaps` and the existing draft PR83.
No new PR and no main merge. Batch canonical admission with compatible
subsequent evidence; this source-stage change requires no Rust/WASM rebuild.

## Evidence and meaning

Tomczak and Godfrey describe an initial **1500 km** Brazil Current reach
beginning near10 degrees south, in chapter14, printed p244 / PDF page254.
The source is a textbook synthesis, not a new observation campaign. Numerical
uncertainty, observation dates, upstream longitude and downstream coordinates
are not supplied for this reach. Preserve the published round number without
adding a physical equality, inequality, confidence interval or inferred endpoint.

The chapter is PDF v1.2, September2002; the first printed edition is1994.
The source directory contains2005 because it serves another chapter's revision.
None of these dates establishes observation support. The following page's
separation discussion and dated front illustrations do not date or terminate
the1500 km reach. Selected pages254 and255 were visually reviewed; version
history was checked on PDF page2. Whole-book page completeness was not audited.

Reuse the exact36625246-byte,401-page retained original and acquisition receipt
in `research/source-data/tomczak-regional-2005/`.
Original SHA256: `35e36f9b834c9c31c2cee64abc36d0c687d71e3d388c2cf1c40bc026e613738b`.
The complete book remains ignored and locally retained; no new redistribution
license is asserted. Only attributed facts and a short passage are distributed.

## Prospective freeze and actual products

Producer, synthetic tests, source facts, protocol, preflight and line-ending
rules were frozen in **fee4925ffa6061e80f42ce7e1abecec709309da7** before the
actual report or SVG existed. The original is pinned through that preflight
and its existing acquisition receipt, rather than redistributed in Git.
Do not change these scientific inputs or outputs after their execution.

First actual generation passed; immediate read-only replay matched both files:

| Product | SHA256 |
|---|---|
| `research/brazil-tomczak-initial-reach-v2.json` | `47e7dba6a54d94afe5b3c700e445cfe8156236cc956ca094577a169ea4953b24` |
| `figures/brazil-tomczak-initial-reach-v2.svg` | `0b7a2088558132674a753d28335f3c3a5d314d6418539125110fee7deee39e22` |

The saved SVG was rendered with PyMuPDF and visually inspected. Text and
limits fit at native size, without observed collisions. Its line is a
schematic segment, not a geographic axis, recovered flow path or physical
length lower bound. This static render is not a mobile/browser validation.

Thirty-three prospective synthetic checks and two independent actual-original
and product checks passed. The independent checks verify the source number,
identity, approximate upstream context, chapter history, every frozen input,
both product hashes and the null/false non-admission fields.

## Local reproduction

With the retained original and pinned test dependencies installed:

```powershell
python -m pytest -q analysis/test_published_current_regional_reaches_v2.py analysis/test_published_current_regional_reaches_v2_admission.py
python analysis/published_current_regional_reaches_v2.py check
```

If the ignored original is absent, its existing checksum-enforcing acquisition
helper can be invoked explicitly, before running the original-dependent checks:

```powershell
python -c "from pathlib import Path; from analysis.acquire_local_paper_fixtures import acquire; acquire('tomczak-regional-2005', Path('research/source-data/tomczak-regional-2005'))"
```

The v2 synthetic suite is added to the existing offline conformance step and
requires no book download. The new actual-original checks also participate in
normal full pytest collection once the existing paper fixtures are present.
The40-target scientific replay driver has not yet been extended for this
ignored-original-dependent product. Do not call its existing CI result proof
of this v2 report. Source-stage local verification is complete; a separate
actual-original Linux replay subsequently passed as recorded below.
Canonical atlas delivery remains a pending batch gate.

## Remaining delivery and measurement gaps

- Add this separate regional-reach record and provenance links to the existing
  query/card collection without changing existing whole-current measurements.
- Preserve the separate verified source-original replay coverage below; do not
  silently skip an unavailable original or claim an unrun check passed.
- Validate native/WASM admission and mobile/keyboard/plain-text diagram access
  once for the compatible batch. Explain in the host UI that this source alone
  supplies no dimensions; independent section-width evidence remains separate.
- Whole-current length, physical width from this statement, seasonal ranges,
  current geometry, state intersections and ranking eligibility are not added.
  This does not close the Brazil whole-current length gap.
- Full Python regression remains an eventual separate final gate, not a
  per-source cycle. Existing remote source-acquisition failures remain separate
  unresolved evidence; do not claim the whole PR or program is validated.

Remote run40027773139 at the preceding delivery commit7a62ea1 passed
conformance, scientific reproduction and the NetCDF fixture job. Its offline
job120668162328 failed before the suite while fetching the Rotschi1972 original
from IRD (`010028590.pdf`), HTTP403. The atlas job was still running when
observed. These results do not cover the new Brazil source-stage products.

## Resource controls

Use one heavy local job, BelowNormal on one logical CPU; numerical and Cargo
workers stay one. No build/data/browser/regression overlap. Close a validation
browser before starting another phase. Native/WASM builds require a disk
preflight and at least2 GiB free under the current local resource policy.
The source-stage checks above use no browser and create only small products.

## Query preparation and systematic source-link finding

Prepared, not yet wired into the live builders:

- `analysis/brazil_regional_reach_query.py` and its exact
  `research/brazil-regional-reach-query-contract-v1.json` preserve the frozen
  report/SVG, prepare four records and three card links, and reject partial,
  duplicate, orphaned or count-inconsistent joins before mutation.
- The source is a scoped textbook excerpt, not another independent document.
  Its full-book SHA identifies the shared compilation. No redistribution,
  completeness, date or observation-class upgrade is made. The proposed host
  explanation distinguishes this source's limits from independent width data.
- `analysis/object_source_links.py` prepares a pure projection of registered
  owner/evidence references, including media, method and snapshot sources.
  Counts derive from those references, not supporting metadata dictionaries.
  Unregistered references and evidence for a different owner reject. All other
  object fields remain exact; input objects are not mutated.

The existing native store was queried read-only at repository commitb742a1c,
logical packet SHA256
`5ea582e44f8fd88d736d9ddf9c46fb52fad8e9c4cdca74f6130da10d979a2345`.
All242 object rows were returned;117 declared counts differed from their
source-ID lists. The captured audit is
`research/object-source-link-count-audit-2026-10-23.json`.
These are metadata mismatches, not117 missing physical currents or measurements.
The comparison alone does not establish complete source associations or
independent-observation counts.

For Brazil specifically, the native row declares5 linked sources but lists3.
The already registered `media:0016` reference to
`source:4f7441b953be4651` is absent from its query projection. That source is
the OSW-authored `ocean-current-nasa-crosswalk.json` media ledger; restoring its
reference does not turn it into an upstream NASA dataset. The focused actual
owner rehearsal gives4 registered references, not3 or5, and leaves every other
owner field exact. No canonical bundle is changed by that rehearsal.

All28 query/projection checks passed, alongside exact contract build/check.
The first inventory-audit request used limit1000, exceeding the existing
native API's documented-in-code maximum500; it failed and admitted no result.
The corrected limit500 request returned the complete242-row inventory. No
browser or compiler was launched for these checks.

The read-only delivery driver now combines frozen report/SVG replay, prepared
query-contract replay and all63 focused checks:

```powershell
python analysis/check_brazil_regional_reach_delivery.py
```

That command passed locally using the retained original, without a network
request. The optional `--acquire-original` flag explicitly hydrates the same
checksum-pinned book first. The isolated `regional-reach-source-replay` CI job
uses that flag and retains a result receipt and logs, never the full book.
It is an advisory source-availability/reproduction job; failure remains visible
in its receipt. It does not replace the required full offline suite or certify
canonical atlas admission. The separate40-target scientific driver still
excludes this product; its Linux coverage is provided by this isolated job.

### Verified Linux source replay

At commitc06271a12dc95254acf497e1ed5c6b96af8a449a,
[run40031761851, job120681459161](https://github.com/giodl73-repo/OSW/actions/runs/40031761851/job/120681459161)
passed. The retained artifact12534792648 was downloaded and its receipt/logs
inspected: Linux/Python3.13, explicit acquisition of the exact36625246-byte
original with the pinned SHA256, exact report/SVG hashes matching the table
above, exact prepared query-contract replay, and all63 focused checks passed.
The receipt explicitly leaves canonical admission unverified. This closes the
source-stage Linux reproduction condition, not the full offline suite, live
source-count correction, native/WASM admission or mobile/browser delivery.

Before canonical integration, fix the dashboard's source-list aliasing and
preserve all registered owned evidence references in query projection. Apply
the projection consistently to the entire object inventory, then perform the
Brazil four-record admission. Merely replacing5 with3 would conceal the missing
media reference. Rebuild dashboard/query/native/WASM together once disk
headroom permits; rerun the full count audit and the single batched browser
gate. The existing live counts remain incorrect until that delivery succeeds.
