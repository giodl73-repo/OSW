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
REQUEST='research/richardson-walsh-1986-characteristic-velocity-browser-request-v1.json'
PREFLIGHT='research/richardson-walsh-1986-characteristic-velocity-browser-preflight-v1.json'
SAVED='research/richardson-walsh-1986-characteristic-velocity-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/richardson-walsh-1986-characteristic-velocity-browser-v1'
WORK=ROOT/'.pytest_cache/richardson-walsh-1986-characteristic-velocity-browser-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='156c254e5560634cf4da4b4046d4906f738782b3'
RUN=41002792054
ARTIFACT={'id':12954307576,'bytes':99102493,'sha256':'5a26096f3c929c5b51462795298f187628499bc3731e60b73525340785e60849'}
OWNER='current:atlantic-north-equatorial'
LOGICAL='d21ade39ba095192df3f4c6adef702d0d5f68570ea736f455eaf84980d9800ea'
BINARY='536521a9aca1ab106bb8cb7445786c8fb224f08cec58e1aa7141dad0b8c9604e'
MANIFEST='9bdca901dc64887f9f8176bc0fb484cebbd95e11baf2d9d1f47143854fbf7df3'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_CHARACTERISTIC_VELOCITIES_BROWSER_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.characteristic-velocities-browser-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    import characteristic_velocities_query_v1 as query
    contract=query.build_contract();records=contract['records']
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
    def cards(panel,expected):
        expect(panel.locator('[data-characteristic-velocity-id]')).to_have_count(len(expected))
        ids=panel.locator('[data-characteristic-velocity-id]').evaluate_all('nodes=>nodes.map(n=>n.dataset.characteristicVelocityId)')
        if ids!=[r['id'] for r in expected]:raise ValueError('Source order or exact record identity changed')
        for row in expected:
            card=panel.locator('[data-characteristic-velocity-id="'+row['id']+'"]')
            expect(card).to_contain_text(row['source_current_label'])
            interval=row['characteristic_mean_vector_speed_interval_m_s']
            mean='â€“'.join(format(v,'.2f') for v in interval) if interval else format(row['characteristic_mean_vector_speed_m_s'],'.2f')
            values=[mean]+[format(row[k],'.2f') for k in ['seasonal_velocity_variation_m_s','annual_harmonic_source_amplitude_m_s','semiannual_harmonic_source_amplitude_m_s']]
            expect(card.locator('dd')).to_have_text([v+' m/s' for v in values])
            expect(card).to_contain_text('annual extrema, confidence interval and monthly series remain unknown')
            expect(card).not_to_contain_text('undefined')
            expect(card.get_by_role('button',name='Inspect velocity summary',exact=True)).to_be_visible()
            metrics=card.locator('h4,dt,dd,p,button,a').evaluate_all("""nodes=>nodes.filter(n=>n.getClientRects().length).map(n=>{const r=n.getBoundingClientRect(),b=n.closest('article').getBoundingClientRect();return {font:parseFloat(getComputedStyle(n).fontSize),inside:r.left>=b.left-2&&r.right<=b.right+2};})""")
            if any(m['font']<11 or not m['inside'] for m in metrics):raise ValueError('Velocity card text clipped or undersized')
            legibility.append({'id':row['id'],'minimum_font_px':min(m['font'] for m in metrics),'all_text_inside_card':True})
    def query_page(page,filters=None,limit=100,offset=0):
        request={'collection':query.COLLECTION,'limit':limit,'offset':offset}
        if filters:request['filters']=filters
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok === true')
        expect(page.locator('#query-engine-info')).to_contain_text(LOGICAL[:12])
        return page.locator('#query-chart-panels .published-characteristic-velocities'),page.evaluate('window.oswLastQueryResult')
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
            for width in (1100,320):
                suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1000})
                panel,result=query_page(page);cards(panel,records)
                if result['total']!=10:raise ValueError('Full query inventory differs')
                for n,row in enumerate(records):capture(panel.locator('[data-characteristic-velocity-id="'+row['id']+'"]'),'query-'+str(n+1).zfill(2)+suffix)
                no_overflow(page);checks.append({'width':width,'case':'all ten source-ordered summaries, four exact metrics, interval and unknowns'})
                owner='current:atlantic-south-equatorial';selected=[r for r in records if r['entity_id']==owner]
                panel,result=query_page(page,[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],1,1)
                if result['total']!=3 or len(result['rows'])!=1:raise ValueError('Filtered pagination differs')
                cards(panel,selected)
                panel.locator('[data-characteristic-velocity-id]').nth(2).get_by_role('button',name='Inspect velocity summary',exact=True).click()
                page.wait_for_function('id=>window.oswLastQueryResult?.rows?.[0]?.id===id&&window.oswLastQueryResult.total===1',arg=selected[2]['id'])
                expect(page.locator('#query-chart-panels .published-characteristic-velocities h3')).to_have_text('Tropical Atlantic: characteristic velocity summaries')
                page.get_by_role('link',name='Source table record',exact=True).click()
                page.wait_for_function('window.oswSourceQueryResult?.ok===true')
                actual=page.evaluate('window.oswSourceQueryResult');source=read(records[0]['source_file'])
                expected=source['table_rows'][int(selected[2]['source_pointer'].split('/')[-1])]
                if actual['source_sha256']!=sha(records[0]['source_file']) or {r['source_key']:r['record'] for r in actual['rows']}!=expected:raise ValueError('Exact original table pointer differs')
                capture(page.locator('#source-query-results').first,'source-pointer'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'pagination retains full matching chart, Inspect navigates to exact record and source pointer'})
                for family in query.FAMILIES:
                    panel,result=query_page(page,[{'field':'current_id','op':'eq','value':family.removeprefix('current:')}])
                    if result['total']!=0:raise ValueError('Family inherited member measurement')
                    expect(panel).to_have_count(0)
                checks.append({'width':width,'case':'two basin families do not inherit velocity evidence'})
                for owner in query.OWNERS:
                    selected=[r for r in records if r['entity_id']==owner]
                    page.goto(base+'/almanac/object.html?id='+quote(owner));page.wait_for_function('owner=>window.oswObjectView?.id===owner',arg=owner)
                    if page.evaluate('window.oswObjectView.bundle_sha256')!=LOGICAL:raise ValueError('Current card engine identity differs')
                    panel=page.locator('#identity .published-characteristic-velocities');expect(panel).to_be_visible();cards(panel,selected);no_overflow(page)
                    if owner in ('current:atlantic-north-equatorial-countercurrent','current:atlantic-south-equatorial'):
                        capture(panel.locator('[data-characteristic-velocity-id]').first,'object-'+owner.removeprefix('current:')+suffix)
                checks.append({'width':width,'case':'all eight current cards show only their own characteristic records'})
                owner='current:atlantic-north-equatorial-countercurrent';selected=[r for r in records if r['entity_id']==owner]
                for name,url,ready,root in [
                    ('atlas',base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(owner)+'#route-atlas','logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical','#route-atlas-preview'),
                    ('seasons',base+'/almanac/seasons.html?current=atlantic-north-equatorial-countercurrent','logical=>window.oswSeasonSnapshot?.bundle_sha256===logical&&document.querySelector("#season-current").value==="atlantic-north-equatorial-countercurrent"','#published-section-transports')]:
                    page.goto(url);page.wait_for_function(ready,arg=LOGICAL)
                    panel=page.locator(root+' .published-characteristic-velocities');expect(panel).to_be_visible();cards(panel,selected)
                    expect(page.locator(root+' .published-seasonal-core-velocities')).to_have_count(1)
                    capture(panel.locator('[data-characteristic-velocity-id]').first,name+'-separate-velocity-context'+suffix);no_overflow(page)
                    scene=page.evaluate('(name)=>window[name].published_speed_scenes["atlantic-north-equatorial-countercurrent"]',arg='oswAtlasSnapshot' if name=='atlas' else 'oswSeasonSnapshot')
                    if scene['kind']!='published_velocity_evidence_groups' or len(scene['scenes'])!=2 or scene['scenes'][0]['kind']!='published_seasonal_core_velocities':raise ValueError('Prior core operator merged or lost')
                checks.append({'width':width,'case':'atlas and seasons retain separate prior core estimates and static characteristic summaries'})
                page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.entries?.length>0')
                entries=page.evaluate('window.oswDashboardSnapshot.snapshot.entries')
                covered=[r for r in entries if r.get('type')=='named_current' and r['capabilities'].get('characteristic_velocity',0)>0]
                if {r['id'] for r in covered}!=set(query.OWNERS) or sum(r['capabilities']['characteristic_velocity'] for r in covered)!=10:raise ValueError('Dashboard characteristic coverage differs')
                page.locator('#dashboard-metric').select_option('characteristic_velocity');page.locator('#dashboard-type').select_option('named_current');page.locator('#dashboard-card-view').click()
                page.wait_for_function('()=>{const s=window.oswDashboardSelection;return document.querySelector("#dashboard-status")?.dataset.pending==="false"&&s?.request.metric==="characteristic_velocity"&&s.request.record_type==="named_current"}')
                ids=page.evaluate('window.oswDashboardSelection.result.ids')
                if set(ids)!=set(query.OWNERS):raise ValueError('Dashboard lit selection differs')
                owner='current:atlantic-south-equatorial';card=page.locator('.motion-card[data-id="'+owner+'"]');expect(card).to_be_visible();expect(card).to_have_class(__import__('re').compile(r'\blit\b'))
                expect(card.locator('.selected-evidence')).to_contain_text('3');capture(card,'dashboard-velocity-light'+suffix);no_overflow(page)
                card.locator('details > summary').first.click();card.get_by_role('link',name='Characteristic velocity summaries and original source',exact=True).click()
                page.wait_for_function('window.oswLastQueryResult?.ok===true&&window.oswLastQueryResult.collection==="current_characteristic_velocities"')
                if page.evaluate('window.oswLastQueryResult.total')!=3:raise ValueError('Dashboard evidence navigation differs')
                checks.append({'width':width,'case':'eight lit current identities, ten summaries, three-record SEC card and direct evidence navigation'})
        if errors or missing or originals:raise ValueError('Page error, missing asset or original science download')
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility,'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility});raise
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
    write(OUT/'result.json',{'schema':'osw.characteristic-velocities-browser-result.v1','status':observed['status'],
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

