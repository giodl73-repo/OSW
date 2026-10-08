"""Distinct diagnostic scales cannot become physical disks or annual ranges."""
import copy,hashlib,json,subprocess
import pytest
from check_astrid_radial_scales import ROOT,PATH,validate
from test_rust_query_browser import CLI
def test_original_radius_definitions_and_scope():
    doc=json.loads((ROOT/PATH).read_bytes());geo=json.loads((ROOT/'research/named-eddy-geography.json').read_bytes());validate(doc,geo)
    for key,value in [('value_km',240),('metric','outer_footprint_radius'),('footprint_inference_eligible',True),('area_inference_eligible',True),('geometry',{'type':'Polygon'}),('reported_uncertainty_km',20),('calendar_months',[3])]:
        bad=copy.deepcopy(doc);bad['measurements'][0][key]=value
        with pytest.raises(ValueError):validate(bad,geo)

def test_compiled_loader_rejects_coherent_scope_rewrites(tmp_path):
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    cli=CLI
    for key,value in [('metric','outer_footprint_radius'),('footprint_inference_eligible',True),('value_km',240)]:
        bad=copy.deepcopy(bundle);receipt=bad['manifest']['atlas_receipts'][PATH];doc=json.loads(receipt['source_json'])
        doc['measurements'][0][key]=value;receipt['source_json']=json.dumps(doc)
        receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][PATH]=receipt['source_sha256']
        path=tmp_path/'changed.json';path.write_text(json.dumps(bad),encoding='utf8')
        run=subprocess.run([str(cli),str(path),'--atlas'],capture_output=True,text=True,encoding='utf8')
        assert run.returncode==2 and 'Astrid diagnostic radius' in run.stderr,run.stderr
