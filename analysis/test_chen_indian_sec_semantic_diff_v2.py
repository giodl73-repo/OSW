import unittest
from chen_indian_sec_semantic_diff_v2 import differences


class SemanticDiff(unittest.TestCase):
    def test_numeric_representation_does_not_hide_actual_corruption(self):
        expected={'representation':1000.0,'integer':9007199254740993,
                  'float':1.8446744073709552e19,'flag':True,'missing':None}
        actual={'representation':1000,'integer':9007199254740992,
                'float':18446744073709552000,'flag':1}
        delta=differences(expected,actual)
        self.assertEqual({d['pointer'] for d in delta},{'/integer','/float','/flag','/missing'})
        self.assertEqual(next(d for d in delta if d['pointer']=='/float')['kind'],'number')


if __name__=='__main__':unittest.main()
