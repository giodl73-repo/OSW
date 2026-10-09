"""Source range chart, no invented midpoint/annual cycle, native/WASM parity."""
import copy, hashlib, json, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import native, CLI
ROOT=Path(__file__).resolve().parents[1]

def main():
    inventory=json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    identifier='black-sea-rim-korotaev-2011-regional-width-range'
    query={'collection':'widths','filters':[{'field':'id','op':'eq','value':identifier}],'limit':10}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=black-sea-rim',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#regional-width-range').hidden===false")
        assert page.locator('#season-title').inner_text()=='Regional width range'
        assert '40–80 km' in page.locator('#season-value').inner_text()
        assert 'No midpoint selected' in page.locator('#regional-width-range').inner_text()
        assert 'Not annual extrema' in page.locator('#regional-width-range svg').get_attribute('aria-label')
        assert page.locator('#regional-width-range svg text').all_text_contents()==['40 km','80 km','0 km','100 km']
        assert 'not a fixed measurement layer' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-play').is_disabled()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert 'os-7-629-2011.pdf' in page.locator('#season-source a').get_attribute('href')
        page.screenshot(path=str(ROOT/'.pytest_cache/black-sea-range-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        assert page.locator('#regional-width-range svg text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        page.screenshot(path=str(ROOT/'.pytest_cache/black-sea-range-mobile-review.png'))
        # Switching removes stale range evidence; the earlier regional range also renders.
        page.locator('#season-current').select_option('labrador')
        assert page.locator('#regional-width-range').is_hidden()
        page.locator('#season-current').select_option('gaspe')
        assert '10–20 km' in page.locator('#regional-width-range').inner_text()
        page.locator('#season-current').select_option('black-sea-rim')
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:black-sea-rim"')
        assert 'Black Sea Rim Current' in page.locator('#route-atlas-preview > h3').inner_text()
        assert '40–80' in page.locator('#width-'+identifier).inner_text()
        assert page.locator('#width-rows tr').count()==len(inventory['measurements'])
        from urllib.parse import quote
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1')
        wasm=page.evaluate('window.oswLastQueryResult')
        assert wasm['rows']==native(query)['rows']
        row=wasm['rows'][0];assert row['width_range_km']==[40,80] and row['approximate_width_km'] is None
        assert row['annual_extrema_eligible'] is False and row['section_geometry'] is None
        # New source additions must not invalidate this regional-width check.
        # Compare the full inventory identities with the shipped query projection.
        width_ids=set();offset=0
        while True:
            all_widths=native({'collection':'widths','limit':100,'offset':offset})
            assert all_widths['total']==len(inventory['measurements'])
            assert all_widths['rows']
            width_ids.update(r['id'] for r in all_widths['rows'])
            offset+=len(all_widths['rows'])
            if offset>=all_widths['total']:break
        assert width_ids=={r['id'] for r in inventory['measurements']}
        # A mean offshore extent uses a distinct label and retains sampling metadata.
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=mindanao-current',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#season-title').textContent==='Mean surface offshore extent'",timeout=90000)
        assert '250–300 km reported offshore extent' in page.locator('#season-value').inner_text()
        assert 'not a paired-boundary full width' in page.locator('#regional-width-range').inner_text()
        assert 'mean surface offshore extent' in page.locator('#regional-width-range svg').get_attribute('aria-label')
        assert page.locator('#regional-width-range svg text').evaluate_all('(es)=>es[0].getBoundingClientRect().right < es[1].getBoundingClientRect().left')
        assert 'January 2014' in page.locator('#season-definition').inner_text()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert 'not available' in page.locator('#season-range').inner_text()
        assert 'not a fixed measurement layer' in page.locator('#season-definition').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        page.screenshot(path=str(ROOT/'.pytest_cache/mindanao-extent-mobile.png'),full_page=True)
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:mindanao-current"',timeout=90000)
        assert 'offshore extent of mean surface flow' in page.locator('#width-mindanao-schonau-2015-mean-surface-offshore-extent').inner_text()
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'mindanao-current'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1',timeout=90000)
        wasm=page.evaluate('window.oswLastQueryResult');assert wasm==native(query)
        row=wasm['rows'][0];assert row['width_range_km']==[250,300] and row['approximate_width_km'] is None
        context=row['mean_offshore_context'];assert context['campaign_context_is_mean_sampling_interval'] is False
        assert context['velocity_reference_depth_range_m']==[0,1000]
        assert context['source_date_discrepancy']
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=norwegian-coastal',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#season-title').textContent==='Regional width range'",timeout=90000)
        assert '20–30 km' in page.locator('#season-value').inner_text()
        assert 'Halten Bank' in page.locator('#season-definition').inner_text()
        assert 'full original article and Fig. 1 remain unreviewed' in page.locator('#season-definition').inner_text()
        assert 'no fixed measurement depth' in page.locator('#season-definition').inner_text()
        assert page.locator('#regional-width-range svg text').all_text_contents()==['20 km','30 km','0 km','50 km']
        assert page.locator('#regional-width-range svg text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        page.screenshot(path=str(ROOT/'.pytest_cache/norwegian-coastal-width-mobile.png'),full_page=True)
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:norwegian-coastal"',timeout=90000)
        assert '20–30' in page.locator('#width-norwegian-coastal-saetre-1999-halten-regional-width').inner_text()
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'norwegian-coastal'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1',timeout=90000)
        wasm=page.evaluate('window.oswLastQueryResult');assert wasm==native(query)
        assert wasm['rows'][0]['width_range_km']==[20,30] and wasm['rows'][0]['approximate_width_km'] is None
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=agulhas-return',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#season-title').textContent==='ADCP crossing width · layer median'",timeout=90000)
        assert '48 ±14 km' in page.locator('#season-value').inner_text()
        assert page.locator('#regional-width-range svg circle').count()==4
        assert 'Projection error is included already' in page.locator('#regional-width-range').inner_text()
        assert 'acoustic Doppler current profiler' in page.locator('#regional-width-range').inner_text()
        assert '1997 cruise' in page.locator('#season-value').inner_text()
        assert page.locator('#regional-width-range svg text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert 'not a fixed-depth surface width' in page.locator('#season-definition').inner_text()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for index,(width,error) in enumerate([(48,14),(73,18),(78,18),(48,18)]):
            page.locator('#season-phase').select_option(str(index))
            assert f'{width} ±{error} km' in page.locator('#season-value').inner_text()
        page.locator('#regional-width-range').scroll_into_view_if_needed()
        page.screenshot(path=str(ROOT/'.pytest_cache/agulhas-return-adcp-mobile.png'),full_page=True)
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:agulhas-return"',timeout=90000)
        assert page.locator('.atlas-width-record').count()==4
        assert '48 ±14 km source width and total error' in page.locator('.atlas-width-record').first.inner_text()
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'agulhas-return'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.total===4',timeout=90000)
        wasm=page.evaluate('window.oswLastQueryResult');assert wasm==native(query)
        assert [(r['approximate_width_km'],r['reported_total_error_km']) for r in wasm['rows']]==[(48,14),(73,18),(78,18),(48,18)]
        assert all(r['width_range_km'] is None and r['adcp_threshold_context']['confidence_level'] is None for r in wasm['rows'])
        # Table 2 stream-tube widths preserve threshold sensitivity and transport definitions.
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=west-spitsbergen&phase=west-spitsbergen-kolas-2018-b-tube-1',wait_until='networkidle')
        chart=page.locator('.stream-tube-width-chart');chart.wait_for(state='visible',timeout=90000)
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.locator('.stream-tube-width-table tbody tr').count()==6
        assert '0.02 m/s: 24 km; 0.08 m/s: 11 km' in page.locator('.stream-tube-width-table').inner_text()
        assert 'not confidence intervals or seasonal changes' in page.locator('#season-section-locator').inner_text()
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        chart.screenshot(path=str(ROOT/'.pytest_cache/wsc-stream-tube-width-chart.png'))
        page.locator('a').filter(has_text='Query all six width records').click()
        page.wait_for_function('window.oswLastQueryResult?.total===6',timeout=90000)
        request={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'west-spitsbergen'}],'limit':100}
        assert page.evaluate('window.oswLastQueryResult')==native(request)
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Awest-spitsbergen#route-atlas',wait_until='networkidle')
        page.locator('.atlas-width-evidence .stream-tube-width-chart').wait_for(state='visible',timeout=90000)
        assert page.locator('.atlas-width-record').count()==6
        # Explicit proposed branches expose numeric evidence without canonical transfer.
        import gzip
        packet=ROOT/'.pytest_cache/norwegian-branch-index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        for owner,count in [('norwegian-atlantic-slope',2),('norwegian-atlantic-front',1)]:
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#inventory-addition-'+owner,wait_until='networkidle')
            chart=page.locator(f'.proposed-width-chart[data-owner="{owner}"]')
            chart.wait_for(state='visible',timeout=90000)
            card=page.locator('#inventory-addition-'+owner)
            assert card.locator('details[id^="proposed-width-"]').count()==count
            assert chart.locator('circle').count()==(1 if count==2 else 0)
            assert 'not a width trend' in chart.get_attribute('aria-label')
            assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
            assert 'ADT means absolute dynamic topography' in card.inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            if count==1:assert 'mean width remains unknown' in card.inner_text()
            chart.screenshot(path=str(ROOT/f'.pytest_cache/{owner}-width-chart.png'))
            card.locator('a').filter(has_text='Query these branch-width records').click()
            page.wait_for_function('n=>window.oswSourceQueryResult?.rows.length===n',arg=count,timeout=90000)
            request={'document':'research/norwegian-atlantic-branch-width-scope-audit.json','pointer':'/measurements','filters':[{'field':'record.proposed_current_id','op':'eq','value':owner}],'limit':10}
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('window.oswSourceQueryResult')==expected
            assert all(r['record']['proposed_current_id']==owner and 'current_id' not in r['record'] for r in expected['rows'])
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#inventory-addition-norwegian-atlantic',wait_until='networkidle')
        page.wait_for_function('document.querySelector("#inventory-addition-norwegian-atlantic")?.textContent.includes("Branch widths cannot be added")',timeout=90000)
        assert page.locator('#inventory-addition-norwegian-atlantic .proposed-width-chart').count()==0
        # Abstract-only Pacific widths render scales, with no manufactured annual series.
        for owner,labels in [('california',['500 km','800 km','0 km','1000 km']),('oyashio',['~100 km','0 km','150 km'])]:
            page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+owner,wait_until='networkidle')
            chart=page.locator('.abstract-regional-width svg');chart.wait_for(state='visible',timeout=90000)
            assert chart.locator('text').all_text_contents()==labels
            assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
            assert 'Abstract summary' in chart.get_attribute('aria-label')
            assert 'original boundary methods and figures remain unreviewed' in page.locator('.abstract-regional-width').inner_text()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-section-locator').is_hidden()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
            chart.screenshot(path=str(ROOT/f'.pytest_cache/{owner}-abstract-width.png'))
            page.locator('#season-atlas').click()
            page.wait_for_function('owner=>document.querySelector("#route-atlas-select")?.value==="current:"+owner',arg=owner,timeout=90000)
            page.locator('#route-atlas-preview .abstract-regional-width svg').wait_for(state='visible',timeout=90000)
            query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner}],'limit':10}
            page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
            page.wait_for_function('window.oswLastQueryResult?.rows?.length===1',timeout=90000)
            assert page.evaluate('window.oswLastQueryResult')==native(query)
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=somali&phase=somali-schott-2001-march-may-coastal-width',wait_until='networkidle')
        chart=page.locator('.seasonal-regional-width svg');chart.wait_for(state='visible',timeout=90000)
        assert page.locator('#season-title').inner_text()=='Seasonal regional width scale'
        assert '50–100 km seasonal regional scale' in page.locator('#season-value').inner_text()
        assert page.locator('[data-width-evidence="seasonal_statement"]').count()==3
        assert page.locator('[data-width-evidence="unknown"]').count()==9
        assert chart.locator('text').all_text_contents()==['50 km','100 km','0 km','150 km']
        assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
        assert page.locator('#season-play').is_disabled()
        assert page.locator('#season-section-locator').is_hidden()
        assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
        assert page.evaluate('oswSeasonPlan.eligible_indices')==[1,2]
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        chart.screenshot(path=str(ROOT/'.pytest_cache/somali-premonsoon-width-mobile.png'))
        page.locator('#season-phase').select_option('1');assert page.locator('#season-play').is_enabled()
        page.locator('#season-play').click()
        page.wait_for_function('document.querySelector("#season-phase").value==="2"',timeout=7000)
        assert 'Width: unknown' in page.locator('#season-definition').inner_text()
        page.locator('#season-play').click();page.locator('#season-phase').select_option('0')
        assert page.locator('#season-play').is_disabled()
        page.locator('#season-atlas').click()
        page.wait_for_function('document.querySelector("#route-atlas-select")?.value==="current:somali"',timeout=90000)
        assert page.locator('#route-atlas-preview [data-width-evidence="seasonal_statement"]').count()==3
        query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'somali'}],'limit':10}
        page.goto('http://127.0.0.1:8788/almanac/query.html?q='+quote(json.dumps(query)),wait_until='networkidle')
        page.wait_for_function('window.oswLastQueryResult?.rows?.length===1',timeout=90000)
        assert page.evaluate('window.oswLastQueryResult')==native(query)
        assert not errors,errors
        browser.close()
    # WSC semantic scope survives coherent record and receipt rewrites.
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    for key,value in [('width_range_km',[11,61]),('fixed_layer_bounds_m',[45,475]),('seasonal_playback_eligible',True)]:
        bad=copy.deepcopy(packet);row=next(r for r in bad['collections']['widths'] if r['id']=='west-spitsbergen-kolas-2018-b-tube-1');row[key]=value
        receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json']);next(r for r in doc['measurements'] if r['id']==row['id'])[key]=value
        receipt['source_json']=json.dumps(doc,ensure_ascii=False);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        path=ROOT/'.pytest_cache/wsc-stream-tube-tampered.json';path.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(path),'-'],input=json.dumps(request),capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'WSC' in result.stderr,(key,result.stderr)
    # Coherent source/row rewrites must still fail the shared Rust scope guard.
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    i=next(i for i,r in enumerate(bundle['collections']['widths']) if r['phase_kind']=='survey_layer_median_threshold_width')
    for key,value in [('confidence_level',0.95),('projection_error_is_included_in_total',False),('depth_bin_range_is_fixed_width_layer',True)]:
        bad=copy.deepcopy(bundle);bad['collections']['widths'][i]['adcp_threshold_context'][key]=value
        receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json']);doc['measurements']=bad['collections']['widths']
        receipt['source_json']=json.dumps(doc,ensure_ascii=False);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        path=ROOT/'.pytest_cache/adcp-scope-tampered.json';path.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(path),'-'],input=json.dumps(query),capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'ADCP' in result.stderr,(key,result.stderr)
    query={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'norwegian-coastal'}],'limit':10}
    for key,value in [('approximate_width_km',25),('fixed_layer_bounds_m',[0,150]),('seasonal_playback_eligible',True),('width_range_km',[20,80])]:
        bad=copy.deepcopy(bundle)
        row=next(r for r in bad['collections']['widths'] if r['current_id']=='norwegian-coastal');row[key]=value
        receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        source=next(r for r in doc['measurements'] if r['current_id']=='norwegian-coastal');source[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        path=ROOT/'.pytest_cache/norwegian-coastal-scope-tampered.json';path.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(path),'-'],input=json.dumps(query),capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Norwegian coastal' in result.stderr,(key,result.stderr)
    for key,value in [('approximate_width_km',40),('fixed_layer_bounds_m',[0,400]),('seasonal_playback_eligible',True)]:
        bad=copy.deepcopy(bundle);path='research/ocean-current-inventory-expansion-candidates.json'
        receipt=bad['manifest']['atlas_receipts'][path];doc=json.loads(receipt['source_json'])
        proposal=next(r for r in doc['entries'] if r['proposed_id']=='norwegian-atlantic-slope');proposal['width_evidence'][0][key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][path]=receipt['source_sha256']
        target=ROOT/'.pytest_cache/norwegian-proposed-scope-tampered.json';target.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(target),'--atlas'],capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Norwegian' in result.stderr,(key,result.stderr)
    for owner,key,value in [('california','approximate_width_km',650),('oyashio','observed_period',{'start':'1999-09-01','end':'2000-08-31'})]:
        bad=copy.deepcopy(bundle)
        next(r for r in bad['collections']['widths'] if r['current_id']==owner)[key]=value
        receipt=bad['manifest']['seasons_receipts']['widths'];doc=json.loads(receipt['source_json'])
        next(r for r in doc['measurements'] if r['current_id']==owner)[key]=value
        receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][receipt['source_file']]=receipt['source_sha256']
        path=ROOT/'.pytest_cache/abstract-width-tampered.json';path.write_text(json.dumps(bad),encoding='utf8')
        result=subprocess.run([str(CLI),str(path),'-'],input=json.dumps(query),capture_output=True,text=True,encoding='utf8')
        assert result.returncode==2 and 'Abstract regional width' in result.stderr,result.stderr
    from test_somali_seasonal_width import check_compiled_scope_and_independent_route_playback
    scratch=ROOT/'.pytest_cache/somali-native-gate';scratch.mkdir(exist_ok=True)
    check_compiled_scope_and_independent_route_playback(scratch)
    print('OK: proposed Norwegian Atlantic branches, Norwegian coastal and Black Sea regional range, primary source, null midpoint, no seasonal/edge inference, responsive range/ADCP error charts, cleanup, native/WASM query parity and coherent ADCP scope rejection')

if __name__=='__main__':main()
