import unittest
from unittest.mock import patch
import check_atlantic_nec_reference_parent_v1 as audit


class ParentTests(unittest.TestCase):
    def test_local_refusal_before_payload_or_network(self):
        with patch.object(audit.os,'name','nt'),patch.object(audit.Path,'read_bytes',side_effect=AssertionError('No local payload access')),patch.object(audit,'api',side_effect=AssertionError('No network')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):audit.controls()

    def test_publication_identity_preserves_ambiguous_matches_for_review(self):
        records=[{'id':'a','doi':'10.1016/S0967-0645(98)00109-X'},
            {'id':'b','url':'https://doi.org/10.1016/S0967-0645%2898%2900109-X'},
            {'id':'c','title':'The mean flow field of the tropical Atlantic Ocean'},
            {'id':'d','url':'https://example.org/stramma99a.pdf'},
            {'id':'unrelated','title':'A different Atlantic study'}]
        self.assertEqual([r['id'] for r in audit.publication_matches(records)],['a','b','c','d'])

    def test_workflow_matches_scoped_request_and_compact_outputs(self):
        text=(audit.ROOT/audit.WORKFLOW).read_text(encoding='utf8')
        self.assertEqual(text.count(audit.REQUEST),3)
        self.assertIn('group: osw-current-gap-delivery',text)
        self.assertIn('cancel-in-progress: false',text)
        self.assertIn(audit.OUT.relative_to(audit.ROOT).as_posix()+'/*.json',text)
        self.assertIn(audit.OUT.relative_to(audit.ROOT).as_posix()+'/*.png',text)


if __name__=='__main__':unittest.main()
