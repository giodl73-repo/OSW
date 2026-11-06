import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import med_undercurrent_branch_depth_contexts_v1 as p
import mixed_interval_section_geometry_v1 as g
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash

class MediterraneanBranchContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1];cls.op=json.loads((cls.root/'research/med-undercurrent-branch-context-depth-sections-operator-v1.json').read_bytes())

    def fixture(self,kind='separated'):
        z=[0,400,500,700,800,900,1000,1250,1500,2000]
        middle=[0,0,.1,.15,.1,-.1,.1,.15,.1,0]
        if kind=='merged':middle=[.1]*9+[0]
        if kind=='missing':middle[5]=None
        return z,[[.01]*len(z),middle,[.01]*len(z)]

    def section(self,branch):
        definition=next(s for s in self.op['sections'] if s['diagnostic_branch_id']==branch);cfg=p.branch_config(self.op,definition)
        z,columns=self.fixture();a=np.array(columns).T
        if branch=='south-iberian':
            lats=np.array([36,36.04,36.08]);lons=np.array([351.42,351.5,351.58]);plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2]),'maximum_longitude_distance_km':0.};u=-a;v=np.zeros_like(a)
        else:
            lats=np.array([37.21,37.25,37.29]);lons=np.array([350,350.08,350.16]);plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.};u=np.zeros_like(a);v=a
        native=g.columns_from_arrays(u,v,lats,lons,plan,cfg['component_bearing_degrees_true']);d=p.diagnose_contexts(z,[c['signed_reference_component_m_s'] for c in native],cfg)
        return {'schema':p.SCHEMA,'entity_id':definition['entity_id'],'diagnostic_branch_id':branch,'section_definition':definition,'source_section_geometry':definition['fixed_axis'],'component_bearing_degrees_true':cfg['component_bearing_degrees_true'],
                'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':native,'decoded_columns_sha256':canonical_hash(native),
                'context_diagnoses':d,'diagnosis':d['upper']['diagnosis'],'default_diagnostic_context_id':'upper','vertical_contexts_are_additive':False,'contexts_are_independent_observations':False,'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**g.retained_geometry(plan,lats,lons,0,len(z))},cfg

    def test_declarations_frames_windows_native_units_and_dates(self):
        self.assertEqual(set(self.op['currents']),{'current:mediterranean-undercurrent'})
        for definition in self.op['sections']:
            cfg=p.branch_config(self.op,definition)
            for key,w in [('upper',[500,900]),('lower',[900,1500])]:
                c=p.context_config(cfg,key);self.assertEqual(c['selection_depth_interval_m'],w);self.assertEqual(c['primary_threshold_m_s'],.05);self.assertIsNone(c['surface_component_gate_m_s'])
        self.assertEqual(len(self.op['snapshot_times_utc']),4);self.assertEqual(self.op['thresholds_m_s'],[.02,.05,.1])

    def test_joint_preflight_eight_sections32targets_not64context_copies(self):
        plans,pairs=g.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),8);self.assertEqual(pairs,4*sum(40*g.profile_count(plan) for plan in plans));self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)

    def test_original_u_v_signed_frames_and_both_geometry_audits(self):
        for branch in self.op['branches']:
            section,cfg=self.section(branch);p.validate_contexts(section,cfg)
            self.assertEqual(section['context_diagnoses']['upper']['diagnosis']['selected_column_index'],1)
            for c in section['columns']:
                expected=[-x for x in c['eastward_velocity_m_s']] if branch=='south-iberian' else c['northward_velocity_m_s']
                np.testing.assert_allclose(c['signed_reference_component_m_s'],expected,atol=1e-14)

    def test_reversal_separates_components_without_clipping_at_search_endpoints(self):
        z,columns=self.fixture();cfg=p.branch_config(self.op,self.op['sections'][0]);d=p.diagnose_contexts(z,columns,cfg)
        a=next(r for r in d['upper']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.05);b=next(r for r in d['lower']['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.05)
        self.assertLess(a['upper_depth_m'],500);self.assertLess(a['lower_depth_m'],900);self.assertGreater(b['upper_depth_m'],900);self.assertGreater(b['lower_depth_m'],1500)

    def test_merged_contexts_are_not_independent_layers(self):
        z,columns=self.fixture('merged');cfg=p.branch_config(self.op,self.op['sections'][0]);d=p.diagnose_contexts(z,columns,cfg)
        a,b=[next(r for r in d[k]['diagnosis']['selected_column_threshold_layers'] if r['threshold_m_s']==.05) for k in ['upper','lower']]
        self.assertEqual((a['upper_depth_m'],a['lower_depth_m']),(b['upper_depth_m'],b['lower_depth_m']))

    def test_missing_shared_endpoint_blocks_both_searches(self):
        z,columns=self.fixture('missing');cfg=p.branch_config(self.op,self.op['sections'][0]);d=p.diagnose_contexts(z,columns,cfg)
        self.assertTrue(all(c['diagnosis']['selected_column_index'] is None for c in d.values()))

    def test_weak_context_cannot_borrow_other_profile_or_sensitivity(self):
        z,columns=self.fixture();cfg=p.branch_config(self.op,self.op['sections'][0])
        for key,(lo,hi) in [('upper',(500,900)),('lower',(900,1500))]:
            changed=copy.deepcopy(columns)
            for i,depth in enumerate(z):
                if lo<=depth<=hi:changed[1][i]=.03
            d=p.diagnose_contexts(z,changed,cfg);self.assertIsNone(d[key]['diagnosis']['selected_column_index']);self.assertIsNotNone(d['lower' if key=='upper' else 'upper']['diagnosis']['selected_column_index'])

    def test_source_branch_component_default_context_and_additivity_mutations_rejected(self):
        for branch in self.op['branches']:
            source,cfg=self.section(branch)
            for kind in ['branch','component','default','context','additive']:
                bad=copy.deepcopy(source)
                if kind=='branch':bad['diagnostic_branch_id']='wrong'
                if kind=='component':bad['columns'][1]['northward_velocity_m_s'][0]=999
                if kind=='default':bad['default_diagnostic_context_id']='lower'
                if kind=='context':bad['context_diagnoses']['lower']['diagnosis']['selected_column_index']=0
                if kind=='additive':bad['vertical_contexts_are_additive']=True
                with self.subTest(branch=branch,kind=kind),self.assertRaises(ValueError):p.validate_contexts(bad,cfg)

    def test_branch_frame_geometry_window_cutoff_retuning_rejected(self):
        for field,value in [('component_bearing_degrees_true',90),('section_geometry','latitude')]:
            op=copy.deepcopy(self.op);op['branches']['south-iberian'][field]=value
            with self.assertRaises(ValueError):p.branch_config(op,op['sections'][0])
        cfg=p.branch_config(self.op,self.op['sections'][0])
        for field,value in [('selection_depth_interval_m',[900,2000]),('primary_threshold_m_s',.1)]:
            bad=copy.deepcopy(cfg);bad['diagnostic_contexts']['lower'][field]=value
            with self.assertRaises(ValueError):p.context_config(bad,'lower')

    def test_pins_frozen_kernel_and_no_physical_or_pressure_conversion(self):
        self.assertIs(p.diagnose,diagnose);self.assertFalse(any(self.op['eligibility'].values()));self.assertFalse(self.op['pressure_to_depth_conversion_performed'])
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)

if __name__=='__main__':unittest.main()
