import importlib.util
import pathlib
import unittest


PATH = pathlib.Path(__file__).with_name("analyze_oras5_drake_monthly_budget.py")
SPEC = importlib.util.spec_from_file_location("analyze_oras5_drake_monthly_budget", PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(module)


class DrakeMonthlyBudgetTests(unittest.TestCase):
    def test_month_axis_has_eleven_adjacent_intervals(self):
        self.assertEqual(12, len(module.MONTHS))
        self.assertEqual(11, len(list(zip(module.MONTHS, module.MONTHS[1:]))))
        self.assertEqual("201801", module.MONTHS[0])
        self.assertEqual("201812", module.MONTHS[-1])
        self.assertEqual(31, (module.DATES["201802"] - module.DATES["201801"]).days)
        self.assertEqual(28, (module.DATES["201803"] - module.DATES["201802"]).days)


if __name__ == "__main__":
    unittest.main()
