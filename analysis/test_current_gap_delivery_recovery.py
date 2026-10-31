"""Publication control checks with tiny clean-Git fixtures; no data rebuild."""
from pathlib import Path
import contextlib
import io
import os
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import recover_current_gap_cloud_delivery as recovery

ROOT=Path(__file__).resolve().parents[1]
SOURCE_COMMIT='6866981896abb5caffd29f9d46c6c76933d4c8ef'


class CleanPublicationCacheChecks(unittest.TestCase):
    def test_fresh_publication_git_excludes_audits_without_hiding_source_changes(self):
        base=subprocess.check_output(['git','-c','core.fsmonitor=false','show',SOURCE_COMMIT+':.gitignore'],cwd=ROOT)
        fixed=(ROOT/'.gitignore').read_bytes()
        self.assertEqual(fixed,base+(b'' if base.endswith(b'\n') else b'\n')+b'.pytest_cache/\n')
        with TemporaryDirectory() as folder:
            root=Path(folder)
            git=['git','-c','core.fsmonitor=false','-c','maintenance.auto=0','-c','gc.auto=0']
            subprocess.run(git+['init','--quiet'],cwd=root,check=True,capture_output=True)
            cache=root/'.pytest_cache/current-gap-publication/source'
            cache.mkdir(parents=True);(cache/'result.json').write_bytes(b'{"status":"PASS"}')
            (root/'research').mkdir();(root/'research/unexpected-source.json').write_bytes(b'{}')
            for ignore,expected_audit in [(base,True),(fixed,False)]:
                (root/'.gitignore').write_bytes(ignore)
                names=subprocess.check_output(git+['ls-files','--others','--exclude-standard'],cwd=root,text=True).splitlines()
                self.assertEqual('.pytest_cache/current-gap-publication/source/result.json' in names,expected_audit)
                self.assertIn('research/unexpected-source.json',names)
                self.assertFalse((root/'.pytest_cache/.gitignore').exists())

    def test_recovery_allows_only_the_exact_operational_change_set(self):
        base=b'# synthetic old ignore\n'
        recovery.verify_control_delta(dict(recovery.CONTROL_FILES),base,recovery.corrected_ignore(base))
        for path in ['rust/osw-query/src/lib.rs','research/ocean-current-width-inventory.json',
                     'almanac/query-data.json','analysis/davidson_wallace_width_admission.py']:
            changes=dict(recovery.CONTROL_FILES);changes[path]='M'
            with self.subTest(path=path),self.assertRaises(ValueError):
                recovery.verify_control_delta(changes,base,recovery.corrected_ignore(base))
        changes=dict(recovery.CONTROL_FILES);changes['.gitignore']='D'
        with self.assertRaises(ValueError):recovery.verify_control_delta(changes,base,recovery.corrected_ignore(base))
        with self.assertRaises(ValueError):
            recovery.verify_control_delta(dict(recovery.CONTROL_FILES),base,recovery.corrected_ignore(base)+b'research/\n')

    def test_recovery_cannot_publish_from_the_local_machine(self):
        with patch.dict(os.environ,{},clear=True),patch('sys.argv',['recover','--publish','--audit-dir','missing']),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:recovery.main()
            self.assertEqual(error.exception.code,2)


if __name__=='__main__':unittest.main()
