import copy
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import eac_kerry_2020_mean_core_v1 as m

class MeanCore(unittest.TestCase):
    def test_exact_table_rows_keep_metric_and_regional_support(self):
        doc=m.build();rows=doc['records']
        self.assertEqual(len(rows),5)
        self.assertEqual(len({r['id'] for r in rows}),5)
        self.assertEqual(rows[0]['offshore_extent_km'],157.6)
        self.assertEqual(rows[-1]['maximum_depth_m'],1250)
        self.assertEqual(rows[2]['latitude_degrees_north'],-32.3)
        self.assertEqual(doc['source_labeling_discrepancy']['figure5_panel_c_header_latitude_degrees_north'],-32.0)
        self.assertEqual(rows[0]['source_component'],'upstream_coherent_jet')
        self.assertEqual(rows[-1]['source_component'],'southern_extension')

    def test_mean_geometry_cannot_become_seasonal_or_observational(self):
        doc=m.build()
        self.assertEqual(doc['method']['averaging_order'],'time_mean_velocity_then_contour_geometry')
        self.assertEqual(doc['method']['signed_mean_alongshore_velocity_contour_m_s'],-0.05)
        self.assertFalse(doc['method']['instantaneous_dimension_time_series_transcribed'])
        for row in doc['records']:
            for key in ['observed_period','calendar_months','fixed_depth_width_km','paired_edge_width_km',
                'uniform_current_thickness_m','annual_width_range_km','annual_depth_range_m',
                'numeric_uncertainty_km','numeric_depth_uncertainty_m','geometry','geographic_state_crossings']:
                self.assertIsNone(row[key],key)
            for key in ['whole_current_representative','seasonal_playback_eligible','physical_state_join_eligible']:
                self.assertFalse(row[key],key)
            self.assertEqual(row['independent_observation_count'],0)
            self.assertIsNone(row['simulation_period']['end_inclusive'])

    def test_changed_source_values_or_forster_latitude_refused(self):
        original=m.read(m.INPUT)
        for field,value in [('latitude_degrees_north',-32),('offshore_extent_km',220),('maximum_depth_m',1200)]:
            changed=copy.deepcopy(original);changed['rows'][2][field]=value
            with patch.object(m,'read',return_value=changed):
                with self.assertRaises(ValueError):m.build()

    def test_figures_keep_metrics_and_mean_qualification(self):
        doc=m.build()
        for compact in [False,True]:
            raw=m.figure(doc,compact);svg=ET.fromstring(raw)
            self.assertEqual(svg.tag,'{http://www.w3.org/2000/svg}svg')
            text=' '.join(svg.itertext())
            for value in ['Offshore extent','Maximum','1994–2016','mean','157.6','1,250']:
                self.assertIn(value,text)
            self.assertNotIn('<polyline',raw.decode())
            self.assertNotIn('<image',raw.decode())

if __name__=='__main__':unittest.main()
