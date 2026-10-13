# Qiu/Chen fixture acquisition fallback

Date: 2026-10-12. Parent: `1e9d31934c2e5f08055a74c93a7e03970c8a0b24`.

## Scope and evidence

Parent hosted run 38283084380 failed while acquiring the Qiu/Chen 2010
original PDF from the university's `www` hostname. Subsequent Rust, Python
and browser gates were skipped; this is not evidence of passing hosted gates.

Both the original URL and its non-www university alias returned 3,012,493
bytes locally, matching the existing SHA256
`b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987`.
The 14-page paper's title and authors were inspected. The alias is another
address on the same service, not an independent archive.

Added the alias to the existing exact fixture/URL/checksum allowlist.
The original acquisition manifest is unchanged. Integrity, PDF format and
size failures cannot trigger fallback. Papers and probe downloads remain
ignored; only verification metadata is versioned.

Verification receipt:
`research/source-data/qiu-chen-nec-2010/mirror-verification-2026-10-12.json`.

## Checks

- `python -m pytest -q analysis/test_acquire_local_paper_fixtures.py`:
  15 tests and seven subtests pass. Three new cases cover timeout exhaustion,
  changed pin/location refusal, and rejection of wrong alias bytes without staging.
- A production `acquire()` exercise with a controlled primary HTTP 403 used a
  real network download from the alias and staged exactly checksum-matching bytes.
  The controlled failure was not an observed local outage.
- `python analysis/acquire_local_paper_fixtures.py`: all 25 existing local
  originals verified. This was cache verification, not 25 remote downloads.
- `git -c core.whitespace=cr-at-eol diff --check` passes.
- Internal role review records 15 findings across SOUNDER, KEEL and LOGBOOK.

The parent full offline suite passed 1,280 tests and 923 subtests. It was not
repeated for this allowlist change; no scientific data, UI or WASM changed.
Hosted success must be observed separately. No scientific coverage increased:
89 published whole-current length gaps and 24 unassessed width owners remain.

## Publication

Stacked draft on `codex/ursa-dated-contour-candidate`; no automatic merge.
Hosted run identifiers and outcomes will be recorded after publication.

Published as draft PR #82:
https://github.com/giodl73-repo/OSW/pull/82
Implementation commit: `7612d326f69fca31324aea8e7037e1b6f145524f`.
Hosted run 38285937558 was in progress at publication; acquisition and
software gates were still pending. No hosted success is claimed.
