"""Inventory source-use evidence in the actual display package, without a license inference."""
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.pytest_cache/public-display-sources-v1'
PACKAGE = ROOT / 'almanac/display-data-v1'
REVIEWS = ROOT / 'research/ocean-motion-source-use-reviews.json'


def refs(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            pointer = path + '/' + key
            if key.endswith('source_id') and isinstance(child, str):
                yield pointer, child
            elif key.endswith('source_ids') and isinstance(child, list):
                for index, item in enumerate(child):
                    if isinstance(item, str):
                        yield pointer + '/' + str(index), item
            else:
                yield from refs(child, pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from refs(child, path + '/' + str(index))


def text_flags(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            pointer = path + '/' + key
            if isinstance(child, str) and re.search(r'quote|excerpt|passage|source_text|raw_text|transcript', key):
                yield {'pointer': pointer, 'field': key, 'words': len(child.split()), 'bytes': len(child.encode('utf8'))}
            else:
                yield from text_flags(child, pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from text_flags(child, path + '/' + str(index))


def main():
    assert os.environ.get('GITHUB_ACTIONS') == 'true'
    assert len(os.sched_getaffinity(0)) == 1 and os.getpriority(os.PRIO_PROCESS, 0) >= 15
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    start = time.monotonic()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('Source-use inventory deadline')))
    signal.alarm(55)
    ledger = json.loads(REVIEWS.read_bytes())
    reviews = {r['url']: r for r in ledger['entries']}
    build = json.loads((PACKAGE / 'build.json').read_bytes())
    sources = {}
    uses = defaultdict(list)
    missing = defaultdict(set)
    schemas = defaultdict(set)
    kinds = Counter()
    quoted = []
    map_roles = Counter()
    objects = []
    total = 0
    for receipt in build['files']:
        raw = (PACKAGE / receipt['path']).read_bytes()
        total += len(raw)
        assert total <= 32_000_000
        assert hashlib.sha256(raw).hexdigest() == receipt['sha256'] and len(raw) == receipt['bytes']
        if not receipt['path'].startswith('records/'):
            continue
        record = json.loads(raw)
        identifier = record['id']
        obj = record['object']
        kinds[obj['type']] += 1
        schemas['object'].update(obj)
        schemas['map_feature'].update(k for feature in obj.get('map_features', []) for k in feature)
        for feature in obj.get('map_features', []):
            map_roles[str(feature.get('role'))] += 1
        for key in ['measurements', 'widths', 'reference_routes', 'sources']:
            for row in record[key]:
                schemas[key].update(row)
        by_id = {s['id']: s for s in record['sources']}
        for source in record['sources']:
            if source['id'] in sources:
                assert sources[source['id']] == source, 'Conflicting source metadata'
            sources[source['id']] = source
        identity_refs = list(refs(obj))
        objects.append({'id': identifier, 'type': obj['type'], 'identity_source_ids': sorted({s for _, s in identity_refs}),
                        'primary_source_id': obj.get('source_id'),
                        'measurement_rows': len(record['measurements']), 'width_rows': len(record['widths']),
                        'reference_route_rows': len(record['reference_routes'])})
        for pointer, source_id in refs(record):
            if source_id not in by_id:
                missing[source_id].add(identifier)
            uses[source_id].append({'object_id': identifier, 'type': obj['type'], 'pointer': pointer})
        quoted.extend({'object_id': identifier, **flag} for flag in text_flags(record))
    rows = []
    for source_id, source in sorted(sources.items()):
        url = source.get('url')
        review = reviews.get(url, {})
        status = review.get('rights_review_status', '')
        rows.append({'id': source_id, 'url': url, 'title': source.get('title') or source.get('label'),
                     'kind': source.get('kind'), 'packaged_rights_status': source.get('rights_status'),
                     'matched_review_status': status or None, 'material_use_class': review.get('material_use_class'),
                     'review_note': review.get('review_note'), 'policy_reference_url': review.get('policy_reference_url'),
                     'reviewed_url_for_current_use': status.startswith('reviewed'),
                     'object_count': len({r['object_id'] for r in uses[source_id]}),
                     'object_types': dict(Counter(r['type'] for r in {r['object_id']: r for r in uses[source_id]}.values())),
                     'example_references': uses[source_id][:8]})
    report = {'schema': 'osw.public-display-source-inventory.v1', 'status': 'SOURCE_USE_RECONCILIATION_REQUIRED',
              'source_commit': os.environ['GITHUB_SHA'], 'scope': 'Exact installed display package, including downloadable record fields',
              'independent_question': 'Which source-use decisions and text fields govern the actual display candidate?',
              'prior_charges': {'numeric_tokens': 0, 'json_bytes': 0, 'active_seconds': 0},
              'review_ledger_sha256': hashlib.sha256(REVIEWS.read_bytes()).hexdigest(),
              'display_build_sha256': hashlib.sha256((PACKAGE / 'build.json').read_bytes()).hexdigest(),
              'json_input_bytes': total, 'object_counts': dict(kinds), 'source_count': len(rows),
              'sources': rows, 'objects': objects, 'schema_fields': {k: sorted(v) for k, v in schemas.items()},
              'missing_source_rows': [{'id': k, 'object_ids': sorted(v)} for k, v in sorted(missing.items())],
              'potential_quoted_text_fields': quoted, 'map_roles': dict(map_roles),
              'approved_for_publication': False,
              'limits': 'A matching URL review is not blanket permission for every field, geometry, quote, or provider-derived value.',
              'active_seconds': time.monotonic() - start}
    raw = (json.dumps(report, indent=2) + '\n').encode('utf8')
    assert len(raw) <= 2_400_000
    (OUT / 'result.json').write_bytes(raw)
    signal.alarm(0)
    print(json.dumps({'status': report['status'], 'sources': len(rows), 'missing_source_rows': len(missing),
                      'potential_quoted_fields': len(quoted), 'active_seconds': report['active_seconds']}))


if __name__ == '__main__':
    main()
