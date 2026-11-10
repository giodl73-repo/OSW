import unittest
from acquire_pratt2000_bab_mandab_primary_v1 import inspect,NoRedirect
class Page:
    def __init__(self,text):self.text=text
    def get_text(self):return self.text
class Tests(unittest.TestCase):
    def sample(self):return [Page('Continuous Dynamical Modes Bab al Mandab PRATT MURRAY JOHNS 2000')]+[Page('text') for _ in range(19)]
    def test_exact_identity_and_page_scope(self):
        pages,n=inspect(self.sample());self.assertEqual(len(pages),20);self.assertEqual(n,1);self.assertEqual(pages[-1]['pdf_page'],20)
    def test_wrong_page_count(self):
        with self.assertRaises(ValueError):inspect(self.sample()[:-1])
    def test_wrong_primary_identity(self):
        p=self.sample();p[0]=Page('Other article')
        with self.assertRaises(ValueError):inspect(p)
    def test_text_or_numeric_limit(self):
        for body in ['x'*180001,'1 '*10001]:
            p=self.sample();p[-1]=Page(body)
            with self.assertRaises(ValueError):inspect(p)
    def test_no_redirect(self):self.assertIsNone(NoRedirect().redirect_request(None,None,None,None,None,None))
if __name__=='__main__':unittest.main()
