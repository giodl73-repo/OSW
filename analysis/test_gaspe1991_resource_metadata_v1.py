import copy,unittest
from capture_gaspe1991_resource_metadata_v1 import IDENTITY,inventory
class Tests(unittest.TestCase):
    def setUp(self):self.p={'success':True,'result':{'name':IDENTITY,'title':'Original dataset','license_id':'government-open-license-canada','resources':[{'id':'one','url':'https://original.example/data.dat','format':'DAT','size':100}],'extras':[]}}
    def test_preserves_original_resource_metadata_without_fields(self):
        r=inventory(self.p);self.assertEqual(r['resources'][0]['url'],'https://original.example/data.dat');self.assertEqual(r['resources'][0]['size'],100);self.assertFalse(r['native_fields_inspected']);self.assertEqual(r['depth_measurements_emitted'],0)
    def test_wrong_record_or_failed_response_rejected(self):
        for p in [{'success':False},dict(self.p,result=dict(self.p['result'],name='different'))]:
            with self.assertRaises(ValueError):inventory(p)
    def test_no_resource_url_guessing(self):
        p=copy.deepcopy(self.p);del p['result']['resources'][0]['url']
        with self.assertRaises(ValueError):inventory(p)
    def test_empty_resources_not_fabricated(self):
        p=copy.deepcopy(self.p);p['result']['resources']=[];self.assertEqual(inventory(p)['resources'],[])
if __name__=='__main__':unittest.main()
