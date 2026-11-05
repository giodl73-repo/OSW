import unittest
from audit_a20_depth_resource_accounting_v1 import numbers,reconcile


class AccountingChecks(unittest.TestCase):
    def test_extra_direct_parse_and_audit_both_charged(self):
        c={'typed_source_packet_numbers_per_pass':496,'case_metadata_touch_bound':5015,
           'case_scalar_bound_including_prior_phases_one_actual_test_and_producer':13123}
        r=reconcile(c,1000)
        self.assertEqual(r['corrected_case_metadata_touch_bound_including_audit'],6511)
        self.assertEqual(r['corrected_case_scalar_bound_including_audit'],14619)
        self.assertEqual(r['new_native_ocean_values_decoded'],0)
        with self.assertRaises(ValueError):reconcile(c,2501)

    def test_counter_excludes_boolean_flags_and_counts_cached_numeric_values(self):
        self.assertEqual(numbers({'flags':[True,False,None],'values':[1,2.0,{'z':3}]}),3)


if __name__=='__main__':unittest.main()
