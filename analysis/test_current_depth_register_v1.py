"""Source identity and scientific promotion guards for the depth register."""
import copy
import hashlib
import json
import unittest
import build_current_depth_register_v1 as depth


class DepthRegisterTests(unittest.TestCase):
    def setUp(self):
        self.data = depth.build()
        self.row = copy.deepcopy(self.data['evidence'][0])
        self.identities = {r['entity_id'] for r in self.data['records']}
        self.metrics = json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def test_complete_identity_inventory_and_explicit_gaps(self):
        original = json.loads((depth.ROOT/depth.INVENTORY).read_bytes())
        self.assertEqual(self.identities, {r['entity_id'] for r in original['records']})
        self.assertEqual(self.data['counts'], {'identities':111, 'depth_references':4, 'identities_with_scoped_depth_reference':3, 'identities_not_yet_assessed':108, 'whole_route_depth_profiles':0, 'volume_estimates':0})
        for row in self.data['records']:
            self.assertIsNone(row['whole_route_depth_m'])
            self.assertIsNone(row['volume_km3'])
            self.assertEqual(row['status']=='not_yet_assessed', not bool(row['depth_reference_ids']))

    def test_retained_outputs_and_source_pointers(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()), self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(), depth.csv_bytes(self.data))
        source = json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.data['evidence']:
            raw = source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual({k: row[k] for k in raw}, raw)
            self.assertEqual(row['source_sha256'], hashlib.sha256((depth.ROOT/depth.SOURCE).read_bytes()).hexdigest())

    def test_depth_reach_does_not_become_thickness_or_volume(self):
        for field,value in [('thickness_m',450),('upper_boundary_m',0),('lower_boundary_m',450),('volume_eligible',True),('whole_current_representative',True),('physical_state_join_eligible',True)]:
            with self.subTest(field=field):
                row=copy.deepcopy(self.row);row[field]=value
                with self.assertRaises(ValueError): depth.validate_reference(row,self.identities,self.metrics)

    def test_seasonal_summary_is_not_an_annual_envelope(self):
        north=[r for r in self.data['evidence'] if r['entity_id']=='current:northern-mediterranean']
        self.assertEqual({r['phase_label']:r['approximate_value_m'] for r in north},{'winter':450,'summer':250})
        for field,value in [('annual_range_m',[250,450]),('calendar_months',[12,1,2]),('seasonal_playback_eligible',True),('annual_extrema_eligible',True)]:
            row=copy.deepcopy(north[0]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_reference(row,self.identities,self.metrics)

    def test_pressure_invalid_values_and_unknown_owner_are_rejected(self):
        for field,value in [('unit','dbar'),('approximate_value_m',-1),('approximate_value_m',True),('approximate_value_m',float('nan')),('entity_id','current:not-in-inventory'),('metric','ocean_bottom_depth')]:
            row=copy.deepcopy(self.row);row[field]=value
            with self.assertRaises(ValueError):depth.validate_reference(row,self.identities,self.metrics)

    def test_section_year_conflict_and_density_boundary_remain_explicit(self):
        azores=[r for r in self.data['evidence'] if r['entity_id'] in ['current:azores','current:azores-countercurrent']]
        for row in azores:
            self.assertEqual(row['observed_period'],{'start':'2009-10-26','end':'2009-11-01'})
            self.assertIn('2010',row['qualification'])
            self.assertIn('27.975',row['source_definition'])
            self.assertIsNone(row['thickness_m'])


if __name__=='__main__':unittest.main()
