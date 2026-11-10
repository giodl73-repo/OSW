"""Execute verified whole-month point reads, preserving every successful original."""
import hashlib
import json
import math
import re
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
import numpy as np
import collect_norkyst_jutland_depth_v1 as frozen
from derive_eac_connected_layer_thickness_v1 import connected_layer

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/norkyst-jutland-calendar-month-collection-operator-v1.json'
PLAN='research/norkyst-jutland-calendar-month-depth-preflight-v1.json'
DEPTH=frozen.DEPTH[:11]


def map_text(text,field,axis,size):
    matches=list(re.finditer(r'(?m)^'+re.escape(field+'.'+axis)+r'\['+str(size)+r'\]\r?\n([^\r\n]+)',text))
    if len(matches)!=1:raise ValueError('One original coordinate map required')
    return matches[0][1].strip()


def parse(raw,target,point):
    n=target['hourly_profiles'];text=raw.decode()
    u=frozen.parse_array(text,'u_eastward',[n,11,1,1]);v=frozen.parse_array(text,'v_northward',[n,11,1,1])
    expected={'time':[datetime.fromisoformat(target['date']+f'T{hour:02d}:00:00+00:00').timestamp() for hour in range(target['first_hour'],target['last_hour']+1)],
              'depth':DEPTH,'Y':[point['source_y_index']*800],'X':[point['source_x_index']*800]}
    for axis,values in expected.items():
        if map_text(text,'u_eastward',axis,len(values))!=map_text(text,'v_northward',axis,len(values)):
            raise ValueError('Shared coordinate text must agree before one numeric decode')
        actual=[float(x) for x in map_text(text,'u_eastward',axis,len(values)).split(',')]
        if actual!=values:raise ValueError('Exact source hours/depths/grid required')
    q=np.full((n,11),np.nan)
    for index,(a,b) in enumerate(zip(u,v)):
        a,b=frozen.decode(a),frozen.decode(b)
        if a is not None and b is not None:q[index//11,index%11]=(a+b)/math.sqrt(2)
    return q


def assign(q,assigned,point,hours,values):
    if values.shape!=(len(hours),11) or len(set(hours))!=len(hours) or any(assigned[point,h] for h in hours):
        raise ValueError('Exactly one source profile assignment per fixed point/hour')
    q[point,hours,:]=values;assigned[point,hours]=True


def statistics(values):
    expected=len(values);counts=np.isfinite(values).sum(axis=0);complete=counts==expected
    result={'expected_hours':expected,'paired_finite_hours':counts.astype(int).tolist(),
            'complete_calendar_month_support':complete.tolist()}
    for name,fn in [('mean',lambda a:np.mean(a,axis=0)),('population_standard_deviation',lambda a:np.std(a,axis=0,ddof=0)),
                    ('p05',lambda a:np.quantile(a,.05,axis=0)),('median',lambda a:np.quantile(a,.5,axis=0)),('p95',lambda a:np.quantile(a,.95,axis=0))]:
        row=[None]*11
        if complete.any():
            numbers=fn(values[:,complete])
            for index,value in zip(np.flatnonzero(complete),numbers):row[int(index)]=float(value)
        result[name]=row
    mu=result['mean'];idx=list(range(9));full=all(mu[i] is not None for i in idx)
    score=sum((mu[a]+mu[b])*(DEPTH[b]-DEPTH[a])/2 for a,b in zip(idx,idx[1:])) if full else None
    eligible=full and score>0 and max(mu[i] for i in idx)>.1
    layers=[connected_layer(DEPTH,mu,t,(0,25)) for t in [.05,.1,.2]]
    result.update(selection_depth_interval_m=[0,25],primary_threshold_m_s=.1,
                  signed_selection_integral_m2_s=score,primary_fixed_point_eligible=bool(eligible),
                  primary_mean_field_depth_descriptor=layers[1] if eligible else None,
                  threshold_contexts=layers,physical_current_thickness_m=None,volume_m3=None,
                  annual_range_m=None,monthly_mean_is_mean_of_instantaneous_depths=False)
    return result


def retrieve(target,receipt,opener):
    receipt.update(target_index=target['target_index'],url=target['http_url'],attempts=1,status='reserved',bytes_received=0)
    request=urllib.request.Request(target['http_url'],headers={'Accept-Encoding':'identity','User-Agent':'OSW-complete-month-Jutland-depth-v1'})
    try:
        with opener(request,timeout=25) as response:
            if response.status!=200 or response.url!=target['http_url'] or response.headers.get('Content-Encoding') not in [None,'identity']:
                raise ValueError('Exact uncompressed source200 response required')
            declared=response.headers.get('Content-Length')
            if declared is not None and (not declared.isdigit() or int(declared)>18000):raise ValueError('Declared response exceeds18000B cap')
            raw=response.read(18001);receipt['bytes_received']=len(raw)
            if len(raw)>18000:raise ValueError('Response exceeds18000B cap')
        receipt.update(status='received',sha256=hashlib.sha256(raw).hexdigest());return raw
    except Exception as error:
        receipt.update(status='failed_no_retry',error_type=type(error).__name__,error_summary=str(error)[:200]);raise


def load(root=ROOT):
    op=json.loads((root/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=pin:raise ValueError('Pinned input changed:'+file)
    plan=json.loads((root/PLAN).read_bytes())
    review=json.loads((root/'research/current-depth-norkyst-jutland-calendar-month-preflight-source-review-v1.json').read_bytes())
    if review['source_run']!=41967640327 or review['tests_passed']!=6 or plan['budget']!=review['budget'] or plan['budget']['combined_reserved_decoded_scalars']!=246018:
        raise ValueError('Exact validated complete-month programme required')
    if op['maximum_http_requests']!=378 or op['maximum_attempts_per_target']!=1 or op['request_timeout_seconds']!=25 or op['maximum_response_bytes']!=18000:
        raise ValueError('Predeclared transport budget cannot change')
    return plan,op


def main():
    plan,op=load();out=ROOT/'norkyst-jutland-calendar-months-v1';out.mkdir(exist_ok=True)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*a,**k):return None
    opener=urllib.request.build_opener(NoRedirect()).open
    programme={'schema':'osw.norkyst-jutland-calendar-month-programme.v1','budget':plan['budget'],
               'operator_file':OPERATOR,'operator_sha256':hashlib.sha256((ROOT/OPERATOR).read_bytes()).hexdigest(),
               'preflight_file':PLAN,'preflight_sha256':hashlib.sha256((ROOT/PLAN).read_bytes()).hexdigest(),
               'months':[],'requests_attempted':0,'new_decoded_scalars_attempted':0,
               'prior_source_and_metadata_retrieved_again':False,'runtime_changed':False,'full_goal_complete':False}
    failures=0
    for month in plan['months']:
        folder=out/f'month-{month:02d}';folder.mkdir(exist_ok=True)
        hours=plan['planned_month_hours'][str(month)];q=np.full((3,hours,11),np.nan);assigned=np.zeros((3,hours),dtype=bool)
        archive=folder/'source-responses.zip'
        if archive.exists():raise ValueError('Fresh source output required; never rerun successful or partial collection')
        for old in plan['reused_prior_noon_profiles']:
            if int(old['date'][5:7])==month:
                h=(15-1)*24+12
                values=np.array([[np.nan if v is None else v for v in old['reused_component_values']]],dtype=float)
                assign(q,assigned,old['point_index'],[h],values)
        month_report={'schema':'osw.norkyst-jutland-complete-month-source.v1','month':month,'year':2024,
                      'expected_hours_per_point':hours,'source_depth_levels_m':DEPTH,'fixed_points':plan['fixed_points'],
                      'source_preflight_sha256':programme['preflight_sha256'],'transport_receipts':[],
                      'component_bearing_degrees_true':45,'vertical_sampling':'provider_interpolated_fixed_z_not_native_ROMS',
                      'credit':'Modified MET Norway/IMR NorKyst_v3 data,CC BY4.0;Christensen etal2026,doi10.5194/gmd-19-2785-2026.',
                      'physical_current_identity_independently_verified':False,'de_tided':False,
                      'seasonal_mean':False,'whole_current_profile':False,'runtime_changed':False,'full_goal_complete':False}
        for target in [t for t in plan['request_plan'] if t['month']==month]:
            receipt={};month_report['transport_receipts'].append(receipt)
            programme['requests_attempted']+=1
            programme['new_decoded_scalars_attempted']+=target['new_packed_velocity_scalars']+target['new_decoded_coordinate_scalars']
            if programme['requests_attempted']>378 or programme['new_decoded_scalars_attempted']+39348>250000:raise ValueError('Global programme budget exhausted')
            try:
                raw=retrieve(target,receipt,opener)
                member=f'target-{target["target_index"]:03d}.ascii'
                with zipfile.ZipFile(archive,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
                    info=zipfile.ZipInfo(member,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                    z.writestr(info,raw,compresslevel=9)
                receipt['archive_member']=member
                values=parse(raw,target,plan['fixed_points'][target['point_index']])
                first=(int(target['date'][-2:])-1)*24+target['first_hour']
                assign(q,assigned,target['point_index'],list(range(first,first+target['hourly_profiles'])),values)
                receipt['status']='received_archived_and_assigned'
            except Exception as error:
                failures+=1
                if receipt.get('status')=='received':receipt.update(status='received_but_derivation_failed_no_replay',error_type=type(error).__name__,error_summary=str(error)[:200])
            month_report['source_hours_assigned_per_point']=assigned.sum(axis=1).astype(int).tolist()
            (folder/'receipt.json').write_bytes(frozen.encode(month_report))
            (out/'programme.json').write_bytes(frozen.encode(programme))
            if target['target_index']%12==0:print(json.dumps({'month':month,'target_index':target['target_index'],'status':receipt['status']}),flush=True)
        month_report['profiles']=[{'point_index':i,'statistics':statistics(q[i])} for i in range(3)]
        month_report['raw_archive_sha256']=hashlib.sha256(archive.read_bytes()).hexdigest() if archive.exists() else None
        month_report['raw_archive_file']='source-responses.zip'
        month_report['counts']={'requests_attempted':len(month_report['transport_receipts']),
                                'successful_responses':sum(r['status']=='received_archived_and_assigned' for r in month_report['transport_receipts']),
                                'complete_time_support_points':int((assigned.sum(axis=1)==hours).sum())}
        month_report['interpretation']=[
            'Fixed search locations, not selected current axes. All missing, weak, reverse and incomplete cases retained.',
            'Monthly statistics require every paired finite calendar hour at each depth; no temporal gap filling or partial means.',
            'Quantiles/population standard deviation describe hourly model variability, not measurement uncertainty.',
            'Depth descriptors are contours of the monthly mean component, not means of instantaneous current depth.',
            'Eleven provider fixed-z levels end at65m. Missing/domain ends remain censors, not current bottom or physical thickness.',
            'Four calendar months are not seasonal means, a full annual envelope or a whole-current volume.']
        (folder/'receipt.json').write_bytes(frozen.encode(month_report))
        if sum(p.stat().st_size for p in folder.iterdir())>2400000:raise ValueError('Per-month scientific output cap exceeded')
        programme['months'].append({'month':month,'counts':month_report['counts'],
                                    'primary_mean_field_descriptors':[p['statistics']['primary_mean_field_depth_descriptor'] for p in month_report['profiles']]})
        (out/'programme.json').write_bytes(frozen.encode(programme))
        print(json.dumps({'completed_month':month,'counts':month_report['counts'],'profiles':month_report['profiles']}),flush=True)
    programme['status']='complete_all_planned_source_requests' if failures==0 else 'partial_source_errors_no_retry'
    (out/'programme.json').write_bytes(frozen.encode(programme))
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
