"""Actual desktop/narrow EAC model-mean evidence and navigation checks, cloud only."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import eac_mean_core_query_v1 as query


def browser_review(root,output):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('OSW_EAC_MEAN_CORE_DELIVERY_V1')!='1'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact scoped cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    contract=query.build_contract();rows=contract['records'];first=rows[0]
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
        if geometry['clipped_axes']:
            (output/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n')
        verify_capture_geometry(geometry)
        path=output/name;locator.screenshot(path=str(path))
        images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):
            raise ValueError('Page-level horizontal overflow')
    def check_panel(panel,expected=5):
        expect(panel.locator('article[data-mean-core-id]')).to_have_count(expected)
        expect(panel).to_contain_text('not seasonal ranges')
        expect(panel).to_contain_text('numerical uncertainty are unknown')
        expect(panel).to_contain_text('Forster')
        expect(panel.get_by_role('link',name='Original study')).to_have_attribute('href',contract['new_source']['url'])
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
                if result['total']!=5 or result['rows']!=rows or result['map_scene'] is not None:
                    raise ValueError('Exact five source-defined EAC rows required')
                panel=page.locator('#query-chart-panels .mean-core-sections');check_panel(panel)
                no_overflow(page);capture(panel.locator('article').first,'eac-mean-core-query-'+suffix)
                panel.get_by_role('button',name='Inspect section record').first.click()
                expect(page.locator('#query-detail')).to_contain_text(first['id'])
                expect(page.locator('#query-detail')).to_contain_text('source reported model mean core geometry')
                capture(page.locator('#query-detail'),'eac-mean-core-inspect-'+suffix)
                selected={'collection':query.COLLECTION,'filters':[{'field':'place','op':'eq','value':'Forster'}],'limit':1}
                page.goto(base+'/almanac/query.html?q='+quote(json.dumps(selected)))
                page.wait_for_function('window.oswLastQueryResult?.ok')
                result=page.evaluate('window.oswLastQueryResult')
                if result['total']!=1 or result['rows']!=[rows[2]]:raise ValueError('Filtered EAC section differs')
                panel=page.locator('#query-chart-panels .mean-core-sections');check_panel(panel,1)
                capture(panel,'eac-mean-core-filtered-'+suffix);no_overflow(page)
                panel.get_by_role('link',name='Source table record',exact=True).click()
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                source=page.evaluate('window.oswSourceQueryResult')
                original=json.loads((root/query.facts.FACTS).read_bytes())['records'][2]
                if (source['source_sha256']!=query.sha(query.facts.FACTS)
                    or {r['source_key']:r['record'] for r in source['rows']}!=original):
                    raise ValueError('Exact source-table navigation differs')
                capture(page.locator('#source-query-results'),'eac-mean-core-source-'+suffix)
                route='east-australian-reference-path-candidate'
                page.goto(base+'/almanac/reference-routes.html#'+route)
                page.wait_for_function('window.oswAtlasSnapshot?.working_reference_routes?.candidates.length===83')
                card=page.locator('#'+route)
                expect(card.locator('.route-map')).to_have_count(1)
                details=card.locator('details.mean-core-sections');expect(details).not_to_have_attribute('open','')
                details.locator('summary').click();check_panel(details)
                capture(details.locator('article').first,'eac-mean-core-route-card-'+suffix);no_overflow(page)
                page.goto(base+'/almanac/reference-routes.html?atlas-feature='+quote(query.OWNER)+'#route-atlas')
                page.wait_for_function('window.oswAtlasSnapshot?.mean_core_section_scenes?.["east-australian"]')
                expect(page.locator('#route-atlas-select')).to_have_value(query.OWNER)
                panel=page.locator('#route-atlas-preview')
                expect(panel.locator('.eac-source-fields')).to_have_count(1)
                expect(panel.locator('.atlas-width-evidence')).to_have_count(1)
                details=panel.locator('details.mean-core-sections');details.locator('summary').click();check_panel(details)
                capture(details.locator('article').first,'eac-mean-core-atlas-'+suffix);no_overflow(page)
                page.goto(base+'/almanac/seasons.html?current=east-australian')
                page.wait_for_function('window.oswSeasonSnapshot?.ok')
                expect(page.locator('#season-current')).to_have_value(query.CURRENT)
                panel=page.locator('#published-section-transports .mean-core-sections');check_panel(panel)
                capture(panel.locator('article').first,'eac-mean-core-seasons-'+suffix);no_overflow(page)
                page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.ok')
                snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                previous={r['id']:r for r in old['entries']}
                for row in snapshot['entries']:
                    if row!= (contract['dashboard_after'] if row['id']==query.OWNER else previous[row['id']]):
                        raise ValueError('Unexpected dashboard current change')
                page.locator('#dashboard-card-view').click();page.locator('#dashboard-type').select_option('named_current')
                page.locator('#dashboard-metric').select_option('reported_model_core_sections')
                page.locator('#dashboard-search').fill('East Australian');page.locator('#dashboard-changed').check()
                card=page.locator('#dashboard-grid article[data-id="'+query.OWNER+'"]')
                expect(card).to_have_count(1);expect(card).to_have_class(re.compile(r'\bupdated\b'))
                expect(card.locator('.selected-evidence')).to_contain_text('5 records')
                expect(card.locator('a[href*="current_mean_core_sections"]').first).to_be_visible()
                capture(card,'eac-mean-core-dashboard-'+suffix);no_overflow(page)
                checks.append({'width':width,'five_exact_records':True,'filtered_record':rows[2]['id'],
                    'inspect_source_navigation':True,'route_width_daily_diagnostic_panels_preserved':True,
                    'only_eac_dashboard_changed':True,'no_seasonal_dimensions_inferred':True})
            for figure in ['figures/eac-kerry-2020-mean-core-dimensions-v2.svg','figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg']:
                response=page.request.get(base+'/'+figure)
                if response.status!=200 or hashlib.sha256(response.body()).hexdigest()!=query.sha(figure):
                    raise ValueError('Context chart asset differs')
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors/missing assets/original downloads: '+str([errors,missing,originals])[:4000])
        if len(images)!=16:raise ValueError('Sixteen actual captures required')
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,
            'original_science_downloads':originals,'visual_review_complete':False}
    finally:server.shutdown();server.server_close()
