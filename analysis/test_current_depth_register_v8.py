"""Verify branch/core operators, regional thickness and original unit semantics."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v7 as previous
import build_current_depth_register_v8 as depth


class RegionalThicknessCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][95:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def test_inventory_and_prior_95_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:95],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':107,'identities_with_scoped_depth_reference':40,'identities_not_yet_assessed':71,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_kuroshio_paths_and_isotach_cores_keep_their_definitions(self):
        expected={'inshore-reach':('reported_vertical_extent',300),'offshore-reach':('reported_vertical_extent',600),
                  'southern-core-boundary':('core_lower_boundary_depth',600),'northern-core-boundary':('core_lower_boundary_depth',1000)}
        for tag,pair in expected.items():
            row=self.rows['kuroshio-hsin-2008-'+tag]
            self.assertEqual((row['metric'],row['approximate_value_m']),pair)
            self.assertEqual(row['climatology_years'],[1982,2005]);self.assertIsNone(row['annual_range_m'])
        original=self.rows['kuroshio-hsin-2008-northern-core-boundary']
        for field,value in [('core_definition',{'kind':'source_velocity_isotach','speed_m_s':0.2}),('metric','reported_vertical_extent'),('branch_section_scope','section_22.5N'),('model_product','observations')]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_norwegian_cores_are_static_transport_selected_masks(self):
        for tag,value in [('svinoy',460),('gimsoy',530)]:
            row=self.rows['nwasc-baumann-2026-'+tag+'-core-bottom']
            self.assertEqual(row['approximate_value_m'],value);self.assertEqual(row['climatology_years'],[1993,2022])
            self.assertEqual(row['core_definition']['excluded_surface_upper_depth_m'],50)
            for field,newvalue in [('fraction_of_mean_transport',0.6),('ranking','decreasing_salinity'),('static_mean_mask',False),('absolute_salinity_min_g_kg',35)]:
                changed=copy.deepcopy(row);changed['core_definition'][field]=newvalue
                with self.assertRaises(ValueError):self.validate(changed)

    def test_source_thickness_is_not_bottom_depth_or_whole_route_geometry(self):
        tsushima=self.rows['tsushima-jma-regional-thickness'];guinea=self.rows['guinea-djakoure-2017-thickness-summary']
        self.assertEqual(tsushima['metric'],'reported_vertical_thickness');self.assertEqual(tsushima['approximate_value_m'],200)
        self.assertEqual(guinea['metric'],'reported_vertical_thickness');self.assertEqual(guinea['range_m'],[30,40])
        for original in [tsushima,guinea]:
            self.assertEqual(original['vertical_datum'],'not_applicable_thickness_distance')
            self.assertIsNone(original['thickness_m']);self.assertIsNone(original['annual_range_m'])
            for field,value in [('vertical_datum','local_sea_surface_positive_down'),('metric','lower_flow_boundary_depth'),('thickness_m',200),('climatology_years',[1985,2010]),('annual_extrema_eligible',True)]:
                row=copy.deepcopy(original);row[field]=value
                with self.assertRaises(ValueError):self.validate(row)

    def test_solomon_model_and_new_ireland_observational_summary_are_distinct(self):
        observed=self.rows['nicu-melet-2010-cited-observed-core'];model=self.rows['siuc-melet-2010-6s-model-core']
        self.assertEqual(observed['approximate_value_m'],235);self.assertEqual(observed['evidence_kind'],'published_literature_synthesis')
        self.assertIsNone(observed.get('climatology_years'))
        self.assertEqual(model['approximate_value_m'],200);self.assertEqual(model['climatology_years'],[1986,2004])
        for original,field,value in [(observed,'climatology_years',[1986,2004]),(observed,'evidence_kind','published_model_climatology'),(model,'section_latitude_degrees_north',6),(model,'entity_id','current:new-ireland-coastal-undercurrent')]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_mediterranean_section_thickness_core_and_pressure_are_distinct(self):
        thickness=self.rows['med-bower-2002-may1993-section1-thickness'];core=self.rows['med-bower-2002-may1993-section3-velocity-core']
        self.assertEqual((thickness['metric'],thickness['approximate_value_m']),('reported_vertical_thickness',200))
        self.assertEqual((core['metric'],core['approximate_value_m']),('core_depth',1100))
        for original in [thickness,core]:
            self.assertEqual(original['section_sampling_month'],'1993-05');self.assertFalse(original['pressure_to_depth_conversion_performed'])
            for field,value in [('unit','dbar'),('pressure_to_depth_conversion_performed',True),('velocity_reference','direct_ADCP'),('section_sampling_month','1994-05')]:
                row=copy.deepcopy(original);row[field]=value
                with self.assertRaises(ValueError):self.validate(row)

    def test_no_uncertainty_volumes_state_joins_or_independent_repeat_promotion(self):
        for field,value in [('uncertainty_m',50),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('independent_observation_count_claimed',True),('same_source_width_reference_id','unreviewed-width')]:
            row=copy.deepcopy(self.new[0]);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)
        for row in self.new:self.validate(row)

    def test_raw_facts_and_outputs_reproduce_with_core_definitions(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),12);self.assertEqual(len({r['entity_id'] for r in self.new}),7)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        row=rows['nwasc-baumann-2026-svinoy-core-bottom']
        self.assertEqual(json.loads(row['core_definition'])['fraction_of_mean_transport'],0.5)
        self.assertEqual(rows['tsushima-jma-regional-thickness']['metric'],'reported_vertical_thickness')
        self.assertEqual(rows['tsushima-jma-regional-thickness']['vertical_datum'],'not_applicable_thickness_distance')
        self.assertEqual(rows['med-bower-2002-may1993-section3-velocity-core']['pressure_to_depth_conversion_performed'],'False')


if __name__=='__main__':unittest.main()
