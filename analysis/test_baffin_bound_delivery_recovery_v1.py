"""Small recovery guards; no packet, native build, browser or original source."""
import copy
import unittest

import recover_baffin_bound_cloud_delivery_v1 as recovery


def evidence():
    run = {'id': recovery.SOURCE_RUN, 'head_sha': recovery.SOURCE_COMMIT,
           'status': 'completed', 'conclusion': 'failure'}
    jobs = {'total_count': 3, 'jobs': [
        {'name': 'select-delivery-phase', 'status': 'completed', 'conclusion': 'success', 'steps': []},
        {'name': 'baffin-candidate-and-views', 'status': 'completed', 'conclusion': 'success',
         'steps': [{'name': f'Source matrix {i:02d}/14: synthetic case', 'conclusion': 'success'} for i in range(1, 15)]},
        {'name': 'publish-baffin-working-data', 'status': 'completed', 'conclusion': 'failure',
         'steps': [{'name': 'Verify all artifact bindings and publish generated working data', 'conclusion': 'failure'}]}]}
    return run, jobs


class RecoveryTests(unittest.TestCase):
    def test_exact_original_run_requires_full_validation(self):
        recovery.verify_source_run(*evidence())

    def test_wrong_run_or_unfinished_run_rejected(self):
        for key, value in [('id', 1), ('head_sha', '0' * 40), ('status', 'in_progress'), ('conclusion', 'success')]:
            run, jobs = evidence()
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                recovery.verify_source_run(run, jobs)

    def test_failed_or_skipped_source_gate_rejected(self):
        for value in ['failure', 'skipped', None]:
            run, jobs = evidence()
            jobs['jobs'][1]['steps'][5]['conclusion'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                recovery.verify_source_run(run, jobs)

    def test_missing_source_gate_rejected(self):
        run, jobs = evidence()
        jobs['jobs'][1]['steps'].pop()
        with self.assertRaises(ValueError):
            recovery.verify_source_run(run, jobs)

    def test_missing_or_duplicate_jobs_rejected(self):
        for mutation in ['missing', 'duplicate']:
            run, jobs = evidence()
            if mutation == 'missing':
                jobs['jobs'].pop()
            else:
                jobs['jobs'][2] = copy.deepcopy(jobs['jobs'][1])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                recovery.verify_source_run(run, jobs)

    def test_different_publisher_failure_rejected(self):
        run, jobs = evidence()
        jobs['jobs'][2]['steps'][0]['name'] = 'Unrelated failure'
        with self.assertRaises(ValueError):
            recovery.verify_source_run(run, jobs)

    def test_only_exact_operational_delta_allowed(self):
        recovery.verify_control_delta(recovery.CONTROL_FILES.copy())
        for path in ['rust/osw-query/src/lib.rs', 'analysis/baffin_latitude_gate_bound_v1.py', 'almanac/query-data.json']:
            bad = {**recovery.CONTROL_FILES, path: 'M'}
            with self.subTest(path=path), self.assertRaises(ValueError):
                recovery.verify_control_delta(bad)
        bad = recovery.CONTROL_FILES.copy()
        bad.pop(recovery.BUILD)
        with self.assertRaises(ValueError):
            recovery.verify_control_delta(bad)

    def test_only_pinned_rust_format_changes_allowed(self):
        lib = 'rust/osw-query/src/lib.rs'
        recovery.verify_formatted_paths({lib}, {lib: 'a' * 64})
        for paths, pins in [({}, {}), ({lib}, {}),
                            ({lib, '../outside.rs'}, {lib: 'a' * 64, '../outside.rs': 'b' * 64}),
                            ({lib, 'research/source.json'}, {lib: 'a' * 64, 'research/source.json': 'b' * 64})]:
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                recovery.verify_formatted_paths(paths, pins)

    def test_request_cannot_change_scope_or_candidate(self):
        request = {'schema': 'osw.baffin-working-data-recovery-request.v1',
                   'source_run_id': recovery.SOURCE_RUN, 'source_commit': recovery.SOURCE_COMMIT,
                   'packet_logical_sha256': recovery.PACKET, 'reason': 'Synthetic fixture',
                   'native_rebuild_requested': False, 'browser_rerun_requested': False,
                   'scientific_source_recomputation_requested': False,
                   'scientific_release_published': False, 'main_merged': False}
        recovery.verify_request(request)
        for key, value in [('packet_logical_sha256', '0' * 64), ('native_rebuild_requested', True),
                           ('scientific_source_recomputation_requested', True), ('main_merged', True)]:
            bad = {**request, key: value}
            with self.subTest(key=key), self.assertRaises(ValueError):
                recovery.verify_request(bad)


if __name__ == '__main__':
    unittest.main()
