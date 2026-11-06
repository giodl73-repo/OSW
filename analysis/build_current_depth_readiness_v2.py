"""Join admitted depth references, unchanged regional gaps and temporal reviews."""
import copy,csv,datetime,hashlib,io,json,os,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from compiled_depth_catalog_view_v3 import load_inventory
ROOT=Path(__file__).resolve().parents[1]
OP='research/current-depth-readiness-operator-v2.json'
CATALOG='research/current-depth-reference-inventory-v40.json'
PRIORITIES='research/current-depth-collection-priorities-v1.json'
PROJECTIONS='research/current-depth-route-projection-inventory-v48.json'
TEMPORAL='research/current-depth-temporal-review-index-v1.json'
PARENT_PRIORITIES={'declared_member_discovery_not_parent_scalar','system_scope_requires_component_or_identity_support'}
DIRECT_GAPS={'no_own_supported_regional_case','regional_cases_unresolved'}

def months_from_cases(cases):
    dates=set();unparsed=[]
    for case in cases:
        stamp=case.get('case_scope',{}).get('snapshot_time_utc')
        if stamp is None:continue
        try:dates.add(datetime.datetime.fromisoformat(stamp.replace('Z','+00:00')).date().isoformat())
        except (ValueError,TypeError,AttributeError):
            if stamp not in unparsed:unparsed.append(copy.deepcopy(stamp))
    return sorted(dates),sorted({int(s[5:7]) for s in dates}),sorted(unparsed,key=repr)

def join_base(view,priority,products):
    owners={r['entity_id']:r for r in view['records']};old={r['entity_id']:r for r in priority['records']}
    if len(owners)!=len(view['records']) or set(owners)!=set(old):raise ValueError('Exact catalog/queue identity join required')
    by_owner={owner:[] for owner in owners}
    for ref in view['evidence']:
        if ref['entity_id'] not in by_owner:raise ValueError('Known direct reference owner required')
        by_owner[ref['entity_id']].append(ref)
    grouped={owner:[] for owner in owners};seen=set()
    for p in products:
        if p['id'] in seen or p['entity_id'] not in grouped:raise ValueError('Unique reviewed product and known owner')
        seen.add(p['id']);grouped[p['entity_id']].append(copy.deepcopy(p))
    rows=[]
    for owner,r in owners.items():
        p=old[owner];refs=by_owner[owner];dates,months,unparsed=months_from_cases(p['cases'])
        parent=p['priority_kind'] in PARENT_PRIORITIES
        direct_gap=p['priority_kind'] in DIRECT_GAPS and not parent
        rows.append({'entity_id':owner,'name':r['name'],'identity_level':p['identity_level'],
            'canonical_reference_count':len(refs),'canonical_reference_ids':[e['id'] for e in refs],
            'reference_metric_counts':dict(sorted(Counter(e['metric'] for e in refs).items())),
            'reference_coordinate_unit_counts':dict(sorted(Counter(e['unit'] for e in refs).items())),
            'distinct_tagged_cast_profile_ids':sorted({e['source_cast_profile_id'] for e in refs if e.get('source_cast_profile_id')}),
            'regional_priority_kind':p['priority_kind'],'regional_collection_priority_rank':p['collection_priority_rank'],
            'supported_regional_case_count':p['supported_regional_case_count'],
            'unresolved_regional_case_count':p['unresolved_regional_case_count'],
            'supported_mean_cross_section_count':p['supported_mean_cross_section_count'],
            'supported_adjacent_segment_occurrences':p['regional_supported_adjacent_segment_occurrences'],
            'gap_segment_occurrences':p['regional_gap_segment_occurrences'],
            'regional_snapshot_date_labels':dates,'regional_snapshot_month_labels':months,
            'unparsed_regional_time_labels':unparsed,
            'snapshot_month_labels_establish_seasonal_climatology':False,
            'reviewed_temporal_products':grouped[owner],
            'temporal_index_status':'reviewed_products_indexed_not_physical_annual_range' if grouped[owner] else 'not_in_this_explicit_review_index_other_project_data_not_excluded',
            'parent_requires_single_depth':False if parent else None,
            'direct_current_without_supported_regional_case':direct_gap,
            'next_regional_collection_action':p['next_collection_action'],
            'old_queue_reference_count_superseded':p['source_depth_reference_count'],
            'regional_cases_are_independent_observations':False,'physical_annual_depth_range_m':None,
            'whole_route_physical_depth_m':None,'volume_km3':None,'runtime_changed':False})
    direct=[r['entity_id'] for r in rows if r['direct_current_without_supported_regional_case']]
    return {'schema':'osw.current-depth-readiness.v2','status':'JOINED_REFERENCE_REGIONAL_AND_REVIEWED_TEMPORAL_CAPABILITIES',
        'counts':{'catalog_identities':len(rows),'canonical_references':sum(r['canonical_reference_count'] for r in rows),
            'supported_regional_cases':sum(r['supported_regional_case_count'] for r in rows),
            'unresolved_regional_cases':sum(r['unresolved_regional_case_count'] for r in rows),
            'individual_current_regional_priority_gaps':len(direct),'indexed_temporal_products':len(products),
            'owners_in_explicit_temporal_review_index':sum(bool(r['reviewed_temporal_products']) for r in rows),
            'new_measurements':0,'new_references':0},
        'direct_current_regional_priority_gaps':sorted(direct),'records':rows,
        'interpretation':'Reference counts, regional case occurrences, snapshot month labels and reviewed analytical products describe different capabilities. This explicit temporal registry is not exhaustive. No complete route/physical annual range/volume or new observation claim.',
        'runtime_changed':False,'query_ui_integration_performed':False,'full_goal_complete':False}

def join(view,priority,products):
    report=join_base(view,priority,products);series=view.get('calendar_depth_series',[])
    for row in report['records']:
        row['canonical_calendar_depth_series']=[copy.deepcopy(s) for s in series if s['entity_id']==row['entity_id']]
        row['canonical_calendar_index_scope']='stored_admitted_series_only_not_exhaustive_other_project_data_not_excluded'
    report['canonical_reference_inventory']='research/current-depth-reference-inventory-v40.json'
    report['counts']['canonical_calendar_series']=len(series)
    report['counts']['canonical_calendar_months']=sum(len(s['months']) for s in series)
    report['counts']['canonical_censored_calendar_months']=sum(r['boundary_reference_id'] is None for s in series for r in s['months'])
    report['interpretation']+=' Stored canonical calendar series keep finite boundaries separate from censored support. No interpolation across missing monthly boundaries or assumed annual extrema.'
    return report


def main():
    def stopped(*a):raise SystemExit('Stopped bounded compiled-depth readiness join')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stopped)
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled descriptors only'))
    start=float(os.environ['OSW_DEPTH_READINESS_START'])
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));out=ROOT/'current-depth-readiness-v2';out.mkdir(exist_ok=False)
    encode=lambda v:(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
    def save(v):
        p=out/'query-ledger.json';tmp=p.with_suffix('.tmp');tmp.write_bytes(encode(v));os.replace(tmp,p)
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0)
    reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen readiness input changed:'+p)
            manifest=json.loads(reader(CATALOG));view=load_inventory(manifest,reader)
            priority=json.loads(reader(PRIORITIES));regional=json.loads(reader(PROJECTIONS))
            if priority['input_sha256'].get(PROJECTIONS)!=hashlib.sha256(reader(PROJECTIONS)).hexdigest() or priority['model_projection_counts_unchanged']!=regional['counts']:
                raise ValueError('Old regional queue must bind exact current projection snapshot; no stale geometry reuse')
            products=json.loads(reader(TEMPORAL))['products']
            for p in products:
                raw=reader(p['review']);review=json.loads(raw)
                p['review_sha256']=hashlib.sha256(raw).hexdigest()
                p['review_metadata']={k:copy.deepcopy(v) for k,v in review.items() if k not in ['input_sha256','scientific_review','review','scope','provenance'] and not isinstance(v,list)}
                p['classification_basis']='explicit_pinned_review_index_not_new_source_product_reanalysis'
            report=join(view,priority,products)
            if report['counts']['canonical_references']!=908 or report['counts']['catalog_identities']!=111:raise ValueError('Exact latest canonical catalog required')
            raw=encode(report)
            if json.loads(raw)!=report:raise ValueError('Actual readiness JSON roundtrip')
        table=io.StringIO(newline='');fields=['entity_id','name','identity_level','canonical_reference_count','regional_priority_kind','supported_regional_case_count','unresolved_regional_case_count','supported_adjacent_segment_occurrences','gap_segment_occurrences','direct_current_without_supported_regional_case','temporal_index_status']
        writer=csv.DictWriter(table,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows({k:r[k] for k in fields} for r in report['records'])
        csv_raw=table.getvalue().encode('utf8')
        decoded_rows=list(csv.DictReader(io.StringIO(csv_raw.decode('utf8'))))
        if decoded_rows!=[{k:str(r[k]) for k in fields} for r in report['records']]:raise ValueError('All readiness CSV values must roundtrip')
        if len(raw)+len(csv_raw)+(out/'query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output chunk cap')
        (out/'readiness.json').write_bytes(raw);(out/'readiness.csv').write_bytes(csv_raw)
        print(json.dumps({'counts':report['counts'],'priority_gaps':report['direct_current_regional_priority_gaps'],
            'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_json_bytes':query.ledger['unique_json_bytes'],
            'runtime_changed':False,'cumulative_active_seconds':time.monotonic()-start,'whole_output_bytes':len(raw)+len(csv_raw)+(out/'query-ledger.json').stat().st_size,'full_goal_complete':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
