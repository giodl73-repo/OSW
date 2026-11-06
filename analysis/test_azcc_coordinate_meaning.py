"""Coordinate positions cannot be promoted to a range of current widths."""
import copy,unittest
from build_azcc_coordinate_meaning_figure import load,validate,svg

class MeaningTests(unittest.TestCase):
    def test_coordinate_arithmetic_and_unknown_current_width(self):
        doc=load();a=doc['coordinate_arithmetic']
        self.assertEqual(a['upper_section_coordinate_km']-a['lower_section_coordinate_km'],150)
        self.assertIsNone(doc['current_width_km']);self.assertIsNone(doc['current_width_range_km'])
        self.assertFalse(a['difference_is_verified_velocity_boundary_span'])
        self.assertIn('Coordinate difference: 150 km',svg(doc))
    def test_promoted_width_or_range_rejected(self):
        for key,value in [('current_width_km',150),('current_width_range_km',[100,250]),('annual_width_range_km',[100,250]),('width_rank_eligible',True),('seasonal_playback_eligible',True)]:
            with self.subTest(key=key):
                doc=copy.deepcopy(load());doc[key]=value
                with self.assertRaises(ValueError):validate(doc)
    def test_source_coordinate_mutation_rejected(self):
        doc=copy.deepcopy(load());doc['coordinate_arithmetic']['lower_section_coordinate_km']=0
        with self.assertRaises(ValueError):validate(doc)

if __name__=='__main__':unittest.main()
