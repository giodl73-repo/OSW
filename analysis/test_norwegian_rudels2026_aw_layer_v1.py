import copy,json,unittest
from pathlib import Path
from verify_norwegian_rudels2026_aw_layer_v1 import verify
class Tests(unittest.TestCase):
    def setUp(self):
        self.facts=json.loads((Path(__file__).resolve().parents[1]/'research/norwegian-rudels2026-aw-layer-facts-v1.json').read_bytes())
        self.raw=b'''The circulation and water mass 10.5194/os-22-3287-2026
        thickness of the Atlantic water layer entering the Norwegian Sea is 300-400 m
        Atlantic water flows north as the Norwegian Atlantic Current in two branches
        One follows the continental slope second branch separates from the slope at the
        Creative Commons Attribution 4.0'''
    def test_range_and_actual_roundtrip(self):
        rows,_=verify(self.raw,self.facts);self.assertEqual(rows,json.loads(json.dumps(rows)));self.assertEqual(rows[0]['water_mass_thickness_range_m'],[300,400])
    def test_source_range_mutation_rejected(self):
        with self.assertRaises(ValueError):verify(self.raw.replace(b'300-400',b'300-500'),self.facts)
    def test_sill_depth_alone_does_not_qualify(self):
        with self.assertRaises(ValueError):verify(b'The circulation and water mass 10.5194/os-22-3287-2026 silldepth500m',self.facts)
    def test_no_physical_thickness_or_lower_boundary(self):
        for k,v in [('metric','physical_current_thickness'),('thickness_m',350),('lower_boundary_m',400)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
    def test_parent_not_copied_to_branch(self):
        for k,v in [('entity_id','current:norwegian-atlantic-slope'),('branch_assignment_performed',True)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
    def test_review_not_new_observation_or_season(self):
        for k,v in [('evidence_kind','direct_observation'),('independent_direct_observation',True),('calendar_month',1)]:
            f=copy.deepcopy(self.facts);f['row'][k]=v
            with self.assertRaises(ValueError):verify(self.raw,f)
if __name__=='__main__':unittest.main()
