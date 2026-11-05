"""Cloud-only complete-month preflight; reuse metadata and snapshot hours."""
import calendar
import hashlib
import json
import urllib.parse
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import collect_norkyst_jutland_depth_v1 as previous
import norkyst_continuous_source as metadata_source

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/norkyst-jutland-calendar-month-preflight-operator-v1.json'
OLD='research/source-data/norkyst-jutland-depth-v1'
ACQUISITION='research/source-data/norkyst-ingoy-months-2024/acquisition-year.json'
MONTHS=[3,6,9,12]
LEVELS=previous.DEPTH[:11]


def build(root=ROOT):
    read=lambda p:json.loads((root/p).read_bytes())
    op=read(OPERATOR)
    for file,pin in op['input_sha256'].items():
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=pin:raise ValueError('Frozen input changed:'+file)
    original=read(previous.OPERATOR); oldpf=read(OLD+'/preflight.json')
    if oldpf!=previous.preflight(original):raise ValueError('Original source grid preflight must reproduce')
    acquisition=read(ACQUISITION)
    records=acquisition['responses']; points=[]; reuse=[]; targets=[]; metadata=[]
    for index,oldplan in enumerate(oldpf['plans'][:3]):
        case=read(OLD+'/case-'+str(index).zfill(2)+'.json'); c=case['columns'][19]
        if c['source_x_index']!=oldplan['x_index'] or c['source_y_index']!=oldplan['y_indices'][19]:raise ValueError('Original editorial center grid node required')
        points.append({'point_index':index,'section_id':oldplan['section_id'],
                       'source_x_index':c['source_x_index'],'source_y_index':c['source_y_index'],
                       'position_lon_lat':c['position_lon_lat'],'source_sea_mask':c['source_sea_mask'],
                       'selection_role':'original_editorial_center_node_not_a_selected_velocity_maximum'})
    for month in MONTHS:
        archive='research/source-data/norkyst-ingoy-months-2024/originals-year-2024-'+str(month).zfill(2)+'.zip'
        with zipfile.ZipFile(root/archive) as source_zip:
            for daynum in range(1,calendar.monthrange(2024,month)[1]+1):
                date=f'2024-{month:02d}-{daynum:02d}'
                recs=[r for r in records if r['date']==date]
                bindings={(r['archive_file'],r['metadata_member'],r['metadata_sha256']) for r in recs}
                if len(bindings)!=1:raise ValueError('One original metadata custody binding per day required')
                bound_archive,member,pin=next(iter(bindings))
                if bound_archive!=archive or source_zip.getinfo(member).file_size>250000 or not member.endswith('.das'):raise ValueError('Read only bounded original DAS member, never field arrays')
                raw=source_zip.read(member)
                if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('Original daily metadata changed')
                metadata_source.metadata(raw,date)
                urls={r['field_url'].split('.ascii?',1)[0] for r in recs}
                if len(urls)!=1:raise ValueError('One observed original daily dataset URL required')
                dataset=next(iter(urls))
                metadata.append({'date':date,'archive_file':archive,'metadata_member':member,'metadata_sha256':pin,
                                 'dataset_url_observed_in_original_acquisition':dataset})
                hours=[(0,11),(13,23)] if daynum==15 else [(0,23)]
                for point in points:
                    if daynum==15:
                        oldindex=MONTHS.index(month)*3+point['point_index']
                        file=OLD+'/case-'+str(oldindex).zfill(2)+'.json';case=read(file);column=case['columns'][19]
                        if case['date']!=date or [column['source_x_index'],column['source_y_index']]!=[point['source_x_index'],point['source_y_index']]:raise ValueError('Exact prior noon/source point binding required')
                        reuse.append({'date':date,'hour_utc':12,'point_index':point['point_index'],'source_case_file':file,
                                      'source_component_pointer':'/columns/19/northeast_component_m_s',
                                      'source_component_first_level_indices':[0,10],
                                      'reused_component_values':column['northeast_component_m_s'][:11]})
                    for first,last in hours:
                        nhours=last-first+1
                        space=f'[{point["source_y_index"]}][{point["source_x_index"]}]'
                        query=','.join(field+f'[{first}:1:{last}][0:1:10]'+space for field in ['u_eastward','v_northward'])
                        target={'target_index':len(targets),'month':month,'date':date,'point_index':point['point_index'],
                                'first_hour':first,'last_hour':last,'hourly_profiles':nhours,
                                'http_url':dataset+'.ascii?'+urllib.parse.quote(query,safe=',:'),
                                'metadata_record_index':len(metadata)-1,
                                'new_packed_velocity_scalars':nhours*11*2,
                                'new_decoded_coordinate_scalars':nhours+11+1+1}
                        if not 3<=nhours<=150 or nhours*11>20000:raise ValueError('Bounded hourly-profile patch required')
                        targets.append(target)
    for month in MONTHS:
        expected={datetime(2024,month,1,tzinfo=timezone.utc)+timedelta(hours=h) for h in range(calendar.monthrange(2024,month)[1]*24)}
        for point in points:
            got=[]
            for t in targets:
                if t['month']==month and t['point_index']==point['point_index']:
                    got.extend(datetime.fromisoformat(t['date']+'T00:00:00+00:00')+timedelta(hours=h) for h in range(t['first_hour'],t['last_hour']+1))
            got.extend(datetime.fromisoformat(r['date']+'T12:00:00+00:00') for r in reuse if int(r['date'][5:7])==month and r['point_index']==point['point_index'])
            if len(got)!=len(set(got)) or set(got)!=expected:raise ValueError('Every calendar hour exactly once; no source replay, time gap or padding')
    new_velocity=sum(t['new_packed_velocity_scalars'] for t in targets)
    new_coordinates=sum(t['new_decoded_coordinate_scalars'] for t in targets)
    prior=oldpf['total_reserved_decoded_scalar_values']; total=prior+new_velocity+new_coordinates
    if total>250000 or total*8>7000000:raise ValueError('All four months plus prior experiment must fit unchanged global source limits')
    if len({t['http_url'] for t in targets})!=len(targets):raise ValueError('One attempt per distinct new target only')
    return {'schema':'osw.norkyst-jutland-calendar-month-depth-preflight.v1',
            'status':'METADATA_AND_COMPLETE_TIME_SUPPORT_VERIFIED_BEFORE_NEW_FIELDS',
            'months':MONTHS,'year':2024,'source_depth_levels_m':LEVELS,'fixed_points':points,
            'daily_metadata_records':metadata,'reused_prior_noon_profiles':reuse,'request_plan':targets,
            'budget':{'prior_reserved_decoded_scalars':prior,'new_velocity_scalars':new_velocity,
                      'new_coordinate_scalars':new_coordinates,'combined_reserved_decoded_scalars':total,
                      'combined_reserved_decoded_bytes':total*8,'global_scalar_cap':250000,'global_decoded_byte_cap':7000000,
                      'new_provider_requests_reserved':len(targets),'maximum_attempts_per_target':1},
            'planned_month_hours':{str(m):calendar.monthrange(2024,m)[1]*24 for m in MONTHS},
            'metadata_archive_members_validated':len(metadata), 'new_provider_requests_performed':0,
            'new_ocean_values_decoded':0,'input_sha256':op['input_sha256'],
            'requirements_for_consumer':[
                'Decode coordinate maps once from u_eastward; verify v_northward map text equals the first map without another numeric decode. Shared coordinates count once; paired velocity values both count.',
                'Reuse twelve prior noon profiles at the exact original center nodes/first eleven levels. Never request those hour12values again.',
                'Archive only new raw responses; refer to existing daily DAS archive/member hashes. Never parse or retrieve prior Ingoy field arrays.',
                'All paired finite hours required per month/depth for monthly mean, population standard deviation or quantiles. Missing/land are null, not zero; no temporal gap fill or rescaled partial mean.',
                'Monthly mean component-depth descriptor is not the mean of instantaneous layer depths. Preserve signed northeast45degree component,0-25mcore/selection and0.1m/sprimary/0.05/0.2sensitivities.',
                'Fixed editorial center nodes are not fitted current axes. Keep dry or weak-current outcomes; do not move points after monthly values.',
                'Eleven provider-interpolated fixed levels end at65m. Domain ends/missing levels remain censors; no inferred physical bottom, width, volume, full-year range or seasonal climatology.',
                'Collect sequentially one idle cloud CPU. Each month is a source-output chunk<=2.4MB with exact raw bytes/member hashes, bounded source requests and persistent receipts. Global reserve includes every month and prior data, not per-point/month budget resets.'],
            'runtime_changed':False,'full_goal_complete':False}


if __name__=='__main__':
    result=build();out=ROOT/'norkyst-jutland-calendar-month-preflight-v1';out.mkdir(exist_ok=True)
    raw=previous.encode(result)
    if len(raw)>2400000:raise ValueError('Preflight artifact cap exceeded')
    (out/'preflight.json').write_bytes(raw)
    print(json.dumps({'budget':result['budget'],'planned_month_hours':result['planned_month_hours'],
                      'metadata_archive_members_validated':result['metadata_archive_members_validated'],
                      'fixed_points':result['fixed_points'],'reused_prior_noon_profiles':len(result['reused_prior_noon_profiles'])}))
