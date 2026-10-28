import copy
import json
import unittest
import eac_mean_core_runtime_v1 as m
from test_eac_mean_core_query_v1 import fixture

def pair():
    contract=m.query.build_contract();collections,manifest=fixture(contract)
    parent={'schema':'osw.query-bundle.v1','manifest':copy.deepcopy(manifest),'collections':dict(collections)}
    m.query.prepare(collections,manifest,contract,parent_logical_sha256=m.query.PARENT)
    audit={'original_sources_verified':633,'original_source_strings_preserved':633,'replaced_source_paths':[],
        'added_source_paths':[m.query.facts.FACTS],'scientific_source_documents_replaced':0}
    manifest[m.index.KEY]=audit;manifest['input_sha256'].update({p:'fixture-index-pin' for p in m.index.INDEX})
    return parent,{'schema':'osw.query-bundle.v1','manifest':manifest,'collections':collections}

class Runtime(unittest.TestCase):
    def test_full_api_comparison_refuses_unrelated_changes_and_missing_scope(self):
        contract=m.query.build_contract()
        dashboard={'entries':[contract['dashboard_before']], 'snapshot_fingerprint':'prior'}
        scene={'kind':'published_mean_core_sections','records':contract['records'],
            'source_file':contract['records'][0]['source_file'],'source_url':contract['new_source']['url'],
            'figure':'figures/eac-kerry-2020-mean-core-dimensions-v2.svg',
            'compact_figure':'figures/eac-kerry-2020-mean-core-dimensions-compact-v2.svg',
            'scope':'model mean, not seasonal ranges','boundary':'-0.05 m/s','definition':'geometry of mean',
            'labeling_note':'Forster source latitude discrepancy'}
        for name in ['dashboard','atlas','seasons']:
            old={'bundle_sha256':'a'*64,'prior_science':{'dated_widths':[1,2]}}
            if name=='dashboard':old['snapshot_json']=json.dumps(dashboard)
            if name=='atlas':old['sources_json']={'research/ocean-motion-dashboard.json':json.dumps(dashboard),'other':'unchanged'}
            new=copy.deepcopy(old);new['bundle_sha256']='b'*64
            if name=='dashboard':new['snapshot_json']=json.dumps(m.dashboard_document(dashboard))
            else:new['mean_core_section_scenes']={m.query.CURRENT:copy.deepcopy(scene)}
            if name=='atlas':new['sources_json']['research/ocean-motion-dashboard.json']=json.dumps(m.dashboard_document(dashboard))
            m.verify_snapshot(name,old,new)
            bad=copy.deepcopy(new);bad['prior_science']['dated_widths'].append(3)
            with self.assertRaises(ValueError):m.verify_snapshot(name,old,bad)
            if name!='dashboard':
                bad=copy.deepcopy(new);del bad['mean_core_section_scenes'][m.query.CURRENT]['boundary']
                with self.assertRaises(ValueError):m.verify_snapshot(name,old,bad)

    def test_only_declared_records_and_namespaces_change(self):
        parent,child=pair();m.verify_collections(parent,child)
        for key in ['widths','reference_routes','entities','unrelated_scientific_table']:
            self.assertIs(parent['collections'][key],child['collections'][key])

    def test_unrelated_science_history_and_added_range_are_refused(self):
        for change in ['width','historical','range']:
            parent,child=pair();child=copy.deepcopy(child)
            if change=='width':child['collections']['widths'][0]['changed']=True
            elif change=='historical':child['manifest']['historical_marker']['keep']=False
            else:child['collections'][m.query.COLLECTION][0]['annual_width_range_km']=[100,200]
            with self.assertRaises(ValueError):m.verify_collections(parent,child)

    def test_dashboard_keeps_all_unrelated_rows_and_source_bytes(self):
        contract=m.query.build_contract();original={'entries':[contract['dashboard_before'],{'id':'other','keep':True}],
            'snapshot_fingerprint':'prior','source_json':'historical bytes'}
        after=m.dashboard_document(original)
        self.assertEqual(after['entries'][0],contract['dashboard_after'])
        self.assertEqual(after['entries'][1],original['entries'][1]);self.assertEqual(after['source_json'],'historical bytes')
        self.assertEqual(original['snapshot_fingerprint'],'prior')

if __name__=='__main__':unittest.main()
