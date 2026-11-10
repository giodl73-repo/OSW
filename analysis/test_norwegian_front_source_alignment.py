"""Check the source audit's geographic, temporal and evidentiary boundaries."""
import hashlib,json,math,unittest
from pathlib import Path
from datetime import datetime
from pyproj import Geod
ROOT=Path(__file__).resolve().parents[1]

class SourceAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.audit=json.loads((ROOT/'research/norwegian-front-glider-source-alignment.json').read_bytes())
    def test_complete_inventory_and_masks(self):
        self.assertEqual(self.audit['generator_sha256'],hashlib.sha256((ROOT/'analysis/build_norwegian_front_source_alignment.py').read_bytes()).hexdigest())
        self.assertEqual([m['profile_count'] for m in self.audit['missions']],[1340,1396])
        self.assertEqual([m['DAC_count'] for m in self.audit['missions']],[673,698])
        self.assertEqual([m['complete_DAC_vectors'] for m in self.audit['missions']],[669,698])
        for mission in self.audit['missions']:
            self.assertEqual(len(mission['profile_positions']),mission['profile_count'])
            self.assertEqual(len(mission['DAC_records']),mission['DAC_count'])
            self.assertEqual(sum(r['vector_magnitude_m_s'] is not None for r in mission['DAC_records']),mission['complete_DAC_vectors'])
            for row in mission['DAC_records']:
                if row['vector_magnitude_m_s'] is not None:self.assertAlmostEqual(row['vector_magnitude_m_s'],math.hypot(row['source_DAC_U_m_s'],row['source_DAC_V_m_s']),places=12)
    def test_independent_position_interpolation(self):
        import bisect
        geod=Geod(ellps='WGS84')
        for mission in self.audit['missions']:
            points=mission['profile_positions'];times=[p['source_epoch_seconds'] for p in points]
            records={r['time']:r for r in mission['DAC_records']}
            for sample in mission['coordinate_comparisons']:
                instant=sample['source_epoch_seconds'];i=max(0,min(len(times)-2,bisect.bisect_right(times,instant)-1));a,b=points[i:i+2];fraction=(instant-times[i])/(times[i+1]-times[i]);lon=a['longitude']+fraction*(b['longitude']-a['longitude']);lat=a['latitude']+fraction*(b['latitude']-a['latitude']);actual=records[sample['time']]
                self.assertAlmostEqual(sample['offset_km'],geod.inv(actual['longitude'],actual['latitude'],lon,lat)[2]/1000,places=7)
    def test_internal_agreement_is_not_paper_reproduction(self):
        for key in ['current_association_verified','corrected_paper_reproduction_verified']:self.assertIs(self.audit[key],False)
        for key in ['whole_current_width_km','whole_current_length_km','annual_width_range_km']:self.assertIsNone(self.audit[key])
        self.assertEqual(self.audit['seasonal_width_samples'],[])
    def test_component_metadata_conflict_remains_visible(self):
        for mission in self.audit['missions']:
            u=mission['variable_metadata']['DAC_U'];self.assertEqual(u['standard_name'],'eastward_sea_water_velocity');self.assertIn('northward',u['long_name'])
        self.assertIn('Direction validation remains open',self.audit['source_metadata_conflict'])
if __name__=='__main__':unittest.main()
