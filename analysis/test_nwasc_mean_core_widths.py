"""Mean geometry, constant-depth support and proposed ownership stay distinct."""
import unittest
import nwasc_mean_core_widths as n

class MeanCoreWidths(unittest.TestCase):
    def test_original_publication_and_report_reproduce(self):
        d,pins=n.verify_inputs()
        self.assertEqual(d,n.build())
        self.assertEqual(len(d['measurements']),2)
        self.assertEqual(pins[n.FILE],n.digest(n.FILE))
        self.assertFalse(d['raw_data_reproduction_claimed'])
        self.assertFalse(d['raw_curated_sections_acquired'])

    def test_same_scalar_has_different_depth_and_sampling_support(self):
        si,gi=n.records()
        self.assertEqual([r['approximate_width_km'] for r in [si,gi]],[50,50])
        self.assertEqual(si['width_plane_depth_m'],50)
        self.assertIsNone(gi['width_plane_depth_m'])
        self.assertNotEqual(si['width_metric'],gi['width_metric'])
        self.assertEqual([si['reported_maximum_core_depth_m'],gi['reported_maximum_core_depth_m']],[460,530])
        self.assertEqual(si['width_support_cast_count'],4)
        self.assertIsNone(gi['width_support_cast_count'])
        for i,r in enumerate([si,gi]):
            with self.subTest(section=i):
                self.assertEqual(r['proposed_current_id'],n.OWNER)
                self.assertNotIn('current_id',r)
                self.assertEqual(r['observed_period'],'1993–2022')
                self.assertEqual(r['mean_transport_fraction'],0.5)
                self.assertEqual(r['core_salinity_minimum_g_kg'],35.16)
                self.assertTrue(r['is_mean_field_geometry'])
                for k in ['is_mean_of_widths','isobath_is_width_layer','is_uniformly_sampled_climatology','seasonal_playback_eligible','annual_extrema_eligible','rank_eligible']:
                    self.assertFalse(r[k],k)
                for k in ['uncertainty_km','width_range_km','fixed_layer_bounds_m','geographic_current_edges','annual_width_range_km']:
                    self.assertIsNone(r[k],k)
                self.assertEqual(r['source_pointer'],f'/measurements/{i}')

    def test_existing_proposed_widths_are_not_rewritten(self):
        from check_nordic_section_widths import proposed_records
        old=proposed_records();new=n.records()
        self.assertEqual(len(old),5)
        self.assertFalse({r['id'] for r in old}&{r['id'] for r in new})
        self.assertTrue(all('baumann' not in r['id'] for r in old))

if __name__=='__main__':unittest.main()
