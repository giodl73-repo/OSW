import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v6 as v6
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell
from build_current_depth_reference_inventory_v43 import verify_facts,references,validate_rows,assemble,OWNER,DOI,URL

def facts():
    return {'id':'bidokhti2009-pgw-published-depths-v1','entity_id':OWNER,'source_doi':DOI,'source_url':URL,'source_citation':'Bidokhti and Ezam2009,'+DOI,'source_locator':'Abstract and Section4',
        'source_text_excerpts':['about 200 m','between 200 and 500 m, especially for summer.'],'source_text_excerpts_total_words':11,'reported_hydrographic_thickness_m':200,'reported_hydrographic_depth_band_m':[200,500],
        'source_survey_year':1992,'source_occupation_dates':None,'source_hydrographic_boundary_threshold':None,
        'vertical_datum':'source_reported_depth_positive_down_datum_not_independently_qualified','thickness_definition':'Hydrographic plume,not a measured velocity-defined thickness or bottom.','depth_band_definition':'Not paired upper/lower boundaries from one profile.','geographic_scope':'Gulf of Oman','temporal_scope':'ROPME1992winter/earlysummer,exact occupations unresolved.',
        'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},
        'original_pdf_byte_custody_performed':False,'original_pdf_pixels_inspected':False,'closed_native_cases_reopened':False,'new_native_or_provider_requests':0,'runtime_changed':False,'full_goal_complete':False}


def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'name':'Synthetic','status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','approximate_value_m':None,'qualifier':'Preserve old source qualifier'} for i in range(911)]
    out={'records':records,'evidence':evidence,'source_contexts':{'old':{'preserve':True}},'calendar_depth_series':[{'entity_id':'current:leeuwin','months':[{'boundary':None,'support':475}]}]};refresh(out);return out

class PGWHydrographicTests(unittest.TestCase):
    def test_three_source_tokens_reserved_before_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v43.int',side_effect=AssertionError('Unreserved conversion'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_wrong_source_owner_units_numbers_or_threshold_rejected(self):
        for change in [{'entity_id':'current:red-sea-saline-overflow'},{'source_doi':'wrong'},{'source_text_excerpts':['about 200 dbar','between 200 and 500 m, especially for summer.']},{'reported_hydrographic_thickness_m':300},{'reported_hydrographic_depth_band_m':[150,400]},{'source_hydrographic_boundary_threshold':36}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_manual_custody_survey_context_and_native_case_flags(self):
        for change in [{'source_survey_year':2009},{'source_occupation_dates':['1992-06-01']},{'original_pdf_byte_custody_performed':True},{'original_pdf_pixels_inspected':True},{'closed_native_cases_reopened':True},{'new_native_or_provider_requests':1}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_thickness_is_not_depth_band_span_or_velocity_bottom(self):
        rows=references(facts(),'a'*64);self.assertEqual(rows[0]['thickness_m'],200);self.assertIsNone(rows[0]['lower_boundary_m']);self.assertEqual(rows[1]['range_m'],[200,500]);self.assertIsNone(rows[1]['thickness_m'])
        for index,change in [(0,{'thickness_m':300}),(0,{'lower_boundary_m':200}),(0,{'upper_boundary_m':150}),(1,{'thickness_m':300}),(1,{'annual_range_m':[200,500]}),(1,{'calendar_months':[6]}),(0,{'volume_eligible':True}),(0,{'physical_current_thickness_established':True})]:
            changed=copy.deepcopy(rows);changed[index].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_all911_prior_rows_owner_fields_calendar_units_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-2],old['evidence']);self.assertEqual(out['counts']['depth_references'],913);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':911});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series']);self.assertEqual(out['source_contexts']['old'],old['source_contexts']['old'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_source_or_reference_rejected(self):
        for field,value in [('source_doi',DOI),('id','pgw-bidokhti2009-reported-hydrographic-plume-thickness')]:
            old=before();old['evidence'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_nulls_and_thickness_band_fidelity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode())))
        keys=set().union(*(r.keys() for r in rows));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'200');self.assertEqual(table[1]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v6_old_dispatch_wrong_predecessor(self):
        with patch.object(v6,'previous',return_value={'old':'unchanged'}) as old:self.assertEqual(v6.load_inventory({'schema':'osw.current-depth-reference-inventory.v42'},lambda p:b''),{'old':'unchanged'});old.assert_called_once()
        with patch.object(v6,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v6.load_inventory({'schema':'osw.current-depth-reference-inventory.v43','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
