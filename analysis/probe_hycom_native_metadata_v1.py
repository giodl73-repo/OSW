"""Bounded cloud-only HYCOM metadata diagnosis; never request velocity/salinity."""
import base64,hashlib,json,re,urllib.error,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/hycom-ncc-mid-norway-metadata-probe-operator-v1.json'
OUT=Path('hycom-ncc-mid-norway-metadata-probe-v1')
PREFIX='https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/'
REQUESTS=[{'dataset':product,'kind':kind,'axis':axis,'url':PREFIX+product+'/2022'+suffix} for product in ['uv3z','ts3z'] for kind,axis,suffix in [('dds',None,'.dds'),('das',None,'.das')]+[('axis',axis,'.ascii?'+axis+'%5B0:1:0%5D') for axis in ['depth','lat','lon','time']]]
LIMIT=128000


def encode(v):return (json.dumps(v,indent=2,allow_nan=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()


class MetadataRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError('No metadata redirects or additional HTTP attempts permitted')


def recognized(request,raw):
    text=raw.decode('utf8',errors='replace').lstrip()
    if request['kind']=='das':return text.startswith('Attributes {') and 'field_type' in text and 'instantaneous' in text
    if not text.startswith('Dataset {'):return False
    required=['water_u','water_v'] if request['dataset']=='uv3z' else ['salinity']
    if request['kind']=='axis':required=[request['axis']]
    return all(re.search(r'\b'+name+r'\b',text) for name in required)


def probe(root=ROOT,out=OUT,opener=None):
    read=lambda p:(root/p).read_bytes();op=json.loads(read(OPERATOR))
    if op['requests']!=REQUESTS or op['maximum_response_body_bytes']!=LIMIT or op['network_operation_timeout_seconds']!=15 or op['new_velocity_or_salinity_field_requests']!=0:raise ValueError('Fixed metadata/schema/first-coordinate-only requests and bounds required')
    for file,pin in op['input_sha256'].items():
        if digest(read(file))!=pin:raise ValueError('Frozen metadata-probe input changed: '+file)
    out=Path(out);out.mkdir(exist_ok=True);report={'schema':'osw.hycom-bounded-native-metadata-probe.v1','status':'PROBE_PENDING','operator_file':OPERATOR,'operator_sha256':digest(read(OPERATOR)),'input_sha256':op['input_sha256'],'started_at_utc':datetime.now(timezone.utc).isoformat(),'requests':[],'new_velocity_or_salinity_field_requests':0,'maximum_coordinate_scalars_requested':8,'native_coordinate_pairing_established':False,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False}
    save=lambda:(out/'probe-report.json').write_bytes(encode(report));save();opener=opener or urllib.request.build_opener(MetadataRedirects())
    for index,spec in enumerate(REQUESTS):
        row={**spec,'status':'REQUEST_PENDING','attempts':1,'network_operation_timeout_seconds':15};report['requests'].append(row);save();raw=b'';http_status=None;error=None
        request=urllib.request.Request(spec['url'],headers={'User-Agent':'OSW-bounded-metadata-diagnosis','Accept-Encoding':'identity'})
        try:
            with opener.open(request,timeout=15) as response:
                http_status=response.status;raw=response.read(LIMIT+1)
        except urllib.error.HTTPError as failure:
            http_status=failure.code;error=type(failure).__name__
            try:raw=failure.read(LIMIT+1)
            except (TimeoutError,OSError) as read_error:error+=':'+type(read_error).__name__
            finally:failure.close()
        except (urllib.error.URLError,TimeoutError,OSError,ValueError) as failure:error=type(failure).__name__
        truncated=len(raw)>LIMIT;body=raw[:LIMIT];ok=error is None and http_status==200 and not truncated and recognized(spec,body)
        payload={'schema':'osw.hycom-metadata-response-body.v1','request':spec,'http_status':http_status,'error_type':error,'retained_response_body_bytes':len(body),'retained_response_body_sha256':digest(body),'response_body_truncated':truncated,'retained_response_body_base64':base64.b64encode(body).decode(),'wire_hash_claimed':False}
        name=f'response-{index+1}.json';encoded=encode(payload);(out/name).write_bytes(encoded)
        row.update(status='RECOGNIZED_METADATA_RESPONSE' if ok else 'METADATA_UNAVAILABLE_OR_UNRECOGNIZED',http_status=http_status,error_type=error,response={'file':name,'bytes':len(encoded),'sha256':digest(encoded)},response_body_truncated=truncated);save();print(json.dumps({k:row[k] for k in ['dataset','kind','axis','status','http_status','error_type']}),flush=True)
    report['status']='ALL12_METADATA_ENDPOINTS_RESPONDED' if all(r['status']=='RECOGNIZED_METADATA_RESPONSE' for r in report['requests']) else 'SOURCE_METADATA_DIAGNOSIS_COMPLETE_WITH_UNAVAILABLE_ENDPOINTS';report['finished_at_utc']=datetime.now(timezone.utc).isoformat();save()
    if sum(p.stat().st_size for p in out.glob('*.json'))>=2400000:raise ValueError('Fixed complete metadata source-batch cap exceeded')
    print(json.dumps({'status':report['status'],'new_velocity_or_salinity_field_requests':0}),flush=True)


if __name__=='__main__':probe()
