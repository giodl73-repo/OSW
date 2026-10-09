"""Transport retries cannot bypass source pins or leave partial local originals."""
import hashlib, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from acquire_local_paper_fixtures import acquire, download, verify

DATA=b'%PDF-1.7\ncontrolled source fixture'
MANIFEST={'source_url':'https://example.invalid/paper.pdf','sha256':hashlib.sha256(DATA).hexdigest()}

class AcquisitionTests(unittest.TestCase):
    def test_book_filename_and_path_restriction(self):
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder);manifest=dict(MANIFEST,document_filename='source-book.pdf')
            (directory/'acquisition.json').write_text(json.dumps(manifest),encoding='utf8')
            with patch('urllib.request.urlopen',return_value=io.BytesIO(DATA)):
                self.assertEqual(acquire('gouriou-atlantic-1988',directory),DATA)
            self.assertEqual((directory/'source-book.pdf').read_bytes(),DATA)
            for name in ['../outside.pdf','nested/book.pdf','C:/outside.pdf']:
                manifest['document_filename']=name;(directory/'acquisition.json').write_text(json.dumps(manifest),encoding='utf8')
                with patch('urllib.request.urlopen') as opener,self.assertRaises(ValueError):acquire('gouriou-atlantic-1988',directory)
                opener.assert_not_called()

    def test_large_government_report_cap_and_pin_are_fixture_specific(self):
        data=b'%PDF-'+b'x'*50_913_968
        manifest=dict(MANIFEST,sha256=hashlib.sha256(data).hexdigest())
        self.assertEqual(verify('glenn-wac-2008',manifest,data),data)
        for name in ['qiu-chen-nec-2010','florida-archer-2017']:
            with self.assertRaisesRegex(ValueError,'expected a PDF below'):verify(name,manifest,data)
        with self.assertRaisesRegex(ValueError,'checksum'):verify('glenn-wac-2008',MANIFEST,data)

    def setUp(self):
        self.scratch=Path(__file__).resolve().parents[1]/'.pytest_cache'/'paper-acquisition-tests'
        self.scratch.mkdir(parents=True,exist_ok=True)

    def test_timeout_and_transient_http_retry_then_pin(self):
        errors=[URLError(TimeoutError('timeout')),HTTPError(MANIFEST['source_url'],503,'busy',{},None)]
        with patch('urllib.request.urlopen',side_effect=[*errors,io.BytesIO(DATA)]) as opener,patch('time.sleep') as sleep:
            self.assertEqual(download('qiu-chen-nec-2010',MANIFEST),DATA)
            self.assertEqual(opener.call_count,3)
            self.assertEqual([c.args[0] for c in sleep.call_args_list],[1,3])
            self.assertTrue(all(c.kwargs['timeout']==60 for c in opener.call_args_list))

    def test_retry_exhaustion_and_nontransient_response(self):
        with patch('urllib.request.urlopen',side_effect=TimeoutError('timeout')) as opener,patch('time.sleep'):
            with self.assertRaises(TimeoutError):download('qiu-chen-nec-2010',MANIFEST)
            self.assertEqual(opener.call_count,3)
        with patch('urllib.request.urlopen',side_effect=HTTPError(MANIFEST['source_url'],403,'forbidden',{},None)) as opener,patch('time.sleep') as sleep:
            with self.assertRaises(HTTPError):download('qiu-chen-nec-2010',MANIFEST)
            self.assertEqual(opener.call_count,1);sleep.assert_not_called()

    def test_integrity_failure_never_retries_or_persists(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as folder:
            directory=Path(folder);(directory/'acquisition.json').write_text(json.dumps(MANIFEST),encoding='utf-8')
            for data in [b'<html>error</html>',b'%PDF-wrong bytes']:
                with patch('urllib.request.urlopen',return_value=io.BytesIO(data)) as opener,patch('time.sleep') as sleep:
                    with self.assertRaises(ValueError):acquire('qiu-chen-nec-2010',directory)
                    self.assertEqual(opener.call_count,1);sleep.assert_not_called()
                    self.assertFalse((directory/'journal-article.pdf').exists())
                    self.assertFalse(list(directory.glob('.paper-*.tmp')))

    def test_existing_pinned_copy_is_offline_and_failed_staging_cleans_up(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as folder:
            directory=Path(folder);(directory/'acquisition.json').write_text(json.dumps(MANIFEST),encoding='utf-8')
            with patch('urllib.request.urlopen',return_value=io.BytesIO(DATA)),patch('os.fsync',side_effect=OSError('disk write failed')):
                with self.assertRaises(OSError):acquire('qiu-chen-nec-2010',directory)
            self.assertFalse((directory/'journal-article.pdf').exists())
            self.assertFalse(list(directory.glob('.paper-*.tmp')))
            (directory/'journal-article.pdf').write_bytes(DATA)
            with patch('urllib.request.urlopen') as opener:
                self.assertEqual(acquire('qiu-chen-nec-2010',directory),DATA);opener.assert_not_called()
            (directory/'journal-article.pdf').write_bytes(b'%PDF-stale')
            with patch('urllib.request.urlopen') as opener,self.assertRaises(ValueError):
                acquire('qiu-chen-nec-2010',directory)
            opener.assert_not_called()

    def test_successful_staging_and_size_limit(self):
        with tempfile.TemporaryDirectory(dir=self.scratch) as folder:
            directory=Path(folder);(directory/'acquisition.json').write_text(json.dumps(MANIFEST),encoding='utf-8')
            with patch('urllib.request.urlopen',return_value=io.BytesIO(DATA)):
                self.assertEqual(acquire('qiu-chen-nec-2010',directory),DATA)
            self.assertEqual((directory/'journal-article.pdf').read_bytes(),DATA)
            self.assertFalse(list(directory.glob('.paper-*.tmp')))
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'%PDF-'+b'x'*20_000_000)) as opener,patch('time.sleep') as sleep:
            with self.assertRaisesRegex(ValueError,'below 20 MB'):download('qiu-chen-nec-2010',MANIFEST)
            self.assertEqual(opener.call_count,1);sleep.assert_not_called()

if __name__=='__main__':unittest.main()
