"""Check Nordic layer/core definitions and out-of-route Davidson evidence."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v19 as previous
import build_current_depth_register_v20 as depth


class NordicAndDavidsonDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][287:]
        cls.rows={r['id']:r for r in cls.new};cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:287],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':291,'identities_with_scoped_depth_reference':84,'identities_not_yet_assessed':27,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_basin_water_mass_depths_not_seasonal_or_swapped(self):
        for tag,interval in [('norwegian-basin',[500,600]),('lofoten-basin',[800,900])]:
            row=self.rows['norwegian-skjelvan-2001-'+tag+'-aw-depth'];self.validate(row)
            self.assertEqual(row['range_m'],interval)
            self.reject(row,[('range_m',[500,900]),('metric','lower_flow_boundary_depth'),('water_mass_component','Norwegian_Coastal_Water'),('depth_basis','measured_zero_velocity_boundary'),('source_current_interpretation','Norwegian_Coastal_Current'),('section_sampling_month','2001-03')])

    def test_water_mass_definition_and_access_scope_retained(self):
        row=self.rows['norwegian-skjelvan-2001-norwegian-basin-aw-depth']
        self.reject(row,[('water_mass_definition',{'practical_salinity_min':34,'temperature_min_deg_C':0}),('source_access_scope','original_full_paper_pixels'),('entity_id','current:north-cape'),('entity_id','current:west-spitsbergen')])

    def test_bso_salinity_core_not_adjacent_velocity_core(self):
        row=self.rows['north-cape-baumann-2026-bso-salinity-core'];self.validate(row)
        self.assertEqual(row['approximate_value_m'],350)
        self.reject(row,[('approximate_value_m',530),('section_name','Gimsoy'),('climatology_years',[2026,2026]),('metric','reported_vertical_extent')])
        for key,value in [('ranking','decreasing_absolute_geostrophic_velocity'),('excluded_surface_upper_depth_m',0),('fraction_of_maximum_mean_transport',0.7),('static_mean_mask',False),('absolute_salinity_min_g_kg',35)]:
            changed=copy.deepcopy(row);changed['core_definition'][key]=value
            with self.subTest(operator=key),self.assertRaises(ValueError):self.validate(changed)

    def test_branch_mapping_not_inherited_into_slope_current(self):
        row=self.rows['north-cape-baumann-2026-bso-salinity-core']
        self.reject(row,[('identity_mapping_source_url',None),('identity_mapping_source_locator',None),('entity_id','current:norwegian-atlantic-slope'),('branch_section_scope','all_Norwegian_branches')])

    def test_davidson_context_outside_reference_route_not_cuc_or_model(self):
        row=self.rows['davidson-beutel-2025-northern-extension-layer'];self.validate(row)
        self.assertEqual(row['range_m'],[0,200]);self.assertFalse(row['reference_route_projection_eligible'])
        self.reject(row,[('entity_id','current:california-undercurrent'),('branch_section_scope','entire_California_Oregon_route'),('reference_route_scope_relation','inside_reference_route'),('reference_route_projection_eligible',True),('evidence_kind','published_model_climatology'),('phase_label','upwelling'),('calendar_months',[11,12,1,2]),('section_sampling_month','2025-11')])

    def test_no_whole_geometry_annual_range_or_volume_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',350),('lower_boundary_m',350),('annual_range_m',[500,900]),('uncertainty_m',50),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('independent_observation_count_claimed',True),('same_source_width_reference_id','unreviewed')])

    def test_json_csv_and_source_facts_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(rows['davidson-beutel-2025-northern-extension-layer']['reference_route_projection_eligible'],'False')
        self.assertEqual(json.loads(rows['north-cape-baumann-2026-bso-salinity-core']['core_definition'])['ranking'],'decreasing_absolute_salinity')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
