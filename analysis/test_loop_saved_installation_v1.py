"""Reject custody errors without reading the real packet or compiled binary."""
import copy
import json
import unittest

import loop_saved_installation_v1 as rules


class InstallationCustody(unittest.TestCase):
    def setUp(self):
        self.original = b'original page'
        self.revised = b'reviewed revised page'
        self.revision = {'original_path': rules.PAGE,
                         'original_sha256': rules.sha(self.original),
                         'candidate_sha256': rules.sha(self.revised),
                         'reviewed_execution_commit': '1' * 40}
        self.manifest = {'sha256': {rules.PAGE: rules.sha(self.original), rules.WASM: '2' * 64,
                                    'research/historical-facts.json': '3' * 64},
                         'abi_version': 1, 'old_delivery_receipt': {'frozen': True}}
        self.inventory = {'rust_source_sha256': {'rust/lib.rs': '4' * 64},
                          'compile_time_data_sha256': {'almanac/index-catalog.json': '5' * 64}}

    def overlay(self, manifest=None, revised=None, inventory=None):
        return rules.presentation_manifest(rules.encode(manifest or self.manifest), self.original,
                                           self.revised if revised is None else revised,
                                           self.revision, inventory or self.inventory)

    def test_only_declared_page_pins_and_receipt_change(self):
        before = copy.deepcopy(self.manifest)
        after = self.overlay()
        self.assertEqual(self.manifest, before)
        changed = {k for k in before['sha256'] if before['sha256'][k] != after['sha256'][k]}
        self.assertEqual(changed, {rules.PAGE})
        self.assertEqual(set(after['sha256']) - set(before['sha256']),
                         {rules.ARCHIVED_PAGE, rules.ARCHIVED_MANIFEST})
        for key in before:
            if key != 'sha256':
                self.assertEqual(after[key], before[key])
        self.assertEqual(after['sha256'][rules.ARCHIVED_MANIFEST], rules.sha(rules.encode(before)))

    def test_modified_page_is_refused(self):
        with self.assertRaises(ValueError):
            self.overlay(revised=b'unreviewed')

    def test_compiled_presentation_path_is_refused(self):
        bad = copy.deepcopy(self.inventory)
        bad['compile_time_data_sha256'][rules.PAGE] = self.revision['original_sha256']
        with self.assertRaises(ValueError):
            self.overlay(inventory=bad)

    def test_changed_saved_page_custody_is_refused(self):
        bad = copy.deepcopy(self.manifest)
        bad['sha256'][rules.PAGE] = '6' * 64
        with self.assertRaises(ValueError):
            self.overlay(manifest=bad)

    def test_history_collision_is_refused(self):
        for path in [rules.ARCHIVED_PAGE, rules.ARCHIVED_MANIFEST]:
            bad = copy.deepcopy(self.manifest)
            bad['sha256'][path] = '7' * 64
            with self.assertRaises(ValueError):
                self.overlay(manifest=bad)

    def test_only_exact_nineteen_generated_paths_allowed(self):
        fixed = ['almanac/query-data.json', rules.WASM, rules.MANIFEST,
                 'almanac/index-catalog.json', 'almanac/index-data.json.gz',
                 'almanac/index-sources.json', 'research/ocean-motion-dashboard.json']
        paths = fixed + [f'almanac/query-parts/{i:06d}-' + f'{i:064x}' + '.bin' for i in range(12)]
        result = {'artifact_paths': paths, 'generated_sha256': {p: 'a' * 64 for p in paths}}
        self.assertEqual(rules.generated_paths(result), set(paths))
        result['artifact_paths'][0] = '../outside'
        with self.assertRaises(ValueError):
            rules.generated_paths(result)


if __name__ == '__main__':
    unittest.main()
