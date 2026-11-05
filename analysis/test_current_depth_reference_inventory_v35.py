import copy,csv,io,json,unittest
from pathlib import Path
import load_current_depth_reference_inventory_v35 as m
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
    def setUp(self):
        self.source=json.loads((ROOT/m.SOURCE).read_bytes())
        self.a={'schema':m.SCHEMA,'id':'pratt2000-hanish-mean-interface-depths-v1','source_contexts':{m.CONTEXT:m.context()},'evidence':m.references(self.source),'runtime_changed':False,'full_goal_complete':False}
        self.before={'records':[{'entity_id':'current:red-sea-saline-overflow','depth_reference_ids':['old'],'status':'scoped_depth_reference'}],'evidence':[{'id':'old','entity_id':'current:red-sea-saline-overflow','metric':'old','unit':'m'}],'source_contexts':{'old-context':{'value':None}}}
    def test_two_reported_endpoints_and_statistic(self):
        r=m.references(self.source);self.assertEqual([x['approximate_value_m'] for x in r],[35,110]);self.assertEqual([x['source_season_label'] for x in r],['winter','summer']);self.assertTrue(all('monthly_mean' in x['metric'] for x in r))
    def test_every_original_source_field_preserved(self):
        for r,s in zip(m.references(self.source),self.source['rows']):
            self.assertEqual(r['source_descriptor'],s)
            for k,v in s.items():self.assertEqual(r[k],v)
    def test_no_physical_or_calendar_promotion(self):
        for r in m.references(self.source):
            for k in m.FALSES:self.assertIs(r[k],False)
            for k in ['upper_boundary_m','lower_boundary_m','thickness_m','range_m','annual_range_m','uncertainty_m','calendar_month','calendar_months','paired_lower_boundary_m']:self.assertIsNone(r[k])
    def test_changed_values_and_labels_rejected(self):
        for k,v in [('approximate_value_m',30),('source_season_label','annual_minimum')]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
    def test_changed_mean_statistic_or_owner_rejected(self):
        for k,v in [('source_statistic','mean_individual_crossings'),('metric','physical_current_depth'),('entity_id','current:norwegian')]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
    def test_physical_pair_calendar_or_range_rejected(self):
        for k,v in [('calendar_month',1),('thickness_m',115),('range_m',[35,110]),('paired_lower_boundary_m',150),('volume_eligible',True)]:
            s=copy.deepcopy(self.source);s['rows'][0][k]=v
            with self.assertRaises(ValueError):m.references(s)
    def test_prior_evidence_context_and_owner_preserved(self):
        after=m.assemble(self.before,self.a,self.source);self.assertEqual(after['evidence'][:-2],self.before['evidence']);self.assertEqual(after['source_contexts']['old-context'],self.before['source_contexts']['old-context']);self.assertEqual(self.before['records'][0]['depth_reference_ids'],['old']);self.assertEqual(after['records'][0]['status'],'scoped_depth_reference')
    def test_duplicate_or_unknown_owner_rejected(self):
        for kind in ['duplicate','unknown']:
            b=copy.deepcopy(self.before)
            if kind=='duplicate':b['evidence'].append(copy.deepcopy(self.a['evidence'][0]))
            else:b['records'][0]['entity_id']='current:norwegian'
            with self.assertRaises(ValueError):m.assemble(b,self.a,self.source)
    def test_all_csv_fields_and_qualifiers_roundtrip(self):
        e=self.a['evidence'];back=list(csv.DictReader(io.StringIO(m.reference_csv_bytes(e).decode())))
        for r,s in zip(back,e):self.assertEqual(r,{k:m.cell(s.get(k)) for k in r})
        self.assertEqual(back[0]['calendar_month'],'');self.assertEqual(back[1]['approximate_value_m'],'110')
    def test_lost_qualification_rejected(self):
        self.a['evidence'][0]['source_qualifications']=[]
        with self.assertRaises(ValueError):m.assemble(self.before,self.a,self.source)
if __name__=='__main__':unittest.main()
