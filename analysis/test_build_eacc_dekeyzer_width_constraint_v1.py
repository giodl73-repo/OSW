import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build_eacc_dekeyzer_width_constraint_v1 as m


class SourceProductCustodyTests(unittest.TestCase):
    def fixture(self,root):
        facts=(m.ROOT/m.FACTS).read_bytes();target=root/m.FACTS
        target.parent.mkdir(parents=True);target.write_bytes(facts)
        (root/m.PREFLIGHT).write_bytes(m.encoded({'input_sha256':{m.FACTS:hashlib.sha256(facts).hexdigest()}}))
        return target

    def test_changed_frozen_source_is_refused_before_render_or_product_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);target=self.fixture(root)
            facts=json.loads(target.read_bytes());facts['records'][0]['reported_bound_km']=150
            target.write_bytes(m.encoded(facts))
            with patch.object(m,'ROOT',root),patch.object(m,'render',side_effect=AssertionError('Unexpected render')):
                with self.assertRaisesRegex(ValueError,'Frozen input differs'):m.build()
            self.assertFalse((root/m.REPORT).exists());self.assertFalse((root/m.FIGURE).exists())

    def test_executed_report_is_never_overwritten_or_rendered_again(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root)
            target=root/m.REPORT;target.write_bytes(b'previous executed report')
            with patch.object(m,'ROOT',root),patch.object(m,'render',side_effect=AssertionError('Unexpected rerender')):
                with self.assertRaisesRegex(ValueError,'Refuse to overwrite'):m.build()
            self.assertEqual(target.read_bytes(),b'previous executed report')


if __name__=='__main__':unittest.main()
