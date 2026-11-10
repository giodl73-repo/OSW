import json,subprocess,tempfile,types,unittest,urllib.request
from pathlib import Path
import probe_hycom_http_coordinates_v2 as p
from test_hycom_http_coordinates_v1 import Opener as OldOpener,Response,metadata,ascii_body


class Opener(OldOpener):
    def open(self,request,timeout):
        url=request.full_url;self.calls.append((url,timeout));product='uv3z' if '/uv3z/' in url else 'ts3z'
        if '.dds?' in url:return Response(metadata('response-1.json' if product=='uv3z' else 'response-7.json'))
        if url.endswith('.das'):return Response(metadata('response-2.json' if product=='uv3z' else 'response-8.json'))
        axis=next(axis for axis in p.frozen.frozen.SHAPES if p.frozen.coordinate_url(p.frozen.frozen.SOURCES[product],axis)==url);return Response(ascii_body(axis,self.arrays[axis]))


class ProjectedCoordinateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def out(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);return Path(tmp.name)
    def test_only_dds_structural_urls_projected(self):
        self.assertEqual(len(p.URLS),12)
        for url in p.frozen.frozen.SOURCES.values():self.assertIn(url+'.dds?depth,lat,lon,time',p.URLS);self.assertNotIn(url+'.dds',p.URLS);self.assertIn(url+'.das',p.URLS);self.assertNotIn(url+'.das?depth,lat,lon,time',p.URLS)
    def test_scoped_configuration_restores_all_original_globals(self):
        old=(p.frozen.OPERATOR,p.frozen.HTTP,p.frozen.URLS)
        with self.assertRaises(RuntimeError):
            with p.configured():self.assertEqual(p.frozen.OPERATOR,p.OPERATOR);self.assertIs(p.frozen.HTTP,p.ProjectedHTTP);raise RuntimeError('deliberate')
        self.assertEqual(old,(p.frozen.OPERATOR,p.frozen.HTTP,p.frozen.URLS))
    def test_http_rewrite_preserves_no_repeat_rule(self):
        opener=Opener()
        with p.configured():
            http=p.ProjectedHTTP(self.out(),opener);url=p.frozen.frozen.SOURCES['uv3z']+'.dds';http.get(url)
            with self.assertRaises(ValueError):http.get(url)
        self.assertEqual(opener.calls,[(url+'?depth,lat,lon,time',15)])
    def test_full_native_arrays_pair_and_both_precision_controls_match(self):
        opener=Opener();report=p.worker(out=self.out(),opener=opener);self.assertEqual(report['status'],'ALL8_COORDINATE_ARRAYS_EXACTLY_PAIRED');self.assertEqual(len(report['records']),8);self.assertEqual(len(report['retained_coordinate_controls']),2);self.assertEqual(len(opener.calls),12);self.assertEqual(report['dds_projection'],'depth,lat,lon,time');self.assertFalse(report['das_projection_applied']);self.assertTrue(all(url in p.URLS and timeout==15 for url,timeout in opener.calls))
    def test_parent_launches_v2_worker_with_unchanged_wall_deadline(self):
        out=self.out();seen=[]
        def runner(command,**kwargs):
            seen.append((command,kwargs));p.frozen.frozen.write_json(out/'worker-report.json',{'schema':'osw.hycom-native-client-coordinate-worker.v1','operator_file':p.OPERATOR,'operator_sha256':p.frozen.frozen.digest((p.ROOT/p.OPERATOR).read_bytes()),'status':'WORKER_STARTING','stage':{'operation':'DATASET_OPEN'},'native_coordinate_pairing_established':False,'new_velocity_or_salinity_field_requests':0,'new_depth_references_admitted':0,'runtime_changed':False,'full_goal_complete':False});raise subprocess.TimeoutExpired(command,120)
        p.probe(out=out,runner=runner);self.assertEqual(Path(seen[0][0][1]),Path(p.__file__).resolve());self.assertEqual(seen[0][1]['timeout'],120)
    def test_projection_cannot_drop_required_axis_or_claim_das_projection(self):
        for key,value in [('dds_projection','depth'),('das_projection_applied',True)]:
            op=dict(self.op);op[key]=value;root=self.out();(root/p.OPERATOR).parent.mkdir(parents=True);(root/p.OPERATOR).write_text(json.dumps(op))
            with self.assertRaises(ValueError):p.validate(root)
    def test_all_public_pins_and_no_field_scope_expansion(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.frozen.frozen.digest((p.ROOT/file).read_bytes()),pin,file)
        for url in p.URLS:self.assertNotIn('water_u',url);self.assertNotIn('water_v',url);self.assertNotIn('salinity',url)


if __name__=='__main__':unittest.main()
