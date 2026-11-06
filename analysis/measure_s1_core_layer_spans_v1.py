"""Measure sign- and rotation-invariant local flow spans, not absolute depths."""
import csv,datetime,hashlib,io,json,math,os,re,signal,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path
from capture_gaspe1991_adcp_info_v1 import NoRedirect
ROOT=Path(__file__).resolve().parents[1]
OP='research/s1-core-layer-span-operator-v1.json'
PRIOR='research/s1-mooring-adcp-metadata-ledger-v1.json'
META='research/s1-mooring-adcp-variable-metadata-v1.json'
COLUMNS=['time','depth','CurrVelE_ADCP','CurrVelN_ADCP','Curr_QC','latitude','longitude']
QUERY=','.join(COLUMNS)+'&time>=2023-07-10T00:00:00Z&time<2023-07-11T00:00:00Z&orderBy("time,depth")'
URL='https://data.iadc.cnr.it/erddap/tabledap/8e2f4c44-d784-40ed-94aa-ef5fa505761a.csv?'+urllib.parse.quote(QUERY,safe=',&=<>:')
THRESHOLDS=(0.05,0.10,0.20)
def tokens(raw):return len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))

def profiles_from_csv(raw):
    rows=list(csv.reader(io.StringIO(raw.decode('utf8'))))
    if len(rows)<3 or rows[0]!=COLUMNS or rows[1]!=['UTC','m','meters for seconds','meters for seconds','','degrees_north','degrees_east']:raise ValueError('Exact provider CSV columns and units required')
    rows=rows[2:]
    if len(rows)>6000 or len(rows)*len(COLUMNS)>20000 or any(len(r)!=7 for r in rows):raise ValueError('Prospective decoded-cell/node bound')
    grouped={}
    for row in rows:grouped.setdefault(row[0],[]).append(row)
    if not 3<=len(grouped)<=150 or any(not 2<=len(p)<=40 for p in grouped.values()):raise ValueError('Original selected profile/level bounds before numeric decoding')
    if len(rows)*len(THRESHOLDS)>6000:raise ValueError('Shared threshold measurement-node cap')
    prospective=12*len(rows)+10*len(grouped)*len(THRESHOLDS)+5000
    if prospective+2*tokens(raw)+4240>250000:raise ValueError('Prospective cumulative scalar upper bound')
    result=[]
    for stamp,source in sorted(grouped.items()):
        when=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))
        if not datetime.datetime(2023,7,10,tzinfo=datetime.timezone.utc)<=when<datetime.datetime(2023,7,11,tzinfo=datetime.timezone.utc):raise ValueError('Exact source-day scope required')
        levels=[]
        for row in source:
            z,u,v=float(row[1]),float(row[2]),float(row[3]);qc=int(row[4]);lat,lon=float(row[5]),float(row[6])
            if not math.isfinite(z) or not -390<z<-141 or abs(lat-76.4455)>1e-8 or abs(lon-13.940816666666667)>1e-8:raise ValueError('Exact site and native coordinate domain required; no sign correction')
            levels.append({'native_vertical_coordinate_m':z,'provider_u_m_s':u if math.isfinite(u) else None,'provider_v_m_s':v if math.isfinite(v) else None,'provider_current_qc':qc})
        levels.sort(key=lambda r:r['native_vertical_coordinate_m'])
        if len({r['native_vertical_coordinate_m'] for r in levels})!=len(levels):raise ValueError('One native bin per profile required')
        result.append({'time_utc':stamp,'latitude_degrees_north':lat,'longitude_degrees_east':lon,'levels':levels})
    return result,prospective

def layer(profile,threshold):
    levels=profile['levels']
    valid=lambda r:r['provider_current_qc']==1 and r['provider_u_m_s'] is not None and r['provider_v_m_s'] is not None
    good=[i for i,r in enumerate(levels) if valid(r)]
    result={'time_utc':profile['time_utc'],'threshold_m_s':threshold,'accepted_provider_qc':[1],
        'metric':'sampled_core_connected_velocity_component_vertical_span',
        'span_m':None,'native_coordinate_endpoints_m':None,'maximum_adjacent_gap_m':10,
        'physical_current_thickness_m':None,'absolute_current_depth_m':None,'current_owner':None,
        'annual_range_m':None,'volume_m3':None,'physical_bottom_established':False,
        'rotation_and_vertical_sign_invariant':True,'source_angular_reference_independently_verified':False}
    if not good:return dict(result,status='NO_GOOD_FINITE_CURRENT_BINS')
    core=max(good,key=lambda i:math.hypot(levels[i]['provider_u_m_s'],levels[i]['provider_v_m_s']))
    u,v=levels[core]['provider_u_m_s'],levels[core]['provider_v_m_s'];speed=math.hypot(u,v)
    result['core_speed_m_s']=speed
    if speed<threshold:return dict(result,status='CORE_BELOW_DECLARED_THRESHOLD')
    def admitted(i):
        r=levels[i]
        return valid(r) and (r['provider_u_m_s']*u+r['provider_v_m_s']*v)/speed>=threshold
    left=right=core
    while left>0 and levels[left]['native_vertical_coordinate_m']-levels[left-1]['native_vertical_coordinate_m']<=10 and admitted(left-1):left-=1
    while right+1<len(levels) and levels[right+1]['native_vertical_coordinate_m']-levels[right]['native_vertical_coordinate_m']<=10 and admitted(right+1):right+=1
    def stop(i,adjacent):
        if not 0<=adjacent<len(levels):return 'SAMPLED_COORDINATE_DOMAIN_END'
        if abs(levels[i]['native_vertical_coordinate_m']-levels[adjacent]['native_vertical_coordinate_m'])>10:return 'VERTICAL_SAMPLING_GAP'
        if not valid(levels[adjacent]):return 'QC_OR_MISSING_VELOCITY'
        return 'COMPONENT_THRESHOLD_BRACKET_NO_INTERPOLATION'
    result.update(native_coordinate_endpoints_m=[levels[left]['native_vertical_coordinate_m'],levels[right]['native_vertical_coordinate_m']],selected_connected_bins=right-left+1,
        numeric_minimum_end_stop=stop(left,left-1),numeric_maximum_end_stop=stop(right,right+1),
        sampling_censored_at_either_numeric_end=left==0 or right==len(levels)-1)
    if left==right:return dict(result,status='ONE_BIN_NO_RESOLVED_VERTICAL_SPAN')
    return dict(result,status='SAMPLED_CONNECTED_SPAN_NOT_PHYSICAL_LAYER_THICKNESS',span_m=levels[right]['native_vertical_coordinate_m']-levels[left]['native_vertical_coordinate_m'])

def main():
    start=float(os.environ['OSW_S1_SPANS_START']);out=ROOT/'s1-core-layer-spans-v1';out.mkdir(exist_ok=False)
    prior=json.loads((ROOT/PRIOR).read_bytes())
    if prior['status']!='ORIGINAL_METADATA_RETAINED_NATIVE_SELECTION_PENDING' or prior['case_numeric_upper_bound']!=4240 or prior['attempted_provider_operations']!=1 or prior['remaining_provider_operations']!=7 or prior['provider_case_closed']:raise ValueError('Exact original open S1 case required')
    ledger=dict(prior,status='NATIVE_DAY_SELECTION_RESERVED',prior_metadata_raw_bytes=prior['raw_bytes'],prior_numeric_upper_bound=prior['case_numeric_upper_bound'],prior_active_seconds=prior['cumulative_active_seconds'])
    encode=lambda v:(json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
    def save():(out/'ledger.json').write_bytes(encode(ledger))
    def stopped(*a):raise TimeoutError('Cumulative original S1 case deadline or SIGTERM')
    elapsed=prior['cumulative_active_seconds']+time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer cumulative clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save();response=None
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        metadata=json.loads((ROOT/META).read_bytes());z=metadata['variables']['depth']['attributes'];g=metadata['global_attributes']
        if z['positive']!='down' or z['actual_range']!='-389.7199993133545, -141.7199993133545' or g['license']!='CC-BY-4.0':raise ValueError('Exact unresolved signed coordinates and licensed source required')
        ledger.update(status='NATIVE_REQUEST_RESERVED_TARGET_CLOSED',source_url=URL,attempted_provider_operations=2,remaining_provider_operations=6);save()
        request=urllib.request.Request(URL,headers={'User-Agent':'OSW-bounded-local-flow-span/1.0','Accept':'text/csv','Accept-Encoding':'identity'})
        try:response=urllib.request.build_opener(NoRedirect()).open(request,timeout=25)
        except urllib.error.HTTPError as error:response=error
        raw=response.read(1000001);(out/'primary-data.csv').write_bytes(raw)
        ledger.update(http_status=response.code,native_raw_bytes=len(raw),native_raw_sha256=hashlib.sha256(raw).hexdigest(),raw_bytes=prior['raw_bytes']+len(raw));save()
        if response.code!=200 or len(raw)>1000000 or ledger['raw_bytes']>1600000:raise ValueError('Native response HTTP/byte gate')
        if 2*tokens(raw)+prior['case_numeric_upper_bound']+5000>250000:raise ValueError('Predecode original numeric cap')
        ledger['native_numeric_reservation_upper_bound']=250000-prior['case_numeric_upper_bound'];save()
        profiles,prospective=profiles_from_csv(raw)
        report={'schema':'osw.s1-local-core-connected-layer-spans.v1','source_url':URL,'source_metadata_sha256':metadata['raw_sha256'],
            'status':'LOCAL_SIGN_AND_ROTATION_INVARIANT_SPANS_ABSOLUTE_DEPTH_UNQUALIFIED','records':[layer(p,t) for p in profiles for t in THRESHOLDS],
            'qualifications':['Native depth coordinates are negative despite provider positive-down declaration; no sign correction or absolute depth inferred.','Provider u/v components are used in a core-relative projection invariant under common horizontal rotation; no true-north or magnetic correction is assumed.','QC1 only; QC gaps/missing bins interrupt connectivity. No gap filling, bin-center interpolation or depth conversion.','Each threshold uses the same original profiles and shared case budget. Sampled connected spans are not physical full-layer thicknesses or current bottoms.','Instantaneous dated local profiles are not daily means, seasonal extrema or an annual cycle. Tidal effects are not removed.','S1 lies in a region with multiple water sources; no named-current owner or water-mass attribution is admitted.'],
            'current_depth_reference_admitted':False,'physical_current_thickness_established':False,'runtime_changed':False,'full_goal_complete':False}
        packet={'schema':'osw.s1-observed-native-velocity-profiles.v1','source_url':URL,'raw_sha256':ledger['native_raw_sha256'],'profiles':profiles,'native_coordinate_sign_resolved':False,'current_identity_assignment_performed':False}
        packetraw,reportraw=encode(packet),encode(report)
        bound=max(prior['case_numeric_upper_bound']+2*tokens(raw)+prospective,prior['case_numeric_upper_bound']+2*tokens(raw)+2*tokens(packetraw)+2*tokens(reportraw)+5000)
        if bound>250000:raise ValueError('Cumulative scalar cap including output and roundtrip')
        if json.loads(packetraw)!=packet or json.loads(reportraw)!=report:raise ValueError('Actual full native packet and span JSON roundtrip')
        (out/'profiles.json').write_bytes(packetraw);(out/'layer-spans.json').write_bytes(reportraw)
        ledger.update(status='LOCAL_INVARIANT_SPANS_RETAINED_CASE_CLOSED_ABSOLUTE_DEPTH_UNQUALIFIED',provider_case_closed=True,remaining_provider_operations=0,unused_provider_operations_surrendered=6,
            case_numeric_upper_bound=bound,selected_profiles=len(profiles),maximum_selected_levels=max(len(p['levels']) for p in profiles),
            decoded_cells=sum(len(p['levels']) for p in profiles)*7,measurement_nodes=sum(len(p['levels']) for p in profiles)*len(THRESHOLDS),
            native_array_values_decoded=sum(len(p['levels']) for p in profiles)*7,span_records=len(report['records']),
            resolved_sampled_spans=sum(r['span_m'] is not None for r in report['records']),new_depth_references=0)
        save()
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole scientific output cap')
        print(json.dumps({'selected_profiles':ledger['selected_profiles'],'span_records':ledger['span_records'],'resolved_sampled_spans':ledger['resolved_sampled_spans'],'example_records':report['records'][:3]}),flush=True)
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        if response is not None:response.close()
        ledger['cumulative_active_seconds']=prior['cumulative_active_seconds']+time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
