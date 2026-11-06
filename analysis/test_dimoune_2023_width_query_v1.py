"""Bounded semantic admission tests; no installed packet or index access."""
import copy
import unittest
from unittest.mock import patch
import dimoune_2023_width_query_v1 as query

class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.contract=query.build_contract()
        self.collections={name:[] for name in self.contract['parent_collection_counts']}
        self.collections['sources']=copy.deepcopy(self.contract['prior_source_inventory'])
        for owner,prior in self.contract['prior_owners'].items():
            for name in ('objects','entities'):
                self.collections[name].extend(copy.deepcopy(prior[name]))
            self.collections['widths'].extend(copy.deepcopy(prior['widths']))
        self.contract['parent_collection_counts']={n:len(r) for n,r in self.collections.items()}
        self.manifest={'input_sha256':{},'unrelated':{'preserve':True}}

    def apply(self):
        return query.apply_verified(self.collections,self.manifest,self.contract,
            parent_logical_sha256=query.PARENT,contract_sha256=query.digest(self.contract))

    def test_exact_additions_preserve_measurements_and_family(self):
        original=copy.deepcopy(self.collections);manifest=copy.deepcopy(self.manifest)
        after,updated=self.apply()
        self.assertEqual(self.collections,original);self.assertEqual(self.manifest,manifest)
        self.assertEqual(after['widths'][:len(original['widths'])],original['widths'])
        self.assertEqual(len(after['widths'])-len(original['widths']),6)
        self.assertEqual(len(after['sources'])-len(original['sources']),1)
        for name in original:
            if name not in ('widths','sources','objects'):self.assertEqual(after[name],original[name])
        family='current:south-equatorial'
        self.assertEqual(next(r for r in after['objects'] if r['id']==family),original['objects'][-1])
        self.assertFalse(any(query.owns(r,family) for r in after['widths']))
        self.assertEqual(updated['unrelated'],manifest['unrelated'])

    def test_basin_specific_width_counts_and_source_only_updates(self):
        after,_=self.apply();objects={r['id']:r for r in after['objects']}
        self.assertEqual(objects['current:atlantic-south-equatorial']['capabilities']['scoped_width'],4)
        self.assertEqual(objects['current:north-brazil']['capabilities']['scoped_width'],4)
        self.assertEqual(objects['current:guiana']['capabilities']['scoped_width'],1)
        self.assertEqual(objects['current:atlantic-north-equatorial-countercurrent']['capabilities']['scoped_width'],2)
        for owner in query.OWNERS:self.assertIn(self.contract['new_source']['id'],objects[owner]['source_ids'])

    def test_changed_prior_width_refused_atomically(self):
        self.collections['widths'][0]['approximate_width_km']=999
        original=copy.deepcopy(self.collections)
        with self.assertRaisesRegex(ValueError,'Prior widths changed'):self.apply()
        self.assertEqual(self.collections,original)

    def test_collision_and_reapplication_refused(self):
        self.collections['claims'].append({'id':self.contract['width_records'][0]['id']})
        self.contract['parent_collection_counts']['claims']=1
        with self.assertRaisesRegex(ValueError,'collision'):self.apply()
        self.collections['claims'].clear();self.contract['parent_collection_counts']['claims']=0
        self.manifest[query.KEY]={}
        with self.assertRaisesRegex(ValueError,'unapplied'):self.apply()

    def test_historical_pin_rebinding_refused(self):
        path=next(iter(self.contract['input_sha256']));self.manifest['input_sha256'][path]='0'*64
        with self.assertRaisesRegex(ValueError,'Historical input'):self.apply()

    def test_source_discrepancies_and_unknowns_survive(self):
        after,_=self.apply();new=after['widths'][-6:]
        self.assertEqual(sum(bool(r['source_discrepancy_note']) for r in new),3)
        for row in new:
            self.assertIn(row['mean_section_context']['section_axis_kind']+' section width',row['range_interpretation'])
            self.assertIsNone(row['annual_width_range_km']);self.assertIsNone(row['numerical_width_uncertainty_km'])
            self.assertIsNone(row['section_geometry']);self.assertFalse(row['seasonal_playback_eligible'])
            self.assertFalse(row['whole_current_representative']);self.assertFalse(row['width_rank_eligible'])
            self.assertFalse(row['independent_new_observation'])
            self.assertEqual(row['mean_section_context']['averaging_period_months'],{'start':'1993-01','end':'2017-12'})

    def test_frozen_contract_reproduces(self):
        self.assertEqual((query.ROOT/query.FILE).read_bytes(),query.encoded(query.build_contract()))

    def test_template_orientation_contradiction_refused(self):
        original_read=query.read;prepared=original_read(query.PREPARED)
        row=next(r for r in prepared['new_width_records'] if r['mean_section_context']['section_axis_kind']=='meridional')
        row['range_interpretation']=row['range_interpretation'].replace('meridional','oblique')
        with patch.object(query,'read',side_effect=lambda path:prepared if path==query.PREPARED else original_read(path)):
            with self.assertRaisesRegex(ValueError,'orientation and scope description disagree'):query.build_contract()

    def test_orientation_correction_preserves_every_other_record_field(self):
        old=query.read('research/dimoune-2023-section-width-admission-prepared-v1.json')['new_width_records']
        new=query.read(query.PREPARED)['new_width_records'];changed=[]
        self.assertEqual([r['id'] for r in old],[r['id'] for r in new])
        for before,after in zip(old,new):
            self.assertEqual({k:v for k,v in before.items() if k!='range_interpretation'},
                             {k:v for k,v in after.items() if k!='range_interpretation'})
            if before['range_interpretation']!=after['range_interpretation']:
                changed.append(after['mean_section_context']['source_flow_label'])
        self.assertEqual(changed,['nSEC5','nSEC6','cSEC6'])

if __name__=='__main__':unittest.main()
