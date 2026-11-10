"""A failed corridor cannot become a physical route by clearing coarse land."""
import copy,json
from unittest.mock import patch
import pytest
import madagascar_navigation_diagnostic as m

def test_retains_every_failed_and_offshore_case_without_new_current_measurements():
    doc,pins=m.verify_inputs()
    assert len(doc['rejected_v1']['attempts'])==27
    assert all(r['crosses_coarse_land'] for r in doc['rejected_v1']['attempts'])
    assert len(doc['offshore_v2']['scenarios'])==27
    assert doc['offshore_reference_polyline_km']==868.574
    assert doc['difference_from_reported_extent_km']==218.574
    assert doc['published_reported_extent_km']==650
    for key in ['route_admitted','rank_eligible','map_feature_admitted','physical_current_axis_verified','physical_state_passage_verified','annual_extrema_eligible','seasonal_playback_eligible']:
        assert doc[key] is False
    assert m.FILE in pins and m.FIGURE in pins
    assert m.record(doc)['document']==doc

@pytest.mark.parametrize('kind',['omitted_failure','omitted_success','changed_length','promoted_rank','changed_nominal_axis','rebound_owner'])
def test_rejects_erasure_changed_lengths_and_scope_promotion(kind):
    rejection=copy.deepcopy(m.read(m.REJECTION));v2=copy.deepcopy(m.read(m.V2))
    if kind=='omitted_failure':rejection['attempts'].pop()
    if kind=='omitted_success':v2['scenarios'].pop()
    if kind=='changed_length':v2['scenarios'][0]['length_km']+=1
    if kind=='promoted_rank':v2['rank_eligible_published_estimates']=True
    if kind=='changed_nominal_axis':v2['coordinates_lon_lat'][0][0]+=1
    if kind=='rebound_owner':v2['current_id']='north-brazil'
    original=m.read
    with patch.object(m,'read',side_effect=lambda p:rejection if p==m.REJECTION else v2 if p==m.V2 else original(p)):
        with pytest.raises(ValueError):m.build()

def test_new_experiment_is_excluded_from_the_reference_route_catalogue():
    doc=m.read(m.V2)
    assert not (m.ROOT/m.V2).name.endswith('-reference-path-candidate.json')
    catalog=m.read('research/ocean-current-reference-path-candidates.json')
    assert len(catalog['candidates'])==76
    assert all(r['current_id']!='southern-east-madagascar' for r in catalog['candidates'])

def test_tiny_display_readback_drift_preserves_original_receipt_bytes():
    original=m.display_coordinates;expected=m.build()
    with patch.object(m,'display_coordinates',side_effect=lambda pts:[(x+1e-10,y) for x,y in original(pts)]):
        assert m.build()==expected

def test_material_display_geometry_change_is_rejected():
    original=m.display_coordinates
    with patch.object(m,'display_coordinates',side_effect=lambda pts:[(x+1e-4,y) for x,y in original(pts)]):
        with pytest.raises(ValueError,match='Changed rejected'):m.build()
