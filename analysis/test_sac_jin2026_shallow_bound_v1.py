import copy,json,unittest
from pathlib import Path
from verify_sac_jin2026_shallow_bound_v1 import verify
class Contract(unittest.TestCase):
    def setUp(self):
        self.facts=json.loads((Path(__file__).resolve().parents[1]/'research/sac-jin2026-shallow-bound-facts-v1.json').read_bytes())
        self.raw=b'''Projected Future Changes of Australian Boundary Currents 10.1029/2026JC024251
        weak and steady SAC has shallow structure (&lt;250 m)
        Historical Mean Transports (1993-2023) SAC 122E 34-35S 250m eastward
        future2071-2090 CMIP6'''
    def test_strict_bound_and_actual_roundtrip(self):
        rows,_=verify(self.raw,self.facts);self.assertEqual(rows,json.loads(json.dumps(rows)));self.assertTrue(rows[0]['upper_bound_exclusive']);self.assertIsNone(rows[0]['approximate_value'])
    def test_source_bound_change_rejected(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'&lt;250',b'&lt;300'),self.facts)
    def test_only_transport_limit_does_not_qualify(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'weak and steady SAC has shallow structure (&lt;250 m)',b''),self.facts)
    def test_no_exact_value_or_inclusive_bound(self):
        for k,v in [('approximate_value',250),('upper_bound_exclusive',False)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
    def test_no_legacy_intersection_or_physical_bottom(self):
        for k,v in [('combined_with_legacy_over200m_as_range',True),('range_m',[200,250]),('transport_integration_limit_is_current_bottom',True)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
    def test_no_calendar_thickness_or_volume(self):
        for k,v in [('calendar_month',6),('thickness_m',250),('volume_m3',1)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
if __name__=='__main__':unittest.main()
