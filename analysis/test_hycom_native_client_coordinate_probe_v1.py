import base64,copy,json,subprocess,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import probe_hycom_native_client_coordinates_v1 as p


class Values:
    def __init__(self,values):self.values=values
    def tolist(self):return list(self.values)


class Variable:
    def __init__(self,name):
        self.name=name;self.shape=(p.SHAPES[name],);self.dimensions=(name,);self.units=p.UNITS.get(name,'hours since 2022-01-01');self.positive='down';self.calls=[];self.hook=None
        if name=='depth':self.values=[0]+list(range(5,195,5))+[5000]
        elif name=='lat':self.values=[-80+i*.04 for i in range(self.shape[0])]
        elif name=='lon':self.values=[i*.08 for i in range(self.shape[0])]
        else:self.values=[i*3 for i in range(self.shape[0])]
    def __getitem__(self,key):
        self.calls.append(key)
        if self.hook:self.hook()
        return Values(self.values)


class Dataset:
    def __init__(self):self.variables={axis:Variable(axis) for axis in p.SHAPES};self.closed=False;self.field_type='instantaneous'
    def __getitem__(self,name):
        if name not in p.SHAPES:raise AssertionError('Model field access prohibited')
        return self.variables[name]
    def ncattrs(self):return ['field_type']
    def getncattr(self,k):return getattr(self,k)
    def close(self):self.closed=True


class NativeClientProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def make(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);return Path(tmp.name)
    def factory(self,uv,ts):return lambda url:uv if url==p.SOURCES['uv3z'] else ts
    def pending(self,out):
        record={'schema':'osw.hycom-native-client-coordinate-worker.v1','operator_file':p.OPERATOR,'operator_sha256':p.digest((p.ROOT/p.OPERATOR).read_bytes()),'status':'WORKER_STARTING','stage':{'operation':'DATASET_OPEN','dataset':'uv3z','axis':None},'native_coordinate_pairing_established':False,'new_velocity_or_salinity_field_requests':0,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False};p.write_json(out/'worker-report.json',record)
    def test_all_eight_arrays_pair_and_reservation_is_complete(self):
        uv,ts=Dataset(),Dataset();out=self.make();report=p.worker(out=out,factory=self.factory(uv,ts));self.assertEqual(report['status'],'ALL8_COORDINATE_ARRAYS_EXACTLY_PAIRED');self.assertEqual(len(report['records']),8);self.assertEqual(report['actual_requested_native_coordinate_scalars'],2*sum(p.SHAPES.values()));self.assertEqual(report['returned_native_coordinate_scalars'],report['planned_native_coordinate_scalars']);self.assertTrue(report['native_coordinate_pairing_established']);self.assertTrue(uv.closed and ts.closed)
    def test_coordinate_pieces_have_exact_hashes_sizes_and_values(self):
        uv,ts=Dataset(),Dataset();out=self.make();report=p.worker(out=out,factory=self.factory(uv,ts))
        for row in report['records']:
            piece=row['piece'];raw=(out/piece['file']).read_bytes();self.assertEqual(len(raw),piece['bytes']);self.assertEqual(p.digest(raw),piece['sha256']);value=json.loads(raw);self.assertEqual(value['values'],(uv if row['dataset']=='uv3z' else ts)[row['axis']].values);self.assertTrue(value['coordinate_metadata_not_current_depth_measurement']);self.assertFalse(value['wire_hash_claimed'])
    def test_model_field_reads_rejected_before_dataset_access(self):
        for name in ['water_u','water_v','salinity','tau']:
            with self.assertRaises(ValueError):p.coordinate_variable(Dataset(),name)
    def test_import_stage_persisted_before_native_library_import(self):
        out=self.make();uv,ts=Dataset(),Dataset()
        def load(name):
            self.assertEqual(name,'netCDF4');self.assertEqual(json.loads((out/'worker-report.json').read_bytes())['stage']['operation'],'IMPORT_NETCDF4');return types.SimpleNamespace(Dataset=self.factory(uv,ts),__version__='test',__netcdf4libversion__='test',__hdf5libversion__='test')
        with patch.object(p.importlib,'import_module',load):p.worker(out=out)
    def test_open_stage_persisted_before_each_dataset_open(self):
        out=self.make();uv,ts=Dataset(),Dataset();seen=[]
        def factory(url):seen.append(json.loads((out/'worker-report.json').read_bytes())['stage']['operation']);return uv if url==p.SOURCES['uv3z'] else ts
        p.worker(out=out,factory=factory);self.assertEqual(seen,['DATASET_OPEN','DATASET_OPEN'])
    def test_read_stage_and_request_reservation_persisted_before_reads(self):
        out=self.make();uv,ts=Dataset(),Dataset();seen=[]
        def hook():
            value=json.loads((out/'worker-report.json').read_bytes());seen.append(value['stage']['operation']);self.assertGreater(value['actual_requested_native_coordinate_scalars'],value['returned_native_coordinate_scalars'])
        for ds in [uv,ts]:
            for var in ds.variables.values():var.hook=hook
        p.worker(out=out,factory=self.factory(uv,ts));self.assertEqual(seen,['COORDINATE_READ']*8)
    def test_unexpected_shape_denied_before_coordinate_read(self):
        uv,ts=Dataset(),Dataset();uv['depth'].shape=(39,);out=self.make()
        with self.assertRaises(ValueError):p.worker(out=out,factory=self.factory(uv,ts))
        self.assertEqual(uv['depth'].calls,[]);self.assertEqual(json.loads((out/'worker-report.json').read_bytes())['failure_stage']['operation'],'COORDINATE_DESCRIPTOR')
    def test_nonfinite_missing_and_nonmonotonic_coordinates_rejected(self):
        for value in [None,float('nan'),-999]:
            uv,ts=Dataset(),Dataset();uv['lat'].values[10]=value;out=self.make()
            with self.subTest(value=value),self.assertRaises(ValueError):p.worker(out=out,factory=self.factory(uv,ts))
            report=json.loads((out/'worker-report.json').read_bytes());self.assertEqual(report['failure_stage']['axis'],'lat');self.assertEqual(report['failure_stage']['operation'],'COORDINATE_READ')
    def test_unit_and_source_metadata_required(self):
        for mode in ['unit','source']:
            uv,ts=Dataset(),Dataset()
            if mode=='unit':uv['lat'].units='radians'
            else:uv.field_type='monthly_mean'
            with self.subTest(mode=mode),self.assertRaises(ValueError):p.worker(out=self.make(),factory=self.factory(uv,ts))
    def test_both_source_axes_must_match_exactly(self):
        uv,ts=Dataset(),Dataset();ts['lon'].values[2]+=.001;out=self.make()
        with self.assertRaises(ValueError):p.worker(out=out,factory=self.factory(uv,ts))
        report=json.loads((out/'worker-report.json').read_bytes());self.assertEqual(report['failure_stage']['operation'],'EXACT_PAIRED_COORDINATE_COMPARISON');self.assertFalse(report['native_coordinate_pairing_established'])
    def test_parent_wall_timeout_retains_last_stage_and_no_retry(self):
        out=self.make();calls=[]
        def runner(command,**kwargs):calls.append(kwargs);self.pending(out);raise subprocess.TimeoutExpired(command,120,output=b'partial',stderr=b'')
        p.probe(out=out,runner=runner);report=json.loads((out/'probe-report.json').read_bytes());self.assertEqual(len(calls),1);self.assertEqual(calls[0]['timeout'],120);self.assertEqual(report['status'],'NATIVE_CLIENT_WORKER_TIMED_OUT_WITH_STAGE_RECEIPT');self.assertEqual(report['last_observed_stage']['operation'],'DATASET_OPEN');self.assertEqual(report['new_velocity_or_salinity_field_requests'],0)
    def test_parent_success_retains_worker_provenance(self):
        out=self.make();uv,ts=Dataset(),Dataset()
        def runner(command,**kwargs):p.worker(out=out,factory=self.factory(uv,ts));return types.SimpleNamespace(returncode=0,stdout=b'completed',stderr=b'')
        p.probe(out=out,runner=runner);report=json.loads((out/'probe-report.json').read_bytes());self.assertEqual(report['status'],'WORKER_PROCESS_COMPLETE');self.assertTrue(report['native_coordinate_pairing_established']);self.assertEqual(report['worker_report']['sha256'],p.digest((out/'worker-report.json').read_bytes()));self.assertEqual(list(out.glob('*.pending')),[])
    def test_parent_failed_worker_and_log_prefix_bounds(self):
        out=self.make()
        def runner(command,**kwargs):self.pending(out);return types.SimpleNamespace(returncode=1,stdout=b'x'*250001,stderr=b'failed')
        p.probe(out=out,runner=runner);report=json.loads((out/'probe-report.json').read_bytes());self.assertEqual(report['status'],'WORKER_PROCESS_FAILED');log=json.loads((out/'process-log.json').read_bytes());self.assertTrue(log['stdout_truncated']);self.assertEqual(len(base64.b64decode(log['stdout_prefix_base64'])),250000)
    def test_declared_wall_and_native_decoded_bounds_cannot_change(self):
        for key,value in [('worker_wall_timeout_seconds',600),('maximum_native_coordinate_scalars',300000),('maximum_conservative_decoded_bytes',9000000),('new_velocity_or_salinity_field_requests',1),('sources',{}),('coordinate_shapes',{})]:
            op=copy.deepcopy(self.op);op[key]=value;root=self.make();(root/p.OPERATOR).parent.mkdir(parents=True);p.write_json(root/p.OPERATOR,op)
            with self.subTest(key=key),self.assertRaises(ValueError):p.operator(root)
    def test_all_public_input_pins_and_fixed_publication_caps(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.digest((p.ROOT/file).read_bytes()),pin,file)
        out=self.make();p.worker(out=out,factory=self.factory(Dataset(),Dataset()));self.assertLess(sum(f.stat().st_size for f in out.glob('*.json')),2400000)


if __name__=='__main__':unittest.main()
