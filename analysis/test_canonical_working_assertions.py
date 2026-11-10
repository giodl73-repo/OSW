"""Coverage admits only documented overrides while retaining every frozen row."""
import copy
import hashlib
import json

import pytest
from canonical_working_assertions import ROOT, assert_canonical_imports


def fixture():
    names = ['sources', 'length_assessments', 'entities']
    collections = {n: json.loads((ROOT / 'almanac/release/v0.1.0' / (n + '.json')).read_bytes()) for n in names}
    pins = {}
    for path, collection, key in [
        ('research/agulhas-vinayachandran-2021-reported-dimensions.json', 'sources', 'source_record'),
        ('research/north-atlantic-nominal-gate-bound.json', 'length_assessments', 'length_assessment'),
    ]:
        raw = (ROOT / path).read_bytes()
        pins[path] = hashlib.sha256(raw).hexdigest()
        row = json.loads(raw)[key]
        collections[collection] = [row if r['id'] == row['id'] else r for r in collections[collection]]
    return {'manifest': {'canonical_collections': names, 'input_sha256': pins}, 'collections': collections}


def test_accepts_pinned_overrides_and_actual_shipped_canonical_imports():
    assert_canonical_imports(fixture())
    from query_packet import read_bundle_bytes
    assert_canonical_imports(json.loads(read_bundle_bytes(ROOT / 'almanac/query-data.json')))


@pytest.mark.parametrize('kind', ['other_frozen_row', 'admitted_rank', 'missing_frozen_row', 'duplicate', 'reorder', 'stripped_pin'])
def test_rejects_undocumented_changes(kind):
    b = copy.deepcopy(fixture())
    if kind == 'other_frozen_row':
        b['collections']['entities'][0]['label'] = 'Changed'
    elif kind == 'admitted_rank':
        next(r for r in b['collections']['length_assessments'] if r['entity_id'] == 'current:north-atlantic')['rank_eligible'] = True
    elif kind == 'missing_frozen_row':
        b['collections']['entities'].pop()
    elif kind == 'duplicate':
        b['collections']['entities'].append(b['collections']['entities'][0])
    elif kind == 'reorder':
        b['collections']['entities'].reverse()
    else:
        b['manifest']['input_sha256'].pop('research/north-atlantic-nominal-gate-bound.json')
    with pytest.raises(AssertionError):
        assert_canonical_imports(b)
