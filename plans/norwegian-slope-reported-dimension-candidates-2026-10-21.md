# Norwegian slope-current dimension candidates

Continue on `codex/current-measurement-gaps`, draft PR #83. No new PR or main merge.

## Evidence and admission

Orvik and Skagseth (2003), doi:10.1029/2003GL017932, supplies a previously
uncatalogued approximate branch-length report and a local annual-mean-flow
width description. The two extracted quantities are retained in
`research/norwegian-atlantic-slope-orvik-2003-dimension-candidates.json`.

Access is publisher-indexed prose, not a downloaded original. Direct publisher
access returned HTTP 403. Record no original checksum or redistribution
license. Acquire and review the full source before promoting these candidates.
The width cites the existing 2001 study and is not independent support.

These records belong to the proposed Norwegian Atlantic Slope Current.
Canonical `norwegian` remains ambiguous; no canonical measurement, identity,
ranking, route, footprint or seasonal range changes. No new canonical current
is counted. Publication date and transport-series dates are not width dates.

## Presentation and query

The existing proposed slope-current card displays two annotated numeric
callouts, with different geographic supports and provisional status. It links
to the paper and to a Rust source query returning both measurement objects.
The visual is a dimension summary, without a geographic line, combined area,
seasonal curve or implied uncertainty interval. Text details preserve the
meaning at narrow widths and for screen readers.

The audit is registered in the existing lossless source index and atlas source
receipts. Existing frozen proposal data and scientific calculation definitions
are preserved. Generic source-query access exposes these candidates without
adding them to the admitted measurement or proposed-width collections.

## Verification scope

Regenerate the source index, Rust query bundle and engine manifest; run the
engine's native/WASM build and Rust tests. Exercise the actual proposed card,
source query, keyboard details and 320px reflow. Compare all existing collections
against the parent commit. A candidate report is progress in evidence capture,
not closure of canonical measurement or original-acquisition gaps.

The last complete local Python baseline belongs to commit `774e466`, not this
batch. Current CI and focused verification must be reported by actual result.

## Executed checks

The rebuilt engine passed 81 Rust tests, locked offline native and WASM
builds, and native atlas receipt validation. The actual browser passed exact
two-row source querying, image loading, keyboard details and 320px card reflow,
with no page errors. All 46 existing typed collections compare exactly to
`e39daea`; canonical admissions remain zero. The rebuilt query bundle is
96,727,873 bytes. The original acquisition and canonical admission gates above
remain open.

Initial atlas validation rejected the unregistered new source receipt. The
Rust receipt validator was extended to compare the complete candidate report
against the compiled source definition, including its admission exclusions.
The subsequent native atlas validation passed. Initial browser launch found
no Playwright-managed browser; rerunning with the installed Chrome passed.
Two coherently rehashed corruptions were rejected: changing the reported
length to 4,000 km, and enabling length-rank eligibility. Both rebuilt the
source receipt and manifest hash, so rejection was by source/scope validation.
