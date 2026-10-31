"""Actual-source v2 report and complete canonical-field custody chain."""
import gzip
import hashlib
import json

from angola_nansen_portable_sections_v2 import ROOT, LEGACY_REPORT, verify


def test_every_portable_field_preserves_every_v1_decoded_byte():
    report = verify()
    legacy = json.loads((ROOT / LEGACY_REPORT).read_bytes())
    assert report['section_count'] == 11
    assert report['profile_count'] == legacy['profile_count'] == 6148
    assert report['velocity_cells_per_component'] == 1022160
    assert report['native_decoded_fields_rebuilt_exactly'] is True
    assert report['legacy_compressed_reencoding_claimed'] is False
    assert report['physical_width_admitted'] is False
    assert report['canonical_current_identity_admitted'] is False
    assert report['members'] == legacy['members']
    for section, old in zip(report['sections'], legacy['sections']):
        raw = (ROOT / section['field_file']).read_bytes()
        assert section['id'] == old['id']
        assert section['field_encoding'] == 'identity-json'
        assert raw == gzip.decompress((ROOT / old['field_file']).read_bytes())
        assert hashlib.sha256(raw).hexdigest() == section['field_sha256'] == old['decoded_sha256']
        assert len(raw) == section['field_bytes'] == old['decoded_bytes']
        assert section['variable_summaries'] == old['variable_summaries']
