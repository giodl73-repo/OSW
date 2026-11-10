# Query packet transport v1

The public query-data.json entrypoint may contain either the complete legacy
osw.query-bundle.v1 JSON or an osw.query-packet.v1 manifest. The latter describes
ordered raw byte parts, each at most 16 MiB. Every nonfinal part is exactly
16 MiB. Paths bind the zero-based index and SHA-256 of each part. Paths cannot
contain traversal, an origin, an absolute path, or arbitrary filenames.

All implementations check the schema, descriptors, length, order, each part's
SHA-256 and the assembled logical SHA-256 before loading the logical bundle.
The browser additionally requires every part pin in the engine manifest.
Native and Python filesystem readers reject resolved paths outside the bundle
directory. Missing or changed parts fail the load; no partial store is installed.
UTF-8 is decoded after assembly because a code point can cross a part boundary.

Workspace and export identity remains the SHA-256 of the complete original
logical bytes, including whitespace. The engine manifest separately pins the
physical entrypoint and each part. Saved source snapshots remain complete JSON
bytes and can be exported and rebased without a transport manifest. Legacy
complete JSON inputs, including scientific corruption fixtures, remain supported.
The UI accepts complete source snapshot uploads up to 512 MiB; the former
100 MB limit already excluded the 102,819,992-byte current snapshot. The source
export/re-attachment browser check exercises bytes above that former limit.
No ABI change is needed: the worker assembles transport bytes, then calls the
existing Rust validation and query API. Selection and scientific validation
continue to run in Rust.

Parts are written before an atomic manifest replacement. Existing parts are
reused only after exact byte verification. The writer does not delete old parts
or source files. A later cleanup must prove an asset is unreferenced before
removing it. The initial migration packages the exact existing logical bytes
from ede0418a637b5bd7ddc3a6ab91c7ae1bec70a574, preserving its generator receipt.
Future scientific builds renew generator provenance as usual.

This removes the single Git blob size bottleneck. It does not provide lazy
collection queries or reduce the full bundle memory requirement. All current
measurements, failed attempts, sources, routes, scope and uncertainty remain
unchanged. Further years and levels require scientific extraction and review.

## Verification commands

Verify or repackage an existing snapshot without changing its logical bytes:

```
python analysis/query_packet.py almanac/query-data.json
python analysis/query_packet.py almanac/query-data.json --pack
```

Future scientific builds use analysis/build_rust_query_bundle.py, then
analysis/build_rust_query_engine.py. The latter runs native tests/builds, compiles
the WASM engine, pins the transport members and checks native atlas loading.

```
python -m pytest analysis/test_query_packet.py analysis/test_query_taxonomy.py -q
python analysis/build_rust_query_engine.py
python analysis/test_query_packet_browser.py
python analysis/test_rust_workspace_browser.py
python analysis/test_rust_rebase_browser.py
python analysis/test_rust_collection_coverage_browser.py
```

Browser checks use the local checkout server on8788 and the configured
Playwright browser. They are also registered in run_rust_query_browser_checks.py.
Collection coverage preserves every frozen release row, checks working additions
through engine admission validators and compares native/WASM first/last records.
The full fresh offline suite remains a separate gate; focused success does not
establish that gate or close outstanding scientific measurement gaps.
