"""Bounded cloud-only NOAA daily ADCP pilot, with a durable pre-request journal."""
import csv
import hashlib
import io
import json
import math
import os
import signal
import time
import urllib.parse
import urllib.request
from datetime import datetime,timedelta
from pathlib import Path
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OP='research/tao-pacific-euc-daily-depth-operator-v1.json'
BASE='https://data.pmel.noaa.gov/pmel/erddap/'
DATA=BASE+'tabledap/pmelTaoDyAdcp.csv?'
FIELDS=['array','station','longitude','latitude','time','depth','u_1205','QU_5205']
UNITS=['','','degrees_east','degrees_north','UTC','m','cm/s','']


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()


def atomic(path,raw):
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def table(raw,fields,units,maxrows):
    rows=list(csv.reader(io.StringIO(raw.decode('iso8859-1'))))
    if len(rows)<2 or rows[0]!=fields or rows[1]!=units or len(rows)-2>maxrows:
        raise ValueError('Exact bounded CSV columns/units/row cap required')
    if any(len(r)!=len(fields) for r in rows[2:]):raise ValueError('Complete CSV records required')
    return [dict(zip(fields,r)) for r in rows[2:]]


def metadata(raw):
    data=json.loads(raw)['table']
    if data['columnNames']!=['Row Type','Variable Name','Attribute Name','Data Type','Value'] or len(data['rows'])>500:
        raise ValueError('Exact ERDDAP metadata table required')
    attributes={(r[1],r[2]):r[4] for r in data['rows'] if r[0]=='attribute'}
    wanted={('u_1205','units'):'cm/s',('u_1205','standard_name'):'eastward_sea_water_velocity',
            ('depth','units'):'m',('depth','positive'):'down',('longitude','units'):'degrees_east',
            ('latitude','units'):'degrees_north',('longitude','long_name'):'Nominal Longitude',
            ('latitude','long_name'):'Nominal Latitude',('time','long_name'):'Centered Time'}
    if any(attributes.get(k)!=v for k,v in wanted.items()):raise ValueError('Observed component/units/nominal coordinate semantics changed')
    if float(attributes['u_1205','_FillValue'])!=1e35 or float(attributes['u_1205','missing_value'])!=1e35:
        raise ValueError('Source fill semantics changed')
    quality=attributes['QU_5205','description']
    if not all(s in quality for s in ['0=missing data','1=highest','2=standard','3=lower']):raise ValueError('Source quality semantics changed')
    summary=attributes['NC_GLOBAL','summary']
    if not all(s in summary for s in ['Daily averages','00:00Z','12:00Z']):raise ValueError('Source daily averaging semantics changed')
    license=attributes['NC_GLOBAL','license']
    if 'used and redistributed for free' not in license:raise ValueError('Source redistribution terms changed')
    return {'units':'cm/s','fill_value':1e35,'quality_accepted':[1,2],
            'source_summary':summary,'source_license':license,'source_institution':attributes['NC_GLOBAL','institution']}


def stations(raw):
    fields=['array','station','longitude','latitude']
    rows=table(raw,fields,['','','degrees_east','degrees_north'],100)
    chosen=[]
    for lon in [165,190,220,250]:
        candidates=[r for r in rows if float(r['longitude'])==lon and float(r['latitude'])==0]
        if len(candidates)!=1:raise ValueError('Exactly one catalogue station at each predeclared nominal longitude required')
        r=candidates[0]
        if not r['station'] or not r['array']:raise ValueError('Catalogue identifiers required')
        chosen.append({'array':r['array'],'station':r['station'],'longitude':lon,'latitude':0})
    return chosen


def targets(chosen):
    out=[]
    for station in chosen:
        for month in [3,6,9,12]:
            dates=[f'2005-{month:02d}-{day:02d}T12:00:00Z' for day in [14,15,16]]
            query=','.join(FIELDS)+'&station='+json.dumps(station['station'])+'&array='+json.dumps(station['array'])
            query+=f'&longitude={station["longitude"]}&latitude=0&time>={dates[0]}&time<={dates[-1]}&depth>=5&depth<=350&orderByClosest("station,time,depth/10")'
            out.append({'target_id':f'field-{len(out):02d}','station':station,'times_utc':dates,
                        'url':DATA+urllib.parse.quote(query,safe=',&=():/'),
                        'cap_bytes':50000,'maximum_rows':120,'reserved_numeric_scalars':720})
    return out


def decode(value,flag):
    a=float(value);q=float(flag)
    if not math.isfinite(a) or abs(a)>=1e34 or q not in [1,2]:return None
    if abs(a)>1000:raise ValueError('Velocity outside predeclared1000cm/s sanity bound')
    return a/100


def layer(z,u,threshold):
    original=connected_layer(z,u,threshold,(50,250))
    if 'core_index' not in original:return original
    seed=original['core_index'];lo=seed;hi=seed
    while lo>0 and z[lo]-z[lo-1]<=15:lo-=1
    while hi+1<len(z) and z[hi+1]-z[hi]<=15:hi+=1
    if hi==lo:
        return {'threshold_m_s':threshold,'core_index':seed,'core_depth_m':z[seed],'core_velocity_m_s':u[seed],
                'upper_depth_m':None,'lower_depth_m':None,'layer_thickness_m':None,
                'status':'unresolved_connected_layer_boundary','upper_status':'censored_at_returned_depth_gap',
                'lower_status':'censored_at_returned_depth_gap','core_search_window_edge':z[seed] in [50,250]}
    # Lock the original core rather than selecting a more convenient core after segmentation.
    result=connected_layer(z[lo:hi+1],u[lo:hi+1],threshold,(z[seed],z[seed]))
    result['core_index']=seed
    for side,edge,gapped in [('upper',lo,lo>0),('lower',hi,hi+1<len(z))]:
        if gapped and result[side+'_status']=='censored_at_sample_domain_edge':
            result[side+'_status']='censored_at_returned_depth_gap'
    if result['status']=='resolved_connected_model_threshold_layer':
        result['status']='resolved_connected_observed_daily_mean_threshold_layer'
    result['source_sampling']='original_row_subsample_near10m_not_all_original_ADCP_bins'
    result['between_retained_levels_assumption']='piecewise_linear_no_unobserved_reversals'
    result['core_search_window_edge']=z[seed] in [50,250]
    return result


def profiles(raw,target):
    rows=table(raw,FIELDS,UNITS,120);groups={t:[] for t in target['times_utc']};seen=set()
    for r in rows:
        s=target['station'];z=float(r['depth']);t=r['time']
        if r['station']!=s['station'] or r['array']!=s['array'] or float(r['longitude'])!=s['longitude'] or float(r['latitude'])!=0 or t not in groups or not 5<=z<=350:
            raise ValueError('Exact station/nominal coordinates/date/depth bounds required')
        if (t,z) in seen:raise ValueError('Duplicate observed depth/time row')
        seen.add((t,z));groups[t].append((z,float(r['u_1205']),float(r['QU_5205'])))
    out=[]
    for t,values in groups.items():
        values.sort();z=[r[0] for r in values]
        if len(z)>40:raise ValueError('Forty-level cap is global per returned profile, not reset')
        u=[decode(a,q) for _,a,q in values]
        contexts=[layer(z,u,threshold) for threshold in [.05,.1,.2]] if len(z)>=2 else []
        primary=contexts[1] if contexts else None
        eligible=bool(primary and 'core_index' in primary and not primary.get('core_search_window_edge',True))
        out.append({'time_center_utc':t,'provider_averaging_interval_utc':{'start':t[:10]+'T00:00:00Z','end_exclusive':(datetime.fromisoformat(t[:10])+timedelta(days=1)).date().isoformat()+'T00:00:00Z'},
                    'nominal_station':target['station'],'source_depths_m':z,'source_u_cm_s':[a if math.isfinite(a) and abs(a)<1e34 else None for _,a,_ in values],
                    'source_u_quality':[q if math.isfinite(q) and abs(q)<1e34 else None for _,_,q in values],
                    'accepted_eastward_velocity_m_s':u,'threshold_contexts':contexts,
                    'primary_core_window_interior':eligible,
                    'primary_lower_isotach_depth_m':primary['lower_depth_m'] if eligible else None,
                    'primary_threshold_layer_span_m':primary['layer_thickness_m'] if eligible else None,
                    'status':'source_profile_returned' if values else 'no_source_rows_for_predeclared_day',
                    'physical_current_identity_independently_verified':False,'physical_current_thickness_m':None,
                    'annual_range_m':None,'volume_m3':None,'mean_field_depth_is_mean_instantaneous_depth':False,
                    'daily_underlying_sample_coverage_verified':False})
    return out,len(rows)*6


class SourceDeadline(Exception):pass


def alarm(signum,frame):
    if signum!=signal.SIGALRM:raise SystemExit('Producer termination signal; no further requests')
    raise SourceDeadline('Absolute acquisition deadline')


def acquire(target,folder,journal,opener,deadline):
    if time.monotonic()+26>deadline:return None
    if any(r['target_id']==target['target_id'] or r['url']==target['url'] for r in journal['requests']):
        raise ValueError('An attempted target must never be replayed')
    if journal['total_body_bytes']+target['cap_bytes']>1200000:raise ValueError('Insufficient aggregate response-body reserve')
    row={'target_id':target['target_id'],'url':target['url'],'attempts':1,'status':'reserved_before_http',
         'cap_bytes':target['cap_bytes'],'bytes_received':0}
    journal['requests'].append(row)
    atomic(folder/'journal.json',encoded(journal))
    raw=bytearray()
    signal.setitimer(signal.ITIMER_REAL,min(25,deadline-time.monotonic()))
    try:
        req=urllib.request.Request(target['url'],headers={'Accept-Encoding':'identity','User-Agent':'OSW-observed-EUC-daily-depth-v1'})
        with opener(req,timeout=25) as response:
            if response.status!=200 or response.url!=target['url'] or response.headers.get('Content-Encoding') not in [None,'identity']:
                raise ValueError('Exact uncompressed200source required')
            size=response.headers.get('Content-Length')
            if size is not None and (not size.isdigit() or int(size)>target['cap_bytes']):raise ValueError('Declared source response exceeds cap')
            while True:
                part=response.read(min(8192,target['cap_bytes']+1-len(raw)))
                if not part:break
                raw.extend(part)
                if len(raw)>target['cap_bytes']:raise ValueError('Source body exceeds cap')
        member=target['target_id']+'.raw';atomic(folder/member,bytes(raw))
        row.update(status='received_archived_before_derivation',raw_file=member,bytes_received=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        atomic(folder/'journal.json',encoded(journal));return bytes(raw)
    except BaseException as error:
        # The pre-request reservation remains authoritative even without retained bytes.
        if raw:
            member=target['target_id']+'.partial';atomic(folder/member,bytes(raw));row.update(partial_file=member,partial_sha256=hashlib.sha256(raw).hexdigest())
        row.update(status='attempted_failed_or_interrupted_no_retry',bytes_received=len(raw),error_type=type(error).__name__,error_summary=str(error)[:200])
        atomic(folder/'journal.json',encoded(journal))
        if isinstance(error,(KeyboardInterrupt,SystemExit)):raise
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        journal['total_body_bytes']+=len(raw)
        atomic(folder/'journal.json',encoded(journal))
        if journal['total_body_bytes']>1200000:raise ValueError('Global programme body cap exceeded')


def main():
    op=json.loads((ROOT/OP).read_bytes())
    for f,h in op['input_sha256'].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h:raise ValueError('Pinned input changed:'+f)
    if op['maximum_http_requests']!=18 or op['maximum_attempts_per_target']!=1 or op['global_scalar_reserve']!=12520 or op['programme_deadline_seconds']!=210:
        raise ValueError('Frozen global transport/decode scope required')
    folder=ROOT/'tao-pacific-euc-daily-depth-v1';folder.mkdir(exist_ok=False)
    deadline=time.monotonic()+210
    for sig in [signal.SIGALRM,signal.SIGTERM,signal.SIGINT]:signal.signal(sig,alarm)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a,**k):return None
    opener=urllib.request.build_opener(NoRedirect()).open
    journal={'schema':'osw.tao-pacific-euc-daily-source-journal.v1','operator_file':OP,
             'operator_sha256':hashlib.sha256((ROOT/OP).read_bytes()).hexdigest(),
             'requests':[],'total_body_bytes':0,'maximum_requests':18,'maximum_attempts_per_target':1,
             'global_field_scalar_reserve':11520,'metadata_coordinate_scalar_reserve':1000,'global_scalar_cap':250000,
             'field_scalars_decoded':0,'producer_finalized_before_artifact_upload':False}
    atomic(folder/'journal.json',encoded(journal))
    results={'schema':'osw.tao-pacific-euc-daily-depth.v1','entity_id':'current:pacific-equatorial-undercurrent',
             'credit':'Modified NOAA/PMEL GTMBA daily ADCP data; acknowledged source and returned quality retained.',
             'profiles':[],'runtime_changed':False,'full_goal_complete':False,'physical_thickness_or_volume_promoted':False}
    meta_target={'target_id':'metadata','url':BASE+'info/pmelTaoDyAdcp/index.json','cap_bytes':200000}
    catalog_query='array,station,longitude,latitude&latitude=0&longitude>=165&longitude<=250&distinct()'
    catalogue={'target_id':'catalogue','url':DATA+urllib.parse.quote(catalog_query,safe=',&=()'),'cap_bytes':200000}
    try:
        raw=acquire(meta_target,folder,journal,opener,deadline)
        if raw is None:raise ValueError('Metadata unavailable; no field requests authorized')
        results['metadata']=metadata(raw)
        raw=acquire(catalogue,folder,journal,opener,deadline)
        if raw is None:raise ValueError('Station catalogue unavailable; no field requests authorized')
        plan=targets(stations(raw));atomic(folder/'field-plan.json',encoded(plan))
        results['source_target_outcomes']=[{'target_id':t['target_id'],'status':'not_attempted'} for t in plan]
        for target in plan:
            if len(journal['requests'])>=18:raise ValueError('Global HTTP reserve exhausted')
            raw=acquire(target,folder,journal,opener,deadline)
            outcome=next(r for r in results['source_target_outcomes'] if r['target_id']==target['target_id'])
            if raw is None:
                outcome['status']='attempted_failed_no_retry' if any(r['target_id']==target['target_id'] for r in journal['requests']) else 'not_attempted_deadline'
                if time.monotonic()+26>deadline:break
                continue
            try:
                value,numeric=profiles(raw,target)
                journal['field_scalars_decoded']+=numeric
                if journal['field_scalars_decoded']>11520:raise ValueError('Global field scalar reserve exhausted')
                results['profiles'].extend(value);journal['requests'][-1]['derivation_status']='parsed_and_diagnosed'
                outcome['status']='parsed_and_diagnosed'
            except Exception as error:
                journal['requests'][-1].update(derivation_status='failed_retained_bytes_no_replay',derivation_error=type(error).__name__+':'+str(error)[:200])
                outcome['status']='derivation_failed_retained_bytes_no_replay'
            atomic(folder/'journal.json',encoded(journal));atomic(folder/'profiles.json',encoded(results))
            print(json.dumps({'target':target['target_id'],'status':journal['requests'][-1].get('derivation_status','no_result')}),flush=True)
        results['status']='planned_source_targets_attempted' if len(journal['requests'])==18 else 'partial_programme_deadline_no_retry'
    except BaseException as error:
        results.update(status='metadata_or_programme_failure_no_retry',error_type=type(error).__name__,error_summary=str(error)[:240])
    finally:
        signal.setitimer(signal.ITIMER_REAL,0)
        journal['producer_finalized_before_artifact_upload']=True
        results['counts']={'request_attempts':len(journal['requests']),'profiles_with_reported_rows':sum(bool(p['source_depths_m']) for p in results['profiles']),
                           'predeclared_daily_profile_rows_in_result':len(results['profiles']),
                           'finite_primary_lower_threshold_depths':sum(p['primary_lower_isotach_depth_m'] is not None for p in results['profiles']),
                           'finite_primary_threshold_layer_spans':sum(p['primary_threshold_layer_span_m'] is not None for p in results['profiles'])}
        atomic(folder/'journal.json',encoded(journal));atomic(folder/'profiles.json',encoded(results))
        if sum(f.stat().st_size for f in folder.iterdir())>2400000:raise ValueError('Scientific chunk cap exceeded')
        print(json.dumps({'status':results['status'],'counts':results['counts'],'field_scalars_decoded':journal['field_scalars_decoded']}),flush=True)
    if len(journal['requests'])!=18 or any(r.get('status')!='received_archived_before_derivation' or (r['target_id'].startswith('field-') and r.get('derivation_status')!='parsed_and_diagnosed') for r in journal['requests']):
        raise SystemExit(1)


if __name__=='__main__':main()
