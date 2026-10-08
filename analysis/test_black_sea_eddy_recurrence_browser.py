"""All nine summaries, original lifetime units, object and query WASM parity."""
import copy, hashlib, json, os, subprocess, tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_query_browser import CLI, ROOT, native

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    rows=bundle['collections']['eddy_recurrence']
    query={'collection':'eddy_recurrence','sort':{'field':'reported_occurrence_days_per_year_approx','direction':'desc'},'limit':50}
    expected=native(query);assert expected['total']==9
    assert expected['rows'][0]['label']=='Bosphorus Eddy'
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':1100,'height':950});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for row in rows:
            page.goto('http://127.0.0.1:8788/almanac/object.html?id='+quote(row['entity_id']),wait_until='networkidle')
            page.wait_for_selector('#eddy-recurrence-summary')
            section=page.locator('#eddy-recurrence-summary');text=section.inner_text()
            assert f"About {row['reported_occurrence_days_per_year_approx']} presence days per year" in text
            assert section.locator('meter').get_attribute('max')=='365'
            assert int(section.locator('meter').get_attribute('value'))==row['reported_occurrence_days_per_year_approx']
            lifetime=row['reported_event_lifetime_approx']
            assert ('Event lifetime: not quantified' if lifetime is None else f"about {lifetime} {row['event_lifetime_unit']}") in text
            assert row['seasonal_description'] in text and 'not a dated individual' in text
            assert 'No dated footprint' in text
            assert page.evaluate('window.oswObjectView.collections.eddy_recurrence')==[row]
            run=subprocess.run([str(CLI),str(ROOT/'almanac/query-data.json'),'--object-view',row['entity_id']],capture_output=True,text=True,encoding='utf-8')
            assert run.returncode==0,run.stderr
            assert page.evaluate('window.oswObjectView')==json.loads(run.stdout)
        page.set_viewport_size({'width':320,'height':800})
        page.locator('#eddy-recurrence-summary').scroll_into_view_if_needed()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(ROOT/'.pytest_cache/eddy-recurrence-mobile.png'))
        page.get_by_role('link',name='Compare all nine Black Sea recurrence summaries').click()
        page.wait_for_function('window.oswLastQueryResult?.total===9')
        assert page.evaluate('window.oswLastQueryResult')==expected
        assert page.locator('#query-rows tr').count()==9
        assert 'presence days/year' in page.locator('#query-rows').inner_text()
        page.goto('http://127.0.0.1:8788/almanac/object.html?id=eddy%3Ageography%3Adanube-eddy-region',wait_until='networkidle')
        page.wait_for_function('window.oswObjectView')
        assert page.locator('#eddy-recurrence-summary').count()==0
        assert page.evaluate('window.oswObjectView.collections.eddy_recurrence')==[]
        assert not errors,errors
        browser.close()
    # Reject coherent receipt rewrites that attempt to turn a region into events.
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        path=Path(folder)/'tampered.json'
        for key,value in [('seasonal_playback_eligible',True),('geometry',{'type':'Point','coordinates':[29,41]}),('observation_period',{'start':'2003-01-01','end':'2003-12-31'})]:
            bad=copy.deepcopy(bundle);bad['collections']['eddy_recurrence'][0][key]=value
            receipt=bad['manifest']['eddy_recurrence_receipt'];doc=json.loads(receipt['source_json']);doc['entries']=bad['collections']['eddy_recurrence']
            receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
            bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
            path.write_text(json.dumps(bad),encoding='utf-8')
            result=subprocess.run([str(CLI),str(path),'-'],input=json.dumps(query),text=True,encoding='utf-8',capture_output=True)
            assert result.returncode==2 and 'Recurrence' in result.stderr,(key,result.stderr)
    print('PASS: all nine recurrence cards and native/WASM parity, units, mobile, sorting, absent Danube summary and three coherent-receipt scope rejections')

if __name__=='__main__':main()
