import io
import itertools
import json
import math
import unittest
import numpy as np
import collect_norkyst_jutland_calendar_months_v1 as m


class CalendarCollection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan,cls.op=m.load()

    def fixture(self):
        target=self.plan['request_plan'][0].copy();target.update(first_hour=0,last_hour=2,hourly_profiles=3)
        point=self.plan['fixed_points'][target['point_index']];n=3;parts=[]
        for field in ['u_eastward','v_northward']:
            text=field+'.'+field+'[3][11][1][1]\n'
            for t,k,y in itertools.product(range(3),range(11),range(1)):
                value=-32767 if field=='u_eastward' and t==1 and k==10 else 100
                text+=f'[{t}][{k}][{y}], {value}\n'
            text+='\n'
            maps={'time':[m.datetime.fromisoformat(target['date']+f'T{h:02d}:00:00+00:00').timestamp() for h in range(3)],'depth':m.DEPTH,
                  'Y':[point['source_y_index']*800],'X':[point['source_x_index']*800]}
            for axis,values in maps.items():text+=field+'.'+axis+'['+str(len(values))+']\n'+', '.join(map(str,values))+'\n\n'
            parts.append(text)
        return ''.join(parts).encode(),target,point

    def test_complete_paired_response_and_fill(self):
        raw,target,point=self.fixture();q=m.parse(raw,target,point)
        self.assertEqual(q.shape,(3,11));self.assertAlmostEqual(q[0,0],.2/math.sqrt(2))
        self.assertTrue(np.isnan(q[1,10]))

    def test_coordinate_maps_verified_without_duplicate_numeric_decode(self):
        raw,target,point=self.fixture();raw=raw.replace(b'v_northward.X[1]\n'+str(point['source_x_index']*800).encode(),b'v_northward.X[1]\n999')
        with self.assertRaises(ValueError):m.parse(raw,target,point)

    def test_changed_hours_or_missing_rows_rejected(self):
        raw,target,point=self.fixture()
        with self.assertRaises(ValueError):m.parse(raw.replace(b'[0][0][0], 100\n',b'',1),target,point)
        changed=target.copy();changed['date']='2024-03-02'
        with self.assertRaises(ValueError):m.parse(raw,changed,point)

    def test_no_duplicate_profile_assignment_even_if_all_missing(self):
        q=np.full((3,4,11),np.nan);assigned=np.zeros((3,4),bool);values=np.full((1,11),np.nan)
        m.assign(q,assigned,0,[0],values)
        self.assertTrue(assigned[0,0])
        with self.assertRaises(ValueError):m.assign(q,assigned,0,[0],values)

    def test_partial_numeric_month_never_yields_partial_mean(self):
        q=np.full((4,11),.2);q[0,0]=np.nan;r=m.statistics(q)
        self.assertEqual(r['paired_finite_hours'][0],3);self.assertIsNone(r['mean'][0])
        self.assertIsNone(r['p95'][0]);self.assertAlmostEqual(r['mean'][1],.2)
        self.assertFalse(r['primary_fixed_point_eligible'])

    def test_mean_field_not_mean_of_instantaneous_depths(self):
        q=np.array([[.2]*11,[-.2]*11]);r=m.statistics(q)
        self.assertEqual(r['mean'],[0.]*11);self.assertIsNone(r['primary_mean_field_depth_descriptor'])
        self.assertFalse(r['monthly_mean_is_mean_of_instantaneous_depths'])

    def test_resolved_mean_component_contour_not_physical_thickness(self):
        q=np.tile([.3]*9+[0.,0.],(4,1));r=m.statistics(q);p=r['primary_mean_field_depth_descriptor']
        self.assertTrue(r['primary_fixed_point_eligible']);self.assertAlmostEqual(p['lower_depth_m'],25+25*2/3)
        self.assertIsNone(r['physical_current_thickness_m']);self.assertIsNone(r['volume_m3'])

    def test_domain_censor_retains_unknown_bottom(self):
        r=m.statistics(np.full((4,11),.2));p=r['primary_mean_field_depth_descriptor']
        self.assertEqual(p['lower_status'],'censored_at_sample_domain_edge')
        self.assertEqual(p['lower_last_connected_depth_m'],65);self.assertIsNone(p['lower_depth_m'])
        self.assertIsNone(p['layer_thickness_m'])

    def test_population_temporal_variability(self):
        r=m.statistics(np.array([[0.]*11,[2.]*11]))
        self.assertEqual(r['mean'],[1.]*11);self.assertEqual(r['population_standard_deviation'],[1.]*11)
        self.assertEqual(r['median'],[1.]*11)

    def test_transport_timeout_one_attempt_only(self):
        target=self.plan['request_plan'][0];calls=[];receipt={}
        def fail(*a,**k):calls.append(1);raise TimeoutError('synthetic')
        with self.assertRaises(TimeoutError):m.retrieve(target,receipt,fail)
        self.assertEqual(calls,[1]);self.assertEqual(receipt['status'],'failed_no_retry')

    def test_transport_body_cap(self):
        target=self.plan['request_plan'][0]
        class Response(io.BytesIO):
            status=200;url=target['http_url'];headers={}
        receipt={}
        with self.assertRaises(ValueError):m.retrieve(target,receipt,lambda *a,**k:Response(b'0'*18001))
        self.assertEqual(receipt['bytes_received'],18001)

    def test_frozen_whole_programme_budget_and_reuse(self):
        self.assertEqual(self.plan['budget']['combined_reserved_decoded_scalars'],246018)
        self.assertEqual(len(self.plan['reused_prior_noon_profiles']),12)
        self.assertEqual(len(self.plan['request_plan']),378)


if __name__=='__main__':unittest.main()
