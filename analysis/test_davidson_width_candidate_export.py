"""Resource/entry-point gates only; never load the actual parent or index."""
import contextlib
import io
import unittest
from unittest.mock import patch

import export_davidson_width_candidate as exporter


class ExportGuards(unittest.TestCase):
    def test_requires_explicit_cloud_and_sufficient_resources(self):
        enough = dict(environment={'GITHUB_ACTIONS':'true'}, free_disk=4*1024**3,
                      available_memory=7*1024**3)
        exporter.require_cloud(True, **enough)
        for explicit, changes in [
            (False, {}), (True, {'environment':{}}),
            (True, {'free_disk':2*1024**3}),
            (True, {'available_memory':5*1024**3}),
            (True, {'available_memory':None}),
        ]:
            with self.subTest(explicit=explicit,changes=changes), self.assertRaises(ValueError):
                exporter.require_cloud(explicit, **{**enough, **changes})

    def test_local_cli_fails_before_memory_inspection_or_parent_loading(self):
        with patch.dict(exporter.os.environ, {}, clear=True), \
                patch('sys.argv', ['export_davidson_width_candidate.py','--cloud-candidate']), \
                patch.object(exporter.resources, 'memory_available') as memory, \
                patch.object(exporter, 'load_parent') as load, \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:exporter.main()
        self.assertEqual(error.exception.code,2)
        memory.assert_not_called()
        load.assert_not_called()


if __name__ == '__main__':unittest.main()
