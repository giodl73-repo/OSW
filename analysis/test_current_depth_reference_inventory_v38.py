import copy,csv,io,json,unittest
from pathlib import Path
import load_current_depth_reference_inventory_v38 as m
class Tests(unittest.TestCase):
    def setUp(self):
        self.source=json.loads((Path(__file__).resolve().parents[1]/m.SOURCE).read_bytes())
        self.a={'schema':m.SCHEMA,'id':'norwegian-rudels2026-entering-aw-layer-thickness-v1','source_contexts':{m.CONTEXT:m.context()},'evidence':m.references(self.source),'runtime_changed':False,'full_goal_complete':False}
        self.before={'records':[{'entity_id':'current:norwegian','depth_reference_ids':['old'],'status':'scoped_depth_reference'}],'evidence':[{'id':'old','entity_id':'current:norwegian','metric':'old','unit':'m'}],'source_contexts':{'old-context':{'value':None}}}
    def test_source_fields_and_water_mass_range_preserved(self):
        r=m.references(self.source)[0];self.assertEqual(r['source_descriptor'],self.source['rows'][0])
        for k,v in self.source['rows'][0].items():self.assertEqual(r[k],v)
        self.assertEqual(r['range_m'],[300,400]);self.assertIsNone(r['approximate_value_m']);self.assertIsNone(r['thickness_m'])
    def test_range_owner_and_metric_mutations_rejected(self):
        for k,v in [('water_mass_thickness_range_m',[300,500]),('entity_id','current:norwegian-coastal'),('metric','physical_current_thickness')]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
    def test_review_not_observation_or_branch(self):
        for k,v in [('evidence_kind','direct_observation'),('independent_direct_observation',True),('branch_assignment_performed',True)]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
    def test_no_point_boundary_calendar_thickness_volume(self):
        for k,v in [('approximate_value',350),('lower_boundary_m',400),('calendar_month',1),('thickness_m',350),('volume_m3',1)]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
        for k in m.FALSES:self.assertIs(m.references(self.source)[0][k],False)
    def test_prior_evidence_context_and_status_preserved(self):
        after=m.assemble(self.before,self.a,self.source);self.assertEqual(after['evidence'][:-1],self.before['evidence']);self.assertEqual(after['source_contexts']['old-context'],self.before['source_contexts']['old-context']);self.assertEqual(after['records'][0]['status'],'scoped_depth_reference');self.assertEqual(self.before['records'][0]['depth_reference_ids'],['old'])
    def test_duplicate_unknown_owner_context_rejected(self):
        for kind in ['duplicate','unknown','context']:
            b=copy.deepcopy(self.before)
            if kind=='duplicate':b['evidence'].append(copy.deepcopy(self.a['evidence'][0]))
            elif kind=='unknown':b['records'][0]['entity_id']='current:norwegian-atlantic-slope'
            else:b['source_contexts'][m.CONTEXT]={}
            with self.assertRaises(ValueError):m.assemble(b,self.a,self.source)
    def test_all_csv_fields_roundtrip(self):
        e=self.a['evidence'];back=list(csv.DictReader(io.StringIO(m.reference_csv_bytes(e).decode())))
        self.assertEqual(back[0],{k:m.cell(e[0].get(k)) for k in back[0]});self.assertEqual(back[0]['thickness_m'],'');self.assertEqual(back[0]['approximate_value_m'],'')
    def test_lost_qualification_rejected(self):
        self.a['evidence'][0]['source_qualifications']=[]
        with self.assertRaises(ValueError):m.assemble(self.before,self.a,self.source)
if __name__=='__main__':unittest.main()
