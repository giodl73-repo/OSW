"""Tiny synthetic ZIP/resource checks; no originals, NetCDF imports or network."""
import io
import hashlib
import types
import zipfile
import pytest
import inspect_osnap_wg_2016_2018_source_v1 as source


def fixture(names):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.writestr(name, b'CDF\x01synthetic-header-only')
    data.seek(0)
    archive = zipfile.ZipFile(data)
    expected = [{'name': info.filename, 'compressed_bytes': info.compress_size,
                 'uncompressed_bytes': info.file_size, 'compression': info.compress_type,
                 'crc32': f'{info.CRC:08x}'} for info in archive.infolist()]
    return archive, expected


def test_local_refusal_precedes_source_access_and_network(monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    def forbidden(*args, **kwargs): pytest.fail('Local guard accessed original/preflight/network')
    monkeypatch.setattr(source, 'verify_preflight', forbidden)
    monkeypatch.setattr(source.urllib.request, 'urlopen', forbidden)
    with pytest.raises(RuntimeError, match='cloud-only'): source.main()


def test_implicit_cloud_execution_rejects():
    with pytest.raises(RuntimeError): source.require_cloud(False, {'GITHUB_ACTIONS': 'true'})


def test_extensionless_instrument_is_retained():
    archive, expected = fixture(['LS7/temperature-without-extension', 'LS1/velocity.nc'])
    with archive:
        assert [r.filename for r in source.checked_members(archive, expected)] == sorted(r['name'] for r in expected)


@pytest.mark.parametrize('change', ['missing', 'extra', 'crc', 'size', 'duplicate_expected'])
def test_changed_instrument_inventory_rejects(change):
    archive, expected = fixture(['LS7/temperature', 'LS1/velocity.nc'])
    if change == 'missing': expected.pop()
    if change == 'extra': expected.append({**expected[0], 'name': 'LS8/missing.nc'})
    if change == 'crc': expected[0]['crc32'] = '00000000'
    if change == 'size': expected[0]['uncompressed_bytes'] += 1
    if change == 'duplicate_expected': expected.append(dict(expected[0]))
    with archive, pytest.raises(ValueError): source.checked_members(archive, expected)


def test_unsafe_unselected_member_rejects():
    archive, expected = fixture(['LS1/velocity.nc', '../not-an-instrument'])
    with archive, pytest.raises(ValueError, match='Unsafe'):
        source.checked_members(archive, expected[:1])


def test_source_receipt_cannot_be_overwritten(tmp_path):
    path = tmp_path / 'receipt.json'
    source.write_once(path, b'original')
    source.write_once(path, b'original')
    with pytest.raises(ValueError): source.write_once(path, b'changed')
    assert path.read_bytes() == b'original'


def test_directory_fingerprint_matches_standard_zip_writer(tmp_path):
    archive, _ = fixture(['LS1/velocity.nc'])
    with archive:
        raw = archive.fp.getvalue()
        start = raw.index(b'PK\x01\x02')
        end = raw.rfind(b'PK\x05\x06')
        path = tmp_path / 'tiny.zip'; path.write_bytes(raw)
        assert source.archive_directory_hash(path) == (hashlib.sha256(raw[start:end]).hexdigest(), 1)


def test_unreviewed_trailing_archive_bytes_reject(tmp_path):
    archive, _ = fixture(['LS1/velocity.nc'])
    with archive:
        path = tmp_path / 'tiny.zip';path.write_bytes(archive.fp.getvalue() + b'changed')
        with pytest.raises(ValueError, match='layout'):source.archive_directory_hash(path)


def test_duplicate_actual_archive_member_rejects():
    with pytest.warns(UserWarning, match='Duplicate name'):
        archive, expected = fixture(['LS1/velocity.nc', 'LS1/velocity.nc'])
    with archive, pytest.raises(ValueError, match='Duplicate archive'):
        source.checked_members(archive, expected[:1])


def test_nested_header_groups_cannot_be_silently_omitted(monkeypatch):
    class Header:
        groups = {'unreviewed-group': object()}
        def __enter__(self): return self
        def __exit__(self, *args): pass
    monkeypatch.setitem(__import__('sys').modules, 'netCDF4', types.SimpleNamespace(Dataset=lambda *a, **k: Header()))
    with pytest.raises(ValueError, match='Nested NetCDF groups'):
        source.header_metadata(b'CDF\x01synthetic-header-only')
