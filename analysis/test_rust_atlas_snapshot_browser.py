"""Checked atlas sources, native/WASM parity, navigation and unavailable data."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI
JOIN='research/ocean-current-reference-route-state-join.json'
BASE='http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas'

def route_atlas_bundle(page,bundle):
    raw=json.dumps(bundle,ensure_ascii=False).encode('utf-8')
    manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_bytes())
    manifest['sha256']['almanac/query-data.json']=hashlib.sha256(raw).hexdigest()
    page.route('**/query-engine.manifest.json',lambda r:r.fulfill(json=manifest))
    page.route('**/query-data.json',lambda r:r.fulfill(body=raw,content_type='application/json'))

def without_state_join(page):
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    del bundle['manifest']['atlas_receipts'][JOIN]
    route_atlas_bundle(page,bundle)

def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    native=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf-8'))
    expected_sources=set(bundle['manifest']['atlas_receipts'])
    expected_sources.update(bundle['manifest']['seasons_receipts'][key]['source_file'] for key in ['widths','routes','frames'])
    expected_sources.add('research/ocean-motion-dashboard.json')
    assert native['state_join_available'] and set(native['sources_json'])==expected_sources
    for path,raw in native['sources_json'].items():assert raw==(ROOT/path).read_bytes().decode('utf-8'),path
    report=bundle['collections']['reference_routes'][0]['candidate_file']
    with tempfile.TemporaryDirectory() as directory:
        for kind in ['hash','missing_report','extra','join_dependency','schema','annual_scope','frame_projection','date_order','width_hash','width_projection','width_scope','gulf_dependency','gulf_scope','gulf_projection','model_support','model_scope','model_sync','model_date']:
            bad=json.loads(json.dumps(bundle));receipts=bad['manifest']['atlas_receipts']
            if kind=='hash':receipts[report]['source_json']+=' '
            elif kind=='missing_report':del receipts[report]
            elif kind=='extra':receipts['research/unsupported.json']=receipts[report]
            elif kind in ['model_support','model_scope','model_sync','model_date']:
                source='research/norkyst-ingoy-2024-map-frames.json'
                doc=json.loads(receipts[source]['source_json'])
                if kind=='model_support':bad['manifest']['input_sha256'][doc['frames'][0]['figure']]='0'*64
                else:
                    if kind=='model_scope':doc['state_footprint_join_eligible']=True
                    elif kind=='model_date':doc['frames'][0]['sample_time_utc']='2024-01-15T00:00:00Z'
                    else:
                        doc['frames'][0]['receipt_file']=doc['frames'][1]['receipt_file']
                        doc['frames'][0]['receipt_sha256']=doc['frames'][1]['receipt_sha256']
                    raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                    receipts[source].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][source]=digest
            elif kind=='gulf_dependency':
                bad['manifest']['input_sha256']['plans/gulf-stream-section-width-protocol-v1.md']='0'*64
            elif kind in ['gulf_scope','gulf_projection']:
                source='research/gulf-stream-section-width-series.json'
                doc=json.loads(receipts[source]['source_json'])
                if kind=='gulf_scope':doc['annual_width_range_km']=[70,150]
                else:doc['frames'][0]['approximate_section_span_km']=999
                raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                receipts[source].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][source]=digest
            elif kind in ['width_hash','width_projection','width_scope']:
                source='research/leeuwin-a101-monthly-plot-extraction.json'
                if kind=='width_hash':receipts[source]['source_json']+=' '
                else:
                    doc=json.loads(receipts[source]['source_json'])
                    if kind=='width_scope':doc['is_confidence_interval']=True
                    else:doc['months'][0]['label']='Different source'
                    raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                    receipts[source].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][source]=digest
            elif kind in ['annual_scope','frame_projection','date_order']:
                path='research/ocean-current-dated-timeline.json'
                doc=json.loads(receipts[path]['source_json'])
                if kind=='annual_scope':doc['annual_extrema_eligible']=True
                elif kind=='frame_projection':doc['frames'][0]['width_km']=123
                else:doc['frames'][0],doc['frames'][1]=doc['frames'][1],doc['frames'][0]
                raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                receipts[path].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][path]=digest
                for row in bad['collections']['geometry_frames']:
                    if row.get('timeline_file')==path:row['timeline_sha256']=digest
            else:
                path=JOIN if kind=='join_dependency' else report
                doc=json.loads(receipts[path]['source_json'])
                if kind=='schema':doc['schema']='unsupported'
                else:doc['input_sha256']['research/ocean-current-reference-path-candidates.json']='0'*64
                raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                receipts[path].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][path]=digest
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            result=subprocess.run([str(CLI),str(path),'--atlas'],capture_output=True,text=True)
            assert result.returncode==2 and not result.stdout and 'atlas' in result.stderr.lower(),(kind,result.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1100,'height':900});errors=[];direct=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct source reads disabled'))[-1])
        page.goto(BASE)
        expect(page.locator('#route-atlas-select option')).to_have_count(101,timeout=90000)
        expect(page.locator('#route-atlas-eddy-select option')).to_have_count(141)
        assert page.evaluate('window.oswAtlasSnapshot')==native
        assert page.locator('.route-card').count()==64
        assert page.locator('#route-status').get_attribute('data-engine')=='rust-osw-query-v1'
        page.locator('#route-atlas-select').select_option('current:agulhas')
        expect(page.locator('#route-atlas-preview')).to_contain_text('Agulhas')
        expect(page.locator('.route-atlas-state-links li[data-state-code="EAFR"]')).to_be_visible()
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not direct and not errors,(direct,errors)
        absent=browser.new_page();partial=json.loads(json.dumps(bundle))
        del partial['manifest']['atlas_receipts'][JOIN]
        del partial['manifest']['atlas_receipts']['research/ocean-current-dated-timeline-2025.json']
        del partial['manifest']['atlas_receipts']['research/leeuwin-a101-monthly-plot-extraction.json']
        route_atlas_bundle(absent,partial);absent.goto(BASE)
        expect(absent.locator('#route-atlas-select option')).to_have_count(101,timeout=90000)
        absent.locator('#route-atlas-select').select_option('current:agulhas')
        expect(absent.locator('.route-atlas-state-links')).to_contain_text('State crossing inventory unavailable')
        assert absent.locator('#route-atlas-preview .route-map').is_visible()
        absent.locator('#route-atlas-select').select_option('current:gulf-stream-system')
        absent.locator('.atlas-timeline summary').click()
        expect(absent.locator('.atlas-timeline-status')).to_contain_text('Saved samples unavailable from checked atlas',timeout=90000)
        assert absent.locator('.atlas-timeline-date').is_disabled()
        assert absent.locator('.atlas-timeline button').is_disabled()
        assert absent.locator('#route-atlas-select').input_value()=='current:gulf-stream-system'
        absent.locator('#route-atlas-select').select_option('current:leeuwin')
        expect(absent.locator('.atlas-width-month-status')).to_contain_text('unavailable or invalid',timeout=90000)
        assert absent.locator('.atlas-width-play').is_disabled()
        assert absent.locator('#route-atlas-preview .route-map').is_visible()
        failed=browser.new_page();failed.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'));failed.goto(BASE)
        expect(failed.locator('#route-status')).to_contain_text('unavailable',timeout=90000)
        expect(failed.locator('#route-atlas-status')).to_contain_text('Atlas unavailable')
        assert failed.locator('.route-card').count()==0
        assert failed.locator('#route-atlas-select option').count()==1
        browser.close()
    print(f'PASS: {len(native["sources_json"])} exact atlas source documents, eighteen loader rejections, native/WASM parity, 100 current/140 eddy selectors, 64 cards, no direct source reads, mobile and optional/unavailable data')

if __name__=='__main__':main()
