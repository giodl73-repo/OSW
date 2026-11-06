import copy
import unittest
from unittest.mock import patch
import eac_mean_core_dashboard_context_v1 as m


class Context(unittest.TestCase):
    def test_exact_saved_engine_preserved_except_three_presentation_assets(self):
        old=m.read(m.OLD);new=m.updated_manifest(old,'browser-source')
        m.verify_manifest_delta(old,new,'browser-source')
        self.assertEqual(old['sha256']['almanac/query-engine.wasm'],new['sha256']['almanac/query-engine.wasm'])
        self.assertEqual(old['sha256']['almanac/query-data.json'],new['sha256']['almanac/query-data.json'])
        self.assertEqual(old['eac_mean_core_engine_v1'],new['eac_mean_core_engine_v1'])
        self.assertNotIn(m.KEY,old)

    def test_unrelated_binary_record_pin_namespace_or_marker_change_is_refused(self):
        old=m.read(m.OLD);new=m.updated_manifest(old,'browser-source')
        for kind in ['binary','source','namespace','marker']:
            bad=copy.deepcopy(new)
            if kind=='binary':bad['sha256']['almanac/query-engine.wasm']='changed'
            elif kind=='source':bad['sha256']['research/eac-mean-core-query-contract-v1.json']='changed'
            elif kind=='namespace':bad['eac_mean_core_engine_v1']['new_mean_core_section_records']=6
            else:bad[m.KEY]['native_or_wasm_rebuild']=True
            with self.assertRaises(ValueError):m.verify_manifest_delta(old,bad,'browser-source')

    def test_changed_scientific_dependency_or_archived_dashboard_is_refused(self):
        old=m.read(m.OLD);original=m.sha
        for path in ['research/eac-mean-core-query-contract-v1.json',
            'research/eac-mean-core-dashboard-context-history-v1/almanac/dashboard.js.source']:
            with patch.object(m,'sha',side_effect=lambda p:'changed' if p==path else original(p)):
                with self.assertRaises(ValueError):m.verify_sources(old)


if __name__=='__main__':unittest.main()
