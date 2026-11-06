"""Synthetic contract checks, run only in the sequential cloud case."""
import copy,json,unittest
from pathlib import Path
from verify_northern_toulon_2011_depth_v1 import verify
class Contract(unittest.TestCase):
    def setUp(self):
        self.facts=json.loads((Path(__file__).resolve().parents[1]/'research/northern-toulon-2011-depth-facts-v1.json').read_bytes())
        self.raw=b'''Wind-induced variability in the Northern Current 10.5194/os-14-689-2018
        2-19 December 2011 During Transect 1 (2-4 December)
        zonal geostrophic velocity computed along the transect
        offshore limit and depth of the NC are approximately ~55 km and ~175 m, respectively
        late-summer conditions at the beginning of the experiment
        For the integrated transport computation, the 5 cm Creative Commons Attribution 4.0'''
    def test_local_value_and_actual_roundtrip(self):
        rows,_=verify(self.raw,self.facts);self.assertEqual(json.loads(json.dumps(rows)),rows)
        self.assertEqual(rows[0]['approximate_value'],175)
    def test_source_value_mutation_rejected(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'175',b'250'),self.facts)
    def test_date_is_not_hydrographic_season(self):
        changed=copy.deepcopy(self.facts);changed['row']['calendar_month']=8
        with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_transport_cutoff_borrowing(self):
        changed=copy.deepcopy(self.facts);changed['row']['source_velocity_cutoff_m_s']=0.05
        with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_physical_volume_promotion(self):
        changed=copy.deepcopy(self.facts);changed['row']['eligibility']['volume']=True
        with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_annual_envelope_or_identity_duplication(self):
        for field,value in [('annual_range_m',[175,450]),('entity_id','current:ligurian')]:
            changed=copy.deepcopy(self.facts);changed['row'][field]=value
            with self.assertRaises(ValueError):verify(self.raw,changed)
if __name__=='__main__':unittest.main()
