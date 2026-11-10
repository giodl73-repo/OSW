"""Cadence, metadata, packed values and source identity for continuous sections."""
from datetime import datetime, timezone
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import norkyst_continuous_source as source


def synthetic(nt=2):
    blocks = []
    start = int(datetime(2024,1,1,tzinfo=timezone.utc).timestamp())
    def axes(name, temporal):
        if temporal:
            blocks.append(f'{name}.time[{nt}]\n' + ', '.join(str(start + i*3600) for i in range(nt)) + '\n')
            blocks.append(f'{name}.depth[1]\n10.0\n')
        for axis, indices in [('Y',source.Y),('X',source.X)]:
            blocks.append(f'{name}.{axis}[{len(indices)}]\n' + ', '.join(str(i*800) for i in indices) + '\n')
    for name in source.VARIABLES:
        lines = [f'{name}.{name}[{nt}][1][48][50]']
        for t in range(nt):
            for y in range(48):
                lines.append(f'[{t}][0][{y}], ' + ', '.join([str(200*t)]*50))
        blocks.append('\n'.join(lines) + '\n');axes(name,True)
    lines = ['sea_mask.sea_mask[48][50]']
    for y in range(48):lines.append(f'[{y}], ' + ', '.join(['1']*50))
    blocks.append('\n'.join(lines) + '\n');axes('sea_mask',False)
    return ('Dataset {}\n---------------------------------------------\n' + '\n'.join(blocks)).encode()


class ContinuousSourceTests(unittest.TestCase):
    def test_full_year_and_leap_day_have_exact_cadence_and_halos(self):
        requests = source.daily_requests(list(range(1,13)))
        self.assertEqual(sum(last-first+1 for _,first,last in requests),8784+72)
        self.assertEqual(requests[0],('2023-12-30',12,23))
        self.assertEqual(requests[-1],('2025-01-02',0,11))
        self.assertIn(('2024-02-29',0,23),requests)
        for month in [1,7]:
            self.assertEqual(sum(b-a+1 for _,a,b in source.daily_requests([month])),816)
        self.assertEqual(source.daily_requests([1,1]),source.daily_requests([1]))
        for month in [0,13,1.0,True]:
            with self.subTest(month=month),self.assertRaises(ValueError):source.month_window(month)

    def test_original_one_hour_reproduces_the_retained_packed_receipt(self):
        raw = (source.ROOT/'research/norkyst-ingoy-20240115.ascii').read_bytes()
        saved = json.loads((source.ROOT/'research/norkyst-ingoy-20240115.json').read_bytes())
        times, values = source.parse_fields(raw,'2024-01-15',12,12)
        self.assertEqual(times,[1705320000])
        for name in source.VARIABLES:
            np.testing.assert_array_equal(values[name][0],saved['packed_field_arrays'][name])
        np.testing.assert_array_equal(values['sea_mask'],saved['packed_field_arrays']['sea_mask'])

    def test_multiple_hour_row_indices_and_zero_are_preserved(self):
        times, values = source.parse_fields(synthetic(),'2024-01-01',0,1)
        self.assertEqual(times[1]-times[0],3600)
        self.assertTrue(np.all(values['u_eastward'][0] == 0))
        self.assertTrue(np.all(values['u_eastward'][1] == 200))
        self.assertEqual(values['salinity'].dtype,np.dtype('int16'))

    def test_missing_duplicate_and_wrong_cadence_rows_reject(self):
        raw = synthetic()
        variants = [raw.replace(b'[1][0][0],',b'[0][0][0],',1),
                    raw.replace(b'[2][1][48][50]',b'[1][1][48][50]',1),
                    raw.replace(b'1704070800',b'1704067200',1),
                    raw.replace(b'salinity.X[50]',b'salinity.X[49]',1)]
        for content in variants:
            with self.subTest(content=content[:30]),self.assertRaises(ValueError):
                source.parse_fields(content,'2024-01-01',0,1)

    def test_fractional_nonfinite_and_out_of_range_packed_values_reject(self):
        for value in [b'0.5',b'NaN',b'32768',b'-32769']:
            raw = synthetic().replace(b'[0][0][0], 0,',b'[0][0][0], '+value+b',',1)
            with self.subTest(value=value),self.assertRaises(ValueError):source.parse_fields(raw,'2024-01-01',0,1)

    def test_source_fill_is_preserved_before_scaling(self):
        raw = synthetic().replace(b'[0][0][0], 0,',b'[0][0][0], -32767,',1)
        _, values = source.parse_fields(raw,'2024-01-01',0,1)
        self.assertEqual(values['salinity'][0,0,0],-32767)

    def test_daily_metadata_rejects_changed_layer_units_packing_projection_and_identity(self):
        raw = (source.ROOT/source.SOURCE/'20240101.das').read_bytes()
        source.metadata(raw,'2024-01-01')
        for before,after in [(b'add_offset 30.0',b'add_offset 0.0'),
                             (b'scale_factor 0.001',b'scale_factor 1.0'),
                             (b'standard_parallel 60.0',b'standard_parallel 70.0'),
                             (b'"seconds since 1970-01-01 00:00:00"',b'"hours since 1970-01-01 00:00:00"'),
                             (b'"Norkyst_v3"',b'"Different_model"'),
                             (b'"CC-BY-4.0"',b'"Other_terms"')]:
            changed = raw.replace(before,after)
            # The license contains a URL and identifier in one string.
            if before == b'"CC-BY-4.0"':changed=raw.replace(b'CC-BY-4.0',b'Other_terms')
            self.assertNotEqual(changed,raw)
            with self.subTest(before=before),self.assertRaises(ValueError):source.metadata(changed,'2024-01-01')
        with self.assertRaises(ValueError):source.metadata(raw,'2024-01-02')

    def test_frozen_rule_bytes_are_not_replaced_by_a_coherent_rehash(self):
        source.preflight()
        original=Path.read_bytes;target=source.ROOT/source.SOURCE/'preflight.json'
        def altered(path):
            raw=original(path)
            if path==target:
                doc=json.loads(raw);doc['fully_blinded']=True;return json.dumps(doc).encode()
            return raw
        with patch.object(Path,'read_bytes',altered),self.assertRaises(ValueError):source.preflight()


if __name__ == '__main__':unittest.main()
