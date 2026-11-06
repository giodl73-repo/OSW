import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v14 as p


class SupportedAndBlockedDepthCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes());cls.data=p.build()
        cls.new=cls.data['projections'][35:]+cls.data['unresolved_reference_cases']
        cls.sources={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['current_source_files']}

    def test_previous35_objects_and_canonical_owned_refs_preserved(self):
        old=json.loads((p.ROOT/self.op['previous_projection_file']).read_bytes())
        self.assertEqual(self.data['projections'][:35],old['projections'])
        register=json.loads((p.ROOT/self.op['depth_register_file']).read_bytes())
        self.assertEqual({r['entity_id']:r['depth_reference_ids'] for r in self.data['records']},{r['entity_id']:r['depth_reference_ids'] for r in register['records']})

    def test_all_six_cases44_anchors38_original_segments_retained(self):
        self.assertEqual(len(self.new),6);self.assertEqual(len({r['id'] for r in self.new}),6)
        self.assertEqual(sum(len(r['anchors']) for r in self.new),44)
        self.assertEqual(sum(len(r['segments']) for r in self.new),38)
        self.assertEqual(self.data['counts']['new_supported_model_scenarios']+self.data['counts']['new_blocked_model_reference_cases'],6)
        self.assertEqual(self.data['counts']['new_conditional_adjacent_segments']+self.data['counts']['new_gap_segments'],38)

    def test_fully_blocked_north_brazil_does_not_inflate_projection_coverage(self):
        self.assertFalse(any(r['entity_id']=='current:north-brazil' for r in self.data['projections']))
        blocked=[r for r in self.data['unresolved_reference_cases'] if r['entity_id']=='current:north-brazil']
        self.assertEqual(len(blocked),2)
        row=next(r for r in self.data['records'] if r['entity_id']=='current:north-brazil')
        self.assertEqual(row['projection_ids'],[]);self.assertEqual(set(row['unresolved_reference_case_ids']),{r['id'] for r in blocked})
        self.assertEqual(row['projection_status'],'reference_cases_blocked_no_supported_projection')
        for case in blocked:
            self.assertTrue(all(not a['lower_projection_eligible'] for a in case['anchors']))
            self.assertTrue(all(s['computed_model_lower_depth_m'] is None for s in case['samples']))

    def test_supported_and_unresolved_collections_are_disjoint_and_correctly_counted(self):
        supported={r['id'] for r in self.data['projections']};blocked={r['id'] for r in self.data['unresolved_reference_cases']}
        self.assertFalse(supported&blocked)
        for r in self.data['projections'][35:]:self.assertTrue(any(a['lower_projection_eligible'] for a in r['anchors']))
        for r in self.data['unresolved_reference_cases']:self.assertFalse(any(a['lower_projection_eligible'] for a in r['anchors']))
        counts=self.data['counts'];records=self.data['records']
        self.assertEqual(counts['regional_projection_scenarios'],len(supported))
        self.assertEqual(counts['unresolved_regional_reference_cases'],len(blocked))
        self.assertEqual(counts['identities_with_regional_projection_scenarios'],sum(bool(r['projection_ids']) for r in records))
        self.assertEqual(counts['identities_not_yet_projected']+counts['identities_with_regional_projection_scenarios'],111)
        self.assertEqual(counts['identities_with_only_blocked_reference_cases']+counts['identities_without_any_regional_reference_case'],counts['identities_not_yet_projected'])

    def test_source_values_statuses_frames_and_offsets_remain_exact(self):
        for case in self.new:
            for a in case['anchors']:
                file,pointer=a['source_profile_refs'][0].split('#');r=self.sources[file]['samples'][int(pointer.split('/')[-1])]
                self.assertEqual(a['model_lower_depth_m'],r['primary_core_lower_descriptor']['lower_isotach_depth_m'])
                self.assertEqual(a['source_component_bearing_degrees_true'],r['locked_reference_bearing_degrees_true'])
                self.assertEqual(a['reference_lon_lat'],r['editorial_lon_lat']);self.assertEqual(a['distance_km'],r['reference_distance_km'])
                expected=r['horizontal_selection_status']=='interior_sampled_maximum_not_independently_validated_axis' and r['primary_core_lower_descriptor']['lower_isotach_depth_m'] is not None
                self.assertEqual(a['lower_projection_eligible'],expected)

    def test_no_primary_threshold_or_date_pooling_and_no_physical_promotion(self):
        for case in self.new:
            self.assertIn(case['snapshot_time_utc'],self.op['snapshot_times_utc'])
            self.assertEqual(case['primary_threshold_m_s'],.1 if case['entity_id']=='current:north-brazil' else .05)
            self.assertFalse(any(case['eligibility'].values()));self.assertIsNone(case['physical_thickness_m']);self.assertIsNone(case['annual_range_m'])
            for sample in case['samples']:
                self.assertIsNone(sample['physical_thickness_m']);self.assertFalse(sample['volume_eligible'])

    def test_classification_rejects_fabricated_value_on_fully_blocked_case(self):
        case=copy.deepcopy(self.data['unresolved_reference_cases'][0]);case['samples'][0]['computed_model_lower_depth_m']=1
        with self.assertRaises(ValueError):p.classify(case)

    def test_projection_csv_keeps_all_old_cells_and_excludes_blocked_cases(self):
        old=list(csv.DictReader(io.StringIO((p.ROOT/self.op['previous_projection_csv']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(p.csv_bytes(self.data).decode('utf8'))))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        blocked={r['id'] for r in self.data['unresolved_reference_cases']}
        self.assertFalse(any(r['projection_id'] in blocked for r in new))
        self.assertEqual(len(new)-len(old),sum(len(r['samples']) for r in self.data['projections'][35:]))

    def test_unresolved_csv_retains_raw_source_depth_but_no_projected_value(self):
        rows=list(csv.DictReader(io.StringIO(p.unresolved_csv_bytes(self.data).decode('utf8'))))
        self.assertEqual(len(rows),sum(len(r['anchors']) for r in self.data['unresolved_reference_cases']))
        self.assertTrue(any(r['source_model_lower_depth_m']!='' for r in rows))
        for row in rows:
            self.assertEqual(row['projected_depth_descriptor_m'],'');self.assertEqual(row['volume_eligible'],'False')
            self.assertTrue(json.loads(row['projection_block_reasons']));self.assertTrue(json.loads(row['source_profile_refs']))

    def test_all_inputs_pinned_and_outputs_fit_fixed_publication_cap(self):
        for file,pin in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/file).read_bytes()).hexdigest(),pin)
        self.assertLess(len((json.dumps(self.data,indent=2,allow_nan=False)+'\n').encode('utf8')),2500000)
        self.assertLess(len(p.csv_bytes(self.data)),2500000)


if __name__=='__main__':unittest.main()
