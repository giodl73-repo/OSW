import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v5 as v5
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell
from build_current_depth_reference_inventory_v42 import verify_facts,reference,validate,assemble,OWNER,DOI,URL

def facts():
    return {'id':'ncc-munk-1995-halocline-v1','entity_id':OWNER,'source_doi':DOI,'source_url':URL,'source_citation':'Munk et al.1995,'+DOI,'source_locator':'Discussion,printed28',
        'source_excerpt':'halocline of the NCC (at about 10 to 15 m depth)','source_excerpt_words':11,'reported_halocline_depth_band_m':[10,15],
        'source_survey_window':['1992-05-10','1992-05-21'],'source_halocline_salinity_or_density_threshold':None,
        'vertical_datum':'source_reported_depth_positive_down_datum_not_independently_qualified','definition':'Hydrographic interface,not a measured velocity-zero boundary.','geographic_scope':'Off Norway,not Jutland.','temporal_scope':'May1992context,not exact occupation.',
        'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},
        'original_pdf_bytes_verified':False,'original_pdf_pixels_inspected':False,'native_source_case_reopened':False,'runtime_changed':False,'full_goal_complete':False}

def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'name':'Synthetic','status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','approximate_value_m':None,'qualifier':'Preserve old source qualifier'} for i in range(910)]
    out={'records':records,'evidence':evidence,'source_contexts':{'old':{'preserve':True}},'calendar_depth_series':[{'entity_id':'current:leeuwin','months':[{'boundary':None,'support':475}]}]};refresh(out);return out

class NCCHaloclineTests(unittest.TestCase):
    def test_two_numeric_tokens_reserved_before_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[2])
        with patch('build_current_depth_reference_inventory_v42.int',side_effect=AssertionError('No unreserved conversion'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_wrong_source_owner_units_numbers_or_threshold_rejected(self):
        for change in [{'entity_id':'current:jutland'},{'entity_id':'current:norwegian'},{'source_doi':'wrong'},{'source_excerpt':'halocline of the NCC (at about 10 to 15 dbar depth)'},{'reported_halocline_depth_band_m':[10,50]},{'source_halocline_salinity_or_density_threshold':34}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_survey_window_and_manual_custody_not_promoted(self):
        for change in [{'source_survey_window':['1992-05-10','1992-05-22']},{'original_pdf_bytes_verified':True},{'original_pdf_pixels_inspected':True},{'native_source_case_reopened':True}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_interface_is_not_current_thickness_or_annual_range(self):
        row=reference(facts(),'a'*64);self.assertEqual(row['range_m'],[10,15]);self.assertIsNone(row['thickness_m']);self.assertIsNone(row['upper_boundary_m']);self.assertIsNone(row['lower_boundary_m']);self.assertIsNone(row['observed_period'])
        for change in [{'thickness_m':5},{'lower_boundary_m':15},{'annual_range_m':[10,15]},{'calendar_months':[5]},{'volume_eligible':True},{'source_interface_criterion':34},{'entity_id':'current:jutland'}]:
            r=copy.deepcopy(row);r.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate(r,facts())
    def test_all910_prior_rows_owner_fields_calendars_units_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-1],old['evidence']);self.assertEqual(out['counts']['depth_references'],911);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':909});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series']);self.assertEqual(out['source_contexts']['old'],old['source_contexts']['old'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_source_or_reference_rejected(self):
        for field,value in [('source_doi',DOI),('id','ncc-munk-1995-may1992-reported-halocline-depth-band')]:
            old=before();old['evidence'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_and_json_null_source_window_parity(self):
        row=reference(facts(),'a'*64);raw=reference_csv_bytes([row]);table=list(csv.DictReader(io.StringIO(raw.decode())))
        self.assertEqual(table,[{k:cell(v) for k,v in row.items()}]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(row)),row)
    def test_v5_prior_dispatch_and_wrong_predecessor_rejected(self):
        with patch.object(v5,'previous',return_value={'old':'unchanged'}) as old:self.assertEqual(v5.load_inventory({'schema':'osw.current-depth-reference-inventory.v41'},lambda p:b''),{'old':'unchanged'});old.assert_called_once()
        with patch.object(v5,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v5.load_inventory({'schema':'osw.current-depth-reference-inventory.v42','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
