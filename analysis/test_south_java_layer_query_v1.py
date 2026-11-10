"""Small offline checks of quantity class, identity and atomic append limits."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import south_java_layer_query_v1 as model


class ModelLayerContextTests(unittest.TestCase):
    def setUp(self):
        self.document = model.build_contract()

    def base(self):
        return {
            'objects':[
                {'id':model.TARGET,'type':'named_current','source_ids':['source:prior'],
                 'linked_source_count':1,'capabilities':{'scoped_width':4,'width_samples':8},
                 'evidence_links':[{'label':'Prior evidence','url':'prior.html'}],
                 'section_fingerprints':{'physical_width':'keep-this'},'fingerprint':'prior-fingerprint',
                 'width_ids':['prior-width'],'whole_current_width_km':None,
                 'geometry_ids':['prior-geometry']},
                {'id':'current:other','type':'named_current','fingerprint':'unchanged-other'}],
            'entities':[{'id':model.TARGET,'type':'named_current'},{'id':'current:other','type':'named_current'}],
            'sources':[{'id':'source:prior','kind':'external','title':'Prior source'}],
            'width_measurements':[{'id':'prior-width','current_id':'other','width_km':13}],
            'geometry':[{'id':'prior-geometry','type':'unrelated_existing_geometry'}],
        }

    def rejected_unchanged(self, data, document=None):
        before = copy.deepcopy(data)
        with self.assertRaises(ValueError):
            model.append(data,self.document if document is None else document)
        self.assertEqual(data,before)

    def test_source_values_keep_definition_core_and_cap_distinct(self):
        layers = self.document['collections'][model.LAYERS]
        depth = self.document['collections'][model.DEPTHS]
        self.assertEqual(len(layers),2)
        self.assertEqual([row['lower_depth_m'] for row in layers],[150,1000])
        self.assertEqual([row.get('reported_depth_m') for row in depth],[50,None,400])
        self.assertEqual(depth[1]['depth_cap_m'],100)
        self.assertEqual(depth[1]['velocity_threshold_cm_s'],5)
        self.assertEqual(depth[1]['velocity_threshold_relation'],'greater_than')
        self.assertIsNone(depth[1]['exact_edge_depth_m'])
        self.assertEqual(depth[2]['reported_peak_speed_cm_s'],3)

    def test_undercurrent_is_related_context_without_surface_ownership(self):
        rows = [row for name in model.OWNER_FIELDS for row in self.document['collections'][name]]
        under = [row for row in rows if row['source_feature']=='SJCU']
        self.assertEqual(len(under),2)
        self.assertTrue(all(row['entity_id'] is None and row['related_current_id']==model.TARGET for row in under))
        self.assertEqual(sum(row['entity_id']==model.TARGET for row in rows),3)

    def test_context_is_not_independent_observed_or_physical_dimension_data(self):
        for name in model.OWNER_FIELDS:
            for row in self.document['collections'][name]:
                self.assertFalse(row['is_observation'])
                self.assertEqual(row['independent_observation_count'],0)
                for key in ['physical_width_km','physical_current_thickness_m','physical_annual_depth_range_m',
                            'physical_uncertainty_m','geometry','sample_date']:
                    self.assertIsNone(row[key])
                for key in ['rank_eligible','physical_state_join_eligible','geographic_seasonal_playback_eligible']:
                    self.assertFalse(row[key])
        self.assertTrue(all(value==0 for value in self.document['admission'].values()))

    def test_append_preserves_prior_dimensions_entities_and_other_objects(self):
        data = self.base(); before = copy.deepcopy(data)
        model.append(data,self.document)
        owner = data['objects'][0]
        self.assertEqual(data['objects'][1],before['objects'][1])
        for name in ['entities','width_measurements','geometry']:
            self.assertEqual(data[name],before[name])
        for name in ['width_ids','whole_current_width_km','geometry_ids']:
            self.assertEqual(owner[name],before['objects'][0][name])
        self.assertEqual(owner['capabilities']['scoped_width'],4)
        self.assertEqual(owner['capabilities']['width_samples'],8)
        self.assertEqual(owner['section_fingerprints']['physical_width'],'keep-this')
        self.assertEqual(owner['capabilities']['model_analysis_layers'],1)
        self.assertEqual(owner['capabilities']['model_depth_context'],2)
        self.assertEqual(owner['linked_source_count'],3)
        self.assertEqual(len(owner['evidence_links']),4)
        self.assertEqual(len(data[model.LAYERS]),2)
        self.assertEqual(len(data[model.DEPTHS]),3)

    def test_duplicate_application_is_refused_without_changes(self):
        data = self.base(); model.append(data,self.document)
        self.rejected_unchanged(data)

    def test_existing_owned_model_context_is_preserved_and_counted(self):
        data=self.base(); owner=data['objects'][0]
        owner['model_analysis_layer_ids']=['older-study-layer']; owner['capabilities']['model_analysis_layers']=1
        prior={'id':'older-study-layer','entity_id':model.TARGET,'source_ids':['source:prior'],
               'source_id':'source:prior','method_source_id':'source:prior','study_context':'unchanged'}
        data[model.LAYERS]=[copy.deepcopy(prior)]
        model.append(data,self.document)
        self.assertEqual(data[model.LAYERS][0],prior)
        self.assertEqual(data['objects'][0]['model_analysis_layer_ids'],['older-study-layer',self.document['collections'][model.LAYERS][0]['id']])
        self.assertEqual(data['objects'][0]['capabilities']['model_analysis_layers'],2)

    def test_record_and_source_collisions_are_refused_atomically(self):
        for name in [model.LAYERS,model.DEPTHS,'sources']:
            with self.subTest(collection=name):
                data = self.base()
                data.setdefault(name,[]).append(copy.deepcopy(self.document['collections'][name][0]))
                self.rejected_unchanged(data)

    def test_invalid_prior_provenance_is_refused_atomically(self):
        for change in ['unresolved_source','would_be_repaired_by_append','wrong_count','duplicate_source','bad_count_type']:
            with self.subTest(change=change):
                data = self.base(); owner=data['objects'][0]
                if change=='unresolved_source': owner['source_ids']=['source:missing']
                elif change=='would_be_repaired_by_append': owner['source_ids']=[model.PAPER]
                elif change=='wrong_count': owner['linked_source_count']=9
                elif change=='duplicate_source': owner['source_ids']*=2; owner['linked_source_count']=2
                else: owner['linked_source_count']=True
                self.rejected_unchanged(data)

    def test_missing_or_duplicate_current_or_entity_is_not_an_identity_admission(self):
        for name in ['objects','entities']:
            for mode in ['absent','duplicate']:
                with self.subTest(collection=name,mode=mode):
                    data=self.base()
                    if mode=='absent': data[name]=[row for row in data[name] if row['id']!=model.TARGET]
                    else: data[name].append(copy.deepcopy(data[name][0]))
                    self.rejected_unchanged(data)

    def test_prior_context_references_and_counts_must_resolve(self):
        for name,(field,capability) in model.OWNER_FIELDS.items():
            for mode in ['missing_record','wrong_owner','wrong_count','bool_count']:
                with self.subTest(collection=name,mode=mode):
                    data=self.base(); owner=data['objects'][0]
                    if mode in ['missing_record','wrong_owner']:
                        owner[field]=['old-context']; owner['capabilities'][capability]=1
                        if mode=='wrong_owner': data[name]=[{'id':'old-context','entity_id':'current:other'}]
                    else: owner[field]=[]; owner['capabilities'][capability]=True if mode=='bool_count' else 7
                    self.rejected_unchanged(data)

    def test_duplicate_publication_doi_needs_explicit_reconciliation(self):
        data=self.base()
        data['sources'].append({'id':'source:old-alias','doi':'https://doi.org/10.1029/2006JC003486'})
        self.rejected_unchanged(data)

    def test_json_boolean_number_type_changes_are_not_equal_contracts(self):
        for field,value in [('is_observation',0),('independent_observation_count',False),
                            ('physical_state_join_eligible',0)]:
            with self.subTest(field=field):
                changed=copy.deepcopy(self.document)
                changed['collections'][model.DEPTHS][0][field]=value
                self.rejected_unchanged(self.base(),changed)

    def test_prior_owned_model_rows_need_resolved_provenance(self):
        data=self.base(); owner=data['objects'][0]
        owner['model_analysis_layer_ids']=['old-context']; owner['capabilities']['model_analysis_layers']=1
        data[model.LAYERS]=[{'id':'old-context','entity_id':model.TARGET,
            'source_ids':['source:missing'],'source_id':'source:missing','method_source_id':'source:missing'}]
        self.rejected_unchanged(data)

    def test_changed_quantities_ownership_or_promotions_are_refused(self):
        mutations = [
            lambda doc: doc['collections'][model.LAYERS][0].update(lower_depth_m=200),
            lambda doc: doc['collections'][model.LAYERS][1].update(entity_id=model.TARGET),
            lambda doc: doc['collections'][model.DEPTHS][1].update(exact_edge_depth_m=100),
            lambda doc: doc['collections'][model.DEPTHS][0].update(physical_width_km=150),
            lambda doc: doc['collections'][model.DEPTHS][0].update(physical_current_thickness_m=150),
            lambda doc: doc['collections'][model.DEPTHS][0].update(is_observation=True),
            lambda doc: doc['collections'][model.DEPTHS][0].update(physical_state_join_eligible=True),
            lambda doc: doc['admission'].update(annual_dimension_ranges=1),
        ]
        for index,mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                changed=copy.deepcopy(self.document); mutate(changed)
                self.rejected_unchanged(self.base(),changed)

    def test_changed_source_fact_bytes_are_rejected_before_projection(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); target=root/model.FACTS; target.parent.mkdir(parents=True)
            doc=json.loads((model.ROOT/model.FACTS).read_bytes())
            doc['layer_definitions'][0]['lower_depth_m']=250
            target.write_bytes(model.encoded(doc))
            with self.assertRaisesRegex(ValueError,'Changed reviewed model context'):
                model.build_contract(root)


if __name__=='__main__':
    unittest.main()
