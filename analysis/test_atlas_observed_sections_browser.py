"""Observed transverse samples zoom into a current card without a route claim."""
import copy,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI
from test_rust_atlas_snapshot_browser import route_atlas_bundle

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788/almanac/reference-routes.html'
DATA='**/antilles-ab0505-400m-section-diagnostic.json'

def main():
    document=json.loads((ROOT/'research/antilles-ab0505-400m-section-diagnostic.json').read_text(encoding='utf-8'))
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    expected=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf-8'))['observed_section_views']['research/antilles-ab0505-400m-section-diagnostic.json']
    for section in document['sections']:
        stations=expected['sections'][section['id']]['stations'];assert len(stations)==len(section['samples'])
        for station,sample in zip(stations,section['samples']):
            lon,lat=sample['coordinates_lon_lat']
            assert abs(station['x']-(60+(lon+180)/360*1480))<1e-9
            assert abs(station['y']-(90+(90-lat)/180*740))<1e-9
            assert station['cast_id']==sample['cast_id'] and sample['average_cast_time_utc'] in station['label']
            assert station['color']==('#a6aeb1' if sample['northward_m_s'] is None else '#f1b15b' if sample['quality_class']=='caution' else '#64dfce')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        direct=[]
        def block_atlas_reads(route):
            if urlparse(page.url).path.endswith('/reference-routes.html'):
                direct.append(route.request.url);route.fulfill(status=503,body='Direct source reads disabled')
            else:route.continue_()
        page.route('**/research/*.json',block_atlas_reads)
        page.goto(BASE+'?atlas-feature=current%3Aantilles#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false',timeout=90000)
        assert page.locator('#route-atlas-map .atlas-observed-station').count()==23
        assert 'has-observed-samples' in page.locator('#route-atlas-map').get_attribute('class')
        assert page.locator('#route-atlas-preview .atlas-observed-section-map').is_visible()
        assert 'Offshore half-peak boundary unresolved' in page.locator('.atlas-observed-section-status').inner_text()
        assert page.locator('#route-atlas-preview .route-map').count()==0
        assert page.locator('#route-atlas-map').get_attribute('viewBox')!='60 90 1480 740'
        assert page.evaluate("window.oswAtlasSnapshot.observed_section_views['research/antilles-ab0505-400m-section-diagnostic.json']")==expected
        for cast,station in zip(page.locator('#route-atlas-map .atlas-observed-station').all(),expected['sections']['abaco_first']['stations']):
            assert float(cast.locator('circle').get_attribute('cx'))==station['x']
            assert float(cast.locator('circle').get_attribute('cy'))==station['y']
            assert cast.get_attribute('aria-label')==station['label']
        select=page.locator('.atlas-observed-section-select');select.select_option('abaco_repeat')
        assert page.locator('#route-atlas-map .atlas-observed-station').count()==27
        assert 'About 37 km one-sided' in page.locator('.atlas-observed-section-status').inner_text()
        assert parse_qs(urlparse(page.url).query)['atlas-section']==['abaco_repeat']
        saved=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        page.reload(wait_until='networkidle')
        expect(page.locator('.atlas-observed-section-select')).to_have_value('abaco_repeat',timeout=90000)
        assert page.url==saved
        x,y,w,h=map(float,page.locator('#route-atlas-map').get_attribute('viewBox').split())
        for sample in document['sections'][1]['samples']:
            lon,lat=sample['coordinates_lon_lat'];assert x<=60+(lon+180)/360*1480<=x+w;assert y<=90+(90-lat)/180*740<=y+h
        station=page.locator('#route-atlas-map .atlas-observed-station').first
        page.mouse.move(0,0);page.locator('#route-atlas-select').focus()
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
        station.focus();page.keyboard.press('Enter')
        assert station.locator('text').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        assert 'AB0505_063' in page.locator('.atlas-observed-cast-info').inner_text(), (page.locator('.atlas-observed-cast-info').inner_text(),station.get_attribute('data-cast-id'),page.evaluate('document.activeElement.outerHTML'))
        assert 'no sample at 400 m' in page.locator('.atlas-observed-cast-info').inner_text()
        page.locator('.atlas-observed-details-link').click()
        page.wait_for_function('document.querySelector("#section-select")?.value==="abaco_repeat"')
        page.get_by_role('link',name='Return to Antilles on the atlas').click()
        try:
            page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false',timeout=90000)
        except Exception as error:
            raise AssertionError({'url':page.url,'atlas_status':page.locator('#route-atlas-status').all_text_contents(),
                                  'section_status':page.locator('.atlas-observed-section-status').all_text_contents(),
                                  'selectors':page.locator('#route-atlas-select').all_text_contents(),'page_errors':errors}) from error
        expect(page.locator('.atlas-observed-section-select')).to_have_value('abaco_repeat',timeout=90000)
        page.locator('#route-atlas').screenshot(path=str(ROOT/'figures/antilles-observed-atlas-card-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('.atlas-observed-overlay').count()==0
        assert 'has-observed-samples' not in (page.locator('#route-atlas-map').get_attribute('class') or '')
        assert 'atlas-section' not in parse_qs(urlparse(page.url).query)
        page.locator('#route-atlas-select').select_option('current:antilles')
        page.wait_for_function('document.querySelector(".atlas-observed-section-select")?.disabled===false',timeout=90000)
        page.locator('#route-atlas-world').click()
        assert page.locator('.atlas-observed-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        assert 'atlas-section' not in page.url
        # A disposed card must not reappear when checked source delivery resolves.
        page.evaluate("window.originalAtlasReady=window.oswAtlasSourcesReady;window.oswObservedDelayResolved=false;window.oswAtlasSourcesReady=window.originalAtlasReady.then(d=>new Promise(resolve=>setTimeout(()=>{window.oswObservedDelayResolved=true;resolve(d)},500)))")
        page.locator('#route-atlas-select').select_option('current:antilles')
        page.locator('#route-atlas-world').click()
        page.wait_for_function('window.oswObservedDelayResolved')
        assert page.locator('.atlas-observed-overlay').count()==0
        assert page.locator('#route-atlas-preview').is_hidden()
        page.evaluate('window.oswAtlasSourcesReady=window.originalAtlasReady')
        # Missing optional observed evidence preserves the checked current card.
        partial=copy.deepcopy(bundle);del partial['manifest']['atlas_receipts']['research/antilles-ab0505-400m-section-diagnostic.json']
        missing=browser.new_page();route_atlas_bundle(missing,partial)
        missing.goto(BASE+'?atlas-feature=current%3Aantilles#route-atlas')
        expect(missing.locator('.atlas-observed-section-status')).to_contain_text('standalone',timeout=90000)
        assert missing.locator('.atlas-observed-overlay').count()==0
        assert missing.locator('.atlas-observed-details-link').get_attribute('href')=='antilles-sections.html'
        assert missing.locator('#route-atlas-select').input_value()=='current:antilles'
        # Altered full-width scope is rejected even with a repinned source receipt.
        bad=copy.deepcopy(bundle);doc=copy.deepcopy(document);doc['whole_current_width_km']=74
        path='research/antilles-ab0505-400m-section-diagnostic.json';raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
        bad['manifest']['atlas_receipts'][path].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][path]=digest
        next(r for r in bad['collections']['diagnostics'] if r['id']=='diagnostic:antilles-observed-sections')['document']=doc
        for row in bad['collections']['series']:
            if row.get('evidence_role')=='observed_sections_with_unadmitted_one_sided_span':row['evidence_sha256']=digest
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'bad.json';file.write_text(json.dumps(bad),encoding='utf-8')
            rejected=subprocess.run([str(CLI),str(file),'--atlas'],capture_output=True,text=True)
            assert rejected.returncode==2 and not rejected.stdout and 'observed' in rejected.stderr.lower(),rejected.stderr
        invalid=browser.new_page();route_atlas_bundle(invalid,bad);invalid.goto(BASE)
        expect(invalid.locator('#route-atlas-status')).to_contain_text('Atlas unavailable',timeout=90000)
        assert invalid.locator('.atlas-observed-overlay').count()==0
        assert not direct,direct
        assert not errors,errors
        browser.close()
    print('OK: 23/27 observed atlas stations, local card, saved occupation, keyboard cast, standalone link, mobile reflow, global/switch cleanup and native/WASM positions, no direct reads, delayed disposal, invalid scope rejection and missing optional evidence')

if __name__=='__main__':main()
