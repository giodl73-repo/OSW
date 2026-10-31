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
REQUEST='research/current-core-dimensions-browser-request-v1.json'
PREFLIGHT='research/current-core-dimensions-browser-preflight-v1.json'
SAVED='research/current-core-dimensions-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/current-core-dimensions-browser-v1'
WORK=ROOT/'.pytest_cache/current-core-dimensions-browser-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='ab9cc0118e56fa752065ee68d552405280db276b'
RUN=41043869467
ARTIFACT={'id':12971394522,'bytes':99173291,'sha256':'2a63ae309295e34f99c50a7c23993b46c850442e2d56aefdb20b37459bdd3610'}
LOGICAL='191874b005d09c9680e13e5f1fd037a4045a47bbc709782318c3a3d5561d5127'
BINARY='208ae406cc8b49094885f3015a6e3ff601d5bac395374682b53ec4703e2da82e'
MANIFEST='06d618d3daed9d3aabfa51cb5bfd67d13b0ab36a6d0ee6290161b3840c48462a'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_CURRENT_CORE_DIMENSIONS_BROWSER_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.current-core-dimensions-browser-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    if api('/git/ref/heads/main')['object']['sha']!='19148702de6433253dbf412a0a28c0cb4f8e409e':raise ValueError('Main moved')
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
    from contextlib import contextmanager
    import current_core_dimensions_query_v1 as query
    contract=query.build_contract()
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors=[];missing=[];originals=[];captures=[];checks=[];legibility=[]
    def capture(locator,name):
        locator.scroll_into_view_if_needed();target=OUT/(name+'.png');locator.screenshot(path=str(target))
        captures.append({'path':target.name,'bytes':target.stat().st_size,'sha256':sha(target)})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Page horizontal overflow')
    def record_for(owner):
        return next(r for key in ['reach_records','width_records'] for r in contract[key] if query.owns(r,owner))
    def card(panel,row):
        is_reach='reported_length_interval_km' in row
        selector='data-dimension-length-id' if is_reach else 'data-dimension-width-id'
        expect(panel.locator('['+selector+']')).to_have_count(1)
        selected=panel.locator('['+selector+'="'+row['id']+'"]');expect(selected).to_be_visible()
        expect(selected).to_contain_text(row['phase_label']);expect(selected).not_to_contain_text('undefined')
        if is_reach:
            expect(selected).to_contain_text('Reported regional reach: 110–120 km')
            expect(selected).to_contain_text('Campaign: 2001-08-21 to 2001-09-12')
            expect(selected).to_contain_text('Exact reach occupation dates: Unknown')
            expect(selected).to_contain_text('Annual length range: Unknown. Numerical length uncertainty: Unknown.')
            expect(selected).to_contain_text('Perim Narrows');expect(selected).to_contain_text('speed 0.2 m/s; salinity 38 psu')
            expect(selected.locator('svg line[stroke-width="8"]')).to_have_count(1)
            expect(selected.locator('svg circle')).to_have_count(0)
            expect(selected.locator('svg')).to_have_attribute('aria-label',__import__('re').compile('Neither uncertainty nor annual extrema'))
            expect(panel.locator('[data-dimension-width-id]')).to_have_count(0)
        else:
            expect(selected).to_contain_text('Cited estimate: about 650 km')
            expect(selected).to_contain_text('Not an independent new observation')
            expect(selected).to_contain_text('Observation dates, paired edges and original measurement method: Unknown')
            expect(selected).to_contain_text('New et al. (2007) is a provisional attribution')
            expect(selected).to_contain_text('Seasonal width range: Unknown. Numerical uncertainty: Unknown.')
            expect(selected.locator('svg circle')).to_have_count(1)
            expect(selected.locator('svg line[stroke-width="10"]')).to_have_count(0)
            expect(panel.locator('[data-dimension-length-id]')).to_have_count(0)
        metrics=selected.locator('p,h4,button,a').evaluate_all("""nodes=>nodes.filter(n=>n.getClientRects().length).map(n=>{const r=n.getBoundingClientRect(),b=n.closest('article').getBoundingClientRect();return {font:parseFloat(getComputedStyle(n).fontSize),inside:r.left>=b.left-2&&r.right<=b.right+2};})""")
        if not metrics or any(m['font']<11 or not m['inside'] for m in metrics):raise ValueError('Dimension card text clipped or undersized')
        legibility.append({'id':row['id'],'minimum_font_px':min(m['font'] for m in metrics),'all_text_inside_card':True})
        return selected
    def query_page(page,collection,owner,limit=100,offset=0):
        request={'collection':collection,'filters':[{'field':'entity_id','op':'eq','value':owner}],'limit':limit,'offset':offset}
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok === true')
        expect(page.locator('#query-engine-info')).to_contain_text(LOGICAL[:12])
        return page.locator('#query-chart-panels .current-dimension-evidence'),page.evaluate('window.oswLastQueryResult')
    def inspect_complete(page,selected,row,collection,suffix):
        selected.get_by_role('button',name='Inspect regional reach record' if collection==query.REACHES else 'Inspect width record',exact=True).click()
        page.wait_for_function('id=>[...document.querySelectorAll("#query-detail details > pre")].some(n=>{try{return JSON.parse(n.textContent).id===id}catch{return false}})',arg=row['id'])
        inspected=page.locator('#query-detail details > pre').evaluate_all('(nodes)=>nodes.map(n=>{try{return JSON.parse(n.textContent)}catch{return null}}).filter(Boolean)')
        if inspected!=[row]:raise ValueError('Inspect changed the complete admitted record')
        capture(page.locator('#query-detail h3').first,'inspect-'+collection+suffix)
    @contextmanager
    def observed_page():
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':1000});page.set_default_timeout(180000);expect.set_options(timeout=180000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz','.mat','.csv')) else None)
            try:yield page
            except Exception:
                try:
                    page.screenshot(path=str(OUT/'browser-failure.png'))
                    write(OUT/'browser-failure-state.json',page.evaluate("""()=>({url:location.href,title:document.title,status:document.querySelector('#dashboard-status')?.textContent,selection:window.oswDashboardSelection?{request:window.oswDashboardSelection.request,ids:window.oswDashboardSelection.result.ids}:null,visibleCardIds:[...document.querySelectorAll('.motion-card')].map(n=>n.dataset.id)})"""))
                except Exception:pass
                raise
            finally:browser.close()
    try:
        with observed_page() as page:
            for width in [1100,320]:
                suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1000})
                for owner in query.OWNERS:
                    row=record_for(owner);collection=query.REACHES if owner==query.OWNERS[0] else 'widths';short=owner.removeprefix('current:')
                    panel,result=query_page(page,collection,owner)
                    if result['total']!=1 or result['rows']!=[row]:raise ValueError('Query differs from exact source record')
                    selected=card(panel,row);capture(selected,'query-'+short+suffix);no_overflow(page)
                    checks.append({'width':width,'owner':owner,'case':'exact regional query, evidence class and unknown precision'})
                    panel,result=query_page(page,collection,owner,limit=1,offset=1)
                    if result['total']!=1 or result['rows']!=[]:raise ValueError('Pagination altered matching inventory')
                    selected=card(panel,row);inspect_complete(page,selected,row,collection,suffix)
                    checks.append({'width':width,'owner':owner,'case':'empty paginated rows retain matching scene and complete Inspect record'})
                    doc=row['source_file'];pointer=row['source_pointer']
                    page.goto(base+'/almanac/query.html?source-q='+quote(json.dumps({'document':doc,'pointer':pointer,'limit':500})))
                    page.wait_for_function('window.oswSourceQueryResult?.ok === true');source=page.evaluate('window.oswSourceQueryResult')
                    expected=query.read(doc)
                    for token in pointer.strip('/').split('/'):expected=expected[token]
                    if source['source_sha256']!=sha(doc) or {r['source_key']:r['record'] for r in source['rows']}!=expected:raise ValueError('Original source pointer or full source hash differs')
                    capture(page.locator('#source-query-results').first,'source-'+short+suffix);no_overflow(page)
                    checks.append({'width':width,'owner':owner,'case':'exact source object pointer and original facts hash'})
                    page.goto(base+'/almanac/object.html?id='+quote(owner));page.wait_for_function('id=>window.oswObjectView?.id===id',arg=owner)
                    data=page.evaluate('window.oswObjectView')
                    if data['bundle_sha256']!=LOGICAL or data['collections'][collection]!=[row]:raise ValueError('Object view source record differs')
                    selected=card(page.locator('#identity .current-dimension-evidence'),row);capture(selected,'object-'+short+suffix);no_overflow(page)
                    page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(owner)+'#route-atlas')
                    page.wait_for_function('logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical',arg=LOGICAL)
                    panel=page.locator('#route-atlas-preview .current-dimension-evidence');expect(panel).to_be_visible();panel.locator('summary').click()
                    selected=card(panel,row);capture(selected,'atlas-'+short+suffix);no_overflow(page)
                    page.goto(base+'/almanac/seasons.html?current='+short)
                    page.wait_for_function('arg=>window.oswSeasonSnapshot?.bundle_sha256===arg.logical&&document.querySelector("#season-current").value===arg.current',arg={'logical':LOGICAL,'current':short})
                    selected=card(page.locator('#published-section-transports .current-dimension-evidence'),row)
                    expect(page.locator('#season-play')).to_be_disabled();capture(selected,'seasons-'+short+suffix);no_overflow(page)
                    checks.append({'width':width,'owner':owner,'case':'current card, atlas and static season context preserve regional scope'})
                for collection in ['widths',query.REACHES]:
                    panel,result=query_page(page,collection,'current:south-equatorial')
                    if result['total']!=0 or result['chart_scene'] is not None:raise ValueError('Regional dimensions inherited by family')
                    expect(panel).to_have_count(0)
                checks.append({'width':width,'case':'neither regional reach nor cited width inherited by family'})
                for owner,metric,label in [(query.OWNERS[0],'reported_regional_reaches','Reported summer plume reach and source limits'),(query.OWNERS[1],'scoped_width','Cited upstream width and attribution limits')]:
                    row=record_for(owner);page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.entries?.length>0')
                    snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                    if sum(r.get('type')=='named_current' and r['capabilities'].get('scoped_width',0)>0 for r in snapshot['entries'])!=94:raise ValueError('Dashboard scoped-width owner count differs')
                    page.locator('#dashboard-metric').select_option(metric);page.locator('#dashboard-type').select_option('named_current');page.locator('#dashboard-covered').check();page.locator('#dashboard-card-view').click()
                    text=contract['final_objects'][owner]['label'];page.locator('#dashboard-search').fill(text)
                    page.wait_for_function("""arg=>{const s=document.querySelector('#dashboard-status'),v=window.oswDashboardSelection;return s?.dataset.pending==='false'&&(s.textContent.startsWith('Selection failed:')||(v?.request.text===arg.text&&v.request.metric===arg.metric&&v.request.covered_only===true&&v.request.record_type==='named_current'));}""",arg={'text':text,'metric':metric})
                    status=page.locator('#dashboard-status').inner_text()
                    if status.startswith('Selection failed:'):raise ValueError(status)
                    selected=page.locator('.motion-card[data-id="'+owner+'"]');expect(selected).to_be_visible();expect(selected).to_have_class(__import__('re').compile(r'\blit\b'))
                    expect(selected.locator('.selected-evidence')).to_contain_text('1 record')
                    capture(selected,'dashboard-'+owner.removeprefix('current:')+suffix);no_overflow(page)
                    selected.locator('details > summary').first.click();selected.get_by_role('link',name=label,exact=True).click()
                    page.wait_for_function('window.oswLastQueryResult?.ok === true')
                    if page.evaluate('window.oswLastQueryResult.rows')!=[row]:raise ValueError('Dashboard evidence link does not open exact record')
                    checks.append({'width':width,'owner':owner,'case':'covered metric lights correct card and links directly to exact evidence'})
            page.set_viewport_size({'width':1100,'height':1000});page.goto(base+'/figures/current-core-gap-followup-scoped-dimensions-v1.svg')
            expect(page.locator('svg')).to_be_visible();capture(page.locator('svg'),'scoped-dimensions-source-figure');no_overflow(page)
            checks.append({'width':1100,'case':'standalone graphic with separate reach and width scales'})
        if errors or missing or originals:raise ValueError('Page error, missing asset or original scientific download')
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility,'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility})
        raise
    finally:server.shutdown();server.server_close()


def main():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    files=saved_files(read(SAVED+'result.json'));extract_saved(files)
    if sha('almanac/query-engine.manifest.json')!=MANIFEST or read('almanac/query-engine.manifest.json')!=read(SAVED+'engine-manifest.json'):
        raise ValueError('Saved engine manifest differs')
    for group in ('rust_source_sha256','compile_time_data_sha256'):
        for path,pin in read(SAVED+'compile-inventory.json')[group].items():
            if sha(path)!=pin:raise ValueError('Saved compiler input differs: '+path)
    manifest=read('almanac/query-engine.manifest.json')
    for path,pin in pref['presentation_sha256'].items():
        if sha(path)!=pin or manifest['sha256'].get(path)!=pin:raise ValueError('Presentation differs from saved engine: '+path)
    observed=browser_review()
    for path,row in files.items():
        if sha(path)!=row['sha256']:raise ValueError('Browser changed saved engine file: '+path)
    write(OUT/'result.json',{'schema':'osw.current-core-dimensions-browser-result.v1','status':observed['status'],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':SOURCE,'saved_engine_run':RUN,'saved_artifact':ARTIFACT,
        'logical_sha256':LOGICAL,'wasm_sha256':BINARY,'engine_manifest_sha256':MANIFEST,
        'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})

if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise

