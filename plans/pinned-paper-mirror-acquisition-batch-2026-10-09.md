# Pinned original-paper transport alternatives

Parent `48f09ee07289915e1b75f2d64a3f6ea34e8b1304` / draft PR76.
Branch `codex/pinned-paper-mirror-acquisition`.

## Observed publication gap

PR76 push run 37937030577 completed with failure during original acquisition:
the last successful fixture was Sasaki/Kuroshio Extension, followed by HTTP
403 on the Zenk newsletter fixture. Companion run 37937121373 completed with
failure after three Qiu/Chen download timeouts. Both NetCDF jobs succeeded.
Neither failed paper job reached code validation. These terminal logs were
inspected directly; no restart was used as evidence of recovery.

## Exact original identity

The Zenk et al. (1999) extraction uses the complete 44-page International WOCE
Newsletter 34, March 1999. Its unchanged acquisition record remains the authority:
`research/source-data/zenk-ngcu-1999/acquisition.json`.

Pinned original: **8,089,173 bytes**, SHA256
`f38a100dc030a94ce776a914b96ea798dd40c6dc1aac80fce3563806c01a6407`.
Primary URL: https://oceanrep.geomar.de/1816/1/news34.pdf.

Fresh downloads on 2026-10-09 established byte identity at:

- https://oceanrep.geomar.de/id/eprint/1816/1/news34.pdf
- https://oceanrep.geomar.de/6814/1/news34.pdf

An additional tested eprint/6814 URL also returned the same bytes but is not
needed in the configured list. All configured alternatives share the GEOMAR
host; they cannot establish recovery from a host-wide access restriction.

NOAA's archived newsletter at
https://www.nodc.noaa.gov/archive/arc0116/0000841/1.1/data/0-data/wocedata_2/wocedocs/newsltr/news34/news34.pdf
returned **8,150,392 bytes**, SHA256
`703b312a2a1169c5823687d4704562b2c8c81becaca561639086a73c40cf64e4`.
It is not byte-identical and is excluded. No content equivalence, source-edition
replacement or PDF normalization is inferred. The wocedata_1 archive URL
returned the same differing NOAA bytes.

## Transport rules

1. Match the exact fixture name, original source URL and original SHA before
   offering the two known institutional alternatives.
2. Try the primary first; follow existing bounded retries for transient failures.
   A final transport failure may try the next configured location. Unconfigured
   fixtures retain their prior failure/retry behavior.
3. Every successful response passes the existing PDF size, signature and original
   checksum verification before return or staging. Integrity and format failures
   do not trigger another mirror, even if another location might be available.
4. Record successful mirror URL and expected checksum in acquisition output.
   Terminal transport exceptions identify fixture name and failed location.
5. Preserve original acquisition manifests, scientific audits, width records,
   source index, query data, Rust/WASM bytes and source-license treatment.
   Originals remain ignored; no new public copy or cache is created.

## Validation receipt

- Acquisition tests exercise exact registry identity, blocked primary, successful
  verified fallback, wrong primary/mirror bytes, corrupt staging, exhausted
  alternatives, bounded retries and unsupported paths.
- An actual institutional mirror download after a controlled primary HTTP 403
  reproduced the local original byte-for-byte through the production downloader.
- All **24** configured local originals verified successfully without downloads.
- Focused acquisition and related PDF transport identity gate: **18 tests and
  5 subtests passed** in 0.78 seconds.
- Publication status is recorded in the publication update. This transport-only
  batch adds no scientific data or UI coverage.

The full parent scientific/UI suite passed before this batch (1,246 tests and
918 subtests, 43 Rust tests plus browser regressions). That is parent evidence,
not a claim of a new full-suite run for this commit. The modified acquisition
module is imported by the two focused test modules; no dataset or engine bytes
change. Remote code validation must still pass its complete workflow.

## Remaining work

Hosted-runner availability of these URLs needs remote evidence. Qiu/Chen provider
timeouts remain unresolved; this registry makes no claim to fix them. If all
GEOMAR paths fail, obtaining an independently reviewed alternative source edition
requires explicit scientific/provenance reconciliation rather than checksum
relaxation. Mainline coverage and the wider current/eddy data gaps remain open.
