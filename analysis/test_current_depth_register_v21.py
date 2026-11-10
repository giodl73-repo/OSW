"""Verify dominant-flow semantics, component attribution and retained evidence."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v20 as previous
import build_current_depth_register_v21 as depth


class AtlanticComponentDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][291:]
        cls.sac,cls.portugal=cls.new
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:291],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':293,'identities_with_scoped_depth_reference':86,'identities_not_yet_assessed':25,'whole_route_depth_profiles':0,'volume_estimates':0})
        for slug in ['south-atlantic','portugal']:
            record=next(r for r in self.data['records'] if r['entity_id']=='current:'+slug)
            self.assertEqual(record['status'],'scoped_depth_reference');self.assertEqual(len(record['depth_reference_ids']),1)

    def test_dominant_layer_not_terminal_boundary_or_quantified_fraction(self):
        self.validate(self.sac)
        self.reject(self.sac,[('approximate_value_m',1500),('metric','lower_flow_boundary_depth'),('dominant_flow_fraction_quantified',True),('depth_basis','observed_zero_velocity_boundary'),('branch_section_scope','whole_Atlantic_route'),('entity_id','current:brazil')])

    def test_reference_level_and_multicruise_support_remain_separate(self):
        self.assertEqual(self.sac['velocity_reference_depth_m'],1500)
        self.reject(self.sac,[('velocity_reference_depth_m',1000),('reference_is_flow_boundary',True),('source_cruise_months',['1998-01']),('continuous_temporal_coverage',True),('climatology_years',[1978,1993]),('section_sampling_month','1989-04'),('calendar_months',[12,1,2])])

    def test_portugal_subpolar_component_not_azores_or_full_thickness(self):
        self.validate(self.portugal);self.assertEqual(self.portugal['range_m'],[250,500])
        self.reject(self.portugal,[('range_m',[0,500]),('range_m',[100,250]),('range_m',[450,500]),('range_m',[0,559]),('water_mass_component','subtropical_ENACW'),('source_component_attribution_explicit',False),('entity_id','current:azores'),('metric','reported_vertical_thickness'),('branch_section_scope','Portugal_coastal_undercurrent')])

    def test_modern_setting_not_paleorecord_and_access_not_overstated(self):
        self.reject(self.portugal,[('context_time_basis','Marine_Isotope_Stage_47'),('section_sampling_month','2022-09'),('source_access_scope','original_pdf_pixels'),('phase_label','upwelling'),('calendar_months',[5,6,7,8,9,10])])

    def test_no_whole_geometry_volume_or_annual_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',1000),('lower_boundary_m',1000),('upper_boundary_m',0),('uncertainty_m',100),('annual_range_m',[250,1000]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_reproduce_and_new_metadata_round_trip(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows[self.sac['id']]['source_cruise_months']),self.sac['source_cruise_months'])
        self.assertEqual(rows[self.portugal['id']]['context_time_basis'],'modern_regional_setting_not_paleorecord')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertTrue(source['source_reviews'][0]['actual_original_pixels_viewed'])
        self.assertFalse(source['source_reviews'][1]['actual_original_pixels_viewed'])
        self.assertEqual(source['deferred_candidates'][0]['entity_id'],'current:atlantic-north-equatorial')
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
