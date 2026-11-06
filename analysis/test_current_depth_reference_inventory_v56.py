import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v19 as v19
from build_current_depth_reference_inventory_v56 import PREVIOUS,CONTEXT,REFERENCE_IDS,verify_facts,references,validate_rows,assemble,DOIS,OWNERS
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    cases=[{'entity_id':OWNERS[0],'source_doi':DOIS[0],'source_url':'https://www7320.nrlssc.navy.mil/pubs/2003/barron4.pdf','source_text_excerpt':'1000-1150 m depth range','range_m':[1000,1150],'approximate_value_m':None,'metric':'reported_flow_depth_band','evidence_kind':'published_observed_float_velocity_band','reported_period_years':[1997,1999],'source_velocity_cutoff_m_s':None,'model_name':None},{'entity_id':OWNERS[1],'source_doi':DOIS[1],'source_url':'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JC014333','source_text_excerpt':'1,000-m depth','range_m':None,'approximate_value_m':1000,'metric':'reported_model_mean_current_vertical_extent','evidence_kind':'published_ecco2_model_mean_velocity_extent','reported_period_years':[1993,2016],'source_velocity_cutoff_m_s':0.1,'model_name':'ECCO2_cube92'}]
    for c in cases:c.update({'source_citation':'Synthetic','source_locator':'Synthetic','definition':'Synthetic source method','qualification':'Synthetic no physical edge','temporal_scope':'Synthetic','site_scope':'Synthetic'})
    return {'id':CONTEXT,'cases':cases,'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0}

class AgulhasEvidenceTests(unittest.TestCase):
    def test_predecessor_and_reservation_before_conversion(self):
        self.assertEqual(PREVIOUS,'research/current-depth-reference-inventory-v55.json');charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v56.int',side_effect=AssertionError('unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_owner_source_period_and_model_cannot_swap(self):
        for index,change in [(0,{'entity_id':OWNERS[1]}),(1,{'source_doi':DOIS[0]}),(0,{'reported_period_years':[1993,2016]}),(1,{'model_name':None}),(0,{'evidence_kind':'published_ecco2_model_mean_velocity_extent'}),(1,{'source_velocity_cutoff_m_s':0.0}),(0,{'range_m':[1000,1500]})]:
            f=facts();f['cases'][index].update(change)
            with self.subTest(index=index,change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_no_extrapolated_edge_volume_thickness_or_season(self):
        for index in [0,1]:
            for change in [{'lower_boundary_m':1500},{'lower_bound_m':1150},{'thickness_m':150},{'annual_range_m':[1000,1150]},{'uncertainty_m':150},{'observed_period':['1997','1999']},{'volume_eligible':True},{'depth_band_endpoints_are_current_edges':True},{'same_source_width_reference_id':'70km'}]:
                rows=references(facts(),'a'*64);rows[index].update(change)
                with self.subTest(index=index,change=change),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_owner_order_and_method_source_binding(self):
        rows=references(facts(),'a'*64)
        with self.assertRaises(ValueError):validate_rows(rows[::-1],facts())
        for field,value in [('entity_id',OWNERS[0]),('model_name',None),('source_definition','Direct observations')]:
            rows=references(facts(),'a'*64);rows[1][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_all938_prior_refs_context_calendar_and_owner_fields_preserved(self):
        records=[{'entity_id':OWNERS[i] if i<2 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior':True} for i in range(111)]
        old={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'prior','unit':'dbar' if i<4 else 'm'} for i in range(938)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'prior':True}]};refresh(old)
        new=assemble(old,facts(),'a'*64);self.assertEqual(new['evidence'][:-2],old['evidence']);self.assertEqual(new['counts']['depth_references'],940);self.assertEqual(new['coordinate_unit_counts'],{'dbar':4,'m':936});self.assertEqual(new['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],new['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
        for doi in DOIS:
            old['evidence'][0]['source_doi']=doi
            with self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_complete_csv_and_json_parity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_exact_typed_predecessor(self):
        with patch.object(v19,'previous',return_value={'old':True}):self.assertEqual(v19.load_inventory({'schema':'old'},lambda p:b''),{'old':True})
        with patch.object(v19,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v19.load_inventory({'schema':'osw.current-depth-reference-inventory.v56','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
