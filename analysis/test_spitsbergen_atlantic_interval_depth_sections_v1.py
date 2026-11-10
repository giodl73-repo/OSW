import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import mixed_interval_section_geometry_v1 as g
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity
import acquire_spitsbergen_atlantic_interval_depth_sections_v1 as c

class SpitsbergenAtlanticIntervalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1];cls.op=json.loads((cls.root/'research/spitsbergen-atlantic-interval-depth-sections-operator-v1.json').read_bytes());cls.cfg={**cls.op,**cls.op['currents']['current:spitsbergen-atlantic']}
    def section(self):
        z=[0,50,100,200,300,500,1000];a=np.array([[0,-.1,0],[.01,.2,.01],[.01,.3,.01],[.01,.3,.01],[.01,.2,.01],[0,.05,0],[0,0,0]])
        lats=np.array([76.26,76.3,76.34]);lons=np.array([13,13.08,13.16]);definition=self.op['sections'][0];plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.}
        columns=g.columns_from_arrays(-a/np.sqrt(2),a/np.sqrt(2),lats,lons,plan,315)
        return {'schema':'osw.mixed-interval-depth-section.v1','entity_id':'current:spitsbergen-atlantic','section_definition':definition,'source_section_geometry':'latitude','component_bearing_degrees_true':315,'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':columns,'decoded_columns_sha256':canonical_hash(columns),'diagnosis':diagnose(z,[x['signed_reference_component_m_s'] for x in columns],self.cfg),'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**g.retained_geometry(plan,lats,lons,0,len(z))}
    def test_canonical_owner_window_frame_and_conditional_scope(self):
        self.assertEqual(set(self.op['currents']),{'current:spitsbergen-atlantic'});self.assertEqual(self.cfg['selection_depth_interval_m'],[50,300]);self.assertEqual(self.cfg['core_search_depth_interval_m'],[50,300]);self.assertEqual(self.cfg['component_bearing_degrees_true'],315);self.assertEqual(self.cfg['primary_threshold_m_s'],.1);self.assertIsNone(self.cfg['surface_component_gate_m_s']);self.assertFalse(self.op['full_wsc_name_equivalence_admitted'])
    def test16targets_joint_preflight_under_original_caps(self):
        self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections']],[76.3,76.4,76.5,76.6]);plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op);self.assertEqual(len(plans),4);self.assertEqual(pairs,4*sum(40*g.profile_count(p) for p in plans));self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
    def test_native_northwest_signed_rotation_and_full_retained_audit(self):
        s=self.section();g.validate_retained(s,self.cfg);self.assertEqual(s['diagnosis']['selected_column_index'],1)
        for col in s['columns']:
            for u,v,along in zip(col['eastward_velocity_m_s'],col['northward_velocity_m_s'],col['signed_reference_component_m_s']):self.assertAlmostEqual(along_velocity(u,v,315),along,places=12)
    def test_weak_interval_cannot_borrow_deeper_flow_or_weaker_sensitivity(self):
        s=self.section();columns=[[.07 if 50<=z<=300 else .4 for z in s['depth_levels_m']]]*3;d=diagnose(s['depth_levels_m'],columns,self.cfg);self.assertIsNone(d['selected_column_index']);self.assertEqual(d['selected_column_threshold_layers'],[])
    def test_full_native_tracing_not_clipped_at300m_window(self):
        s=self.section();layer=next(x for x in s['diagnosis']['selected_column_threshold_layers'] if x['threshold_m_s']==.1);self.assertGreater(layer['lower_depth_m'],300);self.assertLess(layer['upper_depth_m'],50)
    def test_missing_native_endpoint_remains_unknown(self):
        s=self.section();columns=[[.2]*len(s['depth_levels_m']) for _ in range(3)]
        for col in columns:col[s['depth_levels_m'].index(300)]=None
        d=diagnose(s['depth_levels_m'],columns,self.cfg);self.assertIsNone(d['selected_column_index'])
    def test_native_frame_component_and_diagnosis_mutations_rejected(self):
        for kind in ['frame','component','diagnosis']:
            s=self.section()
            if kind=='frame':s['component_bearing_degrees_true']=0
            if kind=='component':s['columns'][1]['eastward_velocity_m_s'][1]=999
            if kind=='diagnosis':s['diagnosis']['selected_column_index']=0
            with self.subTest(kind=kind),self.assertRaises(ValueError):g.validate_retained(s,self.cfg)
    def test_pins_frozen_function_binding_and_no_physical_promotion(self):
        self.assertIs(c.diagnose,diagnose);self.assertIs(c.preflight,g.preflight);self.assertIs(c.validate_retained,g.validate_retained);self.assertFalse(any(self.op['eligibility'].values()));self.assertIsNone(self.cfg['temperature_gate'])
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)

if __name__=='__main__':unittest.main()
