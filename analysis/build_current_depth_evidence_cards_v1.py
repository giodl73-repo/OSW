"""Expose usable depth quantities without merging incompatible definitions or scopes."""
import copy,csv,hashlib,io,json,os,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from load_current_depth_reference_inventory_v38 import load_inventory

ROOT=Path(__file__).resolve().parents[1]
CATALOG='research/current-depth-reference-inventory-v38.json'
OP='research/current-depth-evidence-cards-operator-v1.json'
FIELDS=('id','metric','unit','approximate_value_m','approximate_value_dbar','range_m',
        'lower_bound_m','lower_bound_exclusive','upper_bound_m','upper_bound_exclusive','vertical_datum',
        'upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','range_interpretation',
        'geographic_scope','temporal_scope','observed_period','calendar_months','phase_label',
        'evidence_kind','source_definition','qualification','source_url','source_citation',
        'source_locator','source_file','source_pointer','source_sha256','source_context_id',
        'source_cast_profile_id','source_qualifications','independent_observation_count_claimed',
        'whole_current_representative','volume_eligible','physical_state_join_eligible',
        'seasonal_playback_eligible','annual_extrema_eligible','physical_current_bottom_established',
        'reference_route_projection_eligible')

def role(metric):
    if metric=='core_depth':return 'core_position_not_bottom'
    if metric.startswith('transport_selected_') or metric=='net_section_transport_zero_depth':return 'transport_definition_not_bottom'
    if 'thickness' in metric:return 'layer_thickness_not_depth_below_surface'
    if metric.startswith(('derived_','converted_')) or metric in {'lower_flow_boundary_depth','upper_flow_boundary_depth','core_lower_boundary_depth','velocity_layer_lower_boundary_depth','reported_near_zero_flow_depth','reported_local_geostrophic_current_lower_extent','reported_mean_geostrophic_flow_lower_pressure_extent','reported_monthly_mean_velocity_zero_crossing_interface_depth'}:return 'scoped_boundary_or_flow_proxy'
    return 'published_extent_or_component_context'

def cards(view):
    owners={r['entity_id']:r for r in view['records']}
    if len(owners)!=len(view['records']):raise ValueError('Unique current identities required')
    grouped={owner:[] for owner in owners};seen=set()
    for e in view['evidence']:
        if e['id'] in seen or e['entity_id'] not in grouped:raise ValueError('Unique reference and known direct owner required')
        seen.add(e['id'])
        # Copy source quantities verbatim. No range union, midpoint, averaging,
        # dbar conversion, seasonal extrapolation, or boundary subtraction.
        row={k:copy.deepcopy(e[k]) for k in FIELDS if k in e}
        row['quantity_role']=role(e['metric'])
        row['source_reference_id']=e['id']
        row['asserts_whole_current_depth']=False
        grouped[e['entity_id']].append(row)
    result=[]
    for owner,r in owners.items():
        refs=grouped[owner];roles=Counter(e['quantity_role'] for e in refs)
        result.append({'entity_id':owner,'name':r['name'],'identity_level':r.get('identity_level'),
            'reference_count':len(refs),'quantity_role_counts':dict(sorted(roles.items())),
            'status':'scoped_boundary_or_proxy_available' if roles['scoped_boundary_or_flow_proxy'] else 'context_or_core_only' if refs else 'not_assessed_no_zero_implied',
            'references':refs,'headline_whole_current_depth_m':None,'annual_depth_range_m':None,'volume_km3':None,
            'selection_rule':'Inspect each definition, source and scope; no preferred scalar inferred from reference counts.',
            'next_collection_need':'Direct scoped velocity profile or clearly defined boundary evidence' if not roles['scoped_boundary_or_flow_proxy'] else 'Spatially and temporally matched profiles before a route or seasonal depth estimate',
            'members_inherited_or_aggregated':False})
    return {'schema':'osw.current-depth-evidence-cards.v1','catalog':CATALOG,
        'status':'PRESENTATION_OF_EXISTING_EVIDENCE_NOT_NEW_MEASUREMENTS',
        'counts':{'identities':len(result),'references':len(seen),'new_measurements':0},
        'capability_counts':dict(sorted(Counter(r['status'] for r in result).items())),
        'records':result,'interpretation':'Quantity roles organize existing evidence. Core position, transport limits, layer thickness, flow proxies and component context remain separate. Source ranges are not annual ranges or uncertainty. No current-wide scalar or volume is inferred.',
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}

def main():
    start=float(os.environ['OSW_DEPTH_CARDS_START'])
    def stopped(*a):raise TimeoutError('Bounded offline descriptor query deadline')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped)
    elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock required')
    signal.alarm(max(1,int(60-elapsed)))
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline descriptors only'))
    out=ROOT/'current-depth-evidence-cards-v1';out.mkdir(exist_ok=False)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()
    def save(v):
        tmp=out/'ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0)
    reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
            manifest=json.loads(reader(CATALOG));view=load_inventory(manifest,reader);report=cards(view)
            if report['counts']!={'identities':111,'references':894,'new_measurements':0}:raise ValueError('Exact canonical coverage required')
            raw=encode(report)
            if json.loads(raw)!=report:raise ValueError('Actual complete card JSON roundtrip')
        fields=['entity_id','name','identity_level','reference_count','status','quantity_role_counts','next_collection_need']
        rows=[{k:json.dumps(r[k],sort_keys=True,separators=(',',':')) if isinstance(r[k],dict) else str(r[k]) for k in fields} for r in report['records']]
        table=io.StringIO(newline='');writer=csv.DictWriter(table,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(rows)
        csvraw=table.getvalue().encode('utf8')
        if list(csv.DictReader(io.StringIO(csvraw.decode('utf8'))))!=rows:raise ValueError('All CSV values roundtrip')
        if len(raw)>2500000 or len(raw)+len(csvraw)+(out/'query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
        (out/'evidence-cards.json').write_bytes(raw);(out/'evidence-cards.csv').write_bytes(csvraw)
        print(json.dumps({'counts':report['counts'],'capability_counts':report['capability_counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],'cumulative_active_seconds':time.monotonic()-start,'new_native_values_decoded':0,'provider_requests':0}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
