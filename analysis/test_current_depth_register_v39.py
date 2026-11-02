import copy,csv,hashlib,io,json
import unittest
import build_current_depth_register_v38 as previous
import build_current_depth_register_v39 as depth


class NwASCGeometrySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.row=cls.data['evidence'][-1]
        cls.geometry=json.loads((depth.ROOT/'research/nwasc-core-geometry-source-facts-v1.json').read_bytes())
        cls.ids={r['entity_id'] for r in cls.data['records']};cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def reject(self,changes):
        for k,v in changes:
            r=copy.deepcopy(self.row);r[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):depth.validate_reference(r,self.ids,self.metrics);depth.validate_context(r)

    def test_previous342_references_and_normalizations_preserved(self):
        self.assertEqual(self.data['evidence'][:-1],previous.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':343,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.data['metadata_correction_count'],3)

    def test_bjornoya_static_core_depth_area_and_sampling(self):
        self.assertEqual((self.row['approximate_value_m'],self.row['source_cross_section_area_km2']),(580,17))
        self.assertEqual(self.row['source_section_transect_count'],53)
        self.assertEqual(self.row['core_definition']['fraction_of_mean_transport'],.5)
        self.assertEqual(self.row['core_definition']['ranking'],'decreasing_absolute_geostrophic_velocity')
        self.assertTrue(self.row['source_area_is_approximate'])

    def test_southern_isobath_cutoffs_and_bso_rank_not_inherited(self):
        self.assertIsNone(self.row['core_definition']['shoreward_isobath_m'])
        for cutoff in [1500,2500]:
            definition=dict(self.row['core_definition'],shoreward_isobath_m=cutoff)
            self.reject([('core_definition',definition)])
        self.reject([('core_definition',dict(self.row['core_definition'],ranking='decreasing_salinity'))])

    def test_three_geometry_pairs_link_exact_member_owned_depths(self):
        refs={r['id']:r for r in self.data['evidence']}
        self.assertEqual([(g['section_name'],g['maximum_core_depth_m'],g['source_core_area_km2']) for g in self.geometry['sections']],[('Svinoy',460,11),('Gimsoy',530,8),('Bjornoya',580,17)])
        self.assertEqual(self.geometry['depth_register_sha256'],hashlib.sha256((depth.ROOT/depth.OUTPUT).read_bytes()).hexdigest())
        for g in self.geometry['sections']:
            r=refs[g['depth_reference_id']];self.assertEqual(g['source_context'],r)
            self.assertEqual(g['depth_reference_sha256'],hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest())
            self.assertEqual(r['climatology_years'],[1993,2022]);self.assertEqual(r['core_definition']['fraction_of_mean_transport'],.5)

    def test_idealized_box_is_not_actual_geometry_or_error_bound(self):
        box=self.geometry['source_heat_budget_box_context']
        self.assertEqual((box['assumed_section_area_km2'],box['derived_box_depth_m'],box['reported_box_volume_km3']),(10,200,7500))
        self.assertFalse(box['used_as_actual_core_geometry']);self.assertFalse(self.geometry['BSO_included'])
        self.assertEqual(self.geometry['pathway']['reported_length_km'],750);self.assertTrue(self.geometry['pathway']['length_is_approximate'])
        self.assertFalse(self.geometry['pathway']['path_geometry_reconstructed'])

    def test_static_mean_does_not_establish_physical_thickness_or_seasons(self):
        self.assertFalse(self.row['source_quarterly_interpolation_is_depth_series'])
        self.reject([('calendar_months',[1,4,7,10]),('annual_range_m',[530,580]),('upper_boundary_m',50),('thickness_m',530),('volume_eligible',True),('seasonal_playback_eligible',True),('source_area_uncertainty_km2',1)])

    def test_json_csv_and_member_lookup_preserved(self):
        self.assertEqual(self.data,json.loads((depth.ROOT/depth.OUTPUT).read_bytes()))
        raw=depth.csv_bytes(self.data);self.assertEqual(raw,(depth.ROOT/depth.CSV).read_bytes())
        row=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))[-1]
        self.assertEqual(float(row['source_cross_section_area_km2']),17);self.assertEqual(float(row['source_section_transect_count']),53)
        index=json.loads((depth.ROOT/depth.MEMBER_OUTPUT).read_bytes());self.assertEqual(index['counts']['distinct_member_depth_references'],47)
        for r in index['records']:self.assertNotIn('current:norwegian-atlantic-slope',[m['entity_id'] for m in r['members']])


if __name__=='__main__':unittest.main()
