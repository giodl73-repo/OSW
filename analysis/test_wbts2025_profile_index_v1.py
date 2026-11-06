import unittest
from capture_wbts2025_profile_index_v1 import listing
class Tests(unittest.TestCase):
    def test_exact_index_and_safe_product_names(self):
        raw=b'Index of GC_2025_02/FINAL_ADCP_PRODUCTS <a href="cast001.asc">file</a><a href="cast001.nc">nc</a><a href="../other.asc">outside</a><a href="https://other/cast002.asc">elsewhere</a>'
        self.assertEqual(listing(raw),['cast001.asc','cast001.nc'])
    def test_wrong_directory_or_challenge_rejected(self):
        for raw in [b'403',b'Index of GC_2005_05/FINAL_ADCP_PRODUCTS <a href="cast001.asc">x</a>']:
            with self.assertRaises(ValueError):listing(raw)
    def test_no_products_rejected(self):
        with self.assertRaises(ValueError):listing(b'Index of GC_2025_02/FINAL_ADCP_PRODUCTS')
if __name__=='__main__':unittest.main()
