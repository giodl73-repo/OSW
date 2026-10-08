# Checked source documents in the query workspace

Status: locally validated candidate on `codex/query-source-documents`, following the chart candidate in PR #28. Protected-main publication remains pending.

## Purpose and scope

Expose the checked source catalog through the existing Ask the atlas page. The imported collection workspace and its working-record workflow remain available. Source queries use the existing Rust `IndexStore::query` through the checked index worker. No source files are fetched as an unchecked browser fallback, and no Rust engine or scientific source changes are required by this UI candidate.

The source workspace loads only when opened or when restoring a source-query link. The catalog and its document choices come from validated Rust metadata, not a separately maintained list. The current candidate contains 67 source documents; the UI reports the loaded catalog count rather than hardcoding that number.

## Interaction contract

- Select a document, an array/object JSON Pointer, text and a page limit. The initial selection is the 100-current source inventory, 25 rows per page.
- Structured queries support the existing Rust filters, sort and pagination. Fields are relative to the row wrapper, such as `record.month`. Active advanced constraints remain visible and survive basic edits on the same source.
- Each returned row retains its original source pointer before filtering, sorting or pagination. File-scoped row addresses are not persistent identities or new scientific membership claims.
- Display the original source checksum, byte count and engine scope. Record previews are explicitly limited to 2,000 characters. Full records can be downloaded with provenance; result-page downloads contain both the exact request and its returned result.
- Preserve the imported query's `q` parameter when adding the source request in `source-q`. Restore source selection, filters, sort and page through shared links.
- Invalid requests clear stale source results, sharing and downloads, while keeping the source controls usable for recovery. A missing/invalid source corpus disables its controls and leaves the imported collection workspace usable.
- Render source text with textContent. Keep controls keyboard accessible, give status a polite live region, provide 44-pixel target heights and wrap long addresses/checksums at 320 pixels.

## Verification and publication

`analysis/test_rust_source_query_browser.py` is added to the required runner, making 48 browser checks for this candidate. It checks lazy loading, every catalog option, native/WASM equality, independent monthly values, stable original addresses, numeric filters, sorting and final-page bounds, both downloads, advanced-filter preservation, invalid/scalar pointers, invalid operators, error recovery, shared restoration, mobile reflow and failure isolation.

Run the dedicated check, the existing all-collection check, JavaScript syntax, page assignments and whitespace validation. The engine/source hashes must remain unchanged. Review through the relevant installed roles and pass the full required remote CI before publication. Existing mainline receipts for the earlier 47-check migration remain historical evidence for that commit, not validation of this new panel.

## Local receipt

2026-10-07: the dedicated source workspace check passed all its source/native/WASM, rendering, keyboard, pagination, export, sharing, mobile and isolated-failure assertions. The existing all-collection check passed all 38 collections and 240 map marks. All 37 almanac JavaScript modules, all 14 page assignments and whitespace checks passed. The mobile rendering was inspected. Every engine manifest checksum still matches; no engine/source/frozen-export change is present. Full remote CI for this UI candidate remains pending.
