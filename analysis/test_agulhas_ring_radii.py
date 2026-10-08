"""Conflicted source radii and years cannot become dimensions or footprints."""
import copy,hashlib,json,subprocess
import pytest
from build_agulhas_ring_radius_audit import ROOT,PATH,build,validate
from test_rust_query_browser import CLI

def test_source_slots_keep_conflicts_and_unknown_geometry():
    doc=json.loads((ROOT/PATH).read_bytes());geo=json.loads((ROOT/'research/named-eddy-geography.json').read_bytes());validate(doc,geo)
    rows=doc['entities']['eliza-2007']['measurements']
    assert [r['value_km'] for r in rows]==[None,95,None]
    assert rows[2]['period_month'] is None and rows[2]['date_conflict'] is True
    assert [c['value_km'] for c in rows[0]['source_claims']]==[88,93]
    assert [c['reported_period'] for c in rows[2]['source_claims']]==['Jan/10','January 2019']
    assert doc['entities']['jeannette-2012']['measurements'][0]['value_km']==74
    for key,value in [('value_km',90.5),('radius_range_km',[88,93]),('geometry',{'type':'Polygon'}),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('footprint_inference_eligible',True),('rank_eligible',True),('observation_date','2009-02-14'),('reported_uncertainty_km',13),('conflict_resolution','table preferred')]:
        bad=copy.deepcopy(doc);bad['entities']['eliza-2007']['measurements'][0][key]=value
        with pytest.raises(ValueError):validate(bad,geo)
    bad=copy.deepcopy(doc);bad['entities']['eliza-2007']['measurements'][2]['period_month']='2010-01'
    with pytest.raises(ValueError):validate(bad,geo)
    bad=copy.deepcopy(geo);next(r for r in bad['entries'] if r['id']=='ana-2004')['published_ring_radius_evidence'][0]['value_km']=134
    with pytest.raises(ValueError):validate(doc,bad)

def check_compiled_scope(tmp_path):
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    for key,value in [('value_km',88),('radius_range_km',[88,93]),('footprint_inference_eligible',True),('period_month','2019-01')]:
        bad=copy.deepcopy(packet);receipt=bad['manifest']['atlas_receipts'][PATH];doc=json.loads(receipt['source_json'])
        doc['entities']['eliza-2007']['measurements'][0][key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][PATH]=receipt['source_sha256']
        p=tmp_path/'ring-radii-rewritten.json';p.write_text(json.dumps(bad),encoding='utf8')
        run=subprocess.run([str(CLI),str(p),'--atlas'],capture_output=True,text=True,encoding='utf8')
        assert run.returncode==2 and 'Agulhas radius source' in run.stderr,run.stderr
