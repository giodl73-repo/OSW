"""Independent original-PDF readback and preserved scope/older measurement exports."""
import copy,json,re,subprocess,unittest
from unittest.mock import patch
from pypdf import PdfReader
import agulhas_reported_dimensions as a

class AgulhasReportedTests(unittest.TestCase):
    def test_original_pdf_independently_supports_both_quantities(self):
        a.original();reader=PdfReader(a.ROOT/(a.DIRECTORY+'article.pdf'))
        extent=' '.join(reader.pages[3].extract_text().split())
        core=' '.join(reader.pages[4].extract_text().split())
        self.assertRegex(extent,r'1000\s*km long western boundary current')
        self.assertRegex(core,r'core\s*\([^)]*200\s*km wide')
        self.assertIn('5970',extent);self.assertIn('5971',core)

    def test_width_and_extent_scopes_are_not_combined(self):
        doc,_=a.verify_inputs();w=doc['width_record'];length=doc['length_variant']
        self.assertEqual(w['approximate_width_km'],200);self.assertEqual(length['value_km'],1000)
        self.assertFalse(length['rank_eligible']);self.assertFalse(length['new_length_measurement_admitted'])
        for key in ['observed_period','fixed_layer_bounds_m','uncertainty_km','geographic_current_edges','width_range_km','annual_width_range_km']:
            self.assertIsNone(w[key])
        for key in ['whole_current_representative','seasonal_playback_eligible','annual_extrema_eligible','is_climatology','is_annual_mean','independent_width_observation']:
            self.assertFalse(w[key])
        self.assertEqual(w['related_measurement_ids'],['agulhas-act-eulerian-mean-section-width'])

    def test_effective_export_is_append_only_for_widths_and_preserves_ranked_lengths(self):
        doc=a.verify();old=a.prior.working_export();new=a.effective_export(doc)
        self.assertEqual(new['widths'][:-1],old['widths']);self.assertEqual(new['measurements'],old['measurements'])
        self.assertEqual(new['length_assessments'],old['length_assessments'])
        self.assertEqual((new['ranked_length_count'],len(new['widths']),new['scoped_width_owners']),(12,158,83))
        self.assertEqual(len({w['current_id'] for w in new['widths']}),83)
        for name in [a.prior.PATH,a.prior.EXPORT,'research/ocean-current-width-inventory.json']:
            self.assertEqual(subprocess.check_output(['git','show','ee27a9e:'+name],cwd=a.ROOT),(a.ROOT/name).read_bytes())

    def test_licensed_source_and_exact_diagnostic_are_bound(self):
        doc=a.verify();source=doc['source_record'];self.assertEqual(source['id'],a.SOURCE_ID)
        self.assertEqual(source['license'],'CC BY 4.0');self.assertTrue(source['provider_asset_redistributed'])
        self.assertEqual(a.diagnostic(doc)['source_json'].encode(),(a.ROOT/a.FILE).read_bytes())
        self.assertEqual(source['source_file_sha256'],a.PINS['article.pdf'])

    def test_rehashed_or_scope_modified_report_rejected(self):
        read=a.Path.read_bytes;target=a.ROOT/a.FILE
        for key,value in [('approximate_width_km',219),('width_range_km',[200,219]),('observed_period','2021-11'),('seasonal_playback_eligible',True)]:
            doc=a.verify();doc['width_record'][key]=value
            with self.subTest(key=key),patch.object(a.Path,'read_bytes',lambda p:a.encoded(doc) if p==target else read(p)),self.assertRaisesRegex(ValueError,'Stale'):
                a.verify()

if __name__=='__main__':unittest.main()
