import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v4 as v4
from compiled_depth_catalog_view_v3 import refresh
from build_current_depth_reference_inventory_v41 import verify_facts,references,validate_rows,assemble,OWNER,DOI,URL
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'id':'font-2024-pgw-published-depths-v1','entity_id':OWNER,'source_doi':DOI,'source_url':URL,'source_citation':'Font et al.2024,'+DOI,'source_locator':'Section4.1,printed5of16',
        'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','volume_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},
        'original_pdf_byte_custody_performed':False,'original_pdf_pixels_inspected':False,'closed_native_cases_reopened':False,'new_native_or_provider_requests':0,
        'source_text_excerpts':['corresponding to depths from 150 to 400 m','its core is located at a depth of 200 m'],'source_text_excerpts_total_words':18,
        'reported_hydrographic_depth_band_m':[150,400],'reported_core_depth_m':200,'source_potential_density_anomaly_interval_kg_m3':[25.5,27],
        'vertical_datum':'source_reported_depth_positive_down_datum_not_independently_qualified','core_definition':'Property core,not a maximum-speed core depth.',
        'depth_band_definition':'Not paired upper/lower boundaries or full thickness.','geographic_scope':'Source two Omani transects,not a core station.',
        'temporal_scope':'Source study2015-2016 and2021-2022,not annual mean.'}

def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'name':'Synthetic','status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','old_other_field':{'keep':True}} for i in range(111)]
    evidence=[{'id':'prior-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'core_depth' if i>=2 else 'reported_pressure','unit':'m' if i>=2 else 'dbar','approximate_value_m':None,'qualifier':'Synthetic old qualifier retained'} for i in range(908)]
    out={'records':records,'evidence':evidence,'source_contexts':{'prior':{'caveat':'preserve'}},'calendar_depth_series':[{'entity_id':'current:leeuwin','months':[{'boundary':None,'support':475}]}]};refresh(out);return out

class FontPGWTests(unittest.TestCase):
    def test_three_primary_excerpt_tokens_reserved_before_conversion(self):
        reserved=[];verify_facts(facts(),reserved.append);self.assertEqual(reserved,[3])
        with patch('build_current_depth_reference_inventory_v41.int',side_effect=AssertionError('No conversion before reserve'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):
                verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_changed_source_numbers_or_metre_label_rejected(self):
        for change in [{'reported_core_depth_m':220},{'reported_hydrographic_depth_band_m':[150,350]},{'source_text_excerpts':['corresponding to depths from 150 to 400 dbar','its core is located at a depth of 200 m']},{'source_text_excerpts':['corresponding to depths from 150 to 400 m','its core is located at a depth of 201 m']}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_wrong_owner_source_population_or_custody_rejected(self):
        for change in [{'entity_id':'current:red-sea-saline-overflow'},{'source_doi':'wrong'},{'source_potential_density_anomaly_interval_kg_m3':[26.2,27]},{'original_pdf_byte_custody_performed':True},{'original_pdf_pixels_inspected':True},{'new_native_or_provider_requests':1}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_property_core_and_regional_band_keep_distinct_nulls(self):
        rows=references(facts(),'a'*64);a,b=rows
        self.assertEqual(a['approximate_value_m'],200);self.assertIsNone(a['range_m']);self.assertEqual(b['range_m'],[150,400]);self.assertIsNone(b['approximate_value_m'])
        self.assertTrue(all(r['thickness_m'] is None and r['annual_range_m'] is None and r['upper_boundary_m'] is None and r['lower_boundary_m'] is None for r in rows));self.assertFalse(a['source_original_pdf_byte_custody_performed'])
    def test_row_physical_range_pressure_and_time_promotions_rejected(self):
        for change in [{'thickness_m':250},{'annual_range_m':[150,400]},{'unit':'dbar'},{'source_original_pdf_pixels_inspected':True},{'volume_eligible':True},{'calendar_months':[1]},{'entity_id':'current:norwegian'}]:
            rows=references(facts(),'a'*64);rows[1].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_all908_prior_rows_contexts_owner_fields_calendar_and_units_preserved(self):
        old=before();f=facts();out=assemble(old,f,'a'*64)
        self.assertEqual(out['evidence'][:-2],old['evidence']);self.assertEqual(out['counts']['depth_references'],910);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':908});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series']);self.assertEqual(out['source_contexts']['prior'],old['source_contexts']['prior'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_same_study_and_duplicate_reference_cannot_be_added_twice(self):
        for mutation in ['doi','id']:
            old=before()
            if mutation=='doi':old['evidence'][0]['source_doi']=DOI
            else:old['evidence'][0]['id']='pgw-font-2024-glider-property-core-depth'
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_complete_csv_null_array_qualifier_and_json_roundtrip(self):
        rows=references(facts(),'a'*64);raw=reference_csv_bytes(rows);table=list(csv.DictReader(io.StringIO(raw.decode())))
        self.assertEqual(table,[{k:cell(r.get(k)) for k in table[0]} for r in rows]);self.assertEqual(table[1]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v4_dispatch_delegates_prior_views_and_rejects_wrong_predecessor(self):
        with patch.object(v4,'previous',return_value={'same':'old'}) as prior:
            self.assertEqual(v4.load_inventory({'schema':'osw.current-depth-reference-inventory.v40'},lambda p:b''),{'same':'old'});prior.assert_called_once()
        bad={'schema':'osw.current-depth-reference-inventory.v41','view_metadata':{'runtime_changed':False}}
        with patch.object(v4,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v4.load_inventory(dict(bad,previous_inventory={}),lambda p:b'')

if __name__=='__main__':unittest.main()
