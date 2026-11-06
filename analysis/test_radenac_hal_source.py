"""Protect the full reviewed Radenac article while accepting regenerated HAL covers."""
import hashlib
import io
import json
import re
import zlib

import pytest
from pypdf import PdfReader
from pypdf.generic import IndirectObject, StreamObject

import radenac_hal_source as source
import acquire_local_paper_fixtures as acquisition

BASE = source.resolve_source().read_bytes()
MANIFEST = json.loads((source.DIRECTORY/'acquisition.json').read_bytes())
# Controlled container-metadata variant, never saved over a source document.
_date = str(PdfReader(io.BytesIO(BASE)).metadata['/CreationDate'])[2:16].encode()
_new_date = b'20261018012345' if _date != b'20261018012345' else b'20261019012345'
assert BASE.count(_date) == 1
FRESH = BASE.replace(_date, _new_date, 1)
assert FRESH != BASE


def test_available_source_and_metadata_variant_preserve_complete_article():
    base_proof=source.verify_rendition(BASE, MANIFEST)
    assert base_proof['kind'] == ('exact_reviewed_original' if hashlib.sha256(BASE).hexdigest()==source.ORIGINAL_SHA else 'verified_generated_HAL_cover_rendition')
    proof = source.verify_rendition(FRESH, MANIFEST)
    assert proof['response_sha256'] == hashlib.sha256(FRESH).hexdigest()
    assert proof['reviewed_original_sha256'] == MANIFEST['sha256']
    contract = json.loads(source.CONTRACT.read_bytes())
    assert contract['journal_objects'] == 394 and contract['journal_pages'] == 22
    assert not set(contract['generated_cover_object_ids']) & set(contract['journal_object_ids'])
    assert acquisition.verify('radenac-ngcc-2016', MANIFEST, FRESH) == FRESH


@pytest.mark.parametrize('key,value', [('sha256','0'*64), ('source_url','https://example.invalid/other.pdf')])
def test_receipt_rebinding_is_rejected(key, value):
    with pytest.raises(ValueError, match='receipt'):
        source.verify_rendition(FRESH, {**MANIFEST, key:value})


def mutated_stream(kind):
    reader = PdfReader(io.BytesIO(FRESH), strict=True)
    contract = json.loads(source.CONTRACT.read_bytes())
    for key in contract['journal_object_ids']:
        oid, generation = map(int, key.split(':'))
        obj = reader.get_object(IndirectObject(oid, generation, reader))
        if kind == 'font' and obj.get('/Type') == '/FontDescriptor':
            ref = obj.get('/FontFile2') or obj.get('/FontFile3') or obj.get('/FontFile')
            if ref is not None:
                obj = ref.get_object()
            else:
                continue
        elif kind == 'image':
            if obj.get('/Subtype') != '/Image': continue
        elif kind == 'content':
            streams = reader.pages[12].raw_get('/Contents')
            ref = streams[0] if isinstance(streams, list) else streams
            obj = ref.get_object()
        else:
            continue
        if not isinstance(obj, StreamObject) or len(obj._data) < 20: continue
        payload = obj._data
        if FRESH.count(payload) != 1: continue
        changed = bytearray(payload); changed[len(changed)//2] ^= 1
        return FRESH.replace(payload, bytes(changed), 1)
    raise AssertionError('No unique scientific '+kind+' stream found')


@pytest.mark.parametrize('kind', ['content', 'font', 'image'])
def test_scientific_stream_and_resource_changes_reject(kind):
    with pytest.raises(ValueError, match='journal|protected'):
        source.verify_rendition(mutated_stream(kind), MANIFEST)


@pytest.mark.parametrize('kind', ['geometry', 'page_order'])
def test_geometry_and_page_order_changes_reject_without_rewriting_pdf(kind):
    reader = PdfReader(io.BytesIO(FRESH), strict=True)
    if kind == 'geometry':
        ref = reader.pages[1].indirect_reference
        old, new = b'629.972', b'630.972'
    else:
        ref = reader.trailer['/Root'].raw_get('/Pages')
        old, new = b'9 0 R 10 0 R', b'10 0 R 9 0 R'
    first = reader.xref[ref.generation][ref.idnum]
    last = FRESH.index(b'endobj', first)
    part = FRESH[first:last]
    assert old in part
    changed = FRESH[:first] + part.replace(old,new,1) + FRESH[last:]
    assert len(changed) == len(FRESH)
    with pytest.raises(ValueError, match='journal|protected'):
        source.verify_rendition(changed, MANIFEST)


def test_contract_change_rejects_even_after_positive_cache_hit(tmp_path, monkeypatch):
    source.verify_rendition(FRESH, MANIFEST)
    path = tmp_path/'changed-contract.json'; path.write_bytes(source.CONTRACT.read_bytes()+b' ')
    monkeypatch.setattr(source, 'CONTRACT', path)
    with pytest.raises(ValueError, match='contract'):
        source.verify_rendition(FRESH, MANIFEST)


def test_extra_unreferenced_pdf_object_rejects_with_article_unchanged():
    reader = PdfReader(io.BytesIO(FRESH), strict=True)
    next_id = max(oid for gen, entries in reader.xref.items() if gen!=65535 for oid in entries)+1
    previous = int(re.findall(rb'startxref\s+(\d+)\s+%%EOF', FRESH)[-1])
    prefix = FRESH+b'\n'
    obj = f'{next_id} 0 obj\n<< /Unreviewed (test) >>\nendobj\n'.encode()
    xref = f'xref\n{next_id} 1\n{len(prefix):010d} 00000 n \n'.encode()
    trailer = f'trailer\n<< /Size {next_id+1} /Root 1 0 R /Info 8 0 R /Prev {previous} >>\nstartxref\n{len(prefix)+len(obj)}\n%%EOF\n'.encode()
    changed = prefix+obj+xref+trailer
    assert source.describe(changed)['journal_graph_sha256'] == source.describe(FRESH)['journal_graph_sha256']
    with pytest.raises(ValueError, match='inventory'):
        source.verify_rendition(changed, MANIFEST)


def test_nonvolatile_metadata_change_rejects():
    producer = b'/Producer <FEFF005000440046004C0061005400650058>'
    assert FRESH.count(producer) == 1
    changed = FRESH.replace(producer, producer[:-2]+b'9>', 1)
    with pytest.raises(ValueError, match='metadata|identity'):
        source.verify_rendition(changed, MANIFEST)


def test_changed_cover_text_rejects_even_in_allowed_cover_stream():
    reader = PdfReader(io.BytesIO(FRESH), strict=True)
    ref = reader.pages[0]['/Contents'][0]
    stream = ref.get_object()
    decoded = stream.get_data()
    match = re.search(rb'<[0-9A-Fa-f]{4}>', decoded)
    assert match is not None
    position = match.start()+4
    replacement = ord('1') if decoded[position] != ord('1') else ord('2')
    candidate = decoded[:position]+bytes([replacement])+decoded[position+1:]
    compressed = zlib.compress(candidate)
    previous = int(re.findall(rb'startxref\s+(\d+)\s+%%EOF', FRESH)[-1])
    size = max(oid for gen, entries in reader.xref.items() if gen!=65535 for oid in entries)+1
    # Synthetic incremental cover update: all existing source bytes and every
    # article object remain unchanged; no object IDs are added or removed.
    prefix = FRESH+b'\n'
    obj = f'{ref.idnum} 0 obj\n<< /Filter /FlateDecode /Length {len(compressed)} >>\nstream\n'.encode()+compressed+b'\nendstream\nendobj\n'
    xref = f'xref\n{ref.idnum} 1\n{len(prefix):010d} 00000 n \n'.encode()
    trailer = f'trailer\n<< /Size {size} /Root 1 0 R /Info 8 0 R /Prev {previous} >>\nstartxref\n{len(prefix)+len(obj)}\n%%EOF\n'.encode()
    changed = prefix+obj+xref+trailer
    before, after = source.describe(FRESH), source.describe(changed)
    assert after['journal_graph_sha256'] == before['journal_graph_sha256']
    assert after['cover_text_sha256'] != before['cover_text_sha256']
    assert set(after['object_sha256']) == set(before['object_sha256'])
    with pytest.raises(ValueError, match='identity'):
        source.verify_rendition(changed, MANIFEST)


def test_actual_fresh_acquisition_stages_verified_response_separately(tmp_path, monkeypatch):
    (tmp_path/'acquisition.json').write_text(json.dumps(MANIFEST), encoding='utf8')
    monkeypatch.setattr('urllib.request.urlopen', lambda *args,**kwargs: io.BytesIO(FRESH))
    assert acquisition.acquire('radenac-ngcc-2016', tmp_path) == FRESH
    assert not (tmp_path/'journal-article.pdf').exists()
    assert (tmp_path/source.CURRENT_FILENAME).read_bytes() == FRESH
    assert source.resolve_source(tmp_path) == tmp_path/source.CURRENT_FILENAME
    assert not list(tmp_path.glob('.paper-*'))


def test_corrupt_retained_original_cannot_use_valid_rendition(tmp_path, monkeypatch):
    (tmp_path/'acquisition.json').write_text(json.dumps(MANIFEST), encoding='utf8')
    (tmp_path/'journal-article.pdf').write_bytes(FRESH)
    (tmp_path/source.CURRENT_FILENAME).write_bytes(FRESH)
    with pytest.raises(ValueError, match='retained'):
        source.resolve_source(tmp_path)
    monkeypatch.setattr('urllib.request.urlopen', lambda *args,**kwargs: pytest.fail('Unexpected provider call'))
    with pytest.raises(ValueError, match='retained'):
        acquisition.acquire('radenac-ngcc-2016', tmp_path)


@pytest.mark.parametrize('kind', ['original','generated-cover'])
def test_cli_reports_both_verified_response_kinds(kind, monkeypatch, capsys):
    data = BASE if kind == 'original' else FRESH
    # Isolate reporting after acquire() has verified the response. CI may only
    # possess a generated cover; this does not manufacture an original PDF.
    if kind == 'original':
        monkeypatch.setattr(source, 'ORIGINAL_SHA', hashlib.sha256(data).hexdigest())
    message = 'local original verified' if kind == 'original' else 'unchanged22-page article graph verified'
    monkeypatch.setattr(acquisition, 'PAPERS', ('radenac-ngcc-2016',))
    monkeypatch.setattr(acquisition, 'acquire', lambda name,directory: data)
    acquisition.main()
    assert message in capsys.readouterr().out
