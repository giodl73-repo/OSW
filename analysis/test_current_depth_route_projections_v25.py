import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v25 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate
from interval_depth_diagnostic_v1 import INTERIOR


class WSCIntervalReanalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.op=json.loads((p.ROOT/p.OPERATOR).read_bytes())
        cls.manifest,cls.addendum,cls.pieces,cls.view,cls.report=p.build()
        cls.previous_manifest=json.loads((p.ROOT/cls.op['previous_inventory_file']).read_bytes())
        cls.previous=loader.load_inventory(cls.previous_manifest,lambda f:(p.ROOT/f).read_bytes())
        cls.chunks={f:json.loads((p.ROOT/f).read_bytes()) for f in cls.op['section_files']}
        cls.oldop=json.loads((p.ROOT/cls.op['source_operator_file']).read_bytes())
        cls.cases=cls.addendum['projections']+cls.addendum['unresolved_reference_cases']

    def reader(self,f):return self.pieces[f] if f in self.pieces else (p.ROOT/f).read_bytes()

    def test_all84_previous_cases_csv_cells_and_ownership_lists_preserved(self):
        self.assertEqual(self.view['projections'][:84],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:3],self.previous['unresolved_reference_cases'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        old=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.previous_manifest,lambda f:(p.ROOT/f).read_bytes()).decode())))
        new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})

    def test_all16_source_sections_and_two_original_dates_retained(self):
        self.assertEqual(len(self.report['sections']),16);self.assertEqual(len(self.cases),2)
        self.assertEqual(sum(len(c['anchors']) for c in self.cases),16)
        self.assertEqual({c['snapshot_time_utc'] for c in self.cases},set(self.op['snapshot_times_utc']))
        self.assertEqual(self.report['new_provider_field_reads'],0);self.assertEqual(self.report['new_independent_observations'],0)
        for c in self.cases:
            self.assertEqual([a['source_section_id'] for a in c['anchors']],[s['id'] for s in self.op['sections']])

    def test_raw_profile_and_derived_layer_pointers_have_distinct_correct_targets(self):
        for c in self.cases:
            for a in c['anchors']:
                ref,index=a['source_profile_refs'][0].split('#/sections/');self.assertEqual(ref,p.REPORT)
                row=self.report['sections'][int(index)];selected=row['diagnosis']['selected_column_index']
                if selected is None:
                    self.assertIsNone(a['source_model_profile_ref']);self.assertIsNone(a['source_connected_diagnosis_ref'])
                    self.assertTrue(a['reference_geometry_is_unselected_gate_midpoint']);continue
                self.assertEqual(a['source_model_profile_ref'],row['source_file']+'#/columns/'+str(selected))
                self.assertEqual(a['reference_lon_lat'],self.chunks[row['source_file']]['columns'][selected]['sampled_lon_lat'])
                layer=next(l for l in row['diagnosis']['selected_column_threshold_layers'] if l['threshold_m_s']==.1)
                self.assertEqual(a['source_model_connected_layer'],layer)
                self.assertEqual(a['model_upper_depth_m'],layer['upper_depth_m']);self.assertEqual(a['model_lower_depth_m'],layer['lower_depth_m'])
                self.assertTrue(a['source_connected_diagnosis_ref'].startswith(p.REPORT+'#/sections/'+index+'/diagnosis/'))
                self.assertEqual(a['original_surface_selected_column_index'],self.chunks[row['source_file']]['diagnosis']['selected_column_index'])

    def test_primary_censoring_and_original_adjacency_preserve_every_gap(self):
        for c in self.cases:
            for a in c['anchors']:
                self.assertEqual(a['lower_projection_eligible'],a['source_horizontal_selection_status']==INTERIOR and a['model_lower_depth_m'] is not None)
                if a['model_upper_depth_m'] is None:self.assertFalse(a['layer_projection_eligible'])
            for a,b,s in zip(c['anchors'],c['anchors'][1:],c['segments']):
                values,used,status=interpolate(c['anchors'],(a['distance_km']+b['distance_km'])/2)
                self.assertEqual(used,[a,b])
                if not(a['lower_projection_eligible'] and b['lower_projection_eligible']):
                    self.assertIsNone(values['model_lower_depth_m']);self.assertEqual(s['projection_status'],'gap_no_projection')

    def test_changed_derived_selection_layers_provenance_and_missing_rows_rejected(self):
        for field,value in [('source_sha256','invented'),('original_surface_selected_column_index',9999)]:
            report=copy.deepcopy(self.report);report['sections'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):p.cases_from_report(report,self.chunks,self.oldop,self.op)
        report=copy.deepcopy(self.report);report['sections'][0]['diagnosis']['selected_column_index']=9999
        with self.assertRaises(ValueError):p.cases_from_report(report,self.chunks,self.oldop,self.op)
        report=copy.deepcopy(self.report);report['sections'].pop()
        with self.assertRaises(ValueError):p.cases_from_report(report,self.chunks,self.oldop,self.op)

    def test_original_source_frame_geometry_and_interval_tuning_rejected(self):
        file=next(iter(self.chunks))
        for field,value in [('component_bearing_degrees_true',180),('operator_sha256','invented')]:
            chunks=copy.deepcopy(self.chunks);chunks[file][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):p.derive_report(chunks,self.oldop,self.op)
        op=copy.deepcopy(self.op);op['sections'][0]['longitude_gate_degrees_east'][0]-=1
        with self.assertRaises(ValueError):p.derive_report(self.chunks,self.oldop,op)
        op=copy.deepcopy(self.op);op['selection_depth_interval_m']=[20,400]
        with self.assertRaises(ValueError):p.derive_report(self.chunks,self.oldop,op)

    def test_distinct_method_ids_no_surface_equivalence_or_physical_promotion(self):
        oldids={c['id'] for c in self.previous['projections']}
        for c in self.cases:
            self.assertNotIn(c['id'],oldids);self.assertEqual(c['comparison_group'],'model_interval20_500_no_surface_gate')
            self.assertIsNone(c['source_surface_component_gate_m_s']);self.assertEqual(c['core_search_depth_interval_m'],[20,500])
            self.assertFalse(c['original_surface_cases_replaced']);self.assertFalse(c['model_products_are_statistically_independent'])
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m'])
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],40)
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)

    def test_all_piece_input_pins_counts_and_fixed_byte_caps(self):
        self.assertEqual(self.manifest['base'],self.previous_manifest['base']);self.assertEqual(self.manifest['addenda'][:10],self.previous_manifest['addenda'])
        report=self.addendum['derived_source_report'];self.assertEqual(report['sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest())
        self.assertEqual(report['bytes'],len(self.pieces[p.REPORT]))
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),2400000)
        with self.assertRaises(ValueError):loader.load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        manifest=copy.deepcopy(self.manifest);manifest['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(manifest,self.reader)


if __name__=='__main__':unittest.main()
