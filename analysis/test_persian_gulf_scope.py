import copy
import json
import unittest
from pathlib import Path
from check_persian_gulf_scope import validate

ROOT=Path(__file__).resolve().parents[1]

class PersianGulfScopeTests(unittest.TestCase):
    def setUp(self):self.document=json.loads((ROOT/'research/persian-gulf-gogp99-core-scope-audit.json').read_text(encoding='utf-8'))

    def test_reported_dimensions_preserve_water_mass_and_section_scope(self):
        validate(self.document)
        self.assertEqual(self.document['reported_section_distances']['rows'][-1],{'sections':['R01'],'distance_km':920})
        self.assertEqual(len(self.document['reported_local_core_widths']),6)
        self.assertEqual(len(self.document['source_consistency_notes']),3)

    def test_reject_velocity_width_axis_and_annual_relabeling(self):
        for key,value in [('width_metric','velocity_core'),('velocity_boundary_m_s',.1),('fixed_depth_width',True),('whole_current_length_km',920),('whole_current_width_km',60),('annual_width_range_km',[20,60]),('seasonal_route_playback_supported',True),('width_variation_axis','month')]:
            invalid=copy.deepcopy(self.document);invalid[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate(invalid)
        invalid=copy.deepcopy(self.document);invalid['reported_section_distances']['axis_geometry']={'type':'LineString'}
        with self.assertRaises(ValueError):validate(invalid)

    def test_reject_distance_sort_error_and_invented_width_midpoint(self):
        invalid=copy.deepcopy(self.document);invalid['reported_section_distances']['rows'][1]['distance_km']=-1
        with self.assertRaises(ValueError):validate(invalid)
        invalid=copy.deepcopy(self.document);invalid['reported_local_core_widths'][0]['approximate_width_km']=32.5
        with self.assertRaises(ValueError):validate(invalid)

if __name__=='__main__':unittest.main()
