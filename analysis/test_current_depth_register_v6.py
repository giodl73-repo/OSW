"""Check typed Pacific depth evidence, overlapping cases and censored bounds."""
import copy
import csv
import io
import json
import unittest
import build_current_depth_register_v5 as previous
import build_current_depth_register_v6 as depth


class PacificDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][65:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def test_inventory_and_prior_65_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:65],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':75,'identities_with_scoped_depth_reference':30,'identities_not_yet_assessed':81,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_mindanao_core_and_reach_are_distinct_overlapping_cases(self):
        for year,reach in [(2014,600),(2018,400)]:
            row=self.rows[f'mindanao-zhang-{year}-reach' if year==2014 else f'mindanao-ren-{year}-reach']
            self.assertEqual(row['metric'],'reported_vertical_extent');self.assertEqual(row['approximate_value_m'],reach)
            core=self.rows['mindanao-zhang-2014-core' if year==2014 else 'mindanao-ren-2018-core']
            self.assertEqual(core['metric'],'core_depth');self.assertEqual(core['approximate_value_m'],100)
            self.assertFalse(row['independent_observation_count_claimed']);self.assertIsNone(row['annual_range_m'])
        row=self.rows['mindanao-ren-2018-reach']
        self.assertEqual(row['climatology_period'],{'start_month':'2010-12','end_month':'2014-08'})
        for field,value in [('processing','raw observations'),('overlaps_case_id',None),('mooring_lon_lat',[127.3,8])]:
            changed=copy.deepcopy(row);changed[field]=value
            with self.assertRaises(ValueError):self.validate(changed)

    def test_model_extent_is_not_glider_sampling_bottom(self):
        model=self.rows['ngcuc-azminuddin-2022-140e-reach'];core=self.rows['ngcuc-azminuddin-2022-140e-core']
        observed=self.rows['ngcuc-spray-southern-track-below1000']
        self.assertEqual(model['approximate_value_m'],800);self.assertEqual(model['approximation_wording'],'almost')
        self.assertEqual(core['approximate_value_m'],163);self.assertEqual(core['metric'],'core_depth')
        self.assertEqual(observed['lower_bound_m'],1000);self.assertTrue(observed['lower_bound_exclusive'])
        self.assertIsNone(observed['approximate_value_m']);self.assertIsNone(observed['lower_boundary_m'])
        for original,field,value in [(model,'model_product','observations'),(model,'climatology_period',{'start_month':'1994-01','end_month':'2013-12'}),(model,'depth_uncertainty_inferred_from_velocity',True),(observed,'sampling_limit_is_flow_boundary',True)]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_pacific_bands_do_not_fill_generic_families(self):
        for tag,band in [('euc',[100,300]),('nscc',[200,600])]:
            row=self.rows[f'pacific-{tag}-azminuddin-2022-flow-band']
            self.assertEqual(row['range_m'],band);self.assertEqual(row['metric'],'reported_flow_depth_band')
            self.assertEqual(row['evidence_kind'],'published_literature_synthesis')
            self.assertIsNone(row['calendar_months']);self.assertIsNone(row.get('climatology_period'))
            changed=copy.deepcopy(row);changed['entity_id']='current:equatorial-undercurrent'
            with self.assertRaises(ValueError):self.validate(changed)
        gaps={r['entity_id'] for r in self.data['records'] if not r['depth_reference_ids']}
        self.assertIn('current:equatorial-undercurrent',gaps);self.assertIn('current:alaska',gaps)

    def test_strict_upper_bound_cannot_become_point_or_range(self):
        original=self.rows['alaska-coastal-stabeno-1996-shallow-bound']
        self.assertEqual(original['upper_bound_m'],150);self.assertTrue(original['upper_bound_exclusive'])
        self.assertIsNone(original['approximate_value_m']);self.assertIsNone(original['range_m'])
        for field,value in [('upper_bound_exclusive',False),('upper_bound_m',True),('upper_bound_m',float('nan')),('upper_bound_m',0),('approximate_value_m',150),('range_m',[0,150]),('lower_bound_m',150),('entity_id','current:alaska')]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_no_thickness_volumes_width_joins_or_annual_promotion(self):
        original=self.new[0]
        for field,value in [('thickness_m',600),('annual_range_m',[400,600]),('uncertainty_m',16),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('same_source_width_reference_id','unrelated-width'),('independent_observation_count_claimed',True)]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)
        for row in self.new:self.validate(row)

    def test_source_pointers_preserve_raw_facts(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),10)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})

    def test_json_csv_reproduce_and_export_bounds_and_case_context(self):
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        upper=rows['alaska-coastal-stabeno-1996-shallow-bound']
        self.assertEqual(upper['upper_bound_m'],'150');self.assertEqual(upper['upper_bound_exclusive'],'True')
        self.assertEqual(upper['approximate_value_m'],'');self.assertEqual(upper['range_m'],'')
        row=rows['ngcuc-azminuddin-2022-140e-core']
        self.assertEqual(json.loads(row['climatology_period']),{'start_month':'1994-01','end_month':'2015-12'})
        old=rows['cainzos-2023-t02-row-45-transport-depth-extent']
        self.assertEqual(old['range_m'],'[0,937]');self.assertEqual(old['section_window_start'],'1994-04-01')


if __name__=='__main__':unittest.main()
