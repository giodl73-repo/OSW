"""Cloud-only source-context and semantic checks using synthetic HTML."""
import copy,json,unittest
from pathlib import Path
from verify_azores_ibi_mean_depth_v1 import verify
class Contract(unittest.TestCase):
    def setUp(self):
        self.facts=json.loads((Path(__file__).resolve().parents[1]/'research/azores-ibi-mean-depth-facts-v1.json').read_bytes())
        self.raw=b'''Monitoring main ocean currents of the Iberia 10.5194/sp-4-osr8-5-2024
        meridional section north of Madeira monitors Azores Current
        eastward transport seen in upper layers (up to 600 m depth)
        below 600 m depth transports are strongly influenced by bathymetry
        computed from IBI-REA over the period 1993-2021
        vertical boundaries of the monitoring windows are dynamic
        westward zonal surface flows known as Azores Current
        Creative Commons Attribution 4.0'''
    def test_reported_mean_extent_roundtrip(self):
        rows,_=verify(self.raw,self.facts);self.assertEqual(json.loads(json.dumps(rows)),rows);self.assertEqual(rows[0]['approximate_value'],600)
    def test_changed_source_depth_rejected(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'600',b'500'),self.facts)
    def test_missing_conflicting_direction_context_rejected(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'westward',b'eastward'),self.facts)
    def test_no_observational_or_ensemble_mean_relabel(self):
        changed=copy.deepcopy(self.facts);changed['row']['source_product']='five_product_observed_depth'
        with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_invented_season_or_mean_of_boundaries(self):
        for k,v in [('calendar_month',6),('source_mean_period',[2000,2021]),('metric','mean_individual_current_depths')]:
            changed=copy.deepcopy(self.facts);changed['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_fixed_omi_boundary(self):
        changed=copy.deepcopy(self.facts);changed['row']['omi_boundary_is_fixed_at_reported_extent']=True
        with self.assertRaises(ValueError):verify(self.raw,changed)
    def test_no_physical_range_volume_or_direction_promotion(self):
        for k,v in [('thickness_m',600),('annual_range_m',[0,600]),('source_direction_consistency','verified_eastward')]:
            changed=copy.deepcopy(self.facts);changed['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,changed)
        changed=copy.deepcopy(self.facts);changed['row']['eligibility']['volume']=True
        with self.assertRaises(ValueError):verify(self.raw,changed)
if __name__=='__main__':unittest.main()
