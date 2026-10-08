"""Keep recovered monthly branching positions distinct from dimensions."""
import copy
import json
import unittest
from unittest.mock import patch
from build_indian_sec_monthly_bifurcation import ROOT, CONFIG, OUTPUT, build, digest


class MonthlyBifurcationTests(unittest.TestCase):
    def test_pinned_extraction_and_source_scope(self):
        result=build()
        self.assertEqual(result,json.loads((ROOT/OUTPUT).read_bytes()))
        rows={row['id']:row for row in result['series']}
        self.assertEqual(set(rows),{'surface_ssh','wod_upper400'})
        self.assertEqual([row['approximate_latitude_degrees_north'] for row in rows['surface_ssh']['months']],[-16.8,-16.7,-16.9,-17.0,-17.2,-17.6,-17.6,-17.2,-16.8,-16.6,-16.1,-16.2])
        self.assertEqual([row['approximate_latitude_degrees_north'] for row in rows['wod_upper400']['months']],[-17.9,-17.9,-18.1,-18.1,-18.5,-18.6,-18.4,-18.2,-18.1,-18.1,-17.7,-17.6])
        for row in rows.values():
            self.assertEqual([point['month'] for point in row['months']],list(range(1,13)))
        self.assertIsNone(rows['wod_upper400']['source_period'])
        for key in ['whole_current_length_km','current_width_km','annual_dimension_range_km','geometry']:
            self.assertIsNone(result[key])
        for key in ['rank_eligible','annual_extrema_eligible','geographic_playback_eligible','is_confidence_interval','distinct_observed_years_inferred','source_variability_envelope_extracted']:
            self.assertIs(result[key],False)

    def test_stale_original_missing_markers_and_bad_axis_fail(self):
        config=json.loads((ROOT/CONFIG).read_bytes())
        with patch('build_indian_sec_monthly_bifurcation.digest',return_value='0'*64),self.assertRaises(ValueError):build()
        original_loads=json.loads
        for key,value in [('marker_bounds_points',[323,100,400,215]),('axis_latitude_degrees_north',[-18.8,-15.2])]:
            changed=copy.deepcopy(config);changed[key]=value
            def replacement(raw):
                value=original_loads(raw)
                return changed if value.get('schema')=='osw.monthly-bifurcation-vector-config.v1' else value
            with self.subTest(key=key),patch('build_indian_sec_monthly_bifurcation.json.loads',side_effect=replacement),self.assertRaises(ValueError):build()


if __name__ == '__main__':
    unittest.main()
