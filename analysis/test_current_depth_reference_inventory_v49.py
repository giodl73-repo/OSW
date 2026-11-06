import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v12 as v12
from build_current_depth_reference_inventory_v49 import verify_facts,references,validate_rows,assemble,DOI,OWNER,SCOPE,URL
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'source_text_excerpts':['confined to upper 100 m','50\u2013100 m depth'],'reported_rows':[{'id':'winter','phase':'winter_mean_upper_extent','metric':'reported_mean_flow_upper_layer_extent','upper_bound_m':100,'range_m':None,'locator':'Synthetic','definition':'Synthetic mean extent','temporal_scope':'Synthetic winter','site_scope':'Synthetic regional'},{'id':'summer','phase':'summer_meridional_maximum','metric':'reported_meridional_velocity_core_depth_band','upper_bound_m':None,'range_m':[50,100],'locator':'Synthetic','definition':'Synthetic component maximum','temporal_scope':'Synthetic summer','site_scope':'Synthetic local'}],'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'source_processing':{'synthetic':True},'source_cohort_context':'Synthetic shared cohort','source_citation':'Synthetic','original_source_bytes_verified':False,'original_source_pixels_inspected':False,'eddy_contamination_resolved':False,'new_provider_field_requests':0}

class MonsoonTests(unittest.TestCase):
    def test_reserve_before_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v49.int',side_effect=AssertionError('conversion before reservation'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_mean_component_and_mixed_identity_cannot_be_promoted(self):
        for change in [{'metric':'physical_bottom'},{'range_m':[100,200]},{'phase':'annual'}]:
            f=facts();f['reported_rows'][1].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        for change in [{'entity_id':'current:east-india-coastal'},{'eddy_contamination_resolved':True},{'original_source_pixels_inspected':True}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
        for change in [{'thickness_m':100},{'annual_range_m':[50,100]},{'volume_eligible':True},{'same_source_width_reference_id':'2016-width'},{'metric':'reported_vertical_extent'}]:
            rows=references(facts(),'a'*64);rows[0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_complete_predecessor_preserved_and_duplicate_rejected(self):
        records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed'} for i in range(111)]
        old={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'prior','unit':'dbar' if i<2 else 'm'} for i in range(926)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'preserve':True}]};refresh(old)
        new=assemble(old,facts(),'a'*64);self.assertEqual(new['evidence'][:-2],old['evidence']);self.assertEqual(new['counts']['depth_references'],928);self.assertEqual(new['calendar_depth_series'],old['calendar_depth_series'])
        old['evidence'][0]['source_doi']=DOI
        with self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_and_json_roundtrip(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))))
        self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_exact_dispatch_predecessor(self):
        with patch.object(v12,'previous',return_value={'prior':True}):self.assertEqual(v12.load_inventory({'schema':'old'},lambda p:b''),{'prior':True})
        with patch.object(v12,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v12.load_inventory({'schema':'osw.current-depth-reference-inventory.v49','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
