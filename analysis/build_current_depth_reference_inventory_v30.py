"""Admit frozen local native-frame proxies; never re-open native arrays."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
import load_current_depth_reference_inventory_v30 as loader
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v30.json'
PREVIOUS='research/current-depth-reference-inventory-v29.json'
INVENTORY='research/current-depth-reference-inventory-v30.json'
ADDENDUM='research/current-depth-reference-addenda/i06s-agulhas-native-uv-depths-v1.json'
CSV='research/current-depth-reference-addenda/i06s-agulhas-native-uv-depths-v1.csv'
I06S_LEDGER='research/i06s-agulhas-native-frame-depth-ledger-v2.json'
A20_LEDGER='research/a20-cast-temporal-semantics-correction-ledger-v1.json'
A20_PACKETS={'research/a20-local-component-depth-reference-facts-v1.json':154,
    'research/current-depth-reference-addenda/a20-local-fixed-direction-depths-v1.json':317}

def numbers(v):
    if isinstance(v,dict):return sum(numbers(a) for a in v.values())
    if isinstance(v,list):return sum(numbers(a) for a in v)
    return int(type(v) in (int,float))

def build():
    read=lambda p:(ROOT/p).read_bytes()
    op=json.loads(read(OP))
    if any(op['eligibility'].values()):raise ValueError('No physical/seasonal/volume/runtime promotion')
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(read(p)).hexdigest()!=h:raise ValueError('Frozen dependency changed:'+p)
    a20reads={p:0 for p in A20_PACKETS};newreads={loader.SOURCE:0,ADDENDUM:0}
    def reader(p):
        if p in a20reads:a20reads[p]+=1
        if p in newreads:newreads[p]+=1
        return read(p)
    source_raw=reader(loader.SOURCE)
    if len(source_raw)>400000 or hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:raise ValueError('Bounded exact frozen result packet')
    source=json.loads(source_raw)
    i06s=json.loads(read(I06S_LEDGER));a20=json.loads(read(A20_LEDGER))
    if i06s['numeric_metadata_values_including_reconstruction']!=1973 or i06s['native_array_values_decoded']!=1094 or i06s['provider_operations_remaining']!=0:
        raise ValueError('Original cumulative I06S source counters required')
    if a20['corrected_case_metadata_touch_bound']!=8764 or a20['corrected_case_scalar_bound']!=16872:
        raise ValueError('Preserve latest corrected A20 counters')
    previous_raw=read(PREVIOUS);before=loader.previous.load_inventory(json.loads(previous_raw),reader)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    piece=lambda p,raw:{'file':p,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    addendum={'schema':loader.SCHEMA,'id':'i06s-agulhas-native-uv-depths-v1','source_result':piece(loader.SOURCE,source_raw),
        'operator_file':OP,'operator_sha256':hashlib.sha256(read(OP)).hexdigest(),
        'source_contexts':{loader.CONTEXT:loader.context()},'evidence':loader.references(source),
        'runtime_changed':False,'full_goal_complete':False}
    after=loader.assemble(before,addendum,source)
    if after['evidence'][:-9]!=before['evidence']:raise ValueError('Every prior reference preserved exactly')
    for k,v in before['source_contexts'].items():
        if after['source_contexts'][k]!=v:raise ValueError('Every prior context preserved')
    if after['counts']!={'identities':111,'depth_references':878,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or after['coordinate_unit_counts']!={'dbar':2,'m':876}:
        raise ValueError('Exactly nine additive references; no new owners/physical coverage')
    add_raw=encode(addendum);table=loader.reference_csv_bytes(addendum['evidence'])
    manifest={'schema':'osw.current-depth-reference-inventory.v30','status':'PINNED_REFERENCES_WITH_CONDITIONAL_NATIVE_UV_CAST_DEPTHS',
        'previous_inventory':piece(PREVIOUS,previous_raw),'reference_addendum':{'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,table)},
        'counts':after['counts'],'metric_counts':after['metric_counts'],'coordinate_unit_counts':after['coordinate_unit_counts'],
        'view_metadata':{'schema':'osw.current-depth-reference-view.v30','status':'CONDITIONAL_NATIVE_UV_LOCAL_CAST_DEPTHS',
            'interpretation':'Nine native U/V local cutoff proxies from three northern I06S2019casts; preserve beta/QC/current-membership caveats and every prior reference.',
            'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False},
        'runtime_changed':False,'full_goal_complete':False}
    pieces={INVENTORY:encode(manifest),ADDENDUM:add_raw,CSV:table}
    def final_reader(p):
        if p in pieces:
            if p in newreads:newreads[p]+=1
            return pieces[p]
        return reader(p)
    final=loader.load_inventory(manifest,final_reader)
    if final['evidence']!=after['evidence'] or newreads!={loader.SOURCE:2,ADDENDUM:1} or any(v!=2 for v in a20reads.values()):
        raise ValueError('Exact final loader/JSONCSV roundtrip and actual packet reads')
    decoded=newreads[loader.SOURCE]*numbers(source)+numbers(i06s)+numbers(addendum)+numbers(op)
    metadata=i06s['numeric_metadata_values_including_reconstruction']+decoded
    scalars=metadata+i06s['native_array_values_decoded']
    a20decoded=sum(a20reads[p]*n for p,n in A20_PACKETS.items())+numbers(a20)
    a20meta=a20['corrected_case_metadata_touch_bound']+a20decoded
    a20scalars=a20['corrected_case_scalar_bound']+a20decoded
    if max(metadata,a20meta)>10000 or max(scalars,a20scalars)>250000:raise ValueError('Neither source case allowance resets for cataloging')
    ledger={'schema':'osw.i06s-native-uv-reference-admission-ledger.v1','status':'NINE_CONDITIONAL_REFERENCES_ADMITTED_NO_NEW_NATIVE_READS',
        'counts':after['counts'],'source_cast_profiles':3,'new_references':9,'new_provider_requests':0,'new_native_ocean_values_decoded':0,
        'i06s_source_packet_reads':newreads[loader.SOURCE],'i06s_addendum_reads':newreads[ADDENDUM],
        'i06s_new_metadata_numbers':decoded,'i06s_case_metadata_touch_bound':metadata,'i06s_case_scalar_bound':scalars,
        'i06s_prior_case_time_seconds':i06s['case_time_charge_seconds'],
        'a20_packet_reads':a20reads,'a20_new_metadata_numbers':a20decoded,
        'a20_case_metadata_touch_bound':a20meta,'a20_case_scalar_bound':a20scalars,
        'a20_prior_case_time_seconds':a20['cumulative_case_time_charge_seconds'],
        'runtime_changed':False,'full_goal_complete':False}
    return pieces,ledger

def main():
    def stopped(*a):raise SystemExit('Stopped offline conditional reference admission')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No provider/network access'))
    start=float(os.environ['OSW_I06S_ADMISSION_PHASE_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(60);out=ROOT/'current-depth-reference-inventory-v30';out.mkdir(exist_ok=False)
    try:
        pieces,ledger=build();elapsed=time.monotonic()-start
        ledger['new_phase_seconds']=elapsed
        ledger['i06s_case_time_charge_seconds']=ledger['i06s_prior_case_time_seconds']+elapsed
        ledger['a20_case_time_charge_seconds']=ledger['a20_prior_case_time_seconds']+elapsed
        if max(ledger['i06s_case_time_charge_seconds'],ledger['a20_case_time_charge_seconds'])>180:raise ValueError('Original case clocks unchanged')
        raw=(json.dumps(ledger,indent=2)+'\n').encode()
        if sum(map(len,pieces.values()))+len(raw)>2400000:raise ValueError('Whole output chunk cap')
        for p,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv')]:
            (out/name).write_bytes(pieces[p])
        (out/'admission-ledger.json').write_bytes(raw);print(json.dumps(ledger))
    finally:signal.alarm(0)

if __name__=='__main__':main()
