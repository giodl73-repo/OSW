import copy,json,tempfile,unittest
from pathlib import Path
import netCDF4
import numpy as np
import acquire_ncc_north_joint_sections_v1 as p


class Variable:
    def __init__(self,name,data=None,failures=()):
        self.name=name;self.data=data;self.failures=list(failures);self.calls=[]
        self.units,self.standard_name=p.FIELDS.get(name,('',''));self.dimensions=('time','depth','lat','lon')
    def __getitem__(self,key):
        self.calls.append(key)
        if self.failures:
            error=self.failures.pop(0)
            if error:raise error
        if self.data is not None:return self.data[key]
        _,_,lat,lon=key;n=lon.stop-lon.start;a=np.full((40,1,n),34.,dtype=float)
        if self.name!='salinity':
            a[:]=0 if self.name=='water_u' else .15
            if self.name=='water_v':
                if lon.start<=35<lon.stop:a[:,:,35-lon.start]=.3
                a[24:,:,:]=0
        else:a[24:,:,:]=35.5
        return a
    def ncattrs(self):return ['units','standard_name']
    def getncattr(self,k):return getattr(self,k)


class Dataset:
    def __init__(self):
        self.variables={n:Variable(n) for n in p.FIELDS}
        for name,data,unit in [('depth',[0]+list(range(5,195,5))+[5000],'m'),('lat',[61.48,61.52,62.24,62.28],'degrees_north'),('lon',np.arange(3,8.6,.08),'degrees_east')]:
            self.variables[name]=Variable(name,np.asarray(data,dtype=float));self.variables[name].units=unit
        self.variables['depth'].positive='down';t=Variable('time',np.asarray([netCDF4.date2num(__import__('datetime').datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ'),'hours since 2022-01-01') for s in p.STAMPS]));t.units='hours since 2022-01-01';self.variables['time']=t;self.closed=False
    def __getitem__(self,k):return self.variables[k]
    def ncattrs(self):return ['field_type']
    def getncattr(self,k):return 'instantaneous'
    def __enter__(self):return self
    def __exit__(self,*args):self.closed=True


class JointTransportTests(unittest.TestCase):
    def make(self,planned=120):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);sleep=[];return p.JointReads(planned,Path(tmp.name)/'ledger.json',sleep.append),sleep
    def test_all_three_fields_share_one_reservation(self):
        r,s=self.make()
        for name in p.FIELDS:r.read(Variable(name),0,0,0,2)
        self.assertEqual(r.returned,360);self.assertEqual(r.receipt()['joint_reserved_native_cell_units'],240);self.assertEqual(r.receipt()['conservative_joint_decoded_bytes'],2880);self.assertEqual(len(r.successes),3)
    def test_literal_io_failure_retries_identical_patch(self):
        r,s=self.make();v=Variable('water_v',failures=[RuntimeError('NetCDF: I/O failure'),None]);r.read(v,1,2,3,5)
        self.assertEqual(v.calls[0],v.calls[1]);self.assertEqual(s,[2]);self.assertEqual(r.extra,120);self.assertEqual(r.actual,240);self.assertEqual(r.returned,120)
    def test_three_attempt_limit_and_two_delays(self):
        r,s=self.make();v=Variable('salinity',failures=[RuntimeError('NetCDF: I/O failure')]*3)
        with self.assertRaises(RuntimeError):r.read(v,0,0,0,2)
        self.assertEqual(len(v.calls),3);self.assertEqual(s,[2,5]);self.assertEqual(r.extra,240)
    def test_nontransport_failure_never_retried(self):
        r,s=self.make();v=Variable('water_u',failures=[RuntimeError('permission denied')])
        with self.assertRaises(RuntimeError):r.read(v,0,0,0,2)
        self.assertEqual(len(v.calls),1);self.assertEqual(s,[])
    def test_retry_preserves_all_future_first_reads(self):
        r,s=self.make(124000);v=Variable('water_v',failures=[RuntimeError('NetCDF: I/O failure')])
        with self.assertRaises(ValueError):r.read(v,0,0,0,149)
        self.assertEqual(len(v.calls),1);self.assertEqual(r.extra,0)
    def test_success_never_replayed(self):
        r,s=self.make();v=Variable('water_u');r.read(v,0,0,0,2)
        with self.assertRaises(ValueError):r.read(v,0,0,0,2)
        self.assertEqual(len(v.calls),1)
    def test_invalid_patch_and_field_never_requested(self):
        for name,args in [('temperature',(0,0,0,2)),('salinity',(0,0,0,150)),('water_u',(0,0,1,2)),('water_v',(-1,0,0,2))]:
            r,s=self.make();v=Variable(name)
            with self.assertRaises(ValueError):r.read(v,*args)
            self.assertEqual(v.calls,[])
    def test_no_unreserved_extra_field_reads(self):
        r,s=self.make()
        for name in p.FIELDS:r.read(Variable(name),0,0,0,2)
        v=Variable('salinity')
        with self.assertRaises(ValueError):r.read(v,1,0,0,2)
        self.assertEqual(v.calls,[])
    def test_initial_caps_cannot_expand(self):
        for planned in [True,0,-1,125001]:
            with tempfile.TemporaryDirectory() as d,self.assertRaises(ValueError):p.JointReads(planned,Path(d)/'ledger')
    def test_shape_scaling_errors_not_retried(self):
        for name,data in [('salinity',np.full((1,39,1,3),34.)),('salinity',np.full((1,40,1,3),51.)),('water_v',np.full((1,40,1,3),11.))]:
            r,s=self.make();v=Variable(name,data)
            with self.assertRaises(ValueError):r.read(v,0,0,0,2)
            self.assertEqual(len(v.calls),1);self.assertEqual(r.returned,0);self.assertEqual(s,[])
    def test_ledger_keeps_explicit_missing_without_wire_claim(self):
        r,s=self.make();v=Variable('salinity',np.ma.array(np.full((1,40,1,3),34.),mask=True));a=r.read(v,0,0,0,2)
        self.assertTrue(np.isnan(a).all());receipt=json.loads(r.path.read_bytes());self.assertEqual(receipt,r.receipt());self.assertFalse(receipt['wire_hash_claimed'])


class PreflightAndSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
    def test_complete_paired_metadata_before_any_field_reads(self):
        uv,ts=Dataset(),Dataset();axes,plans,n,times=p.preflight(uv,ts,self.op);self.assertEqual(len(plans),2);self.assertEqual(len(times),4);self.assertEqual(len(axes['depth']),40);self.assertEqual(n,40*4*sum(len(a['longitude_indices']) for a in plans));self.assertTrue(all(not ds[name].calls for ds in [uv,ts] for name in p.FIELDS))
    def test_mismatched_axes_rejected_before_fields(self):
        for name in ['depth','lat','lon']:
            uv,ts=Dataset(),Dataset();ts[name].data[1]+=.01
            with self.subTest(name=name),self.assertRaises(ValueError):p.preflight(uv,ts,self.op)
            self.assertEqual(uv['water_v'].calls,[])
    def test_missing_or_duplicate_exact_dates_rejected(self):
        for mode in ['shift','duplicate']:
            uv,ts=Dataset(),Dataset();ts['time'].data[0]+=1 if mode=='shift' else 0
            if mode=='duplicate':ts['time'].data=np.append(ts['time'].data,ts['time'].data[0])
            with self.assertRaises(ValueError):p.preflight(uv,ts,self.op)
    def test_mismatched_time_indices_rejected(self):
        uv,ts=Dataset(),Dataset();ts['time'].data=ts['time'].data[::-1]
        with self.assertRaises(ValueError):p.preflight(uv,ts,self.op)
    def test_field_and_coordinate_units_and_frame_required(self):
        for field,attr,value in [('depth','positive','up'),('lat','units','radians'),('water_v','standard_name','wrong'),('salinity','units','g/kg')]:
            uv,ts=Dataset(),Dataset();setattr((ts if field=='salinity' else uv)[field],attr,value)
            with self.subTest(field=field),self.assertRaises(ValueError):p.preflight(uv,ts,self.op)
    def test_declared_gates_rules_and_caps_cannot_change(self):
        for key,value in [('sections',[]),('primary_threshold_m_s',.05),('practical_salinity_exclusive_upper_threshold',34),('component_bearing_degrees_true',45),('selection_depth_interval_m',[0,200]),('maximum_total_cell_pairs',300000),('maximum_nearest_latitude_distance_km',10)]:
            op=copy.deepcopy(self.op);op[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):p.validate_operator(op)
    def test_unsupported_axis_is_not_replaced_by_fresh_neighbor(self):
        diagnosis={'horizontal_selection_status':'section_gate_edge_maximum_axis_unresolved','selected_column_index':0}
        r=p.classify([0,100],[{'signed_reference_component_m_s':[.5,.4]}],[[33,33]],diagnosis);self.assertEqual(r['status'],'original_horizontal_axis_unresolved');self.assertFalse(r['core_reselected'])
    def test_salty_original_core_is_not_reselected(self):
        diagnosis={'horizontal_selection_status':p.INTERIOR,'selected_column_index':0,'selected_column_threshold_layers':[{}, {'core_index':0}]};r=p.classify([0,100],[{'signed_reference_component_m_s':[.5,.4]}],[[35,33]],diagnosis);self.assertEqual(r['status'],'original_velocity_core_not_in_declared_fresh_class');self.assertFalse(r['core_reselected'])
    def test_joint_boundary_and_censoring_reuse_frozen_method(self):
        d={'horizontal_selection_status':p.INTERIOR,'selected_column_index':0,'selected_column_threshold_layers':[{}, {'core_index':0}]};r=p.classify([0,100],[{'signed_reference_component_m_s':[.5,.4]}],[[34,36]],d);self.assertEqual(r['lower']['boundary_depth_m'],50)
        r=p.classify([0,100],[{'signed_reference_component_m_s':[.5,None]}],[[34,None]],d);self.assertIsNone(r['lower']['boundary_depth_m']);self.assertEqual(r['lower']['status'],'censored_before_missing_native_input')
    def test_all_eight_sections_end_to_end_with_synthetic_fields(self):
        uv,ts=Dataset(),Dataset()
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);p.collect(out=out,factory=lambda url:uv if url==p.UV else ts);report=json.loads((out/'source-report.json').read_bytes());self.assertEqual(len(report['profiles']),8);self.assertEqual(report['transport']['successful_returned_scalar_values'],3*report['transport']['planned_velocity_cell_pairs']);self.assertEqual(len(report['transport']['requests']),24);self.assertTrue(report['all_targets_preflighted_before_fields']);self.assertEqual(report['new_reference_inventory_rows_admitted'],0);self.assertTrue(uv.closed and ts.closed)
            for piece in report['profiles']:
                raw=(out/piece['file']).read_bytes();self.assertEqual(p.digest(raw),piece['sha256']);section=json.loads(raw);self.assertEqual(section['fresh_component_classification']['status'],'conditional_fresh_component_core_supported');self.assertFalse(section['core_reselected_after_salinity']);self.assertIsNone(section['physical_thickness_m']);self.assertFalse(section['wire_hash_claimed'])
    def test_frozen_public_dependency_pins(self):
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(p.digest((p.ROOT/file).read_bytes()),pin,file)


if __name__=='__main__':unittest.main()
