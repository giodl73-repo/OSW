import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v16 as v16
from build_current_depth_reference_inventory_v53 import PREVIOUS,CONTEXT,REFERENCE_ID,verify_facts,references,validate_rows,assemble,DOI,URL,OWNER,SCOPE
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'id':CONTEXT,'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'source_text_excerpt':'200\u2013400 m deep','reported_range_m':[200,400],'cited_source':'Benzohra and Millot(1995a)','cited_original_reviewed':False,'range_is_this_papers_new_observation':False,'source_observed_period':None,'source_depth_cutoff_rule':None,'range_is_seasonal_extrema':False,'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0,'source_citation':'Synthetic'}

class CitedRangeTests(unittest.TestCase):
    def test_predecessor_and_reservation_before_conversion(self):
        self.assertEqual(PREVIOUS,'research/current-depth-reference-inventory-v52.json');charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[2])
        with patch('build_current_depth_reference_inventory_v53.int',side_effect=AssertionError('unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_secondhand_range_cannot_become_new_measurement(self):
        for change in [{'cited_original_reviewed':True},{'range_is_this_papers_new_observation':True},{'source_observed_period':['1997','2002']},{'source_depth_cutoff_rule':0.1},{'range_is_seasonal_extrema':True},{'reported_range_m':[100,400]},{'entity_id':'current:west-australian'}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_no_midpoint_thickness_error_season_or_width_join(self):
        for change in [{'approximate_value_m':300},{'thickness_m':200},{'annual_range_m':[200,400]},{'uncertainty_m':100},{'observed_period':['1997','2002']},{'volume_eligible':True},{'evidence_kind':'direct_velocity_measurement'},{'same_source_width_reference_id':'30-50km'}]:
            rows=references(facts(),'a'*64);rows[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_all934_prior_refs_context_calendar_and_owner_fields_preserved(self):
        records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior':True} for i in range(111)]
        old={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'prior','unit':'dbar' if i<4 else 'm'} for i in range(934)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'prior':True}]};refresh(old)
        new=assemble(old,facts(),'a'*64);self.assertEqual(new['evidence'][:-1],old['evidence']);self.assertEqual(new['counts']['depth_references'],935);self.assertEqual(new['coordinate_unit_counts'],{'dbar':4,'m':931});self.assertEqual(new['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],new['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
        old['evidence'][0]['source_doi']=DOI
        with self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_complete_csv_and_json_parity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_exact_typed_predecessor(self):
        with patch.object(v16,'previous',return_value={'old':True}):self.assertEqual(v16.load_inventory({'schema':'old'},lambda p:b''),{'old':True})
        with patch.object(v16,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v16.load_inventory({'schema':'osw.current-depth-reference-inventory.v53','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
