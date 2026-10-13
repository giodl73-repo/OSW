"""Independent geometric/operator checks for local spans, holes and monthly support."""
import copy
import json
import unittest
from pathlib import Path
from pyproj import Geod
from acquire_basin_surface_sections import build as inventory, validate_config, CONFIG
from build_basin_surface_section_spans import measure, monthly_profiles, build, ROOT, diagnostic_matches

class BasinComponentTests(unittest.TestCase):
    def section(self):
        return {'fixed_axis':'longitude','fixed_coordinate':-30,'varying_axis':'latitude','domain':[-2,2],'peak_search':[-1,1],'component':'eastward'}

    def profile(self, values):
        return [{'coordinate':x,'component_m_s':v} for x,v in zip([-2,-1,0,1,2],values)]

    def test_triangle_crossings_and_independent_geodesic(self):
        r=measure(self.profile([0,.1,.2,.1,0]),self.section(),.5)
        self.assertEqual(r['boundaries']['low_coordinate']['coordinate'],-1)
        self.assertEqual(r['boundaries']['high_coordinate']['coordinate'],1)
        self.assertAlmostEqual(r['span_km'],Geod(ellps='WGS84').inv(-30,-1,-30,1)[2]/1000,places=9)
        self.assertEqual(r['native_cell_spacings'],6)

    def test_no_bridge_over_missing_or_disjoint_peak(self):
        r=measure(self.profile([.3,None,.2,.1,0]),self.section(),.5)
        self.assertEqual(r['boundaries']['low_coordinate']['status'],'missing_before_crossing')
        self.assertIsNone(r['span_km'])
        r=measure(self.profile([.3,0,.2,0,.3]),self.section(),.5)
        self.assertEqual(r['boundaries']['low_coordinate']['coordinate'],-.5)
        self.assertEqual(r['boundaries']['high_coordinate']['coordinate'],.5)

    def test_weak_and_domain_edges_remain_unresolved(self):
        self.assertEqual(measure(self.profile([0,.001,.01,.001,0]),self.section(),.5)['status'],'weak_or_no_eligible_peak')
        r=measure(self.profile([.12,.13,.2,.13,.12]),self.section(),.5)
        self.assertEqual(r['status'],'unresolved_full_span')
        self.assertIsNone(r['span_km'])

    def test_horizontal_span_preserves_actual_latitude(self):
        section={**self.section(),'fixed_axis':'latitude','fixed_coordinate':40,'varying_axis':'longitude'}
        r=measure(self.profile([0,.1,.2,.1,0]),section,.5)
        self.assertAlmostEqual(r['span_km'],Geod(ellps='WGS84').inv(-1,40,1,40)[2]/1000,places=9)
        self.assertEqual(r['boundaries']['low_coordinate']['longitude_latitude'],[-1,40])

    def test_pair_mask_and_southward_sign(self):
        cell={'coordinate':0,'longitude':0,'latitude':40,'eastward_m_s':.1,'northward_m_s':-.2}
        frames=[{'time':f'2013-{month:02d}-{day:02d}T00:00:00Z','samples':[dict(cell)]} for month in range(1,13) for day in [1,6,11,16,21,26]]
        frames[0]['samples'][0]['eastward_m_s']=None
        rows=monthly_profiles({'frames':frames,'component':'southward'})
        self.assertEqual(rows[0]['profile'][0]['paired_source_samples'],5)
        self.assertAlmostEqual(rows[0]['profile'][0]['component_m_s'],.2)
        frames[1]['samples'][0]['northward_m_s']=None
        self.assertIsNone(monthly_profiles({'frames':frames,'component':'southward'})[0]['profile'][0]['component_m_s'])

    def test_source_inventory_and_all_three_frozen_results(self):
        source=inventory()
        self.assertEqual(sum(s['counts']['times']*s['counts']['cells_per_time'] for s in source['sections']),13608)
        for doc in build():
            with self.subTest(current=doc['current_id']):
                self.assertTrue(diagnostic_matches(json.loads((ROOT/'research'/ (doc['section_id']+'-2013-monthly-component-spans.json')).read_bytes()),doc))
                self.assertEqual(len(doc['months']),12)
                self.assertFalse(doc['current_association_verified'])
                self.assertFalse(doc['width_rank_eligible'])
                self.assertFalse(doc['whole_current_representative'])
                self.assertIsNone(doc['annual_width_range_km'])
                for month in doc['months']:
                    self.assertEqual(len(month['threshold_scenarios']),3)
                    nominal=month['nominal']
                    if nominal['span_km'] is not None:
                        a,b=[nominal['boundaries'][side]['longitude_latitude'] for side in ['low_coordinate','high_coordinate']]
                        self.assertAlmostEqual(nominal['span_km'],Geod(ellps='WGS84').inv(*a,*b)[2]/1000,places=8)
                        self.assertLessEqual(nominal['grid_bracket_span_km'][0],nominal['span_km'])
                        self.assertGreaterEqual(nominal['grid_bracket_span_km'][1],nominal['span_km'])

    def test_owner_geography_and_admission_mutations_rejected(self):
        original=json.loads(CONFIG.read_bytes())
        for key,value in [('current_id','gulf-stream-system'),('fixed_coordinate',42),('component','northward')]:
            changed=copy.deepcopy(original);changed['sections'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_config(changed)
        changed=copy.deepcopy(original);changed['whole_current_representative']=True
        with self.assertRaises(ValueError):validate_config(changed)

if __name__=='__main__':
    unittest.main()
