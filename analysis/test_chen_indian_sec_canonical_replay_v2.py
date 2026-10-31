import copy
import math
import unittest
import chen_indian_sec_ridge_query_v2 as subject

class CanonicalReplay(unittest.TestCase):
    def report(self):
        return {'rows':[{'length_km':4700.0,'coordinates':[[105.15,-11.0]],'flags':[],'approximate_length_km':4700,'resolution_scenarios':[{'length_km':4600.0}]}],
                'cases':[{'nominal_grid_length_km':4700.0,'computed_method_resolution_span_km':[4400.0,4800.0]}]}
    def test_arithmetic_roundoff_preserves_canonical(self):
        a=self.report();b=copy.deepcopy(a);b['rows'][0]['length_km']+=32*math.ulp(4700.0)
        self.assertEqual(len(subject.compare_report(a,b)),1);self.assertEqual(a['rows'][0]['length_km'],4700.0)
    def test_both_ulp_and_absolute_bounds_apply(self):
        for value,delta in [(4700.0,65*math.ulp(4700.0)),(1e10,1e-5)]:
            with self.assertRaises(ValueError):subject.compare_report({'rows':[{'length_km':value}]},{'rows':[{'length_km':value+delta}]})
    def test_geometry_year_flag_and_rounding_changes_refused(self):
        for field in ['geometry','year','flag','rounded']:
            a=self.report();b=copy.deepcopy(a)
            if field=='geometry':b['rows'][0]['coordinates'][0][0]+=math.ulp(105.15)
            elif field=='year':b['rows'][0]['year']=1995
            elif field=='flag':b['rows'][0]['flags']=['new']
            else:b['rows'][0]['approximate_length_km']=4800
            with self.assertRaises(ValueError):subject.compare_report(a,b)
    def test_null_nonfinite_types_and_signs_refused(self):
        for value in [None,True,4700,float('nan'),float('inf'),0.0,-4700.0]:
            with self.assertRaises(ValueError):subject.compare_report({'rows':[{'length_km':4700.0}]},{'rows':[{'length_km':value}]})
    def test_exact_unchanged_nulls_pass(self):
        self.assertEqual(subject.compare_report({'rows':[{'length_km':None}]},{'rows':[{'length_km':None}]}),[])
    def test_all_declared_length_locations(self):
        a=self.report();b=copy.deepcopy(a);b['rows'][0]['resolution_scenarios'][0]['length_km']+=1e-12;b['cases'][0]['nominal_grid_length_km']+=1e-12;b['cases'][0]['computed_method_resolution_span_km'][0]+=1e-12
        self.assertEqual(len(subject.compare_report(a,b)),3)
    def svg(self,d='M100.00,200.00 L101.00,201.00',text='Scope',stroke='blue'):
        return f'<svg xmlns="http://www.w3.org/2000/svg"><text>{text}</text><path d="{d}" fill="none" stroke="{stroke}" stroke-width="2.5"/></svg>'
    def test_only_last_display_decimal_can_differ(self):
        result=subject.compare_figure(self.svg(),self.svg('M100.01,200.00 L101.00,201.00'))
        self.assertEqual(len(result),1)
    def test_svg_large_shift_text_style_commands_and_vertices_refused(self):
        for svg in [self.svg('M100.02,200.00 L101.00,201.00'),self.svg(text='Changed'),self.svg(stroke='red'),self.svg('M100.00,200.00 H101.00,201.00'),self.svg('M100.00,200.00')]:
            with self.assertRaises(ValueError):subject.compare_figure(self.svg(),svg)

if __name__=='__main__':unittest.main()
