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
REQUEST='research/pacific-sec-gourdeau-2008-browser-request-v1.json'
PREFLIGHT='research/pacific-sec-gourdeau-2008-browser-preflight-v1.json'
SAVED='research/pacific-sec-gourdeau-2008-delivery-run-v2/'
OUT=ROOT/'.pytest_cache/pacific-sec-gourdeau-2008-browser-v1'
WORK=ROOT/'.pytest_cache/pacific-sec-gourdeau-2008-browser-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='354ec8b1be387e1b63b153ef38986be3adff759b'
RUN=41029501373
ARTIFACT={'id':12966141942,'bytes':99115745,'sha256':'0d53e557e3d8be582f76aca2d1b444056b9e74d43456d34dd0f1999c495673b7'}
OWNER='current:pacific-south-equatorial'
LOGICAL='7b4b5133c915102014f93a6d838e62201b0169e1b183b1d4beae65e01972bccf'
BINARY='3308ad25494a4ea1f35a18608481a4db9fe727856e87604a048fac1fbed92a21'
MANIFEST='59ffdc89571f4e589646f029b3cbb512952e813c1001d5fe1c49f937549faa37'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_PACIFIC_SEC_JET_WIDTHS_BROWSER_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.pacific-sec-jet-widths-browser-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    import pacific_sec_jet_widths_query_v1 as query
    contract=query.build_contract();owners=query.OWNERS
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
        expect(panel.locator('[data-dimension-width-id]')).to_have_count(len(expected))
        for row in expected:
            card=panel.locator('[data-dimension-width-id="'+row['id']+'"]')
            expect(card).to_contain_text('About '+format(row['approximate_width_km'],'g')+' km')
            expect(card).to_contain_text(row['phase_label'])
            expect(card).to_contain_text(row['component_label'])
            expect(card).to_contain_text(row['vertical_scope'])
            expect(card).to_contain_text('Nonsynoptic campaign')
            expect(card).not_to_contain_text('undefined')
            expect(card).to_contain_text('Seasonal width range: Unknown. Numerical uncertainty: Unknown.')
            if row.get('source_discrepancy_note'):expect(card).to_contain_text('Source discrepancy: '+row['source_discrepancy_note'])
            metrics=card.locator('p,h4,button,a').evaluate_all("""nodes=>nodes.filter(n=>n.getClientRects().length).map(n=>{const r=n.getBoundingClientRect(),b=n.closest('article').getBoundingClientRect();return {text:n.textContent,font:parseFloat(getComputedStyle(n).fontSize),inside:r.left>=b.left-2&&r.right<=b.right+2};})""")
            if any(m['font']<11 or not m['inside'] for m in metrics):raise ValueError('Width card text clipped or undersized')
            legibility.append({'id':row['id'],'minimum_font_px':min(m['font'] for m in metrics),'all_text_inside_card':True})
        expect(panel.locator('[data-flow-event-id]')).to_have_count(0)
    def current_widths(owner):
        return contract['prior_owners'][owner]['widths']+[r for r in contract['width_records'] if query.owns(r,owner)]
    def query_page(page,owner,limit=100,offset=0):
        request={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner.removeprefix('current:')}],'limit':limit,'offset':offset}
        page.goto(base+'/almanac/query.html?q='+quote(json.dumps(request)))
        page.wait_for_function('window.oswLastQueryResult?.ok === true')
        expect(page.locator('#query-engine-info')).to_contain_text(LOGICAL[:12])
        return page.locator('#query-chart-panels .current-dimension-evidence'),page.evaluate('window.oswLastQueryResult')
    def source_page(page,doc,pointer=''):
        page.goto(base+'/almanac/query.html?source-q='+quote(json.dumps({'document':doc,'pointer':pointer,'limit':500})))
        page.wait_for_function('window.oswSourceQueryResult?.ok === true')
        result=page.evaluate('window.oswSourceQueryResult')
        if result['source_sha256']!=sha(doc):raise ValueError('Indexed source hash differs')
        return result
    from contextlib import contextmanager
    @contextmanager
    def observed_page():
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':1000});page.set_default_timeout(180000)
            expect.set_options(timeout=180000)
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
                for owner in (OWNER,):
                    panel,result=query_page(page,owner);expected=current_widths(owner)
                    if result['total']!=2 or len(result['rows'])!=2:raise ValueError('Regional query inventory differs')
                    expect(panel).to_be_visible();cards(panel,expected)
                    for row in contract['width_records']:
                        if query.owns(row,owner):capture(panel.locator('[data-dimension-width-id="'+row['id']+'"]'),'query-'+row['id'].split('-')[-4]+suffix)
                    no_overflow(page)
                checks.append({'width':width,'case':'two reported component widths, campaign/layer scope and unknown bounds'})
                panel,result=query_page(page,OWNER,limit=1,offset=1)
                if result['total']!=2 or len(result['rows'])!=1:raise ValueError('Paginated inventory differs')
                cards(panel,current_widths(OWNER))
                button=panel.locator('[data-dimension-width-id="'+contract['width_records'][0]['id']+'"]').get_by_role('button',name='Inspect width record',exact=True)
                button.click();expect(page.locator('#query-detail')).to_contain_text(contract['width_records'][0]['id'])
                page.wait_for_function('id=>[...document.querySelectorAll("#query-detail details > pre")].some(n=>{try{return JSON.parse(n.textContent).id===id}catch{return false}})',arg=contract['width_records'][0]['id'])
                inspected=page.locator('#query-detail details > pre').evaluate_all('(nodes)=>nodes.map(n=>{try{return JSON.parse(n.textContent)}catch{return null}}).filter(Boolean)')
                if inspected!=[contract['width_records'][0]]:raise ValueError('Inspect did not retain the complete admitted width record')
                capture(page.locator('#query-detail h3').first,'record-inspect'+suffix)
                panel,result=query_page(page,'current:south-equatorial')
                if result['total']!=0 or result['chart_scene'] is not None:raise ValueError('Basin widths inherited by family')
                expect(page.locator('#query-chart-panels .current-dimension-evidence')).to_have_count(0)
                checks.append({'width':width,'case':'pagination retains all matching chart records, Inspect, no family inheritance'})
                doc='research/pacific-sec-gourdeau-2008-width-source-facts-v1.json'
                pointer=contract['width_records'][0]['source_pointer']
                result=source_page(page,doc,pointer)
                expected=query.read(doc)['width_candidates'][0]
                if {r['source_key']:r['record'] for r in result['rows']}!=expected:raise ValueError('Exact source object pointer differs')
                capture(page.locator('#source-query-results').first,'source-pointer'+suffix)
                no_overflow(page)
                checks.append({'width':width,'case':'indexed source facts and exact component object pointer'})
                for owner in owners:
                    page.goto(base+'/almanac/object.html?id='+quote(owner))
                    page.wait_for_function('owner=>window.oswObjectView?.id === owner',arg=owner)
                    if page.evaluate('window.oswObjectView.bundle_sha256')!=LOGICAL:raise ValueError('Current card engine identity differs')
                    panel=page.locator('#identity .current-dimension-evidence');expect(panel).to_be_visible();cards(panel,current_widths(owner))
                    for number in range(2):capture(panel.locator('[data-dimension-width-id]').nth(number),'card-'+str(number)+suffix)
                    no_overflow(page)
                page.goto(base+'/almanac/object.html?id=current%3Asouth-equatorial')
                page.wait_for_function('window.oswObjectView?.id === "current:south-equatorial"')
                expect(page.locator('#identity .current-dimension-evidence')).to_have_count(0)
                checks.append({'width':width,'case':'two current-card summaries and unchanged family separation'})
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'#route-atlas')
                page.wait_for_function('logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical',arg=LOGICAL)
                panel=page.locator('#route-atlas-preview .current-dimension-evidence');expect(panel).to_be_visible()
                panel.locator('summary').click();cards(panel,current_widths(OWNER))
                for number in range(2):capture(panel.locator('[data-dimension-width-id]').nth(number),'atlas-context-'+str(number)+suffix)
                no_overflow(page)
                checks.append({'width':width,'case':'global atlas selection opens regional jet context without invented geometry'})
                page.goto(base+'/almanac/seasons.html?current=pacific-south-equatorial')
                page.wait_for_function('logical=>window.oswSeasonSnapshot?.bundle_sha256===logical&&document.querySelector("#season-current").value==="pacific-south-equatorial"',arg=LOGICAL)
                panel=page.locator('#published-section-transports .current-dimension-evidence');expect(panel).to_be_visible();cards(panel,current_widths(OWNER))
                expect(page.locator('#season-play')).to_be_disabled()
                for number in range(2):capture(panel.locator('[data-dimension-width-id]').nth(number),'seasons-static-context-'+str(number)+suffix)
                no_overflow(page)
                checks.append({'width':width,'case':'seasonal page keeps nonsynoptic campaign evidence static and annual bounds unknown'})
                page.goto(base+'/almanac/dashboard.html')
                page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.entries?.length>0')
                snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                if sum(r.get('type')=='named_current' and r['capabilities'].get('scoped_width',0)>0 for r in snapshot['entries'])!=93:raise ValueError('Dashboard current width coverage differs')
                page.locator('#dashboard-metric').select_option('scoped_width');page.locator('#dashboard-type').select_option('named_current')
                page.locator('#dashboard-card-view').click()
                page.locator('#dashboard-search').fill('Pacific South Equatorial Current')
                page.wait_for_function("""text=>{const status=document.querySelector('#dashboard-status'),selection=window.oswDashboardSelection;return status?.dataset.pending==='false'&&(status.textContent.startsWith('Selection failed:')||(selection?.request.text===text&&selection.request.metric==='scoped_width'&&selection.request.record_type==='named_current'));}""",arg='Pacific South Equatorial Current')
                status=page.locator('#dashboard-status').inner_text()
                if status.startswith('Selection failed:'):raise ValueError(status)
                write(OUT/('dashboard-state'+suffix+'.json'),page.evaluate("""()=>({status:document.querySelector('#dashboard-status').textContent,request:window.oswDashboardSelection.request,ids:window.oswDashboardSelection.result.ids})"""))
                card=page.locator('.motion-card[data-id="'+OWNER+'"]');expect(card).to_be_visible();expect(card).to_have_class(__import__('re').compile(r'\blit\b'))
                expect(card.locator('.selected-evidence')).to_contain_text('2')
                capture(card,'dashboard-width-light'+suffix);no_overflow(page)
                card.locator('details > summary').first.click()
                card.get_by_role('link',name='Published regional jet widths and original source',exact=True).click()
                page.wait_for_function('window.oswLastQueryResult?.ok === true')
                if page.evaluate('window.oswLastQueryResult.total')!=2:raise ValueError('Dashboard evidence navigation differs')
                checks.append({'width':width,'case':'93 covered current identities, two-record lit card and direct evidence navigation'})
        if errors or missing or originals:raise ValueError('Page error, missing asset or original science download')
        result={'status':'PASS_BROWSER_OBSERVATION_VISUAL_REVIEW_PENDING','checks':checks,'screenshots':captures,
            'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility,
            'viewports':[1100,320],'one_page_and_renderer':True,'visual_review_complete':False}
        write(OUT/'browser.json',result);return result
    except Exception as error:
        write(OUT/'browser-failure.json',{'status':'FAIL','error':str(error)[:4000],'checks':checks,'screenshots':captures,
            'page_errors':errors,'missing_assets':missing,'original_science_downloads':originals,'legibility':legibility})
        try:page.screenshot(path=str(OUT/'browser-failure.png'))
        except Exception:pass
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
    write(OUT/'result.json',{'schema':'osw.pacific-sec-jet-widths-browser-result.v1','status':observed['status'],
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

