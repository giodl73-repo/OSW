"""Dated native-level brackets for an explicitly selected warm northward component."""
import datetime,hashlib,json,math,os,re,signal,socket,time
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OP='research/wsc-f3-warm-flow-bracket-operator-v1.json'
PRIOR='research/wsc-f3-original-preview-ledger-v1.json'
RAW='research/source-data/wsc-f3-bounded-preview-v1/preview.html'
TARGETS=('2004-07-21T00:00','2004-07-22T00:00','2004-07-23T00:00')
HEADERS=['Date/Time','GearID','Depthwater[m]','Press[dbar]','Temp[\u00b0C]','Sal','Curvelhor[cm/s]','DIR[deg]','CurvelU[cm/s]','CurvelV[cm/s]']
THRESHOLDS=(5.,10.,20.)
NUMBER=re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?\Z')

class Tables(HTMLParser):
    def __init__(self):super().__init__();self.tables=[];self.table=None;self.row=None;self.cell=None;self.depth=0
    def handle_starttag(self,tag,attrs):
        if tag=='table':
            self.depth+=1
            if self.depth==1:self.table=[]
        elif self.depth==1:
            if tag=='tr':self.row=[]
            elif tag in ('td','th') and self.row is not None:self.cell={'text':[],'attributes':[dict(attrs)]}
            elif self.cell is not None:self.cell['attributes'].append(dict(attrs))
    def handle_data(self,text):
        if self.cell is not None:self.cell['text'].append(text)
    def handle_endtag(self,tag):
        if tag=='table':
            if self.depth==1:self.tables.append(self.table);self.table=None
            self.depth-=1
        elif self.depth==1:
            if tag in ('td','th') and self.cell is not None:
                self.cell['text']=' '.join(' '.join(self.cell['text']).split());self.row.append(self.cell);self.cell=None
            elif tag=='tr' and self.row is not None:
                self.table.append(self.row);self.row=None
                if len(self.table)>2100:raise ValueError('Published preview row bound')

def header(cell):return re.sub(r'\s+','',re.sub(r'^\d+\s*','',cell['text']))
def value(cell):
    text=cell['text']
    # Publisher quality flags (?, /, *, #, <, >, averaged/std-dev) remain
    # nonnumeric. Never strip a flag or convert a censor bound into a point.
    if not NUMBER.fullmatch(text):return None
    if any(re.search(r'question|invalid|unknown|quality.flag|outlier|interpolat|averaged',str(a),re.I) for a in cell['attributes']):return None
    x=float(text)
    return x if math.isfinite(x) else None

def selected_profiles(raw):
    parsed=Tables();parsed.feed(raw.decode('utf8'));matches=[]
    for table in parsed.tables:
        for i,row in enumerate(table):
            if [header(c) for c in row]==HEADERS:matches.append(table[i+1:])
    if len(matches)!=1:raise ValueError('One exact native table with declared parameter identities and units required')
    rows=matches[0]
    if not 1<=len(rows)<=2000 or any(len(r)!=10 for r in rows):raise ValueError('Exact bounded native table shape')
    velocity_gears={r[1]['text'] for r in rows if r[8]['text'] or r[9]['text']}
    selected={stamp:[] for stamp in TARGETS}
    for row in rows:
        stamp=row[0]['text'].removesuffix('Z')
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:00',stamp):stamp=stamp[:-3]
        if stamp in selected and row[1]['text'] in velocity_gears:selected[stamp].append(row)
    if any(len(v)>40 for v in selected.values()):raise ValueError('Selected native levels per profile')
    if sum(len(v)*10 for v in selected.values())>20000 or sum(len(v)*len(THRESHOLDS) for v in selected.values())>6000:raise ValueError('Cumulative selected cell/node cap')
    profiles=[]
    for stamp,items in selected.items():
        points=[]
        for row in items:
            z,temp,u,v=(value(row[i]) for i in [2,4,8,9])
            if z is None or not 0<z<1016:raise ValueError('Actual positive water depth in metres required; no pressure substitution')
            if temp is not None and not -3<=temp<=40:raise ValueError('Temperature plausibility gate')
            if any(x is not None and abs(x)>200 for x in [u,v]):raise ValueError('Component velocity plausibility gate in native cm/s')
            points.append({'gear_id':row[1]['text'],'water_depth_m':z,'temperature_degrees_C':temp,'provider_u_cm_s':u,'provider_v_cm_s':v,'raw_cells':row})
        points.sort(key=lambda p:p['water_depth_m'])
        if len({p['water_depth_m'] for p in points})!=len(points):raise ValueError('Distinct native current-meter levels required')
        profiles.append({'time_utc':stamp+':00Z','latitude_degrees_north':78.8383,'longitude_degrees_east':7.9925,'levels':points,'preview_scope':'first_2000_publisher_rows_only'})
    return profiles,len(rows),sorted(velocity_gears)

def bracket(profile,cutoff):
    levels=profile['levels'];good=lambda p:p['temperature_degrees_C'] is not None and p['provider_v_cm_s'] is not None
    admitted=lambda p:good(p) and p['temperature_degrees_C']>2. and p['provider_v_cm_s']>=cutoff
    passing=[i for i,p in enumerate(levels) if admitted(p)]
    result={'entity_id':'current:west-spitsbergen','time_utc':profile['time_utc'],'northward_threshold_cm_s':cutoff,'temperature_threshold_degrees_C':2.,'temperature_comparison':'strictly_greater','velocity_comparison':'greater_or_equal',
        'range_m':None,'lower_bound_m':None,'lower_bound_exclusive':False,'approximate_value_m':None,
        'upper_boundary_m':None,'lower_boundary_m':None,'thickness_m':None,'annual_range_m':None,'uncertainty_m':None,'volume_m3':None,
        'physical_current_bottom_established':False,'source_frame_basis':'provider_published_north_south_component_not_independently_recalibrated','full_current_representative':False}
    if not passing:return dict(result,status='NO_SUPPORTED_WARM_NORTHWARD_CURRENT_SAMPLE_IN_SELECTED_PROFILE')
    core=max(passing,key=lambda i:levels[i]['provider_v_cm_s']);end=core
    while end+1<len(levels) and levels[end+1]['water_depth_m']-levels[end]['water_depth_m']<=600 and admitted(levels[end+1]):end+=1
    p=levels[end];result.update(deepest_connected_admitted_sample={k:v for k,v in p.items() if k!='raw_cells'},core_gear_id=levels[core]['gear_id'])
    if end+1==len(levels):return dict(result,status='LOWER_SUPPORT_CENSORED_AT_LAST_SAMPLED_CURRENT_METER',lower_bound_m=p['water_depth_m'])
    below=levels[end+1];result['next_sample']={k:v for k,v in below.items() if k!='raw_cells'}
    if below['water_depth_m']-p['water_depth_m']>600:return dict(result,status='LOWER_SUPPORT_UNRESOLVED_LARGE_VERTICAL_GAP',lower_bound_m=p['water_depth_m'])
    if not good(below):return dict(result,status='LOWER_SUPPORT_UNRESOLVED_MISSING_OR_FLAGGED_SAMPLE',lower_bound_m=p['water_depth_m'])
    return dict(result,status='CONDITIONAL_WARM_NORTHWARD_COMPONENT_LOWER_BOUNDARY_BRACKET',range_m=[p['water_depth_m'],below['water_depth_m']],
        bracket_interpretation='Native bounding levels of a predicate change; conditional on unresolved intervening structure. Not a confidence interval, physical whole-current bottom, or seasonal range.',
        interpolation_assumption='No midpoint or interpolated depth computed; connectivity between sparse native levels is an explicit unresolved-structure assumption')

def main():
    start=float(os.environ['OSW_F3_BRACKET_START']);out=ROOT/'wsc-f3-warm-flow-brackets-v1';out.mkdir(exist_ok=False)
    prior=json.loads((ROOT/PRIOR).read_bytes())
    if prior['status']!='ORIGINAL_BOUNDED_PREVIEW_RETAINED_NATIVE_ANALYSIS_PENDING' or prior['provider_case_closed'] or prior['attempted_provider_operations']!=2 or prior['case_numeric_upper_bound']!=147160:raise ValueError('Original open F3 case and carried scalar reservation required')
    ledger=dict(prior,status='OFFLINE_NATIVE_SELECTION_RESERVED',prior_numeric_upper_bound=prior['case_numeric_upper_bound'],prior_active_seconds=prior['cumulative_active_seconds'])
    encode=lambda v:(json.dumps(v,ensure_ascii=False,allow_nan=False,indent=2)+'\n').encode()
    def save():(out/'ledger.json').write_bytes(encode(ledger))
    def stopped(*a):raise TimeoutError('Original cumulative case deadline or SIGTERM')
    elapsed=prior['cumulative_active_seconds']+time.monotonic()-start
    if not 0<=elapsed<30:raise ValueError('Shared synthetic/producer clock')
    signal.signal(signal.SIGALRM,stopped);signal.signal(signal.SIGTERM,stopped);signal.alarm(max(1,int(60-elapsed)));save()
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Offline retained original preview only'))
    try:
        op=json.loads((ROOT/OP).read_bytes())
        for p,h in op['input_sha256'].items():
            if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen input changed:'+p)
        # Original capture reserved two full lexical-source passes. Decode only
        # the declared dates into floats; no complete-year or complete-table
        # floating-point decode, no renewed source request or source reservation.
        ledger['additional_selection_and_output_numeric_upper_bound_reserved']=30000
        if prior['case_numeric_upper_bound']+30000>250000:raise ValueError('Prospective shared scalar cap')
        save();profiles,nrows,gears=selected_profiles((ROOT/RAW).read_bytes())
        cohort_complete=all(len(p['levels'])>=2 for p in profiles)
        records=[bracket(p if cohort_complete else dict(p,levels=[]),t) for p in profiles for t in THRESHOLDS]
        if not cohort_complete:
            for row in records:row['status']='INSUFFICIENT_THREE_PROFILE_NATIVE_COHORT_NO_MEASUREMENT_ADMITTED'
        report={'schema':'osw.wsc-f3-warm-northward-flow-brackets.v1','status':'DATED_NATIVE_COMPONENT_BRACKETS_OR_EXPLICIT_SAMPLING_GAPS',
            'source_doi':'10.1594/PANGAEA.800346','source_raw_sha256':'54aa3e8bab52d710dcb1ce30474a883d41859bf429e67113fd416fbf34445ea1',
            'profiles':profiles,'records':records,'selected_cohort_complete':cohort_complete,'native_preview_rows':nrows,'velocity_gears_in_preview':gears,
            'qualifications':['Published preview is truncated at 2000 rows; absence here is not archive-wide absence.','Declared target dates are the first three UTC midnights after deployment day. No alternate dates selected for a favorable result.','Unprefixed finite numeric values follow the publisher default-valid flag convention; all flagged, censored, averaged or missing cells are excluded. No independent instrument calibration or source tidal filtering is claimed.','Warm Atlantic-water criterion T>2degC follows Beszczynska-Moller et al.2012. This is a selected component, not the complete WSC.','Core-connected sampled levels and a maximum600m native gap define a conditional coarse bracket; unresolved intervening layers may invalidate physical connectivity. No interpolated depth or thickness calculated.','Provider north-south velocities remain in nativecm/s; no pressure-to-depth conversion. Each threshold shares the same native profiles.','One point and three dates do not cover a current route or seasonal cycle, and threshold variants are not independent observations or statistical uncertainty.'],
            'canonical_depth_reference_admitted':False,'runtime_changed':False,'full_goal_complete':False}
        encoded=encode(report)
        if json.loads(encoded)!=report:raise ValueError('Actual complete native-profile/bracket JSON roundtrip')
        extra=2*len(re.findall(rb'[-+]?\d+(?:\.\d+)?',encoded))+5000
        if extra>30000:raise ValueError('Reserved selection/output numeric allowance')
        (out/'warm-flow-brackets.json').write_bytes(encoded)
        ledger.update(status='DATED_NATIVE_COMPONENT_RESULTS_RETAINED_CASE_CLOSED',provider_case_closed=True,remaining_provider_operations=0,unused_provider_operations_surrendered=6,
            case_numeric_upper_bound=prior['case_numeric_upper_bound']+30000,requested_profile_dates=len(profiles),selected_profiles=sum(bool(p['levels']) for p in profiles),selected_profiles_with_native_velocity_levels=sum(bool(p['levels']) for p in profiles),
            selected_native_levels=sum(len(p['levels']) for p in profiles),native_numeric_values_decoded=sum(len(p['levels'])*4 for p in profiles),decoded_cells=sum(len(p['levels'])*10 for p in profiles),measurement_nodes=sum(len(p['levels'])*3 for p in profiles),
            native_source_text_passes_covered_by_original_reservation=True,new_provider_operations=0,new_depth_references=0)
        save()
        if sum(p.stat().st_size for p in out.iterdir())>2400000:raise ValueError('Whole result cap')
        print(json.dumps({'selected_profiles_with_levels':ledger['selected_profiles_with_native_velocity_levels'],'native_levels':ledger['selected_native_levels'],'records':records,'preview_rows':nrows}),flush=True)
    except BaseException as e:
        ledger.update(status='FAILED_NO_RETRY_CASE_CLOSED',error_type=type(e).__name__,error=str(e)[:400],provider_case_closed=True,remaining_provider_operations=0);raise
    finally:
        ledger['cumulative_active_seconds']=prior['cumulative_active_seconds']+time.monotonic()-start;save();signal.alarm(0);print(json.dumps(ledger),flush=True)

if __name__=='__main__':main()
