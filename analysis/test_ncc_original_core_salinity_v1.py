import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from ncc_core_salinity_diagnostic_v1 import diagnose
from acquire_ncc_original_core_salinity_v1 import SalinityReads,preflight,load_targets,ROOT,OPERATOR


class FakeVariable:
    name='salinity';units='psu';standard_name='sea_water_salinity';dimensions=('time','depth','lat','lon')
    def __init__(self,errors=None,shape=(40,1,3)):self.errors=list(errors or []);self.shape=shape;self.calls=[]
    def __getitem__(self,key):
        self.calls.append(key)
        if self.errors:
            error=self.errors.pop(0)
            if error is not None:raise RuntimeError(error)
        return np.ma.array(np.full(self.shape,34.0))
    def ncattrs(self):return ['units','standard_name']
    def getncattr(self,k):return getattr(self,k)


class Axis:
    def __init__(self,values,units,positive=None):self.values=np.asarray(values,dtype=float);self.units=units;self.calendar='gregorian';self.positive=positive
    def __getitem__(self,key):return self.values[key]


def fixture():
    z=list(range(39))+[5000];columns=[{'global_longitude_index':i,'global_latitude_index':0,'native_source_longitude_degrees_east':float(i+3),'native_source_latitude_degrees_north':60.0} for i in range(3)]
    target={'section':{'depth_levels_m':z,'source_time_index':0,'columns':columns},'column':columns[1],'original_audit_record':{'selected_column_index':1,'snapshot_time_utc':'2022-03-15T00:00:00Z'}}
    class Dataset(dict):
        def ncattrs(self):return ['field_type']
        def getncattr(self,k):return 'instantaneous'
    ds=Dataset(depth=Axis(z,'m','down'),lat=Axis([60],'degrees_north'),lon=Axis([3,4,5],'degrees_east'),time=Axis([0],'hours since 2022-03-15 00:00:00'),salinity=FakeVariable())
    return ds,target


class CoreClassificationTests(unittest.TestCase):
    def test_salinity_lower_crossing_at_original_core(self):
        r=diagnose([0,10,20,30],[.3,.3,.3,.3],[34,34.5,35.5,36],0);self.assertEqual(r['status'],'conditional_fresh_component_core_supported');self.assertEqual(r['lower']['boundary_depth_m'],15);self.assertEqual(r['lower']['bracket_m'],[10,20]);self.assertEqual(r['lower']['limiting_criteria'],['salinity']);self.assertEqual(r['upper']['status'],'surface_sample_supported')
    def test_joint_exit_uses_first_failure_in_same_lower_bracket(self):
        r=diagnose([0,10],[.3,.05],[34,36],0);self.assertEqual(r['lower']['boundary_depth_m'],5);self.assertEqual(r['lower']['limiting_criteria'],['salinity']);self.assertAlmostEqual(r['lower']['candidate_crossings_m']['velocity'],8)
    def test_velocity_can_limit_before_salinity(self):
        r=diagnose([0,10],[.2,0],[34,35.5],0);self.assertEqual(r['lower']['boundary_depth_m'],5);self.assertEqual(r['lower']['limiting_criteria'],['velocity'])
    def test_equality_is_excluded_and_adjacent_crossing_is_retained(self):
        r=diagnose([0,10,20],[.2,.1,.3],[34,35,34],0);self.assertEqual(r['lower']['boundary_depth_m'],10);self.assertEqual(set(r['lower']['limiting_criteria']),{'velocity','salinity'});self.assertEqual(r['lower']['last_connected_native_index'],0)
    def test_missing_input_censors_without_known_other_crossing_substitution(self):
        for velocity,salinity,missing in [([.3,None],[34,36],['velocity']),([.3,.05],[34,None],['salinity'])]:
            r=diagnose([0,10],velocity,salinity,0);self.assertEqual(r['lower']['status'],'censored_before_missing_native_input');self.assertIsNone(r['lower']['boundary_depth_m']);self.assertEqual(r['lower']['missing_inputs'],missing);self.assertEqual(r['lower']['last_connected_depth_m'],0)
    def test_salty_original_core_is_not_reselected_to_fresh_surface(self):
        r=diagnose([0,10,20],[.2,.3,.4],[34,35,34],1);self.assertEqual(r['status'],'original_velocity_core_not_in_declared_fresh_class');self.assertFalse(r['core_reselected']);self.assertIsNone(r['lower'])
    def test_missing_or_weak_original_core_remains_unclassified(self):
        self.assertEqual(diagnose([0,10],[.3,.3],[None,34],0)['status'],'original_core_missing_input');self.assertEqual(diagnose([0,10],[.1,.3],[34,34],0)['status'],'original_core_not_above_original_velocity_threshold')
    def test_detached_upper_joint_boundary_uses_first_exit_from_core(self):
        r=diagnose([0,10,20],[0,.3,.3],[36,34,34],1);self.assertEqual(r['upper']['boundary_depth_m'],5);self.assertEqual(r['upper']['limiting_criteria'],['salinity']);self.assertEqual(r['upper']['bracket_m'],[0,10])
    def test_native_domain_end_is_censored_not_exact_bottom(self):
        r=diagnose([0,10,20],[.3,.3,.3],[34,34,34],0);self.assertEqual(r['lower']['status'],'censored_at_native_domain_end');self.assertEqual(r['lower']['last_connected_depth_m'],20);self.assertIsNone(r['lower']['boundary_depth_m']);self.assertFalse(r['physical_current_bottom_established']);self.assertIsNone(r['physical_layer_thickness_m']);self.assertFalse(r['volume_eligible'])
    def test_disconnected_deeper_fresh_patch_is_not_bridged(self):
        r=diagnose([0,10,20,30],[.3]*4,[34,36,34,34],0);self.assertEqual(r['lower']['boundary_depth_m'],5);self.assertEqual(r['lower']['last_connected_native_index'],0)
    def test_invalid_axis_values_and_threshold_retuning_rejected(self):
        for z,v,s,c in [([0,0],[.3,.3],[34,34],0),([0,10],[.3,.3],[34,float('nan')],0),([0,10],[.3,.3],[34,51],0),([0,10],[.3],[34,34],0),([0,10],[.3,.3],[34,34],2)]:
            with self.assertRaises(ValueError):diagnose(z,v,s,c)
        with self.assertRaises(ValueError):diagnose([0,10],[.3,.3],[34,34],0,salinity_threshold=35.1)


class SourceAndTransportTests(unittest.TestCase):
    def test_five_exact_retained_targets_no_reselection(self):
        op=json.loads((ROOT/OPERATOR).read_bytes());targets=load_targets(ROOT,op);self.assertEqual(len(targets),5);self.assertEqual([t['source_audit_pointer'] for t in targets],op['original_audit_pointers']);self.assertTrue(all(t['original_audit_record']['entity_id']=='current:norwegian-coastal' for t in targets))
    def test_metadata_preflight_exact_node_depth_and_timestamp(self):
        ds,target=fixture();plans,attrs,varattrs=preflight(ds,[target]);self.assertEqual(plans[0]['ix'],1);self.assertEqual(plans[0]['stamp'],'2022-03-15T00:00:00Z');self.assertEqual(ds['salinity'].calls,[])
    def test_metadata_axis_time_stencil_or_units_mismatch_before_any_field_read(self):
        for mode in ['depth','lat','lon','time','stencil','unit','standard']:
            ds,target=fixture()
            if mode=='depth':ds['depth'].values[1]=1.1
            elif mode=='lat':ds['lat'].values[0]=60.01
            elif mode=='lon':ds['lon'].values[1]=4.01
            elif mode=='time':ds['time'].values[0]=3
            elif mode=='stencil':target['section']['columns'][0]['global_longitude_index']=3
            elif mode=='unit':ds['salinity'].units='g/kg'
            else:ds['salinity'].standard_name='sea_water_absolute_salinity'
            with self.subTest(mode=mode),self.assertRaises(ValueError):preflight(ds,[target])
            self.assertEqual(ds['salinity'].calls,[])
    def test_retry_only_identical_io_failure_with_two_and_five_second_delays(self):
        with tempfile.TemporaryDirectory() as d:
            waits=[];reads=SalinityReads(Path(d)/'ledger.json',waits.append);var=FakeVariable(['NetCDF: I/O failure','NetCDF: I/O failure',None]);a=reads.read(var,7,8,9);self.assertEqual(a.shape,(40,3));self.assertEqual(waits,[2,5]);self.assertEqual(len(var.calls),3);self.assertTrue(all(c==var.calls[0] for c in var.calls));self.assertEqual(reads.requested,360);self.assertEqual(reads.returned,120);self.assertEqual(reads.retry_reserved,240)
    def test_successful_read_not_automatically_replayed(self):
        with tempfile.TemporaryDirectory() as d:
            reads=SalinityReads(Path(d)/'ledger.json',lambda _:self.fail('No wait on success'));var=FakeVariable();reads.read(var,0,0,1);self.assertEqual(len(var.calls),1);self.assertEqual(reads.requested,120);self.assertEqual(reads.retry_reserved,0)
    def test_non_transport_error_or_shape_change_is_not_retried(self):
        for var in [FakeVariable(['other runtime error']),FakeVariable(shape=(39,1,3))]:
            with tempfile.TemporaryDirectory() as d:
                reads=SalinityReads(Path(d)/'ledger.json',lambda _:self.fail('No wait'))
                with self.assertRaises((RuntimeError,ValueError)):reads.read(var,0,0,1)
                self.assertEqual(len(var.calls),1);self.assertEqual(reads.returned,0)
    def test_attempt_and_requested_value_caps_are_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            reads=SalinityReads(Path(d)/'ledger.json',lambda _:None);var=FakeVariable(['NetCDF: I/O failure']*4)
            with self.assertRaises(RuntimeError):reads.read(var,0,0,1)
            self.assertEqual(len(var.calls),3);reads.requested=1800
            with self.assertRaises(ValueError):reads.read(FakeVariable(),0,0,1)
    def test_frozen_operator_caps_pins_and_non_promotion(self):
        import hashlib
        op=json.loads((ROOT/OPERATOR).read_bytes());self.assertEqual(op['planned_salinity_scalar_values'],600);self.assertEqual(op['maximum_requested_salinity_scalar_values'],1800);self.assertEqual(op['maximum_native_depth_levels'],40);self.assertEqual(op['profiles_per_patch'],3);self.assertFalse(any(op['eligibility'].values()))
        for f,pin in op['input_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
