"""Final readback preserves source bits and full-precision decision outcomes."""
import copy
import math
import unittest
from unittest.mock import patch
import eac_core_readback as readback
import build_eac_section_core_spans as core


def fixture(peak=1.2345678912345):
    values=[0.,peak,0.];distance=[0.,1000.123456789,2000.345678901]
    scenario=core.measure(distance,values,[None]*3)
    scenario['peak_source_components']={'UCUR':.1234567891234567,'VCUR':-0.0,
        'section_normal_central_m_s':peak,'section_tangent_m_s':.1234567891234567,
        'bearing_deg':123.123456789,'tangent_to_normal_ratio_not_width_correction':.1234567891234567}
    return {'schema':'osw.eac-section-core-spans.v1','input_sha256':{'source.npz':'source-pin'},
        'geometry':{'distance_m':distance,'forward_bearing_deg':[123.123456789]*3,
            'longitude_latitude_points':[[153.123456789123,-27.123456789123]],'bottom_depth_m':[.1234567891234567]},
        'profiles':[{'source_time_index':0,'source_time_utc':'2012-01-01T00:00:00Z',
            'section_normal_velocity_m_s':values,'projected_supplied_magnitudes_m_s':[None,.1234567891234567,0.],
            'scenarios':{'central':scenario},'new_unselected_numeric_field':.1234567891234567}],
        'overall_outcomes':[],'monthly_summaries':[],'physical_width_admitted':False,
        'annual_width_range_km':None}


class EacCoreReadbackTests(unittest.TestCase):
    def test_original_fields_and_decisions_preserved_without_mutation(self):
        source=fixture();before=copy.deepcopy(source);actual=readback.canonicalize(source)
        self.assertEqual(source,before)
        self.assertEqual(actual['geometry']['longitude_latitude_points'],source['geometry']['longitude_latitude_points'])
        self.assertEqual(actual['geometry']['bottom_depth_m'],source['geometry']['bottom_depth_m'])
        self.assertEqual(actual['geometry']['distance_m'],[round(v,3) for v in source['geometry']['distance_m']])
        a=actual['profiles'][0];b=source['profiles'][0]
        self.assertEqual(a['new_unselected_numeric_field'],b['new_unselected_numeric_field'])
        self.assertEqual(a['source_time_utc'],b['source_time_utc'])
        for field in ['UCUR','VCUR']:
            self.assertEqual(a['scenarios']['central']['peak_source_components'][field].hex(),
                b['scenarios']['central']['peak_source_components'][field].hex())
        for x,y in zip(a['scenarios']['central']['cases'],b['scenarios']['central']['cases']):
            for field in ['fraction','primary_fraction','status','rounded_section_span_km']:self.assertEqual(x[field],y[field])
            for side in ['shoreward_edge','offshore_edge']:
                for field in ['status','inside_index','outside_index','indices_in_distance_order']:self.assertEqual(x[side][field],y[side][field])
        self.assertFalse(actual['physical_width_admitted']);self.assertIsNone(actual['annual_width_range_km'])

    def test_near_floor_decision_not_recomputed_from_rounded_velocity(self):
        source=fixture(.2999999999);actual=readback.canonicalize(source)
        scenario=actual['profiles'][0]['scenarios']['central']
        self.assertEqual(scenario['peak_component_m_s'],.3)
        self.assertTrue(all(c['status']=='unresolved_peak_below_0_3_m_s' and c['section_span_km'] is None for c in scenario['cases']))
        self.assertEqual(source['profiles'][0]['scenarios']['central']['peak_component_m_s'],.2999999999)

    def test_changed_protocol_schema_or_invalid_selected_value_rejects(self):
        with patch.object(readback,'PROTOCOL_SHA','0'*64),self.assertRaisesRegex(ValueError,'readback protocol'):
            readback.canonicalize(fixture())
        wrong=fixture();wrong['schema']='unknown'
        with self.assertRaisesRegex(ValueError,'schema'):readback.canonicalize(wrong)
        for value in [math.nan,math.inf,True,'1.0']:
            with self.subTest(value=value):
                source=fixture();source['geometry']['distance_m'][1]=value
                with self.assertRaisesRegex(ValueError,'Invalid EAC'):readback.canonicalize(source)

    def test_v1_halfway_fraction_has_stable_v2_readback(self):
        low=math.nextafter(.245473105,0.);high=math.nextafter(.245473105,math.inf)
        self.assertNotEqual(round(low,8),round(high,8))
        actual=[]
        for value in [low,high]:
            source=fixture();case=source['profiles'][0]['scenarios']['central']['cases'][0]
            case['offshore_edge']['fraction_inside_to_outside']=value
            result=readback.canonicalize(source)['profiles'][0]['scenarios']['central']['cases'][0]
            actual.append(result['offshore_edge']['fraction_inside_to_outside'])
            self.assertEqual(result['section_span_km'],round(case['section_span_km'],6))
            self.assertEqual(result['status'],case['status'])
        self.assertEqual(actual,[.2454731,.2454731])


if __name__=='__main__':unittest.main()
