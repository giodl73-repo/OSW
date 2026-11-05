"""Compile nine frozen native scalar proxies without repeating native analysis."""
import copy,hashlib,json,os,signal,socket,time
from pathlib import Path
import load_current_depth_reference_inventory_v27 as prior
import load_current_depth_reference_inventory_v28 as loader

ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-reference-inventory-operator-v28.json'
INVENTORY='research/current-depth-reference-inventory-v28.json'
ADDENDUM='research/current-depth-reference-addenda/a20-local-fixed-direction-depths-v1.json'
CSV='research/current-depth-reference-addenda/a20-local-fixed-direction-depths-v1.csv'
ACCOUNTING='research/a20-depth-resource-accounting-audit-v1.json'


def numbers(v):
    if isinstance(v,dict):return sum(numbers(a) for a in v.values())
    if isinstance(v,list):return sum(numbers(a) for a in v)
    return int(type(v) in (int,float))


def facts_from_frozen_result(source):
    if source['schema']!='osw.a20-gulf-stream-core-direction-depths.v2' or source['counts']['source_cast_profiles']!=3 or source['counts']['adjacent_local_crossings']!=9:
        raise ValueError('Exact processed three-cast source, no native reinterpretation')
    if source['first_native_crossing_verified'] or source['continuous_core_connection_verified'] or source['whole_route_physical_depth_profile_established']:
        raise ValueError('Local bracket limitations required')
    records=[]
    for i,p in enumerate(source['profiles']):
        if p['selected_native_levels']>40 or p['entity_context']!='current:gulf-stream':raise ValueError('Original source selection/owner required')
        for j,c in enumerate(p['threshold_cases']):
            if c['status']!='ADJACENT_NATIVE_CROSSING_WITHIN_FIRST_COARSE_DESCENDING_BRACKET' or c['lower_depth_m'] is None or c['first_native_downcrossing_below_core_verified'] or c['continuous_connection_from_core_verified']:
                raise ValueError('Resolved local adjacent bracket, never global first crossing')
            records.append({'entity_id':'current:gulf-stream','station':p['station'],'threshold_m_s':c['threshold_m_s'],
                'computed_depth_m':c['lower_depth_m'],'native_depth_bracket_m':copy.deepcopy(c['lower_depth_native_bracket_m']),
                'refined_native_indices':copy.deepcopy(c['refined_bracket_indices']),
                'original_coarse_bracket_indices':copy.deepcopy(c['coarse_bracket_indices']),
                'fixed_reference_frame':copy.deepcopy(p['fixed_reference_frame']),
                'cast_datetime_utc':p['cast_datetime_utc'],'source_lon_lat':copy.deepcopy(p['source_lon_lat']),
                'raw_native_file':p['source_file'],'raw_native_sha256':p['source_sha256'],
                'source_case_pointer':'/profiles/'+str(i)+'/threshold_cases/'+str(j),
                'current_membership_basis':'primary_cruise_QC_stations14_to21_candidate_not_independent_axis_validation'})
    facts={'schema':'osw.a20-local-component-depth-reference-facts.v1','source_file':loader.SOURCE,'source_sha256':loader.SOURCE_SHA,
        'metric':loader.METRIC,'source_cast_profiles':3,'records':records,
        'source_uncertainty_semantics':'provider_velocity_uncertainty_estimate_not_SE_or_depth_CI',
        'independent_observation_count_claimed':False,**{k:False for k in loader.FALSE_GATES}}
    loader.validate_facts(facts)
    return facts


def build():
    reader=lambda p:(ROOT/p).read_bytes()
    op=json.loads(reader(OP))
    if any(op['eligibility'].values()):raise ValueError('No physical/seasonal/volume/runtime promotion')
    for p,h in op['input_sha256'].items():
        if hashlib.sha256(reader(p)).hexdigest()!=h:raise ValueError('Frozen source or method changed:'+p)
    source_raw=reader(loader.SOURCE);accounting_raw=reader(ACCOUNTING)
    if len(source_raw)>400000 or len(accounting_raw)>10000 or hashlib.sha256(source_raw).hexdigest()!=loader.SOURCE_SHA:
        raise ValueError('Bounded exact frozen scalar packets required')
    # Each acquisition-case packet is parsed exactly once in the producer; tests use fixtures only.
    source=json.loads(source_raw);accounting=json.loads(accounting_raw)
    if accounting['corrected_case_metadata_touch_bound_including_audit']!=6412 or accounting['corrected_case_scalar_bound_including_audit']!=14520:
        raise ValueError('Corrected cumulative counters, not obsolete source report totals')
    facts=facts_from_frozen_result(source)
    previous=json.loads(reader('research/current-depth-reference-inventory-v27.json'))
    before=prior.load_inventory(previous,reader);parts=prior.read_parts(previous,reader)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
    piece=lambda p,raw:{'file':p,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    facts_raw=encode(facts);source_piece=piece(loader.FACTS,facts_raw)
    addendum={'schema':loader.SCHEMA,'id':'a20-local-fixed-direction-depths-v1','base_snapshot_sha256':previous['base']['json']['sha256'],
        'operator_file':OP,'operator_sha256':hashlib.sha256(reader(OP)).hexdigest(),'input_sha256':op['input_sha256'],
        'reviewed_source_facts':source_piece,'source_contexts':{loader.CONTEXT:facts},'evidence':loader.references(facts,source_piece),
        'runtime_changed':False,'full_goal_complete':False}
    view=loader.assemble(*parts,[(addendum,facts)])
    if view['evidence'][:-9]!=before['evidence']:raise ValueError('All860prior references preserved exactly')
    for k,v in before['source_contexts'].items():
        if view['source_contexts'][k]!=v:raise ValueError('Every prior source context preserved')
    if view['counts']!={'identities':111,'depth_references':869,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0} or view['coordinate_unit_counts']!={'dbar':2,'m':867}:
        raise ValueError('Expected additive catalog counts, not new current identities or physical bottoms')
    add_raw=encode(addendum);table=loader.reference_csv_bytes(addendum['evidence'])
    inventory=copy.deepcopy(previous)
    inventory.update(schema='osw.current-depth-reference-inventory.v28',status='PINNED_REFERENCES_WITH_LOCAL_OBSERVED_A20_COMPONENT_DEPTHS',
        counts=view['counts'],metric_counts=view['metric_counts'],coordinate_unit_counts=view['coordinate_unit_counts'])
    inventory['addenda'].append({'id':addendum['id'],'json':piece(ADDENDUM,add_raw),'csv':piece(CSV,table)})
    inventory['view_metadata'].update(schema='osw.current-depth-reference-view.v28',status=inventory['status'],
        generator_file='analysis/build_current_depth_reference_inventory_v28.py',
        generator_sha256=hashlib.sha256(reader('analysis/build_current_depth_reference_inventory_v28.py')).hexdigest(),interpretation=op['interpretation'])
    pieces={loader.FACTS:facts_raw,ADDENDUM:add_raw,CSV:table,INVENTORY:encode(inventory)}
    # One final manifest roundtrip reads new facts/addendum once. Count their numeric packets too.
    new_reads={loader.FACTS:0,ADDENDUM:0}
    def final_reader(p):
        if p in new_reads:new_reads[p]+=1
        return pieces[p] if p in pieces else reader(p)
    roundtrip=loader.load_inventory(inventory,final_reader)
    if new_reads!={loader.FACTS:1,ADDENDUM:1} or roundtrip['evidence']!=view['evidence']:
        raise ValueError('Exact actual roundtrip and bounded new-packet reads required')
    decoded=numbers(source)+numbers(accounting)+numbers(facts)+numbers(addendum)
    metadata=6412+decoded;scalars=14520+decoded
    if metadata>10000 or scalars>250000:raise ValueError('Original A20 cumulative caps cannot reset for cataloging')
    ledger={'schema':'osw.a20-local-depth-reference-admission-ledger.v1','status':'NINE_LOCAL_REFERENCES_COMPILED_NO_NEW_NATIVE_READS',
        'source_result_packet_numeric_values':numbers(source),'prior_accounting_packet_numeric_values':numbers(accounting),
        'thin_facts_roundtrip_numeric_values':numbers(facts),'new_addendum_roundtrip_numeric_values':numbers(addendum),
        'corrected_case_metadata_touch_bound':metadata,'corrected_case_scalar_bound':scalars,
        'original_case_metadata_cap':10000,'original_case_scalar_cap':250000,'original_case_provider_operations_used':3,
        'original_case_provider_operations_remaining':0,'new_native_ocean_values_decoded':0,'new_provider_requests':0,
        'prior_case_time_charge_seconds':accounting['cumulative_case_time_charge_seconds'],
        'new_references':9,'source_cast_profiles':3,'counts':view['counts'],'runtime_changed':False,'full_goal_complete':False}
    return pieces,ledger


def main():
    def stopped(*a):raise SystemExit('Stopped offline scalar catalog producer')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('No source requests'))
    signal.alarm(90);start=float(os.environ['OSW_A20_ADMISSION_PHASE_START'])
    if not 0<=time.monotonic()-start<90:raise ValueError('Shared synthetic-test/producer phase clock')
    out=ROOT/'current-depth-reference-inventory-v28';out.mkdir(exist_ok=False)
    pieces,ledger=build();ledger['new_reference_admission_phase_seconds']=time.monotonic()-start
    ledger['cumulative_case_time_charge_seconds']=ledger['prior_case_time_charge_seconds']+ledger['new_reference_admission_phase_seconds']
    if ledger['cumulative_case_time_charge_seconds']>180:raise ValueError('Original case time cap unchanged')
    ledger_raw=(json.dumps(ledger,indent=2,allow_nan=False)+'\n').encode()
    if sum(map(len,pieces.values()))+len(ledger_raw)>2400000 or any(len(v)>2500000 for v in pieces.values()):raise ValueError('Fixed publication/output caps')
    for p,name in [(INVENTORY,'inventory.json'),(ADDENDUM,'addendum.json'),(CSV,'references.csv'),(loader.FACTS,'facts.json')]:
        (out/name).write_bytes(pieces[p])
    (out/'admission-ledger.json').write_bytes(ledger_raw)
    print(json.dumps(ledger))


if __name__=='__main__':main()
