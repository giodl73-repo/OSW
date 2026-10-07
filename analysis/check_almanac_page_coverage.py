"""Require a declared validation path for every almanac HTML surface."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit
from run_rust_query_browser_checks import CHECKS

ROOT = Path(__file__).resolve().parents[1]


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.script_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.script_count += 1
        if tag == 'script' and (src := dict(attrs).get('src')):
            self.paths.append(src)


def main():
    doc = json.loads((ROOT/'plans/almanac-page-coverage.json').read_bytes())
    if doc['schema'] != 'osw.almanac-page-coverage.v1':
        raise ValueError('Unsupported page coverage schema')
    declared = {r['page']:r for r in doc['pages']}
    if len(declared) != len(doc['pages']):
        raise ValueError('Duplicate page coverage address')
    actual = {p.relative_to(ROOT/'almanac').as_posix() for p in (ROOT/'almanac').rglob('*.html')}
    if actual != set(declared):
        raise ValueError(f'Page coverage mismatch: undeclared={sorted(actual-set(declared))}, missing={sorted(set(declared)-actual)}')
    counts = {}
    for address,row in declared.items():
        page = ROOT/'almanac'/address
        parser = Scripts()
        parser.feed(page.read_text(encoding='utf-8'))
        scripts = []
        for src in parser.paths:
            url = urlsplit(src)
            if url.scheme or url.netloc:
                raise ValueError('Unreviewed remote page script: '+address)
            path = (page.parent/url.path).resolve()
            path.relative_to(ROOT)
            if not path.is_file():
                raise ValueError('Missing page script: '+src)
            scripts.append(url.path)
        kind = row['kind']
        counts[kind] = counts.get(kind,0)+1
        if kind == 'current_wasm':
            if row['entrypoint'] not in scripts or row['browser_check'] not in CHECKS:
                raise ValueError('WASM page has no registered entrypoint/check: '+address)
            if not (ROOT/'analysis'/row['browser_check']).is_file():
                raise ValueError('Missing browser check: '+address)
        elif kind == 'static_diagnostic':
            if parser.script_count:
                raise ValueError('Static diagnostic unexpectedly became interactive: '+address)
            for field in ['source_builder','source_test']:
                if not (ROOT/row[field]).is_file():
                    raise ValueError('Missing static validation source: '+address)
        elif kind == 'frozen_preview':
            if not row.get('scope') or not (ROOT/row['checker']).is_file():
                raise ValueError('Missing frozen preview scope/checker: '+address)
        else:
            raise ValueError('Unknown page coverage kind: '+kind)
    print(f'PASS: {len(actual)} almanac pages assigned validation: {counts}. Assignments do not establish passing tests or mainline publication.')


if __name__ == '__main__':
    main()
