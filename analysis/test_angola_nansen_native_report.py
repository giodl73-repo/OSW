"""Complete original-provider equality, independent of the serialization kernel."""
import gzip
import hashlib
import json
import zipfile
import numpy as np
from netCDF4 import Dataset
from angola_nansen_native_sections import ROOT, ARCHIVE, REPORT


def test_every_native_coordinate_velocity_and_missing_cell_is_preserved():
    report=json.loads((ROOT/REPORT).read_bytes())
    assert report['section_count']==11 and report['profile_count']==6148
    assert report['velocity_cells_per_component']==1022160
    assert not report['physical_width_admitted'] and not report['canonical_current_identity_admitted']
    count=0
    with zipfile.ZipFile(ROOT/ARCHIVE) as archive:
        assert [i.filename for i in archive.infolist()]==[r['path'] for r in report['members']]
        for section in report['sections']:
            packed=(ROOT/section['field_file']).read_bytes();raw=gzip.decompress(packed)
            assert hashlib.sha256(packed).hexdigest()==section['field_sha256']
            assert hashlib.sha256(raw).hexdigest()==section['decoded_sha256']
            field=json.loads(raw)
            with Dataset('original',memory=archive.read(section['source_member'])) as provider:
                for name,variable in provider.variables.items():
                    variable.set_auto_maskandscale(False);expected=np.asarray(variable[:]);actual=np.asarray(field['variables'][name]['values'],dtype=float)
                    assert expected.shape==actual.shape and np.array_equal(expected,actual,equal_nan=True),(section['id'],name)
                    assert np.array_equal(np.signbit(expected[expected==0]),np.signbit(actual[expected==0]))
                    if name in ['U_CUR','V_CUR']:count+=actual.size
    assert count==2044320
