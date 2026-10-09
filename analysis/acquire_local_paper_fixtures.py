"""Hydrate ignored, checksum-pinned paper fixtures for local/CI validation.

Original papers remain outside Git. This is acquisition, not redistribution.
The offline tests retain their strict checks and require these local originals.
"""
import hashlib
import http.client
import json
import os
import re
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ('kuroshio-liu-gan-2012', 'leeuwin-deng-2008', 'florida-archer-2017', 'chen-madagascar-2014', 'qiu-chen-nec-2010', 'van-aken-astrid-2003', 'schott-mccreary-2001', 'djakoure-guinea-2017', 'gouriou-atlantic-1988', 'sasaki-kuroshio-extension-2013', 'zenk-ngcu-1999', 'siedler-sonne-1997', 'cresswell-zeehan-2000', 'matsuyama-tsushima-1990', 'glenn-wac-2008', 'fissel-baffin-1982', 'chavanne-adriatic-2007', 'skov-jutland-2019', 'nielsen-jutland-2000', 'melet-solomon-2010', 'tomczak-regional-2005', 'park-acc-2019')
RETRY_DELAYS = (1, 3)
TRANSIENT_HTTP = {408, 429, 500, 502, 503, 504}


def normalize_transport_identity(name, manifest, data):
    """Restore one verified volatile PDF ID; every other byte must match the pin."""
    pinned = '483dd114d6bbbff9b153460edf28a3391958a78e1a0b6a646db548eefcb8a674'
    if name != 'sasaki-kuroshio-extension-2013' or manifest['sha256'] != pinned:
        return data
    if hashlib.sha256(data).hexdigest() == pinned:
        return data
    start, end = 3_831_094, 3_831_126
    prefix = b'/ID [<996ea1892d5650af4f179c438e82877f><'
    if len(data) != 3_831_641 or data[start-len(prefix):start] != prefix or data[end:end+3] != b'>] ' or not re.fullmatch(b'[0-9a-f]{32}', data[start:end]):
        return data
    canonical = data[:start] + b'd90a76365c4c151ec2c33f8c7cdfe942' + data[end:]
    if hashlib.sha256(canonical).hexdigest() != pinned:
        return data
    print(f'{name}: restored verified transport-only PDF second ID; response SHA256 {hashlib.sha256(data).hexdigest()}; fixture SHA256 {pinned}', flush=True)
    return canonical


def verify(name, manifest, data):
    maximum = {'florida-archer-2017':50_000_000,'glenn-wac-2008':60_000_000,'tomczak-regional-2005':40_000_000}.get(name,20_000_000)
    if len(data) > maximum or not data.startswith(b'%PDF-'):
        raise ValueError(f'{name}: expected a PDF below {maximum//1_000_000} MB')
    data = normalize_transport_identity(name, manifest, data)
    if hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError(f'{name}: source checksum differs from the pinned acquisition')
    return data


def download(name, manifest):
    source_url = manifest['source_url']
    # Preserve the already verified NOAA download form and client behavior.
    if name == 'florida-archer-2017':
        source_url += '?download=1'
    headers = {} if name == 'florida-archer-2017' else {'User-Agent': 'OSW-source-validation/1.0'}
    request = urllib.request.Request(source_url, headers=headers)
    maximum = {'florida-archer-2017':50_000_000,'glenn-wac-2008':60_000_000,'tomczak-regional-2005':40_000_000}.get(name,20_000_000)
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read(maximum + 1)
            return verify(name, manifest, data)
        except urllib.error.HTTPError as error:
            error.close()
            if error.code not in TRANSIENT_HTTP:
                raise
            failure = error
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead) as error:
            failure = error
        # Source checksum, format and size errors never enter the retry path.
        if attempt == len(RETRY_DELAYS):
            raise failure
        delay = RETRY_DELAYS[attempt]
        print(f'{name}: transient download failure; retry {attempt+2}/3 in {delay}s', flush=True)
        time.sleep(delay)


def acquire(name, directory):
    manifest = json.loads((directory / 'acquisition.json').read_text(encoding='utf-8'))
    filename = manifest.get('document_filename', 'journal-article.pdf')
    if filename not in {'journal-article.pdf','source-book.pdf'}:
        raise ValueError('Unsupported local source document filename')
    destination = directory / filename
    if destination.exists():
        return verify(name, manifest, destination.read_bytes())
    data = download(name, manifest)
    # Stage only verified bytes. A failed write cannot leave a partial fixture.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.paper-', suffix='.tmp', delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        if destination.exists():
            verify(name, manifest, destination.read_bytes())
        else:
            try:
                # Windows rename is exclusive; POSIX hard-link creation is exclusive.
                # Both operate within this directory and never replace a concurrent copy.
                if os.name == 'nt':
                    os.rename(temporary, destination)
                else:
                    os.link(temporary, destination)
            except FileExistsError:
                verify(name, manifest, destination.read_bytes())
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return data


def main():
    for name in PAPERS:
        directory = ROOT / 'research/source-data' / name
        acquire(name, directory)
        print(f'{name}: local original verified; excluded from Git')


if __name__ == '__main__':
    main()
