"""Check independent geometry and failure modes before using model widths."""
import copy
from collections import Counter,defaultdict
import json
import math
import unittest

import kuroshio_axis_normal as k


def straight(left=124,right=125):
    return {name:[[lon,24+i*.05] for i in range(21)]
            for name,lon in [('axis',124.5),('left',left),('right',right)]}


class NormalGeometryTests(unittest.TestCase):
    def test_straight_axis_geodesic_normal_and_unknown_error(self):
        row=k.measure(straight(),24.5,14)
        self.assertEqual(row['status'],'resolved')
        self.assertTrue(100<row['span_km']<103)
        self.assertAlmostEqual(row['axis_tangent_azimuth_degrees'],0,places=8)
        self.assertTrue(all(e['normal_residual_m']<.001 for e in row['edges'].values()))
        self.assertLess(row['inverse_vs_signed_offset_residual_m'],.001)
        for field in ['boundary_fallback_occurred','threshold_attained','physical_uncertainty_km']:
            self.assertIsNone(row[field])

    def test_oblique_axis_is_not_latitude_span(self):
        curves={name:[[lon+i*.05,24+i*.05] for i in range(21)]
                for name,lon in [('axis',124),('left',123.5),('right',124.5)]}
        normal=k.measure(curves,24.5,14)
        fixed=k.base.section_span(curves,24.5)
        self.assertEqual(normal['status'],'resolved');self.assertEqual(fixed['status'],'resolved')
        self.assertTrue(.65<normal['span_km']/fixed['span_km']<.8)

    def test_different_boundary_vertex_counts_do_not_pair_indices(self):
        curves=straight();first=k.measure(curves,24.5,14)
        curves['right']=[[125,24],[125,24.3],[125,24.6],[125,24.9],[125,25]]
        second=k.measure(curves,24.5,14)
        self.assertEqual(second['status'],'resolved')
        self.assertAlmostEqual(first['span_km'],second['span_km'],places=7)

    def test_missing_boundary_break_is_not_bridged(self):
        curves=straight();curves['left']=[[124,24.4],None,[124,24.6]]
        self.assertEqual(k.measure(curves,24.5,14)['status'],'boundary_crossing_missing_or_multiple')

    def test_tangent_cannot_cross_missing_axis_point(self):
        curves=straight();curves['axis'][12]=None
        self.assertEqual(k.measure(curves,24.5,14)['status'],'tangent_missing_source_vertex')

    def test_tangent_is_not_extrapolated_at_endpoint(self):
        curves=straight();curves['axis']=curves['axis'][:12]
        self.assertEqual(k.measure(curves,24.5,14)['status'],'tangent_reaches_source_endpoint')

    def test_reversed_order_or_provider_labels_are_not_repaired(self):
        curves=straight();curves['axis'].reverse()
        self.assertEqual(k.measure(curves,24.5,14)['status'],'reversed_local_axis_latitude_direction')
        curves=straight();curves['left'],curves['right']=curves['right'],curves['left']
        self.assertEqual(k.measure(curves,24.5,14)['status'],'provider_sides_do_not_bracket_axis')

    def test_multiple_boundary_crossings_are_not_selected(self):
        curves=straight();curves['left']=[[124,24.3],[124,24.7],[123.9,24.3]]
        row=k.measure(curves,24.5,14)
        self.assertEqual(row['status'],'boundary_crossing_missing_or_multiple')
        self.assertEqual(row['boundary_crossing_counts']['left'],2)
        self.assertEqual(len(row['ambiguous_boundary_candidates']['left']),2)

    def test_long_boundary_segment_remains_a_rejection(self):
        curves=straight();curves['left']=[[124,24],[124,25]]
        self.assertEqual(k.measure(curves,24.5,14)['status'],'boundary_source_segment_exceeds_50km')

    def test_axis_latitude_overlap_is_unresolved(self):
        curves=straight();curves['axis']=[[124.5,24.4],[124.5,24.5],[124.6,24.5],[124.6,24.6]]
        self.assertEqual(k.measure(curves,24.5,7)['status'],'axis_gate_overlap')

    def test_normal_overlap_is_unresolved(self):
        curves={name:[[lon,-.5+i*.05] for i in range(21)]
                for name,lon in [('axis',124.5),('left',124),('right',125)]}
        curves['left']=[[124,0],[124.2,0]]
        self.assertEqual(k.measure(curves,0,14)['status'],'boundary_normal_overlap')

    def test_source_transect_exceedance_is_flagged_without_clipping(self):
        row=k.measure(straight(123.7,125.3),24.5,14)
        self.assertEqual(row['status'],'resolved');self.assertTrue(row['span_km']>140)
        self.assertTrue(row['exceeds_source_nominal_140km_transect'])
        self.assertIsNone(row['boundary_fallback_occurred'])

    def test_local_search_guard_does_not_shrink_width(self):
        self.assertEqual(k.measure(straight(124,127),24.5,14)['status'],'edge_outside_200km_search_guard')

    def test_ids_use_case_identity(self):
        self.assertEqual(k.sample_id('2024-02-29',23,24.5,14),
                         'dimension:kuroshio:wang-v1:2024-02-29:z23:normal-24p5n-t14km-v1')
        ids={k.sample_id('2024-02-29',level,latitude,window)
             for level in k.base.LEVELS for latitude in k.base.SECTIONS for window in k.WINDOWS}
        self.assertEqual(len(ids),45)


class RetainedReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=k.verify_inputs()

    def test_complete_case_identity_and_unknowns(self):
        doc=self.doc;rows=doc['cases']
        expected={k.sample_id(f'2024-{month:02}-{day:02}',level,latitude,window)
                  for month,days in enumerate([31,29,31,30,31,30,31,31,30,31,30,31],1)
                  for day in range(1,days+1) for level in k.base.LEVELS
                  for latitude in k.base.SECTIONS for window in k.WINDOWS}
        self.assertEqual({r['id'] for r in rows},expected)
        self.assertEqual(len(rows),len(expected))
        self.assertEqual(dict(Counter(r['status'] for r in rows)),doc['status_counts'])
        self.assertFalse(doc['velocity_normal_verified']);self.assertFalse(doc['ocean_connectivity_verified'])
        self.assertFalse(doc['physical_width_inventory_admitted'])
        self.assertEqual(doc['numerical_readback']['longitude_latitude_decimal_places'],7)
        self.assertEqual(doc['numerical_readback']['azimuth_degrees_decimal_places'],6)
        self.assertEqual(doc['numerical_readback']['unrounded_normal_residual_acceptance_m'],.001)
        for row in rows:
            for key in ['physical_uncertainty_km','boundary_fallback_occurred','threshold_attained']:
                self.assertIsNone(row[key])
            self.assertEqual(row['span_km'] is not None,row['status']=='resolved')

    def test_every_resolved_normal_by_forward_geodesic_and_spherical_check(self):
        for row in self.doc['cases']:
            if row['status']!='resolved':continue
            for kind,edge in row['edges'].items():
                bearing=row['right_normal_azimuth_degrees']+(180 if kind=='left' else 0)
                lon,lat,_=k.base.GEOD.fwd(*row['gate']['point'],bearing,abs(edge['signed_normal_offset_km'])*1000)
                self.assertLess(k.base.distance([lon,lat],edge['point'])*1000,.03)
                self.assertLessEqual(edge['normal_residual_m'],.001)
            left,right=[row['edges'][kind]['point'] for kind in ('left','right')]
            a,b,c,d=map(math.radians,[*left,*right])
            hav=math.sin((d-b)/2)**2+math.cos(b)*math.cos(d)*math.sin((c-a)/2)**2
            spherical=6371.0088*2*math.asin(math.sqrt(hav))
            self.assertLess(abs(spherical-row['span_km'])/row['span_km'],.006)
            self.assertLess(abs(k.base.distance(left,right)-row['span_km'])*1000,.03)

    def test_all_monthly_and_annual_summaries_from_retained_attempts(self):
        groups=defaultdict(list)
        for row in self.doc['cases']:
            for month in [None,int(row['sample_date'][5:7])]:
                groups[row['source_level'],row['latitude'],row['tangent_half_window_km'],month].append(row)
        self.assertEqual(len(groups),len(self.doc['summaries']))
        for summary in self.doc['summaries']:
            selected=groups[summary['source_level'],summary['latitude'],summary['tangent_half_window_km'],summary['month']]
            self.assertEqual(len(selected),summary['attempted_count'])
            self.assertEqual(dict(Counter(r['status'] for r in selected)),summary['status_counts'])
            for key,value in k.base.summary([r['span_km'] for r in selected if r['status']=='resolved']).items():
                self.assertEqual(summary[key],value)

    def test_existing_latitude_comparisons_are_exact_and_not_relabelled(self):
        previous=json.loads((k.ROOT/k.base.FILE).read_bytes())
        index={(r['date'],r['source_level'],s['latitude']):s for r in previous['daily'] for s in r['sections']}
        for row in self.doc['cases']:
            old=index[row['sample_date'],row['source_level'],row['latitude']]
            self.assertEqual(row['comparison_latitude_span_km'],old['span_km'])
            self.assertEqual(row['comparison_latitude_span_status'],old['status'])
            if row['status']=='boundary_crossing_missing_or_multiple':
                for kind,count in row['boundary_crossing_counts'].items():
                    if count>1:self.assertEqual(len(row['ambiguous_boundary_candidates'][kind]),count)

    def test_figure_receipt_and_accessible_scope(self):
        receipt=json.loads((k.ROOT/'research/kuroshio-wang-2024-axis-normal-figure.json').read_bytes())
        for path,pin in receipt['input_sha256'].items():self.assertEqual(k.base.digest(path),pin)
        self.assertEqual(k.base.digest(k.FIGURE),receipt['figure_sha256'])
        text=(k.ROOT/k.FIGURE).read_text(encoding='utf-8')
        self.assertIn('role="img"',text)
        self.assertIn('not physical uncertainty intervals or footprints',text)
        self.assertIn('not a verified instantaneous velocity normal',text)


if __name__=='__main__':unittest.main()
