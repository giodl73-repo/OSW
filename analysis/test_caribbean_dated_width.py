"""Historical author bounds cannot become annual width or a depth envelope."""
import copy
import hashlib
import json
import subprocess
import pytest
from check_caribbean_dated_width import ROOT, AUDIT, validate_row
from test_rust_query_browser import CLI

def record():
    return next(r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements'] if r['current_id']=='caribbean')

def test_original_dated_value_and_units():
    row=record();validate_row(row)
    assert row['approximate_width_km']==410 and row['observed_month']=='1974-10'
    c=row['original_regional_context']
    assert c['range_context']['normalized_range_km'] is None
    assert c['range_context']['raw_units']==['nautical_miles','miles_unqualified']
    assert c['speed_context']['associated_october_1974_m_s']==c['speed_context']['associated_october_1974_cm_s']/100

CHANGES=[('width_range_km',[200,410]),('calendar_months',[10]),('fixed_layer_bounds_m',[0,1600]),
         ('observed_month','2015-10'),('uncertainty_km',111.12),('annual_extrema_eligible',True),
         ('current_id','antilles'),('original_regional_context',{})]

@pytest.mark.parametrize('key,value',CHANGES)
def test_source_scope_promotions_rejected(key,value):
    bad=copy.deepcopy(record());bad[key]=value
    with pytest.raises(ValueError):validate_row(bad)

def coherent_packet(packet,key,value):
    bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
    for rows in [doc['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['current_id']=='caribbean')[key]=value
    receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def test_native_scope_guard_rejects_coherent_rewrites(tmp_path):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    path=tmp_path/'caribbean.json'
    for key,value in CHANGES:
        path.write_text(json.dumps(coherent_packet(packet,key,value)),encoding='utf8')
        result=subprocess.run([str(CLI),str(path),'--seasons'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr

