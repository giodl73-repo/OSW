"""Protect source joins, temporal support and diagnostic versus physical boundaries."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v14 as previous
import build_current_depth_register_v15 as depth


class LocalDepthJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][157:]
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']
        cls.layers=[r for r in cls.new if r['entity_id']=='current:caribbean']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def reject(self,row,changes):
        for k,v in changes:
            changed=copy.deepcopy(row);changed[k]=v
            with self.subTest(field=k),self.assertRaises(ValueError):self.validate(changed)

    def test_previous_evidence_and_identities_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:157],prior['evidence'])
        self.assertEqual(self.ids,{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':264,'identities_with_scoped_depth_reference':69,'identities_not_yet_assessed':42,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_all_106_measurements_join_exactly_once(self):
        measurements=json.loads((depth.ROOT/depth.SERIES).read_bytes())['records']
        self.assertEqual(len(self.layers),106)
        self.assertEqual({r['measurement_id'] for r in self.layers},{r['id'] for r in measurements})
        for row in self.layers:self.validate(row)
        self.reject(self.layers[0],[('measurement_id','unknown'),('source_profile_index',-1),('latitude',0),('longitude',0),('transect_id','transect_3'),('measurement_pointer','/records/1'),('operator_sha256','0'*64)])

    def test_diagnostic_threshold_and_discretization_retained(self):
        row=self.layers[0]
        self.reject(row,[('metric','lower_flow_boundary_depth'),('threshold_m_s',0.05),('minimum_support_bins',1),('approximate_value_m',1000),('discretization_bracket_m',[0,1000]),('discretization_bracket_is_confidence_interval',True),('depth_basis','physical_current_bottom')])

    def test_actual_interval_and_source_end_time_not_replaced_with_midpoint(self):
        row=self.layers[0]
        self.assertEqual(row['source_reported_time'],row['sampling_interval']['end'])
        self.assertNotEqual(row['source_reported_time'],row['derived_representative_time'])
        self.reject(row,[('source_reported_time',row['derived_representative_time']),('derived_representative_time',row['source_reported_time']),('sampling_interval',{'start':'2024-01-01','end':'2024-12-31'})])

    def test_unresolved_upper_boundaries_remain_in_linked_series(self):
        records=json.loads((depth.ROOT/depth.SERIES).read_bytes())['records']
        complete=[r for r in records if r['velocity_defined_layer']['layer_thickness_m'] is not None]
        incomplete=[r for r in records if r['velocity_defined_layer']['layer_thickness_m'] is None]
        self.assertEqual((len(complete),len(incomplete)),(57,49))
        for r in incomplete:self.assertNotEqual(r['velocity_defined_layer']['upper']['status'],'bracketed')
        for r in self.layers:self.assertIsNone(r['thickness_m'])

    def test_baffin_arctic_component_not_atlantic_or_fjord_campaign(self):
        row=self.new[-1];self.validate(row)
        self.reject(row,[('entity_id','current:west-greenland'),('water_mass_component','Atlantic_water'),('range_m',[0,640]),('branch_section_scope','whole_current'),('metric','reported_vertical_thickness'),('section_sampling_month','2013-08')])

    def test_no_whole_current_or_volume_promotion(self):
        for row in [self.layers[0],self.new[-1]]:
            self.reject(row,[('lower_boundary_m',300),('thickness_m',200),('uncertainty_m',10),('annual_range_m',[100,300]),('whole_current_representative',True),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('annual_extrema_eligible',True),('independent_observation_count_claimed',True),('same_source_width_reference_id','unreviewed')])

    def test_reproduction_pins_and_csv_joins(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        columns=next(csv.reader(io.StringIO(raw.decode('utf8'))));self.assertEqual(len(columns),len(set(columns)))
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))));row=rows[157]
        self.assertEqual(row['measurement_id'],self.layers[0]['measurement_id'])
        self.assertEqual(json.loads(row['sampling_interval']),self.layers[0]['sampling_interval'])
        self.assertEqual(json.loads(row['discretization_bracket_m']),self.layers[0]['discretization_bracket_m'])
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for p,digest in source['source_input_sha256'].items():self.assertEqual(self.data['input_sha256'][p],digest)


if __name__=='__main__':unittest.main()
