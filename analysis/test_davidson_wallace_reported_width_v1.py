"""Synthetic dimensional/scope checks; never execute the actual source case."""
import copy
from decimal import localcontext
from fractions import Fraction
import importlib.util
import json
import subprocess
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('davidson_wallace_reported_width_v1', Path(__file__).with_name('davidson_wallace_reported_width_v1.py'))
method = importlib.util.module_from_spec(spec)
spec.loader.exec_module(method)


def fixture():
    return {
        'schema': 'osw.reported-regional-transect-width-facts.v1',
        'current_id': 'davidson', 'source_type': 'course_cruise_report',
        'peer_review_verified': False, 'publication_date': None,
        'source_url':method.SOURCE_URL,'source_citation':'Synthetic test source metadata',
        **{key: None for key in method.NULL_FIELDS},
        'state_join_eligible': False, 'physical_playback_eligible': False,
        'canonical_admission_verified': False,
        'prospective_unit_convention': {'international_nautical_mile_m':1852,
                                       'exact_conversion_implies_exact_measurement':False},
        'reported_statements': [{
            'source_value': 7, 'source_unit': 'nautical_mile', 'source_unit_label':'NM', 'approximate': True,
            'quantity_type': 'author_reported_regional_poleward_flow_transect_width',
            'depth_support': 'depth_averaged_interval', 'depth_interval_m': [27,59],
            'campaign_window': ['2008-01-23','2008-01-30'],
            'exact_occupation_date': None, 'paired_edge_coordinates': None,
            'numeric_velocity_cutoff': None, 'uncertainty_nm': None,
            'transect_normal_to_flow_verified': False,
            'independent_raw_values_reproduced': False,
            'canonical_width_admitted': False,
            'conversion_executed':False,'converted_width_km_decimal':None,
            'source_locator': 'synthetic passage', 'region': 'synthetic region',
        }],
    }


class SyntheticChecks(unittest.TestCase):
    def test_conversion_matches_independent_integer_rational(self):
        for value in [1,7,19,83]:
            actual = method.nautical_miles_to_km(value)
            self.assertEqual(Fraction(actual), Fraction(value*1852,1000))

    def test_conversion_and_diagram_do_not_depend_on_caller_decimal_precision(self):
        reference=method.products(fixture())
        with localcontext() as context:
            context.prec=2
            self.assertEqual(method.products(fixture()),reference)

    def test_invalid_numbers_are_not_dimensions(self):
        for value in [True,False,0,-1,1001,1.5,'NaN','Infinity','-Infinity','bad']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                method.nautical_miles_to_km(value)

    def test_all_annual_geographic_and_admission_promotions_reject(self):
        for field in method.NULL_FIELDS:
            case=fixture();case[field]=[1,2]
            with self.subTest(field=field), self.assertRaises(ValueError):method.validate(case)
        for field in ['state_join_eligible','physical_playback_eligible','canonical_admission_verified','peer_review_verified']:
            case=fixture();case[field]=True
            with self.subTest(field=field), self.assertRaises(ValueError):method.validate(case)

    def test_source_scope_cannot_gain_dates_edges_precision_or_layers(self):
        changes={'exact_occupation_date':'2008-01-30','uncertainty_nm':0,
                 'paired_edge_coordinates':[[0,0],[1,1]],'numeric_velocity_cutoff':0,
                 'depth_interval_m':[0,125],'depth_support':'point_depth',
                 'source_unit':'statute_mile','source_unit_label':'mi','approximate':False,
                 'transect_normal_to_flow_verified':True,'independent_raw_values_reproduced':True,
                 'canonical_width_admitted':True}
        for field,value in changes.items():
            case=fixture();case['reported_statements'][0][field]=value
            with self.subTest(field=field), self.assertRaises(ValueError):method.validate(case)
        case=fixture();case['reported_statements']*=2
        with self.assertRaises(ValueError):method.validate(case)

    def test_reproducible_products_preserve_source_value_and_unknowns(self):
        case=fixture();before=copy.deepcopy(case)
        report,svg=method.products(case)
        self.assertEqual(case,before)
        self.assertEqual((report,svg),method.products(case))
        value=json.loads(report);row=value['reported_statements'][0]
        self.assertEqual(row['source_value'],7)
        self.assertEqual(row['converted_width_km_decimal'],'12.964')
        self.assertEqual(value['display_label'],'About 13 km')
        self.assertIsNone(row['uncertainty_nm'])
        self.assertIsNone(row['exact_occupation_date'])
        tree=ET.fromstring(svg)
        self.assertEqual(tree.get('role'),'img')
        self.assertIn('exact occupation date unknown',svg.decode().lower())
        self.assertIn('flow-normal orientation not verified',svg.decode().lower())
        self.assertEqual(len(tree.findall('{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}circle')),1)
        case=fixture();case['reported_statements'][0]['source_value']=83
        with self.assertRaises(ValueError):method.products(case)

    def test_extra_dimension_fields_cannot_evade_scope_checks(self):
        for field in ['annual_width_min_km','annual_width_max_km','width_boundary_polygon']:
            for target in ['top','row']:
                case=fixture();container=case if target=='top' else case['reported_statements'][0]
                container[field]=12
                with self.subTest(field=field,target=target),self.assertRaises(ValueError):method.validate(case)

    def test_conversion_metadata_cannot_misstate_factor_or_precision(self):
        for field,value in [('international_nautical_mile_m',1609),('exact_conversion_implies_exact_measurement',True)]:
            case=fixture();case['prospective_unit_convention'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):method.validate(case)
        for field,value in [('conversion_executed',True),('converted_width_km_decimal','17')]:
            case=fixture();case['reported_statements'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):method.validate(case)

    def test_unfrozen_or_incomplete_dependencies_stop_before_source_execution(self):
        with TemporaryDirectory() as folder:
            root=Path(folder);path=root/'preflight.json'
            for preflight in [{}, {'schema':'osw.reported-regional-transect-width-preflight.v1','dependencies':{}}]:
                path.write_text(json.dumps(preflight),encoding='utf-8')
                with self.assertRaises(ValueError):method.inspect_frozen_inputs(root,'preflight.json')

    def test_changed_or_escaped_dependency_stops_before_source_execution(self):
        names=['producer','tests','protocol','facts','acquisition','unit_definition','width_rules','prose_rules','source_review','environment','role_review']
        with TemporaryDirectory() as folder:
            root=Path(folder);path=root/'preflight.json'
            (root/'dummy').write_bytes(b'synthetic')
            for relative in ['dummy','../outside']:
                preflight={'schema':'osw.reported-regional-transect-width-preflight.v1',
                           'dependencies':{name:{'path':relative,'bytes':9,'sha256':'0'*64} for name in names}}
                path.write_text(json.dumps(preflight),encoding='utf-8')
                with self.subTest(relative=relative),self.assertRaises(ValueError):
                    method.inspect_frozen_inputs(root,'preflight.json')

    def test_frozen_method_must_match_committed_bytes(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            git=['git','-c','core.autocrlf=false','-c','core.fsmonitor=false',
                 '-c','maintenance.auto=0','-c','gc.auto=0']
            def run(*args):
                return subprocess.run(git+list(args),cwd=root,capture_output=True,check=True)
            run('init','--quiet')
            (root/'producer.py').write_bytes(b'# synthetic method\n')
            preflight={'dependencies':{'producer':{'path':'producer.py'}}}
            (root/'preflight.json').write_bytes(json.dumps(preflight).encode())
            run('add','producer.py','preflight.json')
            run('-c','user.name=Synthetic test','-c','user.email=test@example.invalid',
                'commit','--quiet','-m','Freeze synthetic fixture')
            self.assertEqual(method.verify_git_freeze(root,'preflight.json'),run('rev-parse','HEAD').stdout.decode().strip())
            (root/'producer.py').write_bytes(b'# changed synthetic method\n')
            with self.assertRaises(ValueError):method.verify_git_freeze(root,'preflight.json')


if __name__=='__main__':unittest.main()
