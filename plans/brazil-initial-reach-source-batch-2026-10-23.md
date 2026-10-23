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
of this v2 report. Source-stage local verification is complete; Linux actual
reproduction and canonical atlas delivery remain pending batch gates.

## Remaining delivery and measurement gaps

- Add this separate regional-reach record and provenance links to the existing
  query/card collection without changing existing whole-current measurements.
- Include the frozen product in explicit source-original reproduction coverage;
  do not silently skip an unavailable original or claim an unrun check passed.
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
