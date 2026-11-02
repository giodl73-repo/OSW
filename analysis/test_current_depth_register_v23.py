"""Verify source table values and exact Antarctic composite width/depth joins."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v22 as previous
import build_current_depth_register_v23 as depth


class AntarcticCompositeDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][298:]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(section=row['hydrographic_section_number'],field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_preserve_all_previous_evidence_and_identities(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:298],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':305,'identities_with_scoped_depth_reference':90,'identities_not_yet_assessed':21,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_all_seven_original_table_means_and_spatial_ranges(self):
        expected=[(125.7,[108,161]),(137.3,[109,161]),(164.6,[117,215]),(193.9,[143,230]),(184.3,[109,254]),(183.6,[92,230]),(218.0,[158,267])]
        self.assertEqual(len(self.new),7)
        for n,(row,(mean,interval)) in enumerate(zip(self.new,expected),1):
            self.validate(row);self.assertEqual(row['hydrographic_section_number'],n)
            self.assertEqual((row['approximate_value_m'],row['source_spatial_depth_range_m']),(mean,interval))
            self.reject(row,[('approximate_value_m',400),('source_spatial_depth_range_m',[0,400]),('section_depth_statistic','maximum_depth'),('source_spatial_depth_range_interpretation',None)])

    def test_width_joins_cannot_cross_sections_or_change_pins(self):
        widths=json.loads((depth.ROOT/depth.WIDTHS).read_bytes())['measurements']
        for n,row in enumerate(self.new,1):
            pointer=int(row['source_width_reference_pointer'].split('/')[-1]);width=widths[pointer]
            self.assertEqual(width['id'],row['same_source_width_reference_id']);self.assertEqual(width['original_regional_context']['section_number'],n)
            self.reject(row,[('same_source_width_reference_id',None),('same_source_width_reference_id','antarctic-coastal-schubert-2021-section-99'),('source_width_reference_pointer','/measurements/0'),('source_width_reference_sha256','0'*64),('source_audit_sha256','0'*64),('source_audit_pointer','/measurements/99'),('hydrographic_section_number',8)])

    def test_layer_and_lateral_operators_not_reference_depth_or_wrong_current(self):
        row=self.new[0]
        self.reject(row,[('integration_base_salinity_psu',34),('integration_base_is_fixed_depth',True),('geostrophic_reference_depth_m',200),('reference_is_flow_boundary',True),('offshore_edge_fraction_of_center_integrated_velocity',0.5),('center_selection','maximum_local_velocity'),('shoreward_boundary','shelf_break'),('metric','lower_flow_boundary_depth'),('entity_id','current:antarctic-slope')])

    def test_table_counts_and_section_six_discrepancy_preserved(self):
        expected=[(183,221,404),(494,67,561),(1040,145,1185),(753,243,996),(348,168,516),(117,150,267),(147,59,206)]
        for row,(winter,summer,total) in zip(self.new,expected):
            self.assertEqual(row['source_profile_counts'],{'winter_profiles':winter,'summer_profiles':summer,'total_profiles':total})
            self.assertEqual(winter+summer,total)
        self.assertEqual([r['sampling_dominant_season'] for r in self.new],['summer','winter','winter','winter','winter','summer','winter'])
        self.assertTrue(self.new[5]['sampling_prose_discrepancy'])
        self.reject(self.new[5],[('sampling_prose_discrepancy',False),('sampling_dominant_season','winter'),('source_profile_counts',{'winter_profiles':150,'summer_profiles':117,'total_profiles':267})])

    def test_composites_not_synoptic_seasonal_or_independent_repeats(self):
        for row in self.new:
            self.reject(row,[('temporal_operator','monthly_climatology'),('source_profile_period_descriptions',['2005–2015 continuous']),('section_sampling_month','2015-06'),('climatology_years',[2005,2015]),('phase_label','winter'),('calendar_months',[4,5,6,7,8,9]),('independent_observation_count_claimed',True)])

    def test_join_does_not_authorize_area_volume_or_whole_geometry(self):
        for row in self.new:
            self.reject(row,[('mean_depth_weighting_independently_recovered',True),('cross_section_area_eligible',True),('rectangle_cross_section_inferred',True),('exact_boundary_coordinates_available',True),('thickness_m',200),('lower_boundary_m',200),('upper_boundary_m',0),('uncertainty_m',20),('annual_range_m',[92,267]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True)])

    def test_json_csv_and_source_pins_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        for row in self.new:
            self.assertEqual(json.loads(rows[row['id']]['source_spatial_depth_range_m']),row['source_spatial_depth_range_m'])
            self.assertEqual(rows[row['id']]['same_source_width_reference_id'],row['same_source_width_reference_id'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for path,digest in source['source_input_sha256'].items():self.assertEqual(self.data['input_sha256'][path],digest)
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
