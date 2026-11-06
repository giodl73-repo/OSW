import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v32 as p
import load_current_depth_projection_inventory_v1 as loader
from build_current_depth_route_projections_v12 import interpolate
from interval_depth_diagnostic_v1 import INTERIOR


class PacificSSCCIntervalReanalysisTests(unittest.TestCase):
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

    def test_all108_previous_cases_csv_cells_and_ownership_lists_preserved(self):
        self.assertEqual(self.view['projections'][:108],self.previous['projections'])
        self.assertEqual(self.view['unresolved_reference_cases'][:3],self.previous['unresolved_reference_cases'])
        self.assertEqual([(r['entity_id'],r['depth_reference_ids']) for r in self.view['records']],[(r['entity_id'],r['depth_reference_ids']) for r in self.previous['records']])
        old=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.previous_manifest,lambda f:(p.ROOT/f).read_bytes()).decode())))
        new=list(csv.DictReader(io.StringIO(loader.combined_csv_bytes(self.manifest,self.reader).decode())))
        for a,b in zip(old,new):self.assertEqual(a,{k:b[k] for k in a})

    def test_all6_source_sections_and_two_original_dates_retained(self):
        self.assertEqual(len(self.report['sections']),6);self.assertEqual(len(self.cases),2)
        self.assertEqual(sum(len(c['anchors']) for c in self.cases),6)
        self.assertEqual({c['snapshot_time_utc'] for c in self.cases},set(self.op['snapshot_times_utc']))
        self.assertEqual(self.report['new_provider_field_reads'],0);self.assertEqual(self.report['new_independent_observations'],0)
        for c in self.cases:
            self.assertEqual([a['source_section_id'] for a in c['anchors']],[s['id'] for s in self.op['sections']])

    def test_raw_profile_and_derived_layer_pointers_have_distinct_correct_targets(self):
        for c in self.cases:
            for a in c['anchors']:
                ref,index=a['source_profile_refs'][0].split('#/sections/');self.assertEqual(ref,p.REPORT)
                row=self.report['sections'][int(index)];selected=row['selected_source_column_index']
                if selected is None:
                    self.assertIsNone(a['source_model_profile_ref']);self.assertIsNone(a['source_connected_diagnosis_ref'])
                    self.assertTrue(a['reference_geometry_is_unselected_gate_midpoint']);self.assertEqual(a['reference_lon_lat'][1],-4.25);self.assertEqual(a['reference_lon_lat'][0],self.chunks[row['source_file']]['columns'][0]['sampled_lon_lat'][0]);continue
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
        op=copy.deepcopy(self.op);op['analysis_latitude_gate_degrees_north'][0]-=1
        with self.assertRaises(ValueError):p.derive_report(self.chunks,self.oldop,op)
        op=copy.deepcopy(self.op);op['selection_depth_interval_m']=[20,400]
        with self.assertRaises(ValueError):p.derive_report(self.chunks,self.oldop,op)

    def test_distinct_method_ids_no_surface_equivalence_or_physical_promotion(self):
        oldids={c['id'] for c in self.previous['projections']}
        for c in self.cases:
            self.assertNotIn(c['id'],oldids);self.assertEqual(c['comparison_group'],'model_primary_sscc_interval100_400_no_surface_gate')
            self.assertIsNone(c['source_surface_component_gate_m_s']);self.assertEqual(c['core_search_depth_interval_m'],[100,400])
            self.assertFalse(c['original_surface_cases_replaced']);self.assertFalse(c['model_products_are_statistically_independent'])
            self.assertFalse(any(c['eligibility'].values()));self.assertIsNone(c['physical_thickness_m']);self.assertIsNone(c['annual_range_m'])
        self.assertEqual(self.view['counts']['identities_with_regional_projection_scenarios'],51+int(bool(self.addendum['projections'])))
        self.assertEqual(self.view['counts']['whole_route_physical_depth_profiles'],0);self.assertEqual(self.view['counts']['volume_estimates'],0)

    def test_all_piece_input_pins_counts_and_fixed_byte_caps(self):
        self.assertEqual(self.manifest['base'],self.previous_manifest['base']);self.assertEqual(self.manifest['addenda'][:17],self.previous_manifest['addenda'])
        report=self.addendum['derived_source_report'];self.assertEqual(report['sha256'],hashlib.sha256(self.pieces[p.REPORT]).hexdigest())
        self.assertEqual(report['bytes'],len(self.pieces[p.REPORT]))
        for f,pin in self.op['input_sha256'].items():self.assertEqual(hashlib.sha256((p.ROOT/f).read_bytes()).hexdigest(),pin)
        self.assertTrue(all(len(raw)<2500000 for raw in self.pieces.values()));self.assertLess(sum(map(len,self.pieces.values())),2400000)
        with self.assertRaises(ValueError):loader.load_inventory(self.manifest,lambda f:self.reader(f)+b' ' if f==p.ADDENDUM else self.reader(f))
        manifest=copy.deepcopy(self.manifest);manifest['counts']['regional_projection_scenarios']+=1
        with self.assertRaises(ValueError):loader.load_inventory(manifest,self.reader)


    def test_subsurface_counterflow_has_nonzero_upper_and_lower_beyond_selection_window(self):
        from interval_depth_diagnostic_v1 import diagnose
        z=[0,100,200,300,400,700];strong=[-.1,.2,.3,.2,.15,0];weak=[0]*6
        result=diagnose(z,[weak,strong,weak],self.op)
        self.assertEqual(result['selected_column_index'],1);self.assertEqual(result['horizontal_selection_status'],INTERIOR)
        layer=next(l for l in result['selected_column_threshold_layers'] if l['threshold_m_s']==.1)
        self.assertAlmostEqual(layer['upper_depth_m'],200/3);self.assertAlmostEqual(layer['lower_depth_m'],500)
        self.assertFalse(result['surface_velocity_qualification_applied'])

    def test_declared_subset_preserves_original_indices_and_recomputes_raw_components(self):
        source={'depth_levels_m':[0,100,200,300,400,700],'columns':[]}
        for lat in [-5.6,-5.5,-5,-3.5,-3,-2.9]:
            source['columns'].append({'sampled_lon_lat':[-130,lat],
                'eastward_velocity_m_s':[.2]*6,'northward_velocity_m_s':[1]*6,
                'signed_reference_component_m_s':[999]*6})
        indices,profiles=p.recompute_subset(source,self.op)
        self.assertEqual(indices,[1,2,3,4])
        self.assertTrue(all(abs(v-.2)<1e-12 for column in profiles for v in column))
        self.assertEqual(source['columns'][1]['signed_reference_component_m_s'],[999]*6)
        source['columns'][2]['northward_velocity_m_s'][3]=None
        self.assertIsNone(p.recompute_subset(source,self.op)[1][1][3])
        source['columns'][2]['northward_velocity_m_s'][3]=float('nan')
        with self.assertRaises(ValueError):p.recompute_subset(source,self.op)

    def test_actual_source_mapping_components_and_countercurrent_ownership_are_separate(self):
        for row in self.report['sections']:
            source=self.chunks[row['source_file']];indices,components=p.recompute_subset(source,self.op)
            self.assertEqual(row['subset_column_indices'],indices)
            self.assertTrue(all(-5.5<=source['columns'][i]['sampled_lon_lat'][1]<=-3 for i in indices))
            index=row['diagnosis']['selected_column_index']
            if index is not None:
                self.assertEqual(row['selected_source_column_index'],indices[index])
                self.assertEqual(row['selected_recomputed_reference_component_m_s'],components[index])
            else:self.assertIsNone(row['selected_source_column_index'])
            self.assertEqual(source['entity_id'],'current:pacific-south-equatorial');self.assertEqual(source['component_bearing_degrees_true'],270)
            self.assertEqual(row['entity_id'],'current:pacific-south-subsurface-countercurrent');self.assertEqual(row['derived_component_bearing_degrees_true'],90)
        self.assertEqual([s['longitude_degrees_east'] for s in self.op['sections']],[-140,-130,-120])
        for c in self.cases:
            self.assertEqual(c['entity_id'],'current:pacific-south-subsurface-countercurrent')
            owner=next(r for r in self.view['records'] if r['entity_id']==c['entity_id'])
            self.assertIn(c['id'],owner['projection_ids'] if c in self.addendum['projections'] else owner['unresolved_reference_case_ids'])
            for a in c['anchors']:
                self.assertEqual(a['source_original_entity_id'],'current:pacific-south-equatorial')
                self.assertEqual(a['source_original_component_bearing_degrees_true'],270)
                self.assertEqual(a['source_component_bearing_degrees_true'],90)

    def test_subset_component_mapping_and_definition_mutations_are_rejected(self):
        for field,value in [('subset_column_indices',[0,1,2]),('selected_source_column_index',9999),('selected_recomputed_reference_component_m_s',[999])]:
            report=copy.deepcopy(self.report);report['sections'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):p.cases_from_report(report,self.chunks,self.oldop,self.op)
        for field,value in [('entity_id','current:pacific-south-equatorial'),('component_bearing_degrees_true',270),('source_component_bearing_degrees_true',90),('primary_threshold_m_s',.2),('core_search_depth_interval_m',[100,700]),('surface_component_gate_m_s',.05)]:
            op=copy.deepcopy(self.op);op[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):p.derive_report(self.chunks,self.oldop,op)
        report=copy.deepcopy(self.report);report['sections'][0]['diagnosis']['selected_column_threshold_layers']=[{'threshold_m_s':.05,'lower_depth_m':999}]
        with self.assertRaises(ValueError):p.cases_from_report(report,self.chunks,self.oldop,self.op)


if __name__=='__main__':unittest.main()
