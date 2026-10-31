"""Independent additive expectations for every complete historical API response."""
import copy
import hashlib
import json
import math
import atlantic_nsec_reference_query_v1 as query
import atlantic_nsec_reference_delivery_rules_v1 as patch
from pacific_sec_jet_widths_delivery_rules_v1 import selected_rows
from pacific_nec_product_axis_delivery_contract_v1 import same,verify_response,normalized_snapshot


def dashboard(old,c):
    result=copy.deepcopy(old);count=0
    fields=['route_ids','route_url','capabilities','map_features','evidence_links','source_ids','linked_source_count','section_fingerprints','fingerprint']
    for row in result['entries']:
        if row['id']!=query.OWNER:continue
        count+=1
        for key in fields:
            verify_response(c['prior_owner'][key],row[key]);row[key]=copy.deepcopy(c['final_owner'][key])
    if count!=1:raise ValueError('One preceding dashboard owner required')
    pin=query.sha(query.FILE)
    result['snapshot_fingerprint']=hashlib.sha256(('osw.atlantic-nsec-reference.v1\n'+old['snapshot_fingerprint']+'\n'+pin+'\n').encode()).hexdigest()
    return result


def catalogue(old,c):
    result=copy.deepcopy(old)
    if any(r['current_id']=='atlantic-south-equatorial' for r in result['candidates']):raise ValueError('Preceding catalogue references need reconciliation')
    for route in c['routes']:
        entry=copy.deepcopy(route);bounds=route['editorial_probe_length_range_km']
        entry.update(candidate_file=route['source_file'],candidate_sha256=route['source_file_sha256'],figure=route['figure_file'],
            route_extent_kind='northern-branch regional schematic reference',scenario_range_km=[100.0*math.floor(bounds[0]/100),100.0*math.ceil(bounds[1]/100)],
            nominal_atlas_state_crossings=[],state_intersection_status='unassessed_no_physical_join_admitted',
            remaining_gates=['Recover whole-current endpoints and the other SEC branches.',
                'Replace schematic waypoints with dated, layer-compatible total-flow axes before physical dimensions.',
                'No annual range or seasonal playback is established by these two schematics.'])
        report=copy.deepcopy(entry);report.update(figure_aspect_ratio=690/1060,
            source_citation='Stramma and Schott (1999), The mean flow field of the tropical Atlantic Ocean, Figure 4',
            coordinate_selection='OSW rounded waypoints follow the labelled nSEC schematic between selected interior gates. These are not calibrated digitization or measured velocity cores.',
            scenario_rule=route['editorial_probe_interpretation'],method='WGS84 shortest-geodesic segment sums. Gate and drawing variants remain separate from physical uncertainty.',
            map_land_check='All 54 drawing/gate variants clear both retained land masks under at-most-1 km geodesic sampling; geographic screening does not establish a physical current axis.',
            nasa_movie_context=[],rendering_role='derived_inline_editorial_reach_card_not_additional_observation')
        entry['report_inline']=report;result['candidates'].append(entry)
    plans=[i for i,r in enumerate(result['remaining_current_decisions']) if r['current_id']=='atlantic-south-equatorial']
    if len(plans)!=1:raise ValueError('One preceding atlas plan required')
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
    if name=='atlas':
        path='research/ocean-motion-dashboard.json';result['sources_json'][path]=dashboard(json.loads(old['sources_json'][path]),c)
    return result


def expected_object(owner,old,c,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha;result['collections']['sources']+=copy.deepcopy(c['new_sources'])
    if owner==query.OWNER:
        for name,key in [('objects','final_owner'),('route_decisions','final_decision')]:
            if name in result['collections']:result['collections'][name]=[copy.deepcopy(c[key]) if r['id']==c[key]['id'] else r for r in result['collections'][name]]
        if 'reference_routes' in result['collections']:result['collections']['reference_routes']+=copy.deepcopy(c['routes'])
    return result


def line_feature(record,feature,index):
    coordinates=feature['geometry']['coordinates']
    primitive={'kind':'line','d':''.join(('M' if i==0 else 'L')+f' {lon+180:.5f} {90-lat:.5f} ' for i,(lon,lat) in enumerate(coordinates))}
    result={'entity_id':record['id'],'feature_index':index,'label':record.get('label'),'type':record['type'],
        'role':feature['role'],'note':feature.get('note'),'observation_date':feature.get('observation_date'),'primitive':primitive}
    for key in ['source_file_sha256','time_convention','layer','source_url']:
        if key in feature:result[key]=feature[key]
    return result


def owner_selected(request,c):
    if not selected_rows(request,[c['prior_owner']]):return False
    taxonomy=request.get('taxonomy')
    if not taxonomy:return True
    root=taxonomy['root_id'];relation=taxonomy['relation']
    if root==query.OWNER and taxonomy.get('include_root',False):return True
    return root=='current:south-equatorial' and relation in ['children','descendants']


def merge_map(old,added,matching,order):
    result=copy.deepcopy(old);result['features']+=added
    indices={key:i for i,key in enumerate(order)}
    result['features'].sort(key=lambda r:indices[r['entity_id']])
    mapped=len({r['entity_id'] for r in result['features']})
    result.update(matching_objects=matching,mapped_objects=mapped,unmapped_objects=matching-mapped)
    return result


def expected_query(request,old,c,prior):
    result=copy.deepcopy(old);name=request['collection']
    if name=='objects':
        result['rows']=[copy.deepcopy(c['final_owner']) if r['id']==query.OWNER else r for r in result['rows']]
        if owner_selected(request,c):
            if c['prior_owner']['map_features']:raise ValueError('Prior owner geometry needs explicit reconciliation')
            features=[line_feature(c['final_owner'],f,i) for i,f in enumerate(c['final_owner']['map_features'])]
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
            features=[f for f in c['final_owner']['map_features'] if f['candidate_id']==row['id']]
            record={'id':row['id'],'label':row['name'],'type':'reference_route'}
            added.extend(line_feature(record,f,i) for i,f in enumerate(features))
        result['map_scene']=merge_map(old['map_scene'],added,len(after),[r['id'] for r in after])
    return result


def verify_extension(parent,child,c):
    if set(parent['collections'])!=set(child['collections']):raise ValueError('Collection set changed')
    for name,before in parent['collections'].items():
        expected=before+c['routes'] if name=='reference_routes' else before+c['new_sources'] if name=='sources' else [c['final_owner'] if r['id']==query.OWNER else r for r in before] if name=='objects' else [c['final_decision'] if r['id']==c['final_decision']['id'] else r for r in before] if name=='route_decisions' else before
        verify_response(expected,child['collections'][name])
    manifest=copy.deepcopy(parent['manifest']);manifest['input_sha256'].update(c['input_sha256']);manifest['input_sha256'][query.FILE]=query.sha(query.FILE);manifest[query.KEY]=patch.marker(c,query.sha(query.FILE))
    verify_response(manifest,child['manifest'])
    verify_response({k:v for k,v in parent.items() if k not in ['collections','manifest']},{k:v for k,v in child.items() if k not in ['collections','manifest']})
    return {'historical_collections_checked':len(parent['collections']),'existing_measurement_rows_changed':0,'reference_routes_added':2,'sources_added':2,'owner_objects_updated':1,'planning_decisions_updated':1}
