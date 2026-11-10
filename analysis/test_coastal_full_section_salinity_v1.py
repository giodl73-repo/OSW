import copy,json,tempfile,unittest
from datetime import datetime
from pathlib import Path
import netCDF4
import numpy as np
import coastal_full_section_salinity_v1 as p
from ncc_core_salinity_diagnostic_v1 import diagnose as ncc
from egcc_core_salinity_diagnostic_v1 import diagnose as egcc


class Axis:
    def __init__(self,values,units,positive=None):self.values=np.asarray(values,dtype=float);self.units=units;self.positive=positive;self.calendar='gregorian'
    def __getitem__(self,key):return self.values[key]


class Variable:
    name='salinity';units='psu';standard_name='sea_water_salinity';dimensions=('time','depth','lat','lon')
    def __init__(self,controls=None,errors=None,fail_key=None,shape=None):self.controls=controls or [];self.errors=list(errors or []);self.fail_key=fail_key;self.shape=shape;self.calls=[]
    def ncattrs(self):return ['units','standard_name']
    def getncattr(self,key):return getattr(self,key)
    def __getitem__(self,key):
        self.calls.append(key);it=key[0];iy=key[2].start;x0=key[3].start;x1=key[3].stop-1;n=x1-x0+1
        if (it,iy,x0,x1)==self.fail_key:raise RuntimeError('synthetic source error not retried')
        if self.errors:
            error=self.errors.pop(0)
            if error is not None:raise RuntimeError(error)
        a=np.full(self.shape or (40,1,n),33.0)
        if not self.shape:
            for control in self.controls:
                cx0,cx1=control['native_longitude_indices_inclusive']
                if it==control['source_time_index'] and iy==control['native_latitude_index'] and x0<=cx0 and cx1<=x1:
                    for j,column in enumerate(control['practical_salinity_columns']):a[:,0,cx0-x0+j]=[np.nan if v is None else v for v in column]
        return np.ma.masked_invalid(a)


class Dataset(dict):
    def ncattrs(self):return ['field_type']
    def getncattr(self,key):return 'instantaneous'
    def close(self):pass


def section(entity='current:east-greenland-coastal',status=p.INTERIOR):
    return {'entity_id':entity,'depth_levels_m':[0,10,20],'columns':[{'signed_reference_component_m_s':[.3,.3,.3]}]*3,'diagnosis':{'horizontal_selection_status':status,'selected_column_index':1,'selected_column_threshold_layers':[{}, {'core_index':0}]}}


def fixture():
    z=list(range(39))+[5000];cols=[{'global_longitude_index':j,'global_latitude_index':0,'native_source_longitude_degrees_east':float(j+3),'native_source_latitude_degrees_north':60.0} for j in range(3)]
    target={'section':{'columns':cols,'retrieved_hyperslab':{'latitude_index':0,'longitude_indices_inclusive':[0,2],'time_index':0,'depth_indices_inclusive':[0,39]},'source_time_index':0,'snapshot_time_utc':'2022-03-15T00:00:00Z','depth_levels_m':z}}
    ds=Dataset(depth=Axis(z,'m','down'),lat=Axis([60],'degrees_north'),lon=Axis([3,4,5],'degrees_east'),time=Axis([0],'hours since 2022-03-15 00:00:00'),salinity=Variable())
    return ds,target


def full_fake(targets,controls,fail_key=None):
    lat={};lon={};hours={};units='hours since 2022-01-01 00:00:00'
    for t in targets:
        s=t['section'];hours[s['source_time_index']]=float(netCDF4.date2num(datetime.strptime(s['snapshot_time_utc'],'%Y-%m-%dT%H:%M:%SZ'),units))
        for c in s['columns']:lat[c['global_latitude_index']]=c['native_source_latitude_degrees_north'];lon[c['global_longitude_index']]=c['native_source_longitude_degrees_east']
    def axis(known,lower,upper):
        known={**known,0:lower,max(known)+1:upper};indices=sorted(known);return np.interp(np.arange(indices[-1]+1),indices,[known[i] for i in indices])
    return Dataset(depth=Axis(targets[0]['section']['depth_levels_m'],'m','down'),lat=Axis(axis(lat,-90,90),'degrees_north'),lon=Axis(axis(lon,0,360),'degrees_east'),time=Axis(axis(hours,0,max(hours.values())+1),units),salinity=Variable(controls,fail_key=fail_key))


class DiagnosticTests(unittest.TestCase):
    def test_distinct_source_specific_salinity_thresholds(self):
        z=[0,10];v=[.3,.3];salt=[34.5,34.5];self.assertEqual(ncc(z,v,salt,0)['status'],'conditional_fresh_component_core_supported');self.assertEqual(egcc(z,v,salt,0)['status'],'original_velocity_core_not_in_declared_fresh_class')
    def test_egcc_finite_adjacent_salinity_exit(self):
        r=egcc([0,10],[.3,.3],[33.5,34.5],0);self.assertEqual(r['lower']['boundary_depth_m'],5);self.assertEqual(r['lower']['limiting_criteria'],['salinity']);self.assertFalse(r['physical_current_bottom_established']);self.assertIsNone(r['physical_layer_thickness_m'])
    def test_egcc_joint_velocity_exit_and_equality(self):
        r=egcc([0,10],[.2,0],[33.5,34.1],0);self.assertEqual(r['lower']['boundary_depth_m'],5);self.assertEqual(r['lower']['limiting_criteria'],['velocity']);self.assertEqual(egcc([0,10],[.3,.3],[33,34],0)['lower']['boundary_depth_m'],10)
    def test_missing_next_input_censors_instead_of_using_other_known_exit(self):
        r=egcc([0,10],[.3,None],[33,35],0);self.assertEqual(r['lower']['status'],'censored_before_missing_native_input');self.assertIsNone(r['lower']['boundary_depth_m'])
    def test_salty_core_no_reselection_or_disconnected_patch_bridge(self):
        self.assertEqual(egcc([0,10,20],[.3]*3,[33,34.5,33],1)['status'],'original_velocity_core_not_in_declared_fresh_class');r=egcc([0,10,20],[.3]*3,[33,35,33],0);self.assertEqual(r['lower']['last_connected_native_index'],0)
    def test_detached_upper_boundary_and_native_domain_censoring(self):
        r=egcc([0,10,20],[0,.3,.3],[34.5,33.5,33.5],1);self.assertEqual(r['upper']['boundary_depth_m'],5);self.assertEqual(r['lower']['status'],'censored_at_native_domain_end');self.assertFalse(r['volume_eligible'])
    def test_original_unresolved_axis_is_not_replaced(self):
        s=section(status='section_gate_edge_maximum_axis_unresolved');r=p.classify(s,[[33]*3]*3);self.assertEqual(r['status'],'original_horizontal_axis_unresolved');self.assertEqual(r['original_selected_column_index'],1);self.assertFalse(r['core_reselected'])
    def test_classifier_dispatch_and_undeclared_owner_rejection(self):
        salt=[[34.5]*3]*3;self.assertEqual(p.classify(section('current:norwegian-coastal'),salt)['status'],'conditional_fresh_component_core_supported');self.assertEqual(p.classify(section(),salt)['status'],'original_velocity_core_not_in_declared_fresh_class')
        with self.assertRaises(ValueError):p.classify(section('current:other'),salt)
    def test_egcc_threshold_retuning_and_bad_native_values_rejected(self):
        with self.assertRaises(ValueError):egcc([0,10],[.3,.3],[33,34],0,salinity_threshold=34.5)
        with self.assertRaises(ValueError):egcc([0,10],[.3,.3],[33,float('nan')],0)


class CohortAndTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.targets=p.load_targets(p.ROOT,cls.op);cls.controls=[(f,json.loads((p.ROOT/f).read_bytes())) for f in cls.op['retained_control_files']]
    def test_all32_original_cases_four_cuts_four_dates_each_owner(self):
        self.assertEqual(len(self.targets),32)
        for entity in p.RULES:
            own=[t['section'] for t in self.targets if t['section']['entity_id']==entity];self.assertEqual(len(own),16);self.assertEqual(len({s['section_definition']['id'] for s in own}),4);self.assertEqual(len({s['snapshot_time_utc'] for s in own}),4)
    def test_preflight_checks_all_native_columns_not_just_selected_core(self):
        ds,target=fixture();plans,planned,estimated,attrs,varattrs=p.preflight(ds,[target]);self.assertEqual(planned,120);self.assertEqual(len(plans),1);self.assertEqual(ds['salinity'].calls,[])
        ds['lon'].values[0]=2.99
        with self.assertRaises(ValueError):p.preflight(ds,[target])
        self.assertEqual(ds['salinity'].calls,[])
    def test_preflight_rejects_date_depth_frame_units_or_stencil_mismatch(self):
        for mode in ['time','depth','lat','units','standard','stencil']:
            ds,target=fixture()
            if mode=='time':ds['time'].values[0]=3
            elif mode=='depth':ds['depth'].values[1]=1.1
            elif mode=='lat':ds['lat'].values[0]=60.1
            elif mode=='units':ds['salinity'].units='g/kg'
            elif mode=='standard':ds['salinity'].standard_name='sea_water_absolute_salinity'
            else:target['section']['columns'][2]['global_longitude_index']=3
            with self.subTest(mode=mode),self.assertRaises(ValueError):p.preflight(ds,[target])
            self.assertEqual(ds['salinity'].calls,[])
    def test_full_native_cohort_preflight_fits_existing_caps(self):
        ds=full_fake(self.targets,[c for f,c in self.controls]);plans,planned,estimated,attrs,varattrs=p.preflight(ds,self.targets);self.assertEqual(len(plans),32);self.assertLessEqual(2*planned,250000);self.assertLessEqual(24*planned,7000000);self.assertLess(estimated,2400000);self.assertEqual(ds['salinity'].calls,[])
    def test_retry_reservation_protects_remaining_first_attempt_targets(self):
        with tempfile.TemporaryDirectory() as d:
            waits=[];reads=p.SectionReads(125000,Path(d)/'ledger.json',waits.append);var=Variable(errors=['NetCDF: I/O failure'])
            with self.assertRaises(ValueError):reads.read(var,0,0,0,2)
            self.assertEqual(len(var.calls),1);self.assertEqual(reads.extra,0);self.assertEqual(reads.requests[-1]['requested_scalar_values'],0);self.assertEqual(reads.requests[-1]['status'],'retry_denied_to_preserve_all_remaining_first_attempts')
    def test_exact_io_retry_after_two_and_five_seconds(self):
        with tempfile.TemporaryDirectory() as d:
            waits=[];reads=p.SectionReads(120,Path(d)/'ledger.json',waits.append);var=Variable(errors=['NetCDF: I/O failure','NetCDF: I/O failure',None]);a=reads.read(var,3,4,5,7);self.assertEqual(a.shape,(40,3));self.assertEqual(waits,[2,5]);self.assertEqual(reads.requested,360);self.assertEqual(reads.returned,120);self.assertEqual(reads.extra,240);self.assertTrue(all(k==var.calls[0] for k in var.calls))
    def test_successful_read_is_not_automatically_replayed(self):
        with tempfile.TemporaryDirectory() as d:
            reads=p.SectionReads(120,Path(d)/'ledger.json',lambda _:self.fail('No wait'));var=Variable();reads.read(var,0,0,0,2);self.assertEqual(len(var.calls),1);self.assertEqual(reads.extra,0)
    def test_non_io_errors_shape_changes_and_attempt_cap(self):
        for var,attempts in [(Variable(errors=['other error']),1),(Variable(shape=(39,1,3)),1),(Variable(errors=['NetCDF: I/O failure']*4),3)]:
            with tempfile.TemporaryDirectory() as d:
                reads=p.SectionReads(120,Path(d)/'ledger.json',lambda _:None)
                with self.assertRaises((ValueError,RuntimeError)):reads.read(var,0,0,0,2)
                self.assertEqual(len(var.calls),attempts);self.assertEqual(reads.returned,0)
    def test_original_native_and_patch_caps_cannot_be_widened(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):p.SectionReads(125001,Path(d)/'ledger.json')
            reads=p.SectionReads(120,Path(d)/'ledger.json');var=Variable()
            for args in [(0,0,0,1),(0,0,0,150),(0,0,-1,1)]:
                with self.assertRaises(ValueError):reads.read(var,*args)
            self.assertEqual(var.calls,[])
    def controls_fixture(self):
        targets=[];payloads={}
        for i,(file,c) in enumerate(self.controls):
            targets.append({'file':c['original_audit_record']['source_section_file']});cols=[[None]*40 for _ in range(7)];cols[2:5]=copy.deepcopy(c['practical_salinity_columns']);x0=c['native_longitude_indices_inclusive'][0]-2;payloads[i]={'native_longitude_indices_inclusive':[x0,x0+6],'source_time_index':c['source_time_index'],'native_latitude_index':c['native_latitude_index'],'depth_levels_m':c['depth_levels_m'],'practical_salinity_columns':cols}
        return targets,payloads
    def test_all_five_controls_match_exact_subsets(self):
        targets,payloads=self.controls_fixture();passed,results=p.check_controls(targets,payloads,self.controls);self.assertTrue(passed);self.assertEqual(len(results),5)
    def test_one_mismatched_or_missing_control_blocks_every_classification(self):
        targets,payloads=self.controls_fixture();payloads[0]['practical_salinity_columns'][2][0]=49;self.assertFalse(p.check_controls(targets,payloads,self.controls)[0]);payloads.pop(1);passed,results=p.check_controls(targets,payloads,self.controls);self.assertFalse(passed);self.assertIn('CONTROL_TARGET_NOT_RETRIEVED',[r['status'] for r in results])
    def test_metadata_open_failure_retains32_cases_and_no_fields(self):
        calls=[]
        def failure(url):calls.append(url);raise OSError('synthetic metadata failure')
        with tempfile.TemporaryDirectory() as d:
            report=p.collect(out=Path(d),dataset_factory=failure);self.assertEqual(report['status'],'SOURCE_OR_COHORT_PREFLIGHT_FAILED');self.assertEqual(len(report['records']),32);self.assertEqual(report['profiles'],[]);self.assertTrue(all(r['classification'] is None for r in report['records']));self.assertTrue((Path(d)/'source-report.json').exists())
        self.assertEqual(calls,[p.DATASET])
    def test_complete_fake_collection_preserves_cohort_and_requires_controls(self):
        ds=full_fake(self.targets,[])
        with tempfile.TemporaryDirectory() as d:
            report=p.collect(out=Path(d),dataset_factory=lambda url:ds);self.assertEqual(len(report['profiles']),32);self.assertEqual(report['status'],'RETAINED_CONTROL_GATE_NOT_SATISFIED');self.assertTrue(all(r['classification'] is None for r in report['records']));self.assertEqual(len(ds['salinity'].calls),32)
    def test_complete_fake_collection_with_matched_controls_classifies_original_cores(self):
        ds=full_fake(self.targets,[c for f,c in self.controls])
        with tempfile.TemporaryDirectory() as d:
            report=p.collect(out=Path(d),dataset_factory=lambda url:ds);self.assertEqual(report['status'],'ALL32SECTIONS_RETRIEVED_AND_CONTROLS_MATCH');self.assertTrue(report['all_five_retained_controls_match']);self.assertEqual(len(report['profiles']),32);self.assertEqual(report['transport']['additional_retry_scalars_reserved'],0);self.assertTrue(all(r['classification']['core_reselected'] is False for r in report['records']));self.assertEqual(report['new_reference_inventory_rows_admitted'],0)
    def test_failed_noncontrol_target_remains_gap_without_replacement(self):
        s=self.targets[16]['section'];slab=s['retrieved_hyperslab'];key=(s['source_time_index'],slab['latitude_index'],*slab['longitude_indices_inclusive']);ds=full_fake(self.targets,[c for f,c in self.controls],fail_key=key)
        with tempfile.TemporaryDirectory() as d:
            report=p.collect(out=Path(d),dataset_factory=lambda url:ds);self.assertEqual(report['status'],'PARTIAL_SOURCE_WITH_CONTROLS_MATCHED');self.assertEqual(len(report['profiles']),31);self.assertEqual(report['records'][16]['status'],'SOURCE_TARGET_FAILED_NO_SUBSTITUTION');self.assertIsNone(report['records'][16]['classification']);self.assertTrue(report['all_five_retained_controls_match'])
    def test_frozen_operator_pins_and_no_admission_or_cap_increase(self):
        import hashlib
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_joint_native_cell_units'],250000);self.assertEqual(self.op['maximum_decoded_bytes'],7000000);self.assertEqual(self.op['maximum_native_depth_levels'],40);self.assertEqual(self.op['maximum_source_batch_bytes'],2400000)
        for file,pin in self.op['input_sha256'].items():self.assertFalse(file.startswith('.pytest_cache/'));self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin,file)


if __name__=='__main__':unittest.main()
