"""Cloud-only native diagnostics for the exact saved Atlantic SEC candidate.

Temporary profiling instrumentation is restored byte-for-byte after compilation.
No production engine, data, source index, browser or installation is generated.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/current-store-load-profile-request-v1.json'
PREFLIGHT='research/current-store-load-profile-preflight-v1.json'
OUT=ROOT/'.pytest_cache/current-store-load-profile-v1'
WORK=ROOT/'.pytest_cache/current-store-load-profile-work-v1'
MAIN='19148702de6433253dbf412a0a28c0cb4f8e409e'

PROFILE_MODULE=r'''
use std::cell::RefCell;
use std::collections::BTreeMap;
use std::time::Instant;
#[derive(Default)]
struct State { depth: usize, stats: BTreeMap<&'static str,(u64,u128)> }
thread_local! { static STATE:RefCell<State>=RefCell::new(State::default()); }
pub struct Session { name:&'static str, started:Instant }
impl Session {
    pub fn new(name:&'static str)->Self {
        STATE.with(|s| {let mut s=s.borrow_mut();if s.depth==0 {s.stats.clear();}s.depth+=1;});
        Self{name,started:Instant::now()}
    }
}
impl Drop for Session {
    fn drop(&mut self) {
        STATE.with(|s| {let mut s=s.borrow_mut();s.depth-=1;if s.depth==0 {
            let spans=s.stats.iter().map(|(name,(calls,nanos))|serde_json::json!({"name":name,"calls":calls,"inclusive_nanos":nanos})).collect::<Vec<_>>();
            eprintln!("OSW_LOAD_PROFILE {}",serde_json::json!({"session":self.name,"elapsed_nanos":self.started.elapsed().as_nanos(),"spans":spans}));
        }});
    }
}
pub struct Span { name:&'static str, started:Instant }
impl Span {pub fn new(name:&'static str)->Self {Self{name,started:Instant::now()}}}
impl Drop for Span {
    fn drop(&mut self) {STATE.with(|s| {let mut s=s.borrow_mut();if s.depth>0 {let value=s.stats.entry(self.name).or_default();value.0+=1;value.1+=self.started.elapsed().as_nanos();}});}
}
'''

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def read(path):return json.loads((ROOT/path).read_bytes())
def write(path,value):Path(path).write_bytes((json.dumps(value,indent=2)+'\n').encode())
def require(value,message):
    if not value:raise ValueError(message)

def instrument_source(name,text):
    """Add timing only; all original statements and error propagation remain."""
    count=0
    if name=='lib.rs':
        require(text.count('pub fn load(bytes: &[u8]) -> Result<Self, String> {')==1,'Store load signature differs')
        text='mod load_profile;\n'+text
        text=text.replace('pub fn load(bytes: &[u8]) -> Result<Self, String> {','pub fn load(bytes: &[u8]) -> Result<Self, String> {\n        let _osw_profile_session=crate::load_profile::Session::new("Store::load");\n        let _osw_profile_parse=crate::load_profile::Span::new("load:parse");',1)
        needle='serde_json::from_slice(bytes).map_err(|e| format!("Invalid bundle JSON: {e}"))?;'
        require(text.count(needle)==1,'Store JSON parser differs')
        text=text.replace(needle,needle+'\n        drop(_osw_profile_parse);',1)
        needle='        let mut ids = BTreeMap::new();'
        require(text.count(needle)==1,'Store index creation differs')
        text=text.replace(needle,'        let _osw_profile_index=crate::load_profile::Span::new("load:index");\n'+needle,1)
        first='        pacific_nec_product_axes::validate(&bundle)?;'
        require(text.count(first)==1,'Store validation boundary differs')
        text=text.replace(first,'        drop(_osw_profile_index);\n'+first,1)
        pattern=r'(?m)^        ([a-z_]+)::([a-z_]+)\(([^\n]*)\)\?;$'
        def statement(match):
            nonlocal count
            count+=1
            return '        let _osw_profile_stage=crate::load_profile::Span::new("load:'+match[1]+'::'+match[2]+'");\n'+match[0]+'\n        drop(_osw_profile_stage);'
        text=re.sub(pattern,statement,text)
        require(count>=80,'Missing Store validation timing coverage')
        needle='        let spatial = spatial::Index::build(&bundle.collections)?;'
        require(text.count(needle)==1,'Store spatial index differs')
        text=text.replace(needle,'        let _osw_profile_spatial=crate::load_profile::Span::new("load:spatial-index");\n'+needle+'\n        drop(_osw_profile_spatial);',1)
        needle='    pub fn metadata(&self) -> Value {'
        require(text.count(needle)==1,'Store metadata signature differs')
        text=text.replace(needle,needle+'\n        let _osw_profile_session=crate::load_profile::Session::new("Store::metadata");\n        let _osw_profile_metadata=crate::load_profile::Span::new("metadata:total");',1)
    pattern=r'\bfn checked\s*\([^{}]*\)\s*(?:->[^{}]+)?\{'
    def checked(match):
        nonlocal count
        count+=1
        return match[0]+'\n    let _osw_profile_checked=crate::load_profile::Span::new("checked:'+Path(name).stem+'");'
    text=re.sub(pattern,checked,text)
    return text,count

def controls():
    # Refuse before payload reads, instrumentation, compiler use or networking.
    require(os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('RUNNER_OS')=='Linux'
        and os.environ.get('OSW_CURRENT_STORE_LOAD_PROFILE_V1')=='1','Scoped cloud profiling only')
    require(os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW' and os.environ.get('GITHUB_EVENT_NAME')=='push'
        and os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps','Wrong profile event')
    require(len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15,'One low-priority CPU required')
    for key in ['CARGO_BUILD_JOBS','RUST_TEST_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:require(os.environ.get(key)=='1','Worker bounds differ')
    request=read(REQUEST)
    require(request.get('schema')=='osw.current-store-load-profile-request.v1' and request.get('execute') is True
        and request['preflight_sha256']==sha(ROOT/PREFLIGHT),'Disabled or changed profile request')
    for key in ['cloud_saved_engine_read_permitted','native_profiling_build_permitted']:require(request.get(key) is True,'Missing permission')
    for key in ['wasm_build_permitted','browser_permitted','installation_permitted','ocean_field_processing_permitted','main_merge_permitted','local_bulk_sync_permitted']:require(request.get(key) is False,'Unrelated permission enabled')
    require(request.get('max_cloud_jobs')==1 and request.get('max_heavy_local_jobs')==0,'Job bounds differ')
    pref=read(PREFLIGHT)
    for path,pin in pref['input_sha256'].items():require(sha(ROOT/path)==pin,'Frozen profile input differs: '+path)
    for path in pref['disabled_requests']:
        value=read(path);require(value.get('execute',value.get('execution_permitted')) is False,'Another request enabled: '+path)
    for path,row in pref['installed_files'].items():require((ROOT/path).stat().st_size==row['bytes'] and sha(ROOT/path)==row['sha256'],'Installed parent differs')
    require(read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is False,'Broad processing enabled')
    import check_atlantic_nsec_reference_browser_v1 as saved
    head=subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],text=True).strip()
    require(head==os.environ['GITHUB_SHA'] and not subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip(),'Clean exact profile checkout required')
    require(saved.api('/git/ref/heads/main')['object']['sha']==MAIN and saved.api('/git/ref/heads/codex/current-measurement-gaps')['object']['sha']==head,'Remote source moved')
    return saved

def run():
    saved=controls();OUT.mkdir(parents=True,exist_ok=False);WORK.mkdir(parents=True,exist_ok=False)
    inventory=saved.read(saved.SAVED+'compile-inventory.json')
    for path,pin in inventory['rust_source_sha256'].items():require(sha(ROOT/path)==pin,'Saved Rust source differs: '+path)
    saved.WORK=WORK;saved.extract_saved(saved.saved_files(saved.read(saved.SAVED+'result.json')))
    # Generated compiled inputs (including the source-index catalog) belong to
    # the saved candidate, so verify them after its exact artifacts replace the
    # installed parent's files in this disposable cloud checkout.
    for path,pin in inventory['compile_time_data_sha256'].items():require(sha(ROOT/path)==pin,'Saved compiled data differs: '+path)
    descriptor=read('almanac/query-data.json');require(descriptor['logical_sha256']==saved.LOGICAL,'Saved logical identity differs')
    payload=WORK/'logical.json';logical=hashlib.sha256();total=0
    with payload.open('xb') as output:
        for part in descriptor['parts']:
            path=ROOT/'almanac'/part['path'];require(sha(path)==part['sha256'] and path.stat().st_size==part['byte_length'],'Saved part differs')
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(1048576),b''):output.write(block);logical.update(block);total+=len(block)
    require(total==195361434 and logical.hexdigest()==saved.LOGICAL,'Complete saved logical bytes differ')
    src=ROOT/'rust/osw-query/src';profile=src/'load_profile.rs';require(not profile.exists(),'Unexpected profiling source')
    originals={};changes={};injected=0
    try:
        for path in sorted(src.glob('*.rs')):
            raw=path.read_bytes();updated,count=instrument_source(path.name,raw.decode())
            if count:
                originals[path]=raw;path.write_bytes(updated.encode());changes[path.relative_to(ROOT).as_posix()]={'original_sha256':hashlib.sha256(raw).hexdigest(),'profile_sha256':sha(path),'timing_spans':count};injected+=count
        require('rust/osw-query/src/lib.rs' in changes and injected>=100,'Incomplete profiling instrumentation')
        profile.write_bytes(PROFILE_MODULE.encode())
        env={**os.environ,'RUSTUP_TOOLCHAIN':'1.95.0','CARGO_TARGET_DIR':str(WORK/'target'),'CARGO_INCREMENTAL':'0'}
        with (OUT/'native-profile-build.txt').open('wb') as log:
            subprocess.run(['cargo','build','--manifest-path','rust/osw-query/Cargo.toml','--locked','--release','--bin','osw-query-cli'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
    finally:
        for path,raw in originals.items():path.write_bytes(raw)
        if profile.exists():profile.unlink()
    require(all(path.read_bytes()==raw for path,raw in originals.items()),'Original Rust source restoration failed')
    started=time.monotonic()
    with (WORK/'metadata.json').open('wb') as output,(OUT/'native-profile-stderr.txt').open('wb') as errors:
        subprocess.run([str(WORK/'target/release/osw-query-cli'),str(payload)],stdout=output,stderr=errors,check=True,timeout=600)
    elapsed=time.monotonic()-started;metadata=json.loads((WORK/'metadata.json').read_bytes());require(metadata['ok'] is True and metadata['bundle_sha256']==saved.LOGICAL,'Profile did not load exact candidate')
    sessions=[json.loads(line.removeprefix('OSW_LOAD_PROFILE ')) for line in (OUT/'native-profile-stderr.txt').read_text().splitlines() if line.startswith('OSW_LOAD_PROFILE ')]
    require([r['session'] for r in sessions]==['Store::load','Store::metadata'],'Missing complete native profile sessions')
    require(all(r['elapsed_nanos']>0 and r['spans'] for r in sessions),'Empty profile')
    write(OUT/'profile.json',{'schema':'osw.current-store-load-profile.v1','sessions':sessions,'native_process_elapsed_seconds':elapsed,'instrumented_sources':changes,'profile_module_sha256':hashlib.sha256(PROFILE_MODULE.encode()).hexdigest(),'original_sources_restored':True,'timing_semantics':'Inclusive elapsed times overlap for nested calls; do not sum nested spans. Native timings locate repeated validation work and do not establish browser cold-load acceptance.'})
    write(OUT/'result.json',{'status':'PASS_SAVED_CANDIDATE_NATIVE_PROFILE_OBSERVATION','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'saved_engine_source':saved.SOURCE,'saved_engine_run':saved.RUN,'saved_engine_artifact':saved.ARTIFACT,'logical_sha256':saved.LOGICAL,'logical_bytes':total,'saved_wasm_sha256':saved.BINARY,'native_process_elapsed_seconds':elapsed,'profile_sha256':sha(OUT/'profile.json'),'metadata_bytes':(WORK/'metadata.json').stat().st_size,'metadata_sha256':sha(WORK/'metadata.json'),'original_sources_restored':True,'instrumented_build_is_diagnostic_only':True,'production_engine_generated':False,'wasm_rebuilt':False,'installed':False,'main_updated':False,'full_goal_complete':False})
    print('PASS exact saved candidate native profile; diagnostics only, no production engine or installation')

if __name__=='__main__':
    try:run()
    except Exception as error:
        if os.environ.get('GITHUB_ACTIONS')=='true':OUT.mkdir(parents=True,exist_ok=True);write(OUT/'failure.json',{'status':'FAIL','error_type':type(error).__name__,'message':str(error)[:1600],'installed':False,'main_updated':False})
        raise
