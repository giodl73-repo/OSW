import copy,unittest
from recover_wsc_f3_offline_brackets_v2 import recovery_gate

def failed():
    return {'status':'FAILED_NO_RETRY_CASE_CLOSED','error_type':'FileNotFoundError','error':"[Errno 2] No such file or directory: '/home/runner/work/OSW/OSW/analysis/capture_wsc_f3_bounded_preview_v1.py'",'provider_case_closed':True,'remaining_provider_operations':0,'attempted_provider_operations':2,'native_numeric_values_decoded':0,'case_numeric_upper_bound':147160,'source_responses':[{'http_status':200,'status':'ORIGINAL_RAW_RETAINED_TARGET_CLOSED'}]*2}

class RecoveryCustody(unittest.TestCase):
    def test_exact_predecode_failure_does_not_reopen_acquisition_or_mutate_ledger(self):
        p=failed();before=copy.deepcopy(p);recovery_gate(p);self.assertEqual(p,before);self.assertEqual(p['remaining_provider_operations'],0)
    def test_parsed_native_data_spent_allowance_or_provider_failure_cannot_use_this_repair(self):
        for key,v in [('native_numeric_values_decoded',1),('additional_selection_and_output_numeric_upper_bound_reserved',30000),('error_type','ValueError'),('attempted_provider_operations',3),('remaining_provider_operations',6)]:
            p=failed();p[key]=v
            with self.assertRaises(ValueError):recovery_gate(p)
        p=failed();p['source_responses'][0]={'http_status':403,'status':'FAILED'}
        with self.assertRaises(ValueError):recovery_gate(p)

if __name__=='__main__':unittest.main()
