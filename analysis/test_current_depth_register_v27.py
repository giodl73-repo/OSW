"""Check strict velocity-qualified reach and the out-of-route branch boundary."""
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import build_current_depth_register_v26 as previous
import build_current_depth_register_v27 as depth


class AtlanticNorthernNECDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][312]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,changes):
        for k,v in changes:
            changed=copy.deepcopy(self.row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_preserved_and_regional_owner_added(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:312],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':313,'identities_with_scoped_depth_reference':96,'identities_not_yet_assessed':15,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.validate(self.row)

    def test_strict_reach_not_bottom_thickness_or_integration_domain(self):
        self.assertEqual(self.row['lower_bound_m'],100)
        self.reject([('lower_bound_operator','>='),('lower_bound_exclusive',False),('lower_bound_m',300),('lower_bound_m',700),('lower_bound_m',800),('metric','lower_flow_boundary_depth'),('upper_boundary_m',0),('lower_boundary_m',100),('thickness_m',100)])

    def test_threshold_and_northern_band_identity_not_dropped(self):
        self.reject([('source_speed_condition',{'component':'westward_zonal_speed','operator':'>=','value':0.1,'unit':'m_s-1'}),('source_speed_condition',None),('source_speed_condition',{'component':'westward_zonal_speed','operator':'>','value':10,'unit':'m_s-1'}),('source_current_branch','southern_NEC_band'),('section_latitude_lower_exclusive_degrees_north',16),('section_longitude_degrees_east',-24),('entity_id','current:atlantic-north-equatorial-countercurrent')])

    def test_observed_calendar_window_not_model_year_or_publication(self):
        self.assertEqual(self.row['observational_section_window'],{'start_month':'2003-07','end_month':'2003-08'})
        self.reject([('observational_section_window',{'start_month':'2005-12','end_month':'2005-12'}),('model_elapsed_year',2003),('model_phase_label','July_August'),('temporal_operator','two_independent_direct_observations'),('calendar_months',[7,8]),('section_sampling_month','2003-07'),('climatology_years',[2003,2003])])

    def test_route_projection_is_explicitly_excluded_and_pinned(self):
        self.reject([('reference_route_projection_eligible',True),('reference_route_id','whole_NEC'),('route_scope_relationship','same_route_section')])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes());audit=source['reference_route_scope_audit']
        route_path=audit['source_file'];self.assertEqual(self.data['input_sha256'][route_path],audit['source_sha256'])
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);(root/'research').mkdir()
            altered=json.loads((depth.ROOT/route_path).read_bytes())
            route=next(r for r in altered['records'] if r['id']==self.row['reference_route_id'])
            route['coordinates_lon_lat'][0][1]=23
            raw=json.dumps(altered).encode();(root/route_path).write_bytes(raw)
            # Even a consistently repinned route needs reassessment when it enters the northern band.
            audit['source_sha256']=hashlib.sha256(raw).hexdigest();audit['coordinates_lon_lat']=route['coordinates_lon_lat']
            (root/depth.SOURCE).write_text(json.dumps(source),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Reassess'):depth.validate_context(self.row,root)

    def test_no_volume_annual_extrema_or_unreviewed_width_join(self):
        self.reject([('annual_range_m',[100,300]),('uncertainty_m',8),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('same_source_width_reference_id','unreviewed'),('independent_observation_count_claimed',True)])

    def test_json_csv_and_access_metadata_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        row=next(r for r in csv.DictReader(io.StringIO(raw.decode('utf8'))) if r['id']==self.row['id'])
        self.assertEqual(json.loads(row['source_speed_condition']),self.row['source_speed_condition'])
        self.assertEqual(json.loads(row['observational_section_window']),self.row['observational_section_window'])
        self.assertEqual(row['reference_route_projection_eligible'],'False')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertFalse(source['source_reviews'][0]['actual_original_pixels_viewed'])
        self.assertEqual(source['references'][0],{k:self.row[k] for k in source['references'][0]})


if __name__=='__main__':unittest.main()
