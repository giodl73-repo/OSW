---
skill: roles-check
topic: rust-svg-export
date: 2026-10-04
roles_used: [CURRENT, SOUNDER, CHART, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 0
p3_count: 17
verdict: APPROVED-WITH-CONDITIONS
---

# Rust standalone map export review

Artifact: shared Rust SVG renderer, native exclusive-file export, WASM download,
scene metadata, export example and verification. Installed role definitions were
inspected in this conversation. CURRENT covers measurement scope, SOUNDER receipts,
CHART rendering, BEACON wording, HARBOR access, KEEL safety/parity and LOGBOOK status.
ORBIT is inapplicable. Internal role lenses do not constitute scientific admission.

## CURRENT

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Display coordinates could be treated as scientific dimensions. | P3 | Caption | Explicit display-only scope; no exported length/width computation. |
| 2 | A locator can look like an occupied footprint. | P3 | Legend | Keep hollow locators and dashed gateways separate from polygons. |
| 3 | Dated geometry is not an annual current extent. | P3 | Receipt | Retain dates, roles and notes; source scope remains in metadata and titles. |

## SOUNDER

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | A detached image can lose its query and source identity. | P2 | Metadata | Embed bundle hash, query, full features and omissions. Verified against actual source hash and scene. Addressed. |
| 2 | Hashes do not establish official admission. | P3 | Contract | Identify this as a portable display receipt, not a signed release. |
| 3 | The compiled background also needs reproducible provenance. | P3 | Build | Include original OSW ground SVG hash in engine manifest. |

## CHART

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Pagination could truncate the map inventory. | P2 | Scene | Export Rust's pre-pagination scene; tests confirm 100/240 objects at limit 1. Addressed. |
| 2 | Context geometry could look like a state match. | P3 | State | Preserve dimmed context and selected-state outline; NADR scene checked. |
| 3 | Exporting global extent differs from browser zoom. | P3 | Framing | Document global query export. Regional framing remains future work. |

## BEACON

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Map counts can hide unsupported or missing geography. | P3 | Caption | Report mapped/unmapped and omitted counts; retain omission reasons. |
| 2 | Names should appear on interaction. | P3 | Titles | Use SVG titles/focus labels without permanent current labels. |
| 3 | Download failures must not be reported as success. | P3 | UI | Surface worker/renderer errors and restore download control. |

## HARBOR

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Export needs a discoverable keyboard control. | P3 | Button | Native labeled button in map section, unavailable for collections without scenes. |
| 2 | Static SVG is not the interactive query inspector. | P3 | Access | Provide title, description, keyboard-focusable marks and preserved metadata; no inspector behavior is claimed. |
| 3 | Global legends are small on narrow displays. | P3 | Usability | Vector export supports zoom; human accessibility and regional print layout remain open. |

## KEEL

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Source strings could inject SVG markup. | P2 | Serialization | XML-escape data and strip invalid XML controls; injection unit test passes. Trusted background is repository-controlled. Addressed. |
| 2 | Browser and native output could diverge. | P3 | Parity | Downloaded SVG bytes equal native output for currents, all objects and NADR queries. |
| 3 | External images would break portable output. | P3 | Resources | Inline the original background; XML checks reject scripts/images/hrefs. |

## LOGBOOK

| # | Finding | Severity | Section | Recommendation |
|---|---|---|---|---|
| 1 | Export could overwrite an existing deliverable. | P2 | CLI | Exclusively create and sync a new file; existing output remains byte-identical after rejection. Addressed. |
| 2 | Invalid queries could leave misleading output. | P3 | Failure | Render/validate before file creation; non-object query creates no file. |
| 3 | SVG support does not complete raster or seasonal export. | P3 | Status | Update README/contract; leave PNG, regional and animated export explicit follow-ons. |

## Synthesis and amendments

Seven roles, 21 findings: zero P1, four addressed P2 and seventeen P3. Approved
with conditions for local display export. Top finding: the map must retain the
complete query scene and its source scope. CURRENT/SOUNDER agree on provenance;
CHART/KEEL agree on one shared renderer and full-inventory parity.

1. Embed the exact query, source hash, features and omission receipt.
2. Render the full Rust scene, OSW ground and state context through one native/WASM
   serializer, escaping source values and retaining interaction-only names.
3. Create new native outputs exclusively, reject invalid maps before writing and
   verify portable browser rendering plus actual downloaded byte parity.

## Evidence and conditions

Fifteen Rust tests pass. Actual export tests confirm native/WASM byte identity,
100/240 complete scenes with one table row, state highlights, valid XML, query/hash
receipt, no external resources, unchanged existing outputs and non-map rejection.
The rendered global-current screenshot was viewed. Current maps preserve the
source's coarse geography and evidence limitations. This is a local software
review; domain admission, human accessibility and full public release remain open.
