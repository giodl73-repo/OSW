"""Recover an unchanged daily cohort with genuine single-date provider responses."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from urllib.parse import quote, unquote
from urllib.request import urlopen

import numpy as np
from acquire_eac_100m_source import write_json
from acquire_indian_secc_hycom_2013 import pin, coordinates, write_stored_npz
from acquire_south_indian_hycom_hydrography import (
    ROOT, FIELDS, BASE, LIMIT, validate_plan, validate_response, common_means)

OPERATOR='analysis/south_indian_hycom_single_date_resume.py'
PROTOCOL='plans/south-indian-hycom-single-date-transport-v1.md'
DECLARATION='research/south-indian-hycom-single-date-resume.json'
PREVIOUS='research/south-indian-hycom-longer-timeout-resume.json'
ARCHIVE_DECLARATION='single-date-resume.json'
TIMEOUT=180


def subdivisions(request):
    base,query=request['url'].split('?',1)
    query=unquote(query)
    result=[]
    for i,index in enumerate(request['time_indices']):
        pattern=r'\b('+'|'.join(FIELDS)+r')\[\d+:\d+:\d+\]'
        body,count=re.subn(pattern,lambda m:f'{m[1]}[{index}:1:{index}]',query)
        if count!=len(FIELDS):
            raise ValueError('Cannot subdivide all four source variable time slices')
        result.append({'file':Path(request['file']).stem+f'-t{i:02d}.ascii',
                       'month':request['month'],'time_indices':[index],
                       'url':base+'?'+quote(body,safe=''),
                       'logical_request_file':request['file']})
    return result


def effective_requests(plan,declaration):
    matches=[r for r in plan['requests'] if r['file']==declaration['logical_request_file']]
    if len(matches)!=1 or matches[0]!=declaration['original_request']:
        raise ValueError('Changed logical source request')
    expected=subdivisions(matches[0])
    if declaration['subrequests']!=expected:
        raise ValueError('Changed subdivision: time/field/grid coverage must be exact')
    result=[]
    for request in plan['requests']:
        result.extend(expected if request['file']==matches[0]['file'] else [request])
    if ([i for r in result for i in r['time_indices']]
            !=[i for r in plan['requests'] for i in r['time_indices']]):
        raise ValueError('Changed daily source cohort/order')
    return result


def dependency_pins(plan):
    previous=json.loads((ROOT/PREVIOUS).read_bytes())
    return {**plan['operators'],**plan['rules'],**previous['dependencies'],
            PREVIOUS:pin(ROOT/PREVIOUS),OPERATOR:pin(ROOT/OPERATOR),PROTOCOL:pin(ROOT/PROTOCOL)}


def declare(directory):
    directory=Path(directory);plan=validate_plan(directory)
    if (ROOT/DECLARATION).exists() or (directory/ARCHIVE_DECLARATION).exists():
        raise ValueError('Existing subdivision declaration must not be replaced')
    before={};missing=[]
    for request in plan['requests']:
        path=directory/request['file'];rp=path.with_suffix('.receipt.json')
        if path.exists()!=rp.exists():
            raise ValueError('Incomplete original/receipt pair requires inspection')
        if not path.exists():
            missing.append(request);continue
        receipt=json.loads(rp.read_bytes())
        if receipt['url']!=request['url'] or receipt['pin']!=pin(path):
            raise ValueError('Changed successful original')
        validate_response(path.read_bytes(),request,plan,directory)
        before[path.name]={'response':pin(path),'receipt':pin(rp)}
    if len(missing)!=1 or len(missing[0]['time_indices'])<2:
        raise ValueError('This declaration requires exactly one missing multi-date request')
    request=missing[0]
    document={'schema':'osw.south-indian-hycom-single-date-transport.v1',
              'declared_utc':datetime.now(timezone.utc).isoformat(),
              'source_selection':pin(directory/'selection.json'),
              'dependencies':dependency_pins(plan),'existing_successful_originals':before,
              'logical_request_file':request['file'],'original_request':request,
              'subrequests':subdivisions(request),'timeout_seconds':TIMEOUT,
              'workers':2,'response_byte_limit':LIMIT,
              'scope':'Mechanical transport subdivision only. Exact same source timestamp cohort, four variables, native depths/latitude/longitude, masks, arithmetic and byte checks. No synthesized multi-date provider response.',
              'current_association_verified':False,'physical_width_admitted':False}
    effective_requests(plan,document)
    write_json(ROOT/DECLARATION,document)
    (directory/ARCHIVE_DECLARATION).write_bytes((ROOT/DECLARATION).read_bytes())
    return document


def checked(directory):
    directory=Path(directory);plan=validate_plan(directory)
    path=directory/ARCHIVE_DECLARATION
    if pin(path)!=pin(ROOT/DECLARATION):
        raise ValueError('Changed archived transport declaration')
    document=json.loads(path.read_bytes())
    if (document['schema']!='osw.south-indian-hycom-single-date-transport.v1'
            or document['source_selection']!=pin(directory/'selection.json')
            or document['dependencies']!=dependency_pins(plan)
            or document['timeout_seconds']!=TIMEOUT or document['workers']!=2
            or document['response_byte_limit']!=LIMIT
            or document['current_association_verified'] is not False
            or document['physical_width_admitted'] is not False):
        raise ValueError('Changed subdivision declaration/support')
    for name,expected in document['dependencies'].items():
        if pin(ROOT/name)!=expected:
            raise ValueError('Changed declared dependency: '+name)
    expected_before={r['file'] for r in plan['requests']} - {document['logical_request_file']}
    if set(document['existing_successful_originals'])!=expected_before:
        raise ValueError('Changed successful original set')
    for name,expected in document['existing_successful_originals'].items():
        path=directory/name
        if pin(path)!=expected['response'] or pin(path.with_suffix('.receipt.json'))!=expected['receipt']:
            raise ValueError('Previously successful original/receipt changed')
    return plan,document,effective_requests(plan,document)


def acquire(directory):
    directory=Path(directory);plan,document,_=checked(directory)
    def one(request):
        path=directory/request['file'];rp=path.with_suffix('.receipt.json')
        if path.exists()!=rp.exists():raise ValueError('Incomplete source pair requires inspection')
        if path.exists():
            receipt=json.loads(rp.read_bytes())
            if receipt['url']!=request['url'] or receipt['pin']!=pin(path):raise ValueError('Changed original')
            validate_response(path.read_bytes(),request,plan,directory)
            print('retained',path.name,flush=True);return
        try:
            with urlopen(request['url'],timeout=TIMEOUT) as response:
                raw=response.read(LIMIT+1);headers=dict(response.headers);final=response.url
            if len(raw)>LIMIT:raise ValueError('Oversized source response')
            validate_response(raw,request,plan,directory)
            path.write_bytes(raw)
            write_json(rp,{'url':request['url'],'final_url':final,'pin':pin(path),
                          'acquired_utc':datetime.now(timezone.utc).isoformat(),'headers':headers,
                          'logical_request_file':request['logical_request_file'],
                          'single_date_transport_declaration':{'path':DECLARATION,'pin':pin(ROOT/DECLARATION)},
                          'timeout_seconds':TIMEOUT})
            print('acquired',path.name,len(raw),flush=True)
        except Exception as error:
            with (directory/'failures.jsonl').open('a',encoding='utf8') as stream:
                stream.write(json.dumps({'file':request['file'],'url':request['url'],
                             'utc':datetime.now(timezone.utc).isoformat(),'error':repr(error),
                             'operation':'declared_single_date_transport','timeout_seconds':TIMEOUT})+'\n')
            raise
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(one,r) for r in document['subrequests']];errors=[]
        for future in futures:
            try:future.result()
            except Exception as error:errors.append(repr(error))
    if errors:raise ValueError(f'{len(errors)} failed single-date requests; successful originals retained: {errors[0]}')
    checked(directory)


def compile_source(directory):
    """Same arithmetic as the frozen compiler; consume genuine expanded inputs."""
    directory=Path(directory);plan,declaration,requests=checked(directory)
    c=coordinates((directory/'coordinates.ascii').read_text(encoding='utf8'))
    products={name:c[name][plan['selection'][name]] for name in ['depth','lat','lon']}
    products['month']=np.arange(1,13,dtype='<i2');monthly=[];receipts={}
    for m in range(1,13):
        grids=[]
        for request in requests:
            if request['month']!=m:continue
            path=directory/request['file'];receipt=json.loads(path.with_suffix('.receipt.json').read_bytes())
            if receipt['url']!=request['url'] or receipt['pin']!=pin(path):raise ValueError('Changed original source response')
            grids.append(validate_response(path.read_bytes(),request,plan,directory));receipts[request['file']]=pin(path)
        expected=[i for r in plan['requests'] if r['month']==m for i in r['time_indices']]
        if not grids or not np.array_equal(np.concatenate([g['time'] for g in grids]),c['time'][expected]):
            raise ValueError('Incomplete or reordered monthly daily cohort')
        counts,means=common_means({name:np.concatenate([g[name] for g in grids]) for name in FIELDS},
                                  plan['minimum_pairs'][m-1],plan['scale'],plan['offsets'])
        monthly.append({'month':m,'sample_days':len(expected),'counts':counts,'means':means})
    products['common_samples']=np.stack([v['counts'] for v in monthly])
    products.update({name:np.stack([v['means'][name] for v in monthly]) for name in FIELDS})
    write_stored_npz(directory/'monthly.npz',products)
    def nullable(array):
        result=array.astype(object);result[~np.isfinite(array)]=None;return result.tolist()
    binding=pin(directory/ARCHIVE_DECLARATION)
    document={'schema':'osw.south-indian-hycom-hydrography-monthly.v1',
              'selection':pin(directory/'selection.json'),'dataset_url':BASE,'source_model_year':2013,
              'depth_m':products['depth'].tolist(),'latitude_degrees_north':products['lat'].tolist(),
              'longitude_degrees_east':products['lon'].tolist(),'units':{n:v[1] for n,v in FIELDS.items()},
              'months':[{'month':v['month'],'sample_days':v['sample_days'],
                         'minimum_common_samples':plan['minimum_pairs'][v['month']-1],
                         'common_samples':v['counts'].tolist(),
                         'fields':{n:nullable(v['means'][n]) for n in FIELDS}} for v in monthly],
              'interpretation':'Common-valid daily00Z model-field monthly sample means at two native levels; in-situ temperature; no vertical mean or geostrophic reference conversion.',
              'single_date_transport':binding,'current_association_verified':False,
              'physical_width_admitted':False,'physical_axis_admitted':False,'seasonal_footprint_admitted':False}
    (directory/'monthly-fields.json').write_bytes((json.dumps(document,separators=(',',':'),allow_nan=False)+'\n').encode())
    quality={'schema':'osw.south-indian-hycom-hydrography-quality.v1',
             'selection':pin(directory/'selection.json'),'original_responses':receipts,
             'products':{n:pin(directory/n) for n in ['monthly.npz','monthly-fields.json']},
             'single_date_transport':binding,'logical_requests':len(plan['requests']),
             'retained_physical_responses':len(requests),'missing_daily_00z':plan['missing_daily_00z'],
             'grid_shape':list(products['water_u'].shape),
             'months':[{'month':v['month'],'sample_days':v['sample_days'],
                        'depths':[{'depth_m':float(products['depth'][z]),
                                   'eligible_cells':int(np.isfinite(v['means']['water_u'][z]).sum()),
                                   'minimum_common_samples':int(v['counts'][z].min()),
                                   'maximum_common_samples':int(v['counts'][z].max())} for z in range(2)]} for v in monthly],
             'width_admission':False,'current_association_verified':False}
    write_json(directory/'quality.json',quality)
    return quality


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['declare','acquire','compile'])
    parser.add_argument('--directory',type=Path,default=ROOT/'.pytest_cache/south-indian-hycom-2013')
    args=parser.parse_args()
    if args.action=='declare':
        result=declare(args.directory)
        print(json.dumps({'retained_originals':len(result['existing_successful_originals']),
                          'logical_request':result['logical_request_file'],'subrequests':len(result['subrequests'])}))
    elif args.action=='acquire':acquire(args.directory)
    else:print(json.dumps(compile_source(args.directory)['products']))
