# Indian SECC monthly array serialization v1

Declared after the first Linux original-response reconstruction failed at
`quality.json`, while all 33 scientific report rebuilds matched exactly.
Local Python3.14 uses zlib-ng1.3.1; local Python3.13 uses zlib1.3.1. Repacking
the same retained NPY members produces different compressed NPZ bytes:
2,025,722 versus2,000,063 bytes. This is a serialization repair, not a change
to sample selection, masks, packing, means, current identity or measurements.

Monthly NPZ products use ZIP_STORED, with member names sorted, an explicit
1980-01-01 timestamp, creator system3, create/extract version20, Unix0600
attributes and no extra fields/comments. NPY uses explicit format1.0 and
allow_pickle=False. Existing little-endian Float64 coordinates/means and
Int16 month/pair-count arrays retain their original shapes and bits.

Before admitting the repaired source package, require all seven decoded
arrays, original NPY member bytes, complete monthly field JSON, retained
provider-response ZIP and selection manifest to remain byte exact. Quality,
acquisition and derived report/view bindings may change solely to identify
the canonical array container and this protocol. Keep every prior scientific
report/operator unchanged. Do not weaken the exact original-response
reconstruction gate or replace it with tolerances. Linux must reconstruct
the full NPZ, JSON and quality product bytes exactly.

The existing acquisition and local-normal protocols remain authoritative
for scientific calculations. Original compressed NPZ bytes remain available
in commit6ade3c4. Provider original-response archive bytes are retained as an
input; this protocol concerns the regenerated monthly array product.
