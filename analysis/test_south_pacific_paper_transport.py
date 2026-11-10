"""The final repository path is transport only; scientific source pin is fixed."""
import copy
import io
import json
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest
import acquire_local_paper_fixtures as acquisition

DIRECTORY=Path(__file__).resolve().parents[1]/'research/source-data/stramma-south-pacific-1995'
MANIFEST=json.loads((DIRECTORY/'acquisition.json').read_bytes())
NAME='stramma-south-pacific-1995'
FINAL='https://oceanrep.geomar.de/id/eprint/32120/1/1520-0485(1995)025_0077_tspc_2.0.co;2.pdf'


def test_403_legacy_path_uses_verified_final_path_with_same_original():
    original=(DIRECTORY/'journal-article.pdf').read_bytes();before=copy.deepcopy(MANIFEST)
    with patch('urllib.request.urlopen',side_effect=[HTTPError(MANIFEST['source_url'],403,'forbidden',{},None),io.BytesIO(original)]) as opener:
        assert acquisition.download(NAME,MANIFEST)==original
    assert [call.args[0].full_url for call in opener.call_args_list]==[MANIFEST['source_url'],FINAL]
    assert MANIFEST==before


@pytest.mark.parametrize('field,value',[('sha256','0'*64),('source_url','https://example.invalid/paper.pdf')])
def test_changed_receipt_cannot_use_final_path(field,value):
    manifest=dict(MANIFEST);manifest[field]=value
    with patch('urllib.request.urlopen',side_effect=HTTPError(manifest['source_url'],403,'forbidden',{},None)) as opener:
        with pytest.raises(HTTPError):acquisition.download(NAME,manifest)
    assert opener.call_count==1


def test_changed_final_response_never_becomes_local_original(tmp_path):
    (tmp_path/'acquisition.json').write_text(json.dumps(MANIFEST),encoding='utf8')
    with patch('urllib.request.urlopen',side_effect=[HTTPError(MANIFEST['source_url'],403,'forbidden',{},None),io.BytesIO(b'%PDF-1.7\nchanged')]):
        with pytest.raises(ValueError,match='checksum'):acquisition.acquire(NAME,tmp_path)
    assert not (tmp_path/'journal-article.pdf').exists()
    assert not list(tmp_path.glob('.paper-*.tmp'))
