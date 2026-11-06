"""Exact surrounding HYCOM source vectors; no named-current/width admission."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import quote
import urllib.request

import numpy as np
from acquire_eac_100m_source import write_npz

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'research/source-data/hycom-south-australian-2d-2012'
PROTOCOL='plans/south-australian-hycom-2d-source-selection-protocol-v1.md'
PROTOCOL_SHA='eac25dba997bb60b36d64f8aa5de119a7fd5ee61b36c49bd8b6d25cc640c492d'
ORIGINAL='research/source-data/hycom-south-australian-2012/section.ascii'
ORIGINAL_SHA='524cc83b5c873848634e83dc9e03e35e885779757f0466bbcb978792b490ebc6'
OPERATOR='analysis/acquire_south_australian_hycom_2d.py'
BASE='https://tds.hycom.org/thredds/dodsC/GLBu0.08/reanalysis'
LIMIT=40_000_000


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def urls():
    expression=','.join(v+'[6990:1:7355][19][525:1:600][3875:1:3925]' for v in ['water_u','water_v'])
    coordinates='time[6990:1:7355],depth[19],lat[525:1:600],lon[3875:1:3925]'
    return {'cube.ascii':BASE+'.ascii?'+quote(expression,safe=''),'metadata.das':BASE+'.das','metadata.dds':BASE+'.dds',
            'coordinates.ascii':BASE+'.ascii?'+quote(coordinates,safe='')}


def check_coordinate_response(text,arrays):
    headers=list(re.finditer(r'(?m)^(time|depth|lat|lon)\[(\d+)\][\r ]*$',text))
    if not text.startswith('Dataset {') or len(headers)!=4 or {h[1] for h in headers}!={'time','depth','lat','lon'}:
        raise ValueError('Incomplete HYCOM coordinate-only response')
    for i,h in enumerate(headers):
        body=text[h.end():headers[i+1].start() if i+1<len(headers) else len(text)].strip()
        values=np.array([float(t) for t in body.split(',')],dtype='<f8')
        if len(values)!=int(h[2]) or not np.array_equal(values,arrays[h[1]]):raise ValueError('Different separately requested HYCOM coordinates: '+h[1])


def parse_ascii(text,nt=366,ny=76,nx=51):
    headers=list(re.finditer(r'(?m)^(water_[uv])\.(water_[uv]|time|depth|lat|lon)((?:\[\d+\])+)[\r ]*$',text))
    if not text.startswith('Dataset {') or len(headers)!=10:raise ValueError('Incomplete HYCOM grid/maps response')
    declaration=text[:headers[0].start()]
    for name in ['water_u','water_v']:
        token=f'Int16 {name}[time = {nt}][depth = 1][lat = {ny}][lon = {nx}];'
        if declaration.count(token)!=1:raise ValueError('Changed HYCOM declared array type/dimensions')
    parts={}
    for i,h in enumerate(headers):
        key=(h[1],h[2]);body=text[h.end():headers[i+1].start() if i+1<len(headers) else len(text)].strip()
        if key in parts:raise ValueError('Duplicate HYCOM array/map')
        if h[2] in ['water_u','water_v']:
            if h[1]!=h[2] or h[3]!=f'[{nt}][1][{ny}][{nx}]':raise ValueError('Changed HYCOM cube dimensions')
            array=np.empty((nt,ny,nx),dtype='<i2');lines=body.splitlines()
            if len(lines)!=nt*ny:raise ValueError('Missing HYCOM rows')
            for row,line in enumerate(lines):
                m=re.fullmatch(r'\[(\d+)\]\[0\]\[(\d+)\],\s*(.*)',line.strip())
                if m is None or (int(m[1]),int(m[2]))!=divmod(row,ny):raise ValueError('Changed HYCOM row order/identity')
                tokens=[token.strip() for token in m[3].split(',')]
                if len(tokens)!=nx or any(re.fullmatch(r'-?\d+',token) is None for token in tokens):raise ValueError('Malformed packed HYCOM row')
                values=[int(token) for token in tokens]
                if any(v < -32768 or v > 32767 for v in values):raise ValueError('HYCOM value outside Int16')
                array[divmod(row,ny)]=values
            parts[key]=array
        else:
            values=np.array([float(x) for x in body.split(',')],dtype='<f8')
            expected={'time':nt,'depth':1,'lat':ny,'lon':nx}[h[2]]
            if h[3]!=f'[{expected}]' or values.shape!=(expected,) or not np.all(np.isfinite(values)):raise ValueError('Changed HYCOM coordinate map')
            parts[key]=values
    arrays={name:parts['water_u',name] for name in ['time','depth','lat','lon']}
    if any(not np.array_equal(parts['water_v',name],value) for name,value in arrays.items()):raise ValueError('HYCOM components have different coordinates')
    arrays.update({name:parts[name,name] for name in ['water_u','water_v']})
    return arrays


def check_metadata(das):
    for var in ['water_u','water_v']:
        match=re.search(r'\b'+var+r' \{(.*?)\n    \}',das,re.S)
        if not match:raise ValueError('Missing HYCOM velocity metadata')
        for token in ['Int16 _FillValue -30000;','Float32 scale_factor 0.001;','Float32 add_offset 0.0;','String units "m/s";']:
            if token not in match[1]:raise ValueError('Changed HYCOM packing/units')
    for token in ['String units "hours since 2000-01-01 00:00:00";','String calendar "gregorian";']:
        if token not in das:raise ValueError('Changed HYCOM clock convention')
    if 'String distribution_statement "Approved for public release. Distribution unlimited.";' not in das:
        raise ValueError('Changed HYCOM source distribution statement')


def check_cube(arrays,original):
    if arrays['depth'].tolist()!=[100] or arrays['water_u'].shape!=(366,76,51) or arrays['water_v'].shape!=(366,76,51):raise ValueError('Changed declared HYCOM support')
    for name,bounds in [('lat',[-38,-32]),('lon',[130,134])]:
        axis=arrays[name]
        tolerance=1e-4 if name=='lon' else 5e-5
        if np.any(np.abs(axis[[0,-1]]-bounds)>2e-5) or np.any(np.abs(np.diff(axis)-.08)>tolerance):
            raise ValueError(f'Changed HYCOM geographic selection: {name} endpoints {axis[[0,-1]].tolist()}')
        if name=='lon' and np.any(np.abs(axis-(130+np.arange(51)*.08))>1e-4):raise ValueError('Changed HYCOM native longitude support')
    for name in ['time','depth','lat']:
        if not np.array_equal(arrays[name],original[name]):raise ValueError('Changed HYCOM original coordinate overlap: '+name)
    if original['lon'].tolist()!=[132]:raise ValueError('Changed original HYCOM longitude')
    indices=np.flatnonzero(arrays['lon']==132)
    if len(indices)!=1:raise ValueError('Missing unique132Eoverlap')
    index=int(indices[0])
    for name in ['water_u','water_v']:
        if not np.array_equal(arrays[name][:,:,index],original[name][:,:,0]):raise ValueError('Changed HYCOM packed original overlap: '+name)
    dates=[datetime(2000,1,1,tzinfo=timezone.utc)+timedelta(hours=float(v)) for v in arrays['time']]
    expected=[datetime(2012,1,1,tzinfo=timezone.utc)+timedelta(days=i) for i in range(366)]
    if dates!=expected:raise ValueError('Changed Gregorian2012daily00Zclock')
    return dates,index


def quality(arrays,dates,index):
    u,v=arrays['water_u'],arrays['water_v'];valid=(u!=-30000)&(v!=-30000)
    fields={}
    for name in ['water_u','water_v']:
        a=arrays[name];finite=a[a!=-30000]
        fields[name]={'dtype':a.dtype.str,'shape':list(a.shape),'valid':int(finite.size),'missing':int(np.count_nonzero(a==-30000)),
                      'minimum_m_s':float(finite.min())*.001 if finite.size else None,'maximum_m_s':float(finite.max())*.001 if finite.size else None}
    months=[]
    for month in range(1,13):
        indices=[i for i,d in enumerate(dates) if d.month==month];counts=valid[indices].sum(axis=0)
        months.append({'year':2012,'month':month,'source_indices':indices,'days':len(indices),
                       'paired_cells':int(counts.sum()),'cells_with_80_percent_paired_support':int(np.count_nonzero(counts>=math.ceil(.8*len(indices))))})
    return {'schema':'osw.south-australian-hycom-2d-source-quality.v1',
            'status':'surrounding_model_source_vectors_not_named_current_admission','current_id':'south-australian',
            'fields':fields,'source_dates':366,'source_grid_positions':76*51,'vector_positions':int(valid.size),
            'paired_positions':int(valid.sum()),'missing_pairs':int((~valid).sum()),
            'paired_counts_by_cell':valid.sum(axis=0).tolist(),
            'paired_counts_by_date':[int(n) for n in valid.sum(axis=(1,2))],
            'cells_with_time_varying_pair_mask':int(np.any(valid!=valid[0],axis=0).sum()),
            'static_mask_proves_coast_or_bathymetric_current_edge':False,
            'first_time_utc':dates[0].isoformat(),'last_time_utc':dates[-1].isoformat(),'depth_m':100,
            'longitude_bounds':[130,134],'latitude_bounds':[-38,-32],
            'native_longitude_bounds':arrays['lon'][[0,-1]].tolist(),
            'native_latitude_bounds':arrays['lat'][[0,-1]].tolist(),
            'native_longitude_spacing_range':list(map(float,[np.diff(arrays['lon']).min(),np.diff(arrays['lon']).max()])),
            'maximum_nominal_longitude_deviation_degrees':float(np.abs(arrays['lon']-(130+np.arange(51)*.08)).max()),
            'source_132e_overlap':{'longitude_index_in_subset':index,'scalar_values_compared':55632,'all_packed_values_and_masks_equal':True,
                                  'original_file':ORIGINAL,'original_sha256':ORIGINAL_SHA},
            'months':months,'current_association_verified':False,'width_measurement_admitted':False,
            'annual_range_admitted':False,'whole_current_width_km':None,'geographic_current_edges':None}


def verify(directory=DIRECTORY):
    directory=Path(directory);receipt=json.loads((directory/'acquisition.json').read_bytes())
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or sha(ROOT/ORIGINAL)!=ORIGINAL_SHA:raise ValueError('Changed declared HYCOM source-selection input')
    if receipt['schema']!='osw.south-australian-hycom-2d-acquisition.v1' or set(receipt['files'])!=set(urls())|{'source-vectors.npz','quality.json'}:
        raise ValueError('Changed HYCOM receipt inventory/schema')
    for file_key,hash_key in [('protocol_file','protocol_sha256'),('operator_file','operator_sha256'),('npz_writer_file','npz_writer_sha256')]:
        expected={'protocol_file':PROTOCOL,'operator_file':OPERATOR,'npz_writer_file':'analysis/acquire_eac_100m_source.py'}[file_key]
        if receipt[file_key]!=expected or sha(ROOT/expected)!=receipt[hash_key]:raise ValueError('Changed HYCOM source operator/protocol pin')
    if receipt['current_association_verified'] is not False or receipt['width_measurement_admitted'] is not False:
        raise ValueError('Source receipt cannot admit a current measurement')
    for name,entry in receipt['files'].items():
        if name in urls() and entry['url']!=urls()[name]:raise ValueError('Changed HYCOM source URL')
        if sha(directory/name)!=entry['sha256'] or (directory/name).stat().st_size!=entry['bytes']:raise ValueError('Changed HYCOM retained source bytes')
    raw=(directory/'cube.ascii').read_text(encoding='utf8');arrays=parse_ascii(raw)
    check_coordinate_response((directory/'coordinates.ascii').read_text(encoding='utf8'),arrays)
    check_metadata((directory/'metadata.das').read_text(encoding='utf8'))
    original=parse_ascii((ROOT/ORIGINAL).read_text(encoding='utf8'),nx=1);dates,index=check_cube(arrays,original)
    with np.load(directory/'source-vectors.npz',allow_pickle=False) as stored:
        if set(stored.files)!=set(arrays):raise ValueError('Incomplete HYCOM retained numerical subset')
        for name,array in arrays.items():
            if stored[name].dtype!=array.dtype or stored[name].shape!=array.shape or stored[name].tobytes()!=array.tobytes():raise ValueError('Lost HYCOM source bits: '+name)
    report=quality(arrays,dates,index)
    if json.loads((directory/'quality.json').read_bytes())!=report:raise ValueError('Changed HYCOM source-quality report')
    return receipt,arrays,report


def acquire(directory=DIRECTORY):
    directory=Path(directory)
    if directory.exists():raise ValueError('HYCOM2Dsource already exists; refusing overwrite')
    if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or sha(ROOT/ORIGINAL)!=ORIGINAL_SHA:raise ValueError('Changed frozen HYCOM selection/oracle')
    stage_root=ROOT/'.pytest_cache/south-australian-2d-gap';stage_root.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='source-',dir=stage_root))
    print('Retaining acquisition in',stage,flush=True)
    try:
        return acquire_staged(directory,stage)
    except Exception as error:
        (stage/'failure.json').write_text(json.dumps({'failed_utc':datetime.now(timezone.utc).isoformat(),
            'error_type':type(error).__name__,'error':str(error),'protocol_sha256':PROTOCOL_SHA},indent=2)+'\n')
        raise


def acquire_staged(directory,stage):
    responses={};records=json.loads((stage/'responses.json').read_bytes()) if (stage/'responses.json').exists() else {}
    for name,url in urls().items():
        if name in records:
            data=(stage/name).read_bytes();record=records[name]
            if record['url']!=url or record['bytes']!=len(data) or record['sha256']!=hashlib.sha256(data).hexdigest():raise ValueError('Changed retained staged HYCOM response')
            print('Reusing checked',name,len(data),'bytes',flush=True);responses[name]=data;continue
        print('Acquiring',name,flush=True)
        request=urllib.request.Request(url,headers={'User-Agent':'OSW-source-validation/1.0'})
        with urllib.request.urlopen(request,timeout=60) as response:
            data=response.read(LIMIT+1)
            headers={k:response.headers[k] for k in ['Content-Type','Content-Length','ETag','Last-Modified','Date'] if k in response.headers}
        if len(data)>LIMIT:raise ValueError('Oversized HYCOM source response')
        (stage/name).write_bytes(data)
        print('Retained',name,len(data),'bytes',flush=True)
        responses[name]=data;records[name]={'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'response_headers':headers}
        (stage/'responses.json').write_text(json.dumps(records,indent=2)+'\n')
    arrays=parse_ascii(responses['cube.ascii'].decode('utf8'));check_metadata(responses['metadata.das'].decode('utf8'))
    check_coordinate_response(responses['coordinates.ascii'].decode('utf8'),arrays)
    original=parse_ascii((ROOT/ORIGINAL).read_text(encoding='utf8'),nx=1);dates,index=check_cube(arrays,original)
    report=quality(arrays,dates,index)
    write_npz(stage/'source-vectors.npz',arrays)
    (stage/'quality.json').write_bytes((json.dumps(report,indent=2,allow_nan=False)+'\n').encode())
    for name in ['source-vectors.npz','quality.json']:records[name]={'bytes':(stage/name).stat().st_size,'sha256':sha(stage/name)}
    receipt={'schema':'osw.south-australian-hycom-2d-acquisition.v1','acquired_utc':datetime.now(timezone.utc).isoformat(),
             'provider':'HYCOM/NAVO/NRL, GOFS3.0 HYCOM+NCODA reanalysis',
             'rights':'Original NC_GLOBAL distribution_statement: Approved for public release. Distribution unlimited.',
             'protocol_file':PROTOCOL,'protocol_sha256':PROTOCOL_SHA,'operator_file':OPERATOR,'operator_sha256':sha(ROOT/OPERATOR),
             'npz_writer_file':'analysis/acquire_eac_100m_source.py','npz_writer_sha256':sha(ROOT/'analysis/acquire_eac_100m_source.py'),
             'files':records,'current_association_verified':False,'width_measurement_admitted':False}
    if (stage/'response-intake-operator.py').exists():receipt['prior_response_intake_operator_sha256']=sha(stage/'response-intake-operator.py')
    if (stage/'failure.json').exists():receipt['prior_intake_failure']=json.loads((stage/'failure.json').read_bytes())
    (stage/'acquisition.json').write_bytes((json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode())
    verify(stage)
    directory.mkdir(parents=True)
    for name in list(records)+['acquisition.json']:shutil.copyfile(stage/name,directory/name)
    return verify(directory)


if __name__=='__main__':
    parser=argparse.ArgumentParser();choice=parser.add_mutually_exclusive_group();choice.add_argument('--acquire',action='store_true');choice.add_argument('--resume-stage',type=Path);args=parser.parse_args()
    if args.resume_stage:
        if DIRECTORY.exists():raise ValueError('Refusing overwrite of retained HYCOM source')
        if sha(ROOT/PROTOCOL)!=PROTOCOL_SHA or sha(ROOT/ORIGINAL)!=ORIGINAL_SHA:raise ValueError('Changed frozen HYCOM selection/oracle')
        receipt,arrays,report=acquire_staged(DIRECTORY,args.resume_stage)
    else:receipt,arrays,report=acquire() if args.acquire else verify()
    print(json.dumps({'source_dates':report['source_dates'],'paired_positions':report['paired_positions'],'overlap':report['source_132e_overlap']}))
