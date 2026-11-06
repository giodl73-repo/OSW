"""Guard EAC source-paired depths/areas and coherent-jet scope."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_register_v35 as previous
import build_current_depth_register_v36 as depth


class EACMeanMaskSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][327:]
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,row,changes):
        for key,value in changes:
            changed=copy.deepcopy(row);changed[key]=value
            with self.subTest(id=row['id'],key=key),self.assertRaises(ValueError):
                depth.validate_reference(changed,self.ids,self.metrics);depth.validate_context(changed)

    def test_previous327_normalized_refs_and_coverage_preserved(self):
        self.assertEqual(self.data['evidence'][:327],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':332,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.data['metadata_correction_count'],3)

    def test_five_source_depth_area_pairs_remain_at_their_sections(self):
        self.assertEqual([(r['section_latitude_degrees_north'],r['approximate_value_m'],r['source_cross_section_area_km2']) for r in self.rows],[(-27.5,820,97.1),(-30.3,1010,104.2),(-32.3,1190,141.3),(-33.9,980,114.5),(-36.2,1250,132.3)])
        for row in self.rows:self.assertEqual(row['metric'],'core_lower_boundary_depth')

    def test_signed_mean_mask_not_instantaneous_or_positive_return_flow(self):
        for row in self.rows:
            self.assertEqual(row['source_signed_alongshore_isotach_m_s'],-0.05)
            self.assertEqual(row['core_definition']['geometry_statistic'],'fixed_mask_of_long_term_mean_velocity_not_average_of_instantaneous_masks')
            self.reject(row,[('source_signed_alongshore_isotach_m_s',0.05),('core_definition',{'kind':'instantaneous_velocity_mask'}),('temporal_operator','mean_of_instantaneous_core_masks')])

    def test_offshore_distance_is_not_width_or_rectangle(self):
        for row in self.rows:
            self.assertFalse(row['source_distance_offshore_is_current_width'])
            self.reject(row,[('source_distance_offshore_is_current_width',True),('same_source_width_reference_id','offshore_distance_as_width'),('source_cross_section_area_km2',row['source_distance_offshore_km']*row['approximate_value_m']/1000),('metric','reported_vertical_thickness'),('thickness_m',row['approximate_value_m'])])

    def test_only_two_sections_inside_selected_route_gate(self):
        self.assertEqual([r['reference_route_projection_eligible'] for r in self.rows],[True,True,False,False,False])
        route=json.loads((depth.ROOT/'research/east-australian-reference-path-candidate.json').read_bytes())
        low=min(p[1] for p in route['coordinates_lon_lat']);high=max(p[1] for p in route['coordinates_lon_lat'])
        for row in self.rows:self.assertEqual(row['reference_route_projection_eligible'],low<=row['section_latitude_degrees_north']<=high)
        for row in self.rows[2:]:self.reject(row,[('reference_route_projection_eligible',True)])

    def test_exact_reported_model_period_not_forcing_or_observing_window(self):
        for row in self.rows:
            self.assertEqual(row['model_simulation_period'],{'start':'1994-01-01','end':'2016-10-01'})
            self.reject(row,[('model_simulation_period',{'start':'1994-01-01','end':'2015-12-31'}),('model_product','BRAN3p5'),('source_model_grid_rotation_clockwise_degrees',0),('volume_eligible',True),('physical_state_join_eligible',True),('annual_range_m',[820,1250])])

    def test_json_csv_and_unchanged_member_lookup(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        exported=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-5:]
        for row,out in zip(self.rows,exported):
            self.assertEqual(float(out['source_cross_section_area_km2']),row['source_cross_section_area_km2'])
            self.assertEqual(json.loads(out['model_simulation_period']),row['model_simulation_period'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());retained=source['retained_member_index']
        self.assertEqual(hashlib.sha256((depth.ROOT/retained['file']).read_bytes()).hexdigest(),retained['sha256'])
        index=json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes());self.assertEqual(index['counts']['distinct_member_depth_references'],46)
        for parent in index['records']:
            self.assertNotIn('current:east-australian',[m['entity_id'] for m in parent['members']])


if __name__=='__main__':unittest.main()
