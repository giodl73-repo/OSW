"""Real source responses vary only in the PDF's second file identifier."""
import hashlib,json,pytest
from acquire_local_paper_fixtures import ROOT,verify
NAME='sasaki-kuroshio-extension-2013'
DIRECTORY=ROOT/'research/source-data'/NAME

def original():return (DIRECTORY/'journal-article.pdf').read_bytes()
def manifest():return json.loads((DIRECTORY/'acquisition.json').read_bytes())
def changed_id():
    data=original()
    return data[:3831094]+b'12b0a7780104cd91d6cc6e8ce8ce66df'+data[3831126:]
def test_exact_fixture_and_reviewed_response_id():
    assert verify(NAME,manifest(),original())==original()
    raw=changed_id()
    assert hashlib.sha256(raw).hexdigest()=='28839ca252e2fd502d91b42626896dfd6fa5dac2d0ee6c4178e14408a95135d4'
    assert verify(NAME,manifest(),raw)==original()
@pytest.mark.parametrize('offset',[100,100000,3831057,3831130])
def test_every_other_byte_stays_pinned(offset):
    raw=bytearray(changed_id());raw[offset]^=1
    with pytest.raises(ValueError):verify(NAME,manifest(),bytes(raw))
def test_wrong_owner_size_and_unpinned_target_rejected():
    raw=changed_id()
    with pytest.raises(ValueError):verify('other-paper',manifest(),raw)
    with pytest.raises(ValueError):verify(NAME,manifest(),raw+b' ')
    m=manifest();m['sha256']='0'*64
    with pytest.raises(ValueError):verify(NAME,m,raw)
