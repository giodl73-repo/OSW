"""Check dashboard coverage, filtering and content-based update indicators."""
import json
import hashlib
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_rust_query_browser import CLI

ROOT = Path(__file__).resolve().parents[1]


def settle(page):
    page.wait_for_function("document.querySelector('#dashboard-status').dataset.pending==='false'",timeout=90000)


def native_selection(request):
    result=subprocess.run([str(CLI),str(ROOT/'almanac/query-data.json'),'--dashboard-query'],input=json.dumps(request),capture_output=True,text=True,encoding='utf-8')
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def check_selection_oracles(rows):
    requests=[{'metric':'reference_route','text':'Portugal Current'},
        {'metric':'geometry','text':'Gulf of Mexico','record_type':'named_eddy'},
        {'metric':'reported_length','record_type':'named_current','covered_only':True},
        {'metric':'reference_route','changed_only':True,'changed_ids':[rows[0]['id'],rows[-1]['id']]},
        {'metric':'reference_route','text':'no-such-object-12345'}]
    for query in requests:
        result=native_selection(query)
        expected={r['id'] for r in rows if (not query.get('record_type') or r['type']==query['record_type'])
            and query.get('text','').lower() in (r['label']+' '+r['basin']).lower()
            and (not query.get('covered_only') or r['capabilities'][query['metric']]>0)
            and (not query.get('changed_only') or r['id'] in query['changed_ids'])}
        assert set(result['ids'])==expected,query
        assert result['map_scene']['matching_objects']==len(expected)
        assert result['map_scene']['mapped_objects']==len(expected)
    for query in [{'metric':'invented'},{'metric':'geometry','record_type':'invented'},
                  {'metric':'geometry','changed_ids':['missing']},
                  {'metric':'geometry','changed_ids':[rows[0]['id']]*2},
                  {'metric':'geometry','unknown':True},
                  {'metric':'geometry','view_box':[60,90,0,740]},
                  {'metric':'geometry','view_box':[60,90,1480,-1]},
                  {'metric':'geometry','view_box':[60,90,1480]}]:
        result=subprocess.run([str(CLI),str(ROOT/'almanac/query-data.json'),'--dashboard-query'],
            input=json.dumps(query),capture_output=True,text=True,encoding='utf-8')
        assert result.returncode==2 and not result.stdout and result.stderr,query




def route_snapshot(page, data):
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    receipt=json.dumps(data,ensure_ascii=False);digest=hashlib.sha256(receipt.encode()).hexdigest()
    bundle['manifest']['dashboard_receipt'].update(source_json=receipt,source_sha256=digest)
    bundle['manifest']['input_sha256']['research/ocean-motion-dashboard.json']=digest
    source={r['id']:r for r in data['entries']}
    for row in bundle['collections']['objects']:
        row['fingerprint']=source[row['id']]['fingerprint']
        row['section_fingerprints']=source[row['id']]['section_fingerprints']
    raw=json.dumps(bundle,ensure_ascii=False).encode()
    manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_bytes())
    manifest['sha256']['almanac/query-data.json']=hashlib.sha256(raw).hexdigest()
    page.route('**/query-engine.manifest.json',lambda route:route.fulfill(json=manifest))
    page.route('**/query-data.json',lambda route:route.fulfill(body=raw,content_type='application/json'))


def main():
    data = json.loads((ROOT / 'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
    check_selection_oracles(data['entries'])
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    result=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--dashboard'],encoding='utf-8'))
    assert result['ok'] and json.loads(result['snapshot_json'])==data
    # A valid receipt cannot hide disagreement with the shared inventory.
    with tempfile.TemporaryDirectory() as directory:
        for mutation in ['receipt','count','identity','projection']:
            bad=json.loads(json.dumps(bundle));doc=json.loads(bad['manifest']['dashboard_receipt']['source_json'])
            if mutation=='count':doc['counts']['named_current']+=1
            if mutation=='identity':doc['entries'][0]['id']=doc['entries'][1]['id']
            if mutation=='projection':doc['entries'][0]['fingerprint']='changed'
            raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
            bad['manifest']['dashboard_receipt'].update(source_json=raw,source_sha256=digest)
            bad['manifest']['input_sha256']['research/ocean-motion-dashboard.json']=digest
            if mutation=='receipt':bad['manifest']['dashboard_receipt']['source_sha256']='0'*64
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            rejected=subprocess.run([str(CLI),str(path),'--dashboard'],capture_output=True,text=True)
            assert rejected.returncode==2 and not rejected.stdout and 'dashboard' in rejected.stderr.lower(),mutation
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        url = 'http://127.0.0.1:8788/almanac/dashboard.html'
        page.goto(url,wait_until='networkidle')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=90000)
        settle(page)
        assert page.evaluate('window.oswDashboardSnapshot.engine')=='rust-osw-query-v1'
        assert page.evaluate('window.oswDashboardSnapshot.snapshot')==data
        settle(page)
        selection=page.evaluate('window.oswDashboardSelection')
        assert selection['result']==native_selection(selection['request'])
        scene=selection['result']['map_scene']
        assert scene['mapped_objects']==240
        assert not scene['omitted_features']
        grouped=[f for f in scene['features'] if f['kind']=='marker' and f['group']]
        assert len(grouped)==1
        assert set(grouped[0]['entity_ids'])=={r['id'] for r in data['entries'] if any(f.get('group')=='Gulf of Mexico regional gateway' for f in r['map_features'])}
        beck=selection['result']['beck_scene']
        currents=[r for r in data['entries'] if r['type']=='named_current']
        assert [r['id'] for r in beck['stations']]==[r['id'] for r in currents]
        assert {r['id'] for panel in beck['panels'] for r in panel['rows']}=={r['id'] for r in currents}
        assert {c['id'] for c in beck['connections']}=={c['id'] for c in data['connections']}
        assert sum(len(g['ids']) for g in beck['eddy_groups'])==140
        assert page.locator('#dashboard-schematic').is_visible()
        assert page.locator('.beck-station').count() == 100
        assert '100 / 100 current stations in view' in page.locator('#dashboard-station-count').inner_text()
        page.locator('#dashboard-search').fill('Portugal Current')
        settle(page)
        page.locator('#dashboard-covered').check()
        settle(page)
        page.locator('#dashboard-region').select_option('atlantic')
        settle(page)
        assert page.locator('.beck-station').count() == 1
        page.locator('#dashboard-show-all').click()
        settle(page)
        assert page.locator('.beck-station').count() == 100
        assert page.locator('#dashboard-region').input_value() == 'world'
        assert not page.locator('#dashboard-covered').is_checked()
        assert page.locator('.beck-station .beck-name').count() == 100
        station=page.locator('.beck-station').first
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '0'
        station.locator('circle').hover()
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '1'
        page.mouse.move(0,0)
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '0'
        station.focus()
        assert station.locator('.beck-name').evaluate('(el)=>getComputedStyle(el).opacity') == '1'
        stations=page.locator('.beck-station').evaluate_all('(els)=>els.map(e=>({n:Number(e.dataset.stationNumber),x:Number(e.dataset.worldX),y:Number(e.dataset.worldY)}))')
        assert sorted(s['n'] for s in stations) == list(range(1,101))
        assert all(74<=s['x']<=1526 and 104<=s['y']<=816 for s in stations)
        assert all(((a['x']-b['x'])**2+(a['y']-b['y'])**2)**.5>=30 for i,a in enumerate(stations) for b in stations[i+1:])
        assert page.locator('.beck-eddy-gateway').count() > 10
        assert page.locator('.beck-connection').count() == 5
        page.locator('.beck-connection').first.focus()
        page.keyboard.press('Enter')
        assert 'Read the source' in page.locator('#dashboard-schematic-detail').inner_text()
        assert page.locator('.schematic-station').count() == 100
        assert page.locator('.schematic-station text').count() == 100
        page.locator('.schematic-station').first.focus()
        page.keyboard.press('Enter')
        assert page.locator('#dashboard-schematic-detail').is_visible()
        page.locator('#dashboard-map-view').click()
        settle(page)
        assert page.locator('#dashboard-atlas').is_visible()
        assert page.locator('#dashboard-grid').is_hidden()
        assert page.locator('.atlas-marker').count() > 100
        page.locator('#dashboard-search').fill('Portugal Current')
        settle(page)
        assert page.locator('.atlas-route.lit').count() == 1
        page.locator('.atlas-marker').first.focus()
        page.keyboard.press('Enter')
        assert 'Portugal Current' in page.locator('#dashboard-map-detail').inner_text()
        page.locator('#dashboard-search').fill('')
        settle(page)
        page.locator('#dashboard-schematic-view').click()
        settle(page)
        page.locator('#dashboard-search').fill('Antilles Current')
        settle(page)
        page.locator('#dashboard-metric').select_option('scope_notes')
        settle(page)
        assert page.locator('.beck-station.lit').count() == 1
        page.locator('.beck-station').first.focus()
        page.keyboard.press('Enter')
        assert 'Modern observations' in page.locator('#dashboard-schematic-detail').inner_text()
        page.locator('#dashboard-search').fill('')
        settle(page)
        page.locator('#dashboard-metric').select_option('reference_route')
        settle(page)
        page.locator('#dashboard-map-view').click()
        settle(page)
        page.locator('#dashboard-type').select_option('named_eddy')
        settle(page)
        page.locator('#dashboard-region').select_option('gulf')
        settle(page)
        gateway=page.locator('.atlas-marker').filter(has=page.locator('.marker-label')).first
        gateway.locator('.marker-core').click()
        assert 'regional gateway' in page.locator('#dashboard-map-detail').inner_text()
        assert page.locator('#dashboard-map-detail h4').count() >= 96
        page.locator('#dashboard-region').select_option('world')
        settle(page)
        page.locator('#dashboard-type').select_option('all')
        settle(page)
        page.locator('#dashboard-atlas').screenshot(path=str(ROOT / 'figures/motion-dashboard-atlas-review.png'))
        page.locator('#dashboard-card-view').click()
        settle(page)
        assert page.locator('.motion-card').count() == 240
        assert page.locator('.motion-card.updated').count() == 0
        gulf=page.locator('[data-id="current:gulf-stream-system"]')
        gulf.locator('summary').click()
        assert '2026-09-28' in gulf.inner_text()
        coastal=page.locator('[data-id="current:norwegian-coastal"]')
        coastal.locator('summary').click()
        assert '2024-12-15' in coastal.inner_text()
        assert 'not individually reviewed' in coastal.inner_text()
        for metric in ['reference_route','reported_length','scoped_width','geometry','time_samples','source_connectivity','scope_notes','dated_diagnostics','flow_network','passage_transport']:
            page.locator('#dashboard-metric').select_option(metric)
            settle(page)
            expected=sum(r['capabilities'][metric]>0 for r in data['entries'])
            assert page.locator('.motion-card.lit').count() == expected
            page.locator('#dashboard-covered').check()
            settle(page)
            assert page.locator('.motion-card').count() == expected
            selected=page.evaluate('window.oswDashboardSelection')
            assert selected['result']==native_selection(selected['request'])
            assert set(selected['result']['ids'])=={r['id'] for r in data['entries'] if r['capabilities'][metric]>0}
            page.locator('#dashboard-covered').uncheck()
            settle(page)
        page.locator('#dashboard-type').select_option('named_eddy')
        settle(page)
        assert page.locator('.motion-card').count() == 136
        page.locator('#dashboard-type').select_option('all')
        settle(page)
        page.locator('#dashboard-search').fill('Portugal Current')
        settle(page)
        assert page.locator('.motion-card').count() == 1
        page.evaluate("""()=>{const input=document.querySelector('#dashboard-search');for(const value of ['Kuroshio','no-such-object-12345','Portugal Current']){input.value=value;input.dispatchEvent(new Event('input',{bubbles:true}));}}""")
        settle(page)
        assert page.locator('.motion-card').count()==1
        assert page.locator('.motion-card').get_attribute('data-id')=='current:portugal'
        assert 'reference-routes.html#portugal' in page.locator('.record-links a').first.get_attribute('href')
        page.locator('#dashboard-search').fill('')
        settle(page)
        page.locator('#dashboard-grid').screenshot(path=str(ROOT / 'figures/motion-dashboard-cards-review.png'))
        changed=json.loads(json.dumps(data))
        changed['entries'][0]['fingerprint']='test-new-record-content'
        changed['entries'][0]['section_fingerprints']['sources']='test-source-change'
        route_snapshot(page,changed)
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("document.querySelectorAll('.motion-card.updated').length === 1")
        assert '1 changed since marked seen' in page.locator('#dashboard-status').inner_text()
        assert 'Sources changed' in page.locator('.motion-card.updated .change-reason').inner_text()
        page.locator('#dashboard-changed').check()
        settle(page)
        assert page.locator('.motion-card').count() == 1
        page.reload(wait_until='networkidle')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=90000)
        settle(page)
        assert page.locator('.motion-card.updated').count() == 1
        assert page.locator('.atlas-marker.updated').count() > 0
        page.locator('#dashboard-card-view').click()
        settle(page)
        page.locator('#dashboard-seen').click()
        settle(page)
        assert page.locator('.motion-card.updated').count() == 0
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("!document.getElementById('dashboard-refresh').disabled")
        assert page.locator('.motion-card.updated').count() == 0
        page.unroute('**/query-data.json')
        page.route('**/query-data.json',lambda route:route.fulfill(status=503,body='unavailable'))
        page.locator('#dashboard-refresh').click()
        page.wait_for_function("document.getElementById('dashboard-status').textContent.includes('previously loaded')")
        assert page.locator('.motion-card').count() == 240
        page.emulate_media(reduced_motion='reduce')
        page.set_viewport_size({'width':320,'height':900})
        page.locator('#dashboard-map-view').click()
        settle(page)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(ROOT / 'figures/motion-dashboard-mobile-review.png'),full_page=False)
        assert not errors,errors
        blocked=browser.new_page()
        blocked.route('**/query-data.json',lambda route:route.fulfill(status=503,body='unavailable'))
        blocked.goto(url)
        blocked.wait_for_function("document.querySelector('#dashboard-status').textContent.includes('Update check failed')",timeout=90000)
        assert blocked.locator('.motion-card').count()==0
        assert blocked.locator('.beck-station').count()==0
        assert blocked.evaluate('window.oswDashboardSnapshot===undefined')
        browser.close()
    print('OK: native/WASM dashboard parity, four receipt/projection rejections, atlas routes, keyboard selection, 240 records, coverage lights, updates, outage retention and mobile layout')


if __name__ == '__main__': main()
