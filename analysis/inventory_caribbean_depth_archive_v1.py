"""Cloud-only inspection of the published RU29 velocity archive; admits no depths."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REQUEST='research/caribbean-current-depth-source-inventory-request-v1.json'


def download_archive(request,destination):
    expected=request['archive'];url=expected['url']
    if url!='https://zenodo.org/api/records/18332586/files/data.zip/content':
        raise ValueError('Only the reviewed public archive is supported')
    if expected['bytes']!=1070927767 or expected['md5']!='49e12ca9fcfcdb63121788ddb3ebadc1':
        raise ValueError('Published archive pin changed')
    md5=hashlib.md5();sha=hashlib.sha256();size=0;started=time.monotonic()
    with urllib.request.urlopen(url,timeout=60) as response,destination.open('wb') as out:
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>expected['bytes'] or time.monotonic()-started>600:
                raise ValueError('Archive exceeded its pinned size or download time budget')
            md5.update(chunk);sha.update(chunk);out.write(chunk)
    if size!=expected['bytes'] or md5.hexdigest()!=expected['md5']:
        raise ValueError('Published archive size/checksum mismatch')
    return {'url':url,'bytes':size,'md5':md5.hexdigest(),'sha256':sha.hexdigest()}


def clean_value(value):
    if hasattr(value,'tolist'):return clean_value(value.tolist())
    if isinstance(value,bytes):return value.decode('utf8',errors='replace')
    if isinstance(value,float) and not math.isfinite(value):return {'non_finite':str(value)}
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    if isinstance(value,(tuple,list)):return [clean_value(v) for v in value]
    return str(value)


def coordinate_summary(variable):
    """Read only three coordinate scalars; never read a velocity array here."""
    if len(variable.shape)!=1 or not variable.size:return None
    indices=sorted({0,variable.size//2,variable.size-1})
    values=[]
    for index in indices:
        value=variable[index]
        if hasattr(value,'mask') and bool(value.mask):value=None
        values.append({'index':index,'value':clean_value(value)})
    return values


def inspect_netcdf(raw):
    from netCDF4 import Dataset,num2date
    with Dataset('published_processed_velocity.nc',memory=raw) as dataset:
        variables={}
        for name,var in dataset.variables.items():
            variables[name]={'dimensions':list(var.dimensions),'shape':list(var.shape),
                             'dtype':str(var.dtype),'attributes':{k:clean_value(var.getncattr(k)) for k in var.ncattrs()}}
            if name in ['depth','time','start_time','end_time','latitude','longitude']:
                variables[name]['coordinate_samples']=coordinate_summary(var)
        expected={'u_grid','v_grid','depth','time','start_time','end_time','latitude','longitude'}
        if not expected.issubset(variables):raise ValueError('Reviewed processed-velocity schema not present')
        if variables['u_grid']['dimensions']!=['depth','time'] or variables['v_grid']['dimensions']!=['depth','time']:
            raise ValueError('Unexpected velocity dimensions')
        audit=[]
        for index in sorted({0,len(dataset.dimensions['time'])//2,len(dataset.dimensions['time'])-1}):
            dates={}
            for name in ['time','start_time','end_time']:
                var=dataset.variables[name]
                if not getattr(var,'units',None):raise ValueError('Timestamp units missing')
                dates[name]=num2date(var[index],units=var.units,calendar=getattr(var,'calendar','standard'),only_use_cftime_datetimes=False)
            duration=(dates['end_time']-dates['start_time']).total_seconds()
            offset=(dates['time']-dates['start_time']).total_seconds()
            audit.append({'profile_index':index,'start_time':str(dates['start_time']),
                          'reported_time':str(dates['time']),'end_time':str(dates['end_time']),
                          'duration_seconds':duration,'reported_offset_seconds':offset,
                          'reported_time_matches_midpoint':abs(offset-duration/2)<=1,
                          'reported_time_matches_end':abs(offset-duration)<=1})
        return {'dimensions':{k:len(v) for k,v in dataset.dimensions.items()},'variables':variables,
                'global_attributes':{k:clean_value(dataset.getncattr(k)) for k in dataset.ncattrs()},
                'timestamp_sample_audit':audit,'velocity_values_read':False,
                'velocity_units_established_from_file':all(bool(variables[k]['attributes'].get('units')) for k in ['u_grid','v_grid'])}


def inspect_archive(path,request):
    with zipfile.ZipFile(path) as archive:
        members=[m for m in archive.infolist() if not m.is_dir() and not m.filename.startswith('__MACOSX/')]
        inventory=[{'path':m.filename,'bytes':m.file_size,'compressed_bytes':m.compress_size,'crc32':f'{m.CRC:08x}'} for m in members]
        candidates=[m for m in members if Path(m.filename).name==request['processed_velocity_basename']]
        if len(candidates)!=1:raise ValueError('Need exactly one reviewed processed velocity member')
        selected=candidates[0]
        if selected.file_size>128*1024*1024:raise ValueError('Processed velocity member exceeds inspection budget')
        raw=archive.read(selected)
        return {'archive_members':inventory,'selected_member':{'path':selected.filename,'bytes':len(raw),
                'sha256':hashlib.sha256(raw).hexdigest()},'netcdf_schema':inspect_netcdf(raw)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--scratch',required=True);args=parser.parse_args()
    if os.environ.get('GITHUB_ACTIONS')!='true':
        raise RuntimeError('Archive download and inspection run only in the cloud workflow')
    request=json.loads((ROOT/REQUEST).read_bytes());scratch=Path(args.scratch);scratch.mkdir(parents=True,exist_ok=True)
    acquisition=download_archive(request,scratch/'data.zip')
    result={'schema':'osw.caribbean-depth-source-inventory.v1','status':'PASS_SOURCE_SCHEMA_INSPECTED',
            'source_commit':os.environ['GITHUB_SHA'],'request_sha256':hashlib.sha256((ROOT/REQUEST).read_bytes()).hexdigest(),
            'archive':acquisition,**inspect_archive(scratch/'data.zip',request),
            'depth_measurements_added':0,'measurement_operator_executed':False,
            'whole_route_profile_established':False,'volume_estimates_added':0,
            'source_timestamp_policy_required_before_measurement':True,'runtime_changed':False,'full_goal_complete':False}
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'archive_members':len(result['archive_members']),
                      'selected_member':result['selected_member'],'dimensions':result['netcdf_schema']['dimensions'],
                      'velocity_units_in_file':result['netcdf_schema']['velocity_units_established_from_file'],
                      'depth_measurements_added':0}))


if __name__=='__main__':main()
