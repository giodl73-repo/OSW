"""Verify inclusive reach and seasonal water-mass component distinctions."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v21 as previous
import build_current_depth_register_v22 as depth


class AustralianAndPacificDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][293:]
        cls.sac,cls.npc=cls.new[:2];cls.interfaces=cls.new[2:]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:293],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':298,'identities_with_scoped_depth_reference':89,'identities_not_yet_assessed':22,'whole_route_depth_profiles':0,'volume_estimates':0})
        aleutian=next(r for r in self.data['records'] if r['entity_id']=='current:aleutian')
        self.assertEqual(aleutian['status'],'not_yet_assessed')

    def test_south_australian_reach_not_terminal_or_neighbor_branch(self):
        self.validate(self.sac);self.assertEqual(self.sac['lower_bound_m'],200)
        self.reject(self.sac,[('lower_bound_m',250),('lower_bound_m',300),('lower_bound_exclusive',True),('lower_bound_operator','>'),('metric','lower_flow_boundary_depth'),('entity_id','current:leeuwin'),('entity_id','current:zeehan'),('source_reported_speed_max_m_s',50),('phase_label','austral_winter')])

    def test_north_pacific_nonzero_speed_not_aleutian_or_decay_scale(self):
        self.validate(self.npc);self.assertEqual(self.npc['lower_bound_m'],500)
        self.reject(self.npc,[('entity_id','current:aleutian'),('entity_id','current:alaskan-stream'),('lower_bound_m',1000),('lower_bound_exclusive',True),('lower_bound_operator','>'),('metric','reported_vertical_scale_length'),('source_reported_speed_fraction_of_surface',0.367879),('depth_basis','exponential_decay_length'),('exact_source_section_recovered',True),('source_current_naming_convention','North_Pacific_equals_Subarctic')])

    def test_interface_seasons_and_local_exception_not_swapped(self):
        for row,phase,value,region in zip(self.interfaces,['austral_winter','austral_summer','austral_summer'],[300,250,150],['southern_Australian_margin','southern_Australian_margin','upwelling_regions_and_western_Tasmania']):
            self.validate(row);self.assertEqual((row['phase_label'],row['approximate_value_m'],row['region_name']),(phase,value,region))
            self.reject(row,[('approximate_value_m',400),('phase_label','austral_autumn'),('region_name','entire_western_and_southern_route'),('metric','lower_flow_boundary_depth'),('depth_basis','measured_zero_flow_boundary')])
        self.reject(self.interfaces[2],[('region_name','southern_Australian_margin'),('approximate_value_m',250)])

    def test_component_scope_and_conditional_summer_context_retained(self):
        for row in self.interfaces:
            self.reject(row,[('water_mass_component','subantarctic_mode_water'),('interface_water_masses',['subtropical_Leeuwin_System']),('branch_section_scope','all_5500km_system'),('entity_id','current:flinders'),('source_access_scope','original_full_pdf_pixels')])
        self.reject(self.interfaces[0],[('reference_route_phase_relation','conditional_outside_catalog_winter_phase')])
        for row in self.interfaces[1:]:
            self.reject(row,[('reference_route_phase_relation','partial_southern_component_in_catalog_winter')])

    def test_no_invented_dates_route_projection_or_common_model_mean(self):
        for row in self.new:
            self.reject(row,[('reference_route_projection_eligible',True),('section_sampling_month','2020-01'),('calendar_months',[6,7,8]),('climatology_years',[1993,2001])])

    def test_no_geometry_volume_or_annual_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',300),('lower_boundary_m',300),('upper_boundary_m',0),('uncertainty_m',50),('annual_range_m',[150,300]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_reproduce_and_source_access_retained(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(rows[self.npc['id']]['source_reported_speed_fraction_of_surface'],'0.5')
        self.assertEqual(json.loads(rows[self.interfaces[0]['id']]['interface_water_masses']),self.interfaces[0]['interface_water_masses'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual([r['actual_original_pixels_viewed'] for r in source['source_reviews']],[True,True,False])
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
