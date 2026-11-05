import copy,csv,io,json,math,socket,unittest
from pathlib import Path
from unittest.mock import patch
import gsw
import project_current_native_pressure_depths_v1 as projection
ROOT=Path(__file__).resolve().parents[1]
read=lambda f:json.loads((ROOT/f).read_bytes())

class NativePressureProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=projection.build();cls.rows=[r['native_reference'] for r in cls.report['records']]
        cls.benguela=read(projection.BENGUELA);cls.rim=read(projection.RIM);cls.policy=read(projection.CANARY)

    def test_official_75term_examples_sign_and_inverse(self):
        for pressure,expected in [(10,9.9445834469453),(50,49.7180897012550),(125,124.2726219409978),(250,248.4700576548589),(600,595.8253480356214),(1000,992.0919060719987)]:
            depth,back=projection.convert(pressure,4)
            self.assertAlmostEqual(depth,expected,places=8);self.assertAlmostEqual(back,pressure,places=7)
        self.assertEqual(projection.convert(0,-34.5),(0.0,0.0))

    def test_benguela_is_linked_companion_preserving_scope_and_native_units(self):
        rows=projection.project(self.rows,self.benguela,self.rim,self.policy);r=next(r for r in rows if r['native_reference_id']==projection.BENGUELA_ID)
        self.assertEqual(r['source_pressure_dbar'],1270);self.assertEqual(r['conversion_latitude_degrees_north'],-34.5)
        self.assertEqual(r['source_observational_months'],['2013-09','2015-07']);self.assertEqual(r['source_methods'],self.benguela['methods'])
        self.assertNotEqual(r['computed_reference_depth_m'],1270);self.assertLess(r['computed_reference_depth_m'],1270)
        self.assertAlmostEqual(float(gsw.p_from_z(-r['computed_reference_depth_m'],-34.5,0,0)),1270,places=5)
        self.assertEqual(r['display_approximate_reference_depth_m']%10,0)
        self.assertEqual(r['native_reference']['unit'],'dbar');self.assertIsNone(r['native_reference']['approximate_value_m'])
        self.assertEqual(self.report['counts'],{'native_pressure_reference_outcomes':2,'converted_reference_companions':1,'unresolved_reference_companions':1,'new_native_measurements':0,'new_inventory_references':0})

    def test_rim_unknown_latitude_datum_and_censor_never_become_depth(self):
        r=next(r for r in self.report['records'] if r['native_reference_id']==projection.RIM_ID)
        self.assertEqual(r['source_pressure_dbar'],350);self.assertTrue(r['sampling_limit_censors_unknown_flow_bottom'])
        for k in ['conversion_latitude_degrees_north','computed_reference_depth_m','display_approximate_reference_depth_m','roundtrip_sea_pressure_dbar','atmospheric_pressure_subtracted_dbar']:self.assertIsNone(r[k])
        for k,v in [('assumed_latitude_degrees_north',43),('pressure_datum_independently_verified',True)]:
            facts=copy.deepcopy(self.rim);facts[k]=v
            with self.assertRaises(ValueError):projection.project(self.rows,self.benguela,facts,self.policy)

    def test_missing_invalid_absolute_pressure_and_unreviewed_corrections_rejected(self):
        for pressure,latitude in [(float('nan'),4),(350,float('nan')),(-1,4),(350,None),(350,91),(True,4),(350,False),(float('inf'),4)]:
            with self.assertRaises(ValueError):projection.convert(pressure,latitude)
        for kwargs in [{'unit':'Pa'},{'unit':'m'},{'pressure_kind':'absolute_pressure'},{'dynamic_height':10},{'sea_surface_geopotential':10}]:
            with self.assertRaises(ValueError):projection.convert(1270,-34.5,**kwargs)

    def test_frozen_canary_policy_is_shared_without_mutating_native_sources(self):
        before=copy.deepcopy((self.rows,self.benguela,self.rim,self.policy))
        projection.project(self.rows,self.benguela,self.rim,self.policy)
        self.assertEqual((self.rows,self.benguela,self.rim,self.policy),before)
        for k,v in [('gsw_version','unreviewed'),('assumed_dynamic_height_m2_s2',1),('assumed_sea_surface_geopotential_m2_s2',1),('display_rounding_m',1)]:
            op=copy.deepcopy(self.policy);op[k]=v
            with self.assertRaises(ValueError):projection.project(self.rows,self.benguela,self.rim,op)

    def test_no_omission_duplicate_metric_relabel_or_physical_promotion(self):
        for incoming in [self.rows[:1],self.rows+[self.rows[0]]]:
            with self.assertRaises(ValueError):projection.project(incoming,self.benguela,self.rim,self.policy)
        for k,v in [('unit','m'),('approximate_value_m',1270),('volume_eligible',True),('physical_current_bottom_established',True)]:
            rows=copy.deepcopy(self.rows);rows[0][k]=v
            with self.assertRaises(ValueError):projection.project(rows,self.benguela,self.rim,self.policy)
        for r in self.report['records']:
            for k in projection.FLAGS:self.assertFalse(r[k])
            for k in ['physical_depth_uncertainty_m','annual_depth_range_m','physical_thickness_m','whole_current_depth_m']:self.assertIsNone(r[k])
            self.assertFalse(r['new_reference_inventory_row']);self.assertFalse(r['new_measurement'])

    def test_build_is_network_free_and_retains_native_inventory_counts(self):
        def denied(*a,**k):raise RuntimeError('Network forbidden')
        with patch.object(socket,'create_connection',denied),patch.object(socket,'socket',denied):self.assertEqual(projection.build(),self.report)
        self.assertEqual(self.report['reference_inventory_counts_unchanged']['depth_references'],859)
        self.assertEqual(self.report['native_coordinate_unit_counts_unchanged'],{'dbar':2,'m':857})
        table=list(csv.DictReader(io.StringIO(projection.csv_bytes(self.report['records']).decode())))
        self.assertEqual(len(table),2);rim=next(r for r in table if r['native_reference_id']==projection.RIM_ID)
        self.assertEqual(rim['computed_reference_depth_m'],'');self.assertEqual(rim['display_approximate_reference_depth_m'],'')

if __name__=='__main__':unittest.main()
