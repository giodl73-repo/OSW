import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "validate.yml"


class CiContractTests(unittest.TestCase):
    def test_offline_gate_runs_complete_local_contract(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        for command in (
            'python -m unittest discover -s analysis -p "test_*.py"',
            "python -m compileall -q analysis",
            "node --check atlas/app.js",
        ):
            self.assertIn(command, source)
        self.assertNotIn("fetch_oisst_snapshot.py --", source)

    def test_optional_job_installs_pin_and_runs_fixture(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("requirements-observations.txt", source)
        self.assertIn("test_netcdf_fixture_preserves_dimensions_order_and_mask", source)
        self.assertIn("test_fixture_selects_exact_pressure_stride_and_mask", source)
        self.assertIn("permissions:\n  contents: read", source)


if __name__ == "__main__":
    unittest.main()
