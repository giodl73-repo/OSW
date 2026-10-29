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
REQUEST='research/dimoune-2023-width-browser-request-v1.json'
PREFLIGHT='research/dimoune-2023-width-browser-preflight-v1.json'
SAVED='research/dimoune-2023-width-delivery-run-v1/'
OUT=ROOT/'.pytest_cache/dimoune-2023-width-browser-v1'
WORK=ROOT/'.pytest_cache/dimoune-2023-width-browser-work-v1'
REPO='repos/giodl73-repo/OSW'
SOURCE='8976b4b029ff9c2636eebfba7ad6acf360f9e7f9'
RUN=40936955911
ARTIFACT={'id':12924779550,'bytes':98845920,'sha256':'d21a413cef309a477ad705fc5c4721d85c14dbe49c434ffbe5cbb3534adfe4b5'}
OWNER='current:atlantic-south-equatorial'
LOGICAL='32b836f1015a96a5a281e082343bba81c73e2141c1f5ee438228c63f21f42607'
BINARY='628fd63dd68979d4baa168cb65b105387f9f60acae4e06ed7e57718c62621682'
MANIFEST='17a45d20ac53cd91d729cec4522afa98fa3513fc4fc6073eb08ed45254e7e20a'
def read(path):return json.loads((ROOT/path).read_bytes())
def sha(path):
    with (ROOT/path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
def api(path):return json.loads(subprocess.check_output(['gh','api',REPO+path],timeout=55))

def controls():
    if (os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REPOSITORY')!='giodl73-repo/OSW'
        or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps' or os.environ.get('OSW_DIMOUNE_WIDTH_BROWSER_V1')!='1'):
        raise ValueError('Scoped cloud saved-engine browser only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='1':raise ValueError('One worker required')
    request=read(REQUEST)
    if request.get('schema')!='osw.dimoune-2023-width-browser-request.v1' or request.get('execute') is not True or request['preflight_sha256']!=sha(PREFLIGHT) or request.get('max_cloud_jobs')!=1 or request.get('max_heavy_local_jobs')!=0:raise ValueError('Disabled or changed browser request')
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
    import dimoune_2023_width_query_v1 as query
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
            expect(card).to_contain_text('About '+str(row['approximate_width_km'])+' km')
            expect(card).to_contain_text('1993-01 to 2017-12')
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
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(args=['--renderer-process-limit=1'])
            page=browser.new_page(viewport={'width':1100,'height':1000});page.set_default_timeout(180000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:missing.append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 and not r.url.endswith('/favicon.ico') else None)
            page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz','.mat','.csv')) else None)
            for width in (1100,320):
                suffix='-'+str(width)+'px';page.set_viewport_size({'width':width,'height':1000})
                for owner in (OWNER,'current:north-brazil'):
                    panel,result=query_page(page,owner);expected=current_widths(owner)
                    if result['total']!=4 or len(result['rows'])!=4:raise ValueError('Regional query inventory differs')
                    expect(panel).to_be_visible();cards(panel,expected)
                    for row in contract['width_records']:
                        if query.owns(row,owner):capture(panel.locator('[data-dimension-width-id="'+row['id']+'"]'),'query-'+row['mean_section_context']['source_flow_label'].lower()+suffix)
                    no_overflow(page)
                checks.append({'width':width,'case':'six additions, two mean-section owner queries, period/discrepancy/unknown bounds'})
                panel,result=query_page(page,OWNER,limit=1,offset=1)
                if result['total']!=4 or len(result['rows'])!=1:raise ValueError('Paginated inventory differs')
                cards(panel,current_widths(OWNER))
                button=panel.locator('[data-dimension-width-id="'+contract['width_records'][2]['id']+'"]').get_by_role('button',name='Inspect width record',exact=True)
                button.click();expect(page.locator('#query-detail')).to_contain_text(contract['width_records'][2]['id'])
                capture(page.locator('#query-detail h3').first,'record-inspect'+suffix)
                panel,result=query_page(page,'current:south-equatorial')
                if result['total']!=0 or result['chart_scene'] is not None:raise ValueError('Basin widths inherited by family')
                expect(page.locator('#query-chart-panels .current-dimension-evidence')).to_have_count(0)
                checks.append({'width':width,'case':'pagination retains all matching chart records, Inspect, no family inheritance'})
                doc='research/dimoune-2023-section-width-records-prepared-v1.json'
                pointer=contract['width_records'][4]['source_pointer']
                result=source_page(page,doc,pointer)
                expected=next(r for r in query.read(doc)['records'] if r['id']==contract['width_records'][4]['id'])
                if {r['source_key']:r['record'] for r in result['rows']}!=expected:raise ValueError('Exact source pointer differs')
                capture(page.locator('#source-query-results').first,'source-pointer'+suffix)
                no_overflow(page)
                checks.append({'width':width,'case':'indexed original table transcription and exact record pointer'})
                for owner in owners:
                    page.goto(base+'/almanac/object.html?id='+quote(owner))
                    page.wait_for_function('owner=>window.oswObjectView?.id === owner',arg=owner)
                    if page.evaluate('window.oswObjectView.bundle_sha256')!=LOGICAL:raise ValueError('Current card engine identity differs')
                    panel=page.locator('#identity .current-dimension-evidence');expect(panel).to_be_visible();cards(panel,current_widths(owner))
                    capture(panel.locator('[data-dimension-width-id]').first,'card-'+owner.removeprefix('current:')+suffix);no_overflow(page)
                page.goto(base+'/almanac/object.html?id=current%3Asouth-equatorial')
                page.wait_for_function('window.oswObjectView?.id === "current:south-equatorial"')
                expect(page.locator('#identity .current-dimension-evidence')).to_have_count(0)
                checks.append({'width':width,'case':'four current cards, five preserved widths and family separation'})
                page.goto(base+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature='+quote(OWNER)+'#route-atlas')
                page.wait_for_function('logical=>typeof window.restoreReferenceRouteAtlas==="function"&&window.oswAtlasSnapshot?.bundle_sha256===logical',arg=LOGICAL)
                panel=page.locator('#route-atlas-preview .current-dimension-evidence');expect(panel).to_be_visible()
                panel.locator('summary').click();cards(panel,current_widths(OWNER))
                capture(panel.locator('[data-dimension-width-id]').first,'atlas-section-context'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'global atlas selection opens mean-section context without invented geometry'})
                page.goto(base+'/almanac/seasons.html?current=atlantic-south-equatorial')
                page.wait_for_function('logical=>window.oswSeasonSnapshot?.bundle_sha256===logical&&document.querySelector("#season-current").value==="atlantic-south-equatorial"',arg=LOGICAL)
                panel=page.locator('#published-section-transports .current-dimension-evidence');expect(panel).to_be_visible();cards(panel,current_widths(OWNER))
                expect(page.locator('#season-play')).to_be_disabled()
                capture(panel.locator('[data-dimension-width-id]').first,'seasons-static-mean-context'+suffix);no_overflow(page)
                checks.append({'width':width,'case':'seasonal page keeps 25-year mean context static and annual bounds unknown'})
                page.goto(base+'/almanac/dashboard.html')
                page.wait_for_function('window.oswDashboardSnapshot?.snapshot?.entries?.length>0')
                snapshot=page.evaluate('window.oswDashboardSnapshot.snapshot')
                if sum(r.get('type')=='named_current' and r['capabilities'].get('scoped_width',0)>0 for r in snapshot['entries'])!=91:raise ValueError('Dashboard current width coverage differs')
                page.locator('#dashboard-metric').select_option('scoped_width');page.locator('#dashboard-type').select_option('named_current')
                page.locator('#dashboard-search').fill('Atlantic South Equatorial Current')
                card=page.locator('.motion-card[data-id="'+OWNER+'"]');expect(card).to_be_visible();expect(card).to_have_class(__import__('re').compile(r'\blit\b'))
                expect(card.locator('.selected-evidence')).to_contain_text('4')
                capture(card,'dashboard-width-light'+suffix);no_overflow(page)
                card.locator('details > summary').first.click()
                card.get_by_role('link',name='Published mean section widths and original source',exact=True).click()
                page.wait_for_function('window.oswLastQueryResult?.ok === true')
                if page.evaluate('window.oswLastQueryResult.total')!=4:raise ValueError('Dashboard evidence navigation differs')
                checks.append({'width':width,'case':'91 covered current identities, four-record lit card and direct evidence navigation'})
            browser.close()
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
    from dimoune_2023_width_presentation_v1 import presentation_manifest
    scope=read('research/dimoune-2023-width-presentation-scope-v1.json')
    for path,row in scope['source_changes'].items():
        if sha(path)!=row['candidate_sha256'] or sha(row['archive_path'])!=row['parent_sha256']:
            raise ValueError('Display source custody differs: '+path)
    overlay=presentation_manifest((ROOT/'almanac/query-engine.manifest.json').read_bytes(),scope,os.environ['GITHUB_SHA'])
    write(ROOT/'almanac/query-engine.manifest.json',overlay);write(OUT/'engine-manifest-presentation.json',overlay)
    for group in ('rust_source_sha256','compile_time_data_sha256'):
        for path,pin in read(SAVED+'compile-inventory.json')[group].items():
            if sha(path)!=pin:raise ValueError('Saved compiler input differs: '+path)
    manifest=read('almanac/query-engine.manifest.json')
    for path,pin in pref['presentation_sha256'].items():
        if sha(path)!=pin or manifest['sha256'].get(path)!=pin:raise ValueError('Presentation differs from saved engine: '+path)
    observed=browser_review()
    for path,row in files.items():
        if path!='almanac/query-engine.manifest.json' and sha(path)!=row['sha256']:raise ValueError('Browser changed saved engine file: '+path)
    if read('almanac/query-engine.manifest.json')!=overlay:raise ValueError('Browser changed scoped display manifest')
    write(OUT/'result.json',{'schema':'osw.dimoune-2023-width-browser-result.v1','status':observed['status'],
        'source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],
        'saved_engine_source':SOURCE,'saved_engine_run':RUN,'saved_artifact':ARTIFACT,
        'logical_sha256':LOGICAL,'wasm_sha256':BINARY,'parent_engine_manifest_sha256':MANIFEST,
        'presentation_manifest_sha256':sha(OUT/'engine-manifest-presentation.json'),
        'screenshots':len(observed['screenshots']),'browser_checks':len(observed['checks']),
        'native_or_wasm_rebuild':False,'visual_review_complete':False,'installed':False,'main_updated':False,'full_goal_complete':False})

if __name__=='__main__':
    try:main()
    except Exception as error:
        if os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true':
            OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error':str(error)[:4000]})
        raise

