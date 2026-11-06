"""Independent expectations for the two-owner reference/profile packet extension."""
import copy
import hashlib
import json
import math

import current_reference_profile_batch_query_v1 as query
from atlantic_nsec_reference_response_rules_v1 import line_feature,merge_map
from pacific_sec_jet_widths_delivery_rules_v1 import selected_rows
from pacific_nec_product_axis_delivery_contract_v1 import same,verify_response,normalized_snapshot


def profile_scene(rows):
    if not rows:return None
    return {'kind':'published_core_migration_profiles','title':'Pacific SEC: core movement by depth','records':copy.deepcopy(rows),
        'scope':'Regional southern-branch core migration in two longitude sections. Source-plot readings of1960-2020 change; no annual series or exact endpoint displacement inferred.',
        'operator_note':'Reading intervals are pixel-pick allowances, not confidence intervals. Underlying IAP field is1degree; plot precision adds no physical resolution. No current length, width, footprint or monthly animation is established.',
        'source_url':'https://doi.org/10.1186/s40562-025-00393-7','figure':'figures/pacific-sec-sun-2025-core-migration-profile-v1.svg','compact_figure':'figures/pacific-sec-sun-2025-core-migration-profile-compact-v1.svg'}


def dashboard(old,c):
    result=copy.deepcopy(old);seen=set()
    fields=['route_ids','route_url','core_migration_profile_ids','capabilities','map_features','evidence_links','source_ids','linked_source_count','section_fingerprints','fingerprint']
    for row in result['entries']:
        if row['id'] not in c['final_objects']:continue
        owner=row['id'];seen.add(owner)
        for key in fields:
            if key not in c['final_objects'][owner]:continue
            verify_response(c['prior_owners'][owner]['objects'][0].get(key),row.get(key))
            row[key]=copy.deepcopy(c['final_objects'][owner][key])
    if seen!=set(c['final_objects']):raise ValueError('Both preceding dashboard owners required')
    result['snapshot_fingerprint']=hashlib.sha256(('osw.reference-profiles.v1\n'+old['snapshot_fingerprint']+'\n'+query.sha(query.FILE)).encode()).hexdigest()
    return result


def catalogue(old,c):
    result=copy.deepcopy(old)
    if any(r['current_id']=='atlantic-north-equatorial' for r in result['candidates']):raise ValueError('Preceding NEC catalogue needs reconciliation')
    for route in c['routes']:
        entry=copy.deepcopy(route);bounds=route['editorial_probe_length_range_km']
        entry.update(candidate_file=route['source_file'],candidate_sha256=route['source_file_sha256'],figure=route['figure_file'],
            route_extent_kind='interior NEC schematic reference',scenario_range_km=[100.0*math.floor(bounds[0]/100),100.0*math.ceil(bounds[1]/100)],
            nominal_atlas_state_crossings=[],state_intersection_status='unassessed_no_physical_join_admitted',
            remaining_gates=['Whole-current endpoints and the other parallel NEC flows remain unresolved.','No annual range, physical axis, width or seasonal playback is established.'])
        report=copy.deepcopy(entry);report.update(figure_aspect_ratio=0.65,source_citation='Stramma and Schott1999, Figure4',
            coordinate_selection='Rounded OSW waypoints adjacent to the NEC schematic label between selected30W and55W gates; not digitized velocity cores.',
            scenario_rule=route['editorial_probe_interpretation'],method='WGS84 shortest-geodesic segment sums;18 drawing/gate cases per phase.',
            map_land_check='All36 cases clear both source-bound land masks under at-most1km geodesic sampling. No physical current footprint established.',
            nasa_movie_context=[],rendering_role='derived_inline_editorial_reach_card_not_additional_observation')
        entry['report_inline']=report;result['candidates'].append(entry)
    plans=[i for i,r in enumerate(result['remaining_current_decisions']) if r['current_id']=='atlantic-north-equatorial']
    if len(plans)!=1:raise ValueError('One preceding NEC plan required')
    verify_response(c['prior_decision']['source_decision'],result['remaining_current_decisions'][plans[0]])
    result['remaining_current_decisions'][plans[0]]=copy.deepcopy(c['final_decision']['source_decision'])
    for key,delta in [('route_candidates',2),('studied_reach_candidates',2),('currents_with_route_candidates',1),('currents_without_route_candidates',-1),('currents_without_any_reference_card',-1)]:result['counts'][key]+=delta
    strategies=[r for r in result['planning_taxonomy']['strategies'] if r['id']==c['final_decision']['strategy_id']]
    if len(strategies)!=1:raise ValueError('One preceding strategy required')
    strategies[0]['unbuilt_count']-=1
    return result


def expected_snapshot(name,old,c,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=dashboard(json.loads(old['snapshot_json']),c)
    elif name in ['atlas','seasons']:
        result['working_reference_routes']=catalogue(old['working_reference_routes'],c)
        result['core_migration_scenes']={'pacific-south-equatorial':profile_scene(c['records'])}
    if name=='atlas':
        path='research/ocean-motion-dashboard.json';result['sources_json'][path]=dashboard(json.loads(old['sources_json'][path]),c)
    return result


def expected_object(owner,old,c,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha;result['collections']['sources']+=copy.deepcopy(c['new_sources'])
    result['collections'][query.COLLECTION]=[copy.deepcopy(r) for r in c['records'] if query.owns(r,owner)]
    if 'objects' in result['collections']:result['collections']['objects']=[copy.deepcopy(c['final_objects'].get(r['id'],r)) for r in result['collections']['objects']]
    if owner==query.NEC:
        if 'route_decisions' in result['collections']:result['collections']['route_decisions']=[copy.deepcopy(c['final_decision']) if r['id']==c['final_decision']['id'] else r for r in result['collections']['route_decisions']]
        if 'reference_routes' in result['collections']:result['collections']['reference_routes']+=copy.deepcopy(c['routes'])
    if owner==query.SEC:result['core_migration_scene']=profile_scene(c['records'])
    return result


def owner_selected(request,c):
    prior=c['prior_owners'][query.NEC]['objects'][0]
    if not selected_rows(request,[prior]):return False
    taxonomy=request.get('taxonomy')
    if not taxonomy:return True
    return taxonomy['root_id']==query.NEC and taxonomy.get('include_root',False) or taxonomy['root_id']=='current:north-equatorial' and taxonomy['relation'] in ['children','descendants']


def expected_query(request,old,c,prior):
    result=copy.deepcopy(old);name=request['collection']
    if name=='objects':
        result['rows']=[copy.deepcopy(c['final_objects'].get(r['id'],r)) for r in result['rows']]
        if owner_selected(request,c):
            if c['prior_owners'][query.NEC]['objects'][0]['map_features']:raise ValueError('Prior NEC geometry needs explicit reconciliation')
            features=[line_feature(c['final_objects'][query.NEC],f,i) for i,f in enumerate(c['final_objects'][query.NEC]['map_features'])]
            order=[r['id'] for r in selected_rows(request,prior['objects'])]
            result['map_scene']=merge_map(old['map_scene'],features,old['map_scene']['matching_objects'],order)
        return result
    if name not in ['sources','reference_routes','route_decisions']:return result
    before=selected_rows(request,prior[name]);offset=request.get('offset',0);limit=request.get('limit',100)
    if old['total']!=len(before) or not same(old['rows'],before[offset:offset+limit]):raise ValueError('Complete preceding selection differs')
    rows=prior[name]+c['new_sources'] if name=='sources' else prior[name]+c['routes'] if name=='reference_routes' else [c['final_decision'] if r['id']==c['final_decision']['id'] else r for r in prior[name]]
    after=selected_rows(request,rows);result.update(total=len(after),rows=copy.deepcopy(after[offset:offset+limit]))
    if name=='reference_routes':
        added=[]
        for row in after:
            if row not in c['routes']:continue
            features=[f for f in c['final_objects'][query.NEC]['map_features'] if f['candidate_id']==row['id']]
            record={'id':row['id'],'label':row['name'],'type':'reference_route'}
            added.extend(line_feature(record,f,i) for i,f in enumerate(features))
        result['map_scene']=merge_map(old['map_scene'],added,len(after),[r['id'] for r in after])
    return result


def selected_profiles(request,c):
    rows=c['records']
    for f in request.get('filters',[]):
        key,value,op=f['field'],f['value'],f['op']
        if op=='eq':rows=[r for r in rows if same(r.get(key),value)]
        elif op=='gt':rows=[r for r in rows if type(r.get(key)) in (int,float) and r[key]>value]
        elif op=='lt':rows=[r for r in rows if type(r.get(key)) in (int,float) and r[key]<value]
        else:raise ValueError('Undeclared profile predicate')
    if 'record_type' in request:rows=[r for r in rows if r['type']==request['record_type']]
    order=request.get('sort',{'field':'id','direction':'asc'})
    return sorted(sorted(rows,key=lambda r:r['id']),key=lambda r:r[order['field']],reverse=order['direction']=='desc')


def expected_profile_query(request,c):
    rows=selected_profiles(request,c);offset=request.get('offset',0);limit=request.get('limit',100)
    return {'taxonomy_scope':None,'network_paths':None,'ok':True,'engine':'rust-osw-query-v1','collection':query.COLLECTION,
        'total':len(rows),'offset':offset,'limit':limit,'rows':copy.deepcopy(rows[offset:offset+limit]),'map_scene':None,'chart_scene':profile_scene(rows),'spatial_scope':None}


def verify_extension(parent,child,c):
    if set(child['collections'])!=set(parent['collections'])|{query.COLLECTION}:raise ValueError('Unexpected collection change')
    for name,before in parent['collections'].items():
        expected=before+c['routes'] if name=='reference_routes' else before+c['new_sources'] if name=='sources' else [c['final_objects'].get(r['id'],r) for r in before] if name=='objects' else [c['final_decision'] if r['id']==c['final_decision']['id'] else r for r in before] if name=='route_decisions' else before
        verify_response(expected,child['collections'][name])
    verify_response(c['records'],child['collections'][query.COLLECTION])
    manifest=copy.deepcopy(parent['manifest']);manifest['input_sha256'].update(c['input_sha256']);manifest['input_sha256'][query.FILE]=query.sha(query.FILE);manifest[query.KEY]=query.marker(c,query.sha(query.FILE))
    verify_response(manifest,child['manifest'])
    verify_response({k:v for k,v in parent.items() if k not in ['collections','manifest']},{k:v for k,v in child.items() if k not in ['collections','manifest']})
    return {'historical_collections_checked':len(parent['collections']),'existing_measurement_rows_changed':0,'reference_routes_added':2,'sources_added':3,'profile_records_added':24,'owner_objects_updated':2,'planning_decisions_updated':1}
