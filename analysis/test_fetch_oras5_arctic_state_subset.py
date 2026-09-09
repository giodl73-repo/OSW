import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_arctic_state_subset.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_arctic_state_subset", PATH)
module = importlib.util.module_from_spec(SPEC); assert SPEC.loader; SPEC.loader.exec_module(module)


class ArcticStateSubsetTests(unittest.TestCase):
    def test_builds_all_four_native_field_urls(self):
        urls = module.source_urls("201802", "https://example.test/root")
        self.assertEqual({"votemper", "vosaline", "vozocrtx", "vomecrty"}, set(urls))
        self.assertTrue(urls["vosaline"].endswith("201802_grid_T_02.nc"))
        self.assertTrue(urls["vozocrtx"].endswith("201802_grid_U_02.nc"))
        self.assertTrue(urls["vomecrty"].endswith("201802_grid_V_02.nc"))

    def test_rejects_invalid_or_out_of_archive_month(self):
        for value in ("2018-02", "201813", "201902"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.source_urls(value)


if __name__ == "__main__":
    unittest.main()
