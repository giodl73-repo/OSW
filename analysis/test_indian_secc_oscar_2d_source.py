"""Native source integrity and independent paired-only monthly arithmetic."""
import io,json,zipfile
import numpy as np
import pytest
import acquire_indian_secc_oscar_2d as a
import build_indian_secc_oscar_2d_source as b

@pytest.fixture(scope='module')
def original():
    with zipfile.ZipFile(a.DIRECTORY/'source-responses.zip') as z:
        return z.read('metadata.json'),z.read('vectors.csv'),a.baseline()

def test_cube_and_monthly_fields_preserve_originals(original):
    arrays,quality=a.parse(*original)
    assert quality['vector_positions']==322344 and quality['finite_pairs']==322344
    assert quality['historical_overlap_vectors']==4464
    stored,pins=b.verify()
    assert stored['historical_monthly_overlap_cells']==744
    assert stored['historical_monthly_bits_masks_and_counts_exact'] is True
    assert len(stored['monthly_summary'])==12 and len(stored['months'])==12
    assert [f['available_source_times'] for f in stored['months']]==[7,5]+[6]*10
    assert stored['current_association_verified'] is False
    for key in ['whole_current_length_km','whole_current_width_km','annual_physical_length_range_km','annual_physical_width_range_km']:
        assert stored[key] is None
    for f in stored['months']:
        ix=f['source_time_indices'];paired=np.isfinite(arrays['u'][ix])&np.isfinite(arrays['v'][ix]);counts=paired.sum(axis=0)
        np.testing.assert_array_equal(f['paired_samples'],counts)
        for key,field in [('eastward_m_s','u'),('northward_m_s','v')]:
            actual=np.array(f[key],dtype=float);selected=np.where(paired,arrays[field][ix],np.nan)
            total=np.nansum(selected,axis=0);expected=np.full_like(total,np.nan);np.divide(total,counts,out=expected,where=counts>=5)
            np.testing.assert_array_equal(np.isnan(actual),np.isnan(expected))
            bound=np.finfo(float).eps*(len(ix)+2)*np.nansum(np.abs(selected),axis=0)/np.maximum(counts,1)
            finite=np.isfinite(expected)
            assert np.all(np.abs(actual[finite]-expected[finite])<=bound[finite])

@pytest.mark.parametrize('mutation',['header','units','clock','infinite','duplicate','missing_last','changed_old_value','changed_old_mask'])
def test_changed_source_is_rejected(original,mutation):
    metadata,raw,previous=original;lines=raw.decode().splitlines()
    if mutation=='header':lines[0]=lines[0].replace('longitude','x')
    elif mutation=='units':lines[1]=lines[1].replace('m s-1','cm s-1')
    elif mutation=='missing_last':lines.pop()
    elif mutation=='duplicate':lines[3]=lines[2]
    else:
        i=2+6*121+91 if mutation.startswith('changed_old') else 2
        row=lines[i].split(',')
        if mutation=='clock':row[0]='2013-01-02T00:00:00Z'
        elif mutation=='infinite':row[4]='Infinity'
        elif mutation=='changed_old_mask':row[4]='NaN'
        else:row[4]=str(float(row[4])+.001)
        lines[i]=','.join(row)
    with pytest.raises(ValueError):a.parse(metadata,('\n'.join(lines)+'\n').encode(),previous)

def test_one_missing_component_is_not_filled_and_means_require_pairs(original):
    metadata,raw,previous=original;lines=raw.decode().splitlines();first=lines[2].split(',');first[4]='NaN';lines[2]=','.join(first)
    arrays,quality=a.parse(metadata,('\n'.join(lines)+'\n').encode(),previous)
    assert quality['one_component_missing']==1 and np.isnan(arrays['u'][0,0,0]) and np.isfinite(arrays['v'][0,0,0])
    tiny={'times':['2013-01-'+str(i+1).zfill(2) for i in range(5)],'u':np.ones((5,1,1)),'v':np.ones((5,1,1))}
    tiny['u'][0,0,0]=np.nan;f=b.monthly(tiny)
    assert f[0]['paired_samples']==[[4]] and f[0]['eastward_m_s']==[[None]] and f[0]['northward_m_s']==[[None]]
    assert all(m['eligible_mean_cells']==0 for m in f)
