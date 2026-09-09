import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("prepare_agulhas_m3_experiment.py")
SPEC = importlib.util.spec_from_file_location("prepare_agulhas_m3_experiment", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class AgulhasM3ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = module.build()

    def test_contract_does_not_claim_an_estimate(self):
        self.assertIn("no raw M3 velocity", self.contract["boundary"])
        self.assertIn("unavailable_for_new_execution", self.contract["status"])

    def test_crossing_definitions_remain_separate(self):
        destination = self.contract["reference_design"]["destination"]
        self.assertIn("at least one", destination["exchange_definition"])
        self.assertIn("odd number", destination["retention_definition"])

    def test_geometry_is_resolved_but_other_m2_gaps_fail(self):
        self.assertEqual(6, len(self.contract["m2_gap_audit"]))
        verdicts = {item["dimension"]: item["verdict"] for item in self.contract["m2_gap_audit"]}
        self.assertEqual("resolved_for_replication", verdicts["destination"])
        self.assertEqual(5, sum(value == "fail" for value in verdicts.values()))

    def test_heat_requires_its_own_convention(self):
        self.assertIn("optional", self.contract["required_outputs"]["heat"])
        self.assertTrue(any("reference-temperature identity" in item for item in self.contract["acceptance_tests"]))


if __name__ == "__main__":
    unittest.main()
