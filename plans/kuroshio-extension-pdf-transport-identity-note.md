# Kuroshio Extension PDF transport identity

PR58 remote offline run 37887931777, job 113682019691, failed while acquiring
the Sasaki et al. (2013) original: source checksum differed from its pin.
This was before tests, after the first nine originals were verified; it was
not the earlier Qiu/Chen timeout. Both PR58 offline jobs failed and both NetCDF
jobs passed. Only the later failed job log was inspected for this diagnosis.

Two fresh local requests reproduced differing SHA256 responses. Each was
3,831,641 bytes with 16 pages, identical metadata and identical extracted page
text. Byte comparison against the originally downloaded, pinned PDF established
that *only* the 32 hexadecimal bytes of the second `/ID` changed, at offsets
3,831,094 through 3,831,125 (zero-based, inclusive). All other bytes were identical.

Observed response SHA256s:

- 08f9ffb9b85b3560ffcb750c601ffaba33d9b6553cb1ab17082afc951735fd97
- 28839ca252e2fd502d91b42626896dfd6fa5dac2d0ee6c4178e14408a95135d4

Reference fixture SHA256 remains
483dd114d6bbbff9b153460edf28a3391958a78e1a0b6a646db548eefcb8a674.
The first PDF ID remains `996ea1892d5650af4f179c438e82877f`; reference second ID is
`d90a76365c4c151ec2c33f8c7cdfe942`.

The acquisition helper now restores that exact second ID only for this named
source and reference pin, with exact size, offset, first-ID prefix and hexadecimal
field shape. Restoration is accepted only when hashing the resulting *whole
file* produces the existing reference pin. Any other byte change fails. The
original reference fixture is left untouched. No scientific content, source
identity, image, text, timestamp, checksum gate or original fixture pin changes.

On restoration the helper prints the actual response SHA and resulting fixture
SHA. Fresh remote responses and the locally canonical fixture are explicitly
distinguished. This is a deterministic transport normalization, not acceptance
of arbitrary alternative papers or semantic-only PDF equivalence. The complete
original remains ignored; neither response is redistributed.

Tests use the real source fixture and the reviewed second response identifier;
they reject edits elsewhere, first-ID edits, wrong owner, wrong size and changed
target pin. This addresses a known reproducibility issue while preserving exact
scientific bytes. Future changes outside this field require a new source review.
