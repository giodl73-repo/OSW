import copy,csv,io,json,unittest
from unittest.mock import patch
import compiled_depth_catalog_view_v7 as v7
from compiled_depth_catalog_view_v3 import refresh
from load_current_depth_reference_inventory_v1 import reference_csv_bytes,cell
from build_current_depth_reference_inventory_v44 import verify_facts,references,validate_rows,assemble,reference_layer,OWNER,DOI,URL

def facts():
    return {'id':'johns2003-hormuz-published-depths-v1','entity_id':OWNER,'source_doi':DOI,'source_url':URL,'source_citation':'Johns etal2003,'+DOI,'source_locator':'Sections2.1/3.1.1/3.3',
        'source_text_excerpts':['at 110 m depth','at depths of 60–70 m','at a depth of 45 m'],'source_text_excerpts_total_words':16,'reported_site_water_depth_m':110,'reported_velocity_core_depth_band_m':[60,70],'author_transport_interface_depth_m':45,
        'source_occupation_dates':None,'source_velocity_threshold_m_s':None,'vertical_datum':'source_reported_depth_positive_down_datum_not_independently_qualified','core_definition':'Averaged velocity maximum band,not layer thickness.','interface_definition':'Selected transport interface,not a zero-velocity boundary.','geographic_scope':'Southern Hormuz mooring site','temporal_scope':'1996-1998programme,velocity gaps,not annual extrema.',
        'eligibility':{k:False for k in ['whole_current_representative','physical_current_bottom_established','physical_current_thickness_established','volume_eligible','annual_extrema_eligible','seasonal_playback_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']},
        'original_html_bytes_verified':False,'original_source_pixels_inspected':False,'closed_native_cases_reopened':False,'new_native_or_provider_requests':0,'runtime_changed':False,'full_goal_complete':False}


def before():
    records=[{'entity_id':OWNER if i==0 else 'current:synthetic-'+str(i),'name':'Synthetic','status':'scoped_depth_reference' if i<101 else 'not_yet_assessed','prior_flag':False} for i in range(111)]
    evidence=[{'id':'old-'+str(i),'entity_id':records[i%101]['entity_id'],'metric':'reported_pressure' if i<2 else 'core_depth','unit':'dbar' if i<2 else 'm','approximate_value_m':None,'qualifier':'Preserve old source qualifier'} for i in range(913)]
    out={'records':records,'evidence':evidence,'source_contexts':{'old':{'preserve':True}},'calendar_depth_series':[{'entity_id':'current:leeuwin','months':[{'boundary':None,'support':475}]}]};refresh(out);return out

class HormuzVelocityTests(unittest.TestCase):
    def test_four_tokens_reserved_before_any_conversion(self):
        charged=[];verify_facts(facts(),charged.append);self.assertEqual(charged,[4])
        with patch('build_current_depth_reference_inventory_v44.int',side_effect=AssertionError('Unreserved conversion'),create=True):
            with self.assertRaisesRegex(ValueError,'cap'):verify_facts(facts(),lambda n:(_ for _ in ()).throw(ValueError('cap')))
    def test_wrong_owner_source_unit_value_or_threshold_rejected(self):
        for change in [{'entity_id':'current:red-sea-saline-overflow'},{'source_doi':'wrong'},{'source_text_excerpts':['at 110 dbar depth','at depths of 60–70 m','at a depth of 45 m']},{'author_transport_interface_depth_m':40},{'reported_velocity_core_depth_band_m':[40,70]},{'source_velocity_threshold_m_s':0.05}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_manual_custody_native_and_exact_time_flags(self):
        for change in [{'source_occupation_dates':['1997-06-01']},{'original_html_bytes_verified':True},{'original_source_pixels_inspected':True},{'closed_native_cases_reopened':True},{'new_native_or_provider_requests':1}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):verify_facts(f,lambda n:None)
    def test_core_and_transport_interface_not_physical_boundaries(self):
        rows=references(facts(),'a'*64);self.assertEqual(rows[0]['range_m'],[60,70]);self.assertEqual(rows[1]['approximate_value_m'],45)
        for index,change in [(0,{'thickness_m':10}),(0,{'annual_range_m':[60,70]}),(1,{'upper_boundary_m':45}),(1,{'lower_boundary_m':110}),(1,{'approximate_value_m':40}),(0,{'physical_current_bottom_established':True}),(1,{'volume_eligible':True})]:
            changed=copy.deepcopy(rows);changed[index].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):validate_rows(changed,facts())
    def test_reference_interval_arithmetic_roles_and_missing_dimensions(self):
        layer=reference_layer(facts(),'a'*64);self.assertEqual(layer['reference_thickness_m'],65);self.assertEqual(layer['reference_bottom_depth_m'],110);self.assertEqual(layer['reference_top_depth_m'],45)
        self.assertIsNone(layer['physical_current_thickness_m']);self.assertIsNone(layer['volume_km3']);self.assertIsNone(layer['annual_range_m']);self.assertIsNone(layer['width_km']);self.assertFalse(layer['near_bed_layer_directly_resolved']);self.assertFalse(layer['source_eligibility_overridden'])
        for change in [{'reported_site_water_depth_m':100},{'author_transport_interface_depth_m':40},{'eligibility':{'volume_eligible':True}}]:
            f=facts();f.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):reference_layer(f,'a'*64)
    def test_all913_prior_rows_owner_calendar_units_preserved(self):
        old=before();out=assemble(old,facts(),'a'*64);self.assertEqual(out['evidence'][:-2],old['evidence']);self.assertEqual(out['counts']['depth_references'],915);self.assertEqual(out['coordinate_unit_counts'],{'dbar':2,'m':913});self.assertEqual(out['calendar_depth_series'],old['calendar_depth_series']);self.assertEqual(out['source_contexts']['old'],old['source_contexts']['old'])
        for a,b in zip(old['records'],out['records']):self.assertEqual({k:v for k,v in a.items() if k!='depth_reference_ids'},{k:v for k,v in b.items() if k!='depth_reference_ids'})
    def test_duplicate_source_or_reference_rejected(self):
        for field,value in [('source_doi',DOI),('id','pgw-johns2003-hormuz-mean-velocity-core-depth-band')]:
            old=before();old['evidence'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):assemble(old,facts(),'a'*64)
    def test_full_csv_null_and_range_fidelity(self):
        rows=references(facts(),'a'*64);table=list(csv.DictReader(io.StringIO(reference_csv_bytes(rows).decode())))
        self.assertEqual(table,[{k:cell(row.get(k)) for k in table[0]} for row in rows]);self.assertEqual(table[0]['thickness_m'],'');self.assertEqual(table[1]['upper_boundary_m'],'');self.assertEqual(json.loads(json.dumps(rows)),rows)
    def test_v7_prior_dispatch_wrong_predecessor(self):
        with patch.object(v7,'previous',return_value={'old':'unchanged'}) as old:self.assertEqual(v7.load_inventory({'schema':'osw.current-depth-reference-inventory.v43'},lambda p:b''),{'old':'unchanged'});old.assert_called_once()
        with patch.object(v7,'checked_piece',return_value=b'{"schema":"wrong"}'):
            with self.assertRaises(ValueError):v7.load_inventory({'schema':'osw.current-depth-reference-inventory.v44','view_metadata':{'runtime_changed':False},'previous_inventory':{}},lambda p:b'')

if __name__=='__main__':unittest.main()
