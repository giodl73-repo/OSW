"""Actual cloud browser evidence for route/query/atlas/seasons/dashboard integration."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import wicc_winter_reference_query_v1 as query
import wicc_winter_reference_runtime_v1 as runtime


def browser_review(root,output):
    if (os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_WICC_REFERENCE_DELIVERY_V1')!='1'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact scoped cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    contract=runtime.build_contract();route=contract['query_contract']['route']
    old=json.loads(json.loads((output/'parent-dashboard.json').read_bytes())['snapshot_json'])
    baseline={r['id']:{'fingerprint':r['fingerprint'],'sections':r['section_fingerprints']} for r in old['entries']}
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors,missing,originals,images,checks=[],[],[],[],[]
    def capture(locator,name):
        locator.scroll_into_view_if_needed();geometry=locator.evaluate(CAPTURE_GEOMETRY)
        try:verify_capture_geometry(geometry)
        except ValueError:
            (output/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n');raise
        path=output/name;locator.screenshot(path=str(path))
        images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):raise ValueError('Page-level horizontal overflow')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.add_init_script('if(location.pathname.endsWith("/dashboard.html"))localStorage.setItem("osw-motion-dashboard-seen-v2",'+json.dumps(json.dumps(baseline))+');')
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda response:missing.append({'url':response.url,'status':response.status}) if response.url.startswith(base) and response.status>=400 and not response.url.endswith('/favicon.ico') else None)
            page.on('request',lambda req:originals.append(req.url) if req.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            for width in [1100,320]:
                page.set_viewport_size({'width':width,'height':950});suffix=str(width)+'px.png'
                page.goto(base+'/almanac/'+query.query_url())
                page.wait_for_function('window.oswLastQueryResult?.ok')
                result=page.evaluate('window.oswLastQueryResult')
                if result['total']!=1 or result['rows']!=[route] or result['map_scene']['mapped_objects']!=1:
                    raise ValueError('Exact route query and mapped geometry required')
                expect(page.locator('#query-detail')).to_contain_text(query.ROUTE)
                expect(page.locator('#query-map-features')).not_to_be_empty()
                no_overflow(page);capture(page.locator('#query-map'),'wicc-query-map-'+suffix)
                page.locator('#source-query-panel > summary').click()
                expect(page.locator('#source-query-fields')).to_be_enabled()
                page.locator('#source-query-document').select_option(query.CANDIDATE)
                page.locator('#source-query-pointer').fill('/coordinates_lon_lat/0')
                page.locator('#source-query-run').click()
                page.wait_for_function('(pin)=>window.oswSourceQueryResult?.ok&&window.oswSourceQueryResult.source_sha256===pin',arg=contract['input_sha256'][query.CANDIDATE])
                source=page.evaluate('window.oswSourceQueryResult')
                if source['source_sha256']!=contract['input_sha256'][query.CANDIDATE] or [r['record'] for r in source['rows']]!=[75.7,10]:
                    raise ValueError('Exact browser source-coordinate pointer differs')
                capture(page.locator('#source-query-results'),'wicc-source-'+suffix)
                page.goto(base+'/almanac/reference-routes.html#'+query.ROUTE)
                page.wait_for_function('window.oswAtlasSnapshot?.working_reference_routes?.candidates.length===83')
                card=page.locator('#'+query.ROUTE);expect(card).to_be_visible()
                page.wait_for_function('(id)=>{const r=document.getElementById(id)?.getBoundingClientRect();return r&&r.top>=-10&&r.top<innerHeight-80;}',arg=query.ROUTE)
                expect(card).to_contain_text('range unknown');expect(card).to_contain_text('published abstract')
                expect(card).to_contain_text('Whole-current endpoints, physical axis and annual range remain unresolved')
                expect(card.get_by_role('link',name='doi:10.1029/2008JC004874',exact=True)).to_have_attribute('href','https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008JC004874')
                expect(card).to_contain_text('Editorial map overlap only: IND W')
                expect(card).to_contain_text('Physical current passage through atlas regions remains unresolved.')
                image=card.locator('.route-map');page.wait_for_function('(el)=>el.complete&&el.naturalWidth>0',arg=image.element_handle())
                if width==320 and not image.evaluate('el=>el.currentSrc').endswith('wicc-winter-regional-reference-compact-v1.svg'):
                    raise ValueError('Narrow card did not use compact map')
                no_overflow(page);capture(card,'wicc-route-card-'+suffix)
                page.goto(base+'/almanac/'+query.atlas_url())
                page.wait_for_function('window.oswAtlasSnapshot?.working_reference_routes?.candidates.length===83')
                expect(page.locator('#route-atlas-select')).to_have_value(query.OWNER)
                panel=page.locator('#route-atlas-preview');expect(panel).to_be_visible()
                summary=panel.locator('p').filter(has_text='range unknown').first
                expect(summary).to_contain_text('1,500 km')
                capture(summary,'wicc-atlas-range-'+suffix)
                image=panel.locator('.route-map');expect(image).to_have_count(1)
                page.wait_for_function('(el)=>el.complete&&el.naturalWidth>0',arg=image.element_handle())
                if not image.evaluate('el=>el.currentSrc').endswith('wicc-winter-regional-reference-compact-v1.svg'):
                    raise ValueError('Atlas sidebar did not use compact map')
                capture(image,'wicc-atlas-map-'+suffix);no_overflow(page)
                page.goto(base+'/almanac/seasons.html?current=west-india-coastal')
                page.wait_for_function('window.oswSeasonSnapshot?.ok')
                expect(page.locator('#season-current')).to_have_value(query.CURRENT)
                expect(page.locator('#season-play')).to_be_disabled()
                expect(page.locator('#season-length')).to_contain_text('unknown')
                capture(page.locator('#season-length'),'wicc-seasons-length-'+suffix)
                panel=page.locator('.review-cited-widths');expect(panel).to_have_count(1)
                expect(panel).to_contain_text('150 km');capture(panel,'wicc-seasons-width-'+suffix)
                page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.ok')
                snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                prior_by_id={r['id']:r for r in old['entries']}
                for row in snapshot['entries']:
                    if row['id']==query.OWNER:
                        if row!=contract['dashboard_after']:raise ValueError('Exact dashboard route projection differs')
                    elif row!=prior_by_id[row['id']]:raise ValueError('Unrelated dashboard row changed')
                page.locator('#dashboard-card-view').click();page.locator('#dashboard-type').select_option('named_current')
                page.locator('#dashboard-metric').select_option('reference_route');page.locator('#dashboard-search').fill('West India')
                page.locator('#dashboard-changed').check()
                card=page.locator('#dashboard-grid article[data-id="'+query.OWNER+'"]')
                expect(card).to_have_count(1);expect(card).to_have_class(re.compile(r'\bupdated\b'))
                expect(card.locator('.selected-evidence')).to_contain_text('Editorial reference route: 1 record')
                capture(card,'wicc-dashboard-'+suffix);no_overflow(page)
                checks.append(f'Exact mapped query/source pointer; nullable-range card; responsive atlas sidebar; static width/seasonal preservation; WICC-only dashboard update at{width}px')
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors, missing assets or original downloads: '+str([errors,missing,originals])[:4000])
        if len(images)!=16:raise ValueError('Sixteen actual screenshots required')
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'visual_review_complete':False}
    finally:server.shutdown();server.server_close()
