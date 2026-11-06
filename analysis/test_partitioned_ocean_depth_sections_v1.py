import copy
import json
from pathlib import Path
import unittest
import numpy as np
import acquire_zonal_current_depth_sections_v1 as geometry
from current_depth_search_partitions_v1 import validate_partitions,validate_section_partition


class PartitionedOceanDepthSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((Path(__file__).resolve().parents[1]/'research/partitioned-ocean-depth-sections-operator-v1.json').read_bytes())

    def test_four_partitions_keep_two_canonical_owners_and_sixteen_sections(self):
        groups=validate_partitions(self.op)
        self.assertEqual(set(self.op['currents']),{'current:south-atlantic','current:tasman-front'})
        self.assertEqual(len(groups),4);self.assertEqual(len(self.op['sections']),16)
        self.assertTrue(all(len(items)==4 for items in groups.values()))
        for entity in self.op['currents']:self.assertEqual(sum(p['entity_id']==entity for p in self.op['search_partitions'].values()),2)

    def test_all64_native_targets_preflight_before_fields_under_original_caps(self):
        plans,pairs=geometry.preflight(np.arange(-80,80.001,.04),np.arange(0,360,.08),self.op)
        self.assertEqual(len(plans),16);self.assertEqual(pairs,4*sum(40*len(p['latitude_indices']) for p in plans))
        self.assertLess(pairs,250000);self.assertLess(pairs*16,7000000)
        self.assertEqual(self.op['snapshot_times_utc'],['2022-03-15T00:00:00Z','2022-06-15T00:00:00Z','2022-09-15T00:00:00Z','2022-12-15T00:00:00Z'])
        self.assertEqual(self.op['maximum_component_read_attempts'],3)

    def test_exact_corridors_longitudes_windows_frames_and_primary_cutoffs(self):
        expected={'sac-northern-search':('current:south-atlantic',[-37,-33],[-13,-9,-5,-1]),
            'sac-southern-search':('current:south-atlantic',[-41,-37],[-13,-9,-5,-1]),
            'tasman-north-bank-search':('current:tasman-front',[-31.8,-29.5],[167,167.5,168,168.5]),
            'tasman-south-bank-search':('current:tasman-front',[-34,-31.8],[167,167.5,168,168.5])}
        groups=validate_partitions(self.op);self.assertEqual(set(groups),set(expected))
        for key,(entity,gate,longitudes) in expected.items():
            p=self.op['search_partitions'][key];self.assertEqual(p['entity_id'],entity);self.assertEqual(p['latitude_gate_degrees_north'],gate)
            self.assertEqual([s['longitude_degrees_east'] for s in groups[key]],longitudes)
        for entity,c in self.op['currents'].items():
            self.assertEqual(c['core_search_depth_interval_m'],[0,200]);self.assertEqual(c['selection_depth_interval_m'],[0,200])
            self.assertEqual(c['component_bearing_degrees_true'],90);self.assertIsNone(c['surface_component_gate_m_s']);self.assertIsNone(c['temperature_gate'])
            self.assertEqual(c['primary_threshold_m_s'],.05 if entity=='current:south-atlantic' else .1)
        self.assertFalse(any(self.op['eligibility'].values()));self.assertEqual(self.op['maximum_total_temperature_scalars'],0)

    def test_one_shared_boundary_is_allowed_but_positive_width_overlap_rejected(self):
        validate_partitions(self.op);bad=copy.deepcopy(self.op)
        bad['search_partitions']['sac-southern-search']['latitude_gate_degrees_north'][-1]=-36.9
        for s in bad['sections']:
            if s['search_partition_id']=='sac-southern-search':s['latitude_gate_degrees_north'][-1]=-36.9
        with self.assertRaises(ValueError):validate_partitions(bad)

    def test_unknown_partition_owner_duplicate_and_missing_section_rejected(self):
        for field,value in [('search_partition_id','invented'),('entity_id','current:tasman-front'),('latitude_gate_degrees_north',[-36,-33])]:
            bad=copy.deepcopy(self.op);bad['sections'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_partitions(bad)
        bad=copy.deepcopy(self.op);bad['sections'].append(copy.deepcopy(bad['sections'][0]))
        with self.assertRaises(ValueError):validate_partitions(bad)
        bad=copy.deepcopy(self.op);bad['sections']=[s for s in bad['sections'] if s['search_partition_id']!='sac-northern-search']
        with self.assertRaises(ValueError):validate_partitions(bad)

    def test_longitude_order_and_paired_partition_geometry_mutations_rejected(self):
        bad=copy.deepcopy(self.op);bad['sections'][1]['longitude_degrees_east']=bad['sections'][0]['longitude_degrees_east']
        with self.assertRaises(ValueError):validate_partitions(bad)
        bad=copy.deepcopy(self.op);bad['sections'][0]['longitude_degrees_east']=-14
        with self.assertRaises(ValueError):validate_partitions(bad)

    def test_front_identity_interpolation_or_owner_promotion_rejected(self):
        for field in ['front_or_water_mass_classification_performed','persistent_jet_identity_validated','cross_partition_interpolation_permitted','canonical_current_ownership_changed']:
            bad=copy.deepcopy(self.op);bad['search_partitions']['sac-northern-search'][field]=True
            with self.subTest(field=field),self.assertRaises(ValueError):validate_partitions(bad)

    def test_retained_membership_requires_exact_declared_section_and_semantics(self):
        definition=self.op['sections'][0];key=definition['search_partition_id']
        source={'entity_id':definition['entity_id'],'search_partition_id':key,'section_definition':copy.deepcopy(definition),
            'search_partition_kind':'editorial_latitude_search_context','front_or_water_mass_classification_performed':False}
        self.assertEqual(validate_section_partition(source,self.op),key)
        for field,value in [('search_partition_id','sac-southern-search'),('entity_id','current:tasman-front'),('front_or_water_mass_classification_performed',True)]:
            bad=copy.deepcopy(source);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_section_partition(bad,self.op)
        bad=copy.deepcopy(source);bad['section_definition']['latitude_gate_degrees_north'][0]-=.1
        with self.assertRaises(ValueError):validate_section_partition(bad,self.op)


if __name__=='__main__':unittest.main()
