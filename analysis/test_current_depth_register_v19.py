"""Guard geostrophic reach, transport domains, scale distances and current-name distinctions."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v18 as previous
import build_current_depth_register_v19 as depth


class IndianDepthQuantityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][284:]
        cls.rows={r['id']:r for r in cls.new};cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:284],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':287,'identities_with_scoped_depth_reference':81,'identities_not_yet_assessed':30,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_indian_sec_reach_not_terminal_depth_or_direct_current(self):
        row=self.rows['indian-sec-premchand-1976-may-june1965-reach'];self.validate(row)
        self.assertIsNone(row['approximate_value_m']);self.assertEqual(row['lower_bound_m'],500)
        self.reject(row,[('lower_bound_operator','>'),('lower_bound_exclusive',True),('lower_bound_m',1000),('geostrophic_reference_pressure_dbar',500),('pressure_to_depth_conversion_performed',True),('evidence_kind','published_observed_direct_velocity'),('window_role','exact_section_dates'),('campaign_window',{'start_date':'1976-04-25','end_date':'1976-06-20'}),('section_sampling_month','1965-05')])

    def test_south_indian_transport_limit_kept_distinct(self):
        row=self.rows['south-indian-stramma-1992-upper1000-transport'];self.validate(row)
        self.assertEqual(row['approximate_value_m'],1000)
        self.reject(row,[('metric','reported_vertical_extent'),('metric','lower_flow_boundary_depth'),('approximate_value_m',3500),('depth_basis','measured_current_bottom'),('source_access_scope','original_full_paper_pixels'),('entity_id','current:indian-south-equatorial-countercurrent')])

    def test_vertical_scale_has_distance_datum_and_no_assumed_formula(self):
        row=self.rows['west-australian-andrews-1977-reported-scale'];self.validate(row)
        self.assertEqual(row['vertical_datum'],'not_applicable_scale_distance')
        self.reject(row,[('vertical_datum','local_sea_surface_positive_down'),('metric','core_depth'),('metric','reported_vertical_extent'),('metric','reported_vertical_thickness'),('source_scale_definition_recovered',True),('exponential_decay_assumed',True)])

    def test_wac_historical_regional_scope_and_survey_support(self):
        row=self.rows['west-australian-andrews-1977-reported-scale']
        self.reject(row,[('survey_years',[1977,1977]),('source_naming_convention','entire_modern_offshore_gyre_return'),('branch_section_scope','whole_offshore_route'),('calendar_months',[12,1,2]),('source_access_scope','full_operational_definition_recovered')])

    def test_distinct_sicc_not_joined_to_equatorial_secc(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        excluded=source['excluded_or_deferred_source_candidates']
        self.assertEqual(excluded[0]['decision'],'DO_NOT_JOIN_DISTINCT_GEOGRAPHIC_CURRENT')
        self.assertEqual(excluded[0]['candidate_catalog_entity'],'current:indian-south-equatorial-countercurrent')
        target=next(r for r in self.data['records'] if r['entity_id']=='current:indian-south-equatorial-countercurrent')
        self.assertEqual(target['depth_reference_ids'],[])
        self.assertFalse(any('2014JC010076' in r['source_url'] for r in self.new))
        self.assertEqual(excluded[1]['decision'],'DEFER_AMBIGUOUS_DEPTH_SHORTHAND')

    def test_no_unreviewed_geometry_volume_or_repeat_claim(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',370),('lower_boundary_m',500),('annual_range_m',[370,1000]),('uncertainty_m',50),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_source_facts_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(rows['west-australian-andrews-1977-reported-scale']['vertical_datum'],'not_applicable_scale_distance')
        self.assertEqual(rows['west-australian-andrews-1977-reported-scale']['exponential_decay_assumed'],'False')
        self.assertEqual(rows['indian-sec-premchand-1976-may-june1965-reach']['lower_bound_operator'],'>=')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
