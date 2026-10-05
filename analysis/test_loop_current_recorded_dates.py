"""Repeat-date scientific gates, exact readback and unchanged measurement rules."""
import copy
import json
import unittest
from build_loop_current_recorded_dates import ROOT, OUTPUT, build, source_rows, path_for, rebuild_noaa, rebuild_adt
from build_loop_current_dated_streamline import GEOD
from build_loop_current_recorded_date_page import build as page_build

class LoopRecordedDateTests(unittest.TestCase):
    def test_all_outcomes_reproduce_and_failures_remain_null(self):
        result=build();self.assertEqual(result,json.loads(OUTPUT.read_bytes()))
        self.assertEqual([r['date'] for r in result['dates']],['2025-01-15','2025-04-15','2025-07-15','2025-10-15'])
        self.assertEqual([r['noaa_connected_length_km'] for r in result['dates']],[None,1573.2,None,None])
        self.assertEqual([r['adt_selected_length_km'] for r in result['dates']],[2082.9,1592.7,1674.0,989.4])
        self.assertEqual([r['signed_difference_duacs_minus_noaa_km'] for r in result['dates']],[None,19.5,None,None])
        for key in ['whole_current_length_km','width_km','annual_length_range_km','confidence_interval_km']:self.assertIsNone(result[key])
        self.assertFalse(result['rank_eligible'])

    def test_every_date_retains_same_gates_steps_masks_and_candidates(self):
        for row in source_rows():
            noaa=json.loads(path_for('noaa',row['date']).read_bytes());adt=json.loads(path_for('adt',row['date']).read_bytes())
            self.assertEqual(noaa['observation_date'],adt['observation_date']);self.assertEqual(noaa['observation_date'],row['date'])
            north=[v for v in noaa['nominal_seed_candidates'] if v['northward_m_s'] is not None and v['northward_m_s']>0]
            self.assertEqual(noaa['nominal']['seed_lon_lat'],[max(north,key=lambda v:v['northward_m_s'])['longitude'],21.875])
            self.assertEqual(len(noaa['sensitivity_scenarios']),8)
            self.assertEqual(len(adt['scanned_levels']),146)
            chosen=max((c for c in adt['gateway_candidates'] if c['status']=='eligible'),key=lambda c:c['mean_speed_m_s'])
            self.assertEqual(adt['selected'],chosen);self.assertNotIn(chosen['adt_level_m'],[.05,1.5])
            for trace in [noaa['nominal']]+noaa['sensitivity_scenarios']:
                points=trace['coordinates_lon_lat'];length=sum(GEOD.inv(*a,*b)[2] for a,b in zip(points,points[1:]))/1000
                self.assertAlmostEqual(length,trace['travelled_distance_km'],delta=.051)
                if not trace['gate_connected']:self.assertIsNone(trace['open_path_length_km'])
            self.assertFalse(noaa['rank_eligible']);self.assertFalse(adt['rank_eligible'])

    def test_generated_page_keeps_all_dates_outcomes_and_query_links(self):
        page=page_build();self.assertEqual(page,(ROOT/'almanac/loop-current-recorded-dates.html').read_text(encoding='utf-8'))
        for row in source_rows():self.assertIn(row['date'],page)
        self.assertIn('unresolved',page);self.assertIn('not establish annual extrema',page)
        self.assertIn('aria-live="polite"',page);self.assertIn('noscript',page)
        self.assertEqual(page.count('Query this date'),4)

if __name__=='__main__':unittest.main()
