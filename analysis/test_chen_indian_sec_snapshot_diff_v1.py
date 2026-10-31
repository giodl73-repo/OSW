import unittest
import chen_indian_sec_snapshot_diff_v1 as subject

class SnapshotDiff(unittest.TestCase):
    def test_pointer_key_and_type_differences_remain_explicit(self):
        rows=subject.differences({'a/b':None,'lost':1},{'a/b':0,'new':2})
        self.assertEqual({r['kind'] for r in rows},{'missing_key','extra_key','type'})
        self.assertTrue(any(r['pointer']=='/a~1b' for r in rows))
    def test_long_json_is_diagnosed_without_accepting_it(self):
        import json
        a=json.dumps({'padding':'x'*400,'count':1});b=json.dumps({'padding':'x'*400,'count':2})
        row=subject.differences(a,b)[0]
        self.assertEqual(row['semantic_difference_count'],1)
        self.assertTrue(row['first_semantic_differences'][0]['pointer'].endswith('/count'))

if __name__=='__main__':unittest.main()
