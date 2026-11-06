"""Native query rows preserve field values, masks and temporal support."""
import struct
import numpy as np
import pytest
from south_indian_front_level_query import samples, FIELDS, BASE


def fixture():
    lat=np.linspace(-48,-30,326).tolist()
    source={'schema':'osw.south-indian-hycom-front-level-monthly.v1',
            'dataset_url':BASE,'source_model_year':2013,'units':{n:v[1] for n,v in FIELDS.items()},
            'depth_m':[100.,200.],'latitude_degrees_north':lat,'longitude_degrees_east':[79.9200439453125,80.,80.0799560546875],
            'current_association_verified':False,'physical_width_admitted':False,
            'physical_axis_admitted':False,'seasonal_footprint_admitted':False,'months':[]}
    plan={'selection':{'depth':[19,22],'lat':list(range(800,1126)),'lon':[3249,3250,3251]},'requests':[]}
    import calendar,math
    for m in range(1,13):
        days=calendar.monthrange(2013,m)[1]-(m in [8,12])
        counts=np.full((2,326,3),days).tolist()
        fields={n:np.full((2,326,3),i+.1234567890123456).tolist() for i,n in enumerate(FIELDS)}
        counts[1][100][2]=0
        for a in fields.values():a[1][100][2]=None
        fields['water_u'][0][0][0]=-0.
        source['months'].append({'month':m,'sample_days':days,'minimum_common_samples':math.ceil(.8*calendar.monthrange(2013,m)[1]),'common_samples':counts,'fields':fields})
        plan['requests'].append({'month':m,'time_indices':list(range(days))})
    return source,plan


def test_all_cells_fields_and_missing_rows_retained_without_rounding():
    source,plan=fixture();rows=samples(source,plan)
    assert len(rows)==23472 and len({r['id'] for r in rows})==23472
    assert len({r['profile_id'] for r in rows})==72
    assert sum(not r['eligible'] for r in rows)==12
    first=rows[0]
    assert struct.pack('d',first['eastward_velocity_m_s'])==struct.pack('d',-0.)
    assert first['source_depth_index']==19 and first['source_latitude_index']==800 and first['source_longitude_index']==3249
    august=next(r for r in rows if r['month']==8 and r['profile_id']=='front-levels:m08-z1-x2' and r['source_latitude_index']==900)
    assert not august['eligible'] and august['salinity_psu'] is None and august['common_daily_samples']==0
    assert all(not r['current_association_verified'] and not r['physical_width_admitted'] for r in rows)
    assert rows[1]['in_situ_temperature_c']==source['months'][0]['fields']['water_temp'][0][0][1]


def test_every_native_axis_and_float_bit_is_preserved():
    source,plan=fixture()
    z,y,x=np.indices((2,326,3))
    for month in source['months']:
        for n,field in enumerate(FIELDS):
            values=(month['month']+z*.1+y*.0001+x*.000001+n*10).astype(object)
            values[1,100,2]=None
            month['fields'][field]=values.tolist()
    source['months'][0]['fields']['water_u'][0][0][0]=-0.
    expected_columns={'water_u':'eastward_velocity_m_s','water_v':'northward_velocity_m_s',
                      'water_temp':'in_situ_temperature_c','salinity':'salinity_psu'}
    for row in samples(source,plan):
        mi=row['month']-1;zi=plan['selection']['depth'].index(row['source_depth_index'])
        yi=plan['selection']['lat'].index(row['source_latitude_index'])
        xi=plan['selection']['lon'].index(row['source_longitude_index'])
        assert row['latitude_degrees_north']==source['latitude_degrees_north'][yi]
        assert row['longitude_degrees_east']==source['longitude_degrees_east'][xi]
        assert row['depth_m']==source['depth_m'][zi]
        for field,column in expected_columns.items():
            expected=source['months'][mi]['fields'][field][zi][yi][xi]
            if expected is None:assert row[column] is None
            else:assert struct.pack('d',row[column])==struct.pack('d',expected)


@pytest.mark.parametrize('change', ['units','month','count','null','nonfinite','association','days','threshold','coordinates','shape'])
def test_corruption_is_rejected_instead_of_silently_dropping_rows(change):
    source,plan=fixture()
    if change=='units':source['units']['water_temp']='potential_temperature'
    elif change=='month':source['months'][1]['month']=1
    elif change=='count':source['months'][0]['common_samples'][0][0][0]=True
    elif change=='null':source['months'][0]['fields']['water_u'][0][0][0]=None
    elif change=='nonfinite':source['months'][0]['fields']['salinity'][0][0][0]=float('inf')
    elif change=='association':source['current_association_verified']=True
    elif change=='days':source['months'][7]['sample_days']=31
    elif change=='threshold':source['months'][0]['minimum_common_samples']=24
    elif change=='coordinates':source['latitude_degrees_north'].reverse()
    else:source['months'][0]['fields']['water_v'][0].pop()
    with pytest.raises(ValueError):samples(source,plan)


def test_supplementary_rows_cannot_replace_existing_native_level_ids():
    from test_south_indian_hydrography_query import fixture as earlier_fixture
    from south_indian_hydrography_query import samples as earlier_samples
    source, plan = fixture()
    earlier, earlier_plan = earlier_fixture()
    rows, old = samples(source, plan), earlier_samples(earlier, earlier_plan)
    assert not {r['id'] for r in rows} & {r['id'] for r in old}
    assert not {r['profile_id'] for r in rows} & {r['profile_id'] for r in old}
    assert len(rows+old) == 46944
    assert len({r['id'] for r in rows+old}) == 46944
    assert {r['depth_m'] for r in rows+old} == {15, 100, 200, 1000}


@pytest.mark.parametrize('axis', ['depth', 'lat', 'lon'])
def test_wrong_native_indices_rejected(axis):
    source, plan = fixture()
    plan['selection'][axis][0] += 1
    with pytest.raises(ValueError, match='indices'): samples(source, plan)
