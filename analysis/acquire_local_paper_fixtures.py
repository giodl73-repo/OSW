"""Hydrate ignored, checksum-pinned paper fixtures for local/CI validation.

Original papers remain outside Git. This is acquisition, not redistribution.
The offline tests retain their strict checks and require these local originals.
"""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ('kuroshio-liu-gan-2012', 'leeuwin-deng-2008', 'florida-archer-2017', 'chen-madagascar-2014')


def main():
    for name in PAPERS:
        directory = ROOT / 'research/source-data' / name
        manifest = json.loads((directory / 'acquisition.json').read_text(encoding='utf-8'))
        destination = directory / 'journal-article.pdf'
        if destination.exists():
            data = destination.read_bytes()
        else:
            source_url = manifest['source_url']
            # NOAA's bare large-file URL can return a cached 403. Its download
            # form serves the same original; the pinned checksum remains mandatory.
            if name == 'florida-archer-2017':
                source_url += '?download=1'
            # NOAA accepts the standard urllib client but rejects our custom
            # client header for this large-file endpoint.
            headers = {} if name == 'florida-archer-2017' else {'User-Agent': 'OSW-source-validation/1.0'}
            request = urllib.request.Request(source_url, headers=headers)
            with urllib.request.urlopen(request, timeout=60) as response:
                maximum=50_000_000 if name=='florida-archer-2017' else 20_000_000
                data = response.read(maximum+1)
            if len(data) > maximum or not data.startswith(b'%PDF-'):
                raise ValueError(f'{name}: expected a PDF below {maximum//1_000_000} MB')
        if hashlib.sha256(data).hexdigest() != manifest['sha256']:
            raise ValueError(f'{name}: source checksum differs from the pinned acquisition')
        if not destination.exists():
            with destination.open('xb') as output:
                output.write(data)
        print(f'{name}: local original verified; excluded from Git')


if __name__ == '__main__':
    main()
