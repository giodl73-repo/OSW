"""Complete one university chain without adding a trust anchor or disabling TLS."""
import hashlib
from pathlib import Path
import ssl

ROOT=Path(__file__).resolve().parents[1]
CHAIN='research/source-data/tls/emsign-root-tls-g1-cross.pem'
PIN='e99a766c20aa3d8c86d3e8604c4b5c75bc33b4d0353597d3a4190209bfc41e1e'
PAPER_SHA='b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987'
URL='https://www.soest.hawaii.edu/oceanography/bo/QC_NEC.pdf'
ALIASES=(URL,'https://soest.hawaii.edu/oceanography/bo/QC_NEC.pdf')


def options(name,manifest,url):
    if (name,manifest.get('source_url'),manifest.get('sha256')) != ('qiu-chen-nec-2010',URL,PAPER_SHA) or url not in ALIASES:
        return {}
    raw=(ROOT/CHAIN).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PIN:
        raise ValueError('Changed scoped university TLS chain link')
    context=ssl.create_default_context()
    # This certificate is cross-signed, not self-signed. Require the existing
    # system root above it, even on Python versions enabling partial-chain trust.
    context.verify_flags &= ~ssl.VERIFY_X509_PARTIAL_CHAIN
    context.load_verify_locations(cadata=raw.decode('ascii'))
    return {'context':context}
