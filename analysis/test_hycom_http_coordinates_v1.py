import base64,copy,io,json,subprocess,tempfile,types,unittest
from datetime import datetime
from pathlib import Path
import probe_hycom_http_coordinates_v1 as p
from test_hycom_native_client_coordinate_probe_v1 import Variable as FixtureVariable


def metadata(name):
    return base64.b64decode(json.loads((p.ROOT/('research/source-data/hycom-ncc-mid-norway-metadata-probe-v1/'+name)).read_bytes())['retained_response_body_base64'])


def coordinate_fixture():
    arrays={axis:FixtureVariable(axis).values for axis in p.frozen.SHAPES}
    first=json.loads((p.ROOT/p.CONTROLS[0]).read_bytes());hours=(datetime.strptime(first['snapshot_time_utc'],'%Y-%m-%dT%H:%M:%SZ')-datetime(2000,1,1)).total_seconds()/3600;origin=hours-3*first['source_time_index'];arrays['time']=[origin+3*i for i in range(p.frozen.SHAPES['time'])]
    for file in p.CONTROLS:
        case=json.loads((p.ROOT/file).read_bytes());arrays['depth']=case['depth_levels_m'];arrays['lat'][case['native_latitude_index']]=case['native_latitude_degrees_north'];arrays['time'][case['source_time_index']]=(datetime.strptime(case['snapshot_time_utc'],'%Y-%m-%dT%H:%M:%SZ')-datetime(2000,1,1)).total_seconds()/3600
        for col in case['columns']:arrays['lon'][col['global_longitude_index']]=col['native_source_longitude_degrees_east']
    return arrays


def ascii_body(axis,values):return (f'Dataset {{\n    Float64 {axis}[{axis} = {len(values)}];\n}} sample;\n---------------------------------------------\n{axis}[{len(values)}]\n'+', '.join(map(repr,values))+'\n').encode()


class Response(io.BytesIO):status=200


class Opener:
    def __init__(self,transform=None):self.calls=[];self.transform=transform;self.arrays=coordinate_fixture()
    def open(self,request,timeout):
        url=request.full_url;self.calls.append((url,timeout));product='uv3z' if '/uv3z/' in url else 'ts3z'
        if url.endswith('.dds'):raw=metadata('response-1.json' if product=='uv3z' else 'response-7.json')
        elif url.endswith('.das'):raw=metadata('response-2.json' if product=='uv3z' else 'response-8.json')
        else:
            axis=next(a for a in p.frozen.SHAPES if p.coordinate_url(p.frozen.SOURCES[product],a)==url);raw=ascii_body(axis,self.arrays[axis])
        if self.transform:raw=self.transform(url,raw)
        return Response(raw)


class HTTPCoordinateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def out(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);return Path(tmp.name)
    def pending(self,out):p.frozen.write_json(out/'worker-report.json',{'schema':'osw.hycom-native-client-coordinate-worker.v1','operator_file':p.OPERATOR,'operator_sha256':p.frozen.digest((p.ROOT/p.OPERATOR).read_bytes()),'status':'WORKER_STARTING','stage':{'operation':'DATASET_OPEN'},'native_coordinate_pairing_established':False,'new_velocity_or_salinity_field_requests':0,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False})
    def test_actual_retained_dds_and_das_metadata_parsed(self):
        for dds,das in [('response-1.json','response-2.json'),('response-7.json','response-8.json')]:
            self.assertEqual(p.dds_shapes(metadata(dds)),{axis:(size,) for axis,size in p.frozen.SHAPES.items()});attrs=p.das_strings(metadata(das));self.assertEqual(attrs['NC_GLOBAL']['field_type'],'instantaneous');self.assertEqual(attrs['depth']['units'],'m');self.assertEqual(attrs['time']['calendar'],'gregorian')
    def test_float64_coordinate_tokens_preserve_exact_values(self):
        arrays=coordinate_fixture()
        for axis,values in arrays.items():self.assertEqual(p.ascii_values(ascii_body(axis,values),axis),[float(v) for v in values])
    def test_incomplete_wrong_type_nonfinite_or_extra_values_rejected(self):
        values=coordinate_fixture()['depth'];good=ascii_body('depth',values)
        for raw in [good.replace(b'Float64',b'Float32'),ascii_body('depth',values[:-1]),good.replace(b'0.0',b'NaN',1),good+b', 1',good.replace(b'depth[40]',b'depth[39]')]:
            with self.assertRaises(ValueError):p.ascii_values(raw,'depth')
        with self.assertRaises(ValueError):p.ascii_values(ascii_body('depth',[1e309]*40),'depth')
    def test_dds_html_wrong_shape_and_duplicate_declaration_rejected(self):
        good=metadata('response-1.json')
        for raw in [b'<html>unavailable</html>',good.replace(b'depth = 40',b'depth = 39',1),good.replace(b'    Float64 depth[depth = 40];',b'    Float64 depth[depth = 40];\n    Float64 depth[depth = 40];',1)]:
            with self.assertRaises(ValueError):p.dds_shapes(raw)
    def test_closed_http_urls_no_model_fields_or_repeat_requests(self):
        opener=Opener();http=p.HTTP(self.out(),opener);url=p.frozen.SOURCES['uv3z']+'.dds';http.get(url)
        for bad in [url,p.frozen.SOURCES['uv3z']+'.ascii?water_u',p.frozen.SOURCES['uv3z']+'.ascii?depth%5B0:1:0%5D','https://example.org/data']:
            with self.assertRaises(ValueError):http.get(bad)
        self.assertEqual(len(opener.calls),1)
    def test_http_timeout_has_durable_error_receipt_without_retry(self):
        def fail(url,raw):raise TimeoutError('simulated')
        out=self.out();opener=Opener(fail);http=p.HTTP(out,opener)
        with self.assertRaises(ValueError):http.get(p.frozen.SOURCES['uv3z']+'.dds')
        report=json.loads((out/'http-ledger.json').read_bytes());self.assertEqual(len(opener.calls),1);self.assertEqual(report['requests'][0]['error_type'],'TimeoutError');self.assertEqual(report['requests'][0]['status'],'HTTP_REQUEST_FAILED_OR_OVERSIZE')
    def test_oversize_body_retained_only_as_explicit_prefix(self):
        out=self.out();http=p.HTTP(out,Opener(lambda url,raw:b'x'*20001))
        with self.assertRaises(ValueError):http.get(p.frozen.SOURCES['uv3z']+'.dds')
        value=json.loads((out/'http-response-1.json').read_bytes());self.assertTrue(value['response_body_truncated']);self.assertEqual(value['retained_response_body_bytes'],20000)
    def test_no_redirects(self):
        with self.assertRaises(ValueError):p.NoRedirects().redirect_request(None,None,302,'',{},p.frozen.SOURCES['uv3z']+'.dds')
    def test_dataset_model_variables_and_partial_slices_rejected(self):
        opener=Opener();ds=p.Dataset(p.frozen.SOURCES['uv3z'],p.HTTP(self.out(),opener))
        for field in ['water_u','water_v','salinity']:
            with self.assertRaises(ValueError):ds[field]
        with self.assertRaises(ValueError):ds['depth'][0:1]
        self.assertEqual(len(opener.calls),2)
    def test_proxy_coordinate_attributes_and_source_metadata_exact(self):
        ds=p.Dataset(p.frozen.SOURCES['uv3z'],p.HTTP(self.out(),Opener()));self.assertEqual(ds['depth'].shape,(40,));self.assertEqual(ds['lat'].dimensions,('lat',));self.assertEqual(ds['depth'].positive,'down');self.assertEqual(ds.getncattr('field_type'),'instantaneous')
        with self.assertRaises(AttributeError):getattr(ds['lat'],'missing_attribute')
    def test_all_eight_axes_and_old_precision_controls_match(self):
        out=self.out();opener=Opener();report=p.worker(out=out,opener=opener);self.assertTrue(report['native_coordinate_pairing_established']);self.assertEqual(len(report['records']),8);self.assertEqual(len(report['retained_coordinate_controls']),2);self.assertEqual(len(opener.calls),12);self.assertTrue(all(timeout==15 for _,timeout in opener.calls));self.assertEqual(report['coordinate_transport_backend'],'bounded_HTTP_ASCII_Float64');self.assertEqual(report['new_velocity_or_salinity_field_requests'],0)
        ledger=json.loads((out/'http-ledger.json').read_bytes())
        for row in ledger['requests']:
            piece=row['response'];raw=(out/piece['file']).read_bytes();self.assertEqual(p.frozen.digest(raw),piece['sha256']);value=json.loads(raw);body=base64.b64decode(value['retained_response_body_base64']);self.assertEqual(value['retained_response_body_sha256'],p.frozen.digest(body));self.assertFalse(value['wire_hash_claimed'])
        self.assertLess(sum(file.stat().st_size for file in out.glob('*.json')),2400000)
    def test_matching_new_arrays_cannot_override_old_precision_control(self):
        opener=Opener();case=json.loads((p.ROOT/p.CONTROLS[0]).read_bytes());index=case['columns'][0]['global_longitude_index'];opener.arrays['lon'][index]+=1e-12;out=self.out()
        with self.assertRaises(ValueError):p.worker(out=out,opener=opener)
        report=json.loads((out/'worker-report.json').read_bytes());self.assertEqual(report['status'],'HTTP_COORDINATE_CONTROLS_FAILED');self.assertEqual(report['failure_stage']['operation'],'RETAINED_COORDINATE_CONTROLS')
    def test_scoped_original_operator_restored_after_error(self):
        old=p.frozen.OPERATOR
        with self.assertRaises(RuntimeError):
            with p.configured():self.assertEqual(p.frozen.OPERATOR,p.OPERATOR);raise RuntimeError('deliberate')
        self.assertEqual(p.frozen.OPERATOR,old)
    def test_parent_launches_http_worker_instead_of_native_c_script(self):
        out=self.out();seen=[]
        def runner(command,**kwargs):seen.append(command);self.pending(out);return types.SimpleNamespace(returncode=1,stdout=b'',stderr=b'')
        p.probe(out=out,runner=runner);self.assertEqual(Path(seen[0][1]),Path(p.__file__).resolve());self.assertNotEqual(Path(seen[0][1]),Path(p.frozen.__file__).resolve())
    def test_parent_preserves_same_wall_deadline_and_pending_stage(self):
        out=self.out();seen=[]
        def runner(command,**kwargs):seen.append(kwargs['timeout']);self.pending(out);raise subprocess.TimeoutExpired(command,120)
        p.probe(out=out,runner=runner);report=json.loads((out/'probe-report.json').read_bytes());self.assertEqual(seen,[120]);self.assertEqual(report['status'],'NATIVE_CLIENT_WORKER_TIMED_OUT_WITH_STAGE_RECEIPT')
    def test_das_missing_required_metadata_not_invented(self):
        good=metadata('response-2.json')
        with self.assertRaises(ValueError):p.das_strings(good.replace(b'    NC_GLOBAL {',b'    WRONG_GLOBAL {'))
        self.assertNotIn('units',p.das_strings(good.replace(b'String units "m";',b''))['depth'])
    def test_public_pins_and_full_source_still_fixed(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.frozen.digest((p.ROOT/file).read_bytes()),pin,file)
        self.assertEqual(self.op['coordinate_shapes'],p.frozen.SHAPES);self.assertEqual(self.op['worker_wall_timeout_seconds'],120);self.assertEqual(len(p.URLS),12)


if __name__=='__main__':unittest.main()
