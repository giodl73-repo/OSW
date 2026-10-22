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
    for name in bundle['manifest']['canonical_collections']:
        original = json.loads((ROOT / 'almanac/release/v0.1.0' / (name + '.json')).read_bytes())
        current = bundle['collections'][name]
        ids = {r['id'] for r in original}
        assert len(ids) == len(original), name
        assert len({r['id'] for r in current}) == len(current), name
        expected = [overrides.get(name, {}).get(r['id'], r) for r in original]
        assert [r for r in current if r['id'] in ids] == expected, name
        assert set(overrides.get(name, {})) <= ids, name
