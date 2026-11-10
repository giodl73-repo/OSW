"""Guard Pacific branch attribution, simulation years and inclusive versus strict bounds."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v16 as previous
import build_current_depth_register_v17 as depth


class PacificDepthSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][269:]
        cls.rows={r['id']:r for r in cls.new};cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k,value=v),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build();self.assertEqual(self.data['evidence'][:269],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':279,'identities_with_scoped_depth_reference':75,'identities_not_yet_assessed':36,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_coastal_model_depth_not_other_branches_or_calendar_years(self):
        row=self.rows['peru-penven-2005-pcc-mean-reach'];self.validate(row)
        self.assertEqual(row['approximate_value_m'],50)
        self.reject(row,[('approximate_value_m',10),('approximate_value_m',300),('source_branch','peru_chile_undercurrent'),('evidence_kind','published_observed_section'),('model_analysis_years',[2003,2010]),('model_years_are_calendar_years',True),('model_product','OCCAM'),('section_latitude_band_degrees_north',[-20,-5])])

    def test_six_pcuc_sections_retain_spatial_sequence_and_actual_isotachs(self):
        rows=[r for r in self.new if r.get('profile_series_id')]
        self.assertEqual(len(rows),6)
        expected=[('Punta Falsa',-6,240),('Chimbote',-9.4,280),('Callao',-12.1,310),('Pisco',-14,470),('San Juan',-15.7,550),('Arica',-18.6,620)]
        self.assertEqual([(r['section_name'],r['section_latitude_degrees_north'],r['approximate_value_m']) for r in rows],expected)
        for row in rows:
            self.validate(row)
            self.reject(row,[('source_branch','peru_coastal_current'),('boundary_definition',{'kind':'maximum_depth_of_source_poleward_velocity_isotach','speed_m_s':0.1}),('profile_series_kind','observed_whole_route_profile'),('potential_vorticity_prediction_used',True),('section_sampling_month','2005-10')])
        self.reject(rows[1],[('approximate_value_m',340)])
        self.reject(rows[2],[('approximate_value_m',430)])
        self.reject(rows[-1],[('approximate_value_m',640)])

    def test_offshore_observed_bound_remains_inclusive_and_distinct(self):
        row=self.rows['peru-chaigneau-2013-poc-at-least500'];self.validate(row)
        self.assertEqual(row['lower_bound_m'],500);self.assertFalse(row['lower_bound_exclusive'])
        self.reject(row,[('lower_bound_operator','>'),('lower_bound_exclusive',True),('source_branch','peru_coastal_current'),('observing_record_span_years',[2005,2005]),('velocity_reconstruction','ROMS'),('depth_basis','terminal_current_bottom')])

    def test_oyashio_seasonal_upper_bound_not_exact_depth(self):
        row=self.rows['oyashio-qiu-2019-summer-fall-upper-limit'];self.validate(row)
        self.assertIsNone(row['approximate_value_m']);self.assertEqual(row['upper_bound_m'],2000)
        self.reject(row,[('upper_bound_exclusive',False),('upper_bound_m',1000),('phase_label','winter_and_spring'),('source_phases',['winter','spring']),('calendar_months',[6,7,8,9,10,11]),('branch_section_scope','entire_oyashio_system')])

    def test_ke_original_component_supports_inclusive_reach_and_keeps_eddy_context(self):
        row=self.rows['kuroshio-extension-qu-2001-deep-component'];self.validate(row)
        self.assertEqual(row['reported_component_depth_m'],1000)
        self.reject(row,[('entity_id','current:north-pacific'),('entity_id','current:oyashio'),('lower_bound_operator','>'),('lower_bound_exclusive',True),('reported_component_depth_m',2000),('archive_version_is_observation_year',True),('deep_recirculation_influence_retained',False),('branch_section_scope','uniform_jet_section')])

    def test_no_whole_flow_geometry_or_volume_promotion(self):
        for row in self.new:
            self.validate(row)
            self.reject(row,[('thickness_m',500),('lower_boundary_m',500),('annual_range_m',[240,620]),('uncertainty_m',50),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('annual_extrema_eligible',True),('seasonal_playback_eligible',True),('independent_observation_count_claimed',True),('same_source_width_reference_id','unreviewed')])

    def test_reproduction_and_csv_scientific_fields(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(raw.decode('utf8')))}
        self.assertEqual(json.loads(rows['peru-penven-2005-pcuc-pisco-isotach']['boundary_definition'])['speed_m_s'],0.02)
        self.assertEqual(json.loads(rows['peru-penven-2005-pcc-mean-reach']['model_analysis_years']),[3,10])
        self.assertEqual(rows['kuroshio-extension-qu-2001-deep-component']['lower_bound_operator'],'>=')
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            original=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(original,{k:row[k] for k in original})


if __name__=='__main__':unittest.main()
