import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v9 as v9
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell
from build_current_depth_reference_inventory_v46 import verify_facts,references,validate_rows,assemble,OWNER,DOI,URL,EXPECTED

def facts():
    ids=['hanish-winter-lower-salinity-interface','perim-winter-lower-salinity-interface','hanish-summer-lower-salinity-interface','perim-summer-lower-salinity-interface','hanish-time-mean-transport-zero-depth']
    return {'id':'xie2019-redsea-published-depths-v1','entity_id':OWNER,'source_doi':DOI,'source_url':URL,'source_citation':'Xieetal2019,'+DOI,'source_locator':'Sections3.2/5','source_text_excerpts':['about \u221250 m','approximately \u2212100 m','approximately \u2212100 m','between \u2212150 and \u2212200 m','approximately 50 m'],'source_text_excerpts_total_words':17,
        'reported_rows':[{'id':'redsea-xie2019-'+ids[i],'metric':'reported_current_associated_halocline_depth_band' if i<4 else 'net_section_transport_zero_depth','source_signed_depths_m':copy.deepcopy(e[0]),'site':e[1],'phase':e[2],'source_survey_month_context':e[3],'role':'hydrographic_interface_comparison' if i<4 else 'zero_of_time_mean_model_transport_profile','locator':'Synthetic fixture'} for i,e in enumerate(EXPECTED)],
        'source_occupation_dates':None,'source_hydrographic_boundary_threshold':None,'mean_definition':'zero_of_time_mean_transport_profile_not_mean_of_instantaneous_interface_depths','vertical_datum':'source-qualified','geographic_scope':'Hanish/Perim regional','temporal_scope':'Different1995/1996cruises;separatemodelmean.',
        'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'original_html_bytes_verified':False,'original_source_pixels_inspected':False,'closed_native_cases_reopened':False,'new_native_or_provider_requests':0,'runtime_changed':False,'full_goal_complete':False}

def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'name':'Synthetic','status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','qualifier':'Preserve'} for i in range(915)]
    out={'records':records,'evidence':evidence,'source_contexts':{'old':{'preserve':True}},'calendar_depth_series':[{'entity_id':'current:leeuwin','months':[{'boundary':None,'support':475}]}]};refresh(out);return out

class RedSeaPhaseTests(unittest.TestCase):
    def test_six_tokens_reserved_before_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[6])
        with patch('build_current_depth_reference_inventory_v46.int',side_effect=AssertionError('Unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_sign_site_phase_role_and_source_values_rejected(self):
        for change in [{'site':'perim_narrows'},{'phase':'summer_three_layer_pattern'},{'source_signed_depths_m':[50]},{'source_survey_month_context':'1996-05'},{'role':'local_velocity_boundary'}]:
            f=facts();f['reported_rows'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        for change in [{'entity_id':'current:jutland'},{'source_doi':'wrong'},{'source_hydrographic_boundary_threshold':36},{'original_html_bytes_verified':True},{'closed_native_cases_reopened':True}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_positive_depths_and_different_averaging_roles(self):
        rows=references(facts(),'a'*64);self.assertEqual([r['approximate_value_m'] for r in rows],[50,100,100,None,50]);self.assertEqual(rows[3]['range_m'],[150,200]);self.assertIsNone(rows[3]['thickness_m']);self.assertEqual(rows[4]['source_quantity_role'],'zero_of_time_mean_model_transport_profile')
        f=facts();f['mean_definition']='mean_of_instantaneous_zeroes'
        with self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_no_thickness_annualrange_boundary_or_playback_promotion(self):
        rows=references(facts(),'a'*64)
        for i,change in [(3,{'thickness_m':50}),(0,{'upper_boundary_m':50}),(1,{'annual_range_m':[100,200]}),(2,{'calendar_months':[7]}),(4,{'source_definition':'mean_of_instantaneous_zeroes'}),(1,{'seasonal_playback_eligible':True}),(0,{'volume_eligible':True})]:
            r=copy.deepcopy(rows);r[i].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(r,facts())
    def test_all915_prior_records_context_calendar_and_units_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-5],old['evidence']);self.assertEqual(out['counts']['depth_references'],920);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':918});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_study_or_id_rejected(self):
        for field,value in [('source_doi',DOI),('id','redsea-xie2019-hanish-winter-lower-salinity-interface')]:
            old=before();old['evidence'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_signed_values_nulls_phase_and_json_fidelity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode())))
        self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v9_old_dispatch_wrong_predecessor(self):
        with patch.object(v9,'previous',return_value={'old':'unchanged'}) as old:self.assertEqual(v9.load_inventory({'schema':'osw.current-depth-reference-inventory.v45'},lambda p:b''),{'old':'unchanged'});old.assert_called_once()
        with patch.object(v9,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v9.load_inventory({'schema':'osw.current-depth-reference-inventory.v46','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')
if __name__=='__main__':unittest.main()
