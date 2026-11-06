import unittest
from capture_wsc_f3_bounded_preview_v1 import preview_link

class PreviewCustody(unittest.TestCase):
    def test_only_the_original_explicit_bounded_view_is_selected(self):
        raw=b'<a href="?format=textfile">Download dataset</a><a href="?format=html">View dataset as HTML</a>'
        self.assertEqual(preview_link(raw),'https://doi.pangaea.de/10.1594/PANGAEA.800346?format=html')
    def test_mirror_wrong_identity_or_unbounded_format_is_rejected(self):
        for target in ['https://elsewhere.example/?format=html','/10.1594/PANGAEA.800347?format=html','?format=textfile']:
            with self.assertRaises(ValueError):preview_link(('<a href="'+target+'">View dataset as HTML</a>').encode())
    def test_absent_or_ambiguous_preview_never_guesses_a_download_url(self):
        with self.assertRaises(ValueError):preview_link(b'<a href="?format=textfile">Download dataset</a>')
        with self.assertRaises(ValueError):preview_link(b'<a href="?format=html">View dataset as HTML</a>'*2)

if __name__=='__main__':unittest.main()
