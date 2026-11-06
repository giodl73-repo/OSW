"""Test actual native support and the decisions that can create false crossings."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import xarray as xr
import build_p14n_native_field_audit as audit

class NativeFieldTests(unittest.TestCase):
    def test_source_reconstruction_and_independent_quality_counts(self):
        r=audit.verify();s=r['summary']
        self.assertEqual(s['selected_native_profiles'],1585)
        self.assertEqual(s['retained_native_depth_cells'],190200)
        self.assertEqual(sum(s['editing_flag_counts'].values()),190200)
        self.assertEqual(s['joint_finite_unflagged_cells'],182081)
        self.assertEqual(s['supported_layer_means'],1582)
        self.assertEqual(s['short_long_flag_differences'],0)
        self.assertTrue(r['frame_correspondence']['correspondence_within_tolerance'])
        self.assertFalse(r['frame_correspondence']['short_ship_motion_added_again'])
        self.assertEqual([b['eligible_profiles'] for b in r['run_sensitivity']],[623,568,532])
        self.assertEqual([b['run_count'] for b in r['run_sensitivity']],[42,19,19])
        self.assertEqual(s['profiles_with_ctd_event_overlap'],685)
        self.assertEqual(s['underway_eligible_profiles_with_ctd_event_overlap'],0)
        self.assertFalse(r['new_width_record_admitted'])
        self.assertFalse(r['osw_temporal_ocean_velocity_averaging_applied'])
    def test_duration_and_velocity_units_cannot_be_reinterpreted(self):
        source=xr.Dataset({'duration':('time',[300.]),'velocity':('time',[.1])})
        source.duration.attrs['units']='s';source.velocity.attrs['units']='m/s'
        audit.require_units(source,{'duration':'s','velocity':'m/s'})
        for name,unit in [('duration','minutes'),('velocity','cm/s')]:
            original=source[name].attrs['units'];source[name].attrs['units']=unit
            with self.subTest(name=name),self.assertRaises(ValueError):audit.require_units(source,{'duration':'s','velocity':'m/s'})
            source[name].attrs['units']=original
    def test_native_flag_bits_are_exclusions_not_ctd_codes(self):
        depth=np.arange(90,311,10);u=np.ones(len(depth));v=u*2
        for flag in [1,2,4,7,-1,np.nan]:
            with self.subTest(flag=flag):
                result=audit.supported_layer(depth,u,v,np.full(len(depth),flag))
                self.assertIsNone(result['eastward_m_s']);self.assertEqual(result['joint_valid_thickness_m'],0)
        u[:]=np.nan;result=audit.supported_layer(depth,u,v,np.zeros(len(depth)))
        self.assertIsNone(result['northward_m_s'])
        result=audit.supported_layer(depth[::-1],v,v,np.zeros(len(depth)))
        self.assertFalse(result['depth_coordinates_acceptable'])
    def test_nominal_cast_overlap_keeps_multiplicity_and_excludes_touch(self):
        start=datetime(1993,7,14,12,tzinfo=timezone.utc);end=start+timedelta(minutes=5)
        events=[{'ctd_identity':'a','begin_utc':audit.stamp(start),'end_utc':audit.stamp(end)},
                {'ctd_identity':'b','begin_utc':audit.stamp(start-timedelta(minutes=1)),'end_utc':audit.stamp(end-timedelta(minutes=1))},
                {'ctd_identity':'touch','begin_utc':audit.stamp(end),'end_utc':audit.stamp(end+timedelta(minutes=5))}]
        self.assertEqual(audit.overlaps(start,end,events),[{'ctd_identity':'a','nominal_overlap_seconds':300},{'ctd_identity':'b','nominal_overlap_seconds':240}])
        self.assertEqual(audit.overlaps(None,end,events),[])
    def test_runs_break_without_pruning_or_reordering(self):
        epoch=datetime(1993,7,14,tzinfo=timezone.utc)
        def row(i,seconds,speed=2):
            end=epoch+timedelta(seconds=seconds)
            return {'source_time_index':i,'ensemble_end_utc':audit.stamp(end),'ensemble_start_utc':audit.stamp(end-timedelta(seconds=300)),
                    'latitude_degrees_north':45+i*.01,'longitude_degrees_east':179,'ship_speed_m_s':speed,'layer_mean':{'eastward_m_s':.1},'ctd_event_overlaps':[]}
        rows=[row(1,300),row(2,750),row(3,1201),row(5,1501),row(6,1801,1.9),row(7,2101)]
        result=audit.runs(rows,2)
        self.assertEqual([r['source_time_indices'] for r in result['runs']],[[1,2],[3],[5],[7]])
        self.assertEqual(result['eligible_profiles'],5)
        self.assertEqual(result['runs'][0]['northward_steps'],1)
        self.assertFalse(result['runs'][0]['current_length_or_width'])
    def test_all_eleven_native_context_operator_pins_are_enforced(self):
        original=Path.read_bytes
        for name in audit.FROZEN_INPUTS:
            target=audit.ROOT/name
            def changed(path):return original(path)+(b'x' if path==target else b'')
            with self.subTest(path=name),patch.object(Path,'read_bytes',changed),self.assertRaises(ValueError):audit.build()

if __name__=='__main__':unittest.main()
