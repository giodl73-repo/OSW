"""Verify regional Spitsbergen scope and discovery without parent measurements."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import build_current_depth_register_v29 as previous
import build_current_depth_register_v30 as depth


class SpitsbergenMemberDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][315]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']
        cls.index=depth.build_member_index(cls.data)

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,changes):
        for k,v in changes:
            changed=copy.deepcopy(self.row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_and_direct_coverage_counts(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:315],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':316,'identities_with_scoped_depth_reference':99,'identities_not_yet_assessed':12,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.validate(self.row)

    def test_regional_below50_bound_not_full_WSC_or_current_bottom(self):
        self.reject([('lower_bound_m',300),('lower_bound_m',550),('lower_bound_m',1000),('lower_bound_operator','>='),('lower_bound_exclusive',False),('metric','lower_flow_boundary_depth'),('current_identity_assignment','global_WSC_synonym'),('source_current_name','all_West_Spitsbergen_Current'),('lower_boundary_m',300),('thickness_m',277),('source_site_id','Storfjorden_entrance')])

    def test_2016_survey_not_2017_instruments_or_exact_profile_position(self):
        self.assertEqual(self.row['reported_velocity_sampling_domain_m'],[23,300])
        self.reject([('survey_window',{'start':'2017-07-21T06:40:00Z','end':'2017-07-23T06:12:00Z'}),('reported_velocity_sampling_domain_m',[28,550]),('source_depth_bin_spacing_m',16),('profile_averaging_minutes',15),('site_coordinate_role','exact_velocity_profile'),('section_sampling_window',{'start':'2016-06-21','end':'2016-06-23'}),('section_latitude_degrees_north',76.438),('calendar_months',[6]),('climatology_years',[2016,2017])])

    def test_no_unsupported_route_volume_annual_envelope_or_join(self):
        self.reject([('reference_route_projection_eligible',True),('annual_range_m',[50,550]),('uncertainty_m',4),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_member_lookup_coverage_and_shared_reference_deduplication(self):
        self.assertEqual(self.index['counts'],{'parents':9,'families':8,'systems':1,'member_links':23,'distinct_member_identities':20,'distinct_member_depth_references':37,'parents_with_any_member_depth_evidence':9,'parents_with_all_declared_members_referenced':8,'new_measurements':0,'whole_route_profiles':0,'volumes':0})
        unique={ref for row in self.index['records'] for ref in row['unique_linked_reference_ids']}
        self.assertEqual(len(unique),37)
        self.assertGreater(sum(row['linked_reference_count'] for row in self.index['records']),len(unique))
        for row in self.index['records']:
            self.assertIsNone(row['aggregation_operator']);self.assertIsNone(row['parent_depth_m']);self.assertIsNone(row['parent_depth_range_m']);self.assertIsNone(row['parent_volume_km3'])
            self.assertFalse(row['whole_route_profile_established']);self.assertFalse(row['volume_eligible']);self.assertEqual(row['new_measurement_count'],0)

    def test_missing_member_and_identity_exclusions_remain_visible(self):
        parents={r['entity_id']:r for r in self.index['records']}
        sec=parents['current:south-equatorial']
        self.assertEqual(sec['missing_member_depth_entity_ids'],['current:atlantic-south-equatorial'])
        self.assertEqual(next(m for m in sec['members'] if m['entity_id']=='current:atlantic-south-equatorial')['depth_reference_ids'],[])
        gs=parents['current:gulf-stream-system']
        self.assertEqual([m['entity_id'] for m in gs['members']],['current:florida','current:gulf-stream','current:north-atlantic'])
        self.assertEqual([m['identity_level'] for m in gs['members']],['segment','current','system'])
        self.assertNotIn('current:monsoon',[m['entity_id'] for m in parents['current:north-equatorial']['members']])
        self.assertNotIn('current:pacific-south-subsurface-countercurrent',[m['entity_id'] for m in parents['current:south-equatorial-undercurrent']['members']])

    def test_reference_owner_or_unknown_reference_mutations_rejected(self):
        for replacement in ['unreviewed_reference',next(r['id'] for r in self.data['evidence'] if r['entity_id']=='current:atlantic-north-equatorial-countercurrent')]:
            changed=copy.deepcopy(self.data)
            next(r for r in changed['records'] if r['entity_id']=='current:pacific-north-equatorial-countercurrent')['depth_reference_ids'].append(replacement)
            with self.subTest(reference=replacement),self.assertRaisesRegex(ValueError,'ownership'):depth.build_member_index(changed)

    def test_parent_scalar_promotion_and_membership_repin_required(self):
        for field,value in [('whole_route_depth_m',500),('annual_depth_range_m',[100,500]),('volume_km3',100)]:
            changed=copy.deepcopy(self.data)
            next(r for r in changed['records'] if r['entity_id']=='current:gulf-stream-system')[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'scalar parent'):depth.build_member_index(changed)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'research').mkdir()
            (root/depth.SOURCE).write_bytes((depth.ROOT/depth.SOURCE).read_bytes())
            raw=json.loads((depth.ROOT/depth.MEMBERS).read_bytes());raw['conventions'][-1]['members'].append('current:loop')
            (root/depth.MEMBERS).write_text(json.dumps(raw),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'pin mismatch'):depth.build_member_index(self.data,root)

    def test_register_csv_and_member_index_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        row=next(r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['id']==self.row['id'])
        self.assertEqual(json.loads(row['survey_window']),self.row['survey_window'])
        self.assertEqual(json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()),self.index)
        self.assertEqual(self.index['depth_register_sha256'],hashlib.sha256((depth.ROOT/depth.OUTPUT).read_bytes()).hexdigest())
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(source['references'][0],{k:self.row[k] for k in source['references'][0]})


if __name__=='__main__':unittest.main()
