import copy
import csv
import io
import json
import unittest
from datetime import datetime,timedelta
from pathlib import Path
import collect_indian_euc_rama_2005_depth_v1 as source

ROOT=Path(__file__).resolve().parents[1]


def raw_patch(target,modify=None):
    rows=[]
    speeds={40:-10,50:-10,60:0,70:20,80:40,90:80,100:100,110:80,120:50,130:20,140:0}
    for date in target['times_utc']:
        for z in range(40,301,10):rows.append(['RAMA','actual-site',target['nominal_longitude'],0,date,z,speeds.get(z,-10),1])
    if modify:rows=modify(rows)
    buffer=io.StringIO();w=csv.writer(buffer);w.writerow(source.frozen.FIELDS);w.writerow(source.frozen.UNITS);w.writerows(rows)
    return buffer.getvalue().encode('iso8859-1')


def days(n,start='2005-02-01',lon=90,break_index=None):
    return [{'nominal_station':{'longitude':lon},'time_center_utc':(datetime.fromisoformat(start)+timedelta(days=i)).date().isoformat()+'T12:00:00Z',
             'operational_daily_context_candidate':i!=break_index,'primary_lower_isotach_depth_m':135} for i in range(n)]


class IndianDailyPilot(unittest.TestCase):
    def test_preflight_disjoint_global_scope_and_cached_metadata(self):
        targets,metadata=source.preflight()
        self.assertEqual(len(targets),8);self.assertEqual(sum(len(t['times_utc']) for t in targets),132)
        self.assertEqual(sum(t['reserved_numeric_scalars'] for t in targets),23760)
        self.assertEqual(metadata['units'],'cm/s')
        self.assertEqual([len(t['times_utc']) for t in targets[:4]],[28,31,30,31])
        self.assertTrue(all(len(t['times_utc'])==3 for t in targets[4:]))
        self.assertLessEqual(132*(30+10),5400)

    def test_monthly_parser_returns_all_days_and_observed_lower_proxy(self):
        target=source.plan()[0];p,n=source.parse_patch(raw_patch(target),target)
        self.assertEqual(len(p),28);self.assertEqual(n,28*27*6)
        self.assertEqual(p[0]['primary_lower_isotach_depth_m'],135)
        self.assertEqual(p[0]['primary_threshold_layer_span_m'],70)
        self.assertTrue(p[0]['operational_daily_context_candidate'])
        self.assertEqual(p[0]['threshold_contexts'][1]['core_search_depth_interval_m'],[60,160])
        self.assertIsNone(p[0]['physical_current_thickness_m'])
        self.assertFalse(p[0]['daily_underlying_sample_coverage_verified'])

    def test_missing_day_is_not_gap_filled(self):
        target=source.plan()[0]
        p,_=source.parse_patch(raw_patch(target,lambda rows:[r for r in rows if '02-15' not in r[4]]),target)
        self.assertEqual(p[14]['source_status'],'no_source_rows_for_predeclared_day')
        self.assertIsNone(p[14]['primary_lower_isotach_depth_m']);self.assertFalse(p[14]['operational_daily_context_candidate'])

    def test_quality_fill_and_lower_censor_preserved(self):
        target=source.plan()[0]
        def reject(rows):
            for r in rows:
                if r[5]==130:r[-1]=3
            return rows
        p,_=source.parse_patch(raw_patch(target,reject),target)
        self.assertIsNone(p[0]['primary_lower_isotach_depth_m'])
        self.assertEqual(p[0]['threshold_contexts'][1]['lower_status'],'censored_before_missing_or_dry_level')
        self.assertIsNone(source.frozen.decode('1e35',1))

    def test_rejected_upper_reference_does_not_invent_a_surface_comparison(self):
        target=source.plan()[0]
        def reject(rows):
            for r in rows:
                if r[5]==40:r[-1]=0
            return rows
        p,_=source.parse_patch(raw_patch(target,reject),target)
        self.assertEqual(p[0]['primary_lower_isotach_depth_m'],135)
        self.assertFalse(p[0]['operational_daily_context_candidate'])
        self.assertFalse(p[0]['true_surface_comparison_verified'])

    def test_surface_jet_extension_is_not_an_operational_undercurrent_candidate(self):
        target=source.plan()[0]
        def fast_upper(rows):
            for r in rows:
                if r[5] in [40,50]:r[6]=150
            return rows
        p,_=source.parse_patch(raw_patch(target,fast_upper),target)
        self.assertFalse(p[0]['operational_daily_context_candidate'])
        self.assertEqual(p[0]['operational_daily_context_status'],'insufficient_observed_subsurface_contrast')

    def test_locked_core_first_tie_and_depth_gap(self):
        z=list(range(40,201,10));u=[0.0]*len(z)
        for depth,value in [(80,.5),(90,1),(100,.5),(130,.5),(140,1),(150,.5)]:u[z.index(depth)]=value
        r=source.layer(z,u,.1);self.assertEqual(r['core_depth_m'],90);self.assertLess(r['lower_depth_m'],120)
        r=source.layer([40,50,60,70,80,90,140,150],[0,0,0,.2,.5,1,0,0],.1)
        self.assertEqual(r['core_depth_m'],90);self.assertIsNone(r['lower_depth_m'])
        self.assertEqual(r['lower_status'],'censored_at_returned_depth_gap')

    def test_context_gate_duration_requires31_daily_labels_across_month_boundary(self):
        p=days(30);self.assertEqual(source.mark_persistence(p),[])
        self.assertFalse(any(r['persistent_daily_context_qualified'] for r in p))
        p=days(31);runs=source.mark_persistence(p)
        self.assertEqual(len(runs),1);self.assertEqual(runs[0]['end_date'],'2005-03-03')
        self.assertTrue(all(r['persistent_daily_context_qualified'] for r in p))
        self.assertFalse(runs[0]['physical_continuous_presence_verified'])

    def test_missing_or_weak_day_breaks_persistence(self):
        for p in [days(60,break_index=30),[r for i,r in enumerate(days(60)) if i!=30]]:
            self.assertEqual(source.mark_persistence(p),[])

    def test_sparse_site_never_borrows_continuous_site_persistence(self):
        p=days(40)+days(40,lon=80.5)
        source.mark_persistence(p)
        self.assertTrue(all(r['persistent_daily_context_qualified'] for r in p[:40]))
        self.assertTrue(all(r['persistent_daily_context_qualified'] is None for r in p[40:]))
        self.assertTrue(all(r['persistent_context_lower_isotach_depth_m'] is None for r in p[40:]))

    def test_duplicate_wrong_date_coordinate_or_unreliable_depth_rejected(self):
        target=source.plan()[0]
        def wrong_date(rows):rows[0][4]='2005-01-01T12:00:00Z';return rows
        def wrong_site(rows):rows[0][2]=91;return rows
        def wrong_depth(rows):rows[0][5]=30;return rows
        for modify in [lambda rows:rows+[rows[0]],wrong_date,wrong_site,wrong_depth]:
            with self.assertRaises(ValueError):source.parse_patch(raw_patch(target,modify),target)

    def test_global_node_scalar_and_transport_caps_do_not_reset(self):
        op=json.loads((ROOT/source.OP).read_bytes())
        self.assertEqual(op['maximum_http_requests'],8)
        self.assertEqual(op['field_scalar_reserve'],23760)
        self.assertEqual(op['global_scalar_reserve'],24760)
        self.assertEqual(op['global_node_reserve'],5400)
        self.assertLessEqual(op['global_node_reserve'],6000)
        self.assertEqual(op['maximum_attempts_per_target'],1)
        self.assertEqual(op['programme_deadline_seconds'],210)


if __name__=='__main__':unittest.main()
