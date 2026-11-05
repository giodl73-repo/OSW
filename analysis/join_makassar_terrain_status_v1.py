"""Join compiled status strings; never read terrain pixels or native point arrays."""
import copy,csv,hashlib,io,json,os,re,signal,socket,time
from collections import Counter
from pathlib import Path
from compiled_depth_catalog_query_guard_v3 import DescriptorQuery

ROOT=Path(__file__).resolve().parents[1]
OP='research/makassar-terrain-status-join-operator-v1.json'
TERRAIN='research/makassar-etopo-coarse-terrain-screen-v1.csv'
SEGMENTS='research/barents-makassar-conditional-depth-surface-segments-v1.csv'
GEO='research/barents-makassar-conditional-depth-surfaces-v1.geojson'
REVIEW='research/current-depth-makassar-etopo-terrain-source-review-v1.json'
CLEAR='NO_SAMPLED_CONFLICT_NOT_TERRAIN_VALIDATION'
CONFLICT='SAMPLED_CONFLICT_AT_ALL_TESTED_OFFSETS'
SENSITIVE='OFFSET_SENSITIVE_SAMPLED_CONFLICT'
UNKNOWN='NO_FINITE_TERRAIN_SAMPLES_UNKNOWN'
CONDITIONAL='CONDITIONAL_ONLY_COARSE_SCREEN_NOT_VALIDATED'

def encode(x):return (json.dumps(x,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def sha(x):return hashlib.sha256(x).hexdigest()

def strings_csv(raw):
    # Numeric/scenario cells deliberately remain unparsed strings. Only IDs and
    # status categories are used; no native elevations or depth reanalysis.
    return list(csv.DictReader(io.StringIO(raw.decode('utf8'))))

def join(geo,terrain,segments,terrain_sha):
    if geo['type']!='FeatureCollection':raise ValueError('Exact typed source features required')
    fids=[f['id'] for f in geo['features']];tids=[r['id'] for r in terrain];sids=[s['id'] for s in segments]
    if any(len(ids)!=len(set(ids)) for ids in [fids,tids,sids]) or set(fids)!=set(tids):raise ValueError('Every source feature and terrain status exactly once')
    if any(r['status'] not in [CLEAR,CONFLICT,SENSITIVE,UNKNOWN] for r in terrain):raise ValueError('Unknown terrain categories fail closed')
    terrain_by_id={r['id']:(i+2,r) for i,r in enumerate(terrain)};grouped={s:[] for s in sids}
    for f in geo['features']:
        if f['properties']['segment_id'] not in grouped or f['properties']['physical_volume_eligible'] is not False:raise ValueError('Known segment and no physical volume promotion')
        grouped[f['properties']['segment_id']].append(f)
    gates=[]
    for s in segments:
        features=grouped[s['id']];counts=dict(sorted(Counter(terrain_by_id[f['id']][1]['status'] for f in features).items()))
        if s['status'] in ['UNRESOLVED_ENDPOINT_NO_DEPTH_SURFACE_SCENARIO','NO_MATCHED_FOUR_CORNER_DEPTH_SURFACE_SCENARIO']:
            if features:raise ValueError('A source gap cannot acquire geometry')
            status='SOURCE_GAP_NO_DEPTH_SURFACE'
        elif s['status']=='PARTIAL_ASSUMED_DEPTH_SURFACE_SCENARIO':
            if not features:raise ValueError('Every original partial segment must retain patches')
            status='WITHHELD_SAMPLED_TERRAIN_CONFLICT' if counts.get(CONFLICT) else 'WITHHELD_OFFSET_SENSITIVE_TERRAIN_CONFLICT' if counts.get(SENSITIVE) else 'WITHHELD_NO_FINITE_TERRAIN_SAMPLES' if counts.get(UNKNOWN) else CONDITIONAL
        else:raise ValueError('Unknown original segment category')
        gates.append({'segment_id':s['id'],'entity_id':s['entity_id'],'snapshot_time_utc':s['snapshot_time_utc'],'source_status':s['status'],'terrain_gate_status':status,'source_patch_count':len(features),'terrain_patch_status_counts':counts,'source_patch_ids':[f['id'] for f in features],'conditional_segment_volume_presentation_eligible':status==CONDITIONAL,'physical_volume_eligible':False,'terrain_clearance_established':False})
    gates_by_id={g['segment_id']:g for g in gates};out=copy.deepcopy(geo)
    for original,f in zip(geo['features'],out['features']):
        row_number,r=terrain_by_id[f['id']];gate=gates_by_id[f['properties']['segment_id']];props=f['properties']
        added={'terrain_screen_status':r['status'],'terrain_status_source':{'file':TERRAIN,'sha256':terrain_sha,'csv_row_including_header':row_number},'segment_terrain_gate_status':gate['terrain_gate_status'],'conditional_volume_after_terrain_gate_km3':props['conditional_partial_component_volume_km3'] if gate['conditional_segment_volume_presentation_eligible'] else None,'terrain_clearance_established':False}
        if set(added)&set(props):raise ValueError('No overwrite of frozen source properties')
        props.update(added)
        if f['geometry']!=original['geometry'] or any(props[k]!=v for k,v in original['properties'].items()):raise ValueError('Every source geometry/depth/volume property must remain exact')
    out['terrain_review']={'status_source_file':TERRAIN,'status_source_sha256':terrain_sha,'source_credit':'NOAA/NCEI ETOPO2022Global Relief Model doi:10.25921/fd45-gt74;HYCOM Consortium,NRL,COAPS-FSU current-source attribution retained.','interpretation':'All source geometry and original candidate volumes retained. A sampled conflict,sensitivity or absent terrain at any patch withholds the entire source segment volume from conditional presentation. Remaining candidates are conditional interpolation scenarios only;coarse no-conflict is not validation. No patch-volume subtraction or replacement of current bottom with bed.','runtime_changed':False,'full_goal_complete':False}
    counts={'source_features':len(fids),'source_segment_slots':len(sids),'terrain_patch_status_counts':dict(sorted(Counter(r['status'] for r in terrain).items())),'segment_gate_counts':dict(sorted(Counter(g['terrain_gate_status'] for g in gates).items())),'features_withheld_by_whole_segment_gate':sum(f['properties']['conditional_volume_after_terrain_gate_km3'] is None for f in out['features']),'physical_volumes_admitted':0,'new_native_terrain_values_decoded':0,'new_native_velocity_values_decoded':0,'new_provider_requests':0}
    return out,{'schema':'osw.makassar-terrain-reviewed-scenario-gates.v1','counts':counts,'segments':gates,'interpretation':'Metadata/status join of compiled summaries. No native point arrays,raster pixels,provider access,terrain rerun,new volume computation,partial-volume subtraction or physical promotion.','runtime_changed':False,'full_goal_complete':False}

def csv_bytes(rows):
    fields=['segment_id','entity_id','snapshot_time_utc','source_status','terrain_gate_status','source_patch_count','terrain_patch_status_counts','conditional_segment_volume_presentation_eligible','physical_volume_eligible','terrain_clearance_established']
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');w.writeheader()
    for r in rows:w.writerow({k:json.dumps(r[k],separators=(',',':')) if isinstance(r[k],(dict,list,bool)) else r[k] for k in fields})
    return stream.getvalue().encode()

def main():
    start=float(os.environ['OSW_TERRAIN_JOIN_START'])
    def stop(*a):raise TimeoutError('Shared60second typed status join deadline')
    signal.signal(signal.SIGALRM,stop);signal.signal(signal.SIGTERM,stop);elapsed=time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared test/producer clock required')
    signal.alarm(max(1,int(60-elapsed)));socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline compiled statuses only'))
    out=ROOT/'makassar-terrain-reviewed-surfaces-v1';out.mkdir(exist_ok=False)
    def save(v):
        v['combined_numeric_upper_bound']=v['reserved_numeric_tokens']+v.get('csv_string_only_numeric_upper_bound',0);v['combined_unique_bytes']=v['unique_json_bytes']+v.get('csv_unique_bytes',0)
        tmp=out/'query-ledger.tmp';tmp.write_bytes(encode(v));os.replace(tmp,out/'catalog-query-ledger.json')
    query=DescriptorQuery(save,prior_numeric=0,prior_bytes=0);reader=query.reader(lambda p:(ROOT/p).read_bytes())
    try:
        with query.decoding():
            op=json.loads(reader(OP))
            for p,h in op['input_sha256'].items():
                if sha((ROOT/p).read_bytes())!=h:raise ValueError('Exact frozen join input changed:'+p)
            review=json.loads(reader(REVIEW))
            if review['status']!='PASS_COARSE_TERRAIN_SCREEN_FLAGS_TWENTY_TWO_PATCHES_FOR_REVIEW':raise ValueError('Reviewed source screen required')
            terrain_raw=reader(TERRAIN);segments_raw=reader(SEGMENTS)
            # Conservative lexical reservation before CSV string decoding. Count
            # every digit-run,including identifiers and unused scenario strings.
            csv_tokens=sum(len(re.findall(rb'\d+',raw)) for raw in [terrain_raw,segments_raw]);csv_size=len(terrain_raw)+len(segments_raw)
            if csv_size>2500000 or query.ledger['reserved_numeric_tokens']+csv_tokens>250000 or query.ledger['unique_json_bytes']+csv_size>32000000:raise ValueError('Prospective combined CSV/JSON budget')
            query.numeric_cap=250000-csv_tokens;query.byte_cap=32000000-csv_size;query.ledger.update(csv_string_only_numeric_upper_bound=csv_tokens,csv_unique_bytes=csv_size,csv_status_only_no_numeric_cell_conversion=True);save(query.ledger)
            terrain=strings_csv(terrain_raw);segments=strings_csv(segments_raw)
            # One exact hash-pinned,already-compiled GeoJSON is a JSON descriptor
            # container. Keep the generic reader unchanged; decode only this
            # explicit file under the same before-decode JSON guard.
            raw=(ROOT/GEO).read_bytes()
            if sha(raw)!=op['input_sha256'][GEO]:raise ValueError('Exact compiled source GeoJSON')
            geo=json.loads(raw);original=copy.deepcopy(geo);annotated,report=join(geo,terrain,segments,sha(terrain_raw))
            if geo!=original or report['counts']['source_features']!=59 or report['counts']['source_segment_slots']!=24 or report['counts']['terrain_patch_status_counts']!={CLEAR:37,SENSITIVE:1,CONFLICT:21}:raise ValueError('Full original cohort and reviewed terrain counts required')
            report['input_sha256']=op['input_sha256'];gr=encode(annotated);rr=encode(report);table=csv_bytes(report['segments'])
            if json.loads(gr)!=annotated or json.loads(rr)!=report or csv_bytes(json.loads(rr)['segments'])!=table:raise ValueError('Complete annotated GeoJSON/report/CSV roundtrip')
            if len(gr)+len(rr)+len(table)+(out/'catalog-query-ledger.json').stat().st_size>2400000:raise ValueError('Whole output cap')
            for name,data in [('terrain-reviewed-depth-surfaces.geojson',gr),('segment-gates.json',rr),('segment-gates.csv',table)]:(out/name).write_bytes(data)
            print(json.dumps({'counts':report['counts'],'query_numeric_tokens':query.ledger['reserved_numeric_tokens'],'csv_numeric_upper_bound':csv_tokens,'combined_unique_bytes':query.ledger['unique_json_bytes']+csv_size}),flush=True)
    finally:signal.alarm(0)

if __name__=='__main__':main()
