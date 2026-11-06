"""Guard metrics, source phases, piecewise support and previous scenario values."""
import copy
import csv
import hashlib
import io
import json
import unittest
import build_current_depth_route_projections_v1 as previous
import build_current_depth_route_projections_v2 as depth


class MetricSpecificRouteDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.operator=json.loads((depth.ROOT/depth.OPERATOR).read_bytes())
        cls.source=json.loads((depth.ROOT/cls.operator['depth_register_file']).read_bytes())
        cls.refs={r['id']:r for r in cls.source['evidence']}
        cls.projections={p['entity_id']:p for p in cls.data['projections']}

    def test_frozen_wicc_scenario_preserved_with_explicit_field_rename(self):
        prior=previous.build();migrated=copy.deepcopy(self.data['projections'][0])
        for s in migrated['samples']:s['projected_extent_descriptor_m']=s.pop('projected_depth_descriptor_m')
        self.assertEqual(migrated,prior['projections'][0])
        self.assertEqual(json.loads((depth.ROOT/previous.OUTPUT).read_bytes()),prior)

    def test_four_catalog_owners_and_three_distinct_metric_definitions(self):
        self.assertEqual(self.data['counts'],{'catalog_identities':111,'identities_with_regional_projection_scenarios':4,'identities_not_yet_projected':107,'regional_projection_scenarios':4,'source_anchor_references':10,'new_depth_measurements':0,'whole_route_physical_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(self.projections['current:east-india-coastal']['metric'],'projected_core_depth_descriptor')
        self.assertEqual(self.projections['current:somali']['metric'],'projected_reported_vertical_extent_descriptor')
        self.assertEqual(self.projections['current:agulhas']['metric'],'projected_net_section_transport_zero_depth_descriptor')
        for record,source in zip(self.data['records'],self.source['records']):
            self.assertEqual(record['entity_id'],source['entity_id']);self.assertEqual(record['depth_reference_ids'],source['depth_reference_ids'])

    def test_known_anchors_and_unknown_outside_each_new_supported_interval(self):
        expected={'current:somali':[(6,500),(3,600)],'current:east-india-coastal':[(16,150),(12,100)],'current:agulhas':[(-30,1500),(-32,3100),(-34,1900),(-36,3500)]}
        for entity,pairs in expected.items():
            p=self.projections[entity]
            self.assertEqual([(a['latitude_degrees_north'],a['approximate_depth_descriptor_m']) for a in p['anchors']],pairs)
            self.assertIsNone(p['samples'][0]['projected_depth_descriptor_m']);self.assertIsNone(p['samples'][-1]['projected_depth_descriptor_m'])
            self.assertEqual(len([s for s in p['samples'] if s['status']=='source_anchor_mapped_to_editorial_route']),len(pairs))
            for s in p['samples']:
                if s['status']=='unsupported_no_extrapolation':
                    self.assertIsNone(s['projected_depth_descriptor_m']);self.assertEqual(s['source_reference_ids'],[])

    def test_piecewise_interpolation_uses_only_adjacent_anchor_provenance(self):
        anchors=[{'distance_km':0,'approximate_depth_descriptor_m':1500,'reference_id':'a'},{'distance_km':100,'approximate_depth_descriptor_m':3100,'reference_id':'b'},{'distance_km':300,'approximate_depth_descriptor_m':1900,'reference_id':'c'},{'distance_km':400,'approximate_depth_descriptor_m':3500,'reference_id':'d'}]
        self.assertEqual(depth.interpolate(50,anchors),(2300,['a','b']))
        self.assertEqual(depth.interpolate(200,anchors),(2500,['b','c']))
        self.assertEqual(depth.interpolate(350,anchors),(2700,['c','d']))
        self.assertEqual(depth.interpolate(100,anchors),(3100,['b']))
        self.assertEqual(depth.interpolate(401,anchors),(None,[]))
        for bad in [list(reversed(anchors)),[anchors[0],anchors[0]]]:
            with self.assertRaises(ValueError):depth.interpolate(50,bad)
        with self.assertRaises(ValueError):depth.interpolate(float('nan'),anchors)

    def test_frozen_source_metrics_periods_and_model_context_cannot_change(self):
        for case in self.operator['cases']:
            ref_id=case['source_reference_ids'][0]
            for key,value in [('metric','reported_vertical_thickness'),('entity_id','current:gulf-stream'),('approximate_value_m',0),('calendar_months',[7,8]),('phase_label','opposite_flow'),('campaign_window',{'start_month':'2026-01','end_month':'2026-02'}),('model_time_basis',{'calendar_years':[2003,2015]}),('reference_route_projection_eligible',False)]:
                refs=copy.deepcopy(self.refs);refs[ref_id][key]=value
                with self.subTest(case=case['id'],key=key),self.assertRaises(ValueError):depth.validate_case(case,refs)

    def test_case_contract_rejects_core_extent_and_transport_diagnostic_aliases(self):
        for original in self.operator['cases']:
            for key,value in [('projected_metric','physical_lower_flow_boundary'),('source_metric','reported_vertical_extent'),('calendar_months',[1,2,3]),('model_time_basis',None),('route_id','unrelated-route')]:
                if original.get(key)==value:continue
                changed=copy.deepcopy(original);changed[key]=value
                with self.subTest(case=original['id'],key=key),self.assertRaises(ValueError):depth.validate_case(changed,self.refs)

    def test_gate_must_stay_inside_source_longitude_band(self):
        lengths=json.loads((depth.ROOT/self.operator['length_register_file']).read_bytes())
        case=self.operator['cases'][0];route=depth.load_route(depth.ROOT,case,lengths)
        changed=copy.deepcopy(route)
        changed['coordinates_lon_lat']=[[lon+10,lat] for lon,lat in changed['coordinates_lon_lat']]
        with self.assertRaises(ValueError):depth.project(case,changed,self.operator['eligibility'])

    def test_model_seasons_and_historical_survey_remain_separate_from_volume(self):
        somali=self.projections['current:somali'];eicc=self.projections['current:east-india-coastal'];agulhas=self.projections['current:agulhas']
        self.assertEqual(somali['calendar_months'],[11,12,1,2]);self.assertEqual(eicc['calendar_months'],[10,11,12])
        self.assertEqual(eicc['model_time_basis']['analysis_window'],'last_three_simulation_years')
        self.assertIsNone(eicc['model_time_basis']['calendar_years']);self.assertIsNone(eicc['campaign_window'])
        self.assertEqual(agulhas['campaign_window'],{'start_month':'2003-02','end_month':'2003-03'})
        self.assertIsNone(agulhas['model_product']);self.assertIsNone(agulhas['calendar_months'])
        for p in self.data['projections']:
            self.assertFalse(any(p['eligibility'].values()));self.assertIsNone(p['physical_thickness_profile']);self.assertIsNone(p['volume_km3'])
            self.assertIsNone(p['annual_depth_range_m'])

    def test_json_csv_reproduce_with_metric_and_time_context(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        raw=depth.csv_bytes(self.data);self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),raw)
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf8'))))
        self.assertEqual(len(rows),sum(len(p['samples']) for p in self.data['projections']))
        for row in rows:
            self.assertEqual(row['metric'],self.projections[row['entity_id']]['metric'])
            self.assertEqual(row['volume_eligible'],'False')
            if row['entity_id']=='current:east-india-coastal':self.assertEqual(json.loads(row['calendar_months']),[10,11,12])
        for path,digest in self.data['input_sha256'].items():self.assertEqual(hashlib.sha256((depth.ROOT/path).read_bytes()).hexdigest(),digest)


if __name__=='__main__':unittest.main()
