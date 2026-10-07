"""Scoped object evidence, canonical imports, real WASM pages and outage behavior."""
import json,os,subprocess
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import ROOT,CLI


def native(ident):
    return json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--object-view',ident],encoding='utf-8'))


def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes());c=bundle['collections']
    assert len(bundle['manifest']['canonical_collections'])==20
    assert set(c)==set(bundle['manifest']['canonical_collections'])|set(bundle['manifest']['editorial_collections'])
    for name in bundle['manifest']['canonical_collections']:
        assert c[name]==json.loads((ROOT/'almanac/release/v0.1.0'/f'{name}.json').read_bytes()),name
    detection=next(r['id'] for r in c['entities'] if r['type']=='operational_eddy_detection')
    vocabulary=c['classification_vocabularies'][0]['entity_id']
    detections=[r['id'] for r in c['entities'] if r['type']=='operational_eddy_detection']
    ids=list(dict.fromkeys(['current:acc','current:gulf-stream-system','eddy:published:kraken-2013',*detections,'state:CAMR',vocabulary]))
    expected={ident:native(ident) for ident in ids}
    for ident,view in expected.items():
        assert view['ok'] and view['id']==ident
        data=view['collections'];assert set(data)==set(bundle['manifest']['canonical_collections'])
        for name,rows in data.items():
            original={r['id']:r for r in c[name]}
            assert all(r['id'] in original for r in rows),name
            # No evidence row is replaced by a generated scientific record.
            assert [r['id'] for r in rows]==[r['id'] for r in c[name] if r['id'] in {r['id'] for r in rows}],name
        assert [r['id'] for r in data['names']]==[r['id'] for r in c['names'] if r['entity_id']==ident]
        assert [r['id'] for r in data['relations']]==[r['id'] for r in c['relations'] if ident in [r['subject_id'],r['object_id']]]
        assert data['length_assessments']==c['length_assessments']
        assert set(view['footprint_plots'])=={r['id'] for r in data['named_eddy_footprint_candidates']}
        for candidate in data['named_eddy_footprint_candidates']:
            plot=view['footprint_plots'][candidate['id']]
            geometry=next(g for g in c['geometries'] if g['id']==candidate['geometry_id'])
            check_source_plot(plot,geometry,[0,0,500,350])
            assert plot['center_d'] is None and 'candidate' in plot['aria_label']
        if ident in detections:
            geometry=next(g for g in c['geometries'] if g['entity_id']==ident and g['role']=='dated_operational_eddy_polygon')
            check_source_plot(view['detection_plot'],geometry,[0,0,600,350])
            assert view['detection_plot']['center_d']
        else: assert view['detection_plot'] is None
        assert {r['id'] for r in data['named_eddy_state_assessments']}=={r['id'] for r in c['named_eddy_state_assessments'] if ident in [r['eddy_id'],r['state_id']]}
        if ident==detection:
            states={r['state_id'] for r in c['operational_eddy_state_observations'] if r['operational_eddy_id']==ident}
            tile_relations=[r for r in c['tile_state_relations'] if r['state_id'] in states]
            assert data['tile_state_relations']==tile_relations
            assert {r['id'] for r in data['tiles']}=={r['id'] for r in c['tiles'] if r['tile_id'] in {t['tile_id'] for t in tile_relations}}
            claims={r['claim_id'] for r in tile_relations}|{r['claim_id'] for r in c['operational_eddy_state_observations'] if r['operational_eddy_id']==ident}
            assert claims.issubset({r['id'] for r in data['claims']})
    unknown=subprocess.run([str(CLI),str(ROOT/'almanac/query-data.json'),'--object-view','missing'],capture_output=True,text=True)
    assert unknown.returncode==2 and not unknown.stdout and 'Object not found' in unknown.stderr
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1100,'height':1000});errors=[];direct=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:direct.append(r.url) if '/release/' in r.url and r.url.endswith('.json') else None)
        page.route('**/release/**/*.json',lambda r:r.fulfill(status=503,body='Direct release loading disabled'))
        by_id={r['id']:r for r in c['entities']}
        base='http://127.0.0.1:8788/almanac/object.html?id='
        for ident in ids:
            page.goto(base+ident)
            expect(page.locator('#object-title')).to_have_text(by_id[ident]['label'],timeout=90000)
            assert page.evaluate('window.oswObjectView')==expected[ident]
            assert page.locator('#object-options option').count()==318
            assert page.locator('#object-summary').get_attribute('data-engine')=='rust-osw-query-v1'
            if ident==detection:
                with page.expect_download() as packet:
                    page.get_by_role('link',name="Download this detection's evidence packet").click()
                saved=json.loads(__import__('pathlib').Path(packet.value.path()).read_bytes())
                assert saved['entity']['id']==ident and saved['geometries'] and saved['sources']
                assert saved['regional_movie_context']['tiles']
            if expected[ident]['footprint_plots']:
                assert page.locator('#footprint-section').is_visible()
                plots=list(expected[ident]['footprint_plots'].values())
                for i,plot in enumerate(plots):
                    svg=page.locator('#footprints svg').nth(i)
                    check_painted_plot(svg,plot,34.99,34.99,465.01,290.01)
                    assert svg.get_attribute('data-engine')=='rust-osw-query-v1'
                expect(page.locator('#footprints')).to_contain_text('Containment unresolved')
                expect(page.locator('#footprints')).to_contain_text('Scientific claim review: pending')
            if ident in detections:
                plot=expected[ident]['detection_plot'];svg=page.locator('.detection-footprint')
                check_painted_plot(svg,plot,59.99,39.99,540.01,290.01)
                assert svg.locator(':scope > path').get_attribute('d')==plot['center_d']
            page.set_viewport_size({'width':320,'height':850})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),ident
            page.set_viewport_size({'width':1100,'height':1000})
        assert not direct,direct
        assert not errors,errors
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        failed=browser.new_page();failed.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'))
        failed.goto(base+'current:acc');expect(failed.locator('#object-summary')).to_contain_text('Release data unavailable',timeout=90000)
        assert failed.locator('#object-options option').count()==0
        browser.close()
    print(f'PASS: 20 exact canonical imports, {len(c)} declared collections, nine native/WASM object cases, source-bound named contour and four detection plots, packet, no direct JSON reads, mobile and unavailable first load')


def check_source_plot(plot,geometry,frame):
    points=[p for ring in geometry['geometry']['coordinates'] for p in ring]
    bounds=[min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]
    assert plot['available'] and plot['view_box']==frame
    assert all(abs(a-b)<1e-9 for a,b in zip(bounds,plot['geographic_bounds']))
    assert plot['observation_date']==geometry['observation_date']
    assert plot['polygon_d'].count('M')==len(geometry['geometry']['coordinates'])
    assert not plot['omitted_features']


def check_painted_plot(svg,plot,left,top,right,bottom):
    assert svg.locator('g path').get_attribute('d')==plot['polygon_d']
    assert svg.get_attribute('aria-label')==plot['aria_label']
    box=svg.locator('g').evaluate('''g=>{const b=g.getBBox(),m=g.transform.baseVal.consolidate().matrix;return {x:m.a*b.x+m.e,y:m.d*b.y+m.f,width:m.a*b.width,height:m.d*b.height}}''')
    assert box['x']>=left and box['y']>=top,box
    assert box['x']+box['width']<=right and box['y']+box['height']<=bottom,box


if __name__=='__main__':main()
