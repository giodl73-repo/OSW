import copy,unittest
from build_current_depth_readiness_v1 import join,months_from_cases

def priority(owner,kind):
    return {'entity_id':owner,'identity_level':'family' if owner.endswith('family') else 'current',
        'priority_kind':kind,'collection_priority_rank':1,'cases':[],
        'supported_regional_case_count':0,'unresolved_regional_case_count':0,'supported_mean_cross_section_count':0,
        'regional_supported_adjacent_segment_occurrences':0,'regional_gap_segment_occurrences':0,
        'next_collection_action':'scoped collection required','source_depth_reference_count':1}

def fixture():
    view={'records':[{'entity_id':'current:family','name':'Family'},{'entity_id':'current:leaf','name':'Leaf'}],
        'evidence':[{'id':'ref','entity_id':'current:leaf','metric':'core_depth','unit':'m','source_cast_profile_id':'one-cast'}]}
    old={'records':[priority('current:family','declared_member_discovery_not_parent_scalar'),priority('current:leaf','no_own_supported_regional_case')]}
    return view,old

class ReadinessSemantics(unittest.TestCase):
    def test_member_parent_does_not_become_a_missing_individual_measurement(self):
        view,old=fixture();report=join(view,old,[])
        self.assertEqual(report['direct_current_regional_priority_gaps'],['current:leaf'])
        self.assertFalse(report['records'][0]['parent_requires_single_depth'])
        self.assertEqual(report['records'][0]['canonical_reference_count'],0)
        self.assertEqual(report['records'][1]['canonical_reference_count'],1)

    def test_snapshot_labels_are_not_a_seasonal_range(self):
        cases=[{'case_scope':{'snapshot_time_utc':'2022-03-15T00:00:00Z'}},{'case_scope':{'snapshot_time_utc':None}},
            {'case_scope':{'snapshot_time_utc':'2022-09-15T00:00:00Z'}}]
        self.assertEqual(months_from_cases(cases),(['2022-03-15','2022-09-15'],[3,9],[]))
        view,old=fixture();old['records'][1]['cases']=cases;r=join(view,old,[])['records'][1]
        self.assertFalse(r['snapshot_month_labels_establish_seasonal_climatology'])
        self.assertIsNone(r['physical_annual_depth_range_m'])

    def test_reviewed_phase_product_is_not_independent_observation_or_volume(self):
        view,old=fixture();product={'id':'cycle','entity_id':'current:leaf','kind':'fitted_phase_cycle'}
        before=copy.deepcopy((view,old,product));report=join(view,old,[product]);row=report['records'][1]
        self.assertEqual(row['reviewed_temporal_products'],[product])
        self.assertFalse(row['regional_cases_are_independent_observations'])
        self.assertIsNone(row['volume_km3']);self.assertEqual((view,old,product),before)

    def test_absent_from_explicit_registry_does_not_assert_absent_project_data(self):
        view,old=fixture();r=join(view,old,[])['records'][1]
        self.assertIn('other_project_data_not_excluded',r['temporal_index_status'])

    def test_nominal_mean_period_is_not_given_an_invented_calendar_month(self):
        self.assertEqual(months_from_cases([{'case_scope':{'snapshot_time_utc':'provider-mean-period'}}]),([],[],['provider-mean-period']))

    def test_duplicate_product_or_identity_mismatch_rejected(self):
        view,old=fixture();p={'id':'cycle','entity_id':'current:leaf'}
        with self.assertRaises(ValueError):join(view,old,[p,p])
        with self.assertRaises(ValueError):join(view,{'records':old['records'][:1]},[])

if __name__=='__main__':unittest.main()
