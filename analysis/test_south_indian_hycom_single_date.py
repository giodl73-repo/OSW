"""Request subdivision preserves the full native cohort and numeric arithmetic."""
import copy
import json
from pathlib import Path
from urllib.parse import unquote
import numpy as np
import pytest
from south_indian_hycom_single_date_resume import subdivisions,effective_requests
from acquire_south_indian_hycom_hydrography import FIELDS,common_means


def plan():
    path=Path(__file__).resolve().parents[1]/'research/south-indian-hycom-hydrography-source-preflight.json'
    return json.loads(path.read_bytes())['selection']


def declaration():
    p=plan();r=next(r for r in p['requests'] if r['file']=='m04-r02.ascii')
    return p,{'logical_request_file':r['file'],'original_request':r,'subrequests':subdivisions(r)}


def test_all_363_timestamps_preserved_in_order_with_no_duplicate_or_omission():
    p,d=declaration();actual=effective_requests(p,d)
    assert len(p['requests'])==82 and len(actual)==87
    before=[i for r in p['requests'] for i in r['time_indices']]
    after=[i for r in actual for i in r['time_indices']]
    assert before==after and len(after)==len(set(after))==363
    for old in p['requests']:
        if old['file']!=d['logical_request_file']:assert old in actual


def test_each_subrequest_retains_every_variable_and_spatial_slice():
    _,d=declaration();r=d['original_request']
    for i,child in enumerate(d['subrequests']):
        index=r['time_indices'][i];body=unquote(child['url'].split('?',1)[1])
        assert child['time_indices']==[index] and child['month']==4
        assert body==','.join(f'{n}[{index}:1:{index}][7:25:32][800:1:1125][3249:1:3251]' for n in FIELDS)


@pytest.mark.parametrize('kind',['omit','duplicate','reorder','time','depth','variable','parent'])
def test_altered_subdivision_is_rejected(kind):
    p,d=declaration();d=copy.deepcopy(d)
    if kind=='omit':d['subrequests'].pop()
    elif kind=='duplicate':d['subrequests'].append(d['subrequests'][0])
    elif kind=='reorder':d['subrequests'].reverse()
    elif kind=='time':d['subrequests'][0]['time_indices']=[0]
    elif kind=='depth':d['subrequests'][0]['url']=d['subrequests'][0]['url'].replace('7%3A25%3A32','7%3A1%3A7')
    elif kind=='variable':d['subrequests'][0]['url']=d['subrequests'][0]['url'].replace('salinity','water_u')
    else:d['original_request']['month']=5
    with pytest.raises(ValueError):effective_requests(p,d)


def test_integer_packed_partition_preserves_all_mean_and_count_bits():
    rng=np.random.default_rng(29)
    fields={n:rng.integers(-2000,2000,size=(6,2,3,3),dtype=np.int16) for n in FIELDS}
    fields['salinity'][1,0,1,1]=-30000
    scale=float(np.float32(.001));offsets={n:float(v[2]) for n,v in FIELDS.items()}
    expected_counts,expected=common_means(fields,5,scale,offsets)
    split={n:np.concatenate([a[i:i+1] for i in range(6)]) for n,a in fields.items()}
    counts,actual=common_means(split,5,scale,offsets)
    assert counts.tobytes()==expected_counts.tobytes()
    for n in FIELDS:assert actual[n].tobytes()==expected[n].tobytes()
