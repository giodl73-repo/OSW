"""Cloud-only exact historical/datetime separation, source links and update indicators."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import azcc_onken_query_v1 as query


def browser_review(root,output):
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
        or os.environ.get('OSW_AZCC_ONKEN_DELIVERY_V1')!='1'
        or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact scoped cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    contract=query.build_contract();width_record=contract['width_record'];prior_width=contract['prior_records']['widths'][0]
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
        if geometry['clipped_axes']:(output/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n')
        verify_capture_geometry(geometry);path=output/name;locator.screenshot(path=str(path))
        images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Page-level horizontal overflow')
    def check_panel(panel,widths=2):
        expect(panel.locator('article[data-dimension-width-id]')).to_have_count(widths)
        expect(panel.locator('li[data-flow-event-id]')).to_have_count(0)
        expect(panel).to_contain_text('They do not form a seasonal range')
        expect(panel).to_contain_text('Seasonal width range: Unknown. Numerical uncertainty: Unknown.')
        expect(panel.get_by_role('link',name='Original historical study')).to_have_attribute('href',contract['new_source']['url'])
    def query_page(page,request):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok')
        return page.evaluate('window.oswLastQueryResult')
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
                    request={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':query.CURRENT}],'limit':100}
                    result=query_page(page,request)
                    if result['total']!=2 or result['rows']!=[prior_width,width_record]:raise ValueError('Exact separate historical and2009 widths required')
                    panel=page.locator('#query-chart-panels .current-dimension-evidence');check_panel(panel)
                    expect(panel).to_contain_text('About 110 km');expect(panel).to_contain_text('About 200 km')
                    for card in panel.locator('article[data-dimension-width-id]').all():expect(card).to_contain_text('Width scale: 0\u2013200 km')
                    capture(panel,'azcc-width-comparison-'+suffix);no_overflow(page)
                    result=query_page(page,{'collection':'widths','filters':[{'field':'id','op':'eq','value':query.WIDTH_ID}],'limit':1})
                    if result['rows']!=[width_record] or result['map_scene'] is not None:raise ValueError('Historical width filtering/geometry differs')
                    panel=page.locator('#query-chart-panels .current-dimension-evidence');check_panel(panel,1)
                    expect(panel.locator('article')).not_to_contain_text('About 110 km');capture(panel,'azcc-width-filtered-'+suffix)
                    panel.get_by_role('button',name='Inspect width record').click()
                    expect(page.locator('#query-detail')).to_contain_text(query.WIDTH_ID)
                    capture(page.locator('#query-detail'),'azcc-width-inspect-'+suffix)
                    panel.get_by_role('link',name='Source evidence record',exact=True).click();page.wait_for_function('window.oswSourceQueryResult?.ok')
                    response=page.evaluate('window.oswSourceQueryResult');original=json.loads((root/query.FACTS).read_bytes())['cited_width_summary']
                    if response['source_sha256']!=query.sha(query.FACTS) or {r['source_key']:r['record'] for r in response['rows']}!=original:raise ValueError('Exact cited-width source pointer differs')
                    capture(page.locator('#source-query-results'),'azcc-width-source-'+suffix);no_overflow(page)
                    result=query_page(page,{'collection':'widths','filters':[{'field':'id','op':'eq','value':prior_width['id']}],'limit':1})
                    if result['rows']!=[prior_width]:raise ValueError('Existing2009 dated section changed')
                    preserved=page.locator('#query-chart-panels .azores-section-review section[data-width-id="'+prior_width['id']+'"]')
                    expect(preserved).to_have_count(1);capture(preserved,'azcc-preserved-section-query-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(query.OWNER)+'#route-atlas')
                    page.wait_for_function('window.oswAtlasSnapshot?.current_dimension_evidence_scenes?.["azores-countercurrent"]')
                    expect(page.locator('#route-atlas-select')).to_have_value(query.OWNER)
                    details=page.locator('#route-atlas-preview details.current-dimension-evidence')
                    expect(details).not_to_have_attribute('open','');details.locator('summary').click();check_panel(details)
                    card=details.locator('article').last
                    capture(card.locator('h4'),'azcc-atlas-heading-'+suffix)
                    capture(card.locator('svg'),'azcc-atlas-width-chart-'+suffix)
                    capture(card.get_by_role('link',name='Source evidence record',exact=True),'azcc-atlas-source-link-'+suffix);no_overflow(page)
                    page.goto(base+'/almanac/seasons.html?current='+query.CURRENT+'&phase='+prior_width['id']);page.wait_for_function('window.oswSeasonSnapshot?.ok')
                    expect(page.locator('#season-current')).to_have_value(query.CURRENT)
                    panel=page.locator('#published-section-transports .current-dimension-evidence');check_panel(panel)
                    capture(panel.locator('article').last,'azcc-seasons-context-'+suffix);no_overflow(page)
                    preserved=page.locator('#regional-width-range .azores-section-review section[data-width-id="'+prior_width['id']+'"]')
                    expect(preserved).to_have_count(1);expect(page.locator('#season-play')).to_be_disabled()
                    capture(preserved,'azcc-preserved-season-section-'+suffix)
                    page.goto(base+'/almanac/dashboard.html')
                    page.wait_for_function('window.oswDashboardSnapshot?.ok || document.getElementById("dashboard-status")?.textContent.includes("Update check failed")')
                    if not page.evaluate('Boolean(window.oswDashboardSnapshot?.ok)'):raise ValueError('Dashboard failed: '+page.locator('#dashboard-status').inner_text())
                    previous={r['id']:r for r in old['entries']};snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                    for row in snapshot['entries']:
                        if row!=(contract['dashboard_after'] if row['id']==query.OWNER else previous[row['id']]):raise ValueError('Unexpected dashboard row change')
                    page.locator('#dashboard-card-view').click();page.locator('#dashboard-type').select_option('named_current')
                    page.locator('#dashboard-metric').select_option('scoped_width');page.locator('#dashboard-search').fill('Azores Countercurrent');page.locator('#dashboard-changed').check()
                    card=page.locator('#dashboard-grid article[data-id="'+query.OWNER+'"]')
                    expect(card).to_have_count(1);expect(card).to_have_class(re.compile(r'\bupdated\b'))
                    expect(card.locator('.selected-evidence')).to_contain_text('2 records')
                    capture(card,'azcc-dashboard-'+suffix);no_overflow(page)
                    checks.append({'width':width,'two_distinct_widths':True,'filtered_historical_width':True,'source_pointer_verified':True,
                        'dated_section_preserved':True,'no_seasonal_playback':True,'dashboard_only_target_changed':True,'no_horizontal_overflow':True})
                except Exception as error:
                    failure={'status':'FAIL','width':width,'url':page.url,'error':str(error),'page_errors':errors,'missing_assets':missing,'completed_captures':images}
                    try:failure['status_text']=page.locator('body').inner_text()[:4000];page.screenshot(path=str(output/('azcc-failure-'+str(width)+'px.png')))
                    except Exception:pass
                    (output/'browser-observation-failure.json').write_text(json.dumps(failure,indent=2)+'\n');raise
            browser.close()
        if errors or missing or originals:raise ValueError('Page errors, missing assets or original downloads: '+json.dumps([errors,missing,originals]))
        return {'status':'PASS','checks':checks,'captures':images,'actual_screenshots':len(images),'page_errors':errors,
            'missing_assets':missing,'original_downloads':originals,'visual_review_complete':False,'installed':False}
    finally:server.shutdown();server.server_close()
