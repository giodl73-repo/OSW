import copy,json,unittest
from datetime import datetime,timedelta
from pathlib import Path
import collect_indian_euc_rama_2006_depth_v1 as source
import indian_euc_observed_profile_checks_v1 as checks
from test_indian_euc_rama_2005_depth_v1 import raw_patch,days

class PositiveIOD(unittest.TestCase):
    def test_entire_event_disjoint_caps_and_cached_metadata(self):
        targets,metadata=source.preflight()
        self.assertEqual(len(targets),30)
        self.assertEqual(targets[0]['times_utc'][0],'2006-08-01T12:00:00Z')
        self.assertEqual(targets[-1]['times_utc'][-1],'2006-10-29T12:00:00Z')
        self.assertEqual(len({d for t in targets for d in t['times_utc']}),90)
        self.assertEqual(sum(t['reserved_numeric_scalars'] for t in targets),16200)
        op=json.loads((source.ROOT/source.OP).read_bytes())
        self.assertEqual(op['global_scalar_reserve'],19144)
        self.assertEqual(op['global_node_reserve'],4500)
        self.assertEqual(op['maximum_http_requests'],30)
        self.assertEqual(op['maximum_profiles'],90)
        self.assertEqual(op['maximum_response_bytes'],20000)
        self.assertEqual(op['maximum_attempts_per_target'],1)
        self.assertEqual(metadata['units'],'cm/s')

    def test_independent_three_threshold_calculations(self):
        target=source.plan()[0];values,n=source.parse_patch(raw_patch(target),target)
        self.assertEqual(n,486)
        for p in values:checks.verify_indian_profile(p)
        self.assertEqual(values[0]['primary_lower_isotach_depth_m'],135)
        self.assertEqual(values[0]['primary_threshold_layer_span_m'],70)
        corrupt=copy.deepcopy(values[0]);corrupt['threshold_contexts'][1]['lower_depth_m']+=1
        with self.assertRaises(ValueError):checks.verify_indian_profile(corrupt)

    def test_qc_gap_ties_and_core_window_edges(self):
        target=source.plan()[0]
        for depth in [40,90,130]:
            def reject(rows):
                for r in rows:
                    if r[5]==depth:r[-1]=3
                return rows
            values,_=source.parse_patch(raw_patch(target,reject),target)
            for p in values:checks.verify_indian_profile(p)
        z=[40,50,60,70,80,90,140,150];u=[0,0,0,.2,.5,1,0,0]
        result=source.prior.layer(z,u,.1);independent=checks.independent(z,u,.1)
        self.assertIsNone(independent['lower']);self.assertEqual(result['core_index'],independent['core'])
        z=[40,50,60,70,80,90,100,110,120,130,140,150,160,170]
        for core in [60,160]:
            speeds=[100 if v==core else 0 for v in z]
            p=source.profile(target['times_utc'][0],target,z=z,raw_u=speeds,quality=[1]*len(z))
            checks.verify_indian_profile(p)
            self.assertIsNone(p['primary_lower_isotach_depth_m'])

    def test_only_this_continuous_site_can_qualify(self):
        for n in [30,31]:
            p=days(n,start='2006-08-01',lon=80.5)
            for r in p:r['sampling_role']='continuous_daily_window'
            runs=source.mark_persistence(p)
            self.assertEqual(len(runs),int(n==31))
            self.assertTrue(all(r['persistent_daily_context_qualified']==(n==31) for r in p))
            if runs:self.assertFalse(runs[0]['physical_continuous_presence_verified'])
        for p in [days(31,lon=90),days(31,lon=80.5)]:
            for r in p:r['sampling_role']='sparse_comparison_only'
            with self.assertRaises(ValueError):source.mark_persistence(p)

    def test_missing_or_weak_day_breaks_runs_without_month_reset(self):
        for p in [days(60,start='2006-08-01',lon=80.5,break_index=30),[r for i,r in enumerate(days(60,start='2006-08-01',lon=80.5)) if i!=30]]:
            for r in p:r['sampling_role']='continuous_daily_window'
            self.assertEqual(source.mark_persistence(p),[])
        p=days(31,start='2006-08-20',lon=80.5)
        for r in p:r['sampling_role']='continuous_daily_window'
        self.assertEqual(source.mark_persistence(p)[0]['end_date'],'2006-09-19')

    def test_upper_reference_gate_is_not_surface_identity_or_physical_volume(self):
        target=source.plan()[0]
        def fast_upper(rows):
            for r in rows:
                if r[5] in [40,50]:r[6]=150
            return rows
        values,_=source.parse_patch(raw_patch(target,fast_upper),target)
        for p in values:
            checks.verify_indian_profile(p)
            self.assertFalse(p['operational_daily_context_candidate'])
            self.assertIsNone(p['physical_current_thickness_m'])
            self.assertIsNone(p['annual_range_m']);self.assertIsNone(p['volume_m3'])
            self.assertFalse(p['true_surface_comparison_verified'])
        p=copy.deepcopy(values[0]);p['physical_current_thickness_m']=100
        with self.assertRaises(ValueError):checks.verify_indian_profile(p)

if __name__=='__main__':unittest.main()
