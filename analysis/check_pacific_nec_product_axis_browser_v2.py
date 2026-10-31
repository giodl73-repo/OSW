"""One cloud browser, exact saved candidate, no build or field processing."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
from urllib.parse import quote
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/pacific-nec-product-axis-browser-request-v2.json'
PREFLIGHT='research/pacific-nec-product-axis-browser-preflight-v2.json'
SAVED='research/pacific-nec-product-axis-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/pacific-nec-product-axis-browser-v2'
WORK=ROOT/'.pytest_cache/pacific-nec-product-axis-browser-work-v2'
REPO='repos/giodl73-repo/OSW'
SOURCE='6c24a0db510599df803fad9516033c48c2ba520e'
RUN=40909369948
ARTIFACT={'id':12913028078,'bytes':98658436,'sha256':'4578a31d981826b7de3f3f8e2d6c46d899083bfe0d123cf2810f1d988cade696'}
OWNER='current:pacific-north-equatorial'
LOGICAL='dc671a2af236089e37c02489e0cba6bea52e81298879abf0ea809f8d9552a936'
BINARY='7507f7902eb52c43e99563c4cea27f2c1edc285a795d8cb136ca93eea6a1b427'
MANIFEST='0dc5b726c98fe3f074e15a713da5b7c42f48ea5306743ad624b8f2275db7b595'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_NEC_PRODUCT_BROWSER_V2')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.pacific-nec-product-axis-browser-request.v2' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
    for key in ['browser_permitted','cloud_candidate_files_permitted']:
        if request.get(key) is not True:raise ValueError('Missing browser permission')
    for key in ['native_build_permitted','wasm_build_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated work enabled')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen input differs: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256'] or (ROOT/path).stat().st_size!=row['bytes']:raise ValueError('Installed parent differs: '+path)
    for path in pref['disabled_requests']:
        old=read(path)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Older request enabled: '+path)
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad processing enabled')
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or api('/git/ref/heads/codex/current-measurement-gaps')['object']['sha']!=head or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact source checkout required')
    return pref

def saved_files(result):
    if result.get('status')!='PASS_COMPLETE_NATIVE_WASM_CANDIDATE_BROWSER_PENDING' or result.get('source_commit')!=SOURCE or result.get('run_id')!=str(RUN) or result.get('run_attempt')!='1' or result.get('logical_sha256')!=LOGICAL or result.get('wasm_sha256')!=BINARY:raise ValueError('Exact passing saved candidate required')
    files=result['generated_files']
    if len(files)!=18 or files['almanac/query-engine.manifest.json']['sha256']!=MANIFEST:raise ValueError('Exact 18 saved engine files required')
    return files

def extract_saved(files):
    info=api('/actions/artifacts/'+str(ARTIFACT['id']))
    if info['expired'] or info['size_in_bytes']!=ARTIFACT['bytes'] or info['digest']!='sha256:'+ARTIFACT['sha256'] or info['workflow_run']['id']!=RUN or info['workflow_run']['head_sha']!=SOURCE:raise ValueError('Saved artifact metadata differs')
    archive=WORK/'engine.zip'
    with archive.open('xb') as stream:subprocess.run(['gh','api',REPO+'/actions/artifacts/'+str(ARTIFACT['id'])+'/zip'],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=ARTIFACT['bytes'] or sha(archive)!=ARTIFACT['sha256']:raise ValueError('Saved engine ZIP differs')
    with zipfile.ZipFile(archive) as z:
        members=[r for r in z.infolist() if not r.is_dir()];names=[r.filename for r in members]
        if len(names)!=len(set(names)) or set(names)!=set(files) or sum(r.file_size for r in members)>536870912:raise ValueError('Saved extraction inventory differs')
        for row in members:
            path=row.filename;expected=files[path]
            if Path(path).is_absolute() or '..' in Path(path).parts or '\\' in path or not path.startswith('almanac/') or (row.external_attr>>16)&0o170000 not in (0,0o100000) or row.file_size!=expected['bytes'] or row.file_size>104857600:raise ValueError('Unsafe or changed saved member')
            target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(row) as source,target.open('wb') as dest:shutil.copyfileobj(source,dest,1048576)
            if sha(path)!=expected['sha256']:raise ValueError('Saved engine member changed: '+path)

def browser_review():
    from playwright.sync_api import sync_playwright,expect
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start();base='http://127.0.0.1:'+str(server.server_port)
    errors=[];missing=[];originals=[];captures=[];checks=[];legibility=[]
    contract=read('research/pacific-nec-product-axis-query-contract-v1.json');readings=contract['collections_added']['current_axis_readings']
    chosen=next(r for r in readings if r['month']==7 and r['window_deg_north']==[7,19])
    nominal=next(r for r in readings if r['month']==1 and r['window_deg_north']==[8,18])
    eq=lambda field,value:{'field':field,'op':'eq','value':value}
    def capture(locator,name):
        locator.scroll_into_view_if_needed();target=OUT/(name+'.png');locator.screenshot(path=str(target))
        captures.append({'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target)})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Page horizontal overflow')
    def plot_check(panel,width):
        metrics=panel.locator('.product-axis-chart text').evaluate_all("""nodes=>nodes.map(n=>{const r=n.getBoundingClientRect(),b=n.ownerSVGElement.getBoundingClientRect(),m=n.getScreenCTM();return {text:n.textContent,font_css_px:parseFloat(getComputedStyle(n).fontSize)*Math.hypot(m.a,m.b),inside:r.left>=b.left-2&&r.right<=b.right+2&&r.top>=b.top-2&&r.bottom<=b.bottom+2};})""")
        legibility.append({'width':width,'kind':'plot text','metrics':metrics})
        if not metrics or any(r['font_css_px']<11 or not r['inside'] for r in metrics):
            capture(panel,'plot-label-failure-'+str(width)+'px');raise ValueError('Plot labels undersized or clipped')
    def table_check(details,width):
        metrics=details.locator('tbody td').evaluate_all("""nodes=>nodes.map(n=>{const r=n.getBoundingClientRect(),b=n.closest('details').getBoundingClientRect();return {width:r.width,inside:r.left>=b.left-2&&r.right<=b.right+2,text:n.textContent};})""")
        legibility.append({'width':width,'kind':'table cells','count':len(metrics),'minimum_cell_width':min((r['width'] for r in metrics),default=0)})
        if not metrics or width==320 and any(not r['inside'] or r['width']<120 for r in metrics):raise ValueError('Narrow measurement cells clipped or too small')
    def query(page,name,filters=(),limit=100,offset=0):
        request={'collection':name,'filters':list(filters),'limit':limit,'offset':offset}
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok === true')
        expect(page.locator('#query-engine-info')).to_contain_text(LOGICAL[:12])
        return page.locator('#query-chart-panels .surface-product-axes'),page.evaluate('window.oswLastQueryResult')
    def atlas_ready(page):
        page.wait_for_function("logical=>typeof window.restoreReferenceRouteAtlas==='function'&&window.oswAtlasSnapshot?.bundle_sha256===logical",arg=LOGICAL)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1']);page=browser.new_page(viewport={'width':1100,'height':1100});page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz','.mat','.csv')) else None)
            for width in (1100,320):
                suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1100})
                panel,result=query(page,'current_axis_readings')
                if result['total']!=36 or result['chart_scene']['selected_count']!=36:raise ValueError('Full path query differs')
                expect(panel).to_be_visible();plot_check(panel,width);capture(panel,'query-paths'+suffix);no_overflow(page)
                panel.locator('select').nth(0).select_option(chosen['series_id']);panel.locator('select').nth(1).select_option(chosen['id'])
                expect(panel.locator('[aria-live]')).to_contain_text('2013-07');expect(panel.locator('[aria-live]')).to_contain_text('7–19°N')
                play=panel.get_by_role('button',name='Play dated months',exact=True);play.click()
                page.wait_for_function("id=>document.querySelector('#query-chart-panels .surface-product-axes select:nth-of-type(1)')&&document.querySelectorAll('#query-chart-panels .surface-product-axes select')[1].value!==id",arg=chosen['id'])
                panel.get_by_role('button',name='Pause dated months',exact=True).click()
                panel.locator('select').nth(1).select_option(chosen['id']);capture(panel.locator('.product-axis-chart').first,'july-window-path'+suffix)
                panel.get_by_text('Monthly native paths (36)',exact=True).click();details=panel.locator('details').first
                expect(details.locator('tbody tr')).to_have_count(36);table_check(details,width);capture(details.locator('tbody tr').first,'reading-row'+suffix)
                details.locator('summary').click();panel.locator('svg path[role=button]').focus();panel.locator('svg path[role=button]').press('Enter')
                expect(page.locator('#query-detail')).to_contain_text(chosen['id']);capture(page.locator('#query-detail h3').first,'reading-inspection'+suffix)
                checks.append({'width':width,'case':'all paths/window/month/playback/keyboard inspection'})
                panel,result=query(page,'current_axis_readings',[eq('id',chosen['id'])]);expect(panel.locator('select').nth(1).locator('option')).to_have_count(1)
                if result['total']!=1 or len(result['chart_scene']['readings'])!=1:raise ValueError('Filtered path view leaked other months')
                capture(panel,'query-single-path'+suffix)
                panel,result=query(page,'current_axis_readings',limit=1,offset=1)
                if len(result['rows'])!=1 or result['chart_scene']['selected_count']!=36:raise ValueError('Pagination changed complete scene')
                panel,result=query(page,'current_axis_scenarios',[eq('length_km',None)],limit=1,offset=1)
                if result['total']!=85 or result['chart_scene']['readings'] or len(result['chart_scene']['selected_records'])!=85:raise ValueError('Withheld scenario view differs')
                expect(panel.locator('svg')).to_have_count(0);capture(panel,'query-withheld'+suffix)
                panel.get_by_text('Matching operator scenarios (85)',exact=True).click();details=panel.locator('details').first
                expect(details.locator('tbody tr')).to_have_count(85);table_check(details,width);capture(details.locator('tbody tr').first,'scenario-row'+suffix)
                panel,result=query(page,'current_axis_section_spans',[eq('width_km',None)])
                if result['total']!=1:raise ValueError('Censored span missing')
                panel.get_by_text('Fixed-meridian numerical spans (1)',exact=True).click();expect(panel.locator('details').first).to_contain_text('Withheld')
                capture(panel.locator('details').first,'censored-span'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'filtered/paginated/85 withheld scenarios/censored span'})
                doc='research/pacific-nec-product-axis-measurement-rules-v1.json'
                page.goto(base+'/almanac/query.html?source-q='+quote(json.dumps({'document':doc,'pointer':'','limit':500})))
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                result=page.evaluate('window.oswSourceQueryResult')
                if result['source_sha256']!=sha(doc) or {r['source_key']:r['record'] for r in result['rows']}!=read(doc):raise ValueError('Indexed method source changed')
                checks.append({'width':width,'case':'registered measurement rules inspect exactly'})
                page.goto(base+'/almanac/object.html?id='+quote(OWNER));page.wait_for_function('window.oswObjectView?.id === '+json.dumps(OWNER))
                panel=page.locator('#identity .surface-product-axes');expect(panel).to_be_visible();plot_check(panel,width);capture(panel,'current-card'+suffix)
                panel.get_by_text('Product, context paper and measurement method',exact=True).click();panel.locator('details').last.locator('button').first.click()
                page.wait_for_function('window.oswLastQueryResult?.ok');expect(page.locator('#query-rows')).to_contain_text('source:oscar2017-noaa-pifsc-archive')
                page.goto(base+'/almanac/object.html?id=current%3Anorth-equatorial');page.wait_for_function('window.oswObjectView?.id === "current:north-equatorial"')
                expect(page.locator('#identity .surface-product-axes')).to_have_count(0)
                checks.append({'width':width,'case':'current card/source navigation/no family inheritance'})
                url=base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'&atlas-product-reading='+quote(chosen['id'])+'#route-atlas'
                page.goto(url);atlas_ready(page);layer=page.locator('#route-atlas-product-axis-lines');expect(layer.locator('path')).to_have_count(36)
                selected=layer.locator('path.selected');expect(selected).to_have_attribute('data-product-reading-id',chosen['id']);expect(selected).to_be_visible()
                if selected.get_attribute('d').count('M')!=2:raise ValueError('Global path did not preserve separate dateline segments')
                panel=page.locator('#route-atlas-preview .surface-product-axes');plot_check(panel,width)
                capture(page.locator('#route-atlas-map'),'atlas-selected'+suffix);capture(panel.locator('.product-axis-chart').first,'atlas-preview-path'+suffix)
                panel.locator('select').nth(1).select_option(next(r['id'] for r in readings if r['series_id']==chosen['series_id'] and r['month']==8))
                expect(page.locator('#route-atlas-status')).to_contain_text('2013-08')
                share=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
                if 'atlas-product-reading=' not in share:raise ValueError('Shared view lost selected month')
                page.goto(share);atlas_ready(page);expect(page.locator('#route-atlas-status')).to_contain_text('2013-08')
                page.locator('#route-atlas-card-link').click();page.wait_for_function('window.oswObjectView?.id === '+json.dumps(OWNER));expect(page.locator('#identity .surface-product-axes')).to_be_visible()
                page.goto(share);atlas_ready(page);svg=page.locator('#route-atlas-map');before=float(svg.get_attribute('viewBox').split()[2]);page.locator('#route-atlas-in').click()
                if float(svg.get_attribute('viewBox').split()[2])>=before:raise ValueError('Atlas zoom failed')
                page.locator('#route-atlas-world').click();expect(page.locator('#route-atlas-preview')).to_be_hidden()
                if 'atlas-product-reading' in page.url:raise ValueError('Global reset retained product selection')
                capture(svg,'atlas-global'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'atlas dateline/month/share reload/card/zoom/reset'})
                page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.surface_product_axis_diagnostics?.monthly_path_count===36')
                expect(page.locator('#dashboard-product-axis-status')).to_contain_text('Physical measurement coverage is unchanged.')
                capture(page.locator('#dashboard-product-axis-status'),'dashboard-diagnostics'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'separate dashboard diagnostic readiness'})
            browser.close()
        if errors or missing or originals:raise ValueError('Page errors, missing assets or original-field download')
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility,'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility})
        try:page.screenshot(path=str(OUT/'browser-failure.png'))
        except Exception:pass
        raise
    finally:server.shutdown();server.server_close()

def main():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    files=saved_files(read(SAVED+'result.json'));extract_saved(files)
    if sha('almanac/query-engine.manifest.json')!=MANIFEST or read('almanac/query-engine.manifest.json')!=read(SAVED+'engine-manifest.json'):raise ValueError('Saved engine manifest differs')
    from pacific_nec_product_axis_browser_presentation_v1 import presentation_manifest
    scope=read('research/pacific-nec-product-axis-presentation-scope-v1.json')
    for path,row in scope['source_changes'].items():
        if sha(path)!=row['candidate_sha256'] or sha(row['archive_path'])!=row['parent_sha256']:raise ValueError('Presentation source custody differs: '+path)
    overlay=presentation_manifest(read('almanac/query-engine.manifest.json'),scope,os.environ['GITHUB_SHA'])
    write(ROOT/'almanac/query-engine.manifest.json',overlay);write(OUT/'engine-manifest-presentation.json',overlay)
    for group in ['rust_source_sha256','compile_time_data_sha256']:
        for path,pin in read(SAVED+'compile-inventory.json')[group].items():
            if sha(path)!=pin:raise ValueError('Saved compiler input differs: '+path)
    manifest=read('almanac/query-engine.manifest.json')
    for path,pin in pref['presentation_sha256'].items():
        if sha(path)!=pin or manifest['sha256'].get(path)!=pin:raise ValueError('Presentation differs from saved engine: '+path)
    observed=browser_review()
    for path,row in files.items():
        if path!='almanac/query-engine.manifest.json' and sha(path)!=row['sha256']:raise ValueError('Browser changed saved engine files')
    if read('almanac/query-engine.manifest.json')!=overlay:raise ValueError('Browser changed scoped presentation manifest')
    write(OUT/'result.json',{'schema':'osw.pacific-nec-product-axis-browser-result.v2','status':observed['status'],'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':SOURCE,'saved_engine_run':RUN,'saved_artifact':ARTIFACT,'logical_sha256':LOGICAL,'wasm_sha256':BINARY,'parent_manifest_sha256':MANIFEST,'presentation_manifest_sha256':sha(OUT/'engine-manifest-presentation.json'),'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})

if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise
