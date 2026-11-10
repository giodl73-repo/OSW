"""Check inclusive reach, regional flow bands and separately defined cores/jets."""
import copy
import csv
import io
import json
import unittest
import xml.etree.ElementTree as ET
import build_current_depth_register_v8 as previous
import build_current_depth_register_v9 as depth


class EquatorialDepthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=depth.build();cls.new=cls.data['evidence'][107:]
        cls.rows={r['id']:r for r in cls.new}
        cls.ids={r['entity_id'] for r in cls.data['records']}
        cls.metrics=json.loads((depth.ROOT/depth.RULES).read_bytes())['metric_types']

    def validate(self,row):
        depth.validate_reference(row,self.ids,self.metrics);depth.validate_context(row)

    def test_full_inventory_and_prior_107_references_preserved(self):
        prior=previous.build()
        self.assertEqual(self.data['evidence'][:107],prior['evidence'])
        self.assertEqual({r['entity_id'] for r in self.data['records']},{r['entity_id'] for r in prior['records']})
        self.assertEqual(self.data['counts'],{'identities':111,'depth_references':119,'identities_with_scoped_depth_reference':47,'identities_not_yet_assessed':64,'whole_route_depth_profiles':0,'volume_estimates':0})

    def test_at_least_400_is_inclusive_not_point_bottom_or_strict_bound(self):
        original=self.rows['atlantic-secc-bourles-1999-reach']
        self.assertEqual(original['lower_bound_m'],400);self.assertEqual(original['lower_bound_operator'],'>=')
        self.assertFalse(original['lower_bound_exclusive']);self.assertIsNone(original['approximate_value_m']);self.assertIsNone(original['lower_boundary_m'])
        for field,value in [('lower_bound_exclusive',True),('lower_bound_operator','>'),('lower_bound_operator',None),('approximate_value_m',400),('range_m',[0,400]),('lower_boundary_m',400)]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)
        prior=next(r for r in self.data['evidence'] if r['id']=='ngcuc-spray-southern-track-below1000')
        self.assertTrue(prior['lower_bound_exclusive']);self.assertEqual(prior['lower_bound_m'],1000)

    def test_bourles_local_core_depths_and_march_scope_retained(self):
        for tag,value in [('shallow-core',40),('deep-core',240)]:
            row=self.rows['atlantic-secc-bourles-1999-'+tag]
            self.assertEqual(row['metric'],'core_depth');self.assertEqual(row['approximate_value_m'],value)
            self.assertEqual(row['section_sampling_month'],'1994-03');self.assertEqual(row['section_latitude_band_degrees_north'],[-8,-6])
        original=self.rows['atlantic-necc-bourles-1999-march-core']
        self.assertEqual(original['approximate_value_m'],60)
        for field,value in [('entity_id','current:north-equatorial-countercurrent'),('section_sampling_month','1994-01'),('core_definition',{'kind':'salinity_maximum'})]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_pacific_upper_boundaries_preserve_three_jets_and_argo_method(self):
        path=depth.ROOT/'research/source-data/li-neuc-2018/journal-article.xml'
        paragraphs=[''.join(p.itertext()) for p in ET.parse(path).getroot().findall('.//p')]
        original=next(p for p in paragraphs if p.startswith('To further investigate'))
        self.assertIn('upper boundaries',original)
        self.assertIn('300, 450, and 600',original)
        for jet,value in [('NEUCS',300),('NEUCM',450),('NEUCN',600)]:
            row=self.rows['pacific-neuc-li-2018-'+jet.lower()+'-upper-boundary']
            self.assertEqual(row['metric'],'upper_flow_boundary_depth');self.assertEqual(row['approximate_value_m'],value)
            self.assertEqual(row['climatology_years'],[2004,2014]);self.assertIsNone(row['lower_boundary_m'])
            for field,newvalue in [('reference_dataset','LICOMH'),('velocity_reconstruction','direct_ADCP'),('source_jet','all_jets'),('entity_id','current:north-equatorial-undercurrent')]:
                changed=copy.deepcopy(row);changed[field]=newvalue
                with self.assertRaises(ValueError):self.validate(changed)

    def test_atlantic_setting_bands_and_western_euc_core_not_uniform_fields(self):
        for tag,band in [('necc',[0,100]),('neuc',[100,300])]:
            row=self.rows['atlantic-'+tag+'-sivkov-2021-setting-band']
            self.assertEqual(row['range_m'],band);self.assertEqual(row['evidence_kind'],'published_literature_synthesis')
            changed=copy.deepcopy(row);changed['section_sampling_month']='2000-07'
            with self.assertRaises(ValueError):self.validate(changed)
        row=self.rows['atlantic-euc-philander-2001-western-core']
        self.assertEqual(row['approximate_value_m'],100);self.assertIsNone(row['annual_range_m'])
        gaps={r['entity_id'] for r in self.data['records'] if not r['depth_reference_ids']}
        self.assertIn('current:equatorial-undercurrent',gaps)

    def test_threshold_core_and_thermohaline_core_are_separate_kinds(self):
        threshold=self.rows['pacific-secc-rotschi-1972-threshold-reach'];property_core=self.rows['pgw-pous-2004-gogp99-thermohaline-core']
        self.assertEqual(threshold['approximate_value_m'],300);self.assertEqual(threshold['core_definition']['operator'],'>')
        self.assertEqual(property_core['approximate_value_m'],220);self.assertEqual(property_core['core_definition']['kind'],'thermohaline_maxima')
        for original,field,value in [(threshold,'metric','lower_flow_boundary_depth'),(property_core,'core_definition',{'kind':'maximum_eastward_velocity'}),(property_core,'window_role','exact_core_occupation')]:
            row=copy.deepcopy(original);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)

    def test_no_numeric_uncertainty_thickness_volumes_or_playback_inferred(self):
        for field,value in [('uncertainty_m',8),('thickness_m',400),('annual_range_m',[40,400]),('volume_eligible',True),('physical_state_join_eligible',True),('seasonal_playback_eligible',True),('same_source_width_reference_id','unreviewed-width'),('independent_observation_count_claimed',True)]:
            row=copy.deepcopy(self.new[0]);row[field]=value
            with self.assertRaises(ValueError):self.validate(row)
        for row in self.new:self.validate(row)

    def test_raw_source_facts_and_json_csv_reproduce_inclusive_semantics(self):
        source=json.loads((depth.ROOT/depth.SOURCE).read_bytes())
        self.assertEqual(len(self.new),12);self.assertEqual(len({r['entity_id'] for r in self.new}),7)
        for row in self.new:
            raw=source['references'][int(row['source_pointer'].split('/')[-1])]
            self.assertEqual(raw,{k:row[k] for k in raw})
        self.assertEqual(json.loads((depth.ROOT/depth.OUTPUT).read_bytes()),self.data)
        self.assertEqual((depth.ROOT/depth.CSV).read_bytes(),depth.csv_bytes(self.data))
        rows={r['id']:r for r in csv.DictReader(io.StringIO(depth.csv_bytes(self.data).decode('utf8')))}
        row=rows['atlantic-secc-bourles-1999-reach']
        self.assertEqual(row['lower_bound_operator'],'>=');self.assertEqual(row['lower_bound_exclusive'],'False');self.assertEqual(row['approximate_value_m'],'')
        self.assertEqual(rows['pacific-neuc-li-2018-neucs-upper-boundary']['source_jet'],'NEUCS')


if __name__=='__main__':unittest.main()
