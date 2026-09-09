import importlib.util
import json
import pathlib
import sys
import unittest


ANALYSIS = pathlib.Path(__file__).parent
sys.path.insert(0, str(ANALYSIS))
MODULE_PATH = ANALYSIS / "derive_motion_region_passports.py"
SPEC = importlib.util.spec_from_file_location("derive_motion_region_passports", MODULE_PATH)
passports = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(passports)


class MotionRegionPassportTests(unittest.TestCase):
    def test_committed_passports_cover_frozen_regions(self):
        root = ANALYSIS.parent
        payload = json.loads((root / "research" / "osw-motion-region-passports-2018.json").read_text(encoding="utf-8"))
        self.assertEqual(22, len(payload["regions"]))
        self.assertEqual(22, len({item["region_code"] for item in payload["regions"]}))
        self.assertIn("no composite rank", payload["status"])


if __name__ == "__main__":
    unittest.main()
