import copy
import csv
import hashlib
import io
import json
import unittest
from collections import Counter
from datetime import datetime
import build_current_depth_register_v48 as d
from derive_eac_connected_layer_thickness_v1 import connected_layer


class GulfStreamDepthAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((d.ROOT/d.SOURCE).read_bytes())
        cls.data=d.build();cls.rows=cls.data['evidence'][491:]
        cls.old=json.loads((d.ROOT/cls.op['previous_register_file']).read_bytes())
        cls.chunks={f:json.loads((d.ROOT/f).read_bytes()) for f in cls.op['section_files']}

    def source(self,row):
        return self.chunks[row['source_profile_file']]['records'][int(row['source_profile_pointer'].split('/')[-1])]

    def test_previous491_and_all111_identities_preserved(self):
        self.assertEqual(self.data['evidence'][:491],self.old['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':701,'identities_with_scoped_depth_reference':101,'identities_not_yet_assessed':10,'whole_route_depth_profiles':0,'volume_estimates':0})
        for old,new in zip(self.old['records'],self.data['records']):
            if old['entity_id']!='current:gulf-stream':self.assertEqual(old,new)

    def test210_descriptors_share65_profiles(self):
        self.assertEqual(Counter(r['metric'] for r in self.rows),{'core_depth':65,'derived_supported_component_penetration_lower_bound':65,'derived_relative_core_component_decay_depth':65,'derived_fitted_locked_component_isotach_depth':15})
        self.assertEqual(len({r['source_case_id'] for r in self.rows}),65)
        self.assertEqual({r['source_section_id'] for r in self.rows},set(self.op['section_ids']))
        for section in self.op['section_ids']:
            self.assertEqual({tuple(r['calendar_months'] or []) for r in self.rows if r['source_section_id']==section},{()}|{(m,) for m in range(1,13)})

    def test_cores_use_upper200m_native_signed_component(self):
        for row in self.rows:
            if row['metric']!='core_depth':continue
            source=self.source(row);z=source['depth_levels_m'];v=source['selected_profile']['along_locked_mean_direction_m_s']
            eligible=[i for i in range(len(z)) if 10<=z[i]<=200 and v[i] is not None and v[i]>.05]
            seed=max(eligible,key=lambda i:v[i])
            self.assertEqual(row['approximate_value_m'],z[seed])
            self.assertEqual(row['source_sampled_core_at_shallowest_valid_level'],z[seed]==10)
            self.assertEqual(row['source_core_search_depth_interval_m'],[10,200])

    def test_half_core_and_absolute_crossings_rederive_from_raw_profiles(self):
        for row in self.rows:
            if row['metric'] not in ['derived_relative_core_component_decay_depth','derived_fitted_locked_component_isotach_depth']:continue
            source=self.source(row);z=source['depth_levels_m'];v=source['selected_profile']['along_locked_mean_direction_m_s']
            threshold=row['source_velocity_threshold_m_s']
            if row['metric']=='derived_relative_core_component_decay_depth':
                peak=max(value for dep,value in zip(z,v) if 10<=dep<=200 and value is not None and value>.05)
                self.assertEqual(threshold,.5*peak);self.assertEqual(row['source_relative_core_fraction'],.5)
            layer=connected_layer(z,v,threshold)
            self.assertEqual(layer['lower_depth_m'],row['source_computed_depth_before_display_rounding_m'])
            self.assertEqual(layer['lower_bracket_m'],row['source_native_bracketing_depths_m'])
            self.assertEqual(row['approximate_value_m'],int(10*round(layer['lower_depth_m']/10)))
            a,b=row['source_native_bracketing_depths_m'];self.assertEqual(z.index(b),z.index(a)+1)

    def test_censored_penetration_bounds_are_inclusive_not_bottoms(self):
        for row in self.rows:
            if row['metric']!='derived_supported_component_penetration_lower_bound':continue
            source=self.source(row);z=source['depth_levels_m'];v=source['selected_profile']['along_locked_mean_direction_m_s']
            layer=connected_layer(z,v,.05);self.assertIsNone(layer['lower_depth_m'])
            self.assertEqual(row['lower_bound_m'],layer['lower_last_connected_depth_m'])
            self.assertEqual(row['lower_bound_operator'],'>=');self.assertFalse(row['lower_bound_exclusive'])
            self.assertIsNone(row['approximate_value_m']);self.assertIsNone(row['lower_boundary_m'])
            index=z.index(row['lower_bound_m'])
            self.assertTrue(all(value is not None and value>.05 for value in v[layer['core_index']:index+1]))

    def test_locked_frame_source_positions_and_support_preserved(self):
        for row in self.rows:
            selected=self.source(row)['selected_profile']
            self.assertEqual(row['source_selected_lon_lat'],selected['source_lon_lat'])
            self.assertEqual(row['source_locked_reference_direction_at100m_degrees'],selected['locked_reference_direction_at100m_degrees'])
            self.assertEqual(set(selected['source_fit_support']),{'along_stream_scale','cross_stream_scale','downstream_direction','n_pts_fit','n_missions_fit','max_gap','arc_fit'})
            self.assertIn('locked_through_depth',row['source_velocity_quantity'])

    def test_raw_phases_are_not_observations_or_monthly_averages(self):
        for row in self.rows:
            source=self.source(row)
            self.assertEqual(row['source_actual_provider_phase_timestamp_utc'],source['actual_provider_phase_timestamp_utc'])
            self.assertFalse(row['source_phase_timestamp_is_observation_date']);self.assertFalse(row['source_is_monthly_average'])
            self.assertIsNone(row['observed_period']);self.assertIsNone(row['annual_range_m'])
            if row['calendar_months']:
                actual=datetime.fromisoformat(row['source_actual_provider_phase_timestamp_utc'].replace('Z','+00:00'))
                nominal=datetime.fromisoformat(row['source_nominal_phase_calendar_date']+'T00:00:00+00:00')
                self.assertLessEqual(abs((actual-nominal).total_seconds()),600)
                self.assertEqual(nominal.month,row['calendar_months'][0])

    def test_all_source_pointers_and_sha_pins_resolve(self):
        facts=json.loads((d.ROOT/self.op['section_facts_file']).read_bytes())
        for row in self.rows:
            context=self.data['source_contexts'][row['source_context_id']]
            self.assertIn('first_grid_tie',context['source_horizontal_axis_operator'])
            self.assertIn('2023-05-30',context['temporal_scope'])
            self.assertIn('02009-y',context['source_citation'])
            self.assertIn('not whole-current depth',context['qualification'])
            pointer=row['source_pointer'];self.assertTrue(pointer.startswith('/descriptors/'))
            source=facts['descriptors'][int(pointer.split('/')[-1])]
            self.assertEqual(source['source_file'],row['source_profile_file'])
            self.assertEqual(source['source_pointer'],row['source_profile_pointer'])
            self.assertEqual(source['source_sha256'],row['source_profile_sha256'])
        for f,pin in self.data['input_sha256'].items():self.assertEqual(d.digest(d.ROOT/f),pin)

    def test_mutations_reject_metric_identity_frame_phase_and_promotions(self):
        expected={r['id']:r for r in self.rows}
        for row in self.rows:
            d.validate_context(row,expected)
            for key,value in [('entity_id','current:florida'),('source_core_search_depth_interval_m',[0,1000]),('source_locked_reference_direction_at100m_degrees',999),('source_velocity_threshold_m_s',99),('volume_eligible',True),('lower_bound_operator','>'),('source_phase_timestamp_is_observation_date',True)]:
                changed=copy.deepcopy(row);changed[key]=value
                with self.subTest(key=key),self.assertRaises(ValueError):d.validate_context(changed,expected)

    def test_no_width_join_physical_thickness_volume_or_system_inheritance(self):
        for row in self.rows:
            self.assertEqual(row['entity_id'],'current:gulf-stream')
            for key in ['upper_boundary_m','lower_boundary_m','thickness_m','uncertainty_m','same_source_width_reference_id']:self.assertIsNone(row[key])
            for key in ['volume_eligible','whole_current_representative','physical_state_join_eligible','independent_observation_count_claimed','annual_extrema_eligible','reference_route_projection_eligible','source_product_limit_is_current_bottom','source_component_uncertainty_is_depth_error']:self.assertFalse(row[key])

    def test_json_serialization_and_previous_csv_cells_and_new_fields(self):
        raw=d.json_bytes(self.data);self.assertLess(len(raw),2500000);self.assertEqual(json.loads(raw),self.data)
        old=list(csv.DictReader(io.StringIO((d.ROOT/self.op['previous_csv_file']).read_text(encoding='utf8'))))
        new=list(csv.DictReader(io.StringIO(d.csv_bytes(self.data).decode('utf8'))))
        self.assertEqual(len(new),701)
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})
        for row in new[491:]:
            self.assertTrue(row['source_locked_reference_direction_at100m_degrees'])
            self.assertEqual(row['source_core_search_depth_interval_m'],'[10,200]')

    def test_member_lookup_refreshes_all_owned_refs_without_parent_numbers(self):
        raw=d.json_bytes(self.data);index=d.member_index(self.data,raw)
        self.assertEqual(index['depth_register_sha256'],hashlib.sha256(raw).hexdigest())
        owners={r['entity_id']:r['depth_reference_ids'] for r in self.data['records']};union=set()
        for row in index['records']:
            linked=set()
            for member in row['members']:
                self.assertEqual(member['depth_reference_ids'],owners[member['entity_id']]);linked.update(member['depth_reference_ids'])
            self.assertEqual(row['unique_linked_reference_ids'],sorted(linked));union.update(linked)
            for key in ['parent_depth_m','parent_depth_range_m','parent_volume_km3','aggregation_operator']:self.assertIsNone(row[key])
        self.assertEqual(index['counts']['distinct_member_depth_references'],len(union))


if __name__=='__main__':unittest.main()
