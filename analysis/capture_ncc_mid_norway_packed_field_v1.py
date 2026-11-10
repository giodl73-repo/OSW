"""Cloud-only first field capture with the entire original eight-case reserve."""
import base64,gzip,hashlib,json,re,subprocess,sys,urllib.request
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import acquire_ncc_mid_norway_joint_sections_v1 as mid
import hycom_packed_int16_v1 as packed
import probe_hycom_http_coordinates_v1 as coordinates

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/ncc-mid-norway-packed-field-capture-operator-v1.json'
OUT=Path('ncc-mid-norway-packed-field-capture-v1')
PACKET='research/source-data/hycom-http-coordinate-probe-v2/'


def encode(obj):return (json.dumps(obj,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(path,obj):
    path=Path(path);temp=path.with_suffix('.pending');temp.write_bytes(encode(obj));temp.replace(path)


def verify(root):
    op=json.loads((root/OPERATOR).read_bytes())
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Pinned input changed: '+file)
    if op['network_timeout_seconds']!=15 or op['worker_timeout_seconds']!=90 or op['requests_in_this_stage']!=1 or op['cohort_field_targets']!=24:raise ValueError('Fixed format-capture contract required')
    return op


def das(root,number):
    receipt=json.loads((root/(PACKET+'http-response-'+str(number)+'.json')).read_bytes())
    raw=base64.b64decode(receipt['retained_response_body_base64'],validate=True)
    if receipt['http_status']!=200 or receipt['error_type'] is not None or receipt['response_body_truncated'] or len(raw)!=receipt['retained_response_body_bytes'] or digest(raw)!=receipt['retained_response_body_sha256']:raise ValueError('Exact successful retained DAS required')
    return raw


class CachedDataset:
    """Only retained coordinates and metadata; no model values during preflight."""
    def __init__(self,root,product,raw,specs):
        self.attrs=coordinates.das_strings(raw);self.variables={};self.arrays={}
        for axis in ['depth','lat','lon','time']:
            record=json.loads((root/(PACKET+product+'-'+axis+'.json')).read_bytes())
            if record['dataset']!=mid.frozen.UV.replace('uv3z',product) or record['axis']!=axis:raise ValueError('Original retained coordinate identity required')
            self.arrays[axis]=np.asarray(record['values'],dtype=np.float64)
            self.variables[axis]=Coordinate(self.arrays[axis],self.attrs[axis])
        for field,spec in specs.items():
            self.variables[field]=SimpleNamespace(dimensions=('time','depth','lat','lon'),units=json.loads(spec['attributes']['units']['literal']),standard_name=json.loads(spec['attributes']['standard_name']['literal']))
    def __getitem__(self,key):return self.variables[key]
    def getncattr(self,key):return self.attrs['NC_GLOBAL'][key]


class Coordinate:
    def __init__(self,array,attrs):self.array=array;self.__dict__.update(attrs)
    def __getitem__(self,key):
        if key!=slice(None):raise ValueError('Only full native coordinate read allowed')
        return self.array.copy()


def full_plan(root):
    uv_das=das(root,2);ts_das=das(root,8)
    specs={field:packed.specification(ts_das if field=='salinity' else uv_das,field) for field in packed.FIELDS}
    uv=CachedDataset(root,'uv3z',uv_das,{k:v for k,v in specs.items() if k!='salinity'})
    ts=CachedDataset(root,'ts3z',ts_das,{'salinity':specs['salinity']})
    original=json.loads((root/mid.OPERATOR).read_bytes())
    for file,pin in original['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Original scientific input changed: '+file)
    with mid.configured():axes,plans,total,times=mid.frozen.preflight(uv,ts,original)
    targets=[]
    for stamp,it in times:
        for plan in plans:
            ix=plan['longitude_indices'];iy=int(plan['latitude_index'])
            for field in ['water_u','water_v','salinity']:
                targets.append({'variable':field,'section_id':plan['definition']['id'],'snapshot_time_utc':stamp,'time_index':it,'latitude_index':iy,'longitude_indices_inclusive':[int(ix[0]),int(ix[-1])],'depth_indices_inclusive':[0,39],'native_shape':[1,40,1,len(ix)],'scalar_values':40*len(ix)})
    return specs,{'schema':'osw.ncc-mid-norway-http-cohort-preflight.v1','scientific_operator':mid.OPERATOR,'scientific_operator_sha256':digest((root/mid.OPERATOR).read_bytes()),'metadata_provenance':'retained full coordinate packet v2; not a new remote grid verification','all_eight_cases_preflighted_before_fields':True,'planned_velocity_cell_pairs':total,'planned_salinity_scalars':total,'planned_first_attempt_scalar_values':3*total,'joint_reserved_native_cell_units':2*total,'conservative_joint_decoded_bytes':24*total,'maximum_joint_native_cell_units':250000,'maximum_decoded_bytes':7000000,'targets':targets,'core_reselected':False,'physical_current_bottom_established':False}


def field_url(target):
    field=target['variable'];it=target['time_index'];iy=target['latitude_index'];x0,x1=target['longitude_indices_inclusive']
    if field not in packed.FIELDS or target['depth_indices_inclusive']!=[0,39] or target['native_shape']!=[1,40,1,x1-x0+1] or not 3<=x1-x0+1<=150 or any(type(v)!=int or v<0 for v in [it,iy,x0,x1]):raise ValueError('Exact original bounded native patch required')
    root=mid.frozen.TS if field=='salinity' else mid.frozen.UV
    return root+'.ascii?'+field+urllib.parse.quote(f'[{it}:1:{it}][0:1:39][{iy}:1:{iy}][{x0}:1:{x1}]',safe=':')


def structure(raw):
    """Keep exact DDS and index labels; never emit field values into summaries."""
    parts=raw.decode('utf8').split('---------------------------------------------')
    if len(parts)!=2 or not parts[0].lstrip().startswith('Dataset {'):raise ValueError('Original ASCII DDS plus data separator required')
    labels=[]
    for line in parts[1].splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('['):
            found=re.match(r'^(?:\[\d+\])+',line)
            if not found:raise ValueError('Unknown row label format')
            labels.append(found.group(0))
        elif re.match(r'^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?(?:\[\d+\])+\s*$',line):labels.append(line)
    return {'dds_header':parts[0],'data_labels_in_order':labels,'field_numeric_values_emitted':False,'field_numeric_values_verified':False}


def worker(root=ROOT,out=OUT,opener=None):
    verify(root);out=Path(out);out.mkdir(exist_ok=True)
    specs,plan=full_plan(root);save(out/'cohort-preflight.json',plan);save(out/'packed-specifications.json',specs)
    save(out/'decoder-conformance.json',packed.conformance(specs))
    target=plan['targets'][0];url=field_url(target);cap=32*target['scalar_values']+16384
    ledger={'schema':'osw.ncc-mid-norway-first-http-field-ledger.v1','cohort_preflight_sha256':digest((out/'cohort-preflight.json').read_bytes()),'joint_reserved_native_cell_units':plan['joint_reserved_native_cell_units'],'conservative_joint_decoded_bytes':plan['conservative_joint_decoded_bytes'],'actual_requested_scalar_values':target['scalar_values'],'verified_returned_scalar_values':0,'requests':[{'target':target,'url':url,'attempt':1,'status':'PENDING','network_timeout_seconds':15,'maximum_response_body_bytes':cap}],'retries':0,'successful_fields_replayed':False,'wire_hash_claimed':False}
    if (out/'field-response.json').exists() or (out/'http-ledger.json').exists():raise ValueError('Never replay an existing attempted or successful field capture')
    save(out/'http-ledger.json',ledger)
    opener=opener or urllib.request.build_opener(coordinates.NoRedirects())
    raw=b'';status=None;error=None
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'OSW-native-current-depth-cohort','Accept-Encoding':'identity'})
        with opener.open(request,timeout=15) as response:status=response.status;raw=response.read(cap+1)
    except Exception as failure:error=type(failure).__name__
    truncated=len(raw)>cap;raw=raw[:cap]
    receipt={'schema':'osw.hycom-packed-native-http-response.v1','target':target,'url':url,'http_status':status,'error_type':error,'response_body_truncated':truncated,'response_body_bytes':len(raw),'response_body_sha256':digest(raw),'response_body_gzip_base64':base64.b64encode(gzip.compress(raw,mtime=0)).decode(),'wire_hash_claimed':False,'native_values_verified':False}
    save(out/'field-response.json',receipt);ledger['requests'][0].update(status='RAW_RESPONSE_RETAINED' if status==200 and error is None and not truncated else 'FAILED_NOT_RETRIED',http_status=status,error_type=error,response_sha256=digest((out/'field-response.json').read_bytes()));save(out/'http-ledger.json',ledger)
    if ledger['requests'][0]['status']!='RAW_RESPONSE_RETAINED':raise ValueError('First original field request failed; retained failure receipt; no retry')
    shape=structure(raw);save(out/'ascii-structure.json',shape)
    report={'status':'FIRST_ORIGINAL_FIELD_RAW_RESPONSE_RETAINED_FOR_FORMAT_REVIEW','cohort_cases':8,'cohort_field_targets':24,'field_requests_this_stage':1,'remaining_field_targets':23,'successful_field_raw_response_must_be_reused':True,'field_values_admitted':0,'new_depth_references':0,'physical_current_bottom_established':False,'full_goal_complete':False}
    save(out/'worker-report.json',report);print(json.dumps(report),flush=True)


def capture(root=ROOT,out=OUT):
    verify(root);out=Path(out);out.mkdir(exist_ok=True)
    try:
        process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--worker',str(out)],capture_output=True,timeout=90)
        report={'status':'WORKER_FINISHED','returncode':process.returncode};logs=(process.stdout+process.stderr)[-12000:].decode('utf8',errors='replace')
    except subprocess.TimeoutExpired as failure:
        report={'status':'WORKER_KILLED_AT_FIXED_90_SECOND_BOUND','returncode':None};logs=((failure.stdout or b'')+(failure.stderr or b''))[-12000:].decode('utf8',errors='replace')
    save(out/'process-report.json',{**report,'log':logs,'full_goal_complete':False});print(json.dumps(report),flush=True)
    if report['returncode']!=0:raise RuntimeError('Capture incomplete; inspect retained stage receipts; do not blindly replay')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':worker(out=Path(sys.argv[2]))
    elif len(sys.argv)==1:capture()
    else:raise ValueError('Only fixed capture parent/worker invocations allowed')
