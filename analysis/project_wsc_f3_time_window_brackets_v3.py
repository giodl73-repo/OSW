"""Exploratory native-time-window reconstruction within the original closed case."""
import datetime,hashlib,json,math,os,re,signal,socket,time
from pathlib import Path
from derive_wsc_f3_warm_flow_brackets_v1 import Tables,header,HEADERS,value,bracket,TARGETS,THRESHOLDS
ROOT=Path(__file__).resolve().parents[1]
OP='research/wsc-f3-time-window-operator-v3.json'
PRIOR='research/wsc-f3-offline-results-ledger-v2.json'
RAW='research/source-data/wsc-f3-bounded-preview-v1/preview.html'

def source_time(text):
    stamp=datetime.datetime.fromisoformat(text.replace('Z','+00:00'))
    if stamp.utcoffset() not in (None,datetime.timedelta(0)):raise ValueError('Do not silently change source time zones')
    return stamp.replace(tzinfo=None)

def reconstruct(rows):
    gears=sorted({r[1]['text'] for r in rows if r[8]['text'] or r[9]['text']});profiles=[]
    indexed=[(source_time(r[0]['text']),i,r) for i,r in enumerate(rows)]
    for target in TARGETS:
        when=source_time(target);points=[]
        for gear in gears:
            choices=[(abs((t-when).total_seconds()),t,i,r) for t,i,r in indexed if r[1]['text']==gear and abs((t-when).total_seconds())<=7200]
            if not choices:continue
            offset,stamp,index,row=min(choices,key=lambda x:(x[0],x[1],x[2]))
            z,temp,u,v=(value(row[i]) for i in [2,4,8,9])
            if z is None or not 0<z<1016:raise ValueError('Valid positive native water depth required')
            if temp is not None and not -3<=temp<=40 or any(x is not None and abs(x)>200 for x in [u,v]):raise ValueError('Native unit/plausibility gate')
            points.append({'gear_id':gear,'water_depth_m':z,'temperature_degrees_C':temp,'provider_u_cm_s':u,'provider_v_cm_s':v,
                'source_nominal_time':row[0]['text'],'source_time_offset_seconds':(stamp-when).total_seconds(),'source_preview_row_index':index,'raw_cells':row})
        points.sort(key=lambda p:p['water_depth_m'])
        if len(points)>40 or len({p['water_depth_m'] for p in points})!=len(points):raise ValueError('Bounded distinct native levels')
        times=[source_time(p['source_nominal_time']) for p in points]
        profiles.append({'target_nominal_source_time':target,'time_zone_independently_verified':False,'maximum_allowed_time_offset_seconds':7200,
            'actual_source_time_span_seconds':(max(times)-min(times)).total_seconds() if times else None,'levels':points,
            'profile_kind':'noncontemporaneous_nearest_sample_reconstruction_not_observed_instantaneous_profile'})
    return profiles,gears

def main():
    start=float(os.environ['OSW_F3_WINDOW_START']);out=ROOT/'wsc-f3-time-window-brackets-v3';out.mkdir(exist_ok=False)
    prior=json.loads((ROOT/PRIOR).read_bytes())
    if prior['status']!='CLOSED_CASE_FIRST_NATIVE_ANALYSIS_RETAINED_NO_NEW_ACQUISITION' or prior['case_numeric_upper_bound']!=177160 or prior['remaining_provider_operations']!=0 or prior['attempted_provider_operations']!=2 or prior['provider_case_closed'] is not True:raise ValueError('Same closed original case and full previous accounting required')
    ledger=dict(prior,status='EXPLORATORY_TIME_WINDOW_RECONSTRUCTION_RESERVED',prior_numeric_upper_bound=177160,prior_cumulative_active_seconds=prior['cumulative_active_seconds'],new_provider_operations=0)
    encode=lambda v:(json.dumps(v,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    def save():(out/'ledger.json').write_bytes(encode(ledger))
    def stopped(*a):raise TimeoutError('Original cumulative case deadline or SIGTERM')
    elapsed=prior['cumulative_active_seconds']+time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Same original shared source-case clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save()
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Acquisition remains closed; offline only'))
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        raw=(ROOT/RAW).read_bytes();source_charge=len(re.findall(rb'[-+]?\d+(?:\.\d+)?',raw))
        if prior['case_numeric_upper_bound']+source_charge+10000>250000:raise ValueError('Original scalar cap forbids an additional retained-source pass')
        ledger.update(additional_source_lexical_passes=1,additional_source_lexical_numeric_upper_bound=source_charge,additional_selected_output_numeric_allowance=10000,case_numeric_upper_bound=prior['case_numeric_upper_bound']+source_charge+10000);save()
        parser=Tables();parser.feed(raw.decode('utf8'));tables=[]
        for table in parser.tables:
            for i,row in enumerate(table):
                if [header(c) for c in row]==HEADERS:tables.append(table[i+1:])
        if len(tables)!=1 or len(tables[0])!=2000 or any(len(r)!=10 for r in tables[0]):raise ValueError('Same exact bounded native table and units')
        profiles,gears=reconstruct(tables[0]);complete=all(len(p['levels'])>=2 for p in profiles)
        selected=sum(len(p['levels']) for p in profiles)
        if prior['decoded_cells']+selected*10>20000 or prior['measurement_nodes']+selected*3>6000:raise ValueError('Original cumulative selected cell/node cap')
        records=[]
        for p in profiles:
            for threshold in THRESHOLDS:
                r=bracket({'time_utc':p['target_nominal_source_time'],'levels':p['levels'] if complete else []},threshold)
                r['target_nominal_source_time']=r.pop('time_utc');r.update(evidence_kind='exploratory_time_window_reconstruction',actual_source_time_span_seconds=p['actual_source_time_span_seconds'],time_zone_independently_verified=False,instantaneous_observed_profile=False)
                if not complete:r['status']='INSUFFICIENT_NATIVE_LEVELS_IN_TIME_WINDOW'
                records.append(r)
        report={'schema':'osw.wsc-f3-time-window-brackets.v3','status':'EXPLORATORY_NONCONTEMPORANEOUS_DEPTH_BRACKETS_OR_EXPLICIT_GAPS','source_doi':'10.1594/PANGAEA.800346',
            'original_exact_time_result':'research/wsc-f3-exact-time-native-results-v2.json','profiles':profiles,'records':records,'cohort_complete':complete,'velocity_gears_in_preview':gears,
            'qualifications':['This exploratory operator was declared after exact timestamps yielded one level per date; the exact-time null results remain unchanged.','Nearest same-gear source sample within inclusive2h of the same three predeclared targets; ties choose earlier source time, never stronger velocity or warmer water.','Source timestamps are nominal provider times; UTC interpretation is not independently established. Each reconstruction retains actual sample times/offsets and at most4h total spread.','A time-window reconstruction is not an observed simultaneous vertical profile. Variation during the window is unquantified; no statistical or physical uncertainty interval is inferred.','Warm T>2degC and provider northward component thresholds5/10/20cm/s define a selected component;10cm/s is primary. These are methodological variants, not full-current bottom or seasonal extrema.','Sparse vertical connectivity is conditional; no midpoint, interpolated depth, missing-gap fill, physical thickness or volume. Original flag/unit/gap gates retained.','Only the publisher first2000 rows, not complete annual data. No source retrieval, new case, or budget renewal; all raw/text/selected-field passes are cumulatively charged.'],
            'canonical_reference_admission_performed':False,'runtime_changed':False,'full_goal_complete':False}
        encoded=encode(report);output_charge=2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',encoded))+3000
        if output_charge>10000 or json.loads(encoded)!=report:raise ValueError('Reserved output allowance and complete actual JSON roundtrip')
        (out/'time-window-brackets.json').write_bytes(encoded)
        ledger.update(status='CLOSED_ORIGINAL_CASE_EXPLORATORY_RECONSTRUCTIONS_RETAINED',decoded_cells=prior['decoded_cells']+selected*10,measurement_nodes=prior['measurement_nodes']+selected*3,
            native_numeric_values_decoded=prior['native_numeric_values_decoded']+selected*4,source_native_field_parse_attempts=2,time_window_profile_dates=len(profiles),time_window_native_levels=selected,new_depth_references=0)
        save()
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole output cap')
        print(json.dumps({'cohort_complete':complete,'selected_levels':selected,'records':records}),flush=True)
    except BaseException as e:
        ledger.update(status='TIME_WINDOW_RECONSTRUCTION_FAILED_NO_REPLAY',time_window_error_type=type(e).__name__,time_window_error=str(e)[:400]);raise
    finally:
        ledger['cumulative_active_seconds']=prior['cumulative_active_seconds']+time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
