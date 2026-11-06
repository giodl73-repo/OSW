# Melet repository cover and journal-source integrity

Continue draft PR83. The previous goal turn made verified progress at `ff59eea`.
This batch repairs the repeated source-acquisition failure that prevented
remote validation of the current measurement/data work. Measurement gaps remain.

## Evidence

Reviewed original acquisition remains unchanged: 6,048,321 bytes, SHA256
`9d41af95d2ccbcee1e1469ea45d703d9cb1005ce6d1701896f4a94b5e8f1da3d`.
Current HAL download: 6,048,322 bytes, SHA256
`b2785296927acfb199f3a93922bdb4be93e5d5b2645a86dc028cca6d68186346`.
Same HAL v1 URL and Melet et al. (2010), doi:10.1175/2009JPO4264.1.

Whole-byte comparison alone initially showed extensive differences because
offsets shifted. Object comparison identifies fourteen changed objects:
catalog PDF version, generated creation date, cover content/font names,
font descriptors, Unicode/CID maps and cover font subsets. Original/current
cover text and bibliography metadata agree. This is broader than a volatile
PDF-ID field and cannot be handled by the Sasaki metadata restoration rule.

All eighteen journal-page content streams match. The **complete 143-object
journal graph**, including page geometry, references, resources, raw encoded
streams, fonts and figure assets, is identical. Graph SHA256:
`5dfbad4b316d199dfcae389e1f9ce4f4dce15d5f1edb4cafb2e6193720fbd81d`.
All eighteen journal pages render pixel-identically at 72 dpi with the same
PyMuPDF version; the cover rendering also matches. The graph proof is stronger
than extracted-text or screenshot equality alone.

## Integrity rule

Preserve the reviewed original pin and original acquisition receipt. Prefer
the retained exact original; corruption of that file is fatal even if another
valid rendition exists. Never reconstruct its bytes or put a later rendition
under `journal-article.pdf` while claiming the reviewed hash.

Only this identified Melet/HAL source may accept a full regenerated-cover
rendition, retained **unchanged** as `repository-current.pdf` and excluded from
Git. Acceptance requires the frozen journal graph, all protected PDF-object
fingerprints, original object inventory, cover-text identity, bibliography
metadata and constrained catalog/date forms. Only the fourteen proved
generated-cover objects may differ; catalog and bibliography changes are
further restricted. Another paper, source URL, edition, scientific object,
figure/font/stream, geometry, added object or identity change is rejected.

The public integrity contract contains fingerprints only, not copyrighted
source streams, a PDF patch or reconstructed original. Python parsing is pinned
to pypdf 6.11.0. Original PDFs and private comparison/rasterization artifacts
remain outside Git. Other paper acquisition pins/retry/mirror rules are unchanged.

Source-document metadata in the confinement audit explicitly describes the
reviewed acquisition snapshot. Runtime source resolution may use the separately
stored complete rendition after edition verification. Stable data inputs bind
the integrity contract and verifier rather than a mutable repository cover;
actual response hashes are recorded in acquisition output. This prevents
cover regeneration from changing measurement results or committed bundle data.

## Verification and data preservation

Fresh live hydration in an empty isolated directory passed; only the full
`repository-current.pdf` was created. No reviewed original was fabricated.
Both existing confinement records validate from that source. Rebuilding
query and dashboard data with only the current rendition present produces
identical output to rebuilding from the retained original.

Focused acquisition/integrity gate: 21 tests / nine subtests passed. Negative
checks alter a scientific encoded stream, journal geometry, producer/identity,
source URL/pin and contract; corrupted retained originals cannot fall back.
Atomic staging retains full received bytes separately and leaves no partial
fixture. Controlled metadata variants are test fixtures only and never serve
as acquisition originals. All 31 retained local paper pins still verify.

Two confinement reference scales remain 100 km and 40 km, with full widths,
paired edges, annual ranges and numeric uncertainty still unknown. No new
measurement or physical geometry is admitted. Source audit/protocol receipts,
two width evidence fingerprints, seasonal-inventory checksum and generated
source/bundle receipts update. All other scientific values and observations
remain unchanged. Source corpus grows to 211 documents; core collections and
current/width/route counts remain unchanged.

Serialized Rust/native/WASM build and full offline/browser/remote gates are
recorded on completion. The goal remains active until the broader core-data
requirements are met. This source fix is not a scientific gap-completion claim.

## Final local verification

**1,353 tests and 992 subtests passed in 1217.68 seconds (20m17s).**
All 46 Rust tests and serialized native/WASM builds passed. Focused source
gate: 21 tests / nine subtests. Confinement browser passed model/cited cards,
mobile, source/inspector/native-WASM parity and coherent scope rejection.
Index-store browser passed 211 exact sources, twelve seasonal snapshots,
independent NOAA oracle and checked-input failures. All 61 engine pins and
211 source-document hashes/byte counts verified; staged bytes match workspace.
Numerical data, route frames and observation dates preserved; exactly two
intended confinement-evidence fingerprints change. Original acquisition receipt
is byte-identical. Remote validation will be tracked separately after push.
