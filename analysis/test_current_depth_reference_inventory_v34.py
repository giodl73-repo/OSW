import copy,hashlib,io,json,csv,unittest
from pathlib import Path
import load_current_depth_reference_inventory_v34 as m
ROOT=Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
    def setUp(self):
        self.source=json.loads((ROOT/m.SOURCE).read_bytes())
        self.a={'schema':m.SCHEMA,'id':'oman-2025-published-plume-descriptors-v1','source_contexts':{m.CONTEXT:m.context()},'evidence':m.references(self.source),'runtime_changed':False,'full_goal_complete':False}
        self.before={'records':[{'entity_id':'current:persian-gulf-saline-overflow','depth_reference_ids':['old'],'status':'scoped_depth_reference'}],'evidence':[{'id':'old','entity_id':'current:persian-gulf-saline-overflow','metric':'existing','unit':'m'}],'source_contexts':{'old-context':{'value':None}}}
    def test_exact_metric_split_and_ranges(self):
        rows=m.references(self.source)
        self.assertEqual([r['range_m'] for r in rows],[[50,100],None,[130,140],[10,30],None])
        self.assertEqual([r['approximate_value_m'] for r in rows],[None,170,None,None,200])
        self.assertEqual(rows[3]['vertical_datum'],'not_applicable_thickness_distance')
        self.assertNotEqual(rows[0]['metric'],rows[3]['metric'])
    def test_old_evidence_context_and_owner_preserved(self):
        after=m.assemble(self.before,self.a,self.source)
        self.assertEqual(after['evidence'][:1],self.before['evidence']);self.assertEqual(after['source_contexts']['old-context'],self.before['source_contexts']['old-context'])
        self.assertEqual(self.before['records'][0]['depth_reference_ids'],['old']);self.assertEqual(after['records'][0]['status'],'scoped_depth_reference')
    def test_no_physical_temporal_volume_promotion(self):
        for r in m.references(self.source):
            for k in m.FALSES:self.assertIs(r[k],False)
            for k in ['annual_range_m','upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','calendar_months']:self.assertIsNone(r[k])
    def test_selection_change_rejected(self):
        self.source['rows'][0]['selection_fraction']=0.55
        with self.assertRaises(ValueError):m.references(self.source)
    def test_dates_owner_and_boundary_change_rejected(self):
        for key,val in [('current_id','current:norwegian'),('survey_start','2025-01-01'),('lower_boundary_depth_m',200),('exact_position',[56,24])]:
            s=copy.deepcopy(self.source);s['rows'][0][key]=val
            with self.assertRaises(ValueError):m.references(s)
    def test_maximum_not_zero_based_range(self):
        self.source['rows'][1]['minimum_m']=0
        with self.assertRaises(ValueError):m.references(self.source)
    def test_duplicate_or_unknown_owner_rejected(self):
        for change in ['duplicate','unknown']:
            before=copy.deepcopy(self.before)
            if change=='duplicate':before['evidence'].append(copy.deepcopy(self.a['evidence'][0]))
            else:before['records'][0]['entity_id']='current:norwegian'
            with self.assertRaises(ValueError):m.assemble(before,self.a,self.source)
    def test_all_csv_fields_and_null_semantics(self):
        rows=self.a['evidence'];back=list(csv.DictReader(io.StringIO(m.reference_csv_bytes(rows).decode())))
        for row,e in zip(back,rows):self.assertEqual(row,{k:m.cell(e.get(k)) for k in row})
        self.assertEqual(back[1]['range_m'],'');self.assertEqual(back[1]['approximate_value_m'],'170')
    def test_qualifier_change_rejected(self):
        self.a['evidence'][0]['source_caveats']=[]
        with self.assertRaises(ValueError):m.assemble(self.before,self.a,self.source)
    def test_restricted_data_discrepancy_preserved(self):
        c=m.context();self.assertEqual(c['paper_profile_count'],51);self.assertEqual(c['restricted_repository_profile_count'],52);self.assertIs(c['profile_count_discrepancy_resolved'],False);self.assertIs(c['raw_CTD_fields_inspected'],False)
if __name__=='__main__':unittest.main()
