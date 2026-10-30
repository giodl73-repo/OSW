"""Independent complete-response expectations for the new velocity quantity class."""
import copy,hashlib,json
import characteristic_velocities_query_v1 as query
from pacific_nec_product_axis_delivery_contract_v1 import same,verify_response,normalized_snapshot
from atlantic_nec_band_spans_delivery_rules_v1 import selected_rows

def scene(rows,contract):
    if not rows:return None
    return {'kind':'published_characteristic_current_velocities','title':'Tropical Atlantic: characteristic velocity summaries',
        'scope':'Author-selected characteristic values from spatially varying ship-drift maps. Mean-vector speed, seasonal variation and harmonic amplitudes are distinct quantities; these are not whole-current averages or annual extrema.',
        'records':copy.deepcopy(rows),'source_file':'research/richardson-walsh-1986-characteristic-velocity-source-facts-v1.json',
        'source_url':contract['new_source']['url'],'figure':'figures/richardson-walsh-1986-characteristic-velocities-v1.svg',
        'time_support':'Historical observations1875–1976, strongly weighted toward1920–1940; fixed sampling depth unknown.',
        'operator_note':'Seasonal variation: sqrt(mean(u_prime^2)+mean(v_prime^2)). Harmonic amplitude, as printed:0.5*sqrt(A_x^2+A_y^2). Phases and monthly series are not supplied by Table1.',
        'unknowns':'Annual extrema, numerical uncertainty and monthly velocity series: unknown. No geometry or independent observations added.'}

def owner_rows(owner,contract):return [r for r in contract['records'] if query.owns(r,owner)]
def speed_scenes(old,contract):
    result=copy.deepcopy(old)
    for owner in query.OWNERS:
        key=owner.removeprefix('current:');new=scene(owner_rows(owner,contract),contract);prior=result.get(key)
        result[key]=new if prior is None else {'kind':'published_velocity_evidence_groups','title':'Published velocity evidence with separate methods',
            'scope':'Preserve characteristic map summaries and seasonal core estimates as separate evidence; shared source populations are not independent observations.','scenes':[prior,new]}
    return result

def dashboard_document(old,contract):
    result=copy.deepcopy(old)
    fields=('characteristic_velocity_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links')
    for row in result['entries']:
        if row['id'] in contract['final_objects']:
            prior=contract['prior_owners'][row['id']]['objects'][0]
            for field in fields:
                if not same(row.get(field),prior.get(field)):raise ValueError('Preceding dashboard differs')
                row[field]=copy.deepcopy(contract['final_objects'][row['id']][field])
    result['snapshot_fingerprint']=hashlib.sha256(('osw.characteristic-velocities.v1\n'+old['snapshot_fingerprint']+'\n'+query.digest(contract)+'\n').encode()).hexdigest()
    result['published_characteristic_velocities_v1']={'records_added':10,'publication_sources_added':1,'whole_current_dimensions_added':0}
    return result

def expected_snapshot(name,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=dashboard_document(json.loads(old['snapshot_json']),contract)
    else:
        result['published_speed_scenes']=speed_scenes(old['published_speed_scenes'],contract)
        if name=='atlas':
            path='research/ocean-motion-dashboard.json';result['sources_json'][path]=dashboard_document(json.loads(old['sources_json'][path]),contract)
    return result

def expected_object(owner,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha;result['collections']['sources'].append(copy.deepcopy(contract['new_source']))
    selected=owner_rows(owner,contract)
    if selected:result['collections'][query.COLLECTION]=copy.deepcopy(selected);result['characteristic_velocity_scene']=scene(selected,contract)
    return result

def expected_query(request,old,contract,prior_collections):
    result=copy.deepcopy(old);name=request['collection']
    if name=='objects':
        if any(f['field']!='id' for f in request.get('filters',[])):raise ValueError('Undeclared mutable object predicate')
        result['rows']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in old['rows']]
    elif name=='sources':
        before=selected_rows(request,prior_collections[name]);offset=request.get('offset',0);limit=request.get('limit',100)
        if old['total']!=len(before) or not same(old['rows'],before[offset:offset+limit]):raise ValueError('Preceding sources differ')
        after=selected_rows(request,prior_collections[name]+[contract['new_source']]);result['total']=len(after);result['rows']=copy.deepcopy(after[offset:offset+limit])
    return result

def expected_new_query(request,contract):
    if request['collection']!=query.COLLECTION:raise ValueError('Only the new scientific collection is declared')
    matches=selected_rows(request,contract['records']);offset=request.get('offset',0);limit=request.get('limit',100)
    return {'taxonomy_scope':None,'network_paths':None,'ok':True,'engine':'rust-osw-query-v1','collection':query.COLLECTION,
        'total':len(matches),'offset':offset,'limit':limit,'rows':copy.deepcopy(matches[offset:offset+limit]),
        'map_scene':None,'chart_scene':scene(matches,contract),'spatial_scope':None}

def verify_extension(parent,child,contract):
    if set(child['collections'])!=set(parent['collections'])|{query.COLLECTION}:raise ValueError('Collection set changed unexpectedly')
    for name,before in parent['collections'].items():
        expected=before+[contract['new_source']] if name=='sources' else [contract['final_objects'].get(r['id'],r) for r in before] if name=='objects' else before
        verify_response(expected,child['collections'][name])
    verify_response(contract['records'],child['collections'][query.COLLECTION])
    expected=copy.deepcopy(parent['manifest']);expected['input_sha256'].update(contract['input_sha256']);expected['input_sha256'][query.FILE]=query.digest(contract);expected[query.KEY]=query.marker(contract,query.digest(contract));verify_response(expected,child['manifest'])
    verify_response({k:v for k,v in parent.items() if k not in ('collections','manifest')},{k:v for k,v in child.items() if k not in ('collections','manifest')})
    return {'historical_collections_checked':len(parent['collections']),'existing_measurement_rows_changed':0,'collections_added':1,'characteristic_velocity_records_added':10,'sources_added':1,'owner_objects_updated':8,'width_records_added':0,'length_records_added':0}
