"""Gate/mask/selection and same-date comparison checks for the ADT diagnostic."""
import json
import unittest
import numpy as np
from build_loop_current_adt_contours import build, OUTPUT, SOURCE, field_arrays, orient_gate_path, mean_path_speed, scan, GEOD

class LoopAdtTests(unittest.TestCase):
    def test_reproduction_selection_and_source_gates(self):
        result=build();self.assertEqual(result,json.loads(OUTPUT.read_text(encoding='utf-8')))
        self.assertEqual(len(result['scanned_levels']),146)
        self.assertEqual(result['eligible_count'],31)
        selected=result['selected'];self.assertEqual(selected['adt_level_m'],.62)
        self.assertEqual(selected,max((c for c in result['gateway_candidates'] if c['status']=='eligible'),key=lambda c:c['mean_speed_m_s']))
        self.assertFalse(result['search_edge_peak']);self.assertFalse(result['rank_eligible'])
        self.assertEqual(result['approximate_diagnostic_path_km'],2200)
        p=selected['coordinates_lon_lat'];self.assertEqual(p[0][1],21.875);self.assertEqual(p[-1][0],-81.5)
        raw=sum(GEOD.inv(*a,*b)[2] for a,b in zip(p,p[1:]))/1000
        self.assertAlmostEqual(raw,selected['admissible_diagnostic_length_km'],delta=.05)
        self.assertEqual(result['comparison']['signed_difference_duacs_minus_noaa_km'],-55.9)
        for k in ['whole_current_length_km','width_km','annual_length_range_km','confidence_interval_km']:self.assertIsNone(result[k])

    def test_closed_wrong_and_reversed_gates(self):
        good=[[-86.125,21.875],[-84,27],[-81.5,24]]
        self.assertEqual(orient_gate_path(good),good)
        self.assertEqual(orient_gate_path(list(reversed(good))),good)
        self.assertIsNone(orient_gate_path(good+[good[0]]))
        self.assertIsNone(orient_gate_path([good[0],[-81.5,22]]))
        self.assertIsNone(orient_gate_path([[-88,21.875],good[-1]]))

    def test_missing_speed_cannot_be_averaged_away(self):
        source=json.loads(SOURCE.read_text(encoding='utf-8'));fields=field_arrays(source)
        fields['ugos'][:]=1.;fields['vgos'][:]=0.
        coordinates=[[-86,23],[-85,23],[-84,23]]
        self.assertAlmostEqual(mean_path_speed(source,fields,coordinates),1)
        fields['ugos'][:,110:]=np.nan
        self.assertIsNone(mean_path_speed(source,fields,coordinates))
        fields['adt'][:]=np.nan
        empty=scan(source,fields)
        self.assertIsNone(empty['selected']);self.assertEqual(empty['eligible_count'],0)

if __name__=='__main__':unittest.main()
