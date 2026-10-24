"""Generated covers cannot change journal data, hide corruption or replace originals."""
import hashlib,io,json,re,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from acquire_local_paper_fixtures import acquire,verify
import melet_hal_source as source

class MeletSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=(source.DIRECTORY/'journal-article.pdf').read_bytes() if (source.DIRECTORY/'journal-article.pdf').exists() else (source.DIRECTORY/source.CURRENT_FILENAME).read_bytes()
        cls.manifest=json.loads((source.DIRECTORY/'acquisition.json').read_bytes())
        # Controlled metadata-only fixture; never substitutes for the retained original.
        reader=PdfReader(io.BytesIO(cls.original));date=str(reader.metadata['/CreationDate'])[2:16].encode()
        cls.variant=cls.original.replace(date,b'20261014012345',1)
        assert cls.variant!=cls.original

    def test_metadata_variant_keeps_all_journal_resources(self):
        proof=source.verify_rendition(self.variant,self.manifest)
        self.assertEqual(proof['reviewed_original_sha256'],source.ORIGINAL_SHA)
        self.assertEqual(proof['response_sha256'],hashlib.sha256(self.variant).hexdigest())
        self.assertEqual(verify('melet-solomon-2010',self.manifest,self.variant),self.variant)

    def test_scientific_content_and_resource_byte_changes_rejected(self):
        reader=PdfReader(io.BytesIO(self.variant));stream=reader.pages[1].raw_get('/Contents').get_object();payload=stream._data
        self.assertEqual(self.variant.count(payload),1)
        changed=bytearray(payload);changed[len(changed)//2]^=1
        bad=self.variant.replace(payload,bytes(changed),1)
        with self.assertRaisesRegex(ValueError,'journal|protected'):source.verify_rendition(bad,self.manifest)
        # Same-length page geometry alteration, with all text/streams untouched.
        geometry=b'/MediaBox [0.0 0.0 566.99 756.0]'
        self.assertIn(geometry,self.variant)
        bad=self.variant.replace(geometry,geometry.replace(b'566.99',b'567.99',1),1)
        with self.assertRaises(ValueError):source.verify_rendition(bad,self.manifest)

    def test_other_paper_receipt_or_cover_identity_rejected(self):
        for manifest in [dict(self.manifest,sha256='0'*64),dict(self.manifest,source_url='https://example.invalid/paper.pdf')]:
            with self.subTest(manifest=manifest),self.assertRaises(ValueError):source.verify_rendition(self.variant,manifest)
        with self.assertRaises(ValueError):verify('other-paper',self.manifest,self.variant)
        producer=b'/Producer <FEFF005000440046004C0061005400650058>'
        self.assertIn(producer,self.variant)
        changed=self.variant.replace(producer,producer[:-2]+b'9>',1)
        with self.assertRaises(ValueError):source.verify_rendition(changed,self.manifest)

    def test_fresh_hydration_stages_full_rendition_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);(directory/'acquisition.json').write_text(json.dumps(self.manifest),encoding='utf-8')
            with patch('urllib.request.urlopen',return_value=io.BytesIO(self.variant)):
                self.assertEqual(acquire('melet-solomon-2010',directory),self.variant)
            self.assertFalse((directory/'journal-article.pdf').exists())
            self.assertEqual((directory/source.CURRENT_FILENAME).read_bytes(),self.variant)
            self.assertEqual(source.resolve_source(directory),directory/source.CURRENT_FILENAME)
            self.assertFalse(list(directory.glob('.paper-*')))

    def test_corrupt_retained_original_is_not_hidden_by_valid_rendition(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);(directory/'acquisition.json').write_text(json.dumps(self.manifest),encoding='utf-8');(directory/'journal-article.pdf').write_bytes(self.variant);(directory/source.CURRENT_FILENAME).write_bytes(self.variant)
            with self.assertRaisesRegex(ValueError,'retained'):source.resolve_source(directory)
            with self.assertRaisesRegex(ValueError,'retained'),patch('urllib.request.urlopen') as opener:acquire('melet-solomon-2010',directory)
            opener.assert_not_called()

    def test_changed_contract_is_rejected_even_after_cache_hit(self):
        source.verify_rendition(self.variant,self.manifest)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'contract.json';path.write_bytes(source.CONTRACT.read_bytes()+b' ')
            with patch.object(source,'CONTRACT',path),self.assertRaisesRegex(ValueError,'contract'):source.verify_rendition(self.variant,self.manifest)

if __name__=='__main__':unittest.main()
