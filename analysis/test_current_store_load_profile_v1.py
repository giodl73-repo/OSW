import unittest
from unittest.mock import patch
import profile_current_store_load_v1 as profile

class ProfileTests(unittest.TestCase):
    def test_local_profile_refuses_before_file_reads_or_subprocess(self):
        with patch.object(profile.os,'name','nt'),patch.object(profile.Path,'read_bytes',side_effect=AssertionError('No local payload access')),patch.object(profile.subprocess,'check_output',side_effect=AssertionError('No local compiler/network')):
            with self.assertRaisesRegex(ValueError,'Scoped cloud profiling only'):profile.controls()

    def test_all_existing_store_validation_statements_remain_in_order(self):
        raw=(profile.ROOT/'rust/osw-query/src/lib.rs').read_text()
        instrumented,count=profile.instrument_source('lib.rs',raw)
        self.assertGreaterEqual(count,80)
        original=[line.strip() for line in raw.splitlines() if line.startswith('        ') and '::' in line and line.endswith(')?;')]
        self.assertTrue(original)
        position=0
        for line in original:
            found=instrumented.find(line,position)
            self.assertGreaterEqual(found,position,line)
            position=found+len(line)
        self.assertIn('drop(_osw_profile_parse);',instrumented)
        self.assertIn('drop(_osw_profile_index);',instrumented)
        self.assertIn('drop(_osw_profile_spatial);',instrumented)
        self.assertIn('Session::new("Store::metadata")',instrumented)

    def test_checked_instrumentation_preserves_return_and_early_error(self):
        raw='fn checked(c: &Map, manifest: &Value) -> Result<bool, String> {\n if bad(c) { return Err("bad".into()); }\n Ok(true)\n}\n'
        result,count=profile.instrument_source('example.rs',raw)
        self.assertEqual(count,1)
        self.assertEqual(result.replace('\n    let _osw_profile_checked=crate::load_profile::Span::new("checked:example");',''),raw)

    def test_unrecognized_store_boundaries_refused(self):
        with self.assertRaisesRegex(ValueError,'Store load signature differs'):profile.instrument_source('lib.rs','pub fn changed() {}')

if __name__=='__main__':unittest.main()
