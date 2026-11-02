"""Check historical name resolution without importing neighboring profiles."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v28 as previous
import build_current_depth_register_v29 as depth


class HistoricalAleutianDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][314]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,changes):
        for k,v in changes:
            changed=copy.deepcopy(self.row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_and_named_identity_inventory_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:314],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':315,'identities_with_scoped_depth_reference':98,'identities_not_yet_assessed':13,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.validate(self.row)

    def test_name_mapping_keeps_eastward_historical_convention(self):
        self.reject([('entity_id','current:north-pacific'),('source_current_name','Alaskan_Stream'),('source_name_mapping','westward_Alaskan_Stream'),('source_nomenclature_scope','all_North_Pacific_currents'),('source_figure_panel','Figure7b_North_Pacific_curve'),('source_figure_panel','Figure7b_Alaskan_Stream_curve')])

    def test_nonzero_presence_not_digitized_speed_or_exact_boundary(self):
        self.reject([('lower_bound_m',1000),('lower_bound_operator','>'),('lower_bound_exclusive',True),('figure_reading_depth_m',1000),('figure_reading_kind','digitized_zero_crossing'),('speed_digitization_performed',True),('source_speed_fraction_of_surface',0.5),('metric','lower_flow_boundary_depth'),('lower_boundary_m',500),('thickness_m',500)])

    def test_unlocated_undated_profile_cannot_be_projected_or_dated_to_publication(self):
        self.reject([('profile_location_recovered',True),('profile_observation_dates_recovered',True),('section_latitude_degrees_north',47),('section_longitude_degrees_east',160),('section_sampling_month','1975-09'),('climatology_years',[1955,1955]),('reference_route_projection_eligible',True),('route_scope_relationship','exact_route_station'),('temporal_operator','NORPAC1955_observed_section')])

    def test_profile_reference_level_not_assumed_from_general_methods(self):
        self.reject([('profile_geostrophic_reference_level_recovered',True),('geostrophic_reference_depth_m',1000),('geostrophic_reference_pressure_dbar',1000),('evidence_kind','direct_absolute_velocity_profile'),('calendar_months',[2])])

    def test_no_unsupported_width_join_volume_or_annual_geometry(self):
        self.reject([('annual_range_m',[500,1000]),('uncertainty_m',100),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_original_source_access_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        row=next(r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['id']==self.row['id'])
        self.assertEqual(row['source_current_name'],'Subarctic_Current')
        self.assertEqual(row['profile_geostrophic_reference_level_recovered'],'False')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());review=source['source_reviews'][0]
        self.assertTrue(review['actual_original_pixels_viewed']);self.assertEqual(review['actual_reviewed_page'],20)
        self.assertFalse(source['identity_audit']['name_match_is_geographic_profile_location'])
        self.assertEqual(source['references'][0],{k:self.row[k] for k in source['references'][0]})


if __name__=='__main__':unittest.main()
