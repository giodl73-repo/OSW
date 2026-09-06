import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_agulhas_m3_contract_view.py")
SPEC = importlib.util.spec_from_file_location("build_agulhas_m3_contract_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasM3ContractViewTests(unittest.TestCase):
    def test_shipped_plate_keeps_contract_boundary(self):
        path = pathlib.Path(__file__).parents[1] / "figures" / "osw-m3-agulhas-experiment-contract.svg"
        if not path.exists():
            self.skipTest("generated figure not built")
        svg = path.read_text(encoding="utf-8")
        self.assertEqual(5, svg.count("NOT PROMOTED"))
        self.assertIn("GEOMETRY ACQUIRED", svg)
        self.assertIn("NO RAW 3-D VELOCITY", svg)
        self.assertIn("ODD CROSSINGS", svg)
        self.assertIn("10.5194/os-17-1067-2021", svg)


if __name__ == "__main__":
    unittest.main()
