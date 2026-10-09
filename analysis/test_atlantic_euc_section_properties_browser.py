"""Verify original section values, date conflicts, mobile charts and Rust source parity."""
import copy,gzip,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI,native
from check_atlantic_euc_section_properties import PATH
def main():
    audit=json.loads((ROOT/PATH).read_bytes());records=audit['section_properties']['records']
    request={'document':PATH,'pointer':'/section_properties/records','limit':100}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        index=Path(folder)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        expected=json.loads(subprocess.check_output([str(CLI),'--index',str(index),'-'],input=json.dumps(request),encoding='utf8'))
        assert [r['record'] for r in expected['rows']]==records
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#atlantic-euc-reach-reference-path-candidate')
            panel=page.locator('#atlantic-euc-reach-reference-path-candidate .atlantic-euc-section-properties');panel.wait_for(state='visible',timeout=90000)
            assert panel.locator('svg').count()==2 and panel.locator('svg circle').count()==16
            for i,field in enumerate(['maximum_eastward_speed_cm_s','maximum_speed_depth_m']):
                assert panel.locator('svg').nth(i).locator('circle title').all_text_contents()==[f"CAP {r['campaign']}: {r[field]} {'cm/s' if i==0 else 'm'}; Table II {r['table_ii_date_text']}; Table I {r['table_i_campaign_period']}"+('; unresolved date conflict' if r['date_conflict'] else '') for r in records]
            panel.locator('summary').click();assert panel.locator('tbody tr').count()==8
            assert panel.locator('tbody').inner_text().count('Unresolved conflict')==2
            assert 'Nov 74' in panel.inner_text() and 'October–November 1979' in panel.inner_text()
            assert 'Juin 79' in panel.inner_text() and 'June 1980' in panel.inner_text()
            page.set_viewport_size({'width':320,'height':800})
            for svg in panel.locator('svg').all():
                assert svg.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left-1&&b.right<=s.right+1&&parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12})')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            panel.locator('svg').first.screenshot(path=str(ROOT/'.pytest_cache/atlantic-euc-core-speed-mobile.png'))
            panel.get_by_role('link',name='Query all original section records').click()
            page.wait_for_function('window.oswSourceQueryResult?.total===8',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==expected
            assert not errors,errors
            browser.close()
        query={'collection':'route_decisions','filters':[{'field':'current_id','op':'eq','value':'atlantic-equatorial-undercurrent'}],'limit':10}
        result=native(query);assert result['total']==1 and result['rows'][0]['scope_reviews'][0]['document']==audit
        packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
        for key,value in [('whole_current_width_km',200),('seasonal_playback_eligible',True),('date_conflict_count',0)]:
            bad=copy.deepcopy(packet);doc=copy.deepcopy(audit);doc['section_properties'][key]=value
            receipt=bad['manifest']['atlas_receipts'][PATH];receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][PATH]=receipt['source_sha256']
            row=next(r for r in bad['collections']['route_decisions'] if r['current_id']=='atlantic-equatorial-undercurrent');row['scope_reviews'][0]['document']=doc;row['scope_reviews'][0]['source_sha256']=receipt['source_sha256']
            target=Path(folder)/'tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
            run=subprocess.run([str(CLI),str(target),'-'],input=json.dumps(query),text=True,capture_output=True,encoding='utf8')
            assert run.returncode==2 and 'Atlantic section' in run.stderr,run.stderr
    print('PASS: Atlantic section core properties, unresolved dates, mobile text, source/native/WASM parity and coherent native scope mutations')
if __name__=='__main__':main()
