# SOEST paper acquisition: missing cross-signed issuer

Remote CI39080669703 passes the new South Pacific acquisition and verifies
the complete Uhlhorn/Radenac scientific editions. It then fails on both verified
Qiu2010 university aliases: the server sends only its leaf and InCommon OVG2C
intermediate. The chain to the existing emSign Root CA G1 needs an additional
cross-signed emSign Root TLS CA G1 certificate.

The missing link comes from the issuer's HTTPS repository:
[cross-signed issuer](https://repository.emsign.com/certs/crosssign/roottlscag1.crt).
The university IT explanation of the hierarchy is at
[University of Maryland](https://itsupport.umd.edu/itsupport/?id=kb_article_view&sysparm_article=KB0020705).

The public certificate is tracked with an acquisition receipt. The helper
checks its exact PEM checksum and supplies it only for the original Qiu paper
acquisition tuple and the two verified SOEST URLs. A new default SSL context
keeps hostname and certificate verification enabled and disables partial-chain
trust. The existing system root above the supplied link is still required;
there is no added root trust anchor. Other source requests use ordinary TLS.
The original paper URL, original response checksum and all science stay fixed.

## Evidence

- The actual university server chain was inspected with OpenSSL. Its second
  certificate's issuer is emSign Root TLS CA G1; the missing link is issued by
  the older emSign Root CA G1 already present in the default CA bundle.
- Actual download using the ordinary Git/OpenSSL CA bundle fails with the same
  missing-issuer error as CI. Supplying the scoped cross-signed link succeeds,
  with complete-chain/hostname verification and partial-chain trust disabled.
- The downloaded paper is exactly3,012,493 bytes, SHA256
  b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987,
  matching the retained source pin.
-27 focused TLS/acquisition tests and7 subtests pass in0.99 seconds. They check
  hostname verification, complete-chain requirement, changed certificate
  rejection, source/host/path scope, source checksum rejection and acquisition
  receipt consistency, alongside existing retry and mirror tests.

Live proof is local at
`.pytest_cache/current-originals-next/soest-chain-live-proof.json`. No private
keys, source PDFs or server leaf certificates are published. This repair does
not require changing the generated atlas, query data or native/WASM executable.

The full scientific-data suite started from clean62f2a2b before this transport
repair; do not attribute that invocation to the later transport code. The
focused transport suite above covers this repair. Remote CI must independently
confirm acquisition in its environment. Same draft PR83; no merge approval.
