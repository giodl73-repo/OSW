import copy,json,pytest
from check_atlantic_euc_section_properties import ROOT,PATH,validate
def test_original_extraction():
    validate(json.loads((ROOT/PATH).read_bytes()))
@pytest.mark.parametrize('field,value',[('whole_current_width_km',200),('station_latitude_deg',0),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('width_inference_eligible',True),('occupied_geometry_eligible',True),('velocity_reference_depth_m',200),('section_longitude_deg_e',4),('date_conflict_count',0)])
def test_false_support_rejected(field,value):
    audit=copy.deepcopy(json.loads((ROOT/PATH).read_bytes()));audit['section_properties'][field]=value
    with pytest.raises(ValueError):validate(audit)
@pytest.mark.parametrize('field,value',[('maximum_eastward_speed_cm_s',200),('maximum_speed_depth_m',200),('date_conflict',False),('resolved_observation_date','1979-06-01'),('table_i_campaign_period','June 1979')])
def test_table_and_date_mutations_rejected(field,value):
    audit=copy.deepcopy(json.loads((ROOT/PATH).read_bytes()));audit['section_properties']['records'][5][field]=value
    with pytest.raises(ValueError):validate(audit)
