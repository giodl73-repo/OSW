"""Hydrate ignored, checksum-pinned paper fixtures for local/CI validation.

Original papers remain outside Git. This is acquisition, not redistribution.
The offline tests retain their strict checks and require these local originals.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ('kuroshio-liu-gan-2012', 'leeuwin-deng-2008')


def main():
    for name in PAPERS:
        directory = ROOT / 'research/source-data' / name
        manifest = json.loads((directory / 'acquisition.json').read_text(encoding='utf-8'))
        destination = directory / 'journal-article.pdf'
        if destination.exists():
            data = destination.read_bytes()
        else:
            request = urllib.request.Request(manifest['source_url'], headers={'User-Agent': 'OSW-source-validation/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(20_000_001)
            if len(data) > 20_000_000 or not data.startswith(b'%PDF-'):
                raise ValueError(f'{name}: expected a PDF below 20 MB')
        if hashlib.sha256(data).hexdigest() != manifest['sha256']:
            raise ValueError(f'{name}: source checksum differs from the pinned acquisition')
        if not destination.exists():
            with destination.open('xb') as output:
                output.write(data)
        print(f'{name}: local original verified; excluded from Git')


if __name__ == '__main__':
    main()
