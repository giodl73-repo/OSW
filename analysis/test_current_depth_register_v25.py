"""Verify historical instrument depth and regime-limited ADCP reach semantics."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v24 as previous
import build_current_depth_register_v25 as depth


class JutlandGuianaDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][307:];cls.jutland,cls.guiana=cls.new
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:307],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':309,'identities_with_scoped_depth_reference':94,'identities_not_yet_assessed':17,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_jutland_record_depth_not_neighbor_record_or_publication_year(self):
        self.validate(self.jutland);self.assertEqual(self.jutland['lower_bound_m'],19)
        self.reject(self.jutland,[('lower_bound_m',40),('source_station_id','44'),('reported_current_meter_depth_m',40),('source_figure_panel','Figure6_no_motion_layer'),('survey_year',1989),('phase_label','boreal_winter'),('temporal_operator','monthly_climatology'),('source_access_scope','original_pdf_pixels')])

    def test_jutland_original_station_coordinates_retained(self):
        self.assertEqual(self.jutland['source_station_position_degrees_minutes'],{'latitude_north':[57,28.8],'longitude_east':[8,11.8]})
        self.reject(self.jutland,[('source_station_position_degrees_minutes',{'latitude_north':[57,50.1],'longitude_east':[10,51.9]}),('entity_id','current:norwegian-coastal')])

    def test_guiana_deepest_valid_sample_not_bottom_or_mounting_depth(self):
        self.validate(self.guiana);self.assertEqual(self.guiana['lower_bound_m'],118)
        self.assertEqual(self.guiana['valid_ADCP_depth_range_m'],[13,118])
        self.assertLess(118,self.guiana['ADCP_mounting_depth_m']);self.assertLess(130,self.guiana['source_station_water_depth_m'])
        self.reject(self.guiana,[('lower_bound_m',130),('lower_bound_m',150.3),('valid_ADCP_depth_range_m',[0,150.3]),('sampling_limit_is_flow_boundary',True),('source_station_id','M3'),('ADCP_cell_height_m',30),('metric','lower_flow_boundary_depth')])

    def test_guiana_regime_not_permanent_or_opposite_undercurrent(self):
        self.assertEqual(self.guiana['mooring_record_window'],{'start_date':'2003-10-06','end_date':'2004-02-18'})
        self.reject(self.guiana,[('current_persistence_interpretation','permanent_annual_current'),('phase_label','whole_record_northwestward'),('regime_transition_description','fixed_1_December_2003'),('mooring_record_window',{'start_date':'2007-02-24','end_date':'2007-02-24'}),('source_current_name','Guiana_Coastal_Undercurrent'),('branch_section_scope','whole_North_Brazil_Current'),('entity_id','current:north-brazil')])

    def test_bound_and_calendar_support_not_promoted(self):
        for row in self.new:
            self.reject(row,[('lower_bound_operator','>'),('lower_bound_exclusive',True),('section_sampling_month','2003-12'),('calendar_months',[12,1,2]),('climatology_years',[2003,2004])])

    def test_no_whole_geometry_annual_extrema_or_unsupported_joins(self):
        for row in self.new:
            self.reject(row,[('upper_boundary_m',13),('lower_boundary_m',118),('thickness_m',105),('uncertainty_m',3),('annual_range_m',[19,118]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_original_source_semantics_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows[self.guiana['id']]['valid_ADCP_depth_range_m']),[13,118])
        self.assertEqual(json.loads(rows[self.jutland['id']]['source_station_position_degrees_minutes']),self.jutland['source_station_position_degrees_minutes'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual([r['actual_original_pixels_viewed'] for r in source['source_reviews']],[False,False])
        self.assertEqual(len(source['deferred_candidates']),2)
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
