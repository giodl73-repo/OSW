"""Independent filter invariants, missing support and complete-month statistics."""
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

import build_norkyst_continuous_sections as sections
import json
from norkyst_continuous_source import VARIABLES


class ContinuousSectionTests(unittest.TestCase):
    def test_retained_months_reproduce_from_all_originals_with_complete_support(self):
        report=json.loads((sections.FOLDER/'section-diagnostic-pilot.json').read_bytes())
        rebuilt,arrays=sections.build(write_asset=False,return_arrays=True)
        for key,value in report.items():
            if key not in ['months','section_distances_km']:
                self.assertEqual(rebuilt[key],value,key)
        np.testing.assert_allclose(rebuilt['section_distances_km'],report['section_distances_km'],rtol=0,atol=1e-8)
        for actual,expected in zip(rebuilt['months'],report['months']):
            for key,value in expected.items():
                if key!='summary':self.assertEqual(actual[key],value)
            for variable in VARIABLES:
                for kind in ['raw','lowpass']:
                    a=actual['summary'][variable][kind];b=expected['summary'][variable][kind]
                    self.assertEqual(a['valid_hours'],b['valid_hours'])
                    self.assertEqual(a['expected_hours'],b['expected_hours'])
                    for statistic in ['mean','standard_deviation','p05','median','p95']:
                        np.testing.assert_allclose(a[statistic],b[statistic],rtol=0,atol=1.1e-8)
        with np.load(sections.ROOT/report['bulk_asset']['file'],allow_pickle=False) as retained:
            self.assertEqual(set(retained.files),set(arrays))
            for key,array in arrays.items():
                if array.dtype.kind in 'iu':np.testing.assert_array_equal(array,retained[key])
                else:np.testing.assert_allclose(array,retained[key],rtol=0,atol=1e-11,equal_nan=True)
        self.assertEqual(report['acquired_hourly_fields'],1632)
        self.assertEqual(report['completed_calendar_hours'],1488)
        self.assertEqual(set(report['previous_noon_field_comparison']),{'1','7'})
        self.assertFalse(report['complete_annual_temporal_support'])
        self.assertFalse(report['new_width_record_admitted'])
        self.assertIsNone(report['whole_current_width_km'])
        self.assertIsNone(report['annual_width_range_km'])
        for month in report['months']:
            for variable in VARIABLES:
                for kind in ['raw','lowpass']:
                    self.assertEqual(month['summary'][variable][kind]['valid_hours'],[744]*191)

    def test_corrupted_original_archive_cannot_be_used_as_the_reviewed_source(self):
        acquisition=json.loads((sections.FOLDER/'acquisition-pilot.json').read_bytes())
        target=sections.ROOT/acquisition['archives'][0]['file'];original=Path.read_bytes
        def altered(path):
            raw=original(path);return raw+b'changed' if path==target else raw
        with patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):sections.build()

    def test_filter_is_symmetric_normalized_and_preserves_constant_and_linear_signals(self):
        weights=sections.kernel()
        self.assertEqual(len(weights),71)
        np.testing.assert_array_equal(weights,weights[::-1])
        self.assertAlmostEqual(float(weights.sum()),1,places=14)
        for signal in [np.full(200,3.25),np.arange(200,dtype=float)]:
            values=np.broadcast_to(signal[:,None,None],(200,2,3)).copy()
            filtered=sections.lowpass(values)
            self.assertTrue(np.isnan(filtered[:35]).all())
            self.assertTrue(np.isnan(filtered[-35:]).all())
            np.testing.assert_allclose(filtered[35:-35],values[35:-35],rtol=0,atol=1e-12)

    def test_synthetic_tidal_band_attenuation_matches_the_kernel_response(self):
        for period in [12,24,12.42]:
            t=np.arange(1000);signal=np.sin(2*np.pi*t/period)
            filtered=sections.lowpass(np.broadcast_to(signal[:,None,None],(1000,1,3)))
            response=abs(np.sum(sections.kernel()*np.exp(-2j*np.pi*np.arange(71)/period)))
            self.assertLess(response,.001)
            self.assertLessEqual(float(np.max(np.abs(filtered[35:-35]))),response+1e-12)

    def test_one_missing_component_invalidates_all_paired_fields_for_its_full_support(self):
        values=np.ones((250,2,3));values[100,0,1]=np.nan
        filtered=sections.lowpass(values)
        self.assertTrue(np.isnan(filtered[65:136,0]).all())
        self.assertTrue(np.isfinite(filtered[64,0]).all())
        self.assertTrue(np.isfinite(filtered[136,0]).all())
        self.assertTrue(np.isfinite(filtered[35:-35,1]).all())
        for values in [np.ones((70,1,3)),np.ones((200,1,2))]:
            with self.assertRaises(ValueError):sections.lowpass(values)

    def test_complete_month_statistics_are_null_if_any_required_hour_is_missing(self):
        values=np.column_stack([np.arange(744,dtype=float),np.full(744,np.nan),np.ones(744)])
        values[12,2]=np.nan
        report=sections.summarize(values)
        self.assertEqual(report['valid_hours'],[744,0,743])
        self.assertEqual(report['mean'],[371.5,None,None])
        self.assertAlmostEqual(report['standard_deviation'][0],float(np.std(np.arange(744),ddof=0)),places=7)
        self.assertEqual(report['median'],[371.5,None,None])
        self.assertEqual(report['p05'],[37.15,None,None])
        self.assertEqual(report['p95'],[705.85,None,None])

    def test_spatial_interpolation_preserves_paired_missing_support_and_fill_before_scale(self):
        arrays={name:np.zeros((2,2,2),dtype=np.int16) for name in VARIABLES}
        arrays['sea_mask']=np.ones((2,2),dtype=np.int16)
        rows=np.asarray([[0,0,1,1]]);cols=np.asarray([[0,1,0,1]]);weights=np.full((1,4),.25)
        actual=sections.interpolate(arrays,rows,cols,weights)
        np.testing.assert_array_equal(actual[:,:,0],30)
        np.testing.assert_array_equal(actual[:,:,1:],0)
        arrays['v_northward'][1,0,0]=-32767
        actual=sections.interpolate(arrays,rows,cols,weights)
        self.assertTrue(np.isfinite(actual[0]).all())
        self.assertTrue(np.isnan(actual[1]).all())
        arrays['sea_mask'][0,0]=0
        self.assertTrue(np.isnan(sections.interpolate(arrays,rows,cols,weights)).all())

    def test_bulk_asset_is_deterministic_and_preserves_missing_values_and_time_types(self):
        arrays={'field':np.asarray([[1.25,np.nan]]),'epoch_seconds':np.asarray([1704067200],dtype=np.int64)}
        with TemporaryDirectory() as temporary:
            path=Path(temporary)/'profiles.npz';sections.write_npz(path,arrays);first=path.read_bytes()
            sections.write_npz(path,arrays);self.assertEqual(first,path.read_bytes())
            with np.load(io.BytesIO(first),allow_pickle=False) as loaded:
                np.testing.assert_array_equal(loaded['field'],arrays['field'])
                np.testing.assert_array_equal(loaded['epoch_seconds'],arrays['epoch_seconds'])


if __name__=='__main__':unittest.main()
