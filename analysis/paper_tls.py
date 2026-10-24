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
CHEN_URL='https://www.soest.hawaii.edu/oceanography/bo/Chen_etal_JGR2016.pdf'
CHEN_SHA='89af9045ed11f2bf18903b405f6beae14fbe83a3c9ca0202d6cb25122b7d381e'


def options(name,manifest,url):
    identity=(name,manifest.get('source_url'),manifest.get('sha256'))
    qiu=identity==('qiu-chen-nec-2010',URL,PAPER_SHA) and url in ALIASES
    chen=identity==('chen-necc-2016',CHEN_URL,CHEN_SHA) and url==CHEN_URL
    if not (qiu or chen):
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
