"""One cloud browser, exact saved engine, no rebuild or installation."""
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
import chen_indian_sec_browser_contract_v1 as contract

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-browser-request-v3.json'
PREFLIGHT='research/chen-indian-sec-browser-preflight-v3.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-browser-v3'
WORK=ROOT/'.pytest_cache/chen-indian-sec-browser-work-v3'
SAVED='research/chen-indian-sec-delivery-run-v4/'
SCOPE='research/chen-indian-sec-query-navigation-source-scope-v1.json'
REPO='repos/giodl73-repo/OSW'
OWNER='current:indian-south-equatorial'
GEOMETRY="""el=>{const r=el.getBoundingClientRect(),clips=[];
for(let p=el.parentElement;p&&!['BODY','HTML'].includes(p.tagName);p=p.parentElement){
const s=getComputedStyle(p),b=p.getBoundingClientRect();
if(/auto|scroll|hidden|clip/.test(s.overflowY)&&(r.top<b.top-2||r.bottom>b.bottom+2))clips.push('vertical');
if(/auto|scroll|hidden|clip/.test(s.overflowX)&&(r.left<b.left-2||r.right>b.right+2))clips.push('horizontal');}
return {width:r.width,height:r.height,clipped_axes:clips};}"""


def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))


def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true'
            or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps'
            or os.environ.get('OSW_CHEN_INDIAN_SEC_BROWSER_V3')!='1'):
        raise ValueError('Scoped cloud browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if (request.get('schema')!='osw.chen-indian-sec-browser-request.v3' or request.get('execute') is not True
            or request.get('preflight_sha256')!=sha(PREFLIGHT)
            or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0):
        raise ValueError('Disabled or changed browser request')
    for key in ['browser_permitted','cloud_candidate_files_permitted']:
        if request.get(key) is not True:raise ValueError('Missing browser scope')
    for key in ['native_build_permitted','wasm_build_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:
        if request.get(key) is not False:raise ValueError('Unrelated work enabled')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():
        if sha(path)!=pin:raise ValueError('Frozen source changed: '+path)
    for path,row in pref['installed_files'].items():
        if sha(path)!=row['sha256'] or (ROOT/path).stat().st_size!=row['bytes']:raise ValueError('Installed parent differs')
    for path in pref['disabled_requests']:
        old=read(path)
        if old.get('execute',old.get('execution_permitted')) is not False:raise ValueError('Older request enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad processing enabled')
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()
    if head!=os.environ['GITHUB_SHA'] or api('/git/ref/heads/codex/current-measurement-gaps')['object']['sha']!=head:raise ValueError('Exact source checkout required')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean source checkout required')
    return pref


def extract_saved(files):
    info=api('/actions/artifacts/'+str(contract.ARTIFACT['id']))
    if (info['expired'] or info['size_in_bytes']!=contract.ARTIFACT['bytes']
            or info['digest']!='sha256:'+contract.ARTIFACT['sha256']
            or info['workflow_run']['id']!=contract.RUN or info['workflow_run']['head_sha']!=contract.SOURCE):
        raise ValueError('Saved engine artifact metadata differs')
    archive=WORK/'engine.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh','api',REPO+'/actions/artifacts/'+str(contract.ARTIFACT['id'])+'/zip'],stdout=stream,check=True,timeout=300)
    if archive.stat().st_size!=contract.ARTIFACT['bytes'] or sha(archive)!=contract.ARTIFACT['sha256']:raise ValueError('Saved engine ZIP differs')
    with zipfile.ZipFile(archive) as z:
        members=[i for i in z.infolist() if not i.is_dir()]
        names=[i.filename for i in members]
        if len(names)!=len(set(names)) or set(names)!=set(files):raise ValueError('Exact18 saved engine paths required')
        if sum(i.file_size for i in members)>536870912:raise ValueError('Engine extraction budget exceeded')
        for item in members:
            path=item.filename;row=files[path]
            if Path(path).is_absolute() or '..' in Path(path).parts or '\\' in path or not path.startswith('almanac/'):
                raise ValueError('Unsafe saved engine path')
            if item.file_size!=row['bytes'] or item.file_size>104857600 or (item.external_attr>>16)&0o170000 not in (0,0o100000):
                raise ValueError('Invalid saved engine member')
            target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(item) as source,target.open('wb') as dest:shutil.copyfileobj(source,dest,1048576)
            if sha(path)!=row['sha256']:raise ValueError('Saved engine member changed: '+path)


def atlas_ready(page):
    try:
        page.wait_for_function("""logical=>{
          const status=document.getElementById('route-atlas-status')?.textContent||'';
          if(status.startsWith('Global current map unavailable:'))throw new Error(status);
          return typeof window.restoreReferenceRouteAtlas==='function'
            && window.oswAtlasSnapshot?.bundle_sha256===logical;
        }""",arg=contract.LOGICAL,timeout=180000)
    except Exception:
        state=page.evaluate("""()=>({status:document.getElementById('route-atlas-status')?.textContent,
          initializer_ready:typeof window.restoreReferenceRouteAtlas==='function',
          snapshot_logical_sha256:window.oswAtlasSnapshot?.bundle_sha256,
          regional_scene_keys:Object.keys(window.oswAtlasSnapshot?.regional_model_length_scenes||{}),
          path_count:document.querySelectorAll('#route-atlas-regional-model-lines path').length})""")
        write(OUT/'atlas-readiness-failure.json',state)
        page.screenshot(path=str(OUT/'atlas-readiness-failure.png'))
        raise


def browser_review(c):
    from playwright.sync_api import sync_playwright,expect
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors=[];missing=[];originals=[];captures=[];checks=[]
    series=c['series_record']['id'];qualified=[r for r in c['reading_records'] if r['length_km'] is not None]
    nominal=[r for r in qualified if r['kernel_cells']==3]
    k5=next(r for r in qualified if r['kernel_cells']==5)
    withheld=next(r for r in c['reading_records'] if r['length_km'] is None)
    eq=lambda field,value:{'field':field,'op':'eq','value':value}
    def capture(locator,name):
        locator.scroll_into_view_if_needed();geometry=locator.evaluate(GEOMETRY)
        if geometry['width']<=0 or geometry['height']<=0 or geometry['clipped_axes']:
            write(OUT/(name+'.geometry.json'),geometry);raise ValueError('Capture target is clipped: '+name)
        target=OUT/(name+'.png');locator.screenshot(path=str(target))
        captures.append({'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'geometry':geometry})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Page horizontal overflow')
    def open_query(page,request,anchor=''):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request))+anchor)
        page.wait_for_function('window.oswLastQueryResult?.ok === true')
        return page.evaluate('window.oswLastQueryResult')
    def readings(filters=(),limit=100,offset=0):
        return {'collection':'current_length_readings','filters':[eq('series_id',series),*filters],'limit':limit,'offset':offset}
    def check_panel(page,request,count,paths):
        result=open_query(page,request)
        if (result['total']!=count or result['chart_scene']['selected_count']!=count
                or result['map_scene'] is not None):raise ValueError('Regional query response differs')
        expect(page.locator('#query-engine-info')).to_contain_text(contract.LOGICAL[:12])
        panel=page.locator('#query-chart-panels .regional-model-lengths')
        expect(panel).to_be_visible();expect(panel.locator('svg path[data-model-reading-id]')).to_have_count(paths)
        expect(panel).to_contain_text('Whole-current length, physical width, annual dimension ranges and physical uncertainty: Unknown.')
        no_overflow(page);return panel,result
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':1100});page.set_default_timeout(180000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz','.mat')) else None)
            for width in (1100,320):
                suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1100})
                panel,result=check_panel(page,readings(),75,8)
                capture(panel,'query-all'+suffix)
                panel.locator('svg path[data-model-reading-id]').first.focus()
                expect(panel).to_contain_text('Regional model trace.')
                panel.locator('svg path[data-model-reading-id]').first.press('Enter')
                expect(page.locator('#query-detail')).to_be_visible()
                expect(page.locator('#query-detail')).to_contain_text(qualified[0]['id'])
                capture(page.locator('#query-detail h3').first,'reading-inspection'+suffix)
                checks.append({'width':width,'case':'all75/eight traces/keyboard inspection'})
                panel,_=check_panel(page,readings([eq('length_km',None)]),67,0)
                expect(panel).to_contain_text('Failed paths are withheld.');capture(panel,'query-withheld'+suffix)
                panel,_=check_panel(page,readings([eq('provider_year',1995)]),3,2)
                capture(panel,'query-year'+suffix)
                panel,result=check_panel(page,readings(limit=1,offset=1),75,8)
                if len(result['rows'])!=1 or len(result['chart_scene']['selected_records'])!=75:raise ValueError('Pagination dropped complete matching scene')
                panel,result=check_panel(page,{'collection':'current_length_sensitivities','filters':[eq('series_id',series)],'limit':100},120,0)
                if len(result['rows'])!=100:raise ValueError('Sensitivity page count differs')
                capture(panel,'query-sensitivities'+suffix)
                checks.append({'width':width,'case':'withheld/year/pagination/120 sensitivities'})
                legacy=next(r['url'] for r in c['final_owner']['evidence_links'] if r['label']=='View the three regional model traces')
                page.goto(base+'/almanac/'+legacy)
                page.wait_for_function('window.oswLastQueryResult?.ok && location.hash === "#query-chart-section"')
                panel=page.locator('#query-chart-panels .regional-model-lengths')
                expect(panel.locator('svg path[data-model-reading-id]')).to_have_count(3)
                expect(page.locator('#query-map-section')).to_be_hidden()
                expect(page.locator('#query-share')).to_have_attribute('href',page.url)
                page.wait_for_function('Math.abs(document.getElementById("query-chart-section").getBoundingClientRect().top)<3')
                capture(panel,'legacy-trace-target'+suffix)
                share=page.locator('#query-share').get_attribute('href');page.goto(share)
                page.wait_for_function('window.oswLastQueryResult?.ok && Math.abs(document.getElementById("query-chart-section").getBoundingClientRect().top)<3')
                checks.append({'width':width,'case':'legacy and modern trace anchors/share reload'})
                panel,_=check_panel(page,{'collection':'current_length_series','filters':[eq('id',series)],'limit':1},1,0)
                panel.get_by_role('button',name='Paper',exact=True).click()
                expect(page.locator('#query-detail')).to_contain_text(c['series_record']['source_id'])
                capture(page.locator('#query-detail h3').first,'paper-inspection'+suffix)
                doc='research/chen-indian-sec-length-measurement-rules-v1.json'
                page.goto(base+'/almanac/query.html?source-q='+quote(json.dumps({'document':doc,'pointer':'','limit':500})))
                page.wait_for_function('window.oswSourceQueryResult?.ok')
                source=page.evaluate('window.oswSourceQueryResult')
                if source['source_sha256']!=sha(doc) or {r['source_key']:r['record'] for r in source['rows']}!=read(doc):raise ValueError('Indexed method source differs')
                no_overflow(page);checks.append({'width':width,'case':'paper and indexed-method inspection'})
                page.goto(base+'/almanac/object.html?id='+quote(OWNER))
                page.wait_for_function('window.oswObjectView?.ok && window.oswObjectView.id === '+json.dumps(OWNER))
                panel=page.locator('#identity .regional-model-lengths')
                expect(panel.locator('svg path[data-model-reading-id]')).to_have_count(8)
                capture(panel,'current-card'+suffix);no_overflow(page)
                panel.get_by_text('Model-year coverage',exact=True).click()
                expect(panel.locator('details').first.locator('tbody tr')).to_have_count(len(c['series_record']['case_summaries']))
                expect(panel.locator('details').first).to_contain_text('4,700 km')
                expect(panel.locator('details').first).to_contain_text('4,900 km')
                capture(panel.locator('details').first,'model-year-coverage'+suffix)
                page.goto(base+'/almanac/object.html?id=current%3Asouth-equatorial')
                page.wait_for_function('window.oswObjectView?.ok && window.oswObjectView.id === "current:south-equatorial"')
                expect(page.locator('#identity .regional-model-lengths')).to_have_count(0)
                checks.append({'width':width,'case':'current card and no family inheritance'})
                atlas=base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'&atlas-model-reading='+quote(k5['id'])+'#route-atlas'
                page.goto(atlas)
                atlas_ready(page)
                layer=page.locator('#route-atlas-regional-model-lines')
                expect(layer.locator('path')).to_have_count(8)
                selected=layer.locator('path.selected');expect(selected).to_have_attribute('data-model-reading-id',k5['id']);expect(selected).to_be_visible()
                expect(layer.locator('[data-model-nominal="true"]')).to_have_count(3)
                panel=page.locator('#route-atlas-preview .regional-model-lengths')
                expect(panel.locator('svg path[data-model-reading-id]')).to_have_count(8)
                capture(page.locator('#route-atlas-map'),'atlas-selected-map'+suffix)
                capture(panel.locator('h3'),'atlas-evidence-heading'+suffix)
                capture(panel.locator('p').nth(2),'atlas-unknown-dimensions'+suffix)
                capture(panel.locator('svg'),'atlas-regional-traces'+suffix)
                expect(page.locator('#route-atlas-card-link')).to_have_attribute('href','object.html?id='+quote(OWNER,safe=''))
                share=page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
                if 'atlas-model-reading='+quote(k5['id'],safe='') not in share:raise ValueError('Atlas share lost selected trace')
                page.locator('#route-atlas-card-link').click()
                page.wait_for_function('window.oswObjectView?.ok && window.oswObjectView.id === '+json.dumps(OWNER))
                expect(page.locator('#identity .regional-model-lengths svg path[data-model-reading-id]')).to_have_count(8)
                page.goto(share);atlas_ready(page);expect(page.locator('#route-atlas-regional-model-lines path.selected')).to_have_attribute('data-model-reading-id',k5['id'])
                for reading_id in (withheld['id'],'unknown-reading'):
                    url=base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'&atlas-model-reading='+quote(reading_id)+'#route-atlas'
                    page.evaluate('url=>{history.replaceState(null,"",url);window.restoreReferenceRouteAtlas();}',url)
                    expect(page.locator('#route-atlas-regional-model-lines path.selected')).to_have_attribute('data-model-reading-id',nominal[0]['id'])
                svg=page.locator('#route-atlas-map');before=svg.get_attribute('viewBox')
                page.locator('#route-atlas-in').click()
                if float(svg.get_attribute('viewBox').split()[2])>=float(before.split()[2]):raise ValueError('Atlas zoom did not change view')
                page.locator('#route-atlas-out').click()
                page.locator('#route-atlas-world').click()
                expect(page.locator('#route-atlas-preview')).to_be_hidden()
                expect(layer.locator('path.selected')).to_have_count(0)
                if 'atlas-model-reading' in page.url:raise ValueError('Global reset retained selected trace')
                capture(svg,'atlas-global-map'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'atlas k5/share reload/withheld and unknown fallback/zoom/global reset'})
            browser.close()
        if errors or missing or originals:raise ValueError('Browser errors, missing assets or original-science download')
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,
                'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,
                'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,
            'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals})
        raise
    finally:server.shutdown();server.server_close()


def main():
    controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    saved=read(SAVED+'result.json');files=contract.verify_saved_result(saved);extract_saved(files)
    if sha('almanac/query-engine.manifest.json')!=contract.MANIFEST_SHA:raise ValueError('Saved manifest differs')
    original=read('almanac/query-engine.manifest.json')
    if original!=read(SAVED+'engine-manifest.json'):raise ValueError('Saved engine custody differs')
    scope=read(SCOPE)
    for path,row in scope['source_changes'].items():
        if sha(path)!=row['candidate_sha256'] or sha(row['archive_path'])!=row['parent_sha256']:raise ValueError('Navigation source changed')
    overlay=contract.navigation_manifest(original,scope,os.environ['GITHUB_SHA'])
    write(ROOT/'almanac/query-engine.manifest.json',overlay);write(OUT/'engine-manifest-navigation.json',overlay)
    inventory=read(SAVED+'compile-inventory.json')
    for group in ('rust_source_sha256','compile_time_data_sha256'):
        for path,pin in inventory[group].items():
            if sha(path)!=pin:raise ValueError('Saved engine source dependency differs: '+path)
    observed=browser_review(read('research/chen-indian-sec-ridge-length-query-contract-v1.json'))
    for path,row in files.items():
        if path!='almanac/query-engine.manifest.json' and sha(path)!=row['sha256']:raise ValueError('Browser changed engine file')
    if read('almanac/query-engine.manifest.json')!=overlay:raise ValueError('Browser changed navigation manifest')
    write(OUT/'result.json',{'schema':'osw.chen-indian-sec-browser-result.v3','status':observed['status'],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':contract.SOURCE,'saved_engine_run':contract.RUN,'saved_artifact':contract.ARTIFACT,
        'logical_sha256':contract.LOGICAL,'wasm_sha256':contract.BINARY,'parent_manifest_sha256':contract.MANIFEST_SHA,
        'navigation_manifest_sha256':sha(OUT/'engine-manifest-navigation.json'),
        'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})


if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise
