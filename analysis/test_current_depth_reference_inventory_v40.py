"""Synthetic semantic checks; no retained science files or native profiles read."""
import copy,unittest
import load_current_depth_reference_inventory_v40 as m

class MonthlyCensorSemantics(unittest.TestCase):
    def setUp(self):
        self.source={'schema':'osw.leeuwin-monthly-depth-descriptors.v1','status':'NINE_LOCAL_CALCULATED_ZERO_DESCRIPTORS_THREE_UNKNOWN','entity_id':'current:leeuwin','site_id':'WATR50','source_product_sha256':m.PRODUCT_SHA,'months':[],'annual_depth_range_m':None,'seasonal_interpolation_performed':False}
        self.before={'records':[{'entity_id':'current:leeuwin','status':'scoped_depth_reference','depth_reference_ids':[],'volume_km3':None}],'evidence':[],'source_contexts':{'old':{'preserve':True}}}
        for month in range(1,13):
            censored=month in m.CENSORED;rid=None if censored else f'synthetic-month-{month}'
            self.source['months'].append({'month':month,'depth_reference_id':rid,'display_depth_m':None if censored else 100+month,'status':'unknown_no_strict_crossing' if censored else 'calculated_local_mean_velocity_crossing','diagnostic_status':'censored_at_deepest_level' if censored else 'adjacent_zero_crossing','sampling_limit_is_boundary':False})
            if not censored:
                self.before['evidence'].append({'id':rid,'entity_id':'current:leeuwin','metric':'derived_mean_velocity_zero_crossing_depth','unit':'m','calendar_months':[month],'approximate_value_m':100+month,'source_product_sha256':m.PRODUCT_SHA,'local_along_mean_bearing_degrees_true':348,'source_accepted_quality_flags':[1,2,3,4],'source_record_period':{'start':'synthetic-start','end':'synthetic-end'},'mooring_lon_lat':[1.,2.],'source_case_id':'synthetic-cohort','vertical_datum':'local_sea_surface_positive_down','geographic_scope':'synthetic local station','temporal_scope':'synthetic pooled months','computed_zero_crossing_depth_m':100+month+.25,'interpolation_bracket_m':[100+month,105+month]})
        self.review={'status':'PASS_METHOD_SENSITIVITY_SEPARATE_FROM_PUBLISHED_BOUNDARIES','exact_paper_reproduction_established':False,'scientific_review':['','','','March,August,November have no strict sign crossing through the product’s475m deepest level.']}
        self.method={'entity_id':'current:leeuwin','site_id':'WATR50','source_sha256':m.PRODUCT_SHA,'local_along_mean_bearing_degrees_true':348,'positive_velocity_direction':'equatorward','accepted_component_flags':[1,2,3,4],'core_search_depth_interval_m':[0,200],'source_flags':{'1':'observed','2':'extrapolated_near_surface','3':'extrapolated_near_bottom','4':'SOM_filled'},'source_url':'synthetic:test','source_citation':'synthetic test only','source_acknowledgement':'synthetic attribution'}
    def refs(self):return m.references(self.source,self.review,self.method,self.before)
    def assembled(self):
        a={'schema':m.SCHEMA,'id':m.ADDENDUM_ID,'evidence':self.refs(),'source_contexts':{m.CONTEXT:m.context(self.method)},'runtime_changed':False,'full_goal_complete':False}
        return m.assemble(self.before,a,self.source,self.review,self.method)
    def test_support_is_inclusive_not_boundary_thickness_or_observation(self):
        rows=self.refs();self.assertEqual([r['calendar_months'][0] for r in rows],[3,8,11])
        for r in rows:
            self.assertEqual(r['lower_bound_m'],475);self.assertFalse(r['lower_bound_exclusive'])
            for k in ['approximate_value_m','lower_boundary_m','thickness_m','annual_range_m','computed_zero_crossing_depth_m','interpolation_bracket_m','source_selected_daily_records']:self.assertIsNone(r[k])
            for k in ['whole_current_representative','volume_eligible','physical_state_join_eligible','reference_route_projection_eligible','independent_observation_count_claimed']:self.assertFalse(r[k])
            self.assertEqual(r['source_case_id'],'synthetic-cohort');self.assertEqual(r['processed_product_flag_definitions']['4'],'SOM_filled')
    def test_series_preserves_computational_and_display_values_and_unknowns(self):
        series=m.calendar_series(self.assembled(),self.source,self.review,self.method)
        self.assertEqual(series['counts'],{'calendar_months':12,'finite_boundary_descriptors':9,'censored_support_months':3,'unknown_boundary_months':3})
        for row in series['months']:
            if row['month'] in m.CENSORED:
                self.assertIsNone(row['display_boundary_depth_m']);self.assertIsNone(row['computed_zero_crossing_depth_m']);self.assertIsNone(row['boundary_reference_id']);self.assertEqual(row['support_lower_bound_m'],475)
            else:
                self.assertEqual(row['computed_zero_crossing_depth_m'],100+row['month']+.25);self.assertEqual(row['display_boundary_depth_m'],100+row['month']);self.assertIsNone(row['support_lower_bound_m'])
            self.assertFalse(row['sampling_limit_is_boundary']);self.assertIsNone(row['physical_uncertainty_m'])
        self.assertIsNone(series['annual_depth_range_m']);self.assertIsNone(series['volume_m3']);self.assertFalse(series['seasonal_interpolation_performed'])
    def test_boundary_gap_promotion_or_unreviewed_support_rejected(self):
        for key,value in [('display_depth_m',475),('depth_reference_id','invented'),('diagnostic_status','adjacent_zero_crossing'),('sampling_limit_is_boundary',True)]:
            source=copy.deepcopy(self.source);source['months'][2][key]=value
            with self.assertRaises(ValueError):m.references(source,self.review,self.method,self.before)
        review=copy.deepcopy(self.review);review['scientific_review'][3]=review['scientific_review'][3].replace('475m','500m')
        with self.assertRaises(ValueError):m.references(self.source,review,self.method,self.before)
    def test_source_frame_flags_owner_and_existing_boundary_must_reconcile(self):
        for key,value in [('local_along_mean_bearing_degrees_true',332),('accepted_component_flags',[1]),('entity_id','current:other'),('source_sha256','0'*64)]:
            method=copy.deepcopy(self.method);method[key]=value
            with self.assertRaises(ValueError):m.references(self.source,self.review,method,self.before)
        for key,value in [('metric','physical_bottom'),('approximate_value_m',475),('source_case_id','different-cohort')]:
            before=copy.deepcopy(self.before);before['evidence'][1][key]=value
            with self.assertRaises(ValueError):m.references(self.source,self.review,self.method,before)
    def test_append_preserves_prior_references_contexts_and_input_objects(self):
        original=copy.deepcopy((self.before,self.source,self.review,self.method));out=self.assembled()
        self.assertEqual(out['evidence'][:-3],self.before['evidence']);self.assertEqual(out['source_contexts']['old'],self.before['source_contexts']['old']);self.assertEqual((self.before,self.source,self.review,self.method),original)
        self.assertEqual(out['records'][0]['volume_km3'],None);self.assertEqual(out['records'][0]['status'],'scoped_depth_reference')
        self.assertEqual(m.context(self.method)['new_independent_observing_cases'],0)

if __name__=='__main__':unittest.main()
