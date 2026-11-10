import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import mixed_interval_section_geometry_v1 as geometry
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity

class SolomonUndercurrentsIntervalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.op=json.loads((cls.root/'research/solomon-undercurrents-interval-depth-sections-operator-v1.json').read_bytes())

    def test_declared_owner_frame_window_and_dates(self):
        self.assertEqual(set(self.op['currents']),{'current:new-ireland-coastal-undercurrent','current:solomon-island-coastal-undercurrent'})
        c=self.op['currents']['current:new-ireland-coastal-undercurrent']
        self.assertEqual(c['component_bearing_degrees_true'],0)
        self.assertEqual(c['selection_depth_interval_m'],[100,350]);self.assertEqual(c['core_search_depth_interval_m'],[100,350])
        self.assertNotEqual(self.op['currents']['current:new-ireland-coastal-undercurrent']['identity_evidence_basis'],self.op['currents']['current:solomon-island-coastal-undercurrent']['identity_evidence_basis'])
        self.assertEqual(c['primary_threshold_m_s'],.1);self.assertIsNone(c['surface_component_gate_m_s'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_eight_native_cuts_and_complete32target_budget(self):
        self.assertEqual(len(self.op['sections']),8)
        self.assertTrue(all(s['fixed_axis']=='latitude' for s in self.op['sections']))
        self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections']],[-4.4,-3.8,-3.2,-2.6,-6.6,-6.4,-6.2,-6.0])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),8);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        with self.assertRaises(ValueError):geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),{**self.op,'maximum_total_cell_pairs':1})

    def source(self):
        c={**self.op,**self.op['currents']['current:new-ireland-coastal-undercurrent']}
        z=[0,50,100,150,200,250,350,500,700]
        signed=np.array([[0,-.1,0],[.01,-.1,.01],[.01,.2,.01],[.01,.3,.01],[.01,.4,.01],[.01,.3,.01],[.01,.2,.01],[.01,.2,.01],[0,0,0]])
        bearing=np.deg2rad(0);u=signed*np.sin(bearing);v=signed*np.cos(bearing)
        lats=np.array([-4.44,-4.4,-4.36]);lons=np.array([153.2,153.28,153.36])
        plan={'definition':self.op['sections'][0],'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.}
        columns=geometry.columns_from_arrays(u,v,lats,lons,plan,0)
        packet={'entity_id':'current:new-ireland-coastal-undercurrent','section_definition':plan['definition'],'source_section_geometry':'latitude','snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':columns,'decoded_columns_sha256':canonical_hash(columns),'component_bearing_degrees_true':0,'diagnosis':diagnose(z,[x['signed_reference_component_m_s'] for x in columns],c),'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**geometry.retained_geometry(plan,lats,lons,0,len(z))}
        return packet,c

    def test_opposing_surface_does_not_discard_subsurface_flow_or_stop_at350m(self):
        p,c=self.source();geometry.validate_retained(p,c)
        self.assertEqual(p['diagnosis']['selected_column_index'],1)
        layer=next(x for x in p['diagnosis']['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
        self.assertGreater(layer['upper_depth_m'],50);self.assertGreater(layer['lower_depth_m'],350)
        self.assertEqual(along_velocity(0,1,0),1)
        self.assertEqual(along_velocity(0,-1,0),-1)

    def test_selected_gate_edge_is_not_replaced_by_weaker_interior(self):
        p,c=self.source();columns=[x['signed_reference_component_m_s'] for x in p['columns']]
        columns[0]=[x*2 for x in columns[1]]
        d=diagnose(p['depth_levels_m'],columns,c)
        self.assertEqual(d['selected_column_index'],0);self.assertEqual(d['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')

    def test_source_axis_and_component_mutations_are_rejected(self):
        p,c=self.source()
        bad=copy.deepcopy(p);bad['source_section_geometry']='longitude'
        with self.assertRaises(ValueError):geometry.validate_retained(bad,c)
        bad=copy.deepcopy(p);bad['columns'][1]['eastward_velocity_m_s'][4]+=.1
        with self.assertRaises(ValueError):geometry.validate_retained(bad,c)

    def test_all_declared_input_hashes_match(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)

if __name__=='__main__':unittest.main()
