import copy
import json
import tempfile
from pathlib import Path
import unittest
import numpy as np
import mixed_interval_section_geometry_v1 as geometry
from bounded_hycom_mixed_reads_v1 import BoundedMixedReads
from bounded_hycom_component_reads_v1 import BoundedComponentReads
from bounded_hycom_latitude_reads_v1 import BoundedLatitudeReads
from interval_transverse_section_audit_v1 import validate_retained as longitude_audit
from latitude_interval_section_audit_v1 import validate_retained as latitude_audit
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash


class Variable:
    def __init__(self,name='water_u',failures=0,error='NetCDF: I/O failure',wrong_shape=False):
        self.name=name;self.failures=failures;self.error=error;self.wrong_shape=wrong_shape;self.calls=[]
    def __getitem__(self,key):
        self.calls.append(key)
        if len(self.calls)<=self.failures:raise RuntimeError(self.error)
        return np.ones((1,39 if self.wrong_shape else 40,6,6),dtype=np.float32)[key]


class BarentsMakassarMixedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/barents-makassar-interval-depth-sections-operator-v1.json').read_bytes())

    def reader(self,path,maximum_pairs=360):
        return BoundedMixedReads(240,{'maximum_total_cell_pairs':maximum_pairs,'maximum_total_decoded_velocity_bytes':7000000,'maximum_component_read_attempts':3},path,lambda delay:None)

    def test_two_canonical_owners_and_correct_perpendicular_section_axes(self):
        self.assertEqual(set(self.op['currents']),{'current:north-cape','current:indonesian-throughflow'})
        self.assertEqual(len(self.op['sections']),8)
        north=[s for s in self.op['sections'] if s['entity_id']=='current:north-cape'];makassar=[s for s in self.op['sections'] if s['entity_id']=='current:indonesian-throughflow']
        self.assertTrue(all(s['fixed_axis']=='longitude' and s['latitude_gate_degrees_north']==[70.5,73.5] for s in north))
        self.assertEqual([s['longitude_degrees_east'] for s in north],[20,22,24,26])
        self.assertTrue(all(s['fixed_axis']=='latitude' and s['longitude_gate_degrees_east']==[117.5,120] for s in makassar))
        self.assertEqual([s['latitude_degrees_north'] for s in makassar],[-1,-2,-3,-4])

    def test_all32_native_targets_preflight_jointly_under_original_caps(self):
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),8);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])

    def test_joint_budget_rejects_plan_that_only_fits_axes_individually(self):
        lats=np.arange(-80,80.001,.04);lons=np.arange(0,360,.08);counts=[]
        for axis,module in [('longitude',geometry.longitude_geometry),('latitude',geometry.latitude_geometry)]:
            counts.append(module.preflight(lats,lons,{**self.op,'sections':[s for s in self.op['sections'] if s['fixed_axis']==axis]})[1])
        bad={**self.op,'maximum_total_cell_pairs':max(counts)}
        with self.assertRaisesRegex(ValueError,'Joint mixed-axis'):geometry.preflight(lats,lons,bad)
        bad=copy.deepcopy(self.op);bad['sections'][-1]['fixed_axis']='unknown'
        with self.assertRaises(ValueError):geometry.preflight(lats,lons,bad)

    def test_current_specific_intervals_frames_and_no_physical_promotion(self):
        for entity,frame,window in [('current:north-cape',90,[50,350]),('current:indonesian-throughflow',180,[50,200])]:
            c=self.op['currents'][entity];self.assertEqual(c['component_bearing_degrees_true'],frame)
            self.assertEqual(c['selection_depth_interval_m'],window);self.assertEqual(c['core_search_depth_interval_m'],window)
            self.assertEqual(c['primary_threshold_m_s'],.1);self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_mixed_read_and_audit_dispatch_preserve_exact_frozen_functions(self):
        self.assertIs(BoundedMixedReads.read_longitude,BoundedComponentReads.read)
        self.assertIs(BoundedMixedReads.read_latitude,BoundedLatitudeReads.read)
        self.assertIs(geometry.longitude_audit,longitude_audit);self.assertIs(geometry.latitude_audit,latitude_audit)

    def test_both_native_geometries_reaudit_opposing_surface_subsurface_profiles(self):
        z=[0,50,100,200,350,500,700];signed=np.array([[0,-.1,0],[.01,.02,.01],[.01,.2,.01],[.01,.3,.01],[.01,.2,.01],[.01,.02,.01],[0,-.1,0]])
        for entity in self.op['currents']:
            config={**self.op,**self.op['currents'][entity]};south=entity=='current:indonesian-throughflow'
            if south:
                lats=np.array([-3.04,-3,-2.96]);lons=np.array([117.6,117.68,117.76]);definition=next(s for s in self.op['sections'] if s.get('latitude_degrees_north')==-3)
                plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.};u=np.zeros_like(signed);v=-signed
            else:
                lats=np.array([71,71.04,71.08]);lons=np.array([19.92,20,20.08]);definition=next(s for s in self.op['sections'] if s.get('longitude_degrees_east')==20)
                plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2]),'maximum_longitude_distance_km':0.};u=signed;v=np.zeros_like(signed)
            columns=geometry.columns_from_arrays(u,v,lats,lons,plan,config['component_bearing_degrees_true'])
            source={'entity_id':entity,'section_definition':definition,'source_section_geometry':definition['fixed_axis'],
                'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z',
                'depth_levels_m':z,'columns':columns,'decoded_columns_sha256':canonical_hash(columns),
                'component_bearing_degrees_true':config['component_bearing_degrees_true'],'diagnosis':diagnose(z,[c['signed_reference_component_m_s'] for c in columns],config),
                'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**geometry.retained_geometry(plan,lats,lons,0,len(z))}
            geometry.validate_retained(source,config);self.assertEqual(source['diagnosis']['selected_column_index'],1)
            layer=next(x for x in source['diagnosis']['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
            self.assertGreater(layer['upper_depth_m'],0);self.assertGreater(layer['lower_depth_m'],config['selection_depth_interval_m'][1])
            bad=copy.deepcopy(source);bad['source_section_geometry']='latitude' if not south else 'longitude'
            with self.assertRaises(ValueError):geometry.validate_retained(bad,config)

    def test_interleaved_axes_share_retry_reserve_return_counts_and_one_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            reads=self.reader(Path(tmp)/'ledger.json');a,b,c,d=Variable(),Variable('water_v',1),Variable('water_u',1),Variable('water_v')
            reads.read_longitude(a,0,0,2,4);reads.read_longitude(b,0,0,2,4)
            reads.read_latitude(c,0,3,0,2);reads.read_latitude(d,0,3,0,2)
            self.assertEqual([len(x.calls) for x in [a,b,c,d]],[1,2,2,1])
            self.assertEqual(b.calls,[b.calls[0]]*2);self.assertEqual(c.calls,[c.calls[0]]*2)
            self.assertEqual(reads.requested_values,720);self.assertEqual(reads.returned_values,480);self.assertEqual(reads.extra_values,240)
            receipt=json.loads((Path(tmp)/'ledger.json').read_bytes());self.assertEqual(receipt,reads.receipt())
            self.assertEqual(receipt['schema'],'osw.bounded-hycom-mixed-reads.v1')
            successes=[r for r in receipt['requests'] if r['status']=='success']
            self.assertEqual(sum('longitude_index' in x for x in successes),2);self.assertEqual(sum('latitude_index' in x for x in successes),2)

    def test_second_axis_cannot_spend_reserve_for_future_first_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            reads=self.reader(Path(tmp)/'ledger.json',300);a,b,c=Variable(),Variable('water_v',1),Variable('water_u',1)
            reads.read_longitude(a,0,0,2,4);reads.read_longitude(b,0,0,2,4)
            with self.assertRaisesRegex(ValueError,'reserved'):reads.read_latitude(c,0,3,0,2)
            self.assertEqual([len(x.calls) for x in [a,b,c]],[1,2,1]);self.assertEqual(reads.extra_values,120)
            self.assertEqual(reads.requests[-1]['status'],'retry_denied_before_read_by_full_target_budget')

    def test_both_axes_reject_nontransport_and_shape_errors_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            for axis,args in [('longitude',(0,2,4)),('latitude',(3,0,2))]:
                for var in [Variable(failures=2,error='Metadata mismatch'),Variable(wrong_shape=True)]:
                    reads=self.reader(Path(tmp)/'ledger.json')
                    with self.assertRaises((ValueError,RuntimeError)):getattr(reads,'read_'+axis)(var,0,*args)
                    self.assertEqual(len(var.calls),1)

    def test_retry_limit_remains_three_exact_attempts_on_either_axis(self):
        with tempfile.TemporaryDirectory() as tmp:
            for axis,args in [('longitude',(0,2,4)),('latitude',(3,0,2))]:
                reads=self.reader(Path(tmp)/'ledger.json');var=Variable(failures=9)
                with self.assertRaises(RuntimeError):getattr(reads,'read_'+axis)(var,0,*args)
                self.assertEqual(len(var.calls),3);self.assertEqual(var.calls,[var.calls[0]]*3);self.assertEqual(reads.returned_values,0)


if __name__=='__main__':unittest.main()
