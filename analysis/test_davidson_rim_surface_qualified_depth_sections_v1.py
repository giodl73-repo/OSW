import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import surface_qualified_mixed_geometry_v1 as geometry
from acquire_three_current_depth_sections_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity

class DavidsonRimSurfaceQualifiedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.op=json.loads((cls.root/'research/davidson-rim-surface-qualified-depth-sections-operator-v1.json').read_bytes())

    def test_declared_owners_frames_windows_and_dates(self):
        self.assertEqual(set(self.op['currents']),{'current:davidson','current:black-sea-rim'})
        for entity,frame,window in [('current:davidson',0,[0,200]),('current:black-sea-rim',90,[0,200])]:
            c=self.op['currents'][entity]
            self.assertEqual(c['component_bearing_degrees_true'],frame)
            self.assertEqual(c['selection_depth_interval_m'],window);self.assertEqual(c['core_search_depth_interval_m'],window)
            self.assertEqual(c['primary_threshold_m_s'],.1);self.assertEqual(c['surface_component_gate_m_s'],.05);self.assertIsNone(c['temperature_gate'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_eight_cuts_and_complete32target_budget(self):
        self.assertEqual(len(self.op['sections']),8)
        self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections'][:4]],[36.5,38,39.5,41])
        self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections'][4:]],[31,32,33,34])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),8);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)

    def test_joint_plan_cannot_use_independent_axis_budget_resets(self):
        lats=np.arange(-80,80.001,.04);lons=np.arange(0,360,.08);counts=[]
        for axis,module in [('longitude',geometry.longitude_geometry),('latitude',geometry.latitude_geometry)]:
            counts.append(module.preflight(lats,lons,{**self.op,'sections':[s for s in self.op['sections'] if s['fixed_axis']==axis]})[1])
        with self.assertRaisesRegex(ValueError,'Joint mixed-axis'):geometry.preflight(lats,lons,{**self.op,'maximum_total_cell_pairs':max(counts)})

    def source(self,entity):
        c={**self.op,**self.op['currents'][entity]};frame=c['component_bearing_degrees_true']
        z=[0,50,100,150,200,300,500,700]
        signed=np.array([[.01,.2,.01],[.01,.25,.01],[.01,.3,.01],[.01,.4,.01],[.01,.3,.01],[.01,.2,.01],[.01,.1,.01],[0,0,0]])
        theta=np.deg2rad(frame);u=signed*np.sin(theta);v=signed*np.cos(theta)
        definition=next(s for s in self.op['sections'] if s['entity_id']==entity)
        if definition['fixed_axis']=='latitude':
            lats=np.array([36.46,36.5,36.54]);lons=np.array([236.8,236.88,236.96])
            plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.}
        else:
            lats=np.array([41.7,41.74,41.78]);lons=np.array([30.92,31,31.08])
            plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2]),'maximum_longitude_distance_km':0.}
        columns=geometry.columns_from_arrays(u,v,lats,lons,plan,frame)
        p={'surface_velocity_qualification_applied':True,'surface_component_gate_m_s':.05,'entity_id':entity,'section_definition':definition,'source_section_geometry':definition['fixed_axis'],'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':columns,'decoded_columns_sha256':canonical_hash(columns),'component_bearing_degrees_true':frame,'diagnosis':diagnose(z,[x['signed_reference_component_m_s'] for x in columns],c),'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**geometry.retained_geometry(plan,lats,lons,0,len(z))}
        return p,c

    def test_both_native_geometries_trace_beyond_selection_window(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);geometry.validate_retained(p,c)
            self.assertEqual(p['diagnosis']['selected_column_index'],1)
            layer=next(x for x in p['diagnosis']['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
            self.assertEqual(layer['upper_depth_m'],0)
            self.assertGreater(layer['lower_depth_m'],c['selection_depth_interval_m'][1])
            self.assertAlmostEqual(along_velocity(0,1,0),1)
            self.assertEqual(along_velocity(1,0,90),1)

    def test_selected_gate_edge_is_not_replaced_by_weaker_interior(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);columns=[x['signed_reference_component_m_s'] for x in p['columns']]
            columns[0]=[x*2 for x in columns[1]];d=diagnose(p['depth_levels_m'],columns,c)
            self.assertEqual(d['selected_column_index'],0);self.assertEqual(d['horizontal_selection_status'],'section_gate_edge_maximum_axis_unresolved')

    def test_both_source_axis_and_component_mutations_are_rejected(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);bad=copy.deepcopy(p)
            bad['source_section_geometry']='latitude' if p['source_section_geometry']=='longitude' else 'longitude'
            with self.assertRaises(ValueError):geometry.validate_retained(bad,c)
            bad=copy.deepcopy(p);bad['columns'][1]['northward_velocity_m_s'][2]+=.1
            with self.assertRaises(ValueError):geometry.validate_retained(bad,c)

    def test_missing_support_below_selection_censors_without_bridging(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);columns=[x['signed_reference_component_m_s'] for x in p['columns']]
            columns[1][5]=None;d=diagnose(p['depth_levels_m'],columns,c)
            self.assertEqual(d['selected_column_index'],1)
            layer=next(x for x in d['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
            self.assertIsNone(layer['lower_depth_m']);self.assertEqual(layer['lower_status'],'censored_before_missing_or_dry_level')

    def test_all_declared_input_hashes_match(self):
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((self.root/f).read_bytes()).hexdigest(),pin,f)

    def test_surface_opposed_weak_or_missing_deep_jet_is_ineligible(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);columns=[x['signed_reference_component_m_s'] for x in p['columns']]
            for surface in [-.2,.04,None]:
                modified=copy.deepcopy(columns);modified[1][0]=surface
                result=diagnose(p['depth_levels_m'],modified,c)
                self.assertIsNone(result['selected_column_index'])

    def test_surface_qualification_allows_nonzero_primary_upper_crossing_and_rejects_relabeling(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);columns=[x['signed_reference_component_m_s'] for x in p['columns']]
            columns[1][0]=.08;result=diagnose(p['depth_levels_m'],columns,c)
            self.assertEqual(result['selected_column_index'],1)
            primary=next(x for x in result['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
            self.assertGreater(primary['upper_depth_m'],0)
            p['surface_velocity_qualification_applied']=False
            with self.assertRaises(ValueError):geometry.validate_retained(p,c)

    def test_geometry_and_diagnose_bindings_are_exact_frozen_functions(self):
        import mixed_interval_section_geometry_v1 as mixed
        import acquire_three_current_depth_sections_v1 as classic
        self.assertIs(geometry.preflight,mixed.preflight)
        self.assertIs(geometry.columns_from_arrays,mixed.columns_from_arrays)
        self.assertIs(geometry.diagnose,classic.diagnose)


if __name__=='__main__':unittest.main()
