import copy,hashlib,json,unittest
from pathlib import Path
import numpy as np
import mixed_interval_section_geometry_v1 as geometry
from interval_depth_diagnostic_v1 import diagnose
from sample_eac_hycom_route_depth_v1 import canonical_hash,along_velocity

class GaspeJutlandShallowSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).resolve().parents[1]
        cls.op=json.loads((cls.root/'research/gaspe-jutland-shallow-interval-depth-sections-operator-v1.json').read_bytes())

    def test_declared_owners_frames_windows_and_dates(self):
        self.assertEqual(set(self.op['currents']),{'current:gaspe','current:jutland'})
        for entity,frame,window in [('current:gaspe',90,[0,30]),('current:jutland',0,[0,30])]:
            c=self.op['currents'][entity]
            self.assertEqual(c['component_bearing_degrees_true'],frame)
            self.assertEqual(c['selection_depth_interval_m'],window);self.assertEqual(c['core_search_depth_interval_m'],window)
            self.assertEqual(c['selection_window_basis'],'osw_common_shallow_surface_diagnostic_not_source_measured_layer')
            self.assertEqual(c['primary_threshold_m_s'],.1);self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_eight_cuts_and_complete32target_budget(self):
        self.assertEqual(len(self.op['sections']),8)
        self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections'][:4]],[-66.5,-66,-65.5,-65])
        self.assertEqual([s['latitude_degrees_north'] for s in self.op['sections'][4:]],[55.5,56,56.5,57])
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),8);self.assertEqual(pairs,4*sum(40*geometry.profile_count(p) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)

    def test_full_quarterly_plan_cannot_truncate_to_one_date_budget(self):
        lats=np.arange(-80,80.001,.04);lons=np.arange(0,360,.08)
        once={**self.op,'snapshot_times_utc':self.op['snapshot_times_utc'][:1]}
        plans,pairs=geometry.preflight(lats,lons,once)
        with self.assertRaises(ValueError):geometry.preflight(lats,lons,{**self.op,'maximum_total_cell_pairs':pairs})

    def source(self,entity):
        c={**self.op,**self.op['currents'][entity]};frame=c['component_bearing_degrees_true']
        z=[0,10,20,30,50,100,300,700]
        signed=np.array([[.01,.2,.01],[.01,.25,.01],[.01,.3,.01],[.01,.4,.01],[.01,.3,.01],[.01,.2,.01],[.01,.1,.01],[0,0,0]])
        theta=np.deg2rad(frame);u=signed*np.sin(theta);v=signed*np.cos(theta)
        definition=next(s for s in self.op['sections'] if s['entity_id']==entity)
        if entity=='current:gaspe':
            lats=np.array([49.3,49.34,49.38]);lons=np.array([293.42,293.5,293.58])
            plan={'definition':definition,'longitude_index':1,'latitude_indices':np.array([0,1,2]),'maximum_longitude_distance_km':0.}
        else:
            lats=np.array([55.46,55.5,55.54]);lons=np.array([7.8,7.88,7.96])
            plan={'definition':definition,'latitude_index':1,'longitude_indices':np.array([0,1,2]),'nearest_latitude_distance_km':0.}
        columns=geometry.columns_from_arrays(u,v,lats,lons,plan,frame)
        p={'entity_id':entity,'section_definition':definition,'source_section_geometry':definition['fixed_axis'],'snapshot_time_utc':'2022-03-15T00:00:00Z','source_returned_timestamp_utc':'2022-03-15T00:00:00Z','depth_levels_m':z,'columns':columns,'decoded_columns_sha256':canonical_hash(columns),'component_bearing_degrees_true':frame,'diagnosis':diagnose(z,[x['signed_reference_component_m_s'] for x in columns],c),'native100m_temperature_degrees_celsius':None,'temperature_source':None,'eligibility':self.op['eligibility'],**geometry.retained_geometry(plan,lats,lons,0,len(z))}
        return p,c

    def test_fixed_surface_reference_frames_trace_beyond_selection_window(self):
        for entity in self.op['currents']:
            p,c=self.source(entity);geometry.validate_retained(p,c)
            self.assertEqual(p['diagnosis']['selected_column_index'],1)
            layer=next(x for x in p['diagnosis']['selected_column_threshold_layers'] if x['threshold_m_s']==.1)
            self.assertEqual(layer['upper_depth_m'],0)
            self.assertGreater(layer['lower_depth_m'],c['selection_depth_interval_m'][1])
            self.assertEqual(along_velocity(1,0,90),1)
            self.assertEqual(along_velocity(0,1,0),1)

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

if __name__=='__main__':unittest.main()
