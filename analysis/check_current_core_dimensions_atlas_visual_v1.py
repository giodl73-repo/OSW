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
REQUEST='research/current-core-dimensions-atlas-visual-request-v1.json'
PREFLIGHT='research/current-core-dimensions-atlas-visual-preflight-v1.json'
SAVED='research/current-core-dimensions-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/current-core-dimensions-atlas-visual-v1'
WORK=ROOT/'.pytest_cache/current-core-dimensions-atlas-visual-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='ab9cc0118e56fa752065ee68d552405280db276b'
RUN=41043869467
ARTIFACT={'id':12971394522,'bytes':99173291,'sha256':'2a63ae309295e34f99c50a7c23993b46c850442e2d56aefdb20b37459bdd3610'}
LOGICAL='191874b005d09c9680e13e5f1fd037a4045a47bbc709782318c3a3d5561d5127'
BINARY='208ae406cc8b49094885f3015a6e3ff601d5bac395374682b53ec4703e2da82e'
ORIGINAL_MANIFEST='06d618d3daed9d3aabfa51cb5bfd67d13b0ab36a6d0ee6290161b3840c48462a'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_CURRENT_CORE_DIMENSIONS_ATLAS_VISUAL_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.current-core-dimensions-atlas-visual-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    if len(files)!=18 or files['almanac/query-engine.manifest.json']['sha256']!=ORIGINAL_MANIFEST:raise ValueError('Exact 18 saved engine files required')
    return files

def presentation_files(files):
    import current_core_dimensions_atlas_presentation_v1 as presentation
    original=(ROOT/(SAVED+'engine-manifest.json')).read_bytes()
    updates={p:sha(p) for p in sorted(presentation.PATHS)}
    expected=presentation.overlay(original,updates)
    raw=(ROOT/presentation.FILE).read_bytes()
    if json.loads(raw)!=expected:raise ValueError('Presentation overlay differs from exact two-file update')
    final={p:dict(row) for p,row in files.items()}
    final['almanac/query-engine.manifest.json']={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    return final,raw

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
    import current_core_dimensions_query_v1 as query
    contract=query.build_contract()
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors=[];missing=[];screenshots=[];checks=[];loads=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            try:
                page=browser.new_page(viewport={'width':1100,'height':1000});page.set_default_timeout(240000);expect.set_options(timeout=240000)
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
                for owner in query.OWNERS:
                    row=next(r for key in ['reach_records','width_records'] for r in contract[key] if query.owns(r,owner));short=owner.removeprefix('current:')
                    page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(owner)+'#route-atlas')
                    page.wait_for_function('logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical',arg=LOGICAL)
                    loads.append({'owner':owner,'cold_browser_context':not loads,'status':page.evaluate('window.oswAtlasLoadStatus')})
                    panel=page.locator('#route-atlas-preview');details=panel.locator('.current-dimension-evidence');expect(details).to_be_visible();details.locator('summary').click()
                    attribute='data-dimension-length-id' if 'reported_length_interval_km' in row else 'data-dimension-width-id'
                    card=details.locator('['+attribute+'="'+row['id']+'"]');expect(card).to_be_visible();expect(card).to_contain_text(row['phase_label'])
                    metrics=panel.evaluate('(n)=>({overflow:getComputedStyle(n).overflowY,height:n.clientHeight,total:n.scrollHeight})')
                    if metrics['overflow'] not in ['auto','scroll'] or metrics['total']<=metrics['height']:raise ValueError('Expected genuine desktop scroll pane')
                    for position,target in [('top',card.locator('h4')),('bottom',card.get_by_role('link',name='Source evidence record',exact=True))]:
                        target.scroll_into_view_if_needed()
                        # Use the browser's normal scroll operation; do not alter CSS or DOM layout.
                        target.evaluate('(n)=>n.scrollIntoView({block:"center",inline:"nearest",behavior:"instant"})')
                        page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                        probe=target.evaluate('''n=>{const r=n.getBoundingClientRect(),a=n.closest('#route-atlas-preview').getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,hit=document.elementFromPoint(x,y);return {text:n.textContent,visible:r.width>0&&r.height>0&&r.top>=a.top&&r.bottom<=a.bottom&&r.left>=a.left&&r.right<=a.right&&y>=0&&y<innerHeight,hit:n.contains(hit),scrollTop:n.closest('#route-atlas-preview').scrollTop};}''')
                        if not probe['visible'] or not probe['hit']:raise ValueError('Atlas '+position+' target occluded after normal scrolling')
                        filename='atlas-'+short+'-'+position+'-1100px.png';path=OUT/filename;page.screenshot(path=str(path))
                        screenshots.append({'path':filename,'bytes':path.stat().st_size,'sha256':sha(path)})
                        checks.append({'width':1100,'owner':owner,'position':position,'case':'normal pane scrolling reveals card heading or source action without occlusion','probe':probe})
                    expect(card.get_by_role('button',name='Inspect regional reach record' if 'reported_length_interval_km' in row else 'Inspect width record',exact=True)).to_be_visible()
                    if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Desktop horizontal overflow')
                if errors or missing:raise ValueError('Atlas browser page error or missing asset')
            except Exception:
                page.screenshot(path=str(OUT/'browser-failure.png'))
                write(OUT/'cold-load-diagnostics.json',page.evaluate('''()=>({atlasLoad:window.oswAtlasLoadStatus??null,ready:!!window.oswAtlasSnapshot,resources:performance.getEntriesByType("resource").map(r=>({name:r.name,duration:r.duration,transferSize:r.transferSize})),body:document.body.innerText.slice(0,6000)})'''))
                raise
            finally:browser.close()
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':screenshots,'page_errors':errors,'missing_assets':missing,'original_science_downloads':[],'atlas_load_observations':loads,'viewports':[1100],'one_page_and_renderer':True,'visual_review_complete':False,'css_or_layout_modified_for_capture':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':screenshots,'page_errors':errors,'missing_assets':missing});raise
    finally:server.shutdown();server.server_close()


def main():
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    files=saved_files(read(SAVED+'result.json'));extract_saved(files)
    if sha('almanac/query-engine.manifest.json')!=ORIGINAL_MANIFEST or read('almanac/query-engine.manifest.json')!=read(SAVED+'engine-manifest.json'):
        raise ValueError('Saved engine manifest differs')
    for group in ('rust_source_sha256','compile_time_data_sha256'):
        for path,pin in read(SAVED+'compile-inventory.json')[group].items():
            if sha(path)!=pin:raise ValueError('Saved compiler input differs: '+path)
    files,final_raw=presentation_files(files)
    (ROOT/'almanac/query-engine.manifest.json').write_bytes(final_raw)
    manifest=read('almanac/query-engine.manifest.json')
    for path,pin in pref['presentation_sha256'].items():
        if sha(path)!=pin or manifest['sha256'].get(path)!=pin:raise ValueError('Presentation differs from saved engine: '+path)
    observed=browser_review()
    for path,row in files.items():
        if sha(path)!=row['sha256']:raise ValueError('Browser changed saved engine file: '+path)
    write(OUT/'result.json',{'schema':'osw.current-core-dimensions-atlas-visual-result.v1','status':observed['status'],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':SOURCE,'saved_engine_run':RUN,'saved_artifact':ARTIFACT,
        'logical_sha256':LOGICAL,'wasm_sha256':BINARY,'original_engine_manifest_sha256':ORIGINAL_MANIFEST,'engine_manifest_sha256':hashlib.sha256(final_raw).hexdigest(),'presentation_only_updates':['almanac/reference-routes.html','almanac/reference-routes.js'],
        'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})

if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise

