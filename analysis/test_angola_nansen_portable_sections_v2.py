"""Prospective synthetic checks; no actual Angola field calculation here."""
import copy
import gzip
import hashlib
import json

import pytest
from angola_nansen_portable_sections_v2 import canonicalize


def fixture():
    raw = b'{"values":[null,-0.0,1.25],"units":"m/s"}\n'
    old, new = gzip.compress(raw, mtime=0), gzip.compress(raw, mtime=1)
    sha = lambda b: hashlib.sha256(b).hexdigest()
    section = {'id': 'synthetic:1', 'field_file': 'old.gz',
               'field_sha256': sha(old), 'field_bytes': len(old),
               'decoded_sha256': sha(raw), 'decoded_bytes': len(raw),
               'dimensions': {'PROFILE': 1, 'DEPTH': 3}}
    retained = {'schema': 'synthetic.v1', 'sections': [section],
                'physical_width_admitted': False, 'proposed_current_id': 'synthetic'}
    rebuilt = copy.deepcopy(retained)
    rebuilt['sections'][0].update(field_sha256=sha(new), field_bytes=len(new))
    mirrors = [{'section_id': 'synthetic:1', 'compressed_source_file': 'old.gz',
                'compressed_source_sha256': sha(old), 'source_file': 'raw.json',
                'source_sha256': sha(raw), 'source_bytes': len(raw)}]
    storage = {'old.gz': old, 'raw.json': raw}
    return retained, rebuilt, {'old.gz': new}, mirrors, storage


def test_compression_only_difference_keeps_every_decoded_byte_and_inputs():
    retained, rebuilt, products, mirrors, storage = fixture()
    before = copy.deepcopy((retained, rebuilt, products, mirrors, storage))
    result = canonicalize(retained, rebuilt, products, mirrors, storage.__getitem__)
    assert result['sections'][0]['field_file'] == 'raw.json'
    assert result['sections'][0]['field_encoding'] == 'identity-json'
    assert result['sections'][0]['field_sha256'] == retained['sections'][0]['decoded_sha256']
    assert json.loads(storage['raw.json'])['values'] == [None, -0.0, 1.25]
    assert b'-0.0' in storage['raw.json']
    assert result['native_decoded_fields_rebuilt_exactly'] is True
    assert result['legacy_compressed_reencoding_claimed'] is False
    assert result['legacy_compressed_artifact_custody'][0]['field_sha256'] == retained['sections'][0]['field_sha256']
    assert (retained, rebuilt, products, mirrors, storage) == before


@pytest.mark.parametrize('change', ['owner', 'dimension', 'promotion', 'decoded_hash'])
def test_nontransport_report_changes_reject(change):
    retained, rebuilt, products, mirrors, storage = fixture()
    if change == 'owner': rebuilt['proposed_current_id'] = 'other'
    elif change == 'dimension': rebuilt['sections'][0]['dimensions']['DEPTH'] = 2
    elif change == 'promotion': rebuilt['physical_width_admitted'] = True
    else: rebuilt['sections'][0]['decoded_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='beyond compressed'):
        canonicalize(retained, rebuilt, products, mirrors, storage.__getitem__)


@pytest.mark.parametrize('change', ['native_value', 'legacy_bytes', 'mirror_bytes',
                                  'missing_product', 'extra_product', 'missing_mirror',
                                  'duplicate_mirror', 'mirror_owner', 'mirror_hash'])
def test_changed_or_incomplete_native_transport_rejects(change):
    retained, rebuilt, products, mirrors, storage = fixture()
    if change == 'native_value': products['old.gz'] = gzip.compress(b'{"different":1}')
    elif change == 'legacy_bytes': storage['old.gz'] += b'changed'
    elif change == 'mirror_bytes': storage['raw.json'] += b' '
    elif change == 'missing_product': products.clear()
    elif change == 'extra_product': products['extra.gz'] = products['old.gz']
    elif change == 'missing_mirror': mirrors.clear()
    elif change == 'duplicate_mirror': mirrors.append(copy.deepcopy(mirrors[0]))
    elif change == 'mirror_owner': mirrors[0]['section_id'] = 'other'
    elif change == 'mirror_hash': mirrors[0]['source_sha256'] = '0' * 64
    with pytest.raises(ValueError):
        canonicalize(retained, rebuilt, products, mirrors, storage.__getitem__)
