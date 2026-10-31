"""Independent full-response expectations for scoped reach/cited-width admission."""
import copy
import hashlib
import json
import current_core_dimensions_query_v1 as query
from pacific_sec_jet_widths_delivery_rules_v1 import selected_rows,merge_width_scene
from pacific_nec_product_axis_delivery_contract_v1 import same,verify_response,normalized_snapshot

def scene(widths,reaches,owner,contract):
    if not widths and not reaches:return None
    first=(reaches or widths)[0]
    return {'kind':'published_current_dimension_evidence','title':'Red Sea: reported summer plume reach' if reaches else 'Indian SEC: cited upstream width',
        'entity_id':owner,'current_id':owner.removeprefix('current:') if owner else None,'width_records':copy.deepcopy(widths),'length_records':copy.deepcopy(reaches),'event_records':[],
        'scope':'Each record retains its regional extent, evidence class and source operator. These records do not establish whole-current dimensions, measurement uncertainty or annual extrema.',
        'definition':'Red Sea summer reach: reported 110–120 km using speed and salinity contour support. Indian SEC width: about 650 km cited in the 2008 report; original attribution and methods remain unverified. Separate length and width scales.',
        'source_file':first['source_file'],'source_url':first['source_url'],'source_label':'Original source reporting this claim',
        'figure':'figures/current-core-gap-followup-scoped-dimensions-v1.svg'}

def owner_scene(owner,contract):return scene([r for r in contract['width_records'] if query.owns(r,owner)],[r for r in contract['reach_records'] if query.owns(r,owner)],owner,contract)

def dashboard_document(old,contract):
    result=copy.deepcopy(old)
    for row in result['entries']:
        if row['id'] not in contract['final_objects']:continue
        prior=contract['prior_owners'][row['id']]['objects'][0];final=contract['final_objects'][row['id']]
        for field in ['width_ids','regional_reach_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links']:
            if field not in final:continue
            if not same(row.get(field),prior.get(field)):raise ValueError('Preceding dashboard differs')
            row[field]=copy.deepcopy(final[field])
    result['snapshot_fingerprint']=hashlib.sha256(('osw.current-core-dimensions.v1\n'+old['snapshot_fingerprint']+'\n'+query.digest(contract)+'\n').encode()).hexdigest()
    result[query.KEY]={'width_records_added':1,'regional_reaches_added':1,'publication_sources_added':2,'whole_current_dimensions_added':0}
    return result

def expected_snapshot(name,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=dashboard_document(json.loads(old['snapshot_json']),contract)
    else:
        result['supplemental_widths']+=copy.deepcopy(contract['width_records'])
        for owner in query.OWNERS:result['current_dimension_evidence_scenes'][owner.removeprefix('current:')]=owner_scene(owner,contract)
        if name=='atlas':
            path='research/ocean-motion-dashboard.json';result['sources_json'][path]=dashboard_document(json.loads(old['sources_json'][path]),contract)
    return result

def expected_object(owner,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    result['collections']['sources']+=copy.deepcopy(contract['new_sources'])
    for collection,key in [('widths','width_records'),(query.REACHES,'reach_records')]:result['collections'][collection]+=[copy.deepcopy(r) for r in contract[key] if query.owns(r,owner)]
    if owner in query.OWNERS:result['current_dimension_evidence_scene']=owner_scene(owner,contract)
    return result

def expected_query(request,old,contract,prior_collections):
    result=copy.deepcopy(old);name=request['collection']
    if name=='objects':
        if any(f['field']!='id' for f in request.get('filters',[])):raise ValueError('Undeclared mutable object predicate')
        result['rows']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in old['rows']];return result
    key={'sources':'new_sources','widths':'width_records',query.REACHES:'reach_records'}.get(name)
    if key is None:return result
    before=selected_rows(request,prior_collections[name]);offset=request.get('offset',0);limit=request.get('limit',100)
    if old['total']!=len(before) or not same(old['rows'],before[offset:offset+limit]):raise ValueError('Preceding complete selection differs')
    after=selected_rows(request,prior_collections[name]+contract[key]);result['total']=len(after);result['rows']=copy.deepcopy(after[offset:offset+limit])
    if name in ['widths',query.REACHES]:
        selected=[r for r in after if r in contract[key]];owners={r['entity_id'] for r in selected};owner=next(iter(owners)) if len(owners)==1 else None
        extra=scene(selected if name=='widths' else [],selected if name==query.REACHES else [],owner,contract)
        result['chart_scene']=merge_width_scene(old['chart_scene'],extra) if name=='widths' else extra
    return result

def verify_extension(parent,child,contract):
    if set(parent['collections'])!=set(child['collections']):raise ValueError('Collection set changed')
    keys={'sources':'new_sources','widths':'width_records',query.REACHES:'reach_records'}
    for name,before in parent['collections'].items():
        expected=before+contract[keys[name]] if name in keys else [contract['final_objects'].get(r['id'],r) for r in before] if name=='objects' else before
        verify_response(expected,child['collections'][name])
    expected=copy.deepcopy(parent['manifest']);expected['input_sha256'].update(contract['input_sha256']);expected['input_sha256'][query.FILE]=query.digest(contract);expected[query.KEY]=query.marker(contract,query.digest(contract))
    verify_response(expected,child['manifest']);verify_response({k:v for k,v in parent.items() if k not in ['collections','manifest']},{k:v for k,v in child.items() if k not in ['collections','manifest']})
    return {'historical_collections_checked':len(parent['collections']),'existing_measurement_rows_changed':0,'width_records_added':1,'regional_reaches_added':1,'sources_added':2,'owner_objects_updated':2}
