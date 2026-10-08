---
skill: roles-check
topic: query-source-documents
date: 2026-10-07
roles_used: [CURRENT, SOUNDER, BEACON, HARBOR, KEEL, LOGBOOK]
p1_count: 0
p2_count: 4
p2_remaining: 1
p3_count: 14
verdict: APPROVED-WITH-CONDITIONS
---

# Checked source query UI review

Artifact: local source-query panel, registered browser check and feature protocol on `codex/query-source-documents`, based on `0d3c3ea`. Six relevant installed role definitions are applied. CHART is excluded because this component adds no map, geometry, palette or scientific plot; ORBIT is outside its terrestrial scope. This is an internal review, not independent scientific peer review.

## CURRENT

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Source queries return evidence records without admitting new current dimensions, geometry or membership. | P3 | Engine scope and source receipt | Retain source status and scoped field names. |
| 2 | Regional monthly branching values remain signed latitude values in the original source record. | P3 | Independent monthly source oracle | Do not reinterpret these as width or annual ranges. |
| 3 | Imported records and proposed working-record updates retain their existing workflow. | P3 | Separate source panel and unchanged query controller | Keep source editing and scientific admission as explicit future workflows. |

## SOUNDER

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Every catalog option comes from the checked Rust metadata. | P3 | 67 options compared against the compiled catalog | Avoid a separately maintained browser source list. |
| 2 | Original row pointers and source hashes survive sorting and pagination. | P3 | Independent last-month addresses and SHA-256 check | Keep file-scoped provenance on exports. |
| 3 | Result-page downloads initially lacked the request needed to reproduce filtering; the request is now included. | P2 resolved | Request/result export regression | Retain exact request and result as a pair. |

## BEACON

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | The source workspace is discoverable on Ask the atlas and loads only when opened. | P3 | Native details control and request inventory test | Keep the source panel in the existing query experience. |
| 2 | Advanced constraints remain visible when using basic controls. | P3 | Active-filter text and preservation check | Avoid hidden filters that change apparent coverage. |
| 3 | Record previews explicitly announce their character limit and provide complete downloads. | P3 | Text renderer and record export check | Keep truncated previews distinct from complete records. |

## HARBOR

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Long checksums initially overflowed the mobile layout; paragraph wrapping fixed the observed failure. | P2 resolved | 320-pixel browser check and mobile screenshot | Retain narrow-screen coverage. |
| 2 | Source controls have 44-pixel minimum heights and status updates use a polite live region. | P3 | Scoped CSS and markup | Keep focus and errors within the source workspace. |
| 3 | Scrollable record previews now have keyboard focus and visible focus outlines. | P2 resolved | Preview tabindex, aria label and scoped focus style | Verify the focused preview before publication. |

## KEEL

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | Queries use the existing checked worker, with no direct-source fallback. | P3 | Lazy request test and unavailable gzip interception | Keep checksum validation in Rust/worker loading. |
| 2 | The new browser check covers source/native/WASM agreement, paging, downloads, restoration and isolated errors. | P3 | Registered test_rust_source_query_browser.py | Complete final focused checks and full remote CI. |
| 3 | This candidate adds a 48th browser check; earlier 47-check mainline receipts remain historical. | P3 | Required runner and feature plan | Do not reuse earlier CI as proof of this new UI. |

## LOGBOOK

| # | Finding | Severity | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | This local candidate follows pending PR #28; no new mainline status is claimed. | P3 | Git branch and feature plan | Keep dependency and publication status explicit. |
| 2 | Rust, checked source data and frozen exports remain byte-for-byte unchanged by this panel. | P3 | Working-tree paths and manifest checks | Publish only the UI, registered test and review records. |
| 3 | Required remote publication gates are still pending for this candidate. | P2 publication condition | Local working tree without a PR | Create the reviewed candidate and pass protected-main CI before mainline publication. |

## Synthesis and amendments

Six roles, zero P1 blockers, three addressed P2 implementation findings, one pending P2 publication condition and fourteen P3 notes. KEEL and LOGBOOK agree that the earlier engine/data validation and current UI checks are separate from the required full remote gate.

1. Preserve exact source addresses, checksums and both request/result in downloads.
2. Fix observed mobile overflow and keyboard access to scrollable record previews.
3. Complete the final browser checks, publish the reviewed candidate and wait for the 48-script remote gate. Keep the dependency chain explicit.

## Validation scope

The dedicated source browser check passed lazy loading, all catalog options, independent monthly records, native/WASM parity, original source pointers, numeric filters/sort, pagination, exports, shared restoration, mobile reflow, invalid request recovery and failure isolation. The result-export refinement also passed. Final focus and existing collection regression checks remain underway at this receipt. The 771-test offline suite and 37 Rust unit-test receipt belong to the unchanged engine/data baseline in the preceding chart candidate; no new full-suite result is claimed here.

## Final local verification amendment

The final dedicated browser check passed, including keyboard focus on record previews and exact request/result downloads. The existing all-collection UI check passed all 38 collections, both ends of each collection, record inspection, canonical source equality and 240 object map marks. All 37 JavaScript modules and all 14 page assignments passed. The mobile source panel was visually inspected at 320 pixels; long addresses and checksums wrap within the page. Engine manifest hashes are unchanged and all match. Rust, source data and frozen export files are unchanged by this feature. The sole open P2 condition is protected-main publication with the complete 48-check remote gate.
