"""Cloud-only read-only comparison of frozen scientific outputs and a Linux replay."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/chen-indian-sec-replay-diagnostic-request-v1.json'
PREFLIGHT='research/chen-indian-sec-replay-diagnostic-preflight-v1.json'
OUT=ROOT/'.pytest_cache/chen-indian-sec-replay-diagnostic-v1'
def read(p):return json.loads((ROOT/p).read_bytes())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def controls():
    if os.name!='posix' or os.environ.get('GITHUB_ACTIONS')!='true' or os.environ.get('GITHUB_REF')!='refs/heads/codex/current-measurement-gaps':raise ValueError('Cloud diagnostic only')
    if len(os.sched_getaffinity(0))!=1 or os.getpriority(os.PRIO_PROCESS,0)<15:raise ValueError('One CPU and nice15 required')
    r=read(REQUEST)
    if r.get('schema')!='osw.chen-indian-sec-replay-diagnostic-request.v1' or r.get('execute') is not True or r.get('cloud_compact_replay_diagnostic_permitted') is not True:raise ValueError('Disabled request')
    for key in ['parent_packet_read_permitted','native_build_permitted','wasm_build_permitted','index_load_permitted','ocean_field_processing_permitted','browser_permitted','installation_permitted','local_bulk_sync_permitted','main_merge_permitted']:
        if r.get(key) is not False:raise ValueError('Unrelated operation enabled: '+key)
    if sha(PREFLIGHT)!=r['preflight_sha256']:raise ValueError('Changed freeze')
    p=read(PREFLIGHT)
    for path,h in p['input_sha256'].items():
        if sha(path)!=h:raise ValueError('Changed input: '+path)
    for path in p['disabled_requests']:
        value=read(path)
        if value.get('execute',value.get('execution_permitted')) is not False:raise ValueError('Older request enabled')
    if read('research/current-gap-delivery-phase.json')['heavy_work_permitted'] is not False:raise ValueError('Broad work enabled')
    if subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD']).decode().strip()!=os.environ['GITHUB_SHA'] or subprocess.check_output(['git','-c','core.fsmonitor=false','status','--porcelain']).strip():raise ValueError('Clean exact source checkout required')

def differences(a,b,path=''):
    if type(a)!=type(b):return [{'pointer':path,'kind':'type','expected_type':type(a).__name__,'actual_type':type(b).__name__}]
    if isinstance(a,dict):
        if set(a)!=set(b):return [{'pointer':path,'kind':'keys','expected':sorted(a),'actual':sorted(b)}]
        return [d for k in a for d in differences(a[k],b[k],path+'/'+str(k))]
    if isinstance(a,list):
        if len(a)!=len(b):return [{'pointer':path,'kind':'length','expected':len(a),'actual':len(b)}]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,path+'/'+str(i))]
    if a==b:return []
    return [{'pointer':path,'kind':'numeric' if isinstance(a,(float,int)) and not isinstance(a,bool) else 'scalar','expected':a,'actual':b,**({'absolute_difference':abs(a-b)} if isinstance(a,(float,int)) and not isinstance(a,bool) else {})}]

def run():
    controls()
    import chen_indian_sec_regional_ridge_lengths_v1 as science
    import pyproj
    expected=read(science.FILE);actual=science.build();delta=differences(expected,actual)
    actual_bytes=(json.dumps(actual,indent=2)+'\n').encode();figure=science.figure(actual).encode();prior=(ROOT/science.FIGURE).read_bytes()
    changed=list(difflib.unified_diff(prior.decode().splitlines(),figure.decode().splitlines(),n=1))
    report={'schema':'osw.chen-indian-sec-replay-diagnostic-result.v1','status':'DIAGNOSTIC_COMPLETE_NO_ADMISSION','source_commit':os.environ['GITHUB_SHA'],'run_id':os.environ['GITHUB_RUN_ID'],'run_attempt':os.environ['GITHUB_RUN_ATTEMPT'],'pyproj_version':pyproj.__version__,'proj_version':pyproj.proj_version_str,'report_byte_identical':(ROOT/science.FILE).read_bytes()==actual_bytes,'report_structurally_identical':expected==actual,'report_expected_sha256':sha(science.FILE),'report_replayed_sha256':hashlib.sha256(actual_bytes).hexdigest(),'report_difference_count':len(delta),'numeric_difference_count':sum(d['kind']=='numeric' for d in delta),'maximum_numeric_difference':max([d['absolute_difference'] for d in delta if d['kind']=='numeric'],default=0),'first_differences':delta[:50],'figure_byte_identical':prior==figure,'figure_expected_sha256':sha(science.FIGURE),'figure_replayed_sha256':hashlib.sha256(figure).hexdigest(),'figure_diff_line_count':len(changed),'first_figure_diff_lines':[line[:700] for line in changed[:24]],'request_sha256':sha(REQUEST),'preflight_sha256':sha(PREFLIGHT),'installed_packet_read':False,'native_wasm_built':False,'source_measurements_changed':False,'full_goal_complete':False}
    OUT.mkdir(parents=True,exist_ok=False);(OUT/'result.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report),flush=True)

if __name__=='__main__':run()
