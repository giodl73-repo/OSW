"""Exercise a real isolated Git object transaction and nonforce race refusal."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import pacific_secc_git_transport_v1 as transport


class GitTransport(unittest.TestCase):
    def test_exact_tree_preservation_and_nonforce_race_refusal(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / 'work'
            work.mkdir()
            try:
                os.chdir(work)
                transport.git('init', '--quiet')
                remote = str(root / 'remote.git')
                transport.git('init', '--quiet', '--bare', remote)
                transport.git('remote', 'add', 'origin', remote)
                transport.git('read-tree', '--empty')
                preserved = transport.store(b'keep exact\r\n')
                transport.git('update-index', '--add', '--cacheinfo', '100644', preserved, 'preserve.txt')
                source = transport.git('commit-tree', transport.git('write-tree'), '-m', 'parent')
                branch = 'codex/current-measurement-gaps'
                transport.publish(source, branch)
                raw = b'\0binary\xff\r\n'
                added = transport.store(raw)
                entries = [{'path': 'new.bin', 'mode': '100644', 'type': 'blob', 'sha': added}]
                candidate = transport.candidate(source, entries, root / 'private.index')
                self.assertEqual(transport.objects(candidate, ['preserve.txt'])['preserve.txt'],
                    {'oid': preserved, 'byteSize': len(b'keep exact\r\n')})
                self.assertEqual(transport.objects(candidate, ['new.bin'])['new.bin'],
                    {'oid': added, 'byteSize': len(raw)})
                transport.publish(candidate, branch)
                sibling = transport.git('commit-tree', transport.git('rev-parse', source + '^{tree}'),
                                         '-p', source, '-m', 'stale competing transaction')
                with self.assertRaises(subprocess.CalledProcessError):
                    transport.publish(sibling, branch)
                self.assertIn(candidate, transport.git('ls-remote', 'origin', 'refs/heads/' + branch))
                self.assertEqual(transport.git('ls-remote', 'origin', 'refs/heads/main'), '')
            finally:
                os.chdir(previous)


if __name__ == '__main__':
    unittest.main()
