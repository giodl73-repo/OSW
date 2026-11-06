"""Verify retained original evidence for two unresolved current dimensions."""
import argparse
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
AUDIT = 'research/southern-current-width-source-limitations-audit.json'
PIN = 'f0905f67f4cef033f48f7a598cc46f831b8fe8a41fae55df2e51dd935ffc65ba'


def verify(acquire_originals=False):
    raw = (ROOT / AUDIT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed reviewed southern-current source limitations')
    audit = json.loads(raw)
    for source in audit['sources']:
        manifest = ROOT / source['acquisition_file']
        if hashlib.sha256(manifest.read_bytes()).hexdigest() != source['acquisition_sha256']:
            raise ValueError('Changed southern-current original acquisition receipt')
        if acquire_originals:
            from acquire_local_paper_fixtures import acquire
            acquire(manifest.parent.name, manifest.parent)
        path = ROOT / source['source_document_file']
        data = path.read_bytes()
        if len(data) != source['source_document_bytes'] or hashlib.sha256(data).hexdigest() != source['source_document_sha256']:
            raise ValueError('Changed southern-current original source document')
        if len(PdfReader(path, strict=True).pages) != source['source_document_pages']:
            raise ValueError('Incomplete southern-current original source document')
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true', help='Explicitly hydrate the two ignored, checksum-pinned originals')
    args = parser.parse_args()
    audit = verify(args.acquire)
    print('PASS: two primary originals verified; South Indian current width and South Australian physical edges remain unresolved. No product record or dimension admitted.')
