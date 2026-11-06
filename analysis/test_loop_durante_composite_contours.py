"""Geometry, masks, ambiguity and exact-source checks for the declared experiment."""
import copy
import json
import unittest
from unittest.mock import patch
import numpy as np
from pyproj import Geod
from shapely.geometry import Polygon, box
from loop_durante_composite_contours import ROOT,OUTPUT,GEOD,build,sample,orient,assess,case,line_parts,sha
from build_cartographic_current_state_join import project


class CompositeContourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=build()

    def grid(self):
        x=np.arange(-87,-80.875,.125);y=np.arange(21,26.125,.125)
        u=np.full((len(y),len(x)),.3);v=u.copy()
        return x,y,u,v

    def test_all_cases_and_nominal_source_paths_reproduce(self):
        self.assertEqual(self.actual,json.loads((ROOT/OUTPUT).read_bytes()))
        self.assertEqual(len(self.actual['cases']),54)
        self.assertEqual(len({c['id'] for c in self.actual['cases']}),54)
        self.assertEqual(sum(c['nominal'] for c in self.actual['cases']),2)
        self.assertEqual(sum(c['status']=='unique_supported_path' for c in self.actual['cases']),54)
        for c in self.actual['cases']:
            with self.subTest(case=c['id']):
                self.assertEqual(len(c['supported_component_indices']),1)
                p=c['components'][c['supported_component_indices'][0]]
                self.assertTrue(p['all_midpoints_supported'])
                self.assertGreater(p['minimum_along_path_m_s'],0)
                lon,lat=np.asarray(p['coordinates_lon_lat']).T
                expected=Geod(ellps='WGS84').line_length(lon,lat)/1000
                self.assertEqual(round(expected,1),p['geometric_path_length_km'])
                # Each stored piece is a millimetre readback of its geodesic length.
                difference_m=abs(sum(s['piece_length_m'] for s in p['midpoint_samples'])-expected*1000)
                self.assertLessEqual(difference_m,len(p['midpoint_samples'])*.0005+1e-6)
                for sample in p['midpoint_samples']:
                    vector=sample['velocity'];corners=np.asarray(vector['corner_eastward_northward_m_s'])
                    reconstructed=np.asarray(vector['bilinear_weights'])@corners
                    # Four weight readbacks plus one velocity readback bound the reconstruction.
                    allowance=np.sum(np.abs(corners),axis=0)*.5e-8+.5e-8+1e-14
                    np.testing.assert_array_less(np.abs(reconstructed-[vector['eastward_m_s'],vector['northward_m_s']]),allowance)

    def test_masks_are_strict_even_at_zero_weight_corner(self):
        x,y,u,v=self.grid()
        clean=sample(x,y,u,v,-86,22)
        self.assertIsNotNone(clean)
        i,j=clean['cell_row_column'];u[i+1,j+1]=np.nan
        self.assertIsNone(sample(x,y,u,v,-86,22))

    def test_bilinear_vector_values_and_source_corners(self):
        x,y,u,v=self.grid();xx,yy=np.meshgrid(x,y)
        u=xx+2*yy;v=3*xx-yy
        result=sample(x,y,u,v,-85.94,22.03)
        self.assertAlmostEqual(result['eastward_m_s'],-85.94+2*22.03)
        self.assertAlmostEqual(result['northward_m_s'],3*-85.94-22.03)
        self.assertAlmostEqual(sum(result['bilinear_weights']),1)
        self.assertIsNone(sample(x,y,u,v,-90,22))

    def test_orientation_closed_rings_and_wrong_gate(self):
        path=[[-86,21.875],[-85,23],[-81.5,24]]
        self.assertEqual(orient(path[::-1],21.875,-81.5),path)
        self.assertIsNone(orient(path+[path[0]],21.875,-81.5))
        self.assertIsNone(orient([[-86,21.875],[-81.5,26]],21.875,-81.5))

    def test_missing_and_opposing_samples_are_retained(self):
        x,y,u,v=self.grid();path=[[-86,21.875],[-85,23],[-81.5,24]]
        clean=assess(path,x,y,u,v,Polygon());self.assertTrue(clean['supported'])
        p=clean['midpoint_samples'][len(clean['midpoint_samples'])//2]
        i,j=p['velocity']['cell_row_column'];u[i,j]=np.nan
        missing=assess(path,x,y,u,v,Polygon())
        self.assertIn('missing_velocity_along_path',missing['rejection_reasons'])
        self.assertIsNone(missing['mean_vector_speed_m_s'])
        self.assertEqual(len(missing['midpoint_samples']),len(clean['midpoint_samples']))
        x,y,u,v=self.grid();opposing=assess(path,x,y,-u,-v,Polygon())
        self.assertIn('wrong_gateway_flow_direction',opposing['rejection_reasons'])
        self.assertIn('opposing_along_path_velocity',opposing['rejection_reasons'])

    def test_two_supported_components_stay_ambiguous(self):
        x,y,u,v=self.grid()
        lines=[np.array([[-86.5,21],[-85.5,23],[-81,24]]),np.array([[-86,21],[-85,22.5],[-81,23.5]])]
        result=case(lines,'Synthetic',.55,0,0,x,y,u,v,Polygon())
        self.assertEqual(result['status'],'ambiguous_supported_paths')
        self.assertEqual(len(result['supported_component_indices']),2)
        self.assertIsNone(result['supported_contour_path_length_km'])
        self.assertIsNone(result['rounded_supported_contour_path_km'])

    def test_coarse_land_crossing_blocks_support_without_editing_geometry(self):
        x,y,u,v=self.grid();path=[[-86,21.875],[-85,23],[-81.5,24]]
        px,py=project(-85,23);result=assess(path,x,y,u,v,box(px-.2,py-.2,px+.2,py+.2))
        self.assertIn('coarse_atlas_land_crossing',result['rejection_reasons'])
        self.assertGreater(result['geometric_path_length_km'],0)

    def test_source_and_protocol_changes_cannot_silently_recalculate(self):
        with patch('loop_durante_composite_contours.PROTOCOL_SHA','0'*64):
            with self.assertRaisesRegex(ValueError,'Changed declared contour protocol'):build()
        self.assertFalse(self.actual['reference_route_admitted'])
        self.assertFalse(self.actual['rank_eligible'])
        self.assertIsNone(self.actual['whole_current_length_km'])
        self.assertIsNone(self.actual['annual_length_range_km'])
        self.assertIsNone(self.actual['width_km'])

    def test_figure_pins_and_every_declared_case(self):
        figure=json.loads((ROOT/'research/loop-durante-2026-composite-contour-figure.json').read_bytes())
        self.assertEqual(figure['source_report_sha256'],sha(ROOT/OUTPUT))
        self.assertEqual(figure['generator_sha256'],sha(ROOT/figure['generator_file']))
        self.assertEqual(set(figure['all_drawn_case_ids']),{c['id'] for c in self.actual['cases']})
        self.assertEqual(len(figure['all_drawn_case_ids']),54)
        for path,pin in figure['figures'].items():self.assertEqual(sha(ROOT/path),pin)
        self.assertFalse(figure['annual_range_admitted'])


if __name__=='__main__':unittest.main()
