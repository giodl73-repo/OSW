import copy
import json
import unittest
from pathlib import Path
from check_norkyst_ingoy_timeline import validate
from build_norkyst_ingoy_timeline import profile

ROOT = Path(__file__).resolve().parents[1]


class TimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT/'research/norkyst-ingoy-2024-section-timeline.json').read_text(encoding='utf-8'))

    def test_source_reconstruction(self):
        validate(self.data)

    def test_reject_invented_metric_and_date_and_field(self):
        for change in ['width','date','field','extrema']:
            data = copy.deepcopy(self.data)
            if change == 'width': data['frames'][0]['current_width_km'] = 100
            if change == 'date': data['frames'][0]['sample_time_utc'] = '2024-01-15T00:00:00Z'
            if change == 'field': data['frames'][0]['profile'][0]['salinity'] = 99
            if change == 'extrema': data['annual_extrema_eligible'] = True
            with self.assertRaises(ValueError): validate(data)

    def test_land_and_fill_do_not_interpolate(self):
        receipt = json.loads((ROOT/self.data['frames'][0]['receipt_file']).read_text(encoding='utf-8'))
        for row in receipt['packed_field_arrays']['sea_mask']:
            row[:] = [0]*len(row)
        self.assertTrue(all(point['salinity'] is None for point in profile(receipt)))
        for row in receipt['packed_field_arrays']['sea_mask']:
            row[:] = [1]*len(row)
        for row in receipt['packed_field_arrays']['salinity']:
            row[:] = [-32767]*len(row)
        self.assertTrue(all(point['salinity'] is None for point in profile(receipt)))


if __name__ == '__main__': unittest.main()
