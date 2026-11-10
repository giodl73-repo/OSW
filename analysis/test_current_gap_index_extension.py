import copy
import pytest
import current_gap_index_extension as index
import current_gap_candidate_metadata as metadata


def fixture():
    old = {'research/original.json': '{ "value": 42 }\n', metadata.DASHBOARD: '{"entries":[]}\n'}
    descriptors = [{'path': path, 'source_sha256': metadata.digest(raw.encode()),
                    'source_bytes': len(raw.encode()), 'optional': False}
                   for path, raw in old.items()]
    return ({'schema': 'osw.almanac-index-catalog.v1', 'documents': descriptors, 'source_count': 2},
            {'schema': 'osw.almanac-index-bundle.v1', 'documents': old},
            {'schema': 'osw.almanac-index-sources.v1', 'documents': list(old)},
            {'research/new.json': b'{"value":100}\n', metadata.DASHBOARD: b'{"entries":[1]}\n'})


def test_exact_historical_source_text_survives_extension():
    args = fixture()
    before = copy.deepcopy(args)
    catalog, corpus, registry, audit = index.extend(*args)
    assert args == before
    assert corpus['documents']['research/original.json'] == '{ "value": 42 }\n'
    assert catalog['source_count'] == 3
    assert set(registry['documents']) == set(corpus['documents'])
    assert audit['replaced_source_paths'] == [metadata.DASHBOARD]
    assert audit['original_source_strings_preserved'] == 1
    assert audit['scientific_source_documents_replaced'] == 0


@pytest.mark.parametrize('mutation', ['old-bytes', 'old-inventory', 'overwrite', 'escape', 'non-json'])
def test_rejects_bad_custody_without_mutating_inputs(mutation):
    args = list(fixture())
    if mutation == 'old-bytes': args[1]['documents']['research/original.json'] = '{}'
    if mutation == 'old-inventory': args[0]['documents'].pop()
    if mutation == 'overwrite': args[3]['research/original.json'] = b'{"value":43}'
    if mutation == 'escape': args[3]['research/../outside.json'] = b'{}'
    if mutation == 'non-json': args[3]['research/new.json'] = b'1'
    before = copy.deepcopy(args)
    with pytest.raises(ValueError): index.extend(*args)
    assert args == before
