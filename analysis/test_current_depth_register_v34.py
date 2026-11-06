"""Guard Atlantic EUC observation/hindcast/spinup separation."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v33 as previous
import build_current_depth_register_v34 as depth


class AtlanticEUCMeanCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.rows=cls.data['evidence'][323:]
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,row,changes):
        for key,value in changes:
            changed=copy.deepcopy(row);changed[key]=value
            with self.subTest(row=row['id'],key=key),self.assertRaises(ValueError):
                depth.validate_reference(changed,self.ids,self.metrics);depth.validate_context(changed)

    def test_previous323_and_coverage_preserved(self):
        self.assertEqual(self.data['evidence'][:323],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':327,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_observed_hindcast_and_spinup_depths_remain_distinct(self):
        self.assertEqual([(r['section_longitude_degrees_east'],r['approximate_value_m']) for r in self.rows],[(-35,100),(-35,70),(-35,100),(-10,50)])
        self.assertEqual([r['model_product'] for r in self.rows],[None,'FLAME_Hormann2007','SPFLAME_Hormann2007','FLAME_Hormann2007'])
        for row in self.rows:
            self.reject(row,[('metric','reported_vertical_extent'),('core_definition',{'kind':'transport_selected_depth'}),('evidence_kind','published_observed_instantaneous_core')])

    def test_hindcast_years_not_spinup_or_observed_period(self):
        for index in [1,3]:
            self.assertEqual(self.rows[index]['model_time_basis'],{'kind':'interannually_forced_hindcast_monthly_mean','output_years':[1990,2002]})
            self.reject(self.rows[index],[('model_time_basis',{'kind':'hindcast','output_years':[1987,2003]}),('model_product','SPFLAME_Hormann2007')])
        self.assertEqual(self.rows[2]['model_time_basis']['analysis_window'],'last_two_spinup_years')
        self.assertIsNone(self.rows[2]['model_time_basis']['calendar_years']);self.assertIsNone(self.rows[0]['model_time_basis'])
        self.reject(self.rows[2],[('model_time_basis',self.rows[1]['model_time_basis'])])

    def test_sixteen_section_observed_mean_not_fifteen_transport_subset(self):
        observed=self.rows[0];self.assertEqual(observed['source_ship_section_count'],16)
        self.assertEqual(observed['source_ship_section_year_bounds'],[1990,2006])
        self.assertEqual(observed['surface_mean_completion'],'above30m_linear_interpolation_to_surface_drifter_climatology')
        self.reject(observed,[('source_ship_section_count',15),('source_ship_section_year_bounds',[1990,2002]),('surface_mean_completion','observed_continuously_to_sea_surface'),('observed_period',{'start':'1990-01-01','end':'2006-12-31'})])

    def test_exact_model_core_latitude_not_inferred_from_equatorial_section(self):
        self.assertEqual(self.rows[0]['section_latitude_degrees_north'],0)
        for index in [1,2,3]:
            self.assertIsNone(self.rows[index]['section_latitude_degrees_north'])
            self.reject(self.rows[index],[('section_latitude_degrees_north',0),('core_latitude_relation','exactly_on_equator')])

    def test_no_transport_domain_thickness_uncertainty_or_volume_admission(self):
        for row in self.rows:
            self.reject(row,[('upper_boundary_m',30),('lower_boundary_m',300),('thickness_m',270),('uncertainty_m',10),('annual_range_m',[50,100]),('same_source_width_reference_id','unrelated_width'),('volume_eligible',True),('whole_current_representative',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True)])

    def test_json_csv_source_review_and_updated_member_ownership(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        exported=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-4:]
        self.assertEqual(exported[0]['source_ship_section_count'],'16')
        self.assertEqual(json.loads(exported[1]['model_time_basis'])['output_years'],[1990,2002])
        self.assertEqual(exported[1]['section_latitude_degrees_north'],'')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());self.assertFalse(source['source_reviews'][0]['actual_original_pixels_viewed'])
        index=depth.build_member_index(self.data);self.assertEqual(json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes()),index)
        self.assertEqual(index['counts']['distinct_member_depth_references'],46)
        ids={r['id'] for r in self.rows}
        self.assertEqual([r['entity_id'] for r in index['records'] if ids.intersection(r['unique_linked_reference_ids'])],['current:equatorial-undercurrent'])


if __name__=='__main__':unittest.main()
