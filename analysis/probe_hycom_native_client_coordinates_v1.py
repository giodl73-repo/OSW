"""Bounded native-client coordinate diagnosis, never reading ocean model fields."""
import base64,hashlib,importlib,json,math,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OPERATOR='research/hycom-native-client-coordinate-probe-operator-v1.json'
OUT=Path('hycom-native-client-coordinate-probe-v1')
SOURCES={name:'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/'+name+'/2022' for name in ['uv3z','ts3z']}
SHAPES={'depth':40,'lat':4251,'lon':4500,'time':2920}
UNITS={'depth':'m','lat':'degrees_north','lon':'degrees_east'}


def encode(v):return (json.dumps(v,separators=(',',':'),allow_nan=False)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def stamp():return datetime.now(timezone.utc).isoformat()


def write_json(path,value):
    pending=path.with_suffix(path.suffix+'.pending');pending.write_bytes(encode(value));pending.replace(path)


def operator(root):
    op=json.loads((root/OPERATOR).read_bytes())
    if op['sources']!=SOURCES or op['coordinate_shapes']!=SHAPES or op['worker_wall_timeout_seconds']!=120 or op['maximum_native_coordinate_scalars']!=250000 or op['maximum_conservative_decoded_bytes']!=7000000 or op['new_velocity_or_salinity_field_requests']!=0:raise ValueError('Exact coordinate-only source and wall/native/decoded bounds required')
    for file,pin in op['input_sha256'].items():
        if digest((root/file).read_bytes())!=pin:raise ValueError('Frozen native-client-probe input changed: '+file)
    return op


def coordinate_variable(ds,axis):
    if axis not in SHAPES:raise ValueError('Model-field reads prohibited; only four native coordinate variables allowed')
    return ds[axis]


def worker(root=ROOT,out=OUT,factory=None):
    op=operator(root);out=Path(out);out.mkdir(exist_ok=True);report={'schema':'osw.hycom-native-client-coordinate-worker.v1','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'status':'WORKER_STARTING','stage':None,'stage_history':[],'records':[],'planned_native_coordinate_scalars':2*sum(SHAPES.values()),'actual_requested_native_coordinate_scalars':0,'returned_native_coordinate_scalars':0,'new_velocity_or_salinity_field_requests':0,'native_coordinate_pairing_established':False,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False};arrays={};time_context={}
    report['native_request_accounting']='explicit_coordinate_slices_not_backend_prefetch_or_HTTP_wire_bytes'
    save=lambda:write_json(out/'worker-report.json',report)
    def stage(name,dataset=None,axis=None):
        value={'operation':name,'dataset':dataset,'axis':axis,'at_utc':stamp()};report['stage']=value;report['stage_history'].append(value);save();print(json.dumps(value),flush=True)
    save()
    try:
        if factory is None:
            stage('IMPORT_NETCDF4');module=importlib.import_module('netCDF4');factory=module.Dataset;report['netcdf4_python_version']=module.__version__;report['netcdf_c_version']=module.__netcdf4libversion__;report['hdf5_version']=module.__hdf5libversion__;stage('IMPORT_NETCDF4_COMPLETE')
        planned=report['planned_native_coordinate_scalars']
        if planned>250000 or 8*planned>7000000:raise ValueError('Complete paired coordinate-only reservation exceeds fixed caps')
        for name,url in SOURCES.items():
            stage('DATASET_OPEN',name);ds=factory(url);stage('DATASET_OPEN_COMPLETE',name)
            try:
                stage('SOURCE_GLOBAL_METADATA',name);attrs={k:str(ds.getncattr(k)) for k in ds.ncattrs()}
                if attrs.get('field_type')!='instantaneous':raise ValueError('Original instantaneous source metadata required')
                arrays[name]={}
                for axis,size in SHAPES.items():
                    stage('COORDINATE_DESCRIPTOR',name,axis);var=coordinate_variable(ds,axis)
                    if tuple(var.shape)!=(size,) or tuple(var.dimensions)!=(axis,):raise ValueError('Exact retained DDS native coordinate shape required')
                    unit=str(var.units)
                    if axis in UNITS and unit!=UNITS[axis] or axis=='depth' and str(var.positive)!='down' or axis=='time' and 'since' not in unit:raise ValueError('Original native coordinate units/datum required')
                    if axis=='time':time_context[name]={'units':unit,'calendar':str(getattr(var,'calendar','gregorian'))}
                    report['actual_requested_native_coordinate_scalars']+=size;stage('COORDINATE_READ',name,axis);values=var[:].tolist()
                    if len(values)!=size or any(type(v) not in (int,float) or not math.isfinite(v) for v in values) or any(b<=a for a,b in zip(values,values[1:])):raise ValueError('Complete finite increasing native coordinate array required')
                    if axis=='depth' and (values[0]!=0 or values[-1]!=5000 or 100 not in values):raise ValueError('Original40native depth levels0-5000including100m required')
                    payload={'schema':'osw.hycom-native-coordinate-array.v1','dataset':url,'axis':axis,'shape':[size],'units':unit,'values':values,'coordinate_metadata_not_current_depth_measurement':True,'wire_hash_claimed':False};raw=encode(payload);file=name+'-'+axis+'.json'
                    if len(raw)>=2500000:raise ValueError('Fixed coordinate per-file cap exceeded')
                    write_json(out/file,payload);report['returned_native_coordinate_scalars']+=size;arrays[name][axis]=values;report['records'].append({'dataset':name,'axis':axis,'source_global_attributes':attrs,'piece':{'file':file,'bytes':len(raw),'sha256':digest(raw)}});stage('COORDINATE_READ_COMPLETE',name,axis)
            except Exception as error:
                report['failure_stage']=dict(report['stage']);report['error_type']=type(error).__name__;save();raise
            finally:stage('DATASET_CLOSE',name);ds.close();stage('DATASET_CLOSE_COMPLETE',name)
        stage('EXACT_PAIRED_COORDINATE_COMPARISON')
        if arrays['uv3z']!=arrays['ts3z'] or time_context['uv3z']!=time_context['ts3z']:raise ValueError('Native coordinate arrays and time context differ across original datasets')
        report.update(status='ALL8_COORDINATE_ARRAYS_EXACTLY_PAIRED',native_coordinate_pairing_established=True,time_context=time_context);stage('WORKER_COMPLETE');return report
    except Exception as error:
        report['status']='WORKER_FAILED_WITH_STAGE_RECEIPT';report.setdefault('failure_stage',dict(report['stage']) if report['stage'] else None);report['error_type']=type(error).__name__;save();raise


def probe(root=ROOT,out=OUT,runner=subprocess.run):
    op=operator(root);out=Path(out);out.mkdir(exist_ok=True);report={'schema':'osw.hycom-bounded-native-client-coordinate-probe.v1','operator_file':OPERATOR,'operator_sha256':digest((root/OPERATOR).read_bytes()),'input_sha256':op['input_sha256'],'status':'WORKER_STARTING','started_at_utc':stamp(),'worker_wall_timeout_seconds':120,'worker_attempts':1,'new_velocity_or_salinity_field_requests':0,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False};save=lambda:write_json(out/'probe-report.json',report);save();stdout=b'';stderr=b''
    command=[sys.executable,str(Path(__file__).resolve()),'--worker',str(out.resolve())]
    try:
        result=runner(command,capture_output=True,timeout=120,check=False);stdout=result.stdout or b'';stderr=result.stderr or b'';report['worker_return_code']=result.returncode;report['status']='WORKER_PROCESS_COMPLETE' if result.returncode==0 else 'WORKER_PROCESS_FAILED'
    except subprocess.TimeoutExpired as error:stdout=error.stdout or b'';stderr=error.stderr or b'';report['status']='NATIVE_CLIENT_WORKER_TIMED_OUT_WITH_STAGE_RECEIPT'
    for pending in out.glob('*.json.pending'):pending.unlink()
    worker_path=out/'worker-report.json'
    if worker_path.exists():
        worker_raw=worker_path.read_bytes();value=json.loads(worker_raw)
        if value['schema']!='osw.hycom-native-client-coordinate-worker.v1' or value['operator_file']!=OPERATOR or value['operator_sha256']!=report['operator_sha256'] or value['new_velocity_or_salinity_field_requests']!=0 or value['new_depth_references_admitted']!=0 or value['runtime_changed'] or value['full_goal_complete']:raise ValueError('Exact coordinate-only worker provenance required')
        report.update(worker_report={'file':'worker-report.json','bytes':len(worker_raw),'sha256':digest(worker_raw)},last_observed_stage=value.get('stage'),worker_status=value.get('status'),native_coordinate_pairing_established=value.get('native_coordinate_pairing_established',False))
    else:report.update(worker_report=None,last_observed_stage=None,native_coordinate_pairing_established=False)
    log={'schema':'osw.bounded-native-client-process-log.v1','stdout_prefix_base64':base64.b64encode(stdout[:250000]).decode(),'stderr_prefix_base64':base64.b64encode(stderr[:250000]).decode(),'stdout_truncated':len(stdout)>250000,'stderr_truncated':len(stderr)>250000};raw=encode(log);(out/'process-log.json').write_bytes(raw);report.update(process_log={'file':'process-log.json','bytes':len(raw),'sha256':digest(raw)},finished_at_utc=stamp());save()
    if sum(file.stat().st_size for file in out.glob('*.json'))>=2400000:raise ValueError('Fixed diagnostic source-batch cap exceeded')
    print(json.dumps(report),flush=True)


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':worker(out=Path(sys.argv[2]))
    elif len(sys.argv)==1:probe()
    else:raise ValueError('Only bounded parent or exact coordinate-only worker invocation supported')
