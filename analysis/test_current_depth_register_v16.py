"""Check seasonal parent context, sectional isotachs and qualitative near-halt limits."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v15 as previous
import build_current_depth_register_v16 as depth


class RegionalDepthSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][264:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_prior_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:264],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':269,'identities_with_scoped_depth_reference':72,'identities_not_yet_assessed':39,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_ligurian_keeps_broader_parent_summary_and_source_seasons(self):
        for phase,value,metric in [('winter',450,'reported_vertical_extent'),('summer',250,'reported_vertical_thickness')]:
            row=self.rows['ligurian-berta-2018-northern-summary-'+phase];self.validate(row)
            self.assertEqual((row['approximate_value_m'],row['metric']),(value,metric))
            self.reject(row,[('phase_label','autumn'),('identity_relationship','same_whole_current'),('branch_section_scope','whole_ligurian_route'),('source_observation_window_assigned',True),('section_sampling_month','2011-12'),('calendar_months',[12,1,2])])

    def test_depth_and_thickness_keep_distinct_datums(self):
        winter=self.rows['ligurian-berta-2018-northern-summary-winter']
        summer=self.rows['ligurian-berta-2018-northern-summary-summer']
        self.assertEqual(winter['vertical_datum'],'local_sea_surface_positive_down')
        self.assertEqual(summer['vertical_datum'],'not_applicable_thickness_distance')
        self.reject(summer,[('vertical_datum','local_sea_surface_positive_down'),('metric','reported_vertical_extent')])

    def test_balearic_sections_not_catalan_or_sill_depths(self):
        row=self.rows['balearic-garcia-ladona-1996-fe89-section-a'];self.validate(row)
        self.assertEqual(row['range_m'],[100,150])
        self.reject(row,[('range_m',[250,300]),('range_m',[0,600]),('section_labels',['F','D','C']),('entity_id','current:ligurian'),('section_group_summary',True)])
        group=self.rows['balearic-garcia-ladona-1996-fe89-fdc'];self.validate(group)
        self.assertEqual((group['approximate_value_m'],group['section_labels']),(200,['F','D','C']))
        self.reject(group,[('approximate_value_m',600),('approximate_value_m',800),('section_labels',['A']),('section_group_summary',False),('evidence_kind','published_geostrophic_section')])

    def test_balearic_threshold_references_and_cruise_support(self):
        for name in ['section-a','fdc']:
            row=self.rows['balearic-garcia-ladona-1996-fe89-'+name]
            self.reject(row,[('boundary_definition',{'kind':'physical_zero_velocity','speed_m_s':0}),('geostrophic_reference_pressure_dbar',300),('ADCP_deep_reference_depth_m',600),('pressure_to_depth_conversion_performed',True),('campaign_window',{'start_date':'1996-06-04','end_date':'1996-06-19'}),('window_role','exact_section_dates'),('section_sampling_month','1989-07')])

    def test_rim_near_halt_not_exact_zero_or_observing_period(self):
        row=self.rows['rim-podymov-2023-near-halt-band'];self.validate(row)
        self.assertEqual(row['range_m'],[250,300])
        self.reject(row,[('metric','lower_flow_boundary_depth'),('metric','reported_flow_depth_band'),('range_m',[50,200]),('range_m',[300,350]),('velocity_threshold_m_s',0),('exact_zero_established',True),('source_observation_window_assigned',True),('section_sampling_month','2016-01'),('underlying_citation','Oguz1999')])

    def test_no_geometry_extrema_or_independent_repeat_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('lower_boundary_m',300),('thickness_m',250),('annual_range_m',[250,450]),('uncertainty_m',50),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('independent_observation_count_claimed',True),('same_source_width_reference_id','unreviewed')])

    def test_reproduction_csv_and_source_provenance(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows['balearic-garcia-ladona-1996-fe89-fdc']['section_labels']),['F','D','C'])
        self.assertEqual(rows['rim-podymov-2023-near-halt-band']['exact_zero_established'],'False')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
