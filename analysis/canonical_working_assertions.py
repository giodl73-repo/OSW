"""Frozen rows survive in order; only explicitly pinned working overrides differ."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def assert_canonical_imports(bundle):
    overrides = {}
    for path, collection, key in [
        ('research/agulhas-vinayachandran-2021-reported-dimensions.json', 'sources', 'source_record'),
        ('research/north-atlantic-nominal-gate-bound.json', 'length_assessments', 'length_assessment'),
    ]:
        pin = bundle['manifest']['input_sha256'].get(path)
        if pin is None:
            continue
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == pin, path
        row = json.loads(raw)[key]
        overrides.setdefault(collection, {})[row['id']] = row
    rank_updates = {}
    path = 'research/norwegian-atlantic-slope-working-admission.json'
    if path in bundle['manifest']['input_sha256']:
        raw = (ROOT / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == bundle['manifest']['input_sha256'][path], path
        rank_updates = {r['id']: r['working_rank'] for r in json.loads(raw)['rank_updates']}
    for name in bundle['manifest']['canonical_collections']:
        original = json.loads((ROOT / 'almanac/release/v0.1.0' / (name + '.json')).read_bytes())
        current = bundle['collections'][name]
        ids = {r['id'] for r in original}
        assert len(ids) == len(original), name
        assert len({r['id'] for r in current}) == len(current), name
        expected = [dict(overrides.get(name, {}).get(r['id'], r)) for r in original]
        if name == 'length_assessments':
            for row in expected:
                if row['id'] in rank_updates:
                    row['published_rank'] = rank_updates[row['id']]
        assert [r for r in current if r['id'] in ids] == expected, name
        assert set(overrides.get(name, {})) <= ids, name
