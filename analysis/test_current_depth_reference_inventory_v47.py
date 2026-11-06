import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v10 as v10
from build_current_depth_reference_inventory_v47 import EXPECTED,DOI,URL,OWNER,CONTEXT,verify_facts,references,validate_rows,assemble
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':'publisher_abstract_and_opening_model_configuration_only','full_results_reviewed':False,'original_source_bytes_verified':False,'new_provider_field_requests':0,'source_text_excerpts':['between 50 and 100 m','between 100 and 150 m'],'reported_rows':[{'id':'synthetic-'+e[1],'depths_m':copy.deepcopy(e[0]),'phase':e[1],'metric':e[2],'quantity_role':'reported_model_flow_depth_band' if e[1]=='fall' else 'reported_model_core_depth_band'} for e in EXPECTED],'source_analysis_averaging_window':None,'source_exact_section_coordinates':None,'source_citation':'Synthetic citation','model_experiment_context':'Synthetic model only','eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']}}

def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','old_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','old_flag':False} for i in range(920)]
    out={'records':records,'evidence':evidence,'source_contexts':{'prior':{'preserve':True}},'calendar_depth_series':[{'entity_id':OWNER,'months':[{'depth':None}]}]};refresh(out);return out

class ModelDepthAdmissionTests(unittest.TestCase):
    def test_reserve_four_tokens_before_numeric_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[4])
        with patch('build_current_depth_reference_inventory_v47.int',side_effect=AssertionError('Unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_phase_value_owner_metric_and_role_rejected(self):
        for change in [{'depths_m':[50,150]},{'phase':'spring'},{'metric':'core_depth'},{'quantity_role':'reported_model_core_depth_band'}]:
            f=facts();f['reported_rows'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        f=facts();f['entity_id']='current:east-india-coastal'
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_partial_source_cannot_become_fully_reviewed_or_native(self):
        for change in [{'review_scope':'full_results'},{'full_results_reviewed':True},{'original_source_bytes_verified':True},{'new_provider_field_requests':1},{'source_analysis_averaging_window':[1992,2005]}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_band_not_thickness_boundary_or_annual_range(self):
        rows=references(facts(),'a'*64);self.assertEqual([r['range_m'] for r in rows],[[50,100],[100,150]])
        self.assertEqual([r['metric'] for r in rows],['reported_flow_depth_band','core_depth'])
        for change in [{'thickness_m':50},{'lower_boundary_m':100},{'annual_range_m':[50,150]},{'calendar_months':[9,10,11]},{'volume_eligible':True},{'original_source_pixels_inspected':True},{'source_review_scope':'full_results'}]:
            changed=copy.deepcopy(rows);changed[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_all920_prior_refs_context_calendar_and_owner_fields_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-2],old['evidence']);self.assertEqual(out['counts']['depth_references'],922);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':920});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_source_context_and_reference_identity_rejected(self):
        for change in ['doi','context','id']:
            old=before()
            if change=='doi':old['evidence'][0]['source_doi']=DOI
            if change=='context':old['source_contexts'][CONTEXT]={}
            if change=='id':old['evidence'][0]['id']='synthetic-fall'
            with self.subTest(change=change),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_band_nulls_and_json_roundtrip(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))))
        self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v10_dispatch_and_exact_predecessor_gate(self):
        with patch.object(v10,'previous',return_value={'prior':True}) as old:self.assertEqual(v10.load_inventory({'schema':'osw.current-depth-reference-inventory.v46'},lambda p:b''),{'prior':True});old.assert_called_once()
        with patch.object(v10,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v10.load_inventory({'schema':'osw.current-depth-reference-inventory.v47','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
