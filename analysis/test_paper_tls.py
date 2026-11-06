"""A missing chain link must not weaken authenticity or trust unrelated hosts."""
import copy
import io
import json
import ssl
from pathlib import Path
from unittest.mock import patch

import pytest
import paper_tls as tls
import acquire_local_paper_fixtures as acquisition

MANIFEST={'source_url':tls.URL,'sha256':tls.PAPER_SHA}


def test_chen_source_uses_same_complete_chain_without_weakening_original_pin():
    manifest={'source_url':tls.CHEN_URL,'sha256':tls.CHEN_SHA}
    context=tls.options('chen-necc-2016',manifest,tls.CHEN_URL)['context']
    assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    assert not context.verify_flags & ssl.VERIFY_X509_PARTIAL_CHAIN
    with patch('urllib.request.urlopen',return_value=io.BytesIO(b'%PDF-1.7\nchanged')):
        with pytest.raises(ValueError,match='checksum'):acquisition.download_url('chen-necc-2016',manifest,tls.CHEN_URL)
    assert tls.options('chen-necc-2016',{**manifest,'sha256':'0'*64},tls.CHEN_URL)=={}
    assert tls.options('chen-necc-2016',manifest,tls.CHEN_URL.replace('Chen_etal_JGR2016.pdf','other.pdf'))=={}


@pytest.mark.parametrize('url',tls.ALIASES)
def test_scoped_context_requires_hostname_complete_chain_and_system_root(url):
    context=tls.options('qiu-chen-nec-2010',MANIFEST,url)['context']
    assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    assert not context.verify_flags & ssl.VERIFY_X509_PARTIAL_CHAIN
    assert context.minimum_version>=ssl.TLSVersion.TLSv1_2


@pytest.mark.parametrize('case',['name','receipt_url','pin','http','lookalike','path'])
def test_other_acquisition_identities_keep_ordinary_tls(case):
    name='qiu-chen-nec-2010';manifest=copy.deepcopy(MANIFEST);url=tls.URL
    if case=='name':name='another-paper'
    elif case=='receipt_url':manifest['source_url']='https://example.invalid/paper.pdf'
    elif case=='pin':manifest['sha256']='0'*64
    elif case=='http':url=url.replace('https:','http:')
    elif case=='lookalike':url=url.replace('www.soest.hawaii.edu','www.soest.hawaii.edu.example.invalid')
    elif case=='path':url=url.replace('QC_NEC.pdf','other.pdf')
    with patch('paper_tls.ssl.create_default_context') as creator:
        assert tls.options(name,manifest,url)=={}
        creator.assert_not_called()


def test_changed_chain_link_cannot_enter_trust_store(tmp_path,monkeypatch):
    path=tmp_path/tls.CHAIN;path.parent.mkdir(parents=True);path.write_bytes(b'changed')
    monkeypatch.setattr(tls,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='Changed scoped'):tls.options('qiu-chen-nec-2010',MANIFEST,tls.URL)


def test_qiu_transport_context_does_not_bypass_original_pdf_pin():
    with patch('urllib.request.urlopen',return_value=io.BytesIO(b'%PDF-1.7\nchanged')) as opener:
        with pytest.raises(ValueError,match='checksum'):
            acquisition.download_url('qiu-chen-nec-2010',MANIFEST,tls.URL)
    context=opener.call_args.kwargs['context']
    assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED


def test_chain_acquisition_receipt_matches_stored_public_certificate():
    import hashlib
    receipt=json.loads((tls.ROOT/'research/source-data/tls/acquisition.json').read_bytes())
    raw=(tls.ROOT/tls.CHAIN).read_bytes()
    assert receipt['pem_sha256']==tls.PIN==hashlib.sha256(raw).hexdigest()
    der=ssl.PEM_cert_to_DER_cert(raw.decode('ascii'))
    assert len(der)==receipt['source_der_bytes']
    assert hashlib.sha256(der).hexdigest()==receipt['source_der_sha256']
