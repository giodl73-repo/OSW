import copy
import json
import unittest
from check_antarctic_slope_jet_constraint import ROOT, ID, load, record, validate_row, validate_inventory, svg


class DatedJetConstraintTests(unittest.TestCase):
    def test_dated_strict_description_is_not_numeric_whole_current_width(self):
        row = record()
        validate_row(row)
        self.assertEqual(row['observed_period'], {'start':'2009-02-23','end':'2009-02-23'})
        self.assertEqual(row['reported_width_constraint']['operator'], 'lt')
        self.assertIsNone(row['approximate_width_km'])
        self.assertIsNone(row['width_range_km'])
        self.assertIn('original PDF', svg())

    def test_rejects_point_interval_date_depth_and_under_current_reassignment(self):
        row = record()
        for key, value in [('approximate_width_km',28), ('width_range_km',[0,28]),
                           ('observed_period',{'start':'2010-07-02','end':'2010-07-02'}),
                           ('fixed_layer_bounds_m',[0,3000]), ('calendar_months',[2]),
                           ('current_id','antarctic-slope-undercurrent'), ('annual_extrema_eligible',True)]:
            bad = copy.deepcopy(row)
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate_row(bad)
        for key, value in [('operator','le'), ('reference_scale_km',30), ('lower_bound_km',0), ('is_rigorous_upper_bound',True)]:
            bad = copy.deepcopy(row)
            bad['reported_width_constraint'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): validate_row(bad)

    def test_missing_record_and_coherent_source_support_rewrite_fail(self):
        d = json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        d['measurements'] = [r for r in d['measurements'] if r['id'] != ID]
        with self.assertRaises(ValueError): validate_inventory(d)
        a = load()
        a['measurement']['original_regional_context']['bathy_is_width_layer'] = True
        bad = record()
        bad['original_regional_context']['bathy_is_width_layer'] = True
        with self.assertRaises(ValueError): validate_row(bad,a)

    def test_unknown_extra_owner_record_cannot_bypass_identifier_selector(self):
        from check_current_width_inventory import validate as validate_all
        d = json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
        extra = record()
        extra['id'] = 'unreviewed-antarctic-jet'
        del extra['original_regional_context']
        d['measurements'].append(extra)
        d['counts']['measurements'] += 1
        next(r for r in d['current_decisions'] if r['current_id']=='antarctic-slope')['measurement_ids'].append(extra['id'])
        ledger = json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
        with self.assertRaisesRegex(ValueError, 'Antarctic Slope jet constraint'):
            validate_all(d, ledger)


if __name__ == '__main__': unittest.main()
