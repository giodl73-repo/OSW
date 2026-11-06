"""Transport changes must preserve logical bytes and reject partial/tampered data."""
import copy
import json
from pathlib import Path
import pytest
from query_packet import PART_LIMIT, assemble, descriptors, read_bundle_bytes, sha, write_packet


def source():
    # Split the two UTF-8 bytes of é across the part boundary.
    prefix=b'{"schema":"osw.query-bundle.v1","payload":"'
    return prefix+b'a'*(PART_LIMIT-len(prefix)-1)+'é'.encode()+b'"}\r\n'


def test_byte_exact_roundtrip_and_legacy(tmp_path):
    path=tmp_path/'query-data.json';raw=source();path.write_bytes(raw)
    assert read_bundle_bytes(path)==raw
    packet=write_packet(path,raw)
    assert len(packet['parts'])==2
    assert read_bundle_bytes(path)==raw
    assert packet['logical_sha256']==sha(raw)
    # Repacking the same snapshot reuses the exact files and identity.
    assert write_packet(path,raw)==packet
    assert len(list((tmp_path/'query-parts').iterdir()))==2


@pytest.mark.parametrize('change',['path','order','size','aggregate','missing','changed','schema'])
def test_reject_before_logical_load(tmp_path,change):
    raw=source() if change=='order' else b'{"schema":"osw.query-bundle.v1"}'
    path=tmp_path/'query-data.json';packet=write_packet(path,raw)
    bad=copy.deepcopy(packet)
    if change=='path':bad['parts'][0]['path']='../outside.bin'
    elif change=='order':bad['parts'].reverse()
    elif change=='size':bad['parts'][0]['byte_length']-=1
    elif change=='aggregate':bad['logical_sha256']='0'*64
    elif change=='schema':bad['logical_schema']='other'
    elif change=='missing':(tmp_path/bad['parts'][0]['path']).unlink()
    elif change=='changed':
        target=tmp_path/bad['parts'][0]['path'];raw=bytearray(target.read_bytes());raw[0]^=1;target.write_bytes(raw)
    path.write_text(json.dumps(bad),encoding='utf-8')
    with pytest.raises((ValueError,FileNotFoundError)):
        read_bundle_bytes(path)


def test_packet_descriptors_reject_boolean_size():
    with pytest.raises(ValueError):
        descriptors({'schema':'osw.query-packet.v1','logical_byte_length':True})
