import copy
import json
import unittest
import build_agulhas_krug_2012_core_widths_v1 as m


class CoreWidthFactsTests(unittest.TestCase):
    def facts(self):return json.loads((m.ROOT/m.FACTS).read_bytes())

    def test_two_distinct_mean_metrics_with_exact_source_pointers(self):
        facts=self.facts();before=copy.deepcopy(facts);report=m.prepare(facts)
        self.assertEqual(facts,before)
        self.assertEqual([r['reported_mean_width_km'] for r in report['records']],[64,80])
        self.assertEqual([r['source_pointer'] for r in report['records']],['/records/0','/records/1'])
        self.assertIsNone(report['eligibility']['annual_width_range_km'])

    def test_wrong_current_duplicate_extra_and_changed_means_fail(self):
        for change in [lambda f:f['records'][0].update(current_id='agulhas-return'),
                       lambda f:f['records'].append(copy.deepcopy(f['records'][0])),
                       lambda f:f['records'][0].update(id=f['records'][1]['id']),
                       lambda f:f['records'][0].update(reported_mean_width_km=80)]:
            facts=self.facts();change(facts)
            with self.assertRaises(ValueError):m.prepare(facts)

    def test_width_range_dates_uncertainty_and_zero_variability_not_inferred(self):
        for change in [lambda f:f['eligibility'].update(annual_width_range_km=[64,80]),
                       lambda f:f['records'][0].update(reported_width_uncertainty_km=25),
                       lambda f:f['records'][1].update(exact_mean_estimation_start='2004-06'),
                       lambda f:f['seasonality_finding'].update(width_constant_claimed=True),
                       lambda f:f['source_ambiguities'][0].update(resolved=True),
                       lambda f:f['excluded_context'].update(mean_core_positions_are_width_midpoints=True)]:
            facts=self.facts();change(facts)
            with self.assertRaises(ValueError):m.prepare(facts)


if __name__=='__main__':unittest.main()
