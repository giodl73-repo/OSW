import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import netCDF4,numpy as np
import audit_act2011_retained_pair_v2 as source


def fixture(n=3,depth=496.,south=.4,lat=-34.,shift_seconds=0,format='NETCDF3_CLASSIC',positive='down'):
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'point.nc'
        with netCDF4.Dataset(path,'w',format=format) as ds:
            ds.createDimension('time',n);ds.createDimension('timeSeries',1)
            ds.id='test-'+str(depth);ds.mooring_name='B';ds.instrument_depth=str(depth)+' meters';ds.sampling_interval='20 minutes';ds.Conventions='CF-1.6'
            t=ds.createVariable('time','f8',('time',));t.units='seconds since 1970-01-01 00:00:00 0:00';t.standard_name='time'
            la=ds.createVariable('lat','f4',('timeSeries',));la.standard_name='latitude';la[:]=lat
            lo=ds.createVariable('lon','f4',('timeSeries',));lo.standard_name='longitude';lo[:]=28.
            z=ds.createVariable('z','f4',('time',));z.units='meters';z.standard_name='depth';z.positive=positive;z[:]=depth
            u=ds.createVariable('u','f4',('time',));u.units='meters per second';u.long_name='eastward velocity component';u[:]=.2
            v=ds.createVariable('v','f4',('time',));v.units='meters per second';v.long_name='northward velocity component';v[:]=-south
            if n==3:
                dates=[source.frozen.datetime.fromisoformat(s.replace('Z','')) for s in source.frozen.DATES]
                t[:]=netCDF4.date2num(dates,t.units)+shift_seconds
            else:
                start=netCDF4.date2num(source.frozen.datetime(2010,4,8,12),t.units)
                t[:]=start+np.arange(n)*1200+shift_seconds
        return path.read_bytes()

class RetainedSelectivePair(unittest.TestCase):
    def test_legacy_sized_axes_select_only_fixed_samples_inside_global_budget(self):
        r,rows=source.extract([fixture(43000),fixture(43000,996,0)])
        self.assertEqual(len(rows),6);self.assertEqual(len(r['profiles']),3)
        self.assertEqual(r['native_time_axis_scalars_loaded'],86000)
        self.assertLess(r['conservative_case_scalar_bound_including_prior_metadata'],112000)
        self.assertEqual(r['independent_threshold_contexts_verified'],9)
        self.assertAlmostEqual(r['profiles'][0]['native_coordinate_threshold_contexts'][1]['lower_native_depth_coordinate_isotach_scenario_m'],871,places=4)

    def test_CF_coordinate_not_promoted_to_verified_sea_surface_current_bottom(self):
        r,rows=source.extract([fixture(),fixture(depth=996,south=0)])
        for p in r['profiles']:
            self.assertFalse(p['independent_sea_surface_or_gauge_datum_verified']);self.assertFalse(p['physical_current_identity_independently_verified'])
            for key in ['physical_current_bottom_m','physical_thickness_m','uncertainty_m','annual_range_m','volume_m3']:self.assertIsNone(p[key])
            for c in p['native_coordinate_threshold_contexts']:
                self.assertNotIn('lower_isotach_scenario_m',c);self.assertIsNone(c['physical_current_bottom_m'])
        self.assertTrue(all(not v['native_depth_coordinate_is_current_bottom'] for v in rows))

    def test_missing_native_time_and_incompatible_coordinates_do_not_make_profiles(self):
        for raw in [fixture(depth=996,south=0,lat=-34.2),fixture(depth=996,south=0,shift_seconds=60)]:
            r,rows=source.extract([fixture(),raw])
            self.assertTrue(all(p['native_coordinate_threshold_contexts']==[] for p in r['profiles']))
            self.assertEqual(len(rows),6)

    def test_hdf_compression_wrong_direction_and_extra_instrument_rejected_before_arrays(self):
        for raw in [fixture(format='NETCDF4'),fixture(positive='up')]:
            with self.assertRaises(ValueError):source.extract([raw,fixture(depth=996,south=0)])
        with self.assertRaises(ValueError):source.extract([fixture()]*3)

    def test_original_500m_gap_and_reverse_flow_rules_unchanged(self):
        r,rows=source.extract([fixture(),fixture(depth=1096,south=0)])
        self.assertEqual(r['profiles'][0]['native_coordinate_threshold_contexts'][1]['status'],'censored_at_predeclared_500m_sample_gap')
        self.assertIsNone(source.independent_pair([496,996],[-.4,0],.1))
        self.assertIsNone(source.independent_pair([496,996],[.4,.2],.1))

    def test_independent_formula_catches_corrupt_first_reader_result(self):
        actual=source.frozen.pair_diagnostic
        def wrong(*a):
            r=actual(*a)
            if r['lower_isotach_scenario_m'] is not None:r['lower_isotach_scenario_m']+=1
            return r
        with patch.object(source.frozen,'pair_diagnostic',wrong):
            with self.assertRaises(ValueError):source.extract([fixture(),fixture(depth=996,south=0)])

    def test_actual_receipts_override_stale_zero_header_without_mutating_it(self):
        j={'ocean_field_requests':0,'operations':[{'command':'LIST','path':'/x','status':'received_archived_before_interpretation'},
          {'command':'RETR','path':'/a.nc','status':'provider_hash_verified_archived_before_parse'},
          {'command':'RETR','path':'/b.nc','status':'provider_hash_verified_archived_before_parse'}]}
        before=copy.deepcopy(j);self.assertEqual(source.source_transfer_count(j),2);self.assertEqual(j,before)

    def test_network_tripwire(self):
        with self.assertRaises(RuntimeError):source.no_network('provider')

if __name__=='__main__':unittest.main()
