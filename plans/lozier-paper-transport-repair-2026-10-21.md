# Restore the original Lozier paper's acquisition path

CI at `ee27a9e`, run39674219943/job119479712438, stopped before tests:
WHOI's retained lowercase `/science/po/` URL returned HTTP404. Scientific
reproduction and NetCDF jobs succeeded. This is not the earlier IRD403 case.

The same institution's `/science/PO/` route was fetched and independently
verified against the original acquisition: 3,378,622 bytes, SHA256
`daadf0d96ac221ba65f9b70330dd563b26888f8aeacce57c75d23bde8ea0bcd8`.
The explicit fallback registry binds paper ID, original URL and checksum.
Original receipt, paper bytes, numeric source definitions and rights stay
unchanged. No publication is added to Git. Integrity errors and provider
cooldown still prevent fallback; no alternative PDF edition is accepted.

Focused tests exercise the actual retained original through a simulated404,
reject wrong bytes and changed pins, and retain the existing transport tests.
Run `python -m pytest analysis/test_acquire_local_paper_fixtures.py -q`.
This repair removes the observed acquisition-path failure; it does not claim
a fresh passing full CI suite. Keep the broader release gates open until
their actual terminal results are available. Same branch/draft PR83.
