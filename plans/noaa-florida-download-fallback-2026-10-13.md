# Florida source download fallback

Remote runs 38521071708 and 38521066454 at commit 06a8888 stopped during
fixture acquisition. The NOAA Florida Current PDF request with `?download=1`
returned HTTP 404 before the Melet source verification was reached.

On 2026-10-13 both the bare download URL and its `?download=1` form returned
40,242,350 bytes with the existing acquisition SHA256
`f68fa48b85ce9cb37c04d8e32cffbc282fcc8dc60f82f725d5ba80f2b3234e0e`.
The NOAA record independently lists this same checksum:
https://repository.library.noaa.gov/view/noaa/49908

The preferred request remains unchanged. A transport failure can now try the
bare URL, registered only for the exact paper, original source URL and SHA256.
Both responses must pass the original size, format and checksum checks.
Integrity failures cannot fall through to another response. Acquisition
receipts, measurement values and generated scientific data are unchanged.
Original PDFs remain excluded from Git.

Focused verification: 22 tests and nine subtests passed, covering the 404
fallback, unchanged manifest, rejection of corrupt fallback bytes and absence
of fallback with a changed pin. The preceding commit passed the full local
1,353-test/992-subtest suite; that full suite was not rerun for this transport
change. Remote validation is pending at publication.
