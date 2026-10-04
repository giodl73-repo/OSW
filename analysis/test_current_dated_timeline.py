import copy
import json
import unittest
from check_current_dated_timeline import validate, OUTPUT

class DatedTimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(OUTPUT.read_text(encoding='utf-8'))

    def test_pinned_geometry_and_state_intersections(self):
        validate(self.document)
        self.assertFalse(self.document['frames'][0]['reaches_downstream_gate'])
        self.assertTrue(all(f['reaches_downstream_gate'] for f in self.document['frames'][1:]))

    def test_rejects_annual_claim_and_missing_frame(self):
        for key,value in [('annual_extrema_eligible',True),('annual_length_range_km',[1550,2338])]:
            bad=copy.deepcopy(self.document);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(self.document);bad['frames'].pop()
        with self.assertRaises(ValueError):validate(bad)

    def test_rejects_false_success_and_changed_path(self):
        for key,value in [('reaches_downstream_gate',True),('coordinates_lon_lat',[[-72.875,36.875],[-50,40]])]:
            bad=copy.deepcopy(self.document);bad['frames'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(bad)

    def test_year_samples_include_failures_and_processing_versions(self):
        annual = json.loads((OUTPUT.parent / 'ocean-current-dated-timeline-2025.json').read_text(encoding='utf-8'))
        validate(annual)
        self.assertEqual([r['date'] for r in annual['frames']], [f'2025-{month:02d}-15' for month in range(1,13)])
        self.assertEqual(sum(not r['reaches_downstream_gate'] for r in annual['frames']), 4)
        self.assertEqual({r['source_algorithm'] for r in annual['frames']}, {'RADS 4.7.0','RADS 4.7.1'})
        annual['frames'][7]['source_algorithm'] = 'RADS 4.7.0'
        with self.assertRaises(ValueError):validate(annual)

    def test_rejects_incomplete_or_mislabelled_sensitivity(self):
        for field,value in [('is_confidence_interval',True),('is_width_estimate',True),('rounded_successful_scenario_span_km',[0,4000])]:
            bad=copy.deepcopy(self.document)
            bad['frames'][0]['diagnostic_sensitivity'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(self.document)
        bad['frames'][0]['diagnostic_sensitivity']['scenarios'].pop()
        with self.assertRaises(ValueError):validate(bad)
        annual=json.loads((OUTPUT.parent/'ocean-current-dated-timeline-2025.json').read_text(encoding='utf-8'))
        self.assertIsNone(annual['frames'][-1]['diagnostic_sensitivity']['rounded_successful_scenario_span_km'])
        self.assertEqual(annual['frames'][-1]['diagnostic_length_km'],4000)

if __name__=='__main__':unittest.main()
