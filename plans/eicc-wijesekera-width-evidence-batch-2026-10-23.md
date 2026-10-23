# East India Coastal Current: source width evidence batch

Same branch and existing draft PR83. Source-stage progress; canonical query,
native/WASM, current-card delivery and seasonal geographic widths remain open.

## Primary source and interpretation

The NRL-hosted original of Wijesekera et al.2015,
[doi:10.1002/2015JC010744](https://doi.org/10.1002/2015JC010744), was retained
unchanged locally:14987904bytes,17PDF pages,
SHA256`56fababd833dfb08ab4ff606c778eed1268ee9e0d7bc5bbfcc0635b93130b7fc`.
Its AGU All Rights Reserved notice remains applicable; the PDF is ignored,
and public NRL hosting is not treated as an OSW redistribution grant.
The acquisition receipt identifies the accepted-article pagination and selected
reviewed pages. Retention of the whole paper does not assert a complete review.

| Statement | Support | Time and location |
|---|---|---|
| About100km | Section3.2 shipboard survey description | Inbound T24,23-24December2013, approximately5.25N; explicit21m description. |
| Approximately200km | Section3.2 observational synthesis | Westward turn south of Sri Lanka, November-December2013 narrative; exact width-sample days unspecified. |
|250km | Section4 combined observation/model discussion | Broader south-and-west scope; exact support window and width layer unspecified. |

These are source statements, not three new independent observational samples.
Keep the broader250km number visible without turning200-250km into an error
interval or100-250km into an annual width range. The300km northward flow east
of EICC is a different current. Outbound T18 only clipped the eastern edge;
it does not establish another100km sample. Transect bounds, drifter averaging
boxes, velocity contours and transport layers are not width edges/layers.

## Frozen method and actual products

Commit`b7f3dba` froze the new producer,28 prospective synthetic checks,
protocol, source facts, acquisition receipt and eight pinned inputs before
the actual report or diagram existed. Do not edit those executed files.
Existing WICC facts, direction calendars, identity review and prior physical
measurements were not changed.

First generation and immediate read-only replay passed with exact bytes:

| Product | SHA256 |
|---|---|
| `research/eicc-wijesekera-2015-width-evidence-v1.json` | `4a452eeafa4c95a3afafac470bb6858819d748b81b1a4bb43219c8737175479b` |
| `figures/eicc-wijesekera-2015-width-evidence-v1.svg` | `63616a738d10e181afc4b04f33b9b082c9be2f6cdc44bc9d9a16f6298c37055e` |

The saved SVG was rendered with PyMuPDF and inspected. All three markers,
method/date labels and scope qualifications were legible without collisions.
PyMuPDF omitted the SVG hyperlink's citation text in its raster preview;
the actual SVG contains that linked text, independently checked as XML.
Browser source-link rendering, keyboard/mobile access and canonical hosting
remain unverified. No browser was started to resolve this during disk pressure.

Local checks:

```powershell
python -m pytest -q analysis/test_reported_current_width_evidence_v1.py analysis/test_eicc_width_evidence_admission.py
python analysis/reported_current_width_evidence_v1.py check
```

The original must be present and match its receipt. Do not skip this guard or
substitute abstract support when replaying in a fresh checkout.

`analysis/check_eicc_width_evidence_delivery.py` checks the frozen products
and all31 source checks. Its default mode uses the local original without
network access; `--acquire-original` explicitly hydrates that single pinned
paper through the existing acquisition helper. The full original-fixture list
also includes this paper, preserving strict full-suite acquisition requirements.
CI runs the EICC replay sequentially after Brazil in the existing advisory
source-replay job and retains only receipts/logs. Linux execution of this new
step is not yet verified; this setup is not a full-regression pass.

The local replay driver passed with explicit acquisition requested, validating
the already-retained original without downloading it again:14987904bytes,
the pinned digest, exact report/SVG and31passed checks, no skips. Receipt:
`.pytest_cache/eicc-width-source-replay/result.json`. This local pass does not
establish that the NRL download is reachable from Linux CI.

## Required delivery gates

1. Admit the separately reviewed EICC identity without silently changing the
   existing inter-basin Monsoon Current. Source-stage widths do not admit it.
2. Review each statement's collection/admission status independently. Keep
   combined discussion evidence separate from shipboard widths and retain
   missing cutoff, edge coordinates, errors and contextual dates as unknown.
3. Batch compatible evidence into canonical query/card/native/WASM delivery,
   with the inventory-wide source-reference corrections and pending Brazil
   and Indian current evidence. Preserve all older records and exact products.
4. Verify source links, accessible equivalent text, mobile/keyboard display,
   native/WASM parity and non-promotion to annual widths or geographic buffers.
5. Obtain independent multi-season width support, whole-current lengths,
   geometry and state joins. These three statements do not close those gaps.

Resource sequence: acquisition, selected source review, prospective checks,
freeze, source generation/check, native SVG inspection, independent checks.
One logical CPU BelowNormal, worker1, no local build/browser overlap. Native/
WASM builds stay held until the existing free-disk preflight passes.
