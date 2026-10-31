"""Actual cloud browser checks; no source-field downloads or local browser use."""
import functools
import hashlib
import http.server
import json
import os
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import published_current_speed_statistics_v1 as speeds


def browser_review(root,output):
    if (os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_SPEED_DELIVERY_V1')!='1'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'):
        raise ValueError('Exact cloud browser delivery required')
    from playwright.sync_api import sync_playwright,expect
    doc=json.loads((root/speeds.SOURCE).read_bytes());april=doc['monthly_records'][3]
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
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
        panel=page.locator('.published-current-speeds');panel.wait_for(state='visible',timeout=180000)
        expect(panel.locator('tbody tr')).to_have_count(count)
        expect(panel).to_contain_text('Neither SD nor observed extrema')
        page.wait_for_function("() => {const s=document.querySelector('.published-current-speeds svg');return s&&s.getBoundingClientRect().height>0;}")
        page.wait_for_function("() => {const t=document.querySelector('.published-current-speeds svg text');return t&&parseFloat(getComputedStyle(t).fontSize)*Math.abs(t.getScreenCTM().d)>=11.5;}")
        size=panel.locator('svg text').first.evaluate("el=>parseFloat(getComputedStyle(el).fontSize)*Math.abs(el.getScreenCTM().d)")
        if size<11.5:raise ValueError('Chart labels too small at current viewport: '+str(size))
        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):
            raise ValueError('Page horizontal overflow')
        return panel
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            monthly={'collection':speeds.COLLECTION,'filters':[{'field':'statistic_period','op':'eq','value':'monthly'}],'sort':{'field':'month','direction':'asc'},'limit':100}
            for width in [1100,320,390]:
                page.set_viewport_size({'width':width,'height':950})
                page.goto(base+'/almanac/query.html?q='+quote(json.dumps(monthly)))
                page.wait_for_function('window.oswLastQueryResult?.ok')
                response=page.evaluate('window.oswLastQueryResult')
                if response['total']!=12 or response['rows'][3]['id']!=april['id']:raise ValueError('Monthly browser query differs')
                panel=ready(page,12);capture(panel.locator('svg'),'speed-query-monthly-'+str(width)+'px.png')
                row=panel.locator('tbody tr').filter(has_text='Month 4')
                row.get_by_role('button',name='Inspect',exact=True).click()
                expect(page.locator('#query-detail')).to_contain_text(april['id'])
                row.get_by_role('link',name='Source table record',exact=True).click()
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                source=page.evaluate('window.oswSourceQueryResult')
                reconstructed={r['source_key']:r['record'] for r in source['rows']}
                if reconstructed!=april:raise ValueError('Actual source-table link differs from original April row')
                capture(page.locator('#source-query-results'),'speed-source-april-'+str(width)+'px.png')
                checks.append('query, exact inspection and indexed April source at'+str(width)+'px')
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(speeds.OWNER)+'#route-atlas')
                page.wait_for_function("window.oswAtlasSnapshot?.published_speed_scenes?.['east-african-coastal']?.records.length===15")
                expect(page.locator('#route-atlas-select')).to_have_value(speeds.OWNER)
                panel=ready(page,15);capture(panel.locator('svg'),'speed-atlas-'+str(width)+'px.png')
                panel.locator('tbody tr').filter(has_text='Month 4').get_by_role('button',name='Inspect',exact=True).click()
                page.wait_for_function('window.oswLastQueryResult?.ok')
                selected=page.evaluate('window.oswLastQueryResult')
                if selected['total']!=1 or selected['rows'][0]['id']!=april['id']:raise ValueError('Atlas-to-record navigation differs')
                ready(page,1)
                checks.append('atlas card to exact April query at'+str(width)+'px')
                page.goto(base+'/almanac/seasons.html?current=east-african-coastal')
                page.wait_for_function("window.oswSeasonSnapshot?.published_speed_scenes?.['east-african-coastal']?.records.length===15")
                expect(page.locator('#season-current')).to_have_value('east-african-coastal')
                panel=ready(page,15);capture(panel.locator('svg'),'speed-seasons-'+str(width)+'px.png')
                checks.append('regional speed summaries remain visible on seasons page at'+str(width)+'px')
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors/missing assets/original downloads: '+str([errors,missing,originals])[:3000])
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'visual_review_complete':False}
    finally:server.shutdown();server.server_close()
