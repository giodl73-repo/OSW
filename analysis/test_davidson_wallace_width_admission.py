"""Atomic delivery and source-scope checks on small synthetic parent records."""
import copy
import json
import unittest
from unittest.mock import patch

import davidson_wallace_width_admission as a


def baseline(document):
    entity=copy.deepcopy(document['accepted_entity']);source=entity['source_id']
    old_width={'id':'davidson-historical-winter-width','current_id':'davidson',
               'approximate_width_km':64,'source_id':source,'source_publication_year':1978}
    owner={'id':a.ENTITY,'type':'named_current','source_ids':[source],'linked_source_count':1,
           'width_ids':[old_width['id']],'evidence_links':[],
           'capabilities':{'scoped_width':1,'width_samples':3,'time_samples':13,'geometry':1},
           'width_sample_ids':['sample:prior'],'latest_observation_date':None,
           'published_length_km':4321,'length_rank':4,'map_features':[{'sentinel':'keep prior geometry'}],
           'seasonal_playback_eligible':True,'recorded_claims':1,
           'section_fingerprints':{'claims':'prior','measurements':'prior','routes_geometry':'keep'},
           'fingerprint':'prior','claim_review_counts':{'verified':1}}
    return {'objects':[owner,{'id':'current:other','fingerprint':'keep'}],
            'entities':[entity],'sources':[{'id':source,'label':'prior source'}],
            'widths':[old_width],'claims':[{'id':'claim:prior','subject_id':a.ENTITY,
                                          'source_id':source,'review_status':'verified'}],
            'current_measurement_admissions':[{'id':'admission:prior'}],
            'measurements':[{'id':'measurement:prior','entity_id':a.ENTITY,'value':4321,'source_id':source}],
            'geometries':[{'id':'geometry:prior','entity_id':a.ENTITY,'source_id':source}],
            'media':[],'reference_routes':[],
            'width_samples':[{'id':'sample:prior','current_id':'davidson','width_km':23}],
            'length_ranks':[{'id':'rank:prior','current_id':'davidson','rank':4}]}


class DeliveryChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.document=a.build_contract()

    def test_atomic_six_record_preparation_preserves_prior_physical_data(self):
        parent=baseline(self.document);before=copy.deepcopy(parent)
        staged,receipt=a.prepare(parent,self.document)
        self.assertEqual(parent,before)
        self.assertEqual(receipt['added_rows'],{'sources':3,'widths':1,'claims':1,'current_measurement_admissions':1})
        self.assertIs(staged['objects'][1],parent['objects'][1])
        self.assertIs(staged['widths'][0],parent['widths'][0])
        self.assertEqual(staged['widths'][0]['approximate_width_km'],64)
        for name in ['entities','measurements','geometries','media','reference_routes','width_samples','length_ranks']:
            self.assertIs(staged[name],parent[name],name)
        old,new=parent['objects'][0],staged['objects'][0]
        self.assertEqual(new['width_ids'],old['width_ids']+[a.WIDTH])
        self.assertEqual(new['capabilities']['scoped_width'],2)
        for key in ['width_samples','time_samples','geometry']:
            self.assertEqual(new['capabilities'][key],old['capabilities'][key])
        for key in ['latest_observation_date','published_length_km','length_rank','map_features','seasonal_playback_eligible','width_sample_ids']:
            self.assertEqual(new[key],old[key],key)
        self.assertEqual(new['linked_source_count'],len(new['source_ids']))
        self.assertEqual(set(new['source_ids']),{old['source_ids'][0],a.PAPER,a.METHOD,a.UNIT})
        self.assertEqual(new['recorded_claims'],2)
        self.assertEqual(new['section_fingerprints']['routes_geometry'],'keep')
        self.assertEqual(staged['claims'][-1]['review_fingerprint'],a.review_fingerprint(staged['claims'][-1]))

    def test_real_contract_preserves_scope_and_source_grade(self):
        row=self.document['width_record'];claim=self.document['claim']
        self.assertEqual((row['source_reported_value'],row['source_unit_label'],row['normalized_width_km_decimal'],row['approximate_width_km']),
                         (35,'NM','64.82',65))
        self.assertEqual(row['depth_average_interval_m'],[27,59])
        self.assertIsNone(row['exact_occupation_date'])
        self.assertIsNone(row['source_publication_year'])
        self.assertIsNone(row['calendar_months'])
        self.assertEqual(claim['observation_window'],['2008-01-23','2008-01-30'])
        for key in ['annual_width_range_km','whole_current_width_km','uncertainty_km','geographic_current_edges','section_geometry']:
            self.assertIsNone(row[key],key)
        for key in ['peer_review_verified','seasonal_playback_eligible','geographic_width_bar_eligible','width_rank_eligible','independent_width_samples_admitted']:
            self.assertIs(row[key],False,key)

    def test_quantity_date_provenance_and_scope_mutations_reject_atomically(self):
        mutations=[('width_record','approximate_width_km',64.82),
                   ('width_record','annual_width_range_km',[64,65]),
                   ('width_record','exact_occupation_date','2008-01-30'),
                   ('width_record','geographic_current_edges',[[0,0],[1,1]]),
                   ('width_record','peer_review_verified',True),
                   ('width_record','source_id','source:other'),
                   ('claim','source_publication_year',2008)]
        for section,key,value in mutations:
            document=copy.deepcopy(self.document);document[section][key]=value
            parent=baseline(self.document);before=copy.deepcopy(parent)
            with self.subTest(section=section,key=key),self.assertRaises(ValueError):a.prepare(parent,document)
            self.assertEqual(parent,before)

    def test_missing_or_duplicate_identity_and_unresolved_old_provenance_reject(self):
        for mode in ['missing_owner','duplicate_owner','duplicate_entity','wrong_owner_type','missing_source','wrong_width_refs']:
            parent=baseline(self.document)
            if mode=='missing_owner':parent['objects'].pop(0)
            elif mode=='duplicate_owner':parent['objects'].append(copy.deepcopy(parent['objects'][0]))
            elif mode=='duplicate_entity':parent['entities']*=2
            elif mode=='wrong_owner_type':parent['objects'][0]['type']='named_eddy'
            elif mode=='missing_source':parent['sources']=[]
            else:parent['objects'][0]['width_ids']=[]
            before=copy.deepcopy(parent)
            with self.subTest(mode=mode),self.assertRaises(ValueError):a.prepare(parent,self.document)
            self.assertEqual(parent,before)

    def test_duplicate_delivery_or_changed_shared_standard_cannot_erase_rows(self):
        parent=baseline(self.document);staged,_=a.prepare(parent,self.document)
        before=copy.deepcopy(staged)
        with self.assertRaises(ValueError):a.prepare(staged,self.document)
        self.assertEqual(staged,before)
        parent=baseline(self.document)
        standard=copy.deepcopy(self.document['source_records'][2]);standard['definition_exact_m']=1609
        parent['sources'].append(standard);before=copy.deepcopy(parent)
        with self.assertRaises(ValueError):a.prepare(parent,self.document)
        self.assertEqual(parent,before)

    def test_identical_shared_standard_is_reused_without_duplicate_reference(self):
        parent=baseline(self.document);parent['sources'].append(copy.deepcopy(self.document['source_records'][2]))
        staged,receipt=a.prepare(parent,self.document)
        self.assertEqual(receipt['added_rows']['sources'],2)
        self.assertEqual(sum(r['id']==a.UNIT for r in staged['sources']),1)
        self.assertEqual(staged['objects'][0]['linked_source_count'],4)

    def test_changed_source_outputs_proof_or_frozen_dependencies_reject(self):
        original=a.read
        for path in [a.REPORT,a.FIGURE,a.PROOF,'plans/published-prose-dimension-admission-protocol-v1.md']:
            def changed(relative):return original(relative)+(b' ' if relative==path else b'')
            with self.subTest(path=path),patch.object(a,'read',side_effect=changed),self.assertRaises(ValueError):
                a.build_contract()


if __name__=='__main__':unittest.main()
