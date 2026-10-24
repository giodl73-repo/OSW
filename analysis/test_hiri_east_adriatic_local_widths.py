"""Protect naming, metric and date support even after import receipts are repinned."""
from query_packet import read_bundle_bytes
import copy
import hashlib
import json
import subprocess

import pytest
from check_hiri_east_adriatic_local_widths import ROOT, AUDITS, validate_row
from test_rust_query_browser import CLI

def records():
    return [r for r in json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())['measurements']
            if r['current_id'] in AUDITS]

def test_distinct_author_descriptors_and_ownership():
    rows = records()
    assert len(rows) == 3
    for row in rows:
        validate_row(row)
        assert row['section_geometry'] is None and row['width_range_km'] is None
    hiri = [r for r in rows if r['current_id']=='hiri-current']
    assert [(r['observed_month'], r['approximate_width_km']) for r in hiri] == [('1987-07',50),('1990-07',75)]
    assert all(r['width_metric']=='author_reported_e_folding_scale' for r in hiri)
    eac = next(r for r in rows if r['current_id']=='east-adriatic')
    assert eac['approximate_width_km']==10
    c = eac['original_regional_context']
    assert c['instrument_sample_depth_bounds_m']==[10,70] and c['figure_vector_depth_m']==10
    assert c['comparison_cruise_numeric_current_width_km'] is None

CHANGES = [('width_range_km',[50,75]), ('calendar_months',[7]), ('fixed_layer_bounds_m',[0,1500]),
           ('uncertainty_km',5), ('annual_extrema_eligible',True), ('original_regional_context',{}),
           ('current_id','new-guinea-coastal-undercurrent'), ('width_metric','author_reported_current_width')]

@pytest.mark.parametrize('index',range(3))
@pytest.mark.parametrize('key,value',CHANGES)
def test_local_support_promotions_rejected(index,key,value):
    row=copy.deepcopy(records()[index]);row[key]=value
    with pytest.raises(ValueError):
        validate_row(row)

def coherent_packet(packet, ident, key, value):
    bad=copy.deepcopy(packet)
    receipt=bad['manifest']['seasons_receipts']['widths']
    document=json.loads(receipt['source_json'])
    for rows in [document['measurements'],bad['collections']['widths']]:
        next(r for r in rows if r['id']==ident)[key]=value
    receipt['source_json']=json.dumps(document)
    receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
    bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
    return bad

def test_compiled_native_rejects_coherent_scope_changes(tmp_path):
    packet=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    path=tmp_path/'local-widths.json'
    for row in records():
        for key,value in [('approximate_width_km',row['approximate_width_km']*2),
                          ('width_range_km',[50,75]),('current_id','new-guinea-coastal-undercurrent'),
                          ('original_regional_context',{})]:
            path.write_text(json.dumps(coherent_packet(packet,row['id'],key,value)),encoding='utf8')
            result=subprocess.run([str(CLI),str(path),'--seasons'],capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and 'Original regional width' in result.stderr,result.stderr
