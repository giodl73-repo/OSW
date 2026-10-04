import copy
import json
import unittest
from build_current_section_width_series import measure, distance, OUTPUT
from check_current_section_width_series import validate

class SectionWidthTests(unittest.TestCase):
    def test_known_triangular_profile(self):
        profile=[{'latitude':lat,'eastward_m_s':u} for lat,u in [(36,0),(36.5,.5),(37,1),(37.5,.5),(38,0)]]
        result=measure(profile,.5)
        self.assertAlmostEqual(result['span_km'],distance(36.5,37.5),places=5)
        self.assertEqual(result['south_boundary']['latitude'],36.5)
        self.assertEqual(result['north_boundary']['latitude'],37.5)

    def test_missing_boundary_and_weak_peak(self):
        for profile in [[{'latitude':36,'eastward_m_s':None},{'latitude':37,'eastward_m_s':1},{'latitude':38,'eastward_m_s':0}], [{'latitude':36,'eastward_m_s':0},{'latitude':37,'eastward_m_s':.1},{'latitude':38,'eastward_m_s':0}]]:
            self.assertIsNone(measure(profile,.5)['span_km'])

    def test_rejects_false_confidence_and_changed_threshold(self):
        document=json.loads(OUTPUT.read_text(encoding='utf-8'));validate(document)
        for flag in ['is_confidence_interval','whole_current_representative','annual_extrema_eligible']:
            bad=copy.deepcopy(document);bad[flag]=True
            with self.subTest(flag=flag),self.assertRaises(ValueError):validate(bad)
        bad=copy.deepcopy(document);bad['frames'][0]['threshold_scenarios'][0]['fraction']=.3
        with self.assertRaises(ValueError):validate(bad)
        # Pick a frame flagged as marginally resolved rather than assume the first.
        index=next(i for i,r in enumerate(document['frames']) if r['nominal']['resolution_review_required'])
        bad=copy.deepcopy(document);bad['frames'][index]['nominal']['resolution_review_required']=False
        with self.assertRaises(ValueError):validate(bad)

    def test_sample_span_is_not_annual_or_uncertainty(self):
        document=json.loads(OUTPUT.read_text(encoding='utf-8'))
        self.assertEqual(document['sample_value_spans'][0]['rounded_sample_value_span_km'],[70,150])
        self.assertEqual(document['sample_value_spans'][0]['sample_count'],12)
        document['sample_value_spans'][0]['range_kind']='annual_extrema'
        with self.assertRaises(ValueError):validate(document)

if __name__=='__main__':unittest.main()
