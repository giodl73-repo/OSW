"""Check directional depth evidence against time, section and boundary confusion."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v10 as previous
import build_current_depth_register_v11 as depth


class IndianOceanDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][124:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,original,changes):
        for field,value in changes:
            row=copy.deepcopy(original);row[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):self.validate(row)

    def test_prior_evidence_full_inventory_and_coverage(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:124],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':140,'identities_with_scoped_depth_reference':54,'identities_not_yet_assessed':57,'whole_route_depth_profiles':0,'volume_estimates':0})
        gaps={r['entity_id'] for r in self.data['records'] if not r['depth_reference_ids']}
        self.assertIn('current:indian-south-equatorial-countercurrent',gaps)

    def test_simulation_years_do_not_inherit_validation_calendar(self):
        for row in self.new:
            if row.get('model_product')!='Sen2022_ROMS_NIO':continue
            self.assertEqual(row['model_time_basis']['simulation_duration_years'],8)
            self.assertEqual(row['model_time_basis']['analysis_window'],'last_three_simulation_years')
            self.reject(row,[('climatology_years',[2003,2015]),('climatology_years',[1945,1989]),('section_sampling_month','2020-11'),('evidence_kind','published_observed_section'),('model_time_basis',{'kind':'calendar_hindcast','calendar_years':[2003,2015]})])

    def test_eacc_regional_mean_is_not_june_axis_or_physical_thickness(self):
        core=self.rows['eacc-zheng-2024-ofes-core'];reach=self.rows['eacc-zheng-2024-ofes-concentrated-reach']
        self.assertEqual(core['range_m'],[20,80]);self.assertEqual(reach['approximate_value_m'],300)
        self.assertEqual(core['climatology_years'],[1993,2017]);self.assertIsNone(core['calendar_months'])
        self.reject(core,[('calendar_months',[6]),('model_product','AVISO'),('spatial_averaging','June_main_axis_only'),('core_definition',{'kind':'salinity_maximum'}),('metric','reported_vertical_thickness')])
        self.reject(reach,[('lower_boundary_m',300),('metric','lower_flow_boundary_depth')])

    def test_eicc_directional_sections_are_not_interchangeable(self):
        north=self.rows['eicc-sen-2022-north-a-core'];south=self.rows['eicc-sen-2022-south-b-core']
        self.assertEqual(north['approximate_value_m'],150);self.assertEqual(south['approximate_value_m'],150)
        self.assertEqual(north['section_latitude_degrees_north'],19.3);self.assertEqual(south['section_latitude_degrees_north'],16)
        self.reject(north,[('section_name','B'),('calendar_months',[10,11,12]),('flow_direction','southward'),('section_longitude_band_degrees_east',[82.1,84.2])])
        band=self.rows['eicc-sen-2022-north-c-core-band']
        self.assertEqual(band['range_m'],[0,100]);self.assertEqual(band['metric'],'core_depth')
        self.reject(band,[('metric','reported_vertical_thickness'),('thickness_m',100),('approximate_value_m',50)])
        self.assertEqual(self.rows['eicc-sen-2022-north-b-reach']['approximate_value_m'],20)
        regional=self.rows['eicc-sen-2022-south-regional-reach'];self.assertIsNone(regional.get('section_name'))
        self.reject(regional,[('section_name','B')])

    def test_wicc_summer_reversal_not_transport_cutoff(self):
        for tag,value,months in [('south-june-reversal',60,[6]),('south-july-august-reversal',30,[7,8])]:
            row=self.rows['wicc-sen-2022-'+tag]
            self.assertEqual(row['approximate_value_m'],value);self.assertEqual(row['calendar_months'],months)
            self.assertEqual(row['boundary_definition'],'reported_direction_reversal')
            self.reject(row,[('approximate_value_m',100),('boundary_definition','transport_integration_cutoff'),('flow_direction','northward')])
        winter=self.rows['wicc-sen-2022-north-seasonal-reach']
        self.assertEqual(winter['approximate_value_m'],100);self.assertEqual(winter['calendar_months'],[10,11,12,1,2])

    def test_somali_seasonal_sections_not_independent_summer_repeats(self):
        combined=self.rows['somali-sen-2022-northeast-a-c-reach']
        self.assertEqual(combined['section_names'],['A','C']);self.assertEqual(combined['approximate_value_m'],800)
        self.reject(combined,[('section_names',['A','B','C']),('flow_direction','southwestward'),('section_name','B')])
        for tag,value,latitude in [('southwest-b-reach',500,6),('southwest-c-reach',600,3)]:
            row=self.rows['somali-sen-2022-'+tag]
            self.assertEqual(row['approximate_value_m'],value);self.assertEqual(row['section_latitude_degrees_north'],latitude)
            self.reject(row,[('calendar_months',[5,6,7,8,9,10]),('approximate_value_m',800)])

    def test_semc_observed_cores_not_underlying_or_offshore_currents(self):
        core=self.rows['semc-nauw-2008-april2001-t6-t8-core-band'];reach=self.rows['semc-nauw-2008-april2001-jet-reach']
        self.assertEqual(core['range_m'],[100,160]);self.assertEqual(core['section_names'],['T6','T7','T8'])
        self.assertEqual(reach['approximate_value_m'],1000);self.assertEqual(reach['section_sampling_month'],'2001-04')
        self.reject(core,[('section_names',['T5','T6','T7','T8']),('entity_id','current:indian-south-equatorial-countercurrent'),('section_sampling_month','2001-03'),('window_role','exact_section_occupation')])
        self.reject(reach,[('approximate_value_m',2400),('approximate_value_m',1100),('approximate_value_m',1300)])

    def test_no_geometry_promotion_and_source_json_csv_reproduce(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),16)
        for row in self.new:
            self.validate(row)
            self.reject(row,[('uncertainty_m',10),('annual_range_m',[30,1000]),('volume_eligible',True),('seasonal_playback_eligible',True),('whole_current_representative',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)])
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        csv_rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        row=csv_rows['wicc-sen-2022-south-june-reversal']
        self.assertEqual(row['flow_direction'],'southward');self.assertEqual(row['boundary_definition'],'reported_direction_reversal')
        self.assertEqual(json.loads(row['model_time_basis'])['analysis_window'],'last_three_simulation_years')


if __name__=='__main__':unittest.main()
