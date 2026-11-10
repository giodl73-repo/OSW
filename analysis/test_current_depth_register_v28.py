"""Verify observed contour-presence reach without model or layer substitutions."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import build_current_depth_register_v27 as previous
import build_current_depth_register_v28 as depth


class IndianSECCDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][313]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,changes):
        for k,v in changes:
            changed=copy.deepcopy(self.row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_references_preserved_and_one_regional_owner_added(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:313],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':314,'identities_with_scoped_depth_reference':97,'identities_not_yet_assessed':14,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.validate(self.row)

    def test_inclusive_presence_bound_not_exact_bottom_or_sampling_limit(self):
        self.reject([('lower_bound_operator','>'),('lower_bound_exclusive',True),('lower_bound_m',115),('lower_bound_m',300),('lower_bound_m',75),('metric','lower_flow_boundary_depth'),('upper_boundary_m',25),('lower_boundary_m',75),('thickness_m',50)])

    def test_observed_panel_sign_and_labeled_depth_not_model_or_different_current(self):
        self.reject([('source_figure_panel','Figure1b_model_layer1'),('source_figure_panel','Figure3_100_150m_mean'),('figure_reading_kind','digitized_terminal_boundary'),('figure_reading_depth_m',115),('positive_zonal_velocity_direction','westward'),('figure_contour_interval_cm_s',1),('source_current_branch','equatorial_undercurrent'),('entity_id','current:indian-south-equatorial')])

    def test_approximate_eastern_section_not_exact_position_or_other_leg(self):
        self.assertEqual(self.row['section_nominal_longitude_degrees_east'],95)
        self.reject([('source_section_id','I8N_western_leg'),('section_nominal_longitude_degrees_east',80),('figure_reading_latitude_neighborhood_degrees_north',6),('figure_location_precision','exact_digitized_station'),('reference_route_projection_eligible',True),('route_scope_relationship','same_route_section')])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());audit=source['reference_route_scope_audit']
        route_path=audit['source_file'];self.assertEqual(self.data['input_sha256'][route_path],audit['source_sha256'])
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'research').mkdir()
            altered=json.loads((depth.ROOT/route_path).read_bytes())
            route=next(r for r in altered['records'] if r['id']==self.row['reference_route_id'])
            route['coordinates_lon_lat'][-1][0]=96
            raw=json.dumps(altered).encode();(root/route_path).write_bytes(raw)
            audit['source_sha256']=hashlib.sha256(raw).hexdigest();audit['coordinates_lon_lat']=route['coordinates_lon_lat'];audit['route_easternmost_vertex_longitude_degrees_east']=96
            (root/depth.SOURCE).write_text(json.dumps(source),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Reassess'):depth.validate_context(self.row,root)

    def test_campaign_window_not_invented_section_dates_or_seasonal_envelope(self):
        self.assertEqual(self.row['campaign_window'],{'start_date':'1995-02-06','end_date':'1995-03-21'})
        self.reject([('campaign_window',{'start_date':'1998-08-01','end_date':'1998-08-01'}),('section_sampling_month','1995-02'),('section_sampling_window',{'start':'1995-02-06','end':'1995-03-21'}),('calendar_months',[12,1,2,3]),('climatology_years',[1990,1995]),('temporal_operator','monthly_climatology'),('phase_label','southwest_monsoon')])

    def test_no_speed_digitization_significance_or_unsupported_geometry(self):
        self.reject([('speed_digitization_performed',True),('statistical_significance_established',True),('annual_range_m',[100,300]),('uncertainty_m',8),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_original_access_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        row=next(r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['id']==self.row['id'])
        self.assertEqual(json.loads(row['campaign_window']),self.row['campaign_window'])
        self.assertEqual(row['source_section_id'],'I9N_eastern_leg')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());review=source['source_reviews'][0]
        self.assertTrue(review['actual_original_pixels_viewed']);self.assertEqual(review['actual_reviewed_pages'],[2,3])
        self.assertEqual(len(review['original_pdf_sha256']),64)
        self.assertEqual(source['references'][0],{k:self.row[k] for k in source['references'][0]})


if __name__=='__main__':unittest.main()
