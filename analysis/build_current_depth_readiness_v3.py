"""Refresh admitted-depth readiness and expose metric-specific collection gaps."""
import copy,csv,hashlib,io,json,os,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v15 import load_inventory
from build_current_depth_readiness_v2 import join as previous_join,PARENT_PRIORITIES
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-readiness-operator-v3.json'
CATALOG='research/current-depth-reference-inventory-v52.json'
PRIORITIES='research/current-depth-collection-priorities-v1.json'
PROJECTIONS='research/current-depth-route-projection-inventory-v48.json'
TEMPORAL='research/current-depth-temporal-review-index-v1.json'
EXTENT={'reported_vertical_extent','lower_flow_boundary_depth','upper_flow_boundary_depth','velocity_layer_lower_boundary_depth','reported_local_geostrophic_current_lower_extent','reported_mean_flow_upper_layer_extent','reported_monthly_mean_velocity_zero_crossing_interface_depth','reported_mean_geostrophic_flow_lower_pressure_extent','reported_near_zero_flow_depth'}
CORE={'core_depth','core_lower_boundary_depth','core_vertical_thickness','reported_meridional_velocity_core_depth_band'}
THICKNESS={'reported_vertical_thickness','reported_water_mass_plume_thickness','reported_advected_atlantic_water_layer_thickness'}
HYDRO={'current_associated_bedform_field_water_depth_extent','reported_coastal_front_foot_depth_scale','reported_current_associated_halocline_depth_band','reported_episodic_nutrient_bearing_water_mass_upper_layer_extent','reported_hydrographic_outflow_depth_band','reported_salinity_selected_area_mean_water_depth','reported_selected_noncore_water_mass_lower_extent','reported_water_mass_plume_upper_boundary_depth','sampled_water_mass_depth_band'}

def metric_family(metric):
    if metric in CORE:return 'core_structure'
    if 'censored' in metric or 'penetration_lower_bound' in metric:return 'censored_reach'
    if metric.startswith(('derived_','converted_')):return 'processed_velocity_descriptor'
    if metric.startswith(('transport_selected_','net_section_transport_')):return 'transport_operator'
    if metric.startswith(('reported_model_','reported_reanalysis_')):return 'published_model_extent'
    if metric in EXTENT:return 'reported_extent_or_boundary_metric'
    if metric in THICKNESS:return 'reported_layer_or_plume_thickness'
    if metric in HYDRO:return 'hydrographic_or_habitat_proxy'
    if metric in {'reported_regional_bottom_intensified_flow_pressure_band','reported_regional_ladcp_flow_pressure_band'}:return 'regional_pressure_domain'
    if metric in {'reported_flow_depth_band','reported_local_flow_regime_transition_depth_band','reported_vertical_scale_length'}:return 'flow_band_or_scale'
    return 'unclassified_metric_retained'

def enrich(report,view):
    grouped={r['entity_id']:[] for r in view['records']}
    for ref in view['evidence']:
        if ref['entity_id'] not in grouped:raise ValueError('Unknown reference owner')
        grouped[ref['entity_id']].append(ref)
    if len(grouped)!=len(view['records']) or set(grouped)!={r['entity_id'] for r in report['records']}:raise ValueError('Exact readiness/current owner join')
    output=copy.deepcopy(report);queue=[]
    for row in output['records']:
        refs=grouped[row['entity_id']];families=Counter(metric_family(r['metric']) for r in refs)
        if len(refs)!=row['canonical_reference_count'] or [r['id'] for r in refs]!=row['canonical_reference_ids']:raise ValueError('Complete canonical references required')
        row['metric_family_counts']=dict(sorted(families.items()))
        row['metric_family_reference_ids']={family:[r['id'] for r in refs if metric_family(r['metric'])==family] for family in sorted(families)}
        row['metric_grouping_basis']='editorial_metric_name_taxonomy_not_new_physical_validation'
        row['pressure_reference_ids']=[r['id'] for r in refs if r['unit']=='dbar']
        row['unclassified_metric_names']=sorted({r['metric'] for r in refs if metric_family(r['metric'])=='unclassified_metric_retained'})
        row['declared_reference_volume_eligible_count']=sum(r.get('volume_eligible') is True for r in refs)
        row['missing_reference_volume_eligibility_flag_count']=sum('volume_eligible' not in r for r in refs)
        row['eligibility_flag_counts_are_physical_validation']=False
        parent=row['regional_priority_kind'] in PARENT_PRIORITIES
        if parent:gap='component_identity_scope_before_parent_depth';tier=3
        elif not refs:gap='no_direct_canonical_reference';tier=0
        elif not families['reported_extent_or_boundary_metric']:
            gap='reported_extent_or_boundary_metric_not_in_canonical_references';tier=1
        else:gap='extend_regional_extent_evidence_to_aligned_route_and_time';tier=2
        row['collection_gap_kind']=gap
        row['collection_gap_basis']='canonical_reference_metric_presence_and_frozen_regional_queue_only_not_exhaustive_literature_absence'
        row['suggested_whole_current_depth_m']=None
        row['family_requires_single_depth']=False if parent else None
        queue.append({'entity_id':row['entity_id'],'name':row['name'],'gap_kind':gap,'queue_tier':tier,'frozen_regional_priority_rank':row['regional_collection_priority_rank'],'reported_extent_or_boundary_reference_count':families['reported_extent_or_boundary_metric'],'core_reference_count':families['core_structure'],'censored_reach_reference_count':families['censored_reach'],'processed_velocity_reference_count':families['processed_velocity_descriptor'],'published_model_extent_reference_count':families['published_model_extent'],'pressure_reference_count':len(row['pressure_reference_ids']),'canonical_reference_count':len(refs)})
    queue.sort(key=lambda r:(r['queue_tier'],r['frozen_regional_priority_rank'],r['entity_id']))
    for rank,row in enumerate(queue,1):row['editorial_queue_position']=rank
    output['schema']='osw.current-depth-readiness.v3'
    output['canonical_reference_inventory']=CATALOG
    output['status']='CURRENT_CANONICAL_REFERENCE_METRIC_AND_REGIONAL_GAP_AUDIT'
    output['collection_queue']=queue
    output['counts']['metric_family_references']=dict(sorted(Counter(metric_family(r['metric']) for r in view['evidence']).items()))
    output['counts']['collection_gap_kinds']=dict(sorted(Counter(r['collection_gap_kind'] for r in output['records']).items()))
    output['counts']['owners_with_reported_extent_or_boundary_metric']=sum(bool(r['metric_family_counts'].get('reported_extent_or_boundary_metric')) for r in output['records'])
    output['counts']['owners_with_unclassified_metrics']=sum(bool(r['unclassified_metric_names']) for r in output['records'])
    output['counts']['pressure_coordinate_references']=sum(len(r['pressure_reference_ids']) for r in output['records'])
    output['interpretation']+=' Metric families and editorial queue expose collection targets,not interchangeable physical quantities. No nominal depth selected,reference removed,pressure conversion or new measurement. Missing evidence in this pinned inventory does not establish absence in the literature.'
    if sum(output['counts']['metric_family_references'].values())!=sum(r['canonical_reference_count'] for r in output['records']):raise ValueError('Every reference classified exactly once')
    return output

def join(view,priority,products):
    return enrich(previous_join(view,priority,products),view)

def main():
    start=float(os.environ['OSW_DEPTH_READINESS_START'])
    def stop(*a):raise TimeoutError('Shared readiness60seconds including tests')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared clock required')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    out=ROOT/'current-depth-readiness-v3';out.mkdir(exist_ok=False)
    encode=lambda v:(json.dumps(v,ensure_ascii=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
    def save(v):
        p=out/'query-ledger.tmp';p.write_bytes(encode(v));os.replace(p,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
            view=load_inventory(json.loads(reader(CATALOG)),reader)
            priority=json.loads(reader(PRIORITIES));regional=json.loads(reader(PROJECTIONS))
            if priority['input_sha256'].get(PROJECTIONS)!=hashlib.sha256(reader(PROJECTIONS)).hexdigest() or priority['model_projection_counts_unchanged']!=regional['counts']:raise ValueError('Frozen regional priority/projection parity')
            products=json.loads(reader(TEMPORAL))['products']
            for p in products:
                raw=reader(p['review']);review=json.loads(raw);p['review_sha256']=hashlib.sha256(raw).hexdigest()
                p['review_metadata']={k:copy.deepcopy(v) for k,v in review.items() if k not in ['input_sha256','scientific_review','review','scope','provenance'] and not isinstance(v,list)}
                p['classification_basis']='explicit_pinned_review_index_not_new_source_product_reanalysis'
            before=copy.deepcopy(view);report=join(view,priority,products)
            if view!=before or report['counts']['canonical_references']!=934 or report['counts']['catalog_identities']!=111 or report['counts']['pressure_coordinate_references']!=4:raise ValueError('Exact934refs111owners4pressure;no input changes')
            raw=encode(report)
            if json.loads(raw)!=report:raise ValueError('Full actual report roundtrip')
            fields=list(report['collection_queue'][0]);table=io.StringIO(newline='');writer=csv.DictWriter(table,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(report['collection_queue']);csvraw=table.getvalue().encode('utf8')
            if list(csv.DictReader(io.StringIO(csvraw.decode('utf8'))))!=[{k:str(r[k]) for k in fields} for r in report['collection_queue']]:raise ValueError('Complete collection queue CSV parity')
            summary={'schema':'osw.current-depth-readiness-result.v3','counts':report['counts'],'first_collection_targets':[r for r in report['collection_queue'] if r['queue_tier']<2][:12],'new_depth_references':0,'new_depth_measurements':0,'runtime_changed':False,'full_goal_complete':False};result=encode(summary)
            if json.loads(result)!=summary:raise ValueError('Full result roundtrip')
        total=len(raw)+len(csvraw)+len(result)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole artifact cap')
        for name,data in [('readiness.json',raw),('collection-queue.csv',csvraw),('result.json',result)]: (out/name).write_bytes(data)
        print(json.dumps({'counts':report['counts'],'first_collection_targets':summary['first_collection_targets'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start,'new_measurements':0,'runtime_changed':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
