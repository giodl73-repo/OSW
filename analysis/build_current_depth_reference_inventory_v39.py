"""Admit retained Jutland model bounds through an offline descriptor-only query."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
import load_current_depth_reference_inventory_v39 as loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v39.json'
PREVIOUS='research/current-depth-reference-inventory-v38.json'
INVENTORY='research/current-depth-reference-inventory-v39.json'
ADDENDUM='research/current-depth-reference-addenda/jutland-norkyst2024-interior-censored-support-v1.json'
CSV='research/current-depth-reference-addenda/jutland-norkyst2024-interior-censored-support-v1.csv'
REVIEW='research/current-depth-norkyst-jutland-dated-depth-summary-source-review-v1.json'
def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def main():
    start=float(os.environ['OSW_JUTLAND_ADMISSION_START'])
    def stopped(*a):raise TimeoutError('Bounded offline descriptor admission deadline')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped)
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared semantic-test/producer clock')
    signal.alarm(max(1,int(60-elapsed)))
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No native/provider/source access'))
    out=ROOT/'current-depth-reference-inventory-v39';out.mkdir(exist_ok=False)
    def save(v):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    piece=lambda p,raw:{'file':p,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen admission input changed:'+p)
            source_raw=reader(loader.SOURCE)
            if hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:raise ValueError('Exact already-derived source packet required')
            source=json.loads(source_raw);review=json.loads(reader(REVIEW))
            if review['status']!='ALL12_SOURCE_CASES_REPRODUCED_WITH_CENSORED_PRIMARY_DEPTH_BOUNDS' or review['counts']['interior_axis_proxy_cases']!=11 or review['counts']['finite_primary_lower_component_contours']!=0:raise ValueError('Retained validated censoring scope required')
            prior_raw=reader(PREVIOUS);before=loader.previous.load_inventory(json.loads(prior_raw),reader)
            if before['counts']['depth_references']!=894:raise ValueError('Exact canonical predecessor required')
            a={'schema':loader.SCHEMA,'id':loader.ADDENDUM_ID,'source_result':piece(loader.SOURCE,source_raw),'source_contexts':{loader.CONTEXT:loader.context(source)},'evidence':loader.references(source),'runtime_changed':False,'full_goal_complete':False}
            after=loader.assemble(before,a,source)
            if after['evidence'][:-11]!=before['evidence'] or any(after['source_contexts'][k]!=v for k,v in before['source_contexts'].items()):raise ValueError('All894prior references and contexts preserved')
            for old,new in zip(before['records'],after['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('Non-reference owner fields changed')
            if after['counts']!={'identities':111,'depth_references':905,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':903}:raise ValueError('Only11dated model support references admitted')
            ar=encode(a);table=loader.reference_csv_bytes(a['evidence'])
            manifest={'schema':'osw.current-depth-reference-inventory.v39','status':'PINNED_REFERENCES_WITH_JUTLAND_INTERIOR_CENSORED_MODEL_SUPPORT','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':a['id'],'json':piece(ADDENDUM,ar),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v39','status':'ELEVEN_INTERIOR_MODEL_SUPPORT_BOUNDS_ADMITTED_EDGE_UNRESOLVED','interpretation':'Inclusive conditional45degree-component depth support at11dated northernJutland model columns. Missing/dry levels censor lower extent. No finite lower contour, physical thickness, current-wide profile, annual range, width join or volume; one edge selection remains unadmitted.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:ar,CSV:table}
            final_reader=lambda p:pieces[p] if p in pieces else reader(p)
            final=loader.load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if any(final[k]!=after[k] for k in ['evidence','records','source_contexts']):raise ValueError('Actual complete catalog/JSON/CSV roundtrip')
            result={'schema':'osw.jutland-model-support-admission-ledger.v1','status':'ELEVEN_MODEL_LOWER_BOUNDS_ADMITTED_894_PRIOR_REFERENCES_PRESERVED',
                'counts':after['counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'new_references':11,'new_direct_observations':0,'new_depth_values_computed':0,'prior_references_preserved':894,
                'unadmitted_edge_cases':loader.context(source)['unadmitted_edge_cases'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],
                'new_provider_requests':0,'new_native_values_decoded':0,'native_source_case_reopened':False,'historical_native_budget_compliance_reestablished':False,
                'query_scope':query.ledger['scope'],'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
        rr=encode(result)
        if sum(map(len,pieces.values()))+len(rr)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
        for p,n in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]:(out/n).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(rr)
        print(json.dumps({'counts':after['counts'],'new_references':11,'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],'example_reference':a['evidence'][0],'elapsed_seconds':time.monotonic()-start}),flush=True)
    finally:signal.alarm(0)
if __name__=='__main__':main()
