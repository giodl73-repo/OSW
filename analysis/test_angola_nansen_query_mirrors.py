"""Decoded query copies preserve exact native field bytes and reject corruption."""
import gzip
from unittest.mock import patch
from pathlib import Path
import pytest
from prepare_angola_query_sources import ROOT, verify


def test_all_query_sources_are_exact_decoded_native_fields():
    manifest=verify()
    assert len(manifest['documents'])==11
    for row in manifest['documents']:
        assert (ROOT/row['source_file']).read_bytes()==gzip.decompress((ROOT/row['compressed_source_file']).read_bytes())
    assert manifest['physical_width_admitted'] is False


def test_query_source_corruption_is_rejected_without_writing_inputs():
    row=verify()['documents'][0];target=ROOT/row['source_file'];original=Path.read_bytes
    def altered(path):return original(path)+b' ' if path==target else original(path)
    with patch.object(Path,'read_bytes',altered),pytest.raises(ValueError,match='Changed exact native query-source mirror'):
        verify()
