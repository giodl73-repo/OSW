import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_oras5_drake_state_subset.py")
SPEC = importlib.util.spec_from_file_location("fetch_oras5_drake_state_subset", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeStateSubsetTests(unittest.TestCase):
    def test_builds_exact_native_field_urls(self):
        urls = module.source_urls("201802", "https://example.test/root")
        self.assertEqual(
            "https://example.test/root/votemper/opa0/votemper_ORAS5_1m_201802_grid_T_02.nc",
            urls["votemper"],
        )
        self.assertTrue(urls["vozocrtx"].endswith("201802_grid_U_02.nc"))
        self.assertTrue(urls["vomecrty"].endswith("201802_grid_V_02.nc"))

    def test_rejects_bad_month(self):
        for value in ("2018-02", "201813", "20180"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "YYYYMM"):
                module.source_urls(value)

    def test_rejects_year_outside_fixed_archive_contract(self):
        with self.assertRaisesRegex(ValueError, "1979 through 2018"):
            module.source_urls("201902")


if __name__ == "__main__":
    unittest.main()
