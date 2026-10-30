import copy
import unittest
from xml.etree import ElementTree
import current_core_gap_followup_prepare_v1 as prep


class PreparationTests(unittest.TestCase):
    def test_separate_primary_reach_and_secondary_width_without_invented_precision(self):
        value=prep.prepare();reach=value['regional_length_records'][0];width=value['width_claim_records'][0]
        self.assertEqual(reach['reported_length_interval_km'],[110,120])
        self.assertIsNone(reach['representative_length_km'])
        self.assertFalse(reach['rank_eligible'])
        self.assertEqual(width['approximate_width_km'],650)
        self.assertEqual(width['measurement_type'],'literature_cited_approximate_regional_width_claim')
        self.assertFalse(width['underlying_work_is_verified_claim_source'])
        self.assertIsNone(width['observation_period'])
        self.assertIsNone(width['independent_observation_count'])
        self.assertEqual(value['named_inventory_candidate']['numeric_records_admitted'],0)
        self.assertEqual(len(value['publication_records']),2)
        self.assertFalse(value['installed'])

    def test_reject_annual_error_depth_geometry_and_wrong_owner_transfer(self):
        for field,wrong in [('annual_length_range_km',[110,130]),('numerical_length_uncertainty_km',5),('geometry',{'type':'LineString'}),('fixed_depth_bounds_m',[0,600]),('whole_current_rank_eligible',True),('synoptic_snapshot',True)]:
            p=prep.read(prep.PETERS);p['candidate'][field]=wrong
            with self.assertRaises(ValueError,msg=field):prep.prepare(peters=p)
        p=prep.read(prep.PETERS);p['entity_id']='current:persian-gulf-outflow'
        with self.assertRaises(ValueError):prep.prepare(peters=p)

    def test_reject_cited_width_as_new_observation_or_cruise_dated_measurement(self):
        for field,wrong in [('observation_period',{'from':'2008-10-08'}),('width_sampling_depth_m',[0,1000]),('paired_edges',[-10,-16]),('numerical_width_uncertainty_km',50),('annual_width_range_km',[600,700]),('measurement_type','observed_width'),('independent_observation_count',1),('width_rank_eligible',True)]:
            a=prep.read(prep.ASCLME);a['candidate_claim'][field]=wrong
            with self.assertRaises(ValueError,msg=field):prep.prepare(asclme=a)

    def test_reject_source_version_mixing_and_unreviewed_original_upgrade(self):
        a=prep.read(prep.ASCLME);a['source_report']['pages']=48
        with self.assertRaises(ValueError):prep.prepare(asclme=a)
        a=prep.read(prep.ASCLME);a['underlying_work_candidate']['original_full_text_reviewed']=True
        with self.assertRaises(ValueError):prep.prepare(asclme=a)
        n=prep.read(prep.NILSEN);n['publication']['source_figures_visually_reviewed']=True
        with self.assertRaises(ValueError):prep.prepare(nilsen=n)

    def test_inputs_unmodified_and_figure_has_separate_scales_and_accessible_limits(self):
        p=prep.read(prep.PETERS);before=copy.deepcopy(p)
        value=prep.prepare(peters=p);self.assertEqual(p,before)
        raw=prep.figure(value);svg=ElementTree.fromstring(raw)
        self.assertEqual(svg.attrib['role'],'img')
        self.assertIn(b'150 km',raw);self.assertIn(b'700 km',raw)
        self.assertIn(b'Separate scales',raw);self.assertIn(b'exact reach occupation dates unknown',raw)
        value['width_claim_records'][0]['approximate_width_km']=700
        with self.assertRaises(ValueError):prep.figure(value)


if __name__=='__main__':unittest.main()
