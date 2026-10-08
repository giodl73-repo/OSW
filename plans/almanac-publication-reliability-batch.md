# Almanac publication reliability and consolidation

Working branch: `codex/almanac-publication-reliability`, based on
`33cbeed446955956b1ed7c472ef821e4aafb4f66`. Existing publication PR:
<https://github.com/giodl73-repo/OSW/pull/30>, targeting `main`.
This batch does not claim protected landing or scientific completion.

## Observed publication failure

PR 37 workflow 37739283437, offline job 113185991277, is terminal failure
at source acquisition. Logs confirm that the first four paper fixtures were
verified, then the Qiu/Chen author-PDF request timed out. The independent push
workflow 37739198317 was confirmed live and progressing through its test suite;
it was not restarted or treated as terminal.

## Reliability change

The acquisition command now attempts transport failures at most three times,
with a 60-second request timeout and 1/3-second delays. Retryable HTTP statuses:
408, 429, 500, 502, 503, 504. Permanent HTTP responses, invalid PDF magic,
oversized content and checksum mismatches stop without retry. Existing local
originals are checked offline and never silently refreshed.

Verified bytes are staged in the source directory, flushed and fsynced, then
published exclusively. Windows uses exclusive rename; POSIX uses exclusive
hard-link creation. A concurrent existing destination is verified, never
overwritten. Failed staging leaves no partial destination or temporary file.
All five source URLs, known NOAA client behavior, original hashes, file limits
and ignored-original rights decisions remain unchanged.

## Local verification

- Full suite: **817 tests and 619 subtests passed**, 229.58 seconds.
- Final acquisition tests pass through unittest (5) and pytest (5), including
  successful staging, bounded retry, permanent HTTP error, size/format/checksum
  rejection, offline originals and failed-write cleanup.
- Fresh original Qiu/Chen download: 3,012,493 bytes, SHA256
  `b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987`.
- All five existing paper originals verify locally and remain ignored.
- JavaScript syntax passes for 39 modules; all 14 page assignments pass.
  The 52 registered browser checks remain an exact-head CI requirement.
- Windows CRLF-aware whitespace check passes.

The full suite began before the last portability adjustment. The final five
acquisition tests were rerun after it. A standalone unittest attempt initially
hit the sandbox's default temporary-folder permissions; tests now use a scoped
workspace scratch directory. Exclusive hard links were also rejected by the
Windows sandbox; the Windows-exclusive rename path fixed that staging failure.
These failed attempts are recorded rather than counted as passing checks.

## Protected-main path

Refresh remote main and publication-branch refs, verify both are ancestors of
the proposed head, and perform a non-force atomic fast-forward push. PR 30
already has human-enabled squash auto-merge. Its exact new head must pass
protected checks before GitHub can land it. Keep earlier draft PR review
receipts until main publication actually completes.

The accumulated snapshot includes all prior fixes and UI/data batches:
39 Rust/WASM collections, 76 source documents, 240 dashboard objects, 72 scoped
width records, 32 cruise sampling maps and nine named regional recurrence
summaries. The canonical current/eddy identity counts are preserved.

## Remaining full-goal requirements

89 missing published current lengths, 57 unassessed width owners, compatible
annual dimension series, most named-eddy dated footprints and physical state
membership remain incomplete. Repository landing does not admit them or create
an independently reviewed scientific release.

Reproduction:

```powershell
python analysis/acquire_local_paper_fixtures.py
python -m unittest discover -s analysis -p test_acquire_local_paper_fixtures.py
python -m pytest analysis -q
python analysis/check_almanac_javascript.py
python analysis/check_almanac_page_coverage.py
```

Review:
`signals/roles/check/almanac-publication-reliability-roles-check-2026-10-07.md`.
