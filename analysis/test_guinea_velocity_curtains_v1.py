"""Exact source reproduction,graph boundaries and scientific scope on all14 cases."""
import copy,json,unittest
import derive_guinea_velocity_curtains_v1 as derive
from unittest.mock import patch


class GuineaCurtains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report,cls.raw=derive.build();cls.op=json.loads((derive.ROOT/derive.OPERATOR).read_bytes());cls.original=json.loads((derive.ROOT/cls.op['source_operator']).read_bytes())
    def test_complete_original_cohort_preserved_without_retrieval(self):
        r=self.report;self.assertEqual(r['counts']['cases'],14);self.assertEqual({c['entity_id'] for c in r['cases']},{'current:guinea'});self.assertEqual({c['snapshot_time_utc'] for c in r['cases']},set(self.original['snapshot_times_utc']));self.assertEqual(len({(c['section_id'],c['snapshot_time_utc']) for c in r['cases']}),14);self.assertEqual(r['counts']['new_ocean_field_requests'],0);self.assertLess(len(self.raw),2400000)
    def test_original_core_boundaries_reproduce_in_every_resolved_case(self):
        for c in self.report['cases']:
            self.assertFalse(c['core_reselected'])
            if c['columns']:self.assertEqual(sum(run['contains_original_core'] for col in c['columns'] for run in col['connected_depth_runs']),1)
    def test_no_physical_seasonal_or_volume_promotion(self):
        for c in self.report['cases']:
            for key in ['water_mass_classification_performed','named_current_axis_independently_validated','physical_current_bottom_established','annual_extrema_established']:self.assertFalse(c[key])
            for key in ['physical_thickness_m','width_m','cross_section_area_m2','volume_m3']:self.assertIsNone(c[key])
        self.assertEqual(self.report['counts']['new_reference_inventory_rows'],0);self.assertEqual(self.report['counts']['volume_estimates'],0)
    def test_geometry_rotation_and_original_diagnosis_tampering_rejected(self):
        f=self.op['section_files'][0];source=json.loads((derive.ROOT/f).read_bytes());config={**self.original,**self.original['currents'][source['entity_id']]}
        for key,value in [('component_bearing_degrees_true',0),('source_returned_timestamp_utc','2022-01-16T00:00:00Z'),('maximum_nearest_longitude_distance_km',999)]:
            bad=copy.deepcopy(source);bad[key]=value
            with self.assertRaises(ValueError):derive.curtain(bad,config,f)
        bad=copy.deepcopy(source);bad['diagnosis']['selected_column_index']=0
        with self.assertRaises(ValueError):derive.curtain(bad,config,f)
    def test_surface_connectivity_is_native_topology_only(self):
        for c in self.report['cases']:
            self.assertEqual(c['native_surface_seed_connected'],any(run['native_depth_indices_inclusive'][0]==0 for col in c['columns'] for run in col['connected_depth_runs']))
    def test_validated_topology_not_reimplemented_or_retuned(self):
        import derive_barents_makassar_velocity_curtains_v1 as frozen
        self.assertIs(derive.component,frozen.component);self.assertIs(derive.runs,frozen.runs)
        self.assertEqual(derive.component([0,10],[[.2,.1],[.1,.3],[0,0]],0,0),{(0,0)})


if __name__=='__main__':unittest.main()
