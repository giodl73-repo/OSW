import copy,json,unittest
import richardson_walsh_1986_characteristic_velocities_v1 as source

class CharacteristicVelocityTests(unittest.TestCase):
    def facts(self):return json.loads((source.ROOT/source.FACTS).read_bytes())
    def test_table_unit_conversion_and_distinct_SEC_rows(self):
        rows=source.prepare(self.facts())['records']
        self.assertEqual(len(rows),10);self.assertEqual(len({r['entity_id'] for r in rows}),8)
        self.assertEqual(rows[2]['characteristic_mean_vector_speed_m_s'],.75)
        self.assertIsNone(rows[6]['characteristic_mean_vector_speed_m_s'])
        self.assertEqual(rows[6]['characteristic_mean_vector_speed_interval_m_s'],[.05,.10])
        self.assertEqual([r['characteristic_mean_vector_speed_m_s'] for r in rows[-3:]],[.14,.30,.30])
    def test_reclassified_harmonics_annual_bounds_or_family_owner_refused(self):
        for case in range(4):
            f=self.facts()
            if case==0:f['operators']['harmonic_formula_as_printed']='sqrt((A_x^2+A_y^2)/2)'
            elif case==1:f['operators']['seasonal_variation_is_minmax_range']=True
            elif case==2:f['table_rows'][5]['entity_id']='current:north-equatorial'
            else:f['table_rows'][0]['mean_speed_cm_s']=36
            with self.assertRaises(ValueError):source.prepare(f)
    def test_unsupported_derived_fields_stay_unknown(self):
        for r in source.prepare(self.facts())['records']:
            for field in ['monthly_velocity_series','annual_speed_extrema','confidence_interval','numerical_uncertainty_m_s','fixed_depth_m','sampling_geometry']:self.assertIsNone(r[field])
            self.assertFalse(r['monthly_speed_playback_eligible']);self.assertFalse(r['global_speed_rank_eligible'])
    def test_frozen_preparation_and_render_source_match(self):
        saved=json.loads((source.ROOT/source.PREPARED).read_bytes());saved.pop('input_sha256')
        self.assertEqual(saved,source.prepare(self.facts()))
        self.assertEqual((source.ROOT/source.FIGURE).read_bytes(),source.figure(self.facts()).encode())

if __name__=='__main__':unittest.main()
