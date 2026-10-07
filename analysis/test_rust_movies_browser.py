"""Rights-screened movie joins, independent selection oracle and real WASM UI."""
import copy,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI
from test_rust_atlas_snapshot_browser import route_atlas_bundle

BASE='http://127.0.0.1:8788/almanac/movies.html'


def native(selection,bundle=None):
    run=subprocess.run([str(CLI),str(bundle or ROOT/'almanac/query-data.json'),'--movies'],input=json.dumps(selection),text=True,encoding='utf-8',capture_output=True)
    return json.loads(run.stdout) if run.stdout else {'ok':False,'error':run.stderr}


def main():
    preview=ROOT/'almanac/release/v0.1.0-rights-screened-preview'
    docs={name:json.loads((preview/(name+'.json')).read_bytes()) for name in ['tiles','tile_state_relations','media','entities']}
    entities={r['id']:r for r in docs['entities']}
    def expected(selection):
        query=selection.get('query','').strip().lower();result=[]
        for tile in docs['tiles']:
            states=[r for r in docs['tile_state_relations'] if r['tile_id']==tile['tile_id']]
            ids={r['entity_id'] for r in docs['media'] if r.get('tile_id')==tile['tile_id']}
            if selection.get('zoom') is not None and selection['zoom']!=tile['zoom']:continue
            if selection.get('state_id') and not any(r['state_id']==selection['state_id'] for r in states):continue
            if query and query not in tile['tile_id'].lower() and not any(query in entities[id]['label'].lower() for id in ids):continue
            result.append({'tile':tile,'states':[{'entity':entities[r['state_id']],'relation':r} for r in sorted(states,key=lambda r:(-r['display_coverage_fraction'],r['id']))], 'objects':sorted((entities[id] for id in ids),key=lambda r:(r['label'].lower(),r['id']))})
        return result
    selections=[{},*({'zoom':z} for z in range(3)),{'query':' Agulhas '},{'query':'level0_A_1'},{'state_id':'state:CAMR'},{'zoom':2,'state_id':'state:CAMR','query':'gulf'},{'query':'no-such-crop'}]
    views=[native(s) for s in selections]
    for selection,view in zip(selections,views,strict=True):
        assert view['ok'],(selection,view.get('error'))
        assert view['rows']==expected(selection),selection
        assert view['total']==70 and view['matched']==len(view['rows'])
        assert view['source_scope']=='rights_screened_preview_not_published'
    for invalid in [{'zoom':3},{'zoom':-1},{'state_id':'state:missing'},{'query':False},{'unexpected':True}]:assert not native(invalid)['ok']
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with tempfile.TemporaryDirectory() as tmp:
        for kind in ['hash','export_hash','canonical_projection','missing','scope']:
            bad=copy.deepcopy(bundle);receipts=bad['manifest']['movies_receipts']
            if kind=='hash':receipts['media']['source_json']+=' '
            elif kind=='missing':del receipts['entities']
            elif kind=='export_hash':receipts['media']['source_sha256']='0'*64
            else:
                name='manifest' if kind=='scope' else 'entities';doc=json.loads(receipts[name]['source_json'])
                if kind=='scope':doc['status']='published'
                else:doc[0]['label']='changed'
                raw=json.dumps(doc);digest=hashlib.sha256(raw.encode()).hexdigest()
                receipts[name].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][receipts[name]['source_file']]=digest
                if kind=='canonical_projection':
                    manifest=json.loads(receipts['manifest']['source_json'])
                    next(r for r in manifest['files'] if r['path']=='entities.json')['sha256']=digest
                    raw=json.dumps(manifest);digest=hashlib.sha256(raw.encode()).hexdigest()
                    receipts['manifest'].update(source_json=raw,source_sha256=digest);bad['manifest']['input_sha256'][receipts['manifest']['source_file']]=digest
            path=Path(tmp)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8')
            rejected=native({},path);assert not rejected['ok'] and 'movie' in rejected['error'].lower(),(kind,rejected)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1200,'height':900});errors=[];direct=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.route('**/release/**/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct release reads disabled'))[-1])
        page.goto(BASE)
        expect(page.locator('#movie-rows tr')).to_have_count(70,timeout=90000)
        assert page.evaluate('window.oswMovieView')==views[0]
        expect(page.locator('#movie-state option')).to_have_count(57)
        for selection,view in zip(selections,views,strict=True):
            page.locator('#movie-query').fill(selection.get('query',''))
            page.locator('#movie-zoom').select_option(str(selection.get('zoom','all')))
            page.locator('#movie-state').select_option(selection.get('state_id','all'))
            wanted={'query':view['selection']['query'],'zoom':str(view['selection']['zoom']) if view['selection']['zoom'] is not None else 'all','state_id':view['selection']['state_id'] or 'all'}
            page.wait_for_function("s=>window.oswMovieView?.selection.query===s.query&&String(window.oswMovieView.selection.zoom??'all')===s.zoom&&(window.oswMovieView.selection.state_id??'all')===s.state_id",arg=wanted,timeout=90000)
            assert page.evaluate('window.oswMovieView')==view
            assert [r.get_attribute('id') for r in page.locator('#movie-rows tr').all()]==['movie-'+r['tile']['tile_id'] for r in view['rows']]
        sample=next(r for r in views[0]['rows'] if r['objects'])
        page.locator('#movie-query').fill(sample['tile']['tile_id'])
        expect(page.locator('#movie-rows tr')).to_have_count(1)
        row=page.locator('#movie-rows tr');assert row.get_by_role('link',name='Watch at NASA').get_attribute('href')==sample['tile']['url']
        for detail in row.locator('details').all():detail.locator('summary').click()
        assert 'display overlaps' in row.inner_text() and 'geographic links' in row.inner_text()
        assert 'rights-screened review export' in page.locator('.footnote').first.inner_text()
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        failed=browser.new_page();failed.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'));failed.goto(BASE)
        expect(failed.locator('#movie-error')).to_contain_text('HTTP 503',timeout=90000)
        assert failed.locator('#movie-query').is_disabled() and failed.locator('#movie-rows tr').count()==0
        missing=browser.new_page();partial=copy.deepcopy(bundle);del partial['manifest']['movies_receipts'];route_atlas_bundle(missing,partial);missing.goto(BASE)
        expect(missing.locator('#movie-error')).to_contain_text('Missing screened movie receipts',timeout=90000)
        assert missing.locator('#movie-state').is_disabled() and missing.locator('#movie-rows tr').count()==0
        assert not direct and not errors,(direct,errors);browser.close()
    print('PASS: exact screened movie rows/joins, nine independent selections, native/WASM UI parity, five query and five source rejections, no release fetches, mobile and unavailable data')


if __name__=='__main__':main()
