"""Admit two retained Hanish interface descriptors into catalogv35 offline."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
import load_current_depth_reference_inventory_v35 as loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v35.json'
PREVIOUS='research/current-depth-reference-inventory-v34.json'
INVENTORY='research/current-depth-reference-inventory-v35.json'
ADDENDUM='research/current-depth-reference-addenda/pratt2000-hanish-mean-interface-depths-v1.json'
CSV='research/current-depth-reference-addenda/pratt2000-hanish-mean-interface-depths-v1.csv'
PRIOR='research/pratt2000-hanish-mean-interface-derivation-ledger-v1.json'
CAPTURE_OP='research/pratt2000-bab-mandab-primary-operator-v1.json'
CAPTURE_LEDGER='research/pratt2000-bab-mandab-primary-ledger-v1.json'
def numbers(v):
    if isinstance(v,dict):return sum(numbers(x) for x in v.values())
    if isinstance(v,list):return sum(numbers(x) for x in v)
    return int(type(v) in (int,float))
def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def main():
    def stopped(*a):raise SystemExit('Offline Hanish admission stopped; no replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No provider/archive/source access'))
    start=float(os.environ['OSW_HANISH_ADMISSION_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic/producer clock')
    signal.alarm(60);out=ROOT/'current-depth-reference-inventory-v35';out.mkdir(exist_ok=False)
    def save(v):
        p=out/'catalog-query-ledger.json';tmp=p.with_suffix('.tmp');tmp.write_bytes(encode(v));os.replace(tmp,p)
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    piece=lambda p,raw:{'file':p,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            if any(op['eligibility'].values()):raise ValueError('No physical/temporal/volume/runtime promotion')
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
            source_raw=reader(loader.SOURCE)
            if hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:raise ValueError('Exact qualified Hanish packet')
            source=json.loads(source_raw);prior=json.loads(reader(PRIOR));capture_op_raw=reader(CAPTURE_OP);capture_op=json.loads(capture_op_raw);capture_ledger_raw=reader(CAPTURE_LEDGER)
            if prior['status']!='TWO_SOURCE_REPORTED_MEAN_INTERFACES_VERIFIED_NOT_CANONICALLY_ADMITTED' or prior['cumulative_source_case_numeric_bound']!=1126 or prior['provider_operations_remaining']!=0:raise ValueError('Closed source-case counters carried')
            prior_raw=reader(PREVIOUS);before=loader.previous.load_inventory(json.loads(prior_raw),reader)
            if before['counts']['depth_references']!=889:raise ValueError('Exact canonical predecessor')
            a={'schema':loader.SCHEMA,'id':'pratt2000-hanish-mean-interface-depths-v1','source_result':piece(loader.SOURCE,source_raw),'source_contexts':{loader.CONTEXT:loader.context()},'evidence':loader.references(source),'runtime_changed':False,'full_goal_complete':False}
            after=loader.assemble(before,a,source)
            if after['evidence'][:-2]!=before['evidence'] or any(after['source_contexts'][k]!=v for k,v in before['source_contexts'].items()):raise ValueError('All889prior references and contexts preserved')
            for old,new in zip(before['records'],after['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Non-reference owner fields changed')
            if after['counts']!={'identities':111,'depth_references':891,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':889}:raise ValueError('Only two local endpoints admitted')
            ar=encode(a);table=loader.reference_csv_bytes(a['evidence'])
            manifest={'schema':'osw.current-depth-reference-inventory.v35','status':'PINNED_REFERENCES_WITH_HANISH_REPORTED_MEAN_INTERFACES','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':a['id'],'json':piece(ADDENDUM,ar),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v35','status':'TWO_HANISH_MONTHLY_MEAN_INTERFACE_ENDPOINTS_ADMITTED','interpretation':'Source-reported winter35m/summer110m endpoints of monthly mean exchange-flow interface. Not physical current bottom, individual-boundary mean, annual extrema or recurring seasonal climatology.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:ar,CSV:table}
            def final_reader(p):return pieces[p] if p in pieces else reader(p)
            final=loader.load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if any(final[k]!=after[k] for k in ['evidence','records','source_contexts']):raise ValueError('Actual full JSON/CSV/catalog roundtrip')
            # Conservative byte-derived upper bound for original capture bookkeeping
            # omitted from its source-text token count. One numeric value needs >=1 byte.
            prior_capture_bookkeeping_upper_bound=2*len(capture_op_raw)+2*len(capture_ledger_raw)
            newcharge=2*numbers(source)+numbers(prior)+numbers(op)+numbers(capture_op)+numbers(a)+numbers(manifest)
            sourcecase=prior['cumulative_source_case_numeric_bound']+prior_capture_bookkeeping_upper_bound+newcharge
            elapsed=time.monotonic()-start;casetime=prior['cumulative_case_elapsed_seconds']+elapsed
            if sourcecase>250000 or casetime>60:raise ValueError('Original source case limits not renewed')
            result={'schema':'osw.hanish-reported-interface-admission-ledger.v1','status':'TWO_MEAN_INTERFACES_ADMITTED_889_PRIOR_REFERENCES_PRESERVED','counts':after['counts'],'new_references':2,'new_provider_requests':0,'new_native_values_decoded':0,'prior_source_case_ledger_unchanged':copy.deepcopy(prior),'original_capture_bookkeeping_numeric_upper_bound':prior_capture_bookkeeping_upper_bound,'capture_bookkeeping_bound_semantics':'twice byte lengths of frozen capture operator and capture ledger; conservative unenumerated original metadata allowance, not an exact runtime scalar count','new_source_metadata_and_descriptor_charge':newcharge,'source_case_numeric_upper_bound':sourcecase,'new_phase_seconds':elapsed,'source_case_cumulative_seconds':casetime,'native_acquisition_budget_renewed':False,'canonical_query_scope':query.ledger['scope'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
        rr=encode(result)
        if sum(map(len,pieces.values()))+len(rr)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output chunk bound')
        for p,n in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/n).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(rr);print(json.dumps(result))
    finally:signal.alarm(0)
if __name__=='__main__':main()
