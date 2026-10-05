"""Scientific gate, failure preservation, readback and offline reproduction checks."""
import json
import unittest
import numpy as np
from build_loop_current_dated_streamline import build, trace, SOURCE, OUTPUT, GEOD
from build_gulf_stream_geostrophic_path import load_field, sample_velocity
from build_loop_current_experiment_page import build as page

class LoopStreamlineTests(unittest.TestCase):
    def test_pinned_experiment_and_failed_paths(self):
        result=build()
        self.assertEqual(result,json.loads(OUTPUT.read_text(encoding='utf-8')))
        nominal=result['nominal'];self.assertEqual(nominal['seed_lon_lat'],[-86.125,21.875])
        self.assertEqual(nominal['stop_reason'],'florida_gate')
        self.assertEqual(nominal['coordinates_lon_lat'][-1][0],-81.5)
        self.assertTrue(23<=nominal['coordinates_lon_lat'][-1][1]<=25)
        measured=sum(GEOD.inv(*a,*b)[2] for a,b in zip(nominal['coordinates_lon_lat'],nominal['coordinates_lon_lat'][1:]))/1000
        self.assertAlmostEqual(measured,nominal['open_path_length_km'],delta=.05)
        self.assertEqual(result['failure_count'],4)
        for s in result['sensitivity_scenarios']:
            if s['variation']=='seed_longitude':
                self.assertFalse(s['gate_connected']);self.assertIsNone(s['open_path_length_km'])
            else:self.assertLess(abs(s['open_path_length_km']-measured),12)
        self.assertFalse(result['rank_eligible'])
        for key in ['whole_current_length_km','annual_length_range_km','confidence_interval_km','sensitivity_range_km','width_km']:
            self.assertIsNone(result[key])

    def test_source_decode_and_mask_stops(self):
        source=json.loads(SOURCE.read_text(encoding='utf-8'));fields=load_field(source)
        lon,lat=-86.125,21.875
        decoded=sample_velocity(source,fields,lon,lat)
        i=11;j=47
        for n,value in zip(['ugos','vgos'],decoded):
            self.assertAlmostEqual(value,source['velocity_fields_raw_int32'][n][i][j]*.0001)
        fields['ugos'][:]=np.nan
        missing=trace(source,fields,lon)
        self.assertEqual(missing['stop_reason'],'missing_grid_velocity')
        self.assertIsNone(missing['open_path_length_km'])
        self.assertEqual(missing['travelled_distance_km'],0)
        for args in [(-84,10,.1),(-86.125,0,.1),(-86.125,10,0)]:
            with self.assertRaises(ValueError):trace(source,fields,*args)

    def test_visible_failure_scope_and_text_alternative(self):
        markup=page()
        self.assertIn('All four neighboring seed tests fail',markup)
        self.assertEqual(markup.count('<tr>'),10)
        self.assertIn('not measurement accuracy',markup)
        self.assertIn('aria-labelledby="map-title map-desc"',markup)

    def test_crossing_wrong_gate_and_return_flow_are_not_lengths(self):
        source=json.loads(SOURCE.read_text(encoding='utf-8'));fields=load_field(source)
        # A small northward component avoids a geodesic eastward step's
        # slight latitude decrease at the initial gate, yet exits below 23 N.
        fields['ugos'][:]=1.;fields['vgos'][:]=.01
        wrong=trace(source,fields,-86.125)
        self.assertEqual(wrong['stop_reason'],'eastward_crossing_outside_florida_gate')
        self.assertFalse(wrong['gate_connected']);self.assertIsNone(wrong['open_path_length_km'])
        fields['ugos'][:]=0.;fields['vgos'][:]=-1.
        returned=trace(source,fields,-86.125)
        self.assertEqual(returned['stop_reason'],'returned_south_of_yucatan_gate')
        self.assertIsNone(returned['open_path_length_km'])
        fields['vgos'][:]=0.
        weak=trace(source,fields,-86.125)
        self.assertEqual(weak['stop_reason'],'speed_below_threshold')
        self.assertIsNone(weak['open_path_length_km'])

if __name__=='__main__':unittest.main()
