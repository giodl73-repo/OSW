"""Synthetic source-link/header qualification; no real data files read."""
import unittest
import capture_pgw_jgofs_bottles_v1 as m

def page(extra=''):
    return ('<a href="https://creativecommons.org/licenses/by/4.0/">CC-BY-4.0</a><a href="https://datadocs.bco-dmo.org/synthetic/bottle_TT043.csv">winter</a><a href="https://datadocs.bco-dmo.org/synthetic/bottle_TT049.csv">summer</a>'+extra).encode()

class SourcePreflight(unittest.TestCase):
    def test_exact_declared_files_and_no_unit_promotion(self):
        r=m.metadata(page());self.assertEqual(set(r['selected_file_urls']),{'TT043','TT049'});self.assertFalse(r['temperature_scale_qualified']);self.assertFalse(r['pressure_unit_qualified']);self.assertFalse(r['salinity_scale_qualified'])
    def test_identical_duplicate_links_are_not_duplicate_requests(self):
        r=m.metadata(page('<a href="https://datadocs.bco-dmo.org/synthetic/bottle_TT043.csv">again</a>'))
        self.assertEqual(len(r['selected_file_urls']),2)
    def test_ambiguous_links_fail_without_favorable_target_selection(self):
        with self.assertRaises(ValueError):m.metadata(page('<a href="https://datadocs.bco-dmo.org/other/bottle_TT043.csv">other</a>'))
    def test_plain_http_foreign_host_or_missing_license_rejected(self):
        for raw in [page().replace(b'https://datadocs',b'http://datadocs'),page().replace(b'datadocs.bco-dmo.org',b'other.example'),page().replace(b'CC-BY-4.0',b'none').replace(b'creativecommons.org/licenses/by/4.0',b'none.example/none')]:
            with self.assertRaises(ValueError):m.metadata(raw)
    def test_only_header_strings_read_not_native_numeric_rows(self):
        r=m.header(b'# synthetic comment\nlatitude,longitude,pressure,temp,salinity\n22.5,58,200,20,38\n')
        self.assertEqual(r['source_header_line_1based'],2);self.assertEqual(r['columns'],['latitude','longitude','pressure','temp','salinity']);self.assertEqual(r['native_numeric_values_decoded'],0)
    def test_missing_header_is_unknown_not_fabricated_schema(self):
        r=m.header(b'22.5,58,200,20,38\n');self.assertEqual(r['status'],'UNQUALIFIED_HEADER_NO_NATIVE_PARSE');self.assertEqual(r['columns'],[])

if __name__=='__main__':unittest.main()
