import copy
import io
import itertools
import json
import math
import unittest
from pathlib import Path
import collect_norkyst_jutland_depth_v1 as m


class SourceSections(unittest.TestCase):
    def setUp(self):
        self.op = json.loads((m.ROOT / m.OPERATOR).read_bytes())

    def test_joint_preflight_source_budget_and_no_ingoy_replay(self):
        pf = m.preflight(self.op)
        self.assertEqual(len(pf['plans']), 12)
        self.assertLess(pf['total_reserved_decoded_scalar_values'], 250000)
        self.assertLess(pf['total_reserved_decoded_bytes'], 7000000)
        self.assertEqual(pf['provider_fixed_z_levels'], 25)
        self.assertTrue(all(len(p['y_indices']) == 39 for p in pf['plans']))
        self.assertFalse(pf['new_requests_overlap_prior_ingoy_support'])

    def test_declared_component_and_dates_cannot_change(self):
        for key, value in [('component_bearing_degrees_true', 90), ('dates', ['2024-01-01'])]:
            op = copy.deepcopy(self.op); op[key] = value
            with self.assertRaises(ValueError): m.preflight(op)

    def test_out_of_domain_and_old_ingoy_support_refused(self):
        for center in [[0,0], [24,72]]:
            op = copy.deepcopy(self.op); op['sections'][0]['editorial_center_lon_lat'] = center
            with self.assertRaises(ValueError): m.preflight(op)

    def test_parse_all_original_ordered_grid_rows(self):
        text = 'q.q[1][2][3][1]\n' + '\n'.join('[0][' + str(k) + '][' + str(j) + '], ' + str(k*3+j) for k in range(2) for j in range(3)) + '\n\n'
        self.assertEqual(m.parse_array(text, 'q', [1,2,3,1]), [0,1,2,3,4,5])
        for bad in [text.replace('[0][1][1], 4\n', ''), text.replace('[0][1][1], 4', '[0][1][2], 4'), text+text]:
            with self.assertRaises(ValueError): m.parse_array(bad, 'q', [1,2,3,1])

    def test_coordinate_maps_and_shape_refused_if_changed(self):
        self.assertEqual(m.vector('q.depth[3]\n0, 1, 2\n', 'q', 'depth', 3), [0,1,2])
        for text in ['q.depth[2]\n0,1\n', 'q.depth[3]\n0,nan,2\n']:
            with self.assertRaises(ValueError): m.vector(text, 'q', 'depth', 3)
        with self.assertRaises(ValueError): m.parse_array('q.q[2][1]\n[0], 1\n[1], 2\n\n', 'q', [3,1])

    def test_original_packing_and_nulls(self):
        self.assertIsNone(m.decode(-32767))
        self.assertEqual(m.decode(500), .5)
        self.assertEqual(m.decode(4500, 30), 34.5)
        for value in [1.5, float('nan'), float('inf'), 32768]:
            with self.assertRaises(ValueError): m.decode(value)

    def test_frozen_threshold_trace_keeps_missing_bottom_censored(self):
        columns = [[.2] * 9 + [None] * 16, [.3] * 9 + [None] * 16, [.2] * 9 + [None] * 16]
        diagnosis = m.diagnose(m.DEPTH, columns, self.op['diagnostic'])
        self.assertEqual(diagnosis['selected_column_index'], 1)
        primary = diagnosis['selected_column_threshold_layers'][1]
        self.assertEqual(primary['lower_status'], 'censored_before_missing_or_dry_level')
        self.assertEqual(primary['lower_last_connected_depth_m'], 25)
        self.assertIsNone(primary['lower_depth_m'])
        self.assertIsNone(primary['layer_thickness_m'])

    def test_gate_edge_maximum_has_no_weaker_replacement(self):
        columns = [[.4] * 25, [.3] * 25, [.2] * 25]
        diagnosis = m.diagnose(m.DEPTH, columns, self.op['diagnostic'])
        self.assertEqual(diagnosis['selected_column_index'], 0)
        self.assertEqual(diagnosis['horizontal_selection_status'], 'section_gate_edge_maximum_axis_unresolved')

    def test_all_frozen_daily_metadata_and_packing_validate(self):
        for date in self.op['dates']:
            raw = (m.ROOT / ('research/norkyst-ingoy-source-metadata-' + date.replace('-','') + '.das')).read_bytes()
            m.validate_metadata(raw, date)
            with self.assertRaises(ValueError): m.validate_metadata(raw.replace(b'CC-BY-4.0', b'changed'), date)

    def test_transport_failure_has_one_attempt_and_no_retry(self):
        calls = []
        def fail(*args, **kwargs): calls.append(1); raise TimeoutError('synthetic failure')
        receipt = {}
        with self.assertRaises(TimeoutError): m.read_target({'case_index':0,'http_url':'https://example.com'}, receipt, fail)
        self.assertEqual(calls, [1]); self.assertEqual(receipt['status'], 'failed_no_retry')

    def test_oversized_body_rejected_before_derivation(self):
        class Response(io.BytesIO):
            status = 200
            url = 'https://example.com'
            headers = {}
        receipt = {}
        with self.assertRaises(ValueError):
            m.read_target({'case_index':0,'http_url':'https://example.com'}, receipt, lambda *a, **k: Response(b'0'*120001))
        self.assertEqual(receipt['status'], 'failed_no_retry')

    def test_full_response_pipeline_retains_mask_censor_and_source_roles(self):
        from pyproj import CRS, Transformer
        p = m.preflight(self.op)['plans'][0]; p['y_indices'] = p['y_indices'][:3]
        inverse = Transformer.from_crs(CRS.from_proj4(m.PROJ), 4326, always_xy=True)
        positions = [inverse.transform(p['x_index']*800, y*800) for y in p['y_indices']]
        chunks = []
        for name in m.FIELDS:
            shape = [1,25,3,1] if name in m.FIELDS[:3] else [3,1]
            if name in m.FIELDS[:2]: values = [([100,200,100][i] if z<=25 else -32767) for z in m.DEPTH for i in range(3)]
            elif name == 'salinity': values = [4500]*75
            elif name == 'lon': values = [v[0] for v in positions]
            elif name == 'lat': values = [v[1] for v in positions]
            elif name == 'h': values = [100]*3
            else: values = [0,1,1]
            chunk = name+'.'+name+''.join('['+str(n)+']' for n in shape)+'\n'
            for index, value in zip(itertools.product(*(range(n) for n in shape[:-1])), values):
                chunk += ''.join('['+str(i)+']' for i in index)+', '+str(value)+'\n'
            chunk += '\n'
            if name in m.FIELDS[:3]:
                axes = {'time':[m.datetime.fromisoformat(p['date']+'T12:00:00+00:00').timestamp()], 'depth':m.DEPTH,
                        'Y':[y*800 for y in p['y_indices']], 'X':[p['x_index']*800]}
                for axis, values in axes.items(): chunk += name+'.'+axis+'['+str(len(values))+']\n'+', '.join(map(str,values))+'\n\n'
            chunks.append(chunk)
        result = m.derive(''.join(chunks).encode(), p, self.op)
        self.assertTrue(all(v is None for v in result['columns'][0]['northeast_component_m_s']))
        self.assertEqual(result['diagnosis']['selected_column_index'], 1)
        primary = result['diagnosis']['selected_column_threshold_layers'][1]
        self.assertEqual(primary['lower_last_connected_depth_m'], 25)
        self.assertIsNone(primary['lower_depth_m'])
        self.assertEqual(result['source_vertical_sampling'], 'provider_interpolated_fixed_z_not_native_ROMS_s_layers')
        self.assertFalse(result['salinity_gate_applied'])


if __name__ == '__main__': unittest.main()
