"""One sequential cloud browser; capture visible cards and exact source links."""
import functools
import hashlib
import http.server
import json
import os
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import published_satellite_core_widths_v1 as core


def browser_review(root,output):
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_SATELLITE_CORE_WIDTH_DELIVERY_V1')!='1' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps':raise ValueError('Exact cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    rows=core.records();ids=[r['id'] for r in rows];original=json.loads((root/core.SOURCE).read_bytes())
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
    errors,missing,originals,images,checks=[],[],[],[],[]
    def capture(locator,name):
        locator.scroll_into_view_if_needed();geometry=locator.evaluate(CAPTURE_GEOMETRY)
        try:verify_capture_geometry(geometry)
        except ValueError:
            (output/(name+'.geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n');locator.page.screenshot(path=str(output/('debug-'+name)));raise
        path=output/name;locator.screenshot(path=str(path));images.append({'path':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':geometry})
    def ready(page,wanted):
        panel=page.locator('.satellite-core-widths');expect(panel).to_have_count(1);panel.wait_for(state='visible',timeout=180000)
        expect(panel.locator('[data-satellite-width-id]')).to_have_count(len(wanted))
        actual=panel.locator('[data-satellite-width-id]').evaluate_all('nodes=>nodes.map(n=>n.getAttribute("data-satellite-width-id"))')
        if actual!=wanted:raise ValueError('Wrong visible width identity or ordering')
        expect(panel).to_contain_text('not seasonal limits');expect(panel).to_contain_text('width is not assumed constant')
        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):raise ValueError('Page overflow')
        for element in panel.locator('strong').all():
            if element.evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')<12:raise ValueError('Mean text too small')
        return panel
    def card(panel,identity):return panel.locator('[data-satellite-width-id="'+identity+'"]')
    def query(page,request):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)));page.wait_for_function('window.oswLastQueryResult?.ok');return page.evaluate('window.oswLastQueryResult')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1']);page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            for width in [1100,320]:
                page.set_viewport_size({'width':width,'height':950});suffix=str(width)+'px.png'
                result=query(page,{'collection':'widths','filters':[{'field':'source_file','op':'eq','value':core.SOURCE}],'limit':100})
                if result['total']!=2:raise ValueError('Two satellite source means required')
                panel=ready(page,ids);card(panel,ids[0]).locator('summary').click()
                expect(card(panel,ids[0])).to_contain_text('not mathematically equivalent')
                for i,identity in enumerate(ids):capture(card(panel,identity),f'satellite-query-{i}-'+suffix)
                card(panel,ids[0]).get_by_role('button',name='Inspect',exact=True).click();expect(page.locator('#query-detail')).to_contain_text(ids[0])
                card(panel,ids[0]).get_by_role('link',name='Source record',exact=True).click();page.wait_for_function('window.oswSourceQueryResult?.ok')
                response=page.evaluate('window.oswSourceQueryResult')
                if {r['source_key']:r['record'] for r in response['rows']}!=original['records'][0]:raise ValueError('Exact browser source record differs')
                capture(page.locator('#source-query-results'),'satellite-source-altimetry-'+suffix)
                result=query(page,{'collection':'widths','filters':[{'field':'id','op':'eq','value':ids[1]}],'limit':100})
                if result['total']!=1:raise ValueError('Filtered width query differs')
                panel=ready(page,[ids[1]]);expect(panel).not_to_contain_text('64 km mean');capture(card(panel,ids[1]),'satellite-filtered-sst-'+suffix)
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Aagulhas#route-atlas')
                page.wait_for_function('window.oswAtlasSnapshot?.satellite_core_width_scenes?.agulhas?.records.length===2');expect(page.locator('#route-atlas-select')).to_have_value('current:agulhas')
                panel=ready(page,ids)
                for i,identity in enumerate(ids):capture(card(panel,identity),f'satellite-atlas-{i}-'+suffix)
                card(panel,ids[1]).get_by_role('button',name='Inspect',exact=True).click();page.wait_for_function('window.oswLastQueryResult?.ok');ready(page,[ids[1]])
                if page.evaluate('window.oswLastQueryResult.rows[0].id')!=ids[1]:raise ValueError('Atlas-to-query navigation differs')
                page.goto(base+'/almanac/seasons.html?current=agulhas');page.wait_for_function('window.oswSeasonSnapshot?.satellite_core_width_scenes?.agulhas?.records.length===2');expect(page.locator('#season-current')).to_have_value('agulhas')
                panel=ready(page,ids)
                for i,identity in enumerate(ids):capture(card(panel,identity),f'satellite-seasons-overview-{i}-'+suffix)
                for i,identity in enumerate(ids):
                    page.goto(base+'/almanac/seasons.html?current=agulhas&phase='+quote(identity));page.wait_for_function('window.oswSeasonSnapshot?.satellite_core_width_scenes?.agulhas?.records.length===2')
                    panel=ready(page,[identity]);expect(page.locator('#season-play')).to_be_disabled();capture(card(panel,identity),f'satellite-seasons-selected-{i}-'+suffix)
                result=query(page,{'collection':'widths','filters':[{'field':'id','op':'eq','value':'missing-satellite-width'}],'limit':100})
                if result['total']!=0:raise ValueError('Empty filter differs')
                expect(page.locator('.satellite-core-widths')).to_have_count(0)
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio#route-atlas');page.wait_for_function('window.oswAtlasSnapshot?.ok');expect(page.locator('#route-atlas-select')).to_have_value('current:kuroshio');expect(page.locator('.satellite-core-widths')).to_have_count(0)
                checks.append(f'Query two means; filtered/empty; source/Inspect; selected atlas; seasons overview and two static states; unrelated owner at{width}px')
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors/missing assets/original fetches: '+str([errors,missing,originals])[:3000])
        if len(images)!=20:raise ValueError('Twenty actual screenshots required')
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'visual_review_complete':False}
    finally:server.shutdown();server.server_close()
