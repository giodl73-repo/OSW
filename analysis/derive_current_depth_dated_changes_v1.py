"""Dated section diagnostics from the admitted almanac, not seasonal interpolation."""
import copy,datetime,hashlib,json,math,os,signal,socket,time
from collections import Counter,defaultdict
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery
from build_current_depth_almanac_v2 import expand_report
ROOT=Path(__file__).resolve().parents[1]
SOURCE='research/current-depth-almanac-v2.json'
OP='research/current-depth-dated-changes-operator-v1.json'
METRICS=['upper_depth_m','lower_depth_m','thickness_m']
FINITE='finite_component_depth_pair'
STATES={FINITE,'censored_component_depth_pair','unresolved_original_axis'}
finite=lambda x:type(x) in (int,float) and math.isfinite(x)
encode=lambda x:(json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def stamp(text):
    date=datetime.datetime.fromisoformat(text.replace('Z','+00:00'))
    if date.tzinfo is None or date.utcoffset()!=datetime.timedelta(0):raise ValueError('Exact UTC timestamp required')
    return date

def key(row):
    return tuple(row[k] for k in ['dataset_id','entity_id','section_id','component_bearing_degrees_true','velocity_threshold_m_s','source_rule_operator_file'])

def verify_point(row):
    if row['estimate_status'] not in STATES or any(row.get(k) is not None for k in ['physical_current_depth_m','volume_km3']) or row.get('whole_route_interpolation_allowed') is not False or row.get('independent_current_axis_validated') is not False:raise ValueError('Admitted diagnostic only, never physical or interpolated')
    stamp(row['snapshot_time_utc'])
    if row['estimate_status']==FINITE:
        if not all(finite(row[k]) and row[k]>=0 for k in METRICS) or row['thickness_m']<=0 or not math.isclose(row['lower_depth_m']-row['upper_depth_m'],row['thickness_m'],abs_tol=1e-8,rel_tol=1e-10):raise ValueError('Exact finite paired thickness required')
        bounds=row['sampling_thickness_bounds_m']
        if not isinstance(bounds,list) or len(bounds)!=2 or not all(finite(v) for v in bounds) or not 0<=bounds[0]<=row['thickness_m']<=bounds[1]:raise ValueError('Enclosing original sampling bracket required')
    elif row['thickness_m'] is not None or row['sampling_thickness_bounds_m'] is not None:raise ValueError('Unknown thickness and brackets stay null')
    if row['estimate_status']=='unresolved_original_axis':
        if any(row[k] is not None for k in METRICS+['sampled_lon_lat','native_supported_minimum_component_span_m']):raise ValueError('Unresolved location/depth/support stay null')
    else:
        xy=row['sampled_lon_lat']
        if not isinstance(xy,list) or len(xy)!=2 or not all(finite(v) for v in xy) or not -180<=xy[0]<=180 or not -90<=xy[1]<=90:raise ValueError('Original geographic location required')
    for name in METRICS+['native_supported_minimum_component_span_m']:
        if row[name] is not None and (not finite(row[name]) or row[name]<0):raise ValueError('Finite nonnegative descriptor or null')

def summarize_series(rows,indices):
    if not rows or len({key(r) for r in rows})!=1:raise ValueError('One exact dataset/owner/section/frame/cutoff/operator only')
    for row in rows:verify_point(row)
    ordered=sorted(rows,key=lambda r:stamp(r['snapshot_time_utc']))
    if len({stamp(r['snapshot_time_utc']) for r in ordered})!=len(ordered):raise ValueError('Duplicate case timestamp cannot be silently collapsed')
    group_key=key(ordered[0]);identity='depth-series:'+sha(encode(list(group_key)))[:20]
    points=[]
    for row in ordered:
        fields=['id','entity_id','section_id','snapshot_time_utc','estimate_status','sampled_lon_lat',*METRICS,'sampling_thickness_bounds_m','native_supported_minimum_component_span_m','source_status','original_csv','original_csv_sha256','original_csv_data_row_index','source_compiled_descriptor_file','source_compiled_descriptor_sha256','source_descriptor_pointer']
        point={k:copy.deepcopy(row[k]) for k in fields};point['source_expanded_entry_index']=indices[row['id']];points.append(point)
    comparisons=[]
    for a,b in zip(ordered,ordered[1:]):
        comparison={'from_id':a['id'],'to_id':b['id'],'from_time_utc':a['snapshot_time_utc'],'to_time_utc':b['snapshot_time_utc'],
            'elapsed_days':(stamp(b['snapshot_time_utc'])-stamp(a['snapshot_time_utc'])).total_seconds()/86400,
            'status':'not_comparable_unresolved_or_censored','sampled_location_unchanged':None,
            'selected_profile_depth_change_m':{k:None for k in METRICS},'fixed_grid_depth_change_m':None,
            'physical_depth_change_m':None,'annual_range_m':None}
        if a['estimate_status']==FINITE and b['estimate_status']==FINITE:
            same=a['sampled_lon_lat']==b['sampled_lon_lat'];delta={k:b[k]-a[k] for k in METRICS}
            comparison.update(status='same_native_grid_location_finite_diagnostic_change' if same else 'selected_profile_changed_location_finite_diagnostic_change',sampled_location_unchanged=same,selected_profile_depth_change_m=delta,fixed_grid_depth_change_m=copy.deepcopy(delta) if same else None)
        comparisons.append(comparison)
    usable=[r for r in ordered if r['estimate_status']==FINITE]
    ranges={k:[min(r[k] for r in usable),max(r[k] for r in usable)] if len(usable)>=2 else None for k in METRICS}
    bracket=[min(r['sampling_thickness_bounds_m'][0] for r in usable),max(r['sampling_thickness_bounds_m'][1] for r in usable)] if len(usable)>=2 else None
    return {'id':identity,'dataset_id':group_key[0],'entity_id':group_key[1],'section_id':group_key[2],
        'component_bearing_degrees_true':group_key[3],'velocity_threshold_m_s':group_key[4],'source_rule_operator_file':group_key[5],
        'points':points,'adjacent_declared_date_comparisons':comparisons,
        'counts':dict(Counter(r['estimate_status'] for r in ordered)),
        'finite_pair_dated_sample_count':len(usable),'finite_pair_dated_sample_ranges_m':ranges,
        'finite_pair_ranges_use_one_native_grid_location':len({tuple(r['sampled_lon_lat']) for r in usable})==1 if len(usable)>=2 else None,
        'smallest_enclosing_finite_pair_sampling_thickness_bracket_m':bracket,
        'range_population':'finite_paired_selected_profiles_at_retained_declared_dates_only_censored_and_unresolved_cases_retained_separately',
        'range_is_continuous_support_or_physical_uncertainty':False,'annual_extrema_established':False,
        'physical_annual_depth_range_m':None,'seasonal_climatology_established':False,'volume_km3':None}

def build(source):
    if source['schema']!='osw.current-depth-almanac.expanded.v1' or source.get('runtime_changed') is not False or source.get('full_goal_complete') is not False:raise ValueError('Admitted expanded almanac only')
    rows=[r for r in source['entries'] if r['record_type']=='regional_depth_estimate']
    owners=[r for r in source['entries'] if r['record_type']=='current'];indices={r['id']:i for i,r in enumerate(source['entries']) if r['record_type']=='regional_depth_estimate'}
    if len(indices)!=len(rows) or len({r['entity_id'] for r in owners})!=len(owners) or any(r['entity_id'] not in {o['entity_id'] for o in owners} for r in rows):raise ValueError('Unique cases and known canonical identities')
    if source['counts'].get('regional_estimates',len(rows))!=len(rows) or source['counts'].get('currents',len(owners))!=len(owners):raise ValueError('Declared source case/identity counts must reconcile')
    grouped=defaultdict(list)
    for row in rows:grouped[key(row)].append(row)
    series=[summarize_series(grouped[k],indices) for k in sorted(grouped)]
    if len({s['id'] for s in series})!=len(series) or sum(len(s['points']) for s in series)!=len(rows):raise ValueError('Complete one-time case accounting')
    current_index=[{'entity_id':o['entity_id'],'name':o['name'],'identity_level':o['identity_level'],'series_ids':[s['id'] for s in series if s['entity_id']==o['entity_id']],'scope':'explicit_admitted_paired_registry_not_exhaustive_no_series_does_not_mean_no_depth_data','physical_annual_depth_range_m':None,'volume_km3':None} for o in owners]
    comparisons=[c for s in series for c in s['adjacent_declared_date_comparisons']]
    counts={'canonical_identities':len(owners),'source_regional_cases':len(rows),'source_datasets':len({r['dataset_id'] for r in rows}),'section_diagnostic_series':len(series),
        'series_with_two_or_more_finite_pairs':sum(s['finite_pair_dated_sample_count']>=2 for s in series),
        'adjacent_declared_date_comparisons':len(comparisons),**dict(Counter(c['status'] for c in comparisons))}
    return {'schema':'osw.current-depth-dated-changes.v1','counts':counts,'current_index':current_index,'series':series,
        'source_almanac':SOURCE,'source_counts_unchanged':copy.deepcopy(source['counts']),
        'interpretation':'Finite-pair ranges describe only retained dated diagnostics at the same editorial section/frame/cutoff/operator. Selected grid location can move. Fixed-grid changes are emitted only for identical sampled lon/lat and two finite pairs. Same-grid model changes remain conditional component diagnostics, not validated physical-current changes. Censored bounds are not finite observations, unresolved cases stay present and no gap is bridged. No interpolation, annual extrema, physical uncertainty, continuous range, independent-observation count, depth-pressure conversion, parent/member sum or physical volume.',
        'new_observations':0,'new_canonical_references':0,'runtime_changed':False,'full_goal_complete':False}

def main():
    start=float(os.environ['OSW_DEPTH_DATED_CHANGES_START'])
    def stop(*a):raise TimeoutError('Shared60second tests/producer deadline')
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
    if not 0<=time.monotonic()-start<30:raise ValueError('Shared synthetic-test/producer clock')
    signal.alarm(max(1,int(60-(time.monotonic()-start))));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline admitted almanac query only'))
    out=ROOT/'current-depth-dated-changes-v1';out.mkdir(exist_ok=False)
    def save(value):
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(value));os.replace(tmp,out/'query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for path,pin in op['input_sha256'].items():
                if sha((ROOT/path).read_bytes())!=pin:raise ValueError('Frozen input changed:'+path)
            source=expand_report(json.loads(reader(SOURCE)));report=build(source)
            if source['counts']!=op['expected_source_counts']:raise ValueError('Complete admitted926case/111identity/21dataset scope required')
            report['source_almanac_sha256']=sha(reader(SOURCE));raw=encode(report)
            if json.loads(raw)!=report or encode(json.loads(raw))!=raw:raise ValueError('Full actual scientific JSON roundtrip')
        total=len(raw)+(out/'query-ledger.json').stat().st_size
        if total>2400000:raise ValueError('Whole output cap')
        (out/'dated-changes.json').write_bytes(raw)
        print(json.dumps({'counts':report['counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'query_bytes':query.ledger['unique_json_bytes'],'whole_output_bytes':total,'cumulative_active_seconds':time.monotonic()-start,'new_observations':0,'runtime_changed':False,'full_goal_complete':False}))
    finally:signal.alarm(0)

if __name__=='__main__':main()
