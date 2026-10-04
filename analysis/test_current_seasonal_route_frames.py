import copy
import json
import unittest
from check_current_seasonal_route_frames import ROOT, validate

class SeasonalFrameTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "research/ocean-current-seasonal-route-frames.json").read_text(encoding="utf-8"))
        self.reports = {row["route_candidate_file"]: json.loads((ROOT / row["route_candidate_file"]).read_text(encoding="utf-8")) for row in self.document["frames"]}
        self.widths = json.loads((ROOT / self.document['width_inventory_file']).read_text(encoding='utf-8'))

    def test_rejects_scope_metadata_and_annual_extrema(self):
        document = copy.deepcopy(self.document)
        document["frames"][0]["layer"] = "all depths"
        with self.assertRaises(ValueError):
            validate(document, self.reports, self.widths)
        document = copy.deepcopy(self.document)
        document["comparability"][0]["annual_length_range_km"] = [600,1500]
        with self.assertRaises(ValueError):
            validate(document, self.reports, self.widths)

    def test_rejects_invalid_calendar_and_duplicate_frames(self):
        document = copy.deepcopy(self.document)
        document["frames"][0]["calendar_months"] = [0,13]
        with self.assertRaises(ValueError):
            validate(document, self.reports, self.widths)
        document = copy.deepcopy(self.document)
        document["frames"][1] = copy.deepcopy(document["frames"][0])
        with self.assertRaises(ValueError):
            validate(document, self.reports, self.widths)

    def test_rejects_wrong_width_identity_calendar_and_uniform_buffer(self):
        index = next(i for i, row in enumerate(self.document['frames']) if row['current_id'] == 'davidson')
        for key, value in [('width_measurement_ids', ['northern-mediterranean-winter-width']), ('width_measurement_ids', ['missing']), ('calendar_months', [6,7]), ('width_support_role', 'uniform_route_buffer'), ('width_scope_note', '')]:
            document = copy.deepcopy(self.document)
            document['frames'][index][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(document, self.reports, self.widths)

    def test_rejects_reversed_direction_and_unsupported_source_months(self):
        index = next(i for i, row in enumerate(self.document['frames']) if row['current_id'] == 'monsoon' and row['flow_direction'] == 'eastward')
        validate(self.document, self.reports, self.widths)
        for key, value in [('flow_direction', 'westward'), ('calendar_months', [3,4,5]), ('source_season_label', 'autumn')]:
            document = copy.deepcopy(self.document)
            document['frames'][index][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(document, self.reports, self.widths)

if __name__ == "__main__":
    unittest.main()
