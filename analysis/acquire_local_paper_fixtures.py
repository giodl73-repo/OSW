"""Hydrate ignored, checksum-pinned paper fixtures for local/CI validation.

Original papers remain outside Git. This is acquisition, not redistribution.
The offline tests retain their strict checks and require these local originals.
"""
import hashlib
import http.client
import json
import math
import os
import re
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request
from paper_tls import options as paper_tls_options

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ('stramma-south-indian-1992', 'duran-southern-australia-2020', 'stramma-south-atlantic-1990', 'stramma-south-pacific-1995', 'uhlhorn-loop-2008', 'richardson-gulf-stream-1971', 'lozier-gulf-stream-1995', 'pous-hormuz-2004', 'pous-oman-2004', 'molinari-atlantic-seuc-1981', 'radenac-ngcc-2016', 'rotschi-secc-1972', 'peters-redsox-2005', 'pasaric-adriatic-2019', 'hughes-hiri-1993', 'duncan-caribbean-1982', 'kuroshio-liu-gan-2012', 'leeuwin-deng-2008', 'florida-archer-2017', 'chen-madagascar-2014', 'qiu-chen-nec-2010', 'van-aken-astrid-2003', 'schott-mccreary-2001', 'djakoure-guinea-2017', 'gouriou-atlantic-1988', 'sasaki-kuroshio-extension-2013', 'zenk-ngcu-1999', 'siedler-sonne-1997', 'cresswell-zeehan-2000', 'matsuyama-tsushima-1990', 'glenn-wac-2008', 'fissel-baffin-1982', 'chavanne-adriatic-2007', 'skov-jutland-2019', 'nielsen-jutland-2000', 'melet-solomon-2010', 'tomczak-regional-2005', 'park-acc-2019', 'nilsson-tasman-1980', 'richardson-dwbc-1993', 'wijeratne-australia-2018', 'meinen-antilles-2019', 'knorr-kn2004-2011', 'socib-regional-estimates-2023', 'chen-necc-2016')
RETRY_DELAYS = (1, 3)
TRANSIENT_HTTP = {408, 429, 500, 502, 503, 504}
RATE_LIMIT_DELAYS = (15, 45)
MAX_RETRY_AFTER = 60


class SourceCooldown(RuntimeError):
    """A provider cooldown exceeds the bounded automatic wait; do not retry early."""


def retry_pause(error, attempt):
    fallback = RATE_LIMIT_DELAYS[attempt] if error.code == 429 else RETRY_DELAYS[attempt]
    header = error.headers.get('Retry-After') if error.headers else None
    if not header:
        return fallback
    try:
        value = header.strip()
        if value.isdigit():
            delay = int(value)
        else:
            stamp = parsedate_to_datetime(value)
            if stamp.tzinfo is None: stamp = stamp.replace(tzinfo=timezone.utc)
            delay = max(0, math.ceil(stamp.timestamp()-time.time()))
    except (ValueError, TypeError, OverflowError):
        return fallback
    if delay > MAX_RETRY_AFTER:
        raise SourceCooldown(f'HTTP {error.code}: provider Retry-After={header} exceeds the {MAX_RETRY_AFTER}s automatic wait; no early retry or mirror fallback')
    return max(RETRY_DELAYS[attempt], delay)
# Byte-identical institutional locations verified 2026-10-09 (Zenk) and
# 2026-10-12 (Qiu); see the corresponding verification receipts. These are
# transport alternatives, not permission to substitute another PDF edition.
PINNED_MIRRORS = {
    # WHOI's case-sensitive /science/PO route serves the same3,378,622-byte
    # original, verified2026-10-21. The retained lowercase primary returned404
    # in CI. Keep the original acquisition receipt and checksum unchanged.
    ('lozier-gulf-stream-1995', 'https://www.whoi.edu/science/po/people/rcurry/pdf_files/Lozier_etal.PiO1995.pdf',
     'daadf0d96ac221ba65f9b70330dd563b26888f8aeacce57c75d23bde8ea0bcd8'):
    ('https://www.whoi.edu/science/PO/people/rcurry/pdf_files/Lozier_etal.PiO1995.pdf',),
    # Same repository's final EPrints path, verified byte-identical2026-10-17;
    # CI can receive403 from the older percent-encoded redirect path.
    ('stramma-south-pacific-1995', 'https://oceanrep.geomar.de/32120/1/1520-0485%281995%29025_0077_tspc_2.0.co%3B2.pdf',
     '9b471dbdeb5a010bda7411c40dcaa939fb5c55d1559c3a89c8281ca10c2efd28'):
    ('https://oceanrep.geomar.de/id/eprint/32120/1/1520-0485(1995)025_0077_tspc_2.0.co;2.pdf',),
    # Same institutional item and exact 916,643-byte original, verified
    # 2026-10-18. The encoded canonical URL can return HTTP403 in CI.
    ('stramma-south-indian-1992', 'https://oceanrep.geomar.de/id/eprint/32119/1/1520-0485%281992%29022_0421_tsioc_2.0.co%3B2.pdf',
     '96b8af6dc2b3f3084fd65245a20564068b557bf200b50c48f53bd38b13761013'):
    ('https://oceanrep.geomar.de/id/eprint/32119/1/1520-0485(1992)022_0421_tsioc_2.0.co;2.pdf',),
    ('zenk-ngcu-1999', 'https://oceanrep.geomar.de/1816/1/news34.pdf',
     'f38a100dc030a94ce776a914b96ea798dd40c6dc1aac80fce3563806c01a6407'):
    ('https://oceanrep.geomar.de/id/eprint/1816/1/news34.pdf',
     'https://oceanrep.geomar.de/6814/1/news34.pdf'),
    # Same university resource; exact 3,012,493-byte PDF verified 2026-10-12.
    ('qiu-chen-nec-2010', 'https://www.soest.hawaii.edu/oceanography/bo/QC_NEC.pdf',
     'b387e0e05e700fe66b3b2e98ebba56bf2d8151c3b703d37a7aecad43b5675987'):
    ('https://soest.hawaii.edu/oceanography/bo/QC_NEC.pdf',),
    # NOAA's bare download is byte-identical (40,242,350 bytes), verified
    # 2026-10-13; some CI requests to ?download=1 return HTTP 404.
    ('florida-archer-2017', 'https://repository.library.noaa.gov/view/noaa/49908/noaa_49908_DS1.pdf',
     'f68fa48b85ce9cb37c04d8e32cffbc282fcc8dc60f82f725d5ba80f2b3234e0e'):
    ('https://repository.library.noaa.gov/view/noaa/49908/noaa_49908_DS1.pdf',),
}


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
    maximum = {'pasaric-adriatic-2019':110_000_000,'florida-archer-2017':50_000_000,'glenn-wac-2008':60_000_000,'tomczak-regional-2005':40_000_000}.get(name,20_000_000)
    if len(data) > maximum or not data.startswith(b'%PDF-'):
        raise ValueError(f'{name}: expected a PDF below {maximum//1_000_000} MB')
    if name == 'radenac-ngcc-2016':
        from radenac_hal_source import verify_rendition
        verify_rendition(data, manifest)
        return data
    if name == 'uhlhorn-loop-2008':
        from uhlhorn_thesis_source import verify_rendition
        verify_rendition(data, manifest)
        return data
    data = normalize_transport_identity(name, manifest, data)
    if hashlib.sha256(data).hexdigest() != manifest['sha256']:
        if name == 'melet-solomon-2010':
            from melet_hal_source import verify_rendition
            proof = verify_rendition(data, manifest)
            print(f'{name}: verified unchanged journal edition with generated HAL cover; response SHA256 {proof["response_sha256"]}; reviewed original pin {manifest["sha256"]}', flush=True)
            return data
        raise ValueError(f'{name}: source checksum differs from the pinned acquisition')
    return data


def download_url(name, manifest, source_url):
    # The caller selects the exact verified download form.
    # NOAA's reviewed Antilles download rejects explicit User-Agent headers.
    # The exact original checksum remains mandatory with either transport.
    headers = {} if name in {'florida-archer-2017', 'meinen-antilles-2019'} else {'User-Agent': 'OSW-source-validation/1.0'}
    request = urllib.request.Request(source_url, headers=headers)
    maximum = {'pasaric-adriatic-2019':110_000_000,'florida-archer-2017':50_000_000,'glenn-wac-2008':60_000_000,'tomczak-regional-2005':40_000_000}.get(name,20_000_000)
    for attempt in range(len(RETRY_DELAYS) + 1):
        pause = None
        try:
            with urllib.request.urlopen(request, timeout=60, **paper_tls_options(name, manifest, source_url)) as response:
                data = response.read(maximum + 1)
            return verify(name, manifest, data)
        except urllib.error.HTTPError as error:
            if error.code not in TRANSIENT_HTTP:
                error.close()
                raise
            try:
                if attempt < len(RETRY_DELAYS): pause = retry_pause(error, attempt)
            finally:
                error.close()
            failure = error
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead) as error:
            failure = error
        # Source checksum, format and size errors never enter the retry path.
        if attempt == len(RETRY_DELAYS):
            raise failure
        delay = pause if pause is not None else RETRY_DELAYS[attempt]
        print(f'{name}: transient download failure; retry {attempt+2}/3 in {delay}s', flush=True)
        time.sleep(delay)


def download(name, manifest):
    primary = manifest['source_url']
    alternatives = PINNED_MIRRORS.get((name, primary, manifest['sha256']), ())
    # Preserve NOAA's original preferred transport, allowing its separately
    # verified bare URL only for the exact acquisition tuple above.
    preferred = primary + '?download=1' if name == 'florida-archer-2017' else primary
    urls = (preferred, *alternatives)
    for i, url in enumerate(urls):
        try:
            data = download_url(name, manifest, url)
            if i:
                print(f'{name}: verified pinned original from institutional mirror {url}; SHA256 {manifest["sha256"]}', flush=True)
            return data
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead) as error:
            error.add_note(f'{name}: acquisition failed at {url}')
            # Exhausting a provider's rate-limit retries is not permission to
            # request another URL before its cooldown. Ordinary transport/403
            # failures may still use an independently pinned institutional copy.
            if isinstance(error, urllib.error.HTTPError) and (
                error.code == 429 or error.code in TRANSIENT_HTTP and error.headers and error.headers.get('Retry-After')
            ):
                raise
            if i == len(urls) - 1:
                raise
            print(f'{name}: transport failed at {url}: {error}; trying verified institutional mirror', flush=True)
    # Integrity and format exceptions are deliberately not transport fallback.


def acquire(name, directory):
    manifest = json.loads((directory / 'acquisition.json').read_text(encoding='utf-8'))
    filename = manifest.get('document_filename', 'journal-article.pdf')
    if filename not in {'journal-article.pdf','source-book.pdf'}:
        raise ValueError('Unsupported local source document filename')
    destination = directory / filename
    if destination.exists():
        if name in {'melet-solomon-2010','uhlhorn-loop-2008','radenac-ngcc-2016'} and hashlib.sha256(destination.read_bytes()).hexdigest() != manifest['sha256']:
            raise ValueError('Changed retained Melet original; no rendition fallback')
        return verify(name, manifest, destination.read_bytes())
    if name in {'melet-solomon-2010','uhlhorn-loop-2008','radenac-ngcc-2016'}:
        from melet_hal_source import CURRENT_FILENAME
        current = directory / CURRENT_FILENAME
        if current.exists():return verify(name, manifest, current.read_bytes())
    data = download(name, manifest)
    if name in {'melet-solomon-2010','uhlhorn-loop-2008','radenac-ngcc-2016'} and hashlib.sha256(data).hexdigest() != manifest['sha256']:
        destination = directory / CURRENT_FILENAME
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
        data = acquire(name, directory)
        if name == 'melet-solomon-2010':
            from melet_hal_source import ORIGINAL_SHA
            if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
                print(f'{name}: full repository rendition retained unchanged separately; reviewed original pin preserved; excluded from Git')
                continue
        if name == 'uhlhorn-loop-2008':
            from uhlhorn_thesis_source import ORIGINAL_SHA
            if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
                print(f'{name}: unchanged176-page thesis graph verified; generated-cover response retained separately; excluded from Git')
                continue
        if name == 'radenac-ngcc-2016':
            from radenac_hal_source import ORIGINAL_SHA
            if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA:
                print(f'{name}: unchanged22-page article graph verified; generated-cover response retained separately; excluded from Git')
                continue
        print(f'{name}: local original verified; excluded from Git')


if __name__ == '__main__':
    main()
