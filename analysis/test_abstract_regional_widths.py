"""Catch source-scope conflation, including coherently changed audit values."""
import copy,json
import pytest
from check_abstract_regional_widths import ROOT,validate_row

@pytest.mark.parametrize('owner',['california','oyashio'])
def test_abstract_width_scope(owner):
    row=next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']==owner)
    validate_row(row)
    for key,value in [('approximate_width_km',650),('calendar_months',[9]),('observed_period',{'start':'1999-09-01','end':'2000-08-31'}),('width_rank_eligible',True),('fixed_layer_bounds_m',[0,200]),('section_geometry',{'type':'LineString'})]:
        bad=copy.deepcopy(row);bad[key]=value
        with pytest.raises(ValueError):validate_row(bad)
    audit=json.loads((ROOT/row['source_scope_context']['audit_file']).read_bytes())
    audit['measurement']['approximate_width_km']=650
    with pytest.raises(ValueError):validate_row(row,audit)
