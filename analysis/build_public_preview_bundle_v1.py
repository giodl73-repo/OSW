"""Package an explicit, scope-checked website. Scientific data is copied as bytes."""
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/public-preview-bundle-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ['href', 'src', 'xlink:href']:
            if attrs.get(key):
                self.links.append(attrs[key])


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    started = time.monotonic()
    site, delivery = OUT / 'site', OUT / 'delivery'
    site.mkdir(parents=True)
    delivery.mkdir()
    # Administrative manifests only. No decompression or numerical data parsing.
    data_root = 'almanac/preview-data-screened-v1/'
    build_raw = (ROOT / data_root / 'build.json').read_bytes()
    build = json.loads(build_raw)
    review_root = 'almanac/preview-review-v1/'
    review = json.loads((ROOT / review_root / 'screened-manifest.json').read_bytes())
    assert sha(build_raw) == review['data_build_sha256']
    scope_raw = (ROOT / data_root / 'scope-screen.json').read_bytes()
    scope = json.loads(scope_raw)
    assert sha(scope_raw) == build['scope_screen_sha256'] == review['asset_scope_screen_sha256']
    assert scope['status'] == 'PASS_ASSET_METADATA_SCREEN_ONLY'
    assert not any(scope[k] for k in ['forbidden_field_names', 'held_source_urls', 'unreviewed_source_urls'])
    assert build['counts'] == {'named_current': 111, 'named_eddy': 40}
    assert (build['depth_reference_count'], build['eddy_reference_count'], build['eddy_size_reference_count']) == (941, 331, 203)
    files = {}

    def copy(source, target=None, expected=None):
        raw = (ROOT / source).read_bytes()
        if expected:
            assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], source
        assert raw.decode('utf8').encode('utf8') == raw
        target = target or source
        assert not target.startswith(('/', '../')) and '..' not in Path(target).parts and target not in files
        files[target] = raw

    for source, target in [('preview-home.html', 'index.html'), ('preview-methods.html', 'methods.html'), ('LICENSE', 'LICENSE')]:
        copy(source, target)
    for source in ['almanac/atlas.html', 'almanac/explore.html', 'almanac/explore.js', 'almanac/explore.css',
                   'almanac/public-map.js', 'almanac/public-map.css', 'almanac/preview-data.js',
                   'figures/ocean-motion-dashboard-ground.svg']:
        copy(source)
    public_js = files['almanac/public-map.js'].decode('utf8')
    original = "const publicPreview = document.body.dataset.publicPreview === 'true';"
    assert original in public_js
    files['almanac/public-map.js'] = public_js.replace(original, 'const publicPreview = true;').encode('utf8')
    for receipt in build['files']:
        copy(data_root + receipt['path'], expected=receipt)
    copy(data_root + 'build.json')
    copy(data_root + 'scope-screen.json')
    copy(review_root + 'screened-manifest.json')
    for receipt in review['files']:
        copy(review_root + receipt['path'], expected=receipt)
    files['.nojekyll'] = b''
    edition = {'schema': 'osw.public-preview-edition.v1', 'version': '2026.11.1-preview',
               'status': 'review_candidate_not_yet_published', 'prepared_date': '2026-11-08',
               'author': {'given_names': 'Gio', 'family_names': 'Della-Libera'},
               'source_commit': os.environ['GITHUB_SHA'], 'data_build_sha256': sha(build_raw),
               'scope_screen_sha256': sha(scope_raw), 'scope': 'Current and eddy reference atlas, with source-scoped dimensions and qualified region associations.',
               'counts': build['counts'], 'current_depth_references': 941, 'eddy_evidence_references': 331,
               'eddy_size_references': 203, 'not_a_distinct_physical_eddy_count': True,
               'repository': 'https://github.com/giodl73-repo/OSW', 'publication_approved': False}
    files['preview-edition.json'] = (json.dumps(edition, indent=2) + '\n').encode('utf8')
    parsers = {}
    for path, raw in files.items():
        if path.endswith(('.html', '.svg')):
            parser = Links()
            parser.feed(raw.decode('utf8'))
            parsers[path] = parser
    checked = []
    for path, parser in parsers.items():
        for url in parser.links:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc:
                assert parsed.scheme in {'https', 'http', 'data', 'mailto'}, (path, url)
                continue
            target = (site / path).parent / unquote(parsed.path) if parsed.path else site / path
            target = target.resolve()
            assert target.is_relative_to(site.resolve()), (path, url)
            relative = target.relative_to(site.resolve()).as_posix()
            if not parsed.path or parsed.path.endswith('/') or relative == '.':
                relative = (relative.rstrip('/') + '/index.html').lstrip('./') if relative != path else path
            assert relative in files, ('Unbundled local link', path, url, relative)
            if parsed.fragment and relative in parsers:
                assert unquote(parsed.fragment) in parsers[relative].ids, ('Missing anchor', path, url)
            checked.append({'page': path, 'target': relative})
    forbidden = ('research/', 'source-data/', 'query-parts/', 'display-data-v1/', 'preview-data-candidate-v1/')
    assert not any(any(part in path for part in forbidden) for path in files)
    assert not any(path.endswith(('.wasm', '.pdf', '.nc', '.mat', '.csv', '.zip')) for path in files)
    total = sum(map(len, files.values()))
    assert total < 2_400_000, ('Selected website byte cap', total)
    for path, raw in files.items():
        target = site / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    report = {'schema': 'osw.public-preview-bundle.v1', 'status': 'PASS_SELECTED_SITE_BUILD_ONLY',
              'source_commit': os.environ['GITHUB_SHA'], 'version': edition['version'],
              'site_bytes': total, 'file_count': len(files), 'local_links_checked': len(checked),
              'files': [{'path': path, 'bytes': len(raw), 'sha256': sha(raw)} for path, raw in sorted(files.items())],
              'data_build_sha256': sha(build_raw), 'scope_screen_sha256': sha(scope_raw),
              'scientific_values_read_or_recalculated': False, 'new_provider_requests': 0,
              'active_seconds': time.monotonic() - started, 'publication_approved': False}
    (delivery / 'bundle-result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    with zipfile.ZipFile(delivery / 'public-preview-site.zip', 'w') as archive:
        for path, raw in sorted(files.items()):
            info = zipfile.ZipInfo(path, date_time=(2026, 11, 8, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw)
    print(json.dumps({k: report[k] for k in ['status', 'file_count', 'site_bytes', 'local_links_checked', 'active_seconds']}))


if __name__ == '__main__':
    main()
