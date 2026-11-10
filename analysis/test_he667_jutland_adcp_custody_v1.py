import unittest
from acquire_he667_jutland_adcp_custody_v1 import observed_link,size_gate,header_only,BASENAME
class V:
    dimensions=('profile','depth');shape=(3,30);dtype='float32';units='m/s';long_name='eastward velocity'
    def __getitem__(self,key):raise AssertionError('No native arrays allowed in metadata stage')
class D:
    variables={'u':V()};dimensions={}
    def ncattrs(self):return ['title']
    def getncattr(self,k):return 'synthetic metadata'
class Tests(unittest.TestCase):
    def test_exact_observed_link(self):
        url='https://download.pangaea.de/dataset/988085/files/'+BASENAME
        self.assertEqual(observed_link(('<a href="'+url+'">nc</a>').encode()),url)
    def test_unknown_link_or_mirror_rejected(self):
        with self.assertRaises(ValueError):observed_link(b'<a href="https://other.example/file.nc">x</a>')
    def test_missing_or_oversize_metadata_blocks_fields(self):
        self.assertEqual(size_gate({})[0],'SOURCE_SIZE_UNRESOLVED_NO_FIELDS');self.assertIn('EXCEEDS',size_gate({'Content-Length':'1900001'})[0])
    def test_finite_complete_source_size(self):self.assertEqual(size_gate({'Content-Length':'1000'}),('SOURCE_WITHIN_OUTPUT_CUSTODY_CAP',1000))
    def test_header_does_not_read_arrays(self):
        r=header_only(D());self.assertEqual(r['native_array_values_decoded'],0);self.assertEqual(r['variables']['u']['shape'],[3,30])
if __name__=='__main__':unittest.main()
