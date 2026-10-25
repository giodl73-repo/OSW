# Published contour statistics and separation-event query rules v1

## Scope

The first application is the already reviewed Manta et al. (2023) Loop Current
source transcription. Preserve its two method-specific means and temporal
standard deviations, and twelve explicitly listed final-separation days.
Records enter distinct scalar evidence collections. They do not create a
current identity, eddy identity, observed path or physical-width measurement.

## Projection

1. Verify the exact source-preparation document, its five file hashes and its
   actual visual-review result before projection. Preserve source-local IDs.
2. `current_reported_contour_length_summaries` retains mean length, temporal SD,
   gates, period, product, statistic, method and exact source pointer. A mean of
   daily connecting-contour lengths is not a length of a mean axis. Unknown
   uncertainty, annual extrema and geometry stay null. Ranking stays false.
3. `current_reported_separation_events` retains the reported day and source
   final-separation convention, detector and subset coverage. Do not convert a
   final-separation day into an initial-detachment/birth day or assign midnight,
   UTC, an eddy name, geographic position, lifetime or track. Keep the two
   November 2017 events separate. Twelve listed events are not the full 48.
4. Bind both collections to the existing `current:loop` object and entity. The
   entity join means evidence about the current, not a spatial eddy-current join.
   It creates no state intersection or NASA animation identification.
5. One publication plus one extraction-method provenance record are not two
   independent observations. An exactly matching existing source may be reused;
   a changed source-ID collision or a different ID for the same publication
   requires explicit reconciliation before any mutation.
6. Add only these collections/sources and Loop-owned evidence references,
   their two capability counts, one section fingerprint and a refreshed object
   fingerprint. Preserve all existing measurements, reported-length ranking,
   width fields, samples, geometries, names, entities, dates and other objects.
   A reported event date does not update the owner's latest observation date.
7. Check the complete contract with JSON-type-sensitive serialization before
   appending. Validate existing provenance, owner references and counts first.
   Refuse duplicates and partial reapplication; commit all small replacements
   to the mapping only after every validation has passed.
8. Provide label/value/unit/scope fields supported by the existing query UI,
   exact example queries, publication/source-pointer links and the static
   inspected chart. Do not add generic `timeline_file` or geometry fields that
   could make the UI imply a geographic map for an event day.

## Verification and delivery

Use small offline fixtures to test owner/source reassignment, duplicate and
partial application, existing-source reuse, changed values/types, event dates,
subset completeness, prohibited promotions, and preservation of unrelated data.
No local full packet/index loads, browser automation or native/WASM builds.

This contract is preparation. Verify it against the exact installed dataset in
one cloud stage before extending the saved packet. Then review the normal
query UI, source-index links and owner navigation with the matching engine.
Install through the existing branch/PR after those gates; no new PR per gap.
All prior scientific/runtime/source freezes remain unchanged.
