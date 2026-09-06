import hashlib
import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("fetch_geomar_agulhas_derived.py")
SPEC = importlib.util.spec_from_file_location("fetch_geomar_agulhas_derived", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class GeomarAgulhasFetchTests(unittest.TestCase):
    def test_shipped_files_match_published_fetch_manifest(self):
        data = ROOT / "atlas/data/geomar-agulhas"
        for name, expected in module.FILES.items():
            self.assertEqual(expected, hashlib.sha256((data / name).read_bytes()).hexdigest())

    def test_archive_is_https(self):
        self.assertTrue(module.BASE_URL.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
