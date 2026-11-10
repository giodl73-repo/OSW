"""Old phase-controlled deliveries must not compete with scoped data requests."""
import fnmatch
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
FILES=('baffin-bound-candidate.yml','davidson-width-candidate.yml','indian-coastal-context-candidate.yml')


class DeliveryTriggerIsolation(unittest.TestCase):
    def test_only_explicit_phase_or_own_workflow_changes_start_old_deliveries(self):
        for name in FILES:
            path='.github/workflows/'+name
            header=(ROOT/path).read_text(encoding='utf8').split('concurrency:',1)[0]
            selected=re.findall(r'^      - ([^\r\n]+)$',header,re.MULTILINE)
            self.assertEqual(selected,['research/current-gap-delivery-phase.json',path])
            self.assertIn('branches: [codex/current-measurement-gaps]',header)
            self.assertNotIn('paths-ignore:',header)
            for unrelated in ('analysis/pacific_nec_core_sampling_v1.py',
                              'research/pacific-nec-core-sampling-request-v1.json',
                              'research/pacific-nec-core-sampling-execution-review-v1.json',
                              'almanac/query.js','.gitattributes'):
                self.assertFalse(any(fnmatch.fnmatchcase(unrelated,p) for p in selected))

    def test_all_jobs_permissions_workers_and_concurrency_are_byte_identical(self):
        for name in FILES:
            old=(ROOT/'research/current-gap-trigger-parent-v1'/name).read_bytes()
            new=(ROOT/'.github/workflows'/name).read_bytes()
            self.assertEqual(old.split(b'concurrency:',1)[1],new.split(b'concurrency:',1)[1])
            self.assertIn(b'cancel-in-progress: false',new)


if __name__=='__main__':unittest.main()
