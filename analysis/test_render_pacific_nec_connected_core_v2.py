import unittest
from unittest.mock import patch
import render_pacific_nec_connected_core_v2 as render


class PresentationOnly(unittest.TestCase):
    def test_local_refusal_before_input_reads(self):
        with patch.dict(render.os.environ,{},clear=True),patch.object(render,'read',side_effect=AssertionError('No IO')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):render.guard()

    def test_exact_saved_report_and_changed_bytes_refusal(self):
        raw=(render.ROOT/render.REPORT).read_bytes();result=render.read(render.RESULT)
        self.assertEqual(len(render.saved_report(raw,result)['cases']),324)
        with self.assertRaises(ValueError):render.saved_report(raw+b' ',result)

    def test_wrong_custody_refused(self):
        raw=(render.ROOT/render.REPORT).read_bytes();result=render.read(render.RESULT);result['run_id']='other'
        with self.assertRaises(ValueError):render.saved_report(raw,result)


if __name__=='__main__':unittest.main()
