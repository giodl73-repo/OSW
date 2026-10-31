"""Capture actual visible sidebar sections without relaxing clipping guards."""
import functools
import hashlib
import http.server
import json
import os
import re
import threading
from urllib.parse import quote
from check_azores_2009_section_browser_v2 import CAPTURE_GEOMETRY,verify_capture_geometry
import published_wicc_review_width_v1 as core


def browser_review(root,output):
    if os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('OSW_WICC_REVIEW_WIDTH_DELIVERY_V1')!='1' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps':raise ValueError('Exact cloud browser required')
    from playwright.sync_api import sync_playwright,expect
    rows=[core.record()];ids=[core.ID];original=json.loads((root/core.SOURCE).read_bytes())
    prior=json.loads(json.loads((output/'parent-dashboard.json').read_bytes())['snapshot_json'])
    baseline={r['id']:{'fingerprint':r['fingerprint'],'sections':r['section_fingerprints']} for r in prior['entries']}
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
    def ready(page):
        panel=page.locator('.review-cited-widths');expect(panel).to_have_count(1)
        panel.wait_for(state='visible',timeout=180000)
        expect(panel.locator('[data-review-width-id]')).to_have_count(1)
        expect(panel.locator('[data-review-width-id]')).to_have_attribute('data-review-width-id',core.ID)
        expect(panel).to_contain_text('about 150 km')
        expect(panel).to_contain_text('not a new independent width sample')
        expect(panel).to_contain_text('annual range are unreported')
        if page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'):raise ValueError('Page overflow')
        if panel.locator('strong').evaluate('el=>parseFloat(getComputedStyle(el).fontSize)')<12:raise ValueError('Width text too small')
        return panel
    def query(page,request):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok');return page.evaluate('window.oswLastQueryResult')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':950});page.set_default_timeout(180000)
            page.add_init_script('if(location.pathname.endsWith("/dashboard.html"))localStorage.setItem("osw-motion-dashboard-seen-v2",'+json.dumps(json.dumps(baseline))+');')
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
            for width in [1100,320]:
                page.set_viewport_size({'width':width,'height':950});suffix=str(width)+'px.png'
                result=query(page,{'collection':'widths','filters':[{'field':'source_file','op':'eq','value':core.SOURCE}],'limit':100})
                if result['total']!=1 or result['rows']!=rows:raise ValueError('Exact review-cited width required')
                panel=ready(page);panel.locator('summary').click()
                expect(panel).to_contain_text('original methods have not been reviewed')
                expect(panel.get_by_role('link',name='Original review',exact=True)).to_have_attribute('href',original['source']['url'])
                capture(panel,'wicc-query-'+suffix)
                panel.get_by_role('button',name='Inspect',exact=True).click()
                expect(page.locator('#query-detail')).to_contain_text(core.ID)
                panel.get_by_role('link',name='Source record',exact=True).click()
                page.wait_for_function('window.oswSourceQueryResult?.ok');response=page.evaluate('window.oswSourceQueryResult')
                if {r['source_key']:r['record'] for r in response['rows']}!=original['records'][0]:raise ValueError('Exact browser source record differs')
                capture(page.locator('#source-query-results'),'wicc-source-'+suffix)
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Awest-india-coastal#route-atlas')
                page.wait_for_function('window.oswAtlasSnapshot?.review_cited_width_scenes?.["west-india-coastal"]?.records.length===1')
                expect(page.locator('#route-atlas-select')).to_have_value(core.OWNER)
                panel=ready(page)
                for part,target in [('title',panel.locator(':scope > h3')),('scope',panel.locator(':scope > p').nth(0)),('lineage',panel.locator(':scope > p').nth(1)),('width',panel.locator('[data-review-width-id]')),('figure',panel.locator(':scope > p').last)]:
                    capture(target,'wicc-atlas-'+part+'-'+suffix)
                panel.get_by_role('button',name='Inspect',exact=True).click()
                page.wait_for_function('window.oswLastQueryResult?.ok');ready(page)
                if page.evaluate('window.oswLastQueryResult.rows[0].id')!=core.ID:raise ValueError('Atlas Inspect navigation differs')
                for selected in [False,True]:
                    page.goto(base+'/almanac/seasons.html?current=west-india-coastal'+('&phase='+quote(core.ID) if selected else ''))
                    page.wait_for_function('window.oswSeasonSnapshot?.review_cited_width_scenes?.["west-india-coastal"]?.records.length===1')
                    expect(page.locator('#season-current')).to_have_value('west-india-coastal')
                    panel=ready(page);expect(page.locator('#season-play')).to_be_disabled()
                    expect(page.locator('#season-value')).to_contain_text('about 150 km')
                    capture(panel,'wicc-seasons-'+('selected-' if selected else 'default-')+suffix)
                page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.ok')
                snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot');prior_by_id={r['id']:r for r in prior['entries']}
                for row in snapshot['entries']:
                    old=prior_by_id[row['id']]
                    if row['id']==core.OWNER:
                        if row['capabilities']['scoped_width']!=1 or row['fingerprint']==old['fingerprint'] or row['section_fingerprints']['measurements']==old['section_fingerprints']['measurements']:raise ValueError('WICC dashboard did not light up')
                    elif row!=old:raise ValueError('Unrelated dashboard row changed')
                page.locator('#dashboard-card-view').click();page.locator('#dashboard-type').select_option('named_current')
                page.locator('#dashboard-metric').select_option('scoped_width');page.locator('#dashboard-search').fill('West India')
                page.locator('#dashboard-changed').check()
                card=page.locator('#dashboard-grid article[data-id="'+core.OWNER+'"]')
                expect(card).to_have_count(1);expect(card).to_have_class(re.compile(r'\bupdated\b'))
                expect(card.locator('.change-reason')).to_contain_text('Measurements changed')
                expect(card.locator('.selected-evidence')).to_contain_text('Scoped width evidence: 1 record')
                capture(card,'wicc-dashboard-updated-'+suffix)
                result=query(page,{'collection':'widths','filters':[{'field':'id','op':'eq','value':'missing-wicc-width'}],'limit':100})
                if result['total']!=0:raise ValueError('Empty filter differs')
                expect(page.locator('.review-cited-widths')).to_have_count(0)
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio#route-atlas')
                page.wait_for_function('window.oswAtlasSnapshot?.ok');expect(page.locator('#route-atlas-select')).to_have_value('current:kuroshio')
                expect(page.locator('.review-cited-widths')).to_have_count(0)
                checks.append(f'Exact query/source/Inspect; atlas navigation; static seasons; WICC-only dashboard update; empty/unrelated at{width}px')
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors/missing assets/original fetches: '+str([errors,missing,originals])[:3000])
        if len(images)!=20:raise ValueError('Twenty actual screenshots required')
        return {'status':'PASS','checks':checks,'screenshots':images,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'visual_review_complete':False}
    finally:server.shutdown();server.server_close()
