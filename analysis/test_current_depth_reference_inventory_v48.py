import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v11 as v11
from build_current_depth_reference_inventory_v48 import EXPECTED,SCOPE,PROCESSING,DOI,URL,OWNER,CONTEXT,verify_facts,references,validate_rows,assemble
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    scopes=['southeastern_eicc_northern_exception_excluded']*2+['authors_multi_site_shelf_slope_summary_not_station_level_boundary','regional_undated_deep_bursts_not_full_winter_state']
    return {'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0,'source_text_excerpts':['<40 m','beyond 100 m','\u223c100 m or more'],'reported_rows':[{'id':'synthetic-'+str(i),'depth_m':e[0],'phase':e[1],'metric':e[2],'bound_side':e[3],'exclusive':e[4],'approximate':e[5],'excerpt_index':[0,0,1,2][i],'site_scope':scopes[i],'locator':'Synthetic fixture'} for i,e in enumerate(EXPECTED)],'shelf_depth_assignment_conflict_unresolved':True,'source_figure_windows_assigned_to_bounds':False,'source_exact_section_coordinates':None,'source_depth_threshold_criterion':None,'source_citation':'Synthetic','source_processing':copy.deepcopy(PROCESSING),'source_cohort_context':'Synthetic composite record','temporal_scope':'Synthetic transient phases','eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']}}

def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','prior_flag':False} for i in range(922)]
    out={'records':records,'evidence':evidence,'source_contexts':{'prior':{'preserve':True}},'calendar_depth_series':[{'entity_id':OWNER,'months':[{'depth':None}]}]};refresh(out);return out

class ObservationalBoundsTests(unittest.TestCase):
    def test_three_tokens_reserved_before_conversion_and_shared_excerpt_not_double_parsed(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v48.int',side_effect=AssertionError('Unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_value_phase_metric_side_and_approximation_rejected(self):
        for change in [{'depth_m':100},{'phase':'all_year'},{'metric':'core_depth'},{'bound_side':'lower'},{'exclusive':False},{'approximate':True}]:
            f=facts();f['reported_rows'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_caption_conflict_northern_exception_and_gap_processing_preserved(self):
        for change in [{'shelf_depth_assignment_conflict_unresolved':False},{'source_figure_windows_assigned_to_bounds':True},{'source_exact_section_coordinates':[80,12]},{'source_depth_threshold_criterion':0.1},{'original_source_pixels_inspected':True}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        f=facts();f['reported_rows'][0]['site_scope']='entire_current'
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        f=facts();f['source_processing']['lowpass_cutoff_hours']['cuddalore']=50
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        rows=references(facts(),'a'*64);rows[0]['source_processing']['authors_gap_filling_applied']=False
        with self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_strict_upper_lower_and_approximate_reach_not_nominal_depth(self):
        rows=references(facts(),'a'*64)
        self.assertEqual([r['upper_bound_m'] for r in rows],[40,40,None,None]);self.assertEqual([r['lower_bound_m'] for r in rows],[None,None,100,100])
        self.assertTrue(rows[2]['lower_bound_exclusive']);self.assertFalse(rows[3]['lower_bound_exclusive']);self.assertTrue(rows[3]['reported_bound_is_approximate'])
        for change in [{'upper_bound_exclusive':False},{'approximate_value_m':40},{'thickness_m':40},{'annual_range_m':[40,100]},{'observed_period':{'start':'2011-10-01'}},{'volume_eligible':True},{'bound_is_hard_measurement_error_limit':True}]:
            changed=copy.deepcopy(rows);changed[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_all922_prior_refs_context_calendar_and_owner_fields_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-4],old['evidence']);self.assertEqual(out['counts']['depth_references'],926);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':924});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_source_context_id_and_unknown_owner_rejected(self):
        for change in ['doi','context','id']:
            old=before()
            if change=='doi':old['evidence'][0]['source_doi']=DOI
            if change=='context':old['source_contexts'][CONTEXT]={}
            if change=='id':old['evidence'][0]['id']='synthetic-0'
            with self.subTest(change=change),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
        f=facts();f['entity_id']='current:indian-equatorial-undercurrent'
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_complete_csv_inequalities_nulls_and_json_roundtrip(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))))
        self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v11_dispatch_and_exact_predecessor(self):
        with patch.object(v11,'previous',return_value={'prior':True}) as old:self.assertEqual(v11.load_inventory({'schema':'osw.current-depth-reference-inventory.v47'},lambda p:b''),{'prior':True});old.assert_called_once()
        with patch.object(v11,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v11.load_inventory({'schema':'osw.current-depth-reference-inventory.v48','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
