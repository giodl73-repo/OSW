"""Check main-jet identity, spatial core semantics and archive fit support."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v25 as previous
import build_current_depth_register_v26 as depth


class PacificSouthernCoreDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][309:]
        cls.west,cls.east,cls.central=cls.new
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_and_coverage_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:309],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':312,'identities_with_scoped_depth_reference':95,'identities_not_yet_assessed':16,'whole_route_depth_profiles':0,'volume_estimates':0})
        owners=[r for r in self.data['records'] if r['entity_id']=='current:pacific-south-subsurface-countercurrent']
        self.assertEqual(owners[0]['depth_reference_ids'],[r['id'] for r in self.new])

    def test_core_depths_are_scoped_spatial_values(self):
        self.assertEqual([r['approximate_value_m'] for r in self.new],[300,150,200])
        for row in self.new:
            self.validate(row)
            self.reject(row,[('metric','lower_flow_boundary_depth'),('metric','reported_vertical_thickness'),('range_m',[150,300]),('annual_range_m',[150,300]),('upper_boundary_m',150),('lower_boundary_m',300),('thickness_m',150),('uncertainty_m',100)])

    def test_western_regional_result_not_exact_origin_or_northern_jet(self):
        self.assertIsNone(self.west['section_longitude_degrees_east'])
        self.reject(self.west,[('approximate_value_m',325),('source_current_branch','NSCC'),('section_longitude_degrees_east',155),('section_latitude_degrees_north',3),('branch_section_scope','whole_Pacific_current')])

    def test_eastern_result_not_introductory_longitude_or_secondary_jet(self):
        self.assertEqual(self.east['section_longitude_degrees_east'],-95)
        self.assertIsNone(self.east['section_latitude_degrees_north'])
        self.reject(self.east,[('section_longitude_degrees_east',-110),('section_latitude_degrees_north',-6),('source_current_branch','secondary_SSCC'),('sampling_time_space_aliasing_possible',False),('temporal_operator','synoptic_section')])

    def test_central_main_jet_not_neighboring_cores(self):
        self.assertEqual((self.central['section_longitude_degrees_east'],self.central['section_latitude_degrees_north']),(-140,-4.5))
        self.reject(self.central,[('approximate_value_m',250),('section_latitude_degrees_north',-7),('section_latitude_degrees_north',4),('approximate_value_m',110),('entity_id','current:pacific-equatorial-undercurrent'),('source_current_branch','secondary_SSCC')])

    def test_reconstructed_mean_retains_pooling_and_temporal_support(self):
        self.assertEqual(self.central['archive_observation_window'],{'start_month':'1985-06','end_month':'2000-12'})
        self.reject(self.central,[('archive_observation_window',{'start_month':'2002-01','end_month':'2002-12'}),('fit_longitude_neighborhood_degrees',0),('fit_minimum_local_sections_exclusive',0),('annual_harmonic_included',False),('SOI_term_included',False),('temporal_operator','direct_instantaneous_ADCP')])
        for row in self.new:
            self.reject(row,[('section_sampling_month','1995-06'),('calendar_months',[6]),('climatology_years',[1985,2000])])

    def test_no_unsupported_geometry_independence_or_seasonal_playback(self):
        for row in self.new:
            self.reject(row,[('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True),('source_figure_pixels_used_for_value',True)])

    def test_json_csv_and_source_access_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows[self.central['id']]['archive_observation_window']),self.central['archive_observation_window'])
        self.assertEqual(rows[self.east['id']]['section_longitude_degrees_east'],'-95')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual([r['actual_original_pixels_viewed'] for r in source['source_reviews']],[False,True])
        self.assertEqual(len(source['deferred_candidates']),3)
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
