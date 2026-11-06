"""One cloud browser, sequential desktop/narrow views; no original data fetches."""
import functools
import hashlib
import http.server
import json
import os
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY, verify_capture_geometry
import published_seasonal_core_velocities_v1 as core


def browser_review(root, output):
    if (os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_CORE_VELOCITY_DELIVERY_V1')!='1'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact cloud browser required')
    from playwright.sync_api import sync_playwright, expect
    source=json.loads((root/core.SOURCE).read_bytes());rows=source['records'];threshold=rows[5]
    owners=list(dict.fromkeys(r['current_id'] for r in rows))
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors,missing,originals,images,checks=[],[],[],[],[]
    def capture(locator,name):
        locator.scroll_into_view_if_needed();geometry=locator.evaluate(CAPTURE_GEOMETRY)
        verify_capture_geometry(geometry)
        path=output/name;locator.screenshot(path=str(path))
        images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def ready(page,count):
        panel=page.locator('.published-seasonal-core-velocities');panel.wait_for(state='visible',timeout=180000)
        expect(panel.locator('tbody tr')).to_have_count(count)
        expect(panel).to_contain_text('not error bars or confidence intervals')
        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'): raise ValueError('Page overflow')
        for node in panel.locator('tbody tr td:nth-child(3) span').all():
            if node.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')<12: raise ValueError('Estimate text too small')
        return panel
    def query(page,request):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok')
        return page.evaluate('window.oswLastQueryResult')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            for width in [1100,320]:
                page.set_viewport_size({'width':width,'height':950})
                result=query(page,{'collection':core.COLLECTION,'limit':100})
                if result['total']!=6: raise ValueError('All-row query differs')
                panel=ready(page,6)
                capture(panel.locator('[role="region"]'),'core-query-'+str(width)+'px.png')
                selected=panel.locator('tbody tr').nth(5)
                selected.get_by_role('button',name='Inspect',exact=True).click()
                expect(page.locator('#query-detail')).to_contain_text(threshold['id'])
                selected.get_by_role('link',name='Source record',exact=True).click()
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                result=page.evaluate('window.oswSourceQueryResult')
                if {r['source_key']:r['record'] for r in result['rows']}!=threshold: raise ValueError('Exact browser source pointer differs')
                capture(page.locator('#source-query-results'),'core-source-threshold-'+str(width)+'px.png')
                result=query(page,{'collection':core.COLLECTION,'filters':[{'field':'id','op':'eq','value':threshold['id']}]})
                if result['total']!=1 or result['rows'][0]['value_m_s'] is not None or result['rows'][0]['interval_m_s'] is not None: raise ValueError('Open threshold promoted to finite value')
                panel=ready(page,1);expect(panel).to_contain_text('greater than 0.30 m/s')
                capture(panel.locator('[role="region"]'),'core-filtered-threshold-'+str(width)+'px.png')
                for owner in owners:
                    page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote('current:'+owner)+'#route-atlas')
                    page.wait_for_function('(id)=>window.oswAtlasSnapshot?.published_speed_scenes?.[id]?.records.length===2',arg=owner)
                    expect(page.locator('#route-atlas-select')).to_have_value('current:'+owner)
                    panel=ready(page,2)
                    capture(panel.locator('[role="region"]'),'core-atlas-'+owner+'-'+str(width)+'px.png')
                    panel.locator('tbody tr').first.get_by_role('button',name='Inspect',exact=True).click()
                    page.wait_for_function('window.oswLastQueryResult?.ok')
                    result=page.evaluate('window.oswLastQueryResult')
                    if result['total']!=1 or result['rows'][0]['current_id']!=owner: raise ValueError('Atlas owner-to-query navigation differs')
                    ready(page,1)
                    page.goto(base+'/almanac/seasons.html?current='+quote(owner))
                    page.wait_for_function('(id)=>window.oswSeasonSnapshot?.published_speed_scenes?.[id]?.records.length===2',arg=owner)
                    expect(page.locator('#season-current')).to_have_value(owner)
                    panel=ready(page,2)
                    capture(panel.locator('[role="region"]'),'core-seasons-'+owner+'-'+str(width)+'px.png')
                    checks.append(owner+': atlas, exact query inspection and seasons at'+str(width)+'px')
                checks.append('six-row query, exact source and filtered threshold at'+str(width)+'px')
            browser.close()
        if errors or missing or originals: raise ValueError('Browser errors/missing assets/original fetches: '+str([errors,missing,originals])[:3000])
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'visual_review_complete':False}
    finally:
        server.shutdown();server.server_close()
