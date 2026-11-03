import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import dwbc_abaco_depth_contexts_v1 as contexts
import mixed_interval_section_geometry_v1 as geometry
from sample_eac_hycom_route_depth_v1 import canonical_hash


class DwbcAbacoDepthContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.op=json.loads((cls.root/'research/dwbc-abaco-multi-context-depth-sections-operator-v1.json').read_bytes())
        cls.config={**cls.op,**cls.op['currents']['current:deep-western-boundary']}

    def fixture(self,kind='separated'):
        z=[0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000]
        middle=[0,0,.2,.3,.3,.2,-.1,.2,.3,.3,.2,.05,0]
        if kind=='merged':middle=[.2]*12+[0]
        if kind=='missing':middle[6]=None
        columns=[[.01]*len(z),middle,[.01]*len(z)]
        return z,columns

    def section(self):
        z,columns=self.fixture();a=np.array(columns).T
        lats=np.array([24.46,24.5,24.54]);lons=np.array([283,283.08,283.16])
        definition=self.op['sections'][0];plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'maximum_latitude_distance_km':0.}
        native=geometry.columns_from_arrays(np.zeros_like(a),-a,lats,lons,plan,180)
        diagnoses=contexts.diagnose_contexts(z,columns,self.config)
        return {'schema':contexts.SCHEMA,'entity_id':self.config['entity_id'],'section_definition':definition,'source_section_geometry':'latitude',
                'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z',
                'depth_levels_m':z,'columns':native,'decoded_columns_sha256':canonical_hash(native),'component_bearing_degrees_true':180,
                'context_diagnoses':diagnoses,'diagnosis':diagnoses['upper']['diagnosis'],'default_diagnostic_context_id':'upper',
                'vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,
                'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],
                **geometry.retained_geometry(plan,lats,lons,0,len(z))}

    def test_windows_owner_dates_and_no_surface_gate_are_predeclared(self):
        self.assertEqual(set(self.op['currents']),{'current:deep-western-boundary'})
        for key,window in [('upper',[1000,3000]),('lower',[3000,5000])]:
            cfg=contexts.context_config(self.config,key);self.assertEqual(cfg['selection_depth_interval_m'],window)
            self.assertEqual(cfg['primary_threshold_m_s'],.1);self.assertIsNone(cfg['surface_component_gate_m_s'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])

    def test_preflight_reads_four_geometries_not_eight_context_copies(self):
        self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections']],[24.5,25.5,26.5,27.5])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),4);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans));self.assertLess(pairs,250000)

    def test_reversal_keeps_shallow_and_deep_connected_layers_separate(self):
        z,columns=self.fixture();d=contexts.diagnose_contexts(z,columns,self.config)
        a=next(r for r in d['upper']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        b=next(r for r in d['lower']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1)
        self.assertLess(a['lower_depth_m'],3000);self.assertGreater(b['upper_depth_m'],3000)
        self.assertEqual(a['upper_depth_m'],750);self.assertGreater(b['lower_depth_m'],5000)

    def test_weak_context_cannot_borrow_other_context_or_sensitivity(self):
        z,columns=self.fixture()
        for weak,key in [('lower','lower'),('upper','upper')]:
            modified=copy.deepcopy(columns)
            for i,depth in enumerate(z):
                if (weak=='lower' and 3000<=depth<=5000) or (weak=='upper' and 1000<=depth<=3000):modified[1][i]=.07
            d=contexts.diagnose_contexts(z,modified,self.config)
            self.assertIsNone(d[key]['diagnosis']['selected_column_index'])
            self.assertIsNotNone(d['upper' if key=='lower' else 'lower']['diagnosis']['selected_column_index'])

    def test_missing_shared_endpoint_disqualifies_both_contexts_without_bridge(self):
        z,columns=self.fixture('missing');d=contexts.diagnose_contexts(z,columns,self.config)
        for key in ['upper','lower']:
            self.assertIsNone(d[key]['diagnosis']['selected_column_index'])
            self.assertEqual(d[key]['diagnosis']['selected_column_threshold_layers'],[])

    def test_same_connected_component_is_not_promoted_to_additive_layers(self):
        z,columns=self.fixture('merged');d=contexts.diagnose_contexts(z,columns,self.config)
        layers=[next(r for r in d[key]['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.1) for key in ['upper','lower']]
        self.assertEqual(layers[0]['upper_depth_m'],layers[1]['upper_depth_m']);self.assertEqual(layers[0]['lower_depth_m'],layers[1]['lower_depth_m'])
        section=self.section();self.assertFalse(section['vertical_contexts_are_additive']);self.assertFalse(section['contexts_are_independent_observations'])

    def test_both_context_audits_reject_component_diagnosis_and_default_mutations(self):
        section=self.section();contexts.validate_contexts(section,self.config)
        for kind in ['component','lower','default','additive']:
            bad=copy.deepcopy(section)
            if kind=='component':bad['columns'][1]['eastward_velocity_m_s'][2]+=.1
            if kind=='lower':bad['context_diagnoses']['lower']['diagnosis']['selected_column_index']=0
            if kind=='default':bad['default_diagnostic_context_id']='lower'
            if kind=='additive':bad['vertical_contexts_are_additive']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):contexts.validate_contexts(bad,self.config)

    def test_context_boundary_and_cutoff_retuning_rejected(self):
        for key,value in [('selection_depth_interval_m',[100,350]),('primary_threshold_m_s',.05)]:
            cfg=copy.deepcopy(self.config);cfg['diagnostic_contexts']['lower'][key]=value
            with self.assertRaises(ValueError):contexts.context_config(cfg,'lower')

    def test_all_pins_and_frozen_function_binding_match(self):
        from interval_depth_diagnostic_v1 import diagnose
        self.assertIs(contexts.diagnose,diagnose)
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)


if __name__=='__main__':unittest.main()
