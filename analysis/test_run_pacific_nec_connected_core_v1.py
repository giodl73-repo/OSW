import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import run_pacific_nec_connected_core_v1 as driver


class SavedSourceReplay(unittest.TestCase):
    def test_local_refusal_before_network_or_input_reads(self):
        with patch.dict(driver.os.environ,{},clear=True), \
             patch.object(driver,'read',side_effect=AssertionError('No file reads')), \
             patch.object(driver,'api',side_effect=AssertionError('No network')):
            with self.assertRaisesRegex(ValueError,'Cloud-only'):driver.guard()

    def test_only_exact_saved_source_bytes_can_be_extracted(self):
        contents={'metadata.json':b'{}','vectors.csv':b'bounded\r\n','acquisition.json':b'{}\n'}
        expected={k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in contents.items()}
        for case in ('valid','extra','corrupt','symlink'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);archive=root/'saved.zip'
                with zipfile.ZipFile(archive,'w') as saved:
                    for name,raw in contents.items():
                        item=zipfile.ZipInfo(name)
                        if case=='symlink' and name=='vectors.csv':item.create_system=3;item.external_attr=0o120777<<16
                        saved.writestr(item,b'bounded\n\n' if case=='corrupt' and name=='vectors.csv' else raw)
                    if case=='extra':saved.writestr('../outside',b'bad')
                if case=='valid':
                    driver.extract_source(archive,root/'source',expected)
                    self.assertEqual((root/'source/vectors.csv').read_bytes(),contents['vectors.csv'])
                else:
                    with self.assertRaises(ValueError):driver.extract_source(archive,root/'source',expected)
                self.assertFalse((root/'outside').exists())


if __name__=='__main__':unittest.main()
