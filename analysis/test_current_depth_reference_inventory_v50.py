import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v13 as v13
from build_current_depth_reference_inventory_v50 import EXPECTED,verify_facts,references,validate_rows,assemble,DOI,URL,OWNER,SCOPE
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'source_text_excerpts':['1800 m','1000 m','1500 m'],'reported_rows':[{'id':'semc-halo2014-'+s,'depth_m':v,'phase':p,'excerpt_index':e,'site_scope':site,'locator':'Synthetic','temporal_scope':'Synthetic model context'} for s,v,p,e,site in EXPECTED],'source_model':{'name':'SWIM_ROMS','horizontal_grid_degrees':0.2,'vertical_sigma_layers':45,'run_years':10,'spinup_years':3,'output_averaging_days':2,'mean_figure_caption_years':7,'exact_mean_model_year_indices_resolved':False},'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0,'source_depth_cutoff_rule':None,'model_underrepresents_EMUC':True,'seasonal_range_from_sections_allowed':False,'source_citation':'Synthetic'}

class ModelDepthTests(unittest.TestCase):
    def test_reservation_before_conversion_reused_excerpt_once(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v50.int',side_effect=AssertionError('unreserved conversion'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_source_values_model_year_and_undercurrent_limits(self):
        for change in [{'depth_m':1500},{'phase':'annual_minimum'},{'site_scope':'whole_route'}]:
            f=facts();f['reported_rows'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        for change in [{'source_depth_cutoff_rule':0.1},{'model_underrepresents_EMUC':False},{'seasonal_range_from_sections_allowed':True},{'original_source_pixels_inspected':True},{'entity_id':'current:indian-south-equatorial-countercurrent'}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        f=facts();f['source_model']['exact_mean_model_year_indices_resolved']=True
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_mean_and_snapshot_extents_never_physical_or_seasonal(self):
        rows=references(facts(),'a'*64);self.assertEqual([r['approximate_value_m'] for r in rows],[1800,1000,1500,1500]);self.assertNotEqual(rows[0]['metric'],rows[2]['metric'])
        for change in [{'thickness_m':1800},{'annual_range_m':[1000,1800]},{'observed_period':{'year':2010}},{'model_year_is_calendar_year':True},{'volume_eligible':True},{'metric':'reported_vertical_extent'},{'same_source_width_reference_id':'ponsoni2016'}]:
            changed=copy.deepcopy(rows);changed[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_all_prior_refs_context_calendars_and_owner_fields_preserved(self):
        records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior':True} for i in range(111)]
        before={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'old','unit':'dbar' if i<2 else 'm'} for i in range(928)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'prior':True}]};refresh(before)
        after=assemble(before,facts(),'a'*64);self.assertEqual(after['evidence'][:-4],before['evidence']);self.assertEqual(after['counts']['depth_references'],932);self.assertEqual(after['calendar_depth_series'],before['calendar_depth_series'])
        for a,b in zip(before['records'],after['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
        before['evidence'][0]['source_doi']=DOI
        with self.assertRaises(ValueError):assemble(before,facts(),'a'*64)
    def test_csv_complete_parity_and_nulls(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_typed_view_exact_predecessor(self):
        with patch.object(v13,'previous',return_value={'old':True}):self.assertEqual(v13.load_inventory({'schema':'old'},lambda p:b''),{'old':True})
        with patch.object(v13,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v13.load_inventory({'schema':'osw.current-depth-reference-inventory.v50','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
