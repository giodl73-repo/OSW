import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import equatorial_basin_identity_query_v2 as m


class BasinIdentityContract(unittest.TestCase):
    def small_rehearsal(self):
        """Only authoritative selected families/sources plus unrelated sentinels.

        The application unit tests replace the trusted contract constructor and
        its saved file with a reduced inventory. They never load the installed
        packet or pretend these sentinels are original scientific observations.
        Separate tests exercise the actual frozen contract and recomputation.
        """
        contract=m.build_contract();families=contract['prior_family_records']
        rows={'entities':[],'objects':[],'names':[],
            'sources':copy.deepcopy(contract['prior_glossary_sources']),
            'length_assessments':[{'id':'prior:length','value':23}],
            'current_identity_admissions':[{'id':'prior:admission','geometry':None}],
            'route_decisions':[{'id':'prior:route','construction_status':'unchanged'}],
            'widths':[{'id':'prior:width','current_id':'other','value':42,'nested':{'keep':[1,2]}}]}
        for prior in families.values():
            for name in ['entities','objects','names']:rows[name].extend(copy.deepcopy(prior[name]))
        for name in ['entities','objects','names','sources']:rows[name].append({'id':'sentinel:'+name,'label':'Unrelated sentinel'})
        contract['prior_collection_counts']={k:len(v) for k,v in rows.items()}
        contract['after_collection_counts']={**contract['prior_collection_counts'],
            **{key:contract['prior_collection_counts'].get(key,0)+len(value) for key,value in contract['additions'].items()}}
        return contract,rows

    def apply_small(self,rows,manifest,contract):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/m.FILE;p.parent.mkdir(parents=True);p.write_bytes(m.encoded(contract))
            with patch.object(m,'ROOT',Path(folder)),patch.object(m,'build_contract',return_value=copy.deepcopy(contract)):
                m.prepare(rows,manifest,contract,parent_logical_sha256=m.PARENT)

    def test_actual_contract_rebuild_counts_source_reuse_and_measurement_gaps(self):
        c=m.build_contract();self.assertEqual(m.encoded(c),(m.ROOT/m.FILE).read_bytes())
        self.assertEqual(c['accepted_current_identities_after'],111)
        self.assertEqual(c['prior_collection_counts'],m.read(m.RESULT)['collection_counts'])
        self.assertEqual(c['new_publication_sources'],0);self.assertNotIn('sources',c['additions'])
        self.assertEqual(c['after_collection_counts']['entities'],329)
        self.assertEqual(c['after_collection_counts']['objects'],251)
        self.assertEqual(c['after_collection_counts']['length_assessments'],111)
        self.assertEqual(c['after_collection_counts']['widths'],178)
        self.assertEqual(c['after_collection_counts']['width_samples'],463)
        self.assertEqual(c['after_collection_counts']['reference_routes'],83)
        for name,rows in c['additions'].items():self.assertEqual(len(rows),5,name)
        for r in c['additions']['objects']:
            self.assertEqual(r['source_ids'],[m.SOURCE]);self.assertTrue(all(v==0 for v in r['capabilities'].values()))
            for key in ['map_features','width_ids','measurement_ids','series','state_evidence']:self.assertEqual(r[key],[])
            self.assertIsNone(r['published_length_km']);self.assertIsNone(r['latest_observation_date'])

    def test_addition_is_atomic_and_preserves_all_older_rows_and_manifest_namespaces(self):
        c,rows=self.small_rehearsal();old=copy.deepcopy(rows)
        manifest={'historical':{'keep':[1,2]},'input_sha256':{'older.json':'historical-pin'}};before=copy.deepcopy(manifest)
        self.apply_small(rows,manifest,c)
        for name,prior in old.items():
            self.assertEqual(rows[name][:len(prior)],prior)
            self.assertEqual(rows[name][len(prior):],c['additions'].get(name,[]))
        self.assertEqual(rows['current_basin_memberships'],c['additions']['current_basin_memberships'])
        self.assertEqual(manifest['historical'],before['historical'])
        self.assertEqual(manifest['input_sha256']['older.json'],'historical-pin')
        self.assertEqual(manifest[m.KEY]['new_measurements'],0)

    def test_existing_exact_identity_alias_and_partial_object_refused_atomically(self):
        for collection,record in [('entities',{'id':'current:'+m.EXPECTED[0],'label':'Other'}),
                ('names',{'id':'name:collision','entity_id':'current:other','label':'Atlantic North Equatorial Current'}),
                ('objects',{'id':'current:'+m.EXPECTED[0],'label':'Other'})]:
            c,rows=self.small_rehearsal();rows[collection].append(record)
            c['prior_collection_counts'][collection]+=1;before=copy.deepcopy(rows);manifest={'keep':True}
            with self.assertRaises(ValueError):self.apply_small(rows,manifest,c)
            self.assertEqual(rows,before);self.assertEqual(manifest,{'keep':True})

    def test_changed_audited_family_source_or_duplicate_id_refused_atomically(self):
        for mutation in ['family','source','duplicate','count']:
            c,rows=self.small_rehearsal()
            if mutation=='family':rows['entities'][0]['label']='Changed family'
            elif mutation=='source':rows['sources'][0]['record_count']=999
            elif mutation=='duplicate':rows['widths'].append(copy.deepcopy(rows['widths'][0]));c['prior_collection_counts']['widths']+=1
            else:rows['widths'].append({'id':'unexpected:width'})
            before=copy.deepcopy(rows);manifest={'keep':True}
            with self.assertRaises(ValueError):self.apply_small(rows,manifest,c)
            self.assertEqual(rows,before);self.assertEqual(manifest,{'keep':True})

    def test_historical_input_rebinding_and_repeated_application_refused(self):
        c,rows=self.small_rehearsal();before=copy.deepcopy(rows)
        manifest={'input_sha256':{m.FACTS:'wrong'}};old=copy.deepcopy(manifest)
        with self.assertRaises(ValueError):self.apply_small(rows,manifest,c)
        self.assertEqual(rows,before);self.assertEqual(manifest,old)
        for key in ['receipt','collection']:
            c,rows=self.small_rehearsal();manifest={m.KEY:{}} if key=='receipt' else {}
            if key=='collection':rows['current_basin_memberships']=[]
            with self.assertRaises(ValueError):self.apply_small(rows,manifest,c)

    def test_actual_wrong_parent_or_modified_measurement_contract_refused(self):
        c=m.build_contract();rows={};manifest={'keep':True}
        with self.assertRaises(ValueError):m.prepare(rows,manifest,c,parent_logical_sha256='wrong')
        c['additions']['objects'][0]['published_length_km']=1234
        with self.assertRaises(ValueError):m.prepare(rows,manifest,c,parent_logical_sha256=m.PARENT)
        self.assertEqual(rows,{});self.assertEqual(manifest,{'keep':True})

    def test_rewritten_contract_file_cannot_promote_measurements_coherently(self):
        c=m.build_contract();c['additions']['objects'][0]['capabilities']['scoped_width']=1
        actual_root=m.ROOT
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/m.FILE;p.parent.mkdir(parents=True);p.write_bytes(m.encoded(c))
            def read(path):return json.loads((actual_root/path).read_bytes())
            def sha(path):
                import hashlib
                return hashlib.sha256(((Path(folder) if path==m.FILE else actual_root)/path).read_bytes()).hexdigest()
            with patch.object(m,'ROOT',Path(folder)),patch.object(m,'read',side_effect=read),patch.object(m,'sha',side_effect=sha):
                with self.assertRaisesRegex(ValueError,'Frozen unmodified contract'):m.prepare({}, {}, c,parent_logical_sha256=m.PARENT)

    def test_family_links_branch_charts_and_no_indian_nec_are_explicit(self):
        c=m.build_contract();members=c['additions']['current_basin_memberships']
        self.assertEqual({r['current_id'] for r in members},set(m.EXPECTED))
        self.assertTrue(all(not r['membership_is_physical_connection'] and not r['measurements_inherited'] and r['geometry'] is None for r in members))
        self.assertEqual(sum(r['family_entity_id']=='current:north-equatorial' for r in members),2)
        self.assertEqual(sum(r['family_entity_id']=='current:south-equatorial' for r in members),3)
        for owner in c['additions']['objects']:
            short=owner['id'].removeprefix('current:')
            branch=[r for r in owner['evidence_links'] if 'bifurcation' in r['label']]
            self.assertEqual(len(branch),int(short in m.BRANCH_SOURCES))
            if branch:self.assertIn('not current dimensions',branch[0]['label'])

    def test_rebound_source_facts_refused_before_admission(self):
        original=m.sha
        with patch.object(m,'sha',side_effect=lambda p:'changed' if p==m.FACTS else original(p)):
            with self.assertRaisesRegex(ValueError,'Frozen five-member installed audit'):m.build_contract()



    def test_route_rows_match_existing_planning_validator_contract(self):
        c=m.build_contract();plans={r['current_id']:r for r in m.read(m.PLANNING)['entries']}
        for row in c['additions']['route_decisions']:
            source=plans[row['current_id']]
            self.assertEqual(row['source_decision'],source)
            self.assertEqual(row['source_catalog_file'],m.PLANNING)
            self.assertEqual(row['source_catalog_sha256'],m.sha(m.PLANNING))
            self.assertEqual(row['status'],'editorial_planning_crosswalk_not_scientific_classification_approval')
            self.assertEqual(row['candidate_count'],len(source['candidate_ids']))
            for key,other in [('current_id','current_id'),('label','name'),('strategy_id','route_strategy_id'),
                    ('strategy_label','route_strategy_label'),('construction_status','reference_path_decision'),
                    ('route_ids','candidate_ids'),('next_action','next_action'),('scope','existing_scope'),
                    ('status','planning_status'),('source_url','name_source_url')]:
                self.assertEqual(row[key],source[other])

    def test_v2_repairs_only_route_bindings_and_typed_distinction_shape(self):
        old=m.read('research/equatorial-basin-identity-query-contract-v1.json');new=m.build_contract()
        for collection in new['additions']:
            if collection not in ['route_decisions','current_identity_admissions']:
                self.assertEqual(old['additions'][collection],new['additions'][collection],collection)
        for before,after in zip(old['additions']['current_identity_admissions'],new['additions']['current_identity_admissions']):
            self.assertEqual({k:v for k,v in before.items() if k not in ['route_planning_decision','distinguished_from']},
                {k:v for k,v in after.items() if k not in ['route_planning_decision','distinguished_from','excluded_feature_classes']})
            self.assertEqual(after['distinguished_from'][0]['entity_id'],before['distinguished_from'][0])
            self.assertEqual(after['excluded_feature_classes'],before['distinguished_from'][1:])
        self.assertEqual(old['after_collection_counts'],new['after_collection_counts'])


if __name__=='__main__':unittest.main()
