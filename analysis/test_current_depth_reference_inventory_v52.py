import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v15 as v15
from build_current_depth_reference_inventory_v52 import EXPECTED,PREVIOUS,verify_facts,references,validate_rows,assemble,DOI,URL,OWNER,SCOPE
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'source_text_excerpts':['between 600 and 2000 dbar','between 1000 and 2500 dbar'],'reported_rows':[{'id':'asc-meijers2016-'+s,'range_dbar':band,'metric':metric,'excerpt_index':i,'locator':'Synthetic','definition':'Synthetic regional band'} for i,(s,band,metric) in enumerate(EXPECTED)],'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'pressure_to_depth_conversion_performed':False,'regional_band_is_single_column_layer':False,'lander_measures_velocity':False,'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0,'source_processing':{'synthetic':True},'source_citation':'Synthetic','temporal_scope':'Synthetic repeat summer occupations'}

class PressureBandTests(unittest.TestCase):
    def test_exact_predecessor_and_reservation_before_conversion(self):
        self.assertEqual(PREVIOUS,'research/current-depth-reference-inventory-v51.json');charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[4])
        with patch('build_current_depth_reference_inventory_v52.int',side_effect=AssertionError('unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_source_coordinate_regional_and_lander_limits(self):
        for change in [{'range_dbar':[600,2500]},{'metric':'physical_layer'},{'excerpt_index':1}]:
            f=facts();f['reported_rows'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        for key in ['pressure_to_depth_conversion_performed','regional_band_is_single_column_layer','lander_measures_velocity','original_source_pixels_inspected']:
            f=facts();f[key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_no_pressure_metre_physical_or_annual_promotion(self):
        rows=references(facts(),'a'*64)
        for change in [{'unit':'m'},{'range_m':[600,2000]},{'thickness_m':1400},{'annual_range_m':[600,2500]},{'volume_eligible':True},{'regional_band_is_single_column_layer':True},{'same_source_width_reference_id':'regional-width'}]:
            changed=copy.deepcopy(rows);changed[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_all932_prior_refs_and_owner_fields_preserved(self):
        records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior':True} for i in range(111)]
        old={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'prior','unit':'dbar' if i<2 else 'm'} for i in range(932)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'prior':True}]};refresh(old)
        new=assemble(old,facts(),'a'*64);self.assertEqual(new['evidence'][:-2],old['evidence']);self.assertEqual(new['counts']['depth_references'],934);self.assertEqual(new['coordinate_unit_counts'],{'dbar':4,'m':930});self.assertEqual(new['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],new['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
        old['evidence'][0]['source_doi']=DOI
        with self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_json_roundtrip(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['range_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_typed_view_dispatch(self):
        with patch.object(v15,'previous',return_value={'old':True}):self.assertEqual(v15.load_inventory({'schema':'old'},lambda p:b''),{'old':True})
        with patch.object(v15,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v15.load_inventory({'schema':'osw.current-depth-reference-inventory.v52','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
