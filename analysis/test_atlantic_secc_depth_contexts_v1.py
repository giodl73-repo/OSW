import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import atlantic_secc_depth_contexts_v1 as contexts
import mixed_interval_section_geometry_v1 as geometry
from sample_eac_hycom_route_depth_v1 import canonical_hash


class AtlanticSeccDepthContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.op=json.loads((cls.root/'research/atlantic-secc-multi-context-depth-sections-operator-v1.json').read_bytes())
        cls.config={**cls.op,**cls.op['currents']['current:atlantic-south-equatorial-countercurrent']}

    def fixture(self,kind='separated'):
        z=[0,25,50,75,100,110,150,200,250,300,350,400,500]
        middle=[.2,.25,.3,.25,.2,-.1,.2,.25,.3,.25,.2,.05,0]
        if kind=='merged':middle=[.2]*12+[0]
        if kind=='missing':middle[5]=None
        columns=[[.01]*len(z),middle,[.01]*len(z)]
        return z,columns

    def section(self):
        z,columns=self.fixture();a=np.array(columns).T
        lats=np.array([-8,-7.96,-7.92]);lons=np.array([329.92,330,330.08])
        definition=self.op['sections'][0];plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2]),'maximum_longitude_distance_km':0.}
        native=geometry.columns_from_arrays(a,np.zeros_like(a),lats,lons,plan,90)
        diagnoses=contexts.diagnose_contexts(z,columns,self.config)
        return {'schema':contexts.SCHEMA,'entity_id':self.config['entity_id'],'section_definition':definition,'source_section_geometry':'longitude',
                'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z',
                'depth_levels_m':z,'columns':native,'decoded_columns_sha256':canonical_hash(native),'component_bearing_degrees_true':90,
                'context_diagnoses':diagnoses,'diagnosis':diagnoses['shallow']['diagnosis'],'default_diagnostic_context_id':'shallow',
                'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,
                'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],
                **geometry.retained_geometry(plan,lats,lons,0,len(z))}

    def test_windows_owner_dates_and_no_surface_gate_are_predeclared(self):
        self.assertEqual(set(self.op['currents']),{'current:atlantic-south-equatorial-countercurrent'})
        for key,window in [('shallow',[0,100]),('deep',[150,350])]:
            cfg=contexts.context_config(self.config,key);self.assertEqual(cfg['selection_depth_interval_m'],window)
            self.assertEqual(cfg['primary_threshold_m_s'],.1);self.assertIsNone(cfg['surface_component_gate_m_s'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])

    def test_preflight_reads_four_geometries_not_eight_context_copies(self):
        self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections']],[-30,-28,-26,-24])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),4);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans));self.assertLess(pairs,250000)

    def test_reversal_keeps_shallow_and_deep_connected_layers_separate(self):
        z,columns=self.fixture();d=contexts.diagnose_contexts(z,columns,self.config)
        a=next(r for r in d['shallow']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        b=next(r for r in d['deep']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertLess(a['lower_depth_m'],110);self.assertGreater(b['upper_depth_m'],110)
        self.assertEqual(a['upper_depth_m'],0);self.assertGreater(b['lower_depth_m'],350)

    def test_weak_context_cannot_borrow_other_context_or_sensitivity(self):
        z,columns=self.fixture()
        for weak,key in [('deep','deep'),('shallow','shallow')]:
            modified=copy.deepcopy(columns)
            for i,depth in enumerate(z):
                if (weak=='deep' and 150<=depth<=350) or (weak=='shallow' and depth<=100):modified[1][i]=.07
            d=contexts.diagnose_contexts(z,modified,self.config)
            self.assertIsNone(d[key]['diagnosis']['selected_column_index'])
            self.assertIsNotNone(d['shallow' if key=='deep' else 'deep']['diagnosis']['selected_column_index'])

    def test_missing_intermediate_support_censors_both_sides_without_bridging(self):
        z,columns=self.fixture('missing');d=contexts.diagnose_contexts(z,columns,self.config)
        a=next(r for r in d['shallow']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        b=next(r for r in d['deep']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertIsNone(a['lower_depth_m']);self.assertIsNone(b['upper_depth_m'])

    def test_same_connected_component_is_not_promoted_to_additive_layers(self):
        z,columns=self.fixture('merged');d=contexts.diagnose_contexts(z,columns,self.config)
        layers=[next(r for r in d[key]['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1) for key in ['shallow','deep']]
        self.assertEqual(layers[0]['upper_depth_m'],layers[1]['upper_depth_m']);self.assertEqual(layers[0]['lower_depth_m'],layers[1]['lower_depth_m'])
        section=self.section();self.assertFalse(section['vertical_contexts_are_additive']);self.assertFalse(section['contexts_are_independent_observations'])

    def test_both_context_audits_reject_component_diagnosis_and_default_mutations(self):
        section=self.section();contexts.validate_contexts(section,self.config)
        for kind in ['component','deep','default','additive']:
            bad=copy.deepcopy(section)
            if kind=='component':bad['columns'][1]['eastward_velocity_m_s'][2]+=.1
            if kind=='deep':bad['context_diagnoses']['deep']['diagnosis']['selected_column_index']=0
            if kind=='default':bad['default_diagnostic_context_id']='deep'
            if kind=='additive':bad['vertical_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):contexts.validate_contexts(bad,self.config)

    def test_context_boundary_and_cutoff_retuning_rejected(self):
        for key,value in [('selection_depth_interval_m',[100,350]),('primary_threshold_m_s',.05)]:
            cfg=copy.deepcopy(self.config);cfg['diagnostic_contexts']['deep'][key]=value
            with self.assertRaises(ValueError):contexts.context_config(cfg,'deep')

    def test_all_pins_and_frozen_function_binding_match(self):
        from interval_depth_diagnostic_v1 import diagnose
        self.assertIs(contexts.diagnose,diagnose)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
