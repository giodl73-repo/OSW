import copy
import unittest
import pacific_nec_nominal_width_query_v1 as m


def fixture(contract):
    identities=contract['prior_records']['identities'];counts=contract['parent_collection_counts'];collections={}
    for name,key in [('objects','object'),('entities','entity')]:
        records=[copy.deepcopy(r[key]) for r in identities.values()]
        collections[name]=records+[{'id':f'fixture:{name}:{i}'} for i in range(counts[name]-len(records))]
    for name in ['widths','reference_routes']:
        collections[name]=[{'id':f'fixture:{name}:{i}','current_id':'fixture-other'} for i in range(counts[name])]
    sources={r['id']:copy.deepcopy(r) for identity in identities.values() for r in identity['owner_sources']}
    collections['sources']=list(sources.values())+[{'id':f'fixture:source:{i}','title':f'Unrelated fixture publication{i}'} for i in range(counts['sources']-len(sources))]
    collections['unrelated_scientific_table']=[{'id':'keep','values':[0,None,1,2]}]
    return collections,{'input_sha256':{'historical:pin':'keep'},'equatorial_basin_identities_v3':{'frozen':'keep'},'other_namespace':{'keep':True}}


class NominalWidthContract(unittest.TestCase):
    def refused(self,collections,manifest,contract,parent=m.PARENT):
        old=copy.deepcopy(collections);before=copy.deepcopy(manifest)
        with self.assertRaises(ValueError):m.prepare(collections,manifest,contract,parent_logical_sha256=parent)
        self.assertEqual(collections,old);self.assertEqual(manifest,before)

    def test_nominal_derived_width_has_no_invented_edges_dates_or_ranges(self):
        c=m.build_contract();w=c['width_record']
        self.assertEqual(w['approximate_width_km'],1000)
        self.assertEqual(w['source_reported_latitude_bounds_deg_north'],[8,17])
        self.assertEqual(w['related_source_context']['latitude_band_deg_north'],[7,17])
        for key in ['source_reported_width_km','width_range_km','annual_width_range_km','numerical_width_uncertainty_km','observed_period','sampling_dates','calendar_months','boundary_rule','edge_operator','paired_edge_coordinates','section_geometry']:self.assertIsNone(w[key],key)
        for key in ['whole_current_representative','flow_normal_width_diagnosed','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','independent_new_observation','source_figure_digitized','is_annual_mean','is_climatology']:self.assertIs(w[key],False,key)
        self.assertEqual(c['new_length_records'],0);self.assertEqual(c['new_independent_observations'],0)
        self.assertEqual(len(c['new_sources']),2)
        self.assertNotIn('10.1002/2016jc012143',[s['doi'] for s in c['new_sources']])

    def test_append_preserves_every_old_row_and_unrelated_collection(self):
        c=m.build_contract();collections,manifest=fixture(c);before=dict(collections);old=copy.deepcopy(collections)
        history=copy.deepcopy(manifest)
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.assertEqual(set(collections),set(before))
        for name in ['entities','reference_routes','unrelated_scientific_table']:self.assertIs(collections[name],before[name])
        self.assertEqual(collections['widths'],old['widths']+[c['width_record']])
        self.assertEqual(collections['sources'],old['sources']+c['new_sources'])
        self.assertEqual(collections['objects'][0],c['final_owner'])
        for i in range(1,len(before['objects'])):self.assertIs(collections['objects'][i],before['objects'][i])
        for key in history:self.assertEqual(manifest[key] if key!='input_sha256' else manifest[key]['historical:pin'],history[key] if key!='input_sha256' else history[key]['historical:pin'])
        self.assertEqual(manifest[m.KEY],m.marker(c))

    def test_only_scoped_width_and_source_capabilities_change(self):
        c=m.build_contract();old=c['dashboard_before'];new=c['final_owner']
        allowed={'width_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links'}
        self.assertEqual(set(old),set(new))
        for key in set(old)-allowed:self.assertEqual(new[key],old[key],key)
        for key,v in old['capabilities'].items():self.assertEqual(new['capabilities'][key],v+(key=='scoped_width'),key)
        for key in set(old['section_fingerprints'])-{'measurements','sources'}:self.assertEqual(new['section_fingerprints'][key],old['section_fingerprints'][key])
        self.assertIsNone(new['latest_observation_date']);self.assertIsNone(new['published_length_km'])
        self.assertEqual(new['vertical_setting'],'unspecified');self.assertEqual(new['linked_source_count'],3)
        self.assertEqual(c['dashboard_after'],new)

    def test_changed_member_or_family_records_refused_before_mutation(self):
        c=m.build_contract()
        for name,index in [('objects',0),('objects',1),('entities',0),('entities',1),('sources',0)]:
            collections,manifest=fixture(c);collections[name][index]['unexpected']=True
            self.refused(collections,manifest,c)

    def test_width_or_route_filed_under_family_or_member_requires_reconciliation(self):
        c=m.build_contract()
        for name in ['widths','reference_routes']:
            for owner in ['pacific-north-equatorial','north-equatorial']:
                collections,manifest=fixture(c);collections[name][0]['current_id']=owner
                self.refused(collections,manifest,c)

    def test_publication_aliases_and_reserved_new_ids_refused(self):
        c=m.build_contract()
        for row in [c['new_sources'][0],c['new_sources'][1],{'id':'by-doi','doi':'https://doi.org/10.5670/OCEANOG.2015.78'},
                {'id':'by-title','title':c['new_sources'][1]['title'].upper()},
                {'id':'by-url','url':'http://www.soest.hawaii.edu/oceanography/bo/Qiu_etal_TOS2015.pdf?tracking=1'}]:
            collections,manifest=fixture(c);collections['sources'][-1]=copy.deepcopy(row)
            self.refused(collections,manifest,c)

    def test_wrong_parent_modified_contract_and_repeat_application_refused(self):
        c=m.build_contract();collections,manifest=fixture(c)
        self.refused(collections,manifest,c,parent='0'*64)
        changed=copy.deepcopy(c);changed['width_record']['annual_width_range_km']=[990,1100]
        self.refused(collections,manifest,changed)
        m.prepare(collections,manifest,c,parent_logical_sha256=m.PARENT)
        self.refused(collections,manifest,c)

    def test_historical_pin_rebinding_and_duplicate_width_id_refused(self):
        c=m.build_contract();collections,manifest=fixture(c);manifest['input_sha256'][m.nominal.FACTS]='previous-pin'
        self.refused(collections,manifest,c)
        collections,manifest=fixture(c);collections['widths'][-1]['id']=m.WIDTH_ID
        self.refused(collections,manifest,c)

    def test_duplicate_ids_and_collection_count_changes_refused(self):
        c=m.build_contract()
        for name in ['objects','entities','widths','reference_routes','sources']:
            collections,manifest=fixture(c);collections[name][-1]=copy.deepcopy(collections[name][0])
            self.refused(collections,manifest,c)
            collections,manifest=fixture(c);collections[name].pop();self.refused(collections,manifest,c)


if __name__=='__main__':unittest.main()
