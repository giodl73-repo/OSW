"""Barriers, native adjacency and paired monthly support for flow context."""
import numpy as np
import json
import xml.etree.ElementTree as ET
import pytest

import build_south_australian_flow_context as context


def test_diagonal_cells_and_missing_barriers_do_not_join():
    values=np.array([[2.,0.,2.],[0.,2.,0.],[2.,0.,2.]])
    result=context.connected_component(values,np.ones((3,3),dtype=bool),(1,1),1.)
    assert result['cells']==[[1,1]]
    assert result['touched_box_sides']==[]
    assert result['neighbor_barrier_edges']=={'unsupported':0,'sub_threshold':4,'domain':0}
    values[:]=2.;supported=np.ones((3,3),dtype=bool);supported[1,:]=False
    result=context.connected_component(values,supported,(0,1),1.)
    assert result['cells']==[[0,0],[0,1],[0,2]]
    assert result['touched_box_sides']==['east','south','west']
    assert result['neighbor_barrier_edges']=={'unsupported':3,'sub_threshold':0,'domain':5}


def test_threshold_ties_are_included_and_unusable_seed_is_retained():
    values=np.array([[1.,1.,.999]])
    support=np.ones(values.shape,dtype=bool)
    result=context.connected_component(values,support,(0,0),1.)
    assert result['cells']==[[0,0],[0,1]]
    result=context.connected_component(values,support,(0,2),1.)
    assert result['status']=='seed_not_supported_above_threshold'
    assert result['cells']==[]
    values[0,0]=np.nan
    assert context.connected_component(values,support,(0,0),.5)['cells']==[]


def test_monthly_mean_uses_same_complete_pairs_and_support_threshold():
    u=np.full((5,1,3),100,dtype='<i2');v=np.full_like(u,200)
    u[0,0,0]=1000;v[0,0,0]=-30000
    u[:2,0,1]=-30000
    u[:,0,2]=-30000
    mean_u,mean_v,counts,supported=context.monthly_vectors({'water_u':u,'water_v':v},list(range(5)),4)
    assert counts.tolist()==[[4,3,0]]
    assert supported.tolist()==[[True,False,False]]
    assert mean_u[0,0]==.1 and mean_v[0,0]==.2
    assert np.isnan(mean_u[0,1:]).all() and np.isnan(mean_v[0,1:]).all()


def test_declared_inputs_remain_pinned():
    assert context.sha(context.ROOT/context.PROTOCOL)==context.PROTOCOL_SHA
    assert context.sha(context.ROOT/context.ORIGINAL)==context.ORIGINAL_SHA


def test_retained_source_and_all_context_cases_reproduce():
    saved=json.loads((context.ROOT/context.OUTPUT).read_bytes())
    assert context.build()==saved
    assert [m['month'] for m in saved['months']]==list(range(1,13))
    assert sum(len(m['threshold_cases']) for m in saved['months'])==36
    assert not saved['current_association_verified'] and not saved['width_measurement_admitted']
    assert not saved['annual_range_admitted'] and not saved['cells_are_current_footprint']


def test_resealed_acquisition_receipt_is_rejected(monkeypatch):
    original_sha=context.sha
    monkeypatch.setattr(context,'sha',lambda path:'0'*64 if path==context.DIRECTORY/'acquisition.json' else original_sha(path))
    with pytest.raises(ValueError,match='frozen surrounding-source'):context.build()


@pytest.mark.parametrize('receipt_name',['south-australian-hycom-2d-source-figure.json','south-australian-hycom-2d-flow-context-figure.json'])
def test_published_figures_are_pinned_and_described(receipt_name):
    receipt=json.loads((context.ROOT/'research'/receipt_name).read_bytes())
    assert context.sha(context.ROOT/receipt['generator_file'])==receipt['generator_sha256']
    assert not receipt['current_association_verified'] and not receipt['width_measurement_admitted']
    for path,digest in receipt['figures'].items():
        assert context.sha(context.ROOT/path)==digest
        if path.endswith('.svg'):
            svg=ET.parse(context.ROOT/path).getroot()
            assert svg.get('role')=='img'
            for element_id in svg.get('aria-labelledby').split():
                element=next(n for n in svg if n.get('id')==element_id)
                assert element.text
