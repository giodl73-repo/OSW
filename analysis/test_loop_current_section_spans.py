"""Section-boundary identity, missing support and product separation."""
import json
import unittest
from build_loop_current_section_spans import build, output, measure, separation
from build_query_width_samples import build as samples

class LoopSectionSpanTests(unittest.TestCase):
    def test_triangular_peak_and_overlapping_bracket_lower_bound(self):
        profile=[{'longitude':x,'northward_m_s':v} for x,v in [(-86.5,0),(-86.25,1),(-86,0)]]
        result=measure(profile,.5,.25)
        self.assertAlmostEqual(result['west_boundary']['longitude'],-86.375)
        self.assertAlmostEqual(result['east_boundary']['longitude'],-86.125)
        self.assertAlmostEqual(result['span_km'],separation(-86.375,-86.125),places=5)
        self.assertEqual(result['grid_bracket_span_km'][0],0)
        self.assertTrue(result['resolution_review_required'])
        profile[0]['northward_m_s']=None
        failed=measure(profile,.5,.25)
        self.assertIsNone(failed['span_km'])
        self.assertIsNone(failed['west_boundary'])
        self.assertEqual(failed['west_stop_reason'],'missing_velocity')
        self.assertIsNotNone(failed['east_boundary'])

    def test_invalid_threshold_order_and_nonfinite_data(self):
        for f in [0,1,float('nan')]:
            with self.assertRaises(ValueError):measure([],f,.25)
        for p in [[{'longitude':0,'northward_m_s':float('inf')}],
                  [{'longitude':1,'northward_m_s':1},{'longitude':0,'northward_m_s':1}],
                  [{'longitude':0,'northward_m_s':0},{'longitude':.5,'northward_m_s':1}]]:
            with self.assertRaises(ValueError):measure(p,.5,.25)

    def test_pinned_products_keep_all_dates_and_separate_sample_ranges(self):
        for method,expected in [('noaa',[120,110,110,110,100]),('adt',[90,80,80,80,70])]:
            doc=build(method);self.assertEqual(doc,json.loads(output(method).read_bytes()))
            self.assertEqual([r['approximate_section_span_km'] for r in doc['frames']],expected)
            self.assertEqual([r['failed_threshold_count'] for r in doc['frames']],[0]*5)
            self.assertEqual(doc['sample_value_spans'][0]['sample_count'],4)
            self.assertFalse(doc['whole_current_representative']);self.assertIsNone(doc['annual_width_range_km'])
            rows=samples([{'id':f'diagnostic:yucatan-{method}-sections','document':doc}])
            self.assertEqual(len(rows),5)
            self.assertTrue(all(r['latitude_degrees_north']==21.875 and r['longitude_degrees_east'] is None for r in rows))
            self.assertTrue(all(r['source_sample']==frame for r,frame in zip(rows,doc['frames'])))

if __name__=='__main__':unittest.main()
