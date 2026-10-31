"""Cloud-only actual width/event/source/atlas/dashboard checks at two viewports."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import madagascar_dimensions_query_v1 as query

def browser_review(root,output):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('OSW_MADAGASCAR_DIMENSIONS_DELIVERY_V5')!='1'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact scoped cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    contract=query.build_contract();rows=contract['event_records'];width_record=contract['width_record']
    selected=rows[2];old=json.loads(json.loads((output/'parent-dashboard.json').read_bytes())['snapshot_json'])
    baseline={r['id']:{'fingerprint':r['fingerprint'],'sections':r['section_fingerprints']} for r in old['entries']}
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors,missing,originals,images,checks=[],[],[],[],[]
    def capture(locator,name):
        locator.scroll_into_view_if_needed();geometry=locator.evaluate(CAPTURE_GEOMETRY)
        if geometry['clipped_axes']:(output/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n')
        verify_capture_geometry(geometry);path=output/name;locator.screenshot(path=str(path))
        images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Page-level horizontal overflow')
    def check_panel(panel,widths=2,events=8):
        expect(panel.locator('article[data-dimension-width-id]')).to_have_count(widths)
        expect(panel.locator('li[data-flow-event-id]')).to_have_count(events)
        expect(panel).to_contain_text('not an annual min/max')
        if widths:expect(panel).to_contain_text('Seasonal width range: Unknown. Numerical uncertainty: Unknown.')
        expect(panel.get_by_role('link',name='Original mooring study')).to_have_attribute('href',contract['new_source']['url'])
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.add_init_script('if(location.pathname.endsWith("/dashboard.html"))localStorage.setItem("osw-motion-dashboard-seen-v2",'+json.dumps(json.dumps(baseline))+');')
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda response:missing.append({'url':response.url,'status':response.status}) if response.url.startswith(base) and response.status>=400 and not response.url.endswith('/favicon.ico') else None)
            page.on('request',lambda request:originals.append(request.url) if request.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            for width in [1100,320]:
                try:
                    page.set_viewport_size({'width':width,'height':950});suffix=str(width)+'px.png'
                    page.goto(base+'/almanac/'+query.query_url('widths'));page.wait_for_function('window.oswLastQueryResult?.ok')
                    result=page.evaluate('window.oswLastQueryResult')
                    if result['total']!=2 or result['rows']!=contract['prior_records']['widths']+[width_record]:raise ValueError('Exact two distinct study widths required')
                    panel=page.locator('#query-chart-panels .current-dimension-evidence');check_panel(panel,2,0)
                    expect(panel).to_contain_text('About 60\u2013100 km');expect(panel).to_contain_text('About 120 km')
                    card=panel.locator('article[data-dimension-width-id="'+width_record['id']+'"]')
                    capture(card,'madagascar-width-query-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/'+query.query_url(query.COLLECTION));page.wait_for_function('window.oswLastQueryResult?.ok')
                    result=page.evaluate('window.oswLastQueryResult')
                    if result['total']!=8 or result['rows']!=rows or result['map_scene'] is not None:raise ValueError('Exact eight chronological source events required')
                    panel=page.locator('#query-chart-panels .current-dimension-evidence');check_panel(panel,0,8)
                    capture(panel.locator('ol'),'madagascar-flow-events-'+suffix);no_overflow(page)
                    filtered={'collection':query.COLLECTION,'filters':[{'field':'date','op':'eq','value':selected['date']}],'limit':1}
                    page.goto(base+'/almanac/query.html?q='+quote(json.dumps(filtered)));page.wait_for_function('window.oswLastQueryResult?.ok')
                    result=page.evaluate('window.oswLastQueryResult')
                    if result['total']!=1 or result['rows']!=[selected]:raise ValueError('Filtered event differs')
                    panel=page.locator('#query-chart-panels .current-dimension-evidence');check_panel(panel,0,1)
                    capture(panel,'madagascar-flow-filtered-'+suffix)
                    panel.get_by_role('button',name='Inspect dated event').click()
                    expect(page.locator('#query-detail')).to_contain_text(selected['id'])
                    capture(page.locator('#query-detail'),'madagascar-flow-inspect-'+suffix)
                    panel.get_by_role('link',name='Source evidence record',exact=True).click();page.wait_for_function('window.oswSourceQueryResult?.ok')
                    response=page.evaluate('window.oswSourceQueryResult');original=json.loads((root/query.source.FACTS).read_bytes())['event_index'][2]
                    if response['source_sha256']!=query.sha(query.source.FACTS) or {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('Exact event source pointer differs')
                    capture(page.locator('#source-query-results'),'madagascar-flow-source-'+suffix);no_overflow(page)
                    route=contract['prior_records']['reference_routes'][0]['id']
                    page.goto(base+'/almanac/reference-routes.html#'+route)
                    page.wait_for_function('window.oswAtlasSnapshot?.working_reference_routes?.candidates.length===83')
                    card=page.locator('#'+route);expect(card.locator('.route-map')).to_have_count(1)
                    details=card.locator('details.current-dimension-evidence');expect(details).not_to_have_attribute('open','')
                    details.locator('summary').click();check_panel(details)
                    capture(details.locator('article').last,'madagascar-route-card-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/reference-routes.html?atlas-feature='+quote(query.OWNER)+'#route-atlas')
                    page.wait_for_function('window.oswAtlasSnapshot?.current_dimension_evidence_scenes?.["southern-east-madagascar"]')
                    expect(page.locator('#route-atlas-select')).to_have_value(query.OWNER)
                    details=page.locator('#route-atlas-preview details.current-dimension-evidence');details.locator('summary').click();check_panel(details)
                    capture(details.locator('article').last,'madagascar-atlas-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/seasons.html?current='+query.CURRENT);page.wait_for_function('window.oswSeasonSnapshot?.ok')
                    expect(page.locator('#season-current')).to_have_value(query.CURRENT)
                    panel=page.locator('#published-section-transports .current-dimension-evidence');check_panel(panel)
                    capture(panel.locator('article').last,'madagascar-seasons-context-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/dashboard.html')
                    page.wait_for_function('window.oswDashboardSnapshot?.ok || document.getElementById("dashboard-status")?.textContent.includes("Update check failed")')
                    if not page.evaluate('Boolean(window.oswDashboardSnapshot?.ok)'):raise ValueError('Dashboard failed: '+page.locator('#dashboard-status').inner_text())
                    previous={r['id']:r for r in old['entries']};snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                    for row in snapshot['entries']:
                        if row!=(contract['dashboard_after'] if row['id']==query.OWNER else previous[row['id']]):raise ValueError('Unexpected dashboard row change')
                    page.locator('#dashboard-card-view').click();page.locator('#dashboard-type').select_option('named_current')
                    page.locator('#dashboard-metric').select_option('reported_flow_events');page.locator('#dashboard-search').fill('Southern East Madagascar');page.locator('#dashboard-changed').check()
                    card=page.locator('#dashboard-grid article[data-id="'+query.OWNER+'"]')
                    expect(card).to_have_count(1);expect(card).to_have_class(re.compile(r'\bupdated\b'))
                    expect(card.locator('.selected-evidence')).to_contain_text('8 records')
                    expect(card.locator('a[href*="current_reported_flow_events"]').first).to_be_visible()
                    capture(card,'madagascar-dashboard-'+suffix);no_overflow(page)
                    checks.append({'width':width,'two_study_widths':True,'eight_events':True,'filtered_event':selected['id'],
                        'source_pointer_verified':True,'dashboard_only_target_changed':True,'no_horizontal_overflow':True})
                except Exception as error:
                    failure={'status':'FAIL','width':width,'url':page.url,'error':str(error),'page_errors':errors,'missing_assets':missing}
                    try:
                        failure['status_text']=page.locator('body').inner_text()[:4000];page.screenshot(path=str(output/('madagascar-failure-'+str(width)+'px.png')))
                    except Exception:pass
                    (output/'browser-failure.json').write_text(json.dumps(failure,indent=2)+'\n');raise
            browser.close()
        if errors or missing or originals:raise ValueError('Page errors, missing assets or original downloads: '+json.dumps([errors,missing,originals]))
        return {'status':'PASS','checks':checks,'captures':images,'actual_screenshots':len(images),'page_errors':errors,
            'missing_assets':missing,'original_downloads':originals,'visual_review_complete':False,'installed':False}
    finally:server.shutdown();server.server_close()
