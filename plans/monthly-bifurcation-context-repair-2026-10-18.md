# Monthly branching context checksum repair

Baseline `2b3d47a1a57c9a2768c7bfd7915d6aaff99b1777`; same branch and PR83.

The complete clean caf7008 run reported a failure while remaining live.
Its collected test order identified the Indian SEC monthly reconstruction
check. A separate targeted run reproduced the failure: the retained report
still referenced the old equatorial endpoint audit checksum after that audit's
family dependency was refreshed. The Pacific NEC report uses the same audit
and has the same stale dependency.

For each report, recompute with its existing generator and confirm that the
only difference is `scope_audit_sha256`. Replace only that checksum in the
original bytes. All 36 monthly latitude values, source variability bands,
reading allowances, periods, source PDFs, protocols, admission flags and
every other field remain unchanged. No generator or scientific rule changes.

Rebuild the lossless source index and engine pins. The query packet and
dashboard bytes remain unchanged. All four Indian/Pacific source tests and
eight subtests pass in 0.64 seconds; all 62 Rust tests pass. The engine's
native atlas smoke passes. Actual source-query UI returns both exact repaired
documents with native/WASM parity, unchanged series and the current context
checksum. No page errors occur.

This targeted diagnosis does not substitute for the live caf7008 run's
eventual terminal result. Keep that process and receipt intact, investigate
any additional failures, and require a complete clean latest successor
before main release. This metadata repair adds no measurements or coverage.
