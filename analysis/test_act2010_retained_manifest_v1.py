import copy,unittest,xml.etree.ElementTree as ET
import index_act2010_retained_manifest_v1 as source


def fixture():
    return b'<accession manifest_version="2"><head><id>0140939</id><version>1.1</version><directory>/nodc/archive/arc0085/0140939/1.1/</directory><file_count>2</file_count><byte_count>105</byte_count></head><body><files><file><path>data/0-data/instrument.nc</path><digest algorithm="sha256">'+b'a'*64+b'</digest><type_category>regular</type_category><type>netcdf</type><size>100</size></file><file><path>NODC-Readme.txt</path><digest algorithm="sha256">'+b'b'*64+b'</digest><type_category>regular</type_category><type>text</type><size>5</size></file></files></body></accession>'

class RetainedManifest(unittest.TestCase):
    def test_exact_entries_checksums_and_no_permission_or_data_claim(self):
        r=source.inventory(fixture())
        self.assertEqual(r['indexed_entry_count'],2);self.assertEqual(r['candidate_netCDF_count'],1)
        self.assertEqual(r['entry_count_scope_reconciled'],'all_entries');self.assertEqual(r['byte_count_scope_reconciled'],'all_entries')
        self.assertFalse(r['native_field_acquisition_eligible']);self.assertEqual(r['provider_requests'],0)
        self.assertFalse(r['entries'][0]['native_file_hash_independently_verified'])
        self.assertEqual(r['entries'][0]['provider_asserted_sha256'],'a'*64)
        self.assertEqual(r['entries'][0]['source_manifest_xpath'],'/accession/body/files/file[1]')
        self.assertTrue(r['entries'][1]['documentation_candidate'])

    def test_path_escape_and_duplicates_rejected(self):
        for path in [b'../../outside.nc',b'/absolute.nc',b'data\\outside.nc']:
            with self.assertRaises(ValueError):source.inventory(fixture().replace(b'data/0-data/instrument.nc',path))
        with self.assertRaises(ValueError):source.inventory(fixture().replace(b'NODC-Readme.txt',b'data/0-data/instrument.nc'))

    def test_source_accession_version_and_sha256_required(self):
        for a,b in [(b'<id>0140939</id>',b'<id>999</id>'),(b'<version>1.1</version>',b'<version>2.0</version>'),(b'algorithm="sha256"',b'algorithm="sha1"')]:
            with self.assertRaises(ValueError):source.inventory(fixture().replace(a,b))

    def test_oversize_candidate_is_indexed_but_not_downloaded(self):
        r=source.inventory(fixture().replace(b'<size>100</size>',b'<size>3000000</size>'))
        self.assertFalse(r['entries'][0]['fits_2p4MB_single_response_before_other_case_output'])
        self.assertFalse(r['entries'][0]['native_file_downloaded']);self.assertFalse(r['entries'][0]['field_acquisition_eligible'])
        self.assertEqual(r['byte_count_scope_reconciled'],'unresolved')

    def test_entities_and_body_cap_rejected(self):
        for raw in [b'<!DOCTYPE x>'+fixture(),b'<!ENTITY x>'+fixture(),b'x'*128001]:
            with self.assertRaises(ValueError):source.inventory(raw)

    def test_budget_and_scientific_nonpromotion_flags_remain_exact(self):
        r=source.inventory(fixture())
        self.assertEqual(r['case_remote_operations_used_unchanged'],6);self.assertEqual(r['case_remote_operations_cap_unchanged'],18)
        self.assertEqual(r['metadata_stage_remote_operations_used_unchanged'],6)
        self.assertFalse(r['manifest_metadata_is_scientific_depth_evidence']);self.assertFalse(r['case_native_profile_or_scalar_reserves_reset'])
        self.assertEqual(r['new_native_ocean_values_decoded'],0);self.assertEqual(r['new_current_depth_references'],0)

if __name__=='__main__':unittest.main()
