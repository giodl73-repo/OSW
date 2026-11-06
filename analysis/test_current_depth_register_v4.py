"""Keep mooring-climatology boundary depths distinct from depth summaries."""
import copy
import json
import unittest
import build_current_depth_register_v3 as prior
import build_current_depth_register_v4 as depth
from build_current_depth_register_v2 import validate_reference


class BoundaryCurrentDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][52:]
        cls.leeuwin=[r for r in cls.new if r['entity_id']=='current:leeuwin']
        cls.identities={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def test_prior_52_references_and_complete_inventory_preserved(self):
        self.assertEqual(self.data['evidence'][:52],prior.build()['evidence'])
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':58,'identities_with_scoped_depth_reference':22,'identities_not_yet_assessed':89,'whole_route_depth_profiles':0,'volume_estimates':0})
        self.assertEqual(len(self.identities),111)

    def test_leeuwin_phases_keep_local_zero_crossing_and_actual_months(self):
        rows={r['phase_label']:r for r in self.leeuwin}
        self.assertEqual({k:r['approximate_value_m'] for k,r in rows.items()},{'annual mean':300,'August–September':260,'February–March':350})
        self.assertEqual(rows['August–September']['calendar_months'],[8,9])
        self.assertEqual(rows['February–March']['calendar_months'],[2,3])
        self.assertIsNone(rows['annual mean']['calendar_months'])
        self.assertEqual(len({r['source_case_id'] for r in self.leeuwin}),1)
        for row in self.leeuwin:
            self.assertEqual(row['metric'],'lower_flow_boundary_depth');self.assertIsNone(row['range_m'])
            self.assertIsNone(row['annual_range_m']);self.assertFalse(row['annual_extrema_eligible'])

    def test_instrument_bottom_or_missing_processing_cannot_replace_boundary(self):
        for field,value in [('depth_operator','mooring_bottom_depth'),('mooring_id','TR20'),('processing',None),('climatology_period',{'start_month':'2011-01','end_month':'2023-05'}),('metric','observation_layer')]:
            row=copy.deepcopy(self.leeuwin[0]);row[field]=value
            with self.assertRaises(ValueError):depth.validate_boundary_context(row)

    def test_summaries_do_not_become_diagnosed_vertical_boundaries(self):
        rows={r['entity_id']:r for r in self.new if r not in self.leeuwin}
        self.assertEqual({k:r['approximate_value_m'] for k,r in rows.items()},{'current:agulhas':2000,'current:somali':1000,'current:east-australian':200})
        self.assertEqual(rows['current:somali']['calendar_months'],[6])
        self.assertEqual(rows['current:east-australian']['evidence_kind'],'institutional_literature_synthesis')
        self.assertIn('screenshot cache misses',rows['current:east-australian']['qualification'])
        changed=copy.deepcopy(rows['current:east-australian']);changed['metric']='lower_flow_boundary_depth'
        with self.assertRaises(ValueError):depth.validate_boundary_context(changed)

    def test_depth_references_cannot_promote_to_volume_or_monthly_playback(self):
        for field,value in [('volume_eligible',True),('seasonal_playback_eligible',True),('physical_state_join_eligible',True),('thickness_m',300),('annual_range_m',[260,350]),('uncertainty_m',45)]:
            row=copy.deepcopy(self.leeuwin[0]);row[field]=value
            with self.assertRaises(ValueError):validate_reference(row,self.identities,self.metrics)

    def test_new_source_pointers_and_observation_scope_remain_explicit(self):
        raw=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        for row in self.new:
            source=raw['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(source,{k:row[k] for k in source})
            self.assertIsNone(row['observed_period']);self.assertFalse(row['whole_current_representative'])

    def test_json_and_csv_outputs_reproduce(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))


if __name__=='__main__':unittest.main()
