"""Historical regional width and two qualitative occupations retain separate supports."""
import copy,gzip,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from check_zeehan_historical_width import AUDIT

def main():
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'zeehan'}],'limit':50}
    expected=native(query);row=expected['rows'][0]
    assert expected['total']==1 and row['approximate_width_km']==40 and row['width_range_km'] is None
    records=row['original_regional_context']['section_comparison']['records']
    request={'document':AUDIT,'pointer':'/measurement/original_regional_context/section_comparison/records','limit':50}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        index=Path(directory)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        source_expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
        assert [r['record'] for r in source_expected['rows']]==records
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Azeehan#route-atlas')
            panel=page.locator('#route-atlas-preview .qualitative-section-comparison');panel.wait_for(state='visible',timeout=90000)
            assert panel.locator('strong').all_text_contents()==['1997-03','1997-12']
            assert panel.inner_text().count('Numerical width: unknown')==2
            assert 'historical 40 km value is not assigned' in panel.inner_text()
            assert '40 km' in page.locator('#width-zeehan-cresswell-2000-historical-slope-width').inner_text()
            assert panel.locator('svg,circle,path').count()==0
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            panel.screenshot(path=str(ROOT/'.pytest_cache/zeehan-section-comparison-mobile.png'))
            panel.get_by_role('link',name='Query both occupation contexts').click()
            page.wait_for_function('window.oswSourceQueryResult?.total===2',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==source_expected
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=zeehan&phase=zeehan-cresswell-2000-historical-slope-width')
            page.wait_for_function('window.oswSeasonPlan?.current_id==="zeehan"',timeout=90000)
            assert page.locator('#season-play').is_disabled() and page.evaluate('oswSeasonPlan.eligible_indices')==[]
            assert page.locator('#regional-width-range .qualitative-section-comparison').count()==1
            assert 'not a 1997 Strahan section width' in page.locator('#regional-width-range').inner_text()
            assert page.locator('#season-section-locator').is_hidden()
            assert not errors,errors
            browser.close()
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for key,value in [('approximate_width_km',80),('calendar_months',[3,12]),('fixed_layer_bounds_m',[0,300]),('seasonal_playback_eligible',True),('original_regional_context',{})]:
            bad=copy.deepcopy(packet);receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
            next(r for r in doc['measurements'] if r['current_id']=='zeehan')[key]=value
            next(r for r in bad['collections']['widths'] if r['current_id']=='zeehan')[key]=value
            receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
            target=Path(directory)/'tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
            run=subprocess.run([str(CLI),str(target),'-'],input=json.dumps(query),text=True,capture_output=True,encoding='utf8')
            assert run.returncode==2 and 'Original regional width' in run.stderr,run.stderr
    print('PASS: Zeehan historical width and separate qualitative occupations; mobile, source/native/WASM parity, no playback and coherent scope mutations')
if __name__=='__main__':main()
