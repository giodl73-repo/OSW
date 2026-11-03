import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import monsoon_direction_depth_contexts_v1 as p
import mixed_interval_section_geometry_v1 as geometry
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash


class MonsoonDirectionDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1];cls.op=json.loads((cls.root/'research/monsoon-direction-depth-sections-operator-v1.json').read_bytes());cls.config={**cls.op,**cls.op['currents'][p.TARGET]}

    def section(self):
        z=[0,50,100,150,200,300,500,1000]
        a=np.array([[.01,.08,.01,-.09,.01],[.01,.1,.01,-.1,.01],[.01,.12,.01,-.12,.01],[.01,.08,.01,-.08,.01],[.01,.04,.01,-.04,.01],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]])
        lats=np.array([3.8,3.84,3.88,3.92,3.96]);lons=np.array([77.42,77.5,77.58]);definition=self.op['sections'][0]
        plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2,3,4]),'maximum_longitude_distance_km':0.}
        columns=geometry.columns_from_arrays(a,np.zeros_like(a),lats,lons,plan,90)
        section={'schema':p.SCHEMA,'entity_id':p.TARGET,'section_definition':definition,'source_section_geometry':'longitude','component_bearing_degrees_true':90,
                 'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':columns,
                 'decoded_columns_sha256':canonical_hash(columns),'diagnosis':diagnose(z,[c['signed_reference_component_m_s'] for c in columns],self.config),
                 'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],'default_direction_context_id':'eastward',
                 'direction_contexts_are_additive':False,'contexts_are_independent_observations':False,'surface_undercurrent_separation_performed':False,
                 **geometry.retained_geometry(plan,lats,lons,0,len(z))}
        section['direction_contexts']=p.derive_contexts(section,self.config)
        return section

    def test_declared_owner_frames_windows_cutoffs_dates(self):
        self.assertEqual(set(self.op['currents']),{p.TARGET})
        for key,bearing in [('eastward',90),('westward',270)]:
            c=p.context_config(self.config,key);self.assertEqual(c['component_bearing_degrees_true'],bearing);self.assertEqual(c['selection_depth_interval_m'],[0,100]);self.assertEqual(c['primary_threshold_m_s'],.1)
        self.assertEqual(self.op['thresholds_m_s'],[.05,.1,.2]);self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])

    def test16field_targets_preflight_once_without_direction_read_duplication(self):
        self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections']],[77.5,78.5,79.5,80.5])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),4);self.assertEqual(pairs,4*sum(40*geometry.profile_count(plan) for plan in plans));self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)

    def test_opposite_signed_series_preserve_native_profile_pointers(self):
        section=self.section();a=section['direction_contexts']['eastward']['profiles'];b=section['direction_contexts']['westward']['profiles']
        for i,(east,west) in enumerate(zip(a,b)):
            self.assertEqual(east['source_native_profile_pointer'],'/columns/'+str(i));self.assertEqual(west['sampled_lon_lat'],section['columns'][i]['sampled_lon_lat'])
            for x,y in zip(east['signed_reference_component_m_s'],west['signed_reference_component_m_s']):self.assertAlmostEqual(x,-y,places=12)

    def test_each_context_selects_its_own_column_and_both_audits_pass(self):
        section=self.section();p.validate_contexts(section,self.config)
        self.assertEqual(section['direction_contexts']['eastward']['diagnosis']['selected_column_index'],1);self.assertEqual(section['direction_contexts']['westward']['diagnosis']['selected_column_index'],3)
        self.assertFalse(section['direction_contexts_are_additive']);self.assertFalse(section['contexts_are_independent_observations'])

    def test_missing_component_remains_unknown_in_both_contexts(self):
        section=self.section();section['columns'][1]['eastward_velocity_m_s'][0]=None
        contexts=p.derive_contexts(section,self.config)
        self.assertIsNone(contexts['eastward']['profiles'][1]['signed_reference_component_m_s'][0]);self.assertIsNone(contexts['westward']['profiles'][1]['signed_reference_component_m_s'][0])

    def test_weak_upper_flow_cannot_borrow_deep_flow_or_lower_sensitivity(self):
        section=self.section()
        for column in section['columns']:
            column['eastward_velocity_m_s']=[.03 if z<=100 else .3 for z in section['depth_levels_m']];column['northward_velocity_m_s']=[0.0]*len(section['depth_levels_m'])
        contexts=p.derive_contexts(section,self.config)
        for c in contexts.values():self.assertIsNone(c['diagnosis']['selected_column_index']);self.assertEqual(c['diagnosis']['selected_column_threshold_layers'],[])

    def test_window_endpoint_is_not_imposed_lower_boundary(self):
        section=self.section()
        for i,z in enumerate(section['depth_levels_m']):section['columns'][1]['eastward_velocity_m_s'][i]=.12 if z<=500 else 0
        contexts=p.derive_contexts(section,self.config);layer=next(r for r in contexts['eastward']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertGreater(layer['lower_depth_m'],100)

    def test_source_component_context_profile_default_and_additivity_mutations_rejected(self):
        section=self.section()
        for kind in ['native','profile','direction','default','additive']:
            bad=copy.deepcopy(section)
            if kind=='native':bad['columns'][1]['eastward_velocity_m_s'][0]=999
            if kind=='profile':bad['direction_contexts']['westward']['profiles'][3]['source_native_profile_pointer']='/columns/9999'
            if kind=='direction':bad['direction_contexts']['westward']['component_bearing_degrees_true']=90
            if kind=='default':bad['default_direction_context_id']='westward'
            if kind=='additive':bad['direction_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):p.validate_contexts(bad,self.config)

    def test_frame_window_primary_retuning_rejected(self):
        for field,value in [('component_bearing_degrees_true',290),('selection_depth_interval_m',[0,150]),('primary_threshold_m_s',.05)]:
            cfg=copy.deepcopy(self.config);cfg['direction_contexts']['westward'][field]=value
            with self.assertRaises(ValueError):p.context_config(cfg,'westward')

    def test_input_pins_frozen_function_binding_and_no_physical_promotion(self):
        self.assertIs(p.diagnose,diagnose);self.assertFalse(any(self.op['eligibility'].values()));self.assertIsNone(self.config['temperature_gate']);self.assertIsNone(self.config['surface_component_gate_m_s'])
        for file,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/file).read_bytes()).hexdigest(),pin,file)


if __name__=='__main__':unittest.main()
