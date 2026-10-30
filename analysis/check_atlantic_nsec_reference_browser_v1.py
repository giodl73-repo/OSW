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
REQUEST='research/atlantic-nsec-reference-browser-request-v1.json'
PREFLIGHT='research/atlantic-nsec-reference-browser-preflight-v1.json'
SAVED='research/atlantic-nsec-reference-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/atlantic-nsec-reference-browser-v1'
WORK=ROOT/'.pytest_cache/atlantic-nsec-reference-browser-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='bd0200eb6779d14628f45df823623c2ae63e31ad'
RUN=41071742540
ARTIFACT={'id':12987049064,'bytes':99204166,'sha256':'3185a7d660c6100a2bc7cff7e998d8f72a52968a4ab8ba3c7ce2ade9cd1fa60d'}
LOGICAL='09b882c97c922a0643880885a6165388bf41b19903e72a6d9ca44437da1ed41e'
BINARY='d5cee93f0d1636be3902d4a875cb86cc30a6c9b887d2b4fd9e677e9ec0559c57'
MANIFEST='bf958da200693e48e174ae87791473284ebcfefe3b718f66463ac5345e1792ed'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_ATLANTIC_NSEC_REFERENCE_BROWSER_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.atlantic-nsec-reference-browser-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    import atlantic_nsec_reference_query_v1 as query
    contract=query.build_contract();owner=query.OWNER;short=owner.removeprefix('current:')
    routes=contract['routes']
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base='http://127.0.0.1:'+str(server.server_port)
    errors=[];missing=[];originals=[];captures=[];checks=[];loads=[];legibility=[]
    def capture(page,name):
        path=OUT/(name+'.png');page.screenshot(path=str(path))
        captures.append({'path':path.name,'bytes':path.stat().st_size,'sha256':sha(path)})
    def no_overflow(page):
        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):raise ValueError('Horizontal page overflow')
    def query_page(page,request):
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok===true')
        expect(page.locator('#query-engine-info')).to_contain_text(LOGICAL[:12])
        return page.evaluate('window.oswLastQueryResult')
    def route_query(**extra):
        return {'collection':'reference_routes','filters':[{'field':'current_id','op':'eq','value':short}],'limit':100,**extra}
    def selected_record(page,row):
        page.wait_for_function('id=>[...document.querySelectorAll("#query-detail details > pre")].some(n=>{try{return JSON.parse(n.textContent).id===id}catch{return false}})',arg=row['id'])
        values=page.locator('#query-detail details > pre').evaluate_all('(ns)=>ns.map(n=>{try{return JSON.parse(n.textContent)}catch{return null}}).filter(Boolean)')
        if values!=[row]:raise ValueError('Inspect did not retain the complete exact route record')
    def atlas_ready(page):
        page.wait_for_function('logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical',arg=LOGICAL)
        expect(page.locator('#route-atlas-preview')).to_be_visible()
        width_status=page.locator('#width-status').inner_text()
        if width_status.startswith('Width evidence unavailable:'):
            raise ValueError('Atlas width inventory adapter failed: '+width_status)
        expect(page.locator('#width-status')).to_contain_text('190 scoped width records for 94 of 111 current identities;')
        expect(page.locator('#width-rows > tr')).to_have_count(190)
        expect(page.locator('#width-decision-rows > tr')).to_have_count(111)
        bound=page.locator('#width-eacc-dekeyzer-2012-bell-cited-width-lower-bound > td').nth(1)
        expect(bound).to_contain_text('>160 km')
        expect(bound).to_contain_text('central width and upper limit unknown')
        expect(bound).not_to_contain_text('About 160')
        progress=page.evaluate('window.oswAtlasLoadStatus.worker_progress')
        if progress['phase']!='ready' or [r['phase'] for r in progress['completed_phases']]!=['runtime-files','packet-and-compile','instantiate','rust-load','workspace','metadata']:
            raise ValueError('Complete cold-load worker phase diagnostics missing')
        snapshot=page.evaluate('short=>({candidates:window.oswAtlasSnapshot.working_reference_routes.candidates.filter(r=>r.current_id===short),order:window.oswAtlasSnapshot.working_reference_routes.reference_route_length_order})',short)
        candidates=snapshot['candidates']
        if [r['id'] for r in candidates]!=[r['id'] for r in routes]:raise ValueError('Atlas lost one of the two distinct source phases')
        if any(r['id'] in snapshot['order'] for r in routes):raise ValueError('Regional reference entered whole-route ordering')
        return page.locator('#route-atlas-preview')
    def select_path(page,panel,row):
        button=panel.get_by_role('button',name=row['label'],exact=True)
        expect(button).to_be_visible();button.click();expect(button).to_have_attribute('aria-pressed','true')
        page.wait_for_function('id=>new URL(location.href).searchParams.get("atlas-route")===id',arg=row['id'])
        expect(panel.get_by_role('link',name='Full route card, measurements and sources ↓',exact=True)).to_have_attribute('href','#'+row['id'])
        expect(panel).to_contain_text('Studied reach only; this is not a whole-current length.')
        expect(panel).to_contain_text('State intersections have not been assessed')
        expect(panel).not_to_contain_text('undefined')
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            try:
                page=browser.new_page(viewport={'width':1100,'height':1000});page.set_default_timeout(240000);expect.set_options(timeout=240000)
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
                page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz','.mat','.csv')) else None)
                for width in [1100,320]:
                    suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1000})
                    page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(owner)+'&atlas-route='+routes[1]['id']+'#route-atlas')
                    panel=atlas_ready(page)
                    loads.append({'width':width,'cold_browser_context':not loads,'status':page.evaluate('window.oswAtlasLoadStatus')})
                    page.locator('#width-eacc-dekeyzer-2012-bell-cited-width-lower-bound').scroll_into_view_if_needed()
                    capture(page,'width-inventory-exclusive-bound'+suffix)
                    checks.append({'width':width,'case':'all 190 width records and 111 identities render; EACC remains an exclusive lower bound with no finite range'})
                    expect(panel.get_by_role('button',name=routes[1]['label'],exact=True)).to_have_attribute('aria-pressed','true')
                    for row in routes:
                        select_path(page,panel,row);no_overflow(page)
                        page.locator('#route-atlas-map').scroll_into_view_if_needed();capture(page,'atlas-'+row['phase']+suffix)
                        panel.get_by_role('link',name='Full route card, measurements and sources ↓',exact=True).click()
                        card=page.locator('[id="'+row['id']+'"]');expect(card).to_be_visible()
                        expect(card).to_contain_text('Studied reach only. Excluded from reference-route ordering above.')
                        expect(card.locator(':scope > h3')).to_contain_text(row['name'])
                        image=card.locator('img.route-map');image.scroll_into_view_if_needed()
                        page.wait_for_function('id=>{const n=document.getElementById(id)?.querySelector("img.route-map");return n?.complete&&n.naturalWidth>0}',arg=row['id'])
                        if width==320:
                            metrics=image.evaluate('n=>({source:n.currentSrc,width:n.getBoundingClientRect().width,naturalWidth:n.naturalWidth})')
                            if not metrics['source'].endswith('/figures/atlantic-nsec-regional-reference-reaches-compact-v1.svg'):raise ValueError('Narrow card did not select the compact source-bound figure')
                            metrics['minimum_text_px']=17*metrics['width']/360
                            if metrics['minimum_text_px']<11:raise ValueError('Compact route labels below 11px')
                            legibility.append(metrics)
                        capture(page,'route-card-'+row['phase']+suffix);no_overflow(page)
                        expect(card.locator('a[href="'+row['source_url']+'"]').first).to_be_attached()
                        card.get_by_role('link',name='Back to global current map ↑',exact=True).click()
                        expect(panel).to_be_visible()
                    checks.append({'width':width,'case':'cold direct fall route restored; distinct spring/fall tabs, global map and full map-card navigation; no ranking or physical-state promotion'})
                    result=query_page(page,route_query())
                    if result['total']!=2 or sorted(result['rows'],key=lambda r:r['id'])!=sorted(routes,key=lambda r:r['id']) or result['map_scene']['mapped_objects']!=2:raise ValueError('Query did not show both exact reference rows and marks')
                    expect(page.locator('#query-map-features .query-map-mark')).to_have_count(2)
                    page.locator('#query-map').scroll_into_view_if_needed();capture(page,'query-two-routes'+suffix)
                    for row in routes:
                        mark=page.locator('#query-map-features [data-entity="'+row['id']+'"]')
                        mark.focus();expect(page.locator('#query-map-hover')).to_contain_text(row['name']);mark.press('Enter');selected_record(page,row)
                    result=query_page(page,route_query(limit=1,offset=2))
                    if result['total']!=2 or result['rows']!=[] or result['map_scene']['mapped_objects']!=2:raise ValueError('Empty paginated table lost the matching route inventory')
                    mark=page.locator('#query-map-features [data-entity="'+routes[1]['id']+'"]');mark.focus();mark.press('Enter');selected_record(page,routes[1])
                    page.locator('#query-detail h3').first.scroll_into_view_if_needed();capture(page,'query-empty-page-inspect'+suffix);no_overflow(page)
                    checks.append({'width':width,'case':'both map marks expose names on focus and inspect complete rows; empty page retains both matching geometries'})
                    for row in routes:
                        path=row['source_file'];pointer=row['source_pointer'];expected=query.read(path)
                        for token in pointer.strip('/').split('/'):
                            token=token.replace('~1','/').replace('~0','~');expected=expected[int(token)] if isinstance(expected,list) else expected[token]
                        page.goto(base+'/almanac/query.html?source-q='+quote(json.dumps({'document':path,'pointer':pointer,'limit':500})))
                        page.wait_for_function('window.oswSourceQueryResult?.ok===true');source=page.evaluate('window.oswSourceQueryResult')
                        if source['source_sha256']!=sha(path) or {r['source_key']:r['record'] for r in source['rows']}!=expected:raise ValueError('Exact route source object or file hash differs')
                    page.locator('#source-query-results').first.scroll_into_view_if_needed();capture(page,'source-route-pointer'+suffix);no_overflow(page)
                    checks.append({'width':width,'case':'both source pointers resolve to exact retained prepared records with original document hash'})
                    page.goto(base+'/almanac/object.html?id='+quote(owner));page.wait_for_function('id=>window.oswObjectView?.id===id',arg=owner)
                    data=page.evaluate('window.oswObjectView')
                    if data['bundle_sha256']!=LOGICAL or data['collections']['route_decisions']!=[contract['final_decision']]:raise ValueError('Current card planning record differs')
                    link=page.get_by_role('link',name='Explore on the current atlas',exact=True);expect(link).to_be_visible();link.click();panel=atlas_ready(page);select_path(page,panel,routes[1])
                    checks.append({'width':width,'case':'canonical current card opens its map and both source-phase reference cards'})
                    page.goto(base+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.entries?.length>0')
                    rows=page.evaluate('window.oswDashboardSnapshot.snapshot.entries');selected=next(r for r in rows if r['id']==owner)
                    if selected['route_ids']!=contract['final_owner']['route_ids'] or selected['capabilities']['reference_route']!=2:raise ValueError('Dashboard route coverage differs')
                    page.locator('#dashboard-metric').select_option('reference_route');page.locator('#dashboard-type').select_option('named_current');page.locator('#dashboard-covered').check();page.locator('#dashboard-card-view').click();page.locator('#dashboard-search').fill(selected['label'])
                    page.wait_for_function('arg=>{const s=document.querySelector("#dashboard-status"),v=window.oswDashboardSelection;return s?.dataset.pending==="false"&&(s.textContent.startsWith("Selection failed:")||(v?.request.text===arg&&v.request.metric==="reference_route"&&v.request.covered_only===true))}',arg=selected['label'])
                    if page.locator('#dashboard-status').inner_text().startswith('Selection failed:'):raise ValueError('Dashboard selection failed')
                    tile=page.locator('.motion-card[data-id="'+owner+'"]');expect(tile).to_be_visible();expect(tile).to_have_class(__import__('re').compile(r'\blit\b'));expect(tile.locator('.selected-evidence')).to_contain_text('2 records')
                    tile.scroll_into_view_if_needed();capture(page,'dashboard-reference-coverage'+suffix);no_overflow(page)
                    tile.locator('details > summary').first.click();tile.get_by_role('link',name=routes[1]['label'],exact=True).click();page.wait_for_function('window.oswLastQueryResult?.ok===true')
                    if page.evaluate('window.oswLastQueryResult.rows')!=[routes[1]]:raise ValueError('Dashboard evidence link did not open the selected phase')
                    selected_record(page,routes[1]);checks.append({'width':width,'case':'reference metric lights the current card and its evidence link opens the exact fall route and Inspect record'})
                    page.goto(base+'/almanac/seasons.html?current='+short)
                    page.wait_for_function('arg=>window.oswSeasonSnapshot?.bundle_sha256===arg.logical&&document.querySelector("#season-current").value===arg.current',arg={'logical':LOGICAL,'current':short})
                    expect(page.locator('#season-play')).to_be_disabled();no_overflow(page)
                    checks.append({'width':width,'case':'two climatological schematics do not enable monthly physical playback'})
                    result=query_page(page,{'collection':'reference_routes','filters':[{'field':'current_id','op':'eq','value':'south-equatorial'}],'limit':100})
                    if result['total']!=0 or result['map_scene']['mapped_objects']!=0:raise ValueError('Parent family inherited member reference geometry')
                    checks.append({'width':width,'case':'parent family has no inherited route rows or map marks'})
                # Run after the cold atlas checks, so negative fixtures cannot
                # warm the binary before the real cold-entry observation.
                manifest=read('almanac/query-engine.manifest.json')
                fixtures=[('wrong-schema',b'{"schema":"unsupported","manifest":{},"collections":{"objects":[]}}','Unsupported bundle schema'),
                    ('malformed-json',b'{"schema":"osw.query-bundle.v1","manifest":{},"collections":','Invalid bundle JSON'),
                    ('invalid-utf8',b'{"schema":"osw.query-bundle.v1","manifest":{},"collections":{},"bad":"\xff"}','Invalid bundle JSON')]
                for label,body,error in fixtures:
                    pin=hashlib.sha256(body).hexdigest();part='query-parts/000000-'+pin+'.bin'
                    packet={'schema':'osw.query-packet.v1','logical_schema':'osw.query-bundle.v1','hash_algorithm':'sha256',
                        'part_byte_limit':16*1024*1024,'logical_sha256':pin,'logical_byte_length':len(body),
                        'parts':[{'index':0,'path':part,'sha256':pin,'byte_length':len(body)}]}
                    raw=json.dumps(packet).encode();fixture_manifest=json.loads(json.dumps(manifest))
                    fixture_manifest['sha256'].update({'almanac/query-data.json':hashlib.sha256(raw).hexdigest(),'almanac/'+part:pin})
                    routes_to_remove=[]
                    def intercept(pattern,handler):page.route(pattern,handler);routes_to_remove.append((pattern,handler))
                    intercept('**/query-engine.manifest.json',lambda r:r.fulfill(json=fixture_manifest))
                    intercept('**/query-data.json',lambda r:r.fulfill(body=raw,content_type='application/json'))
                    intercept('**/'+part,lambda r:r.fulfill(body=body,content_type='application/octet-stream'))
                    try:
                        page.goto(base+'/almanac/query.html')
                        page.wait_for_function('wanted=>document.querySelector("#query-status")?.textContent.includes(wanted)',arg=error)
                        if page.evaluate('!!window.oswLastQueryResult'):raise ValueError('Malformed source produced a successful query')
                        page.locator('#query-status').scroll_into_view_if_needed();capture(page,'rust-refuses-'+label)
                        checks.append({'width':320,'case':'Hash-valid '+label+' is refused by the unchanged Rust parser before engine load success','expected_error':error})
                    finally:
                        for pattern,handler in routes_to_remove:page.unroute(pattern,handler)
                if errors or missing or originals:raise ValueError('Page errors, missing assets or original scientific downloads')
            except Exception:
                page.screenshot(path=str(OUT/'browser-failure.png'))
                write(OUT/'browser-failure-state.json',page.evaluate('()=>({url:location.href,atlasLoad:window.oswAtlasLoadStatus??null,widthStatus:document.querySelector("#width-status")?.textContent,body:document.body.innerText.slice(0,9000)})'))
                raise
            finally:browser.close()
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility,'atlas_load_observations':loads,'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals});raise
    finally:server.shutdown();server.server_close()



def bind_client_manifest(original_raw,apply_binding=True):
    if not apply_binding:return original_raw,[]
    import atlantic_nsec_client_transport_manifest_v1 as transport_binding
    final_raw=(ROOT/transport_binding.FILE).read_bytes()
    expected=transport_binding.overlay(original_raw,{p:sha(p) for p in sorted(transport_binding.PATHS)})
    if json.loads(final_raw)!=expected:raise ValueError('Client transport binding differs from the exact saved engine')
    return final_raw,sorted(transport_binding.PATHS)

def main(*,apply_client_transport_binding=True):
    pref=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    files=saved_files(read(SAVED+'result.json'));extract_saved(files)
    if sha('almanac/query-engine.manifest.json')!=MANIFEST or read('almanac/query-engine.manifest.json')!=read(SAVED+'engine-manifest.json'):
        raise ValueError('Saved engine manifest differs')
    # A rebuilt engine can already bind every reviewed client asset. Preserve
    # its verified bytes when an older saved-engine overlay is not needed.
    final_raw,client_updates=bind_client_manifest((ROOT/'almanac/query-engine.manifest.json').read_bytes(),apply_client_transport_binding)
    files={p:dict(row) for p,row in files.items()}
    files['almanac/query-engine.manifest.json']={'sha256':hashlib.sha256(final_raw).hexdigest(),'bytes':len(final_raw)}
    (ROOT/'almanac/query-engine.manifest.json').write_bytes(final_raw)
    (OUT/'engine-manifest.json').write_bytes(final_raw)
    for group in ('rust_source_sha256','compile_time_data_sha256'):
        for path,pin in read(SAVED+'compile-inventory.json')[group].items():
            if sha(path)!=pin:raise ValueError('Saved compiler input differs: '+path)
    manifest=read('almanac/query-engine.manifest.json')
    for path,pin in pref['presentation_sha256'].items():
        if sha(path)!=pin or manifest['sha256'].get(path)!=pin:raise ValueError('Presentation differs from saved engine: '+path)
    observed=browser_review()
    for path,row in files.items():
        if sha(path)!=row['sha256']:raise ValueError('Browser changed saved engine file: '+path)
    write(OUT/'result.json',{'schema':'osw.atlantic-nsec-reference-browser-result.v1','status':observed['status'],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':SOURCE,'saved_engine_run':RUN,'saved_artifact':ARTIFACT,
        'logical_sha256':LOGICAL,'wasm_sha256':BINARY,'original_engine_manifest_sha256':MANIFEST,
        'engine_manifest_sha256':hashlib.sha256(final_raw).hexdigest(),'client_transport_updates':client_updates,
        'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})

if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise

