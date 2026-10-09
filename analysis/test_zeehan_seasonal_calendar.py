import copy,json,pytest
from check_zeehan_seasonal_calendar import ROOT,PATH,validate

def audit():return json.loads((ROOT/PATH).read_bytes())
def test_reviewed_calendar():
    doc=validate(audit());calendar=doc['seasonal_calendar']
    assert len(calendar['claims'])==6 and len(calendar['months'])==12
    assert calendar['months'][9]['claim_ids']==['summer-indication','summer-anomaly']
    assert calendar['months'][3]['claim_ids']==['april-transition','summer-anomaly']
@pytest.mark.parametrize('key,value',[('observation_dates',['2007-06-01']),('speed_values',[1]*12),('width_values',[20]*12),('occupied_geometry',[]),('annual_dimension_extrema_eligible',True),('seasonal_geometry_playback_eligible',True)])
def test_false_measurement_support(key,value):
    doc=copy.deepcopy(audit());doc['seasonal_calendar'][key]=value
    with pytest.raises(ValueError):validate(doc)
def test_qualified_endpoint_and_anomaly_reference_preserved():
    for index,key,value in [(4,'endpoint_qualifier','exact'),(5,'reference_state','absolute flow'),(4,'months',[5,6,7,8]),(0,'kind','observed_axis')]:
        doc=audit();doc['seasonal_calendar']['claims'][index][key]=value
        with pytest.raises(ValueError):validate(doc)
def test_dashboard_updates_without_new_observation_samples():
    from build_motion_dashboard import build
    row=next(r for r in build()['entries'] if r['id']=='current:zeehan')
    assert row['capabilities']['scope_notes']==1
    assert row['capabilities']['time_samples']==0
    assert row['latest_observation_date'] is None
    assert any('seasonal calendar' in link['label'] for link in row['evidence_links'])
