import importlib.util
import json
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("build_oras5_arctic_gate_readiness_view.py")
SPEC = importlib.util.spec_from_file_location("build_oras5_arctic_gate_readiness_view", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)
ROOT = pathlib.Path(__file__).parents[1]


class ArcticGateReadinessViewTests(unittest.TestCase):
    def test_view_preserves_gate_verdict_and_claim_boundary(self):
        payload = json.loads((ROOT / "research/osw-m3-oras5-arctic-gate-readiness.json").read_text(encoding="utf-8"))
        svg = module.build(payload, ROOT / "atlas/data/oras5-arctic-entrances-mesh.nc")
        self.assertIn("ONE GATE FITS THE GRID. ONE DOES NOT.", svg)
        self.assertIn("60 NATIVE FACES", svg)
        self.assertIn("OBSERVATIONAL PROXY OR MODEL CLOSURE", svg)
        self.assertIn("WET T CELL IN ORCA025", svg)
        self.assertIn("mixed U/V staircase", svg)
        self.assertIn("NO VOLUME OR HEAT TRANSPORT", svg)


if __name__ == "__main__":
    unittest.main()
