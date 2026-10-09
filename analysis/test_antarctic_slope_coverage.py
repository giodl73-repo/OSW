"""Coverage lights and source-review semantics must follow the actual evidence."""
import copy
import json
import pytest
from build_motion_dashboard import build
from check_antarctic_slope_scope import ROOT,AUDIT,validate


def test_observed_coverage_updates_without_width_admission():
    row=next(r for r in build()['entries'] if r['id']=='current:antarctic-slope')
    assert row['capabilities']['observed_velocity']==61
    assert row['capabilities']['time_samples']==61
    assert row['capabilities']['scoped_width']==0
    assert row['latest_observation_date']=='2021-02-13'
    assert row['series'][0]['paired_source_readings']==16393
    assert row['series'][0]['nominal_depth_m']==228
    assert row['scope_notes'][0]['audit_file']==AUDIT


@pytest.mark.parametrize('change',[{'whole_current_width_km':5},{'annual_width_range_km':[5,80]},{'map_buffer_eligible':True}])
def test_spacing_cannot_be_promoted_to_current_width(change):
    audit=json.loads((ROOT/AUDIT).read_bytes());audit.update(change)
    with pytest.raises(ValueError):validate(audit,json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes()))


def test_width_review_keeps_numeric_unknowns():
    audit=json.loads((ROOT/AUDIT).read_bytes())
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    validate(audit,inventory)
    decision=next(r for r in inventory['current_decisions'] if r['current_id']=='antarctic-slope')
    assert decision['width_decision']=='sources_reviewed_no_comparable_numeric_current_width'
    assert decision['measurement_ids']==[] and decision['whole_current_width_km'] is None
    changed=copy.deepcopy(audit);changed['width_review']['whole_current_width_km']=10
    next(r for r in inventory['review_assessments'] if r['current_id']=='antarctic-slope')['whole_current_width_km']=10
    with pytest.raises(ValueError):validate(changed,inventory)
