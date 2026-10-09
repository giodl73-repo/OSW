"""Transport retries cannot bypass source pins or leave partial local originals."""
import hashlib, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from acquire_local_paper_fixtures import acquire, download, verify, PINNED_MIRRORS

DATA=b'%PDF-1.7\ncontrolled source fixture'
MANIFEST={'source_url':'https://example.invalid/paper.pdf','sha256':hashlib.sha256(DATA).hexdigest()}

class AcquisitionTests(unittest.TestCase):
    def mirror_case(self):
        key=next(iter(PINNED_MIRRORS));name,url,sha=key
        return name,dict(MANIFEST,source_url=url,sha256=sha),PINNED_MIRRORS[key]

    def test_blocked_primary_uses_verified_mirror_without_changing_manifest(self):
        name,manifest,mirrors=self.mirror_case();before=dict(manifest)
        with patch('urllib.request.urlopen',side_effect=[HTTPError(manifest['source_url'],403,'blocked',{},None),io.BytesIO(DATA)]) as opener,patch('acquire_local_paper_fixtures.verify',return_value=DATA) as check,patch('time.sleep') as sleep:
            self.assertEqual(download(name,manifest),DATA)
            self.assertEqual([c.args[0].full_url for c in opener.call_args_list],[manifest['source_url'],mirrors[0]])
            check.assert_called_once_with(name,manifest,DATA);sleep.assert_not_called()
        self.assertEqual(manifest,before)

    def test_mirror_registry_requires_exact_fixture_source_and_pin(self):
        name,manifest,_=self.mirror_case()
        cases=[('other-paper',manifest),(name,dict(manifest,source_url='https://example.invalid/changed.pdf')),(name,dict(manifest,sha256=MANIFEST['sha256']))]
        for fixture,receipt in cases:
            with self.subTest(fixture=fixture,receipt=receipt):
                with patch('urllib.request.urlopen',side_effect=HTTPError(receipt['source_url'],403,'blocked',{},None)) as opener,patch('time.sleep') as sleep:
                    with self.assertRaises(HTTPError):download(fixture,receipt)
                    self.assertEqual(opener.call_count,1);sleep.assert_not_called()

    def test_integrity_failure_at_primary_or_mirror_never_falls_through(self):
        name,manifest,_=self.mirror_case()
        for responses in [[io.BytesIO(DATA)],[HTTPError(manifest['source_url'],403,'blocked',{},None),io.BytesIO(DATA)]]:
            with self.subTest(attempts=len(responses)):
                with patch('urllib.request.urlopen',side_effect=responses) as opener,patch('time.sleep') as sleep:
                    with self.assertRaisesRegex(ValueError,'checksum'):download(name,manifest)
                    self.assertEqual(opener.call_count,len(responses));sleep.assert_not_called()

    def test_all_mirrors_blocked_identifies_fixture_and_failed_location(self):
        name,manifest,mirrors=self.mirror_case();urls=[manifest['source_url'],*mirrors]
        errors=[HTTPError(url,403,'blocked',{},None) for url in urls]
        with patch('urllib.request.urlopen',side_effect=errors) as opener,patch('time.sleep') as sleep:
            with self.assertRaises(HTTPError) as caught:download(name,manifest)
            self.assertEqual(opener.call_count,len(urls));sleep.assert_not_called()
            self.assertIn(f'{name}: acquisition failed at {urls[-1]}',caught.exception.__notes__)

    def test_corrupt_mirror_is_not_staged_as_an_original(self):
        name,manifest,_=self.mirror_case()
        with tempfile.TemporaryDirectory() as folder:
            directory=Path(folder);(directory/'acquisition.json').write_text(json.dumps(manifest),encoding='utf8')
            with patch('urllib.request.urlopen',side_effect=[HTTPError(manifest['source_url'],403,'blocked',{},None),io.BytesIO(DATA)]):
                with self.assertRaisesRegex(ValueError,'checksum'):acquire(name,directory)
            self.assertFalse((directory/'journal-article.pdf').exists())
            self.assertFalse(list(directory.glob('.paper-*.tmp')))

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
