"""Admit six frozen P06 proxies and preserve three unresolved contexts."""
import hashlib,json,os,signal,socket,time
from pathlib import Path
import load_current_depth_reference_inventory_v31 as loader
from compiled_depth_catalog_query_guard_v1 import DescriptorQuery
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v31.json'
PREVIOUS='research/current-depth-reference-inventory-v30.json'
INVENTORY='research/current-depth-reference-inventory-v31.json'
ADDENDUM='research/current-depth-reference-addenda/p06-eac-native-uv-depths-v1.json'
CSV='research/current-depth-reference-addenda/p06-eac-native-uv-depths-v1.csv'
UNRESOLVED='research/p06-eac-native-uv-unresolved-reference-contexts-v1.json'
PRIOR_LEDGER='research/p06-eac-native-frame-depth-ledger-v2.json'

def numbers(v):
    if isinstance(v,dict):return sum(numbers(a) for a in v.values())
    if isinstance(v,list):return sum(numbers(a) for a in v)
    return int(type(v) in (int,float))

def build(out):
    read=lambda p:(ROOT/p).read_bytes()
    op=json.loads(read(OP))
    if any(op['eligibility'].values()):raise ValueError('No physical/seasonal/volume/runtime promotion')
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(read(p)).hexdigest()!=h:raise ValueError('Frozen dependency changed:'+p)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    def save_query(value):
        p=out/'catalog-query-ledger.json';tmp=p.with_suffix('.tmp');tmp.write_bytes(encode(value));os.replace(tmp,p)
    query=DescriptorQuery(save_query)
    guarded_reader=query.reader(read)
    def prior_query(raw,reader):
        with query.decoding():return loader.previous.load_inventory(json.loads(raw),query.reader(reader))
    source_raw=read(loader.SOURCE)
    if len(source_raw)>400000 or hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:raise ValueError('Exact bounded frozen P06 packet')
    source=json.loads(source_raw);prior=json.loads(read(PRIOR_LEDGER))
    if prior['numeric_metadata_values_including_reconstruction']!=1932 or prior['native_array_values_decoded']!=1064 or prior['provider_operations_remaining']!=0:
        raise ValueError('Original P06 cumulative counters required')
    previous_raw=read(PREVIOUS)
    before=prior_query(previous_raw,guarded_reader)
    piece=lambda p,raw:{'file':p,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':loader.SCHEMA,'id':'p06-eac-native-uv-depths-v1','source_result':piece(loader.SOURCE,source_raw),
        'operator_file':OP,'operator_sha256':hashlib.sha256(read(OP)).hexdigest(),
        'source_contexts':{loader.CONTEXT:loader.context()},'evidence':loader.references(source),
        'runtime_changed':False,'full_goal_complete':False}
    unresolved=loader.unresolved(source);after=loader.assemble(before,addendum,source)
    if after['evidence'][:-6]!=before['evidence']:raise ValueError('All 878 previous references preserved exactly')
    for k,v in before['source_contexts'].items():
        if after['source_contexts'][k]!=v:raise ValueError('Every previous context preserved')
    if after['counts']!={'identities':111,'depth_references':884,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':882}:
        raise ValueError('Six additive conditional references only')
    add_raw=encode(addendum);table=loader.reference_csv_bytes(addendum['evidence']);unresolved_raw=encode(unresolved)
    manifest={'schema':'osw.current-depth-reference-inventory.v31','status':'PINNED_REFERENCES_WITH_CONDITIONAL_P06_CAST_DEPTHS',
        'previous_inventory':piece(PREVIOUS,previous_raw),'reference_addendum':{'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,table)},
        'unresolved_contexts':piece(UNRESOLVED,unresolved_raw),'counts':after['counts'],
        'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
        'view_metadata':{'schema':'osw.current-depth-reference-view.v31','status':'SIX_CONDITIONAL_P06_REFERENCES_THREE_UNRESOLVED_CONTEXTS',
            'interpretation':'Six local cutoff proxies from two qualifying frames in a three-cast EAC-region winter cohort. Shallow-cast estimates remain unresolved; no physical bottom or seasonal range.',
            'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},
        'runtime_changed':False,'full_goal_complete':False}
    pieces={INVENTORY:encode(manifest),ADDENDUM:add_raw,CSV:table,UNRESOLVED:unresolved_raw}
    reads={loader.SOURCE:1,ADDENDUM:0,UNRESOLVED:0}
    def final_reader(p):
        if p in reads:reads[p]+=1
        return pieces[p] if p in pieces else read(p)
    final=loader.load_inventory(json.loads(pieces[INVENTORY]),final_reader,prior_query)
    if final['evidence']!=after['evidence'] or reads!={loader.SOURCE:2,ADDENDUM:1,UNRESOLVED:1}:raise ValueError('Full actual JSON/CSV/unresolved roundtrip')
    decoded=2*numbers(source)+numbers(prior)+numbers(op)+numbers(addendum)+numbers(unresolved)+numbers(manifest)
    metadata=prior['numeric_metadata_values_including_reconstruction']+decoded;scalars=metadata+prior['native_array_values_decoded']
    if metadata>10000 or scalars>250000:raise ValueError('Original P06 source allowance does not reset')
    ledger={'schema':'osw.p06-native-uv-reference-admission-ledger.v1','status':'SIX_REFERENCES_ADMITTED_THREE_CONTEXTS_EXPLICITLY_UNRESOLVED',
        'counts':after['counts'],'source_cast_profiles':3,'qualifying_reference_frames':2,'new_references':6,'unresolved_contexts':3,
        'new_provider_requests':0,'new_native_ocean_values_decoded':0,'p06_source_packet_reads':2,
        'p06_new_metadata_numbers':decoded,'p06_case_metadata_touch_bound':metadata,'p06_case_scalar_bound':scalars,
        'p06_prior_case_time_seconds':prior['case_time_charge_seconds'],
        'prior_catalog_query_scope':query.ledger['scope'],'prior_catalog_query_reserved_numeric_tokens':query.ledger['reserved_numeric_tokens'],
        'prior_catalog_query_unique_json_bytes':query.ledger['unique_json_bytes'],'prior_catalog_query_cache_hits':query.ledger['cache_hits'],
        'older_native_acquisition_budgets_renewed':False,'older_native_ocean_fields_reopened':False,
        'older_catalog_validation_scope':'frozen_compiled_reference_validation_under_descriptor_query_guard',
        'runtime_changed':False,'full_goal_complete':False}
    return pieces,ledger

def main():
    def stopped(*a):raise SystemExit('Stopped offline P06 admission; no replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No network/provider access'))
    start=float(os.environ['OSW_P06_ADMISSION_PHASE_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer phase clock')
    signal.alarm(60);out=ROOT/'current-depth-reference-inventory-v31';out.mkdir(exist_ok=False)
    try:
        pieces,ledger=build(out);elapsed=time.monotonic()-start
        ledger['new_phase_seconds']=elapsed;ledger['p06_case_time_charge_seconds']=ledger['p06_prior_case_time_seconds']+elapsed
        if ledger['p06_case_time_charge_seconds']>180:raise ValueError('Original P06 case clock unchanged')
        raw=(json.dumps(ledger,indent=2)+'\n').encode()
        if sum(map(len,pieces.values()))+len(raw)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output chunk cap')
        for p,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(UNRESOLVED,'unresolved.json')]:
            (out/name).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(raw);print(json.dumps(ledger))
    finally:signal.alarm(0)

if __name__=='__main__':main()
