"""Compile the Oman published descriptors into canonical catalogv34 offline."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
import load_current_depth_reference_inventory_v34 as loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v34.json'
PREVIOUS='research/current-depth-reference-inventory-v33.json'
INVENTORY='research/current-depth-reference-inventory-v34.json'
ADDENDUM='research/current-depth-reference-addenda/oman-2025-published-plume-descriptors-v1.json'
CSV='research/current-depth-reference-addenda/oman-2025-published-plume-descriptors-v1.csv'
SOURCE_LEDGER='research/oman-2025-published-depth-ledger-v1.json'
def encode(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def main():
    def stopped(*a):raise SystemExit('Bounded offline admission stopped; no provider/archive replay')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptor admission only'))
    start=float(os.environ['OSW_OMAN_ADMISSION_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic/producer clock')
    signal.alarm(60);out=ROOT/'current-depth-reference-inventory-v34';out.mkdir(exist_ok=False)
    def save(v):
        p=out/'catalog-query-ledger.json';tmp=p.with_suffix('.tmp');tmp.write_bytes(encode(v));os.replace(tmp,p)
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0)
    reader=query.reader(lambda p:(ROOT/p).read_bytes())
    piece=lambda p,raw:{'file':p,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            if any(op['eligibility'].values()):raise ValueError('No physical/time/volume/runtime promotion')
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen method/input changed:'+p)
            source_raw=reader(loader.SOURCE)
            if hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:raise ValueError('Exact qualified descriptor packet')
            source=json.loads(source_raw);ledger=json.loads(reader(SOURCE_LEDGER));prior_raw=reader(PREVIOUS)
            if ledger['status']!='PUBLISHED_DESCRIPTORS_VERIFIED' or ledger['attempted_provider_operations']!=1 or ledger['source_numeric_tokens']!=1082 or ledger['descriptor_numeric_tokens_conservative']!=233 or ledger['raw_native_arrays_decoded']!=0:raise ValueError('Carry closed source accounting unchanged')
            before=loader.previous.load_inventory(json.loads(prior_raw),reader)
            if before['counts']['depth_references']!=884:raise ValueError('Exact884canonical predecessor')
            a={'schema':loader.SCHEMA,'id':'oman-2025-published-plume-descriptors-v1','source_result':piece(loader.SOURCE,source_raw),'source_contexts':{loader.CONTEXT:loader.context()},'evidence':loader.references(source),'runtime_changed':False,'full_goal_complete':False}
            after=loader.assemble(before,a,source)
            if after['evidence'][:-5]!=before['evidence'] or any(after['source_contexts'][k]!=v for k,v in before['source_contexts'].items()):raise ValueError('Every prior reference/context preserved')
            for old,new in zip(before['records'],after['records']):
                if {k:v for k,v in old.items() if k!='depth_reference_ids'}!={k:v for k,v in new.items() if k!='depth_reference_ids'}:raise ValueError('All non-reference owner fields unchanged')
            if after['counts']!={'identities':111,'depth_references':889,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':887}:raise ValueError('Five additive scoped descriptors only')
            ar=encode(a);table=loader.reference_csv_bytes(a['evidence'])
            manifest={'schema':'osw.current-depth-reference-inventory.v34','status':'PINNED_REFERENCES_WITH_OMAN_PUBLISHED_PLUME_SPATIAL_DESCRIPTORS','previous_inventory':piece(PREVIOUS,prior_raw),'reference_addendum':{'id':a['id'],'json':piece(ADDENDUM,ar),'csv':piece(CSV,table)},'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],'view_metadata':{'schema':'osw.current-depth-reference-view.v34','status':'FIVE_OMAN_REPORTED_SPATIAL_PLUME_DESCRIPTORS_ADMITTED','interpretation':'Three upper-depth and two thickness descriptors from oneJuly2025hydrographic survey. Spatial ranges/maxima, not paired station boundaries or annual/whole-route physical depths.','runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},'runtime_changed':False,'full_goal_complete':False}
            pieces={INVENTORY:encode(manifest),ADDENDUM:ar,CSV:table}
            def final_reader(p):return pieces[p] if p in pieces else reader(p)
            final=loader.load_inventory(json.loads(pieces[INVENTORY]),final_reader)
            if final['evidence']!=after['evidence'] or final['records']!=after['records'] or final['source_contexts']!=after['source_contexts']:raise ValueError('Actual full JSON/CSV/catalog roundtrip')
            result={'schema':'osw.oman-published-depth-admission-ledger.v1','status':'FIVE_SPATIAL_DESCRIPTORS_ADMITTED_884_PRIOR_REFERENCES_PRESERVED','counts':after['counts'],'new_references':5,'new_native_values_decoded':0,'new_provider_requests':0,'original_source_case_accounting_unchanged':copy.deepcopy(ledger),'native_acquisition_budget_renewed':False,'canonical_query_scope':query.ledger['scope'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],'elapsed_seconds':time.monotonic()-start,'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}
        rr=encode(result)
        if sum(map(len,pieces.values()))+len(rr)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output chunk cap')
        for p,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]: (out/name).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(rr);print(json.dumps(result))
    finally:signal.alarm(0)
if __name__=='__main__':main()
