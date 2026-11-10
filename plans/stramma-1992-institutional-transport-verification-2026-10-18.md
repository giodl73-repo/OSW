# Stramma 1992: exact institutional download fallback

Continues draft PR83 on `codex/current-measurement-gaps`.

Hosted run39135217743 atd1fcc22 failed before tests with HTTP403 at the
percent-encoded canonical GEOMAR path for the South Indian Current paper.
The canonical source URL and acquisition receipt remain unchanged.

At2026-10-18 14:21:40UTC the same institutional item's unencoded URL returned
the **exact retained original**:

- [Verified institutional alternative](https://oceanrep.geomar.de/id/eprint/32119/1/1520-0485(1992)022_0421_tsioc_2.0.co;2.pdf)
- Bytes: **916,643**; pages: **10**.
- SHA256: `96b8af6dc2b3f3084fd65245a20564068b557bf200b50c48f53bd38b13761013`.
- Every response byte equals the previously retained, reviewed PDF.

The alternative is allowed only for the existing exact fixture name,
canonical URL and SHA tuple. Certificate verification, bounds, PDF-format
checks, checksum validation, atomic staging and retry rules are unchanged.
An integrity failure never enters transport fallback. The PDF and source
images remain ignored; this does not redistribute the article, change its
edition, alter an extraction or admit another measurement.

The source acquisition suite passes **17 tests / 9 subtests in0.70seconds**.
The new case exercises blocked-primary success with real retained original
bytes, rejects different PDF bytes without staging them, rejects a changed
canonical URL or pin and preserves the receipt. All **45 default local paper
fixtures** verify after the change. Existing retry, TLS and staging cases
remain in the suite.

The complete clean d1fcc22 analysis run is already running separately; it
predates this fallback addition. No later full-suite or hosted success is
claimed here. The distinct Reading/Van Aken source-host refusal remains
unresolved; neither its bare-host alias nor the www host currently accepts
connections. The different-hash KNMI rendition is not silently substituted.

Reproduce the offline checks:

```text
python -m pytest analysis/test_acquire_local_paper_fixtures.py -q
python analysis/acquire_local_paper_fixtures.py
```

The second command reuses valid local originals without network requests;
missing originals trigger explicit, checksum-verified acquisition. An
independent live call to `download_url` verified the alternative above.
Current scientific data, query/UI assets and coverage counts are unchanged.
