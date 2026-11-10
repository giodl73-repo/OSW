import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v18 as v18
from build_current_depth_reference_inventory_v55 import PREVIOUS,CONTEXT,REFERENCE_IDS,verify_facts,references,validate_rows,assemble,DOI,URL,OWNER,SCOPE
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell

def facts():
    return {'id':CONTEXT,'source_doi':DOI,'source_url':URL,'entity_id':OWNER,'review_scope':SCOPE,'source_text_excerpt':'surface to about 400 m;50-480 m depth range','main_core_lower_extent_m':400,'onshore_jet_depth_band_m':[50,480],'source_observed_period':['2020-01-12T16:00:00Z','2020-01-12T23:20:00Z'],'velocity_definition':'Meridional SADCP velocities normalized by whole-dataset mean;jet Vnorm>1,core Vnorm>2.','site_scope':'Synthetic','source_limits':'Sampled17.6-460/500m;not current bottom','source_depth_cutoff_rule':'Relative normalization;not an absolute fixed velocity cutoff.','lower_boundary_support_resolved':None,'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},'original_source_bytes_verified':False,'original_source_pixels_inspected':False,'new_provider_field_requests':0,'source_citation':'Synthetic'}

class JetDepthTests(unittest.TestCase):
    def test_predecessor_and_reservation_before_conversion(self):
        self.assertEqual(PREVIOUS,'research/current-depth-reference-inventory-v54.json');charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[3])
        with patch('build_current_depth_reference_inventory_v55.int',side_effect=AssertionError('unreserved'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_no_swapped_features_dates_or_resolved_support(self):
        for change in [{'main_core_lower_extent_m':480},{'onshore_jet_depth_band_m':[0,480]},{'source_observed_period':['1997','1997']},{'lower_boundary_support_resolved':True},{'velocity_definition':'absolute0.1m/s'},{'entity_id':'current:alaska'}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_no_thickness_surface_season_width_or_normalization_promotion(self):
        for index in [0,1]:
            for change in [{'lower_boundary_m':480},{'thickness_m':430},{'annual_range_m':[400,480]},{'uncertainty_m':50},{'observed_period':['2020','2020']},{'volume_eligible':True},{'surface_observation_at_zero_m_established':True},{'lower_boundary_support_resolved':False},{'normalized_velocity_threshold':3},{'same_source_width_reference_id':'historicwidth'}]:
                rows=references(facts(),'a'*64);rows[index].update(change)
                with self.subTest(index=index,change=change),self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_feature_order_and_ownership(self):
        rows=references(facts(),'a'*64)
        with self.assertRaises(ValueError):validate_rows(rows[::-1],facts())
        rows[1]['entity_id']='current:acc'
        with self.assertRaises(ValueError):validate_rows(rows,facts())
    def test_all936_prior_refs_context_calendar_and_owner_fields_preserved(self):
        records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior':True} for i in range(111)]
        old={'records':records,'evidence':[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'prior','unit':'dbar' if i<4 else 'm'} for i in range(936)],'source_contexts':{'prior':{}},'calendar_depth_series':[{'prior':True}]};refresh(old)
        new=assemble(old,facts(),'a'*64);self.assertEqual(new['evidence'][:-2],old['evidence']);self.assertEqual(new['counts']['depth_references'],938);self.assertEqual(new['coordinate_unit_counts'],{'dbar':4,'m':934});self.assertEqual(new['calendar_depth_series'],old['calendar_depth_series'])
        for a,b in zip(old['records'],new['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
        old['evidence'][0]['source_doi']=DOI
        with self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_complete_csv_and_json_parity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode('utf8'))));self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_exact_typed_predecessor(self):
        with patch.object(v18,'previous',return_value={'old':True}):self.assertEqual(v18.load_inventory({'schema':'old'},lambda p:b''),{'old':True})
        with patch.object(v18,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v18.load_inventory({'schema':'osw.current-depth-reference-inventory.v55','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
