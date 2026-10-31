"""Independent complete-response expectations for six regional width additions."""
import copy
import hashlib
import json
import atlantic_nec_band_spans_query_v1 as query
from pacific_nec_product_axis_delivery_contract_v1 import same,verify_response,normalized_snapshot

def scene(rows,owner,contract):
    if not rows:return None
    return {'kind':'published_current_dimension_evidence','title':'Atlantic NEC: regional southern-band spans',
        'entity_id':owner,'current_id':owner.removeprefix('current:') if owner else None,
        'width_records':copy.deepcopy(rows),'event_records':[],
        'scope':'Observed July–August 2003 and July model output at the regional section near 27°W. The two southern-band extents are separate; they are not annual bounds, uncertainty or whole-current widths.',
        'definition':'Nominal WGS84 meridional separation of author-reported latitude bounds, rounded to 100 km. Eddy interruptions, unspecified paired-edge threshold and unknown fixed-depth width are retained.',
        'source_file':'research/atlantic-nec-stramma-2005-source-facts-v2.json',
        'source_url':contract['new_source']['url'],'source_label':'Original published study and section',
        'figure':'figures/atlantic-nec-stramma-2005-band-spans-prepared-v2.svg'}

def owner_widths(owner,contract):
    return contract['prior_owners'][owner]['widths']+[r for r in contract['width_records'] if query.owns(r,owner)]

def selected_rows(request,rows):
    if any(f['op']!='eq' for f in request.get('filters',[])):raise ValueError('Only explicit equality cases declared')
    rows=[r for r in rows if all(same(r.get(f['field']),f['value']) for f in request.get('filters',[]))]
    if 'record_type' in request:rows=[r for r in rows if r.get('type')==request['record_type']]
    order=request.get('sort',{'field':'id','direction':'asc'});field=order['field']
    rows=sorted(rows,key=lambda r:r['id'])
    return sorted([r for r in rows if r.get(field) is not None],key=lambda r:r[field],reverse=order['direction']=='desc')+[r for r in rows if r.get(field) is None]

def dashboard_document(old,contract):
    result=copy.deepcopy(old)
    fields=('width_ids','capabilities','source_ids','linked_source_count','section_fingerprints','fingerprint','evidence_links')
    for row in result['entries']:
        if row['id'] in contract['final_objects']:
            for field in fields:
                if not same(row[field],contract['prior_owners'][row['id']]['objects'][0][field]):raise ValueError('Preceding dashboard differs')
                row[field]=copy.deepcopy(contract['final_objects'][row['id']][field])
    result['snapshot_fingerprint']=hashlib.sha256(('osw.atlantic-nec-band-spans.v1\n'+old['snapshot_fingerprint']+'\n'+query.digest(contract)+'\n').encode()).hexdigest()
    result['published_atlantic_nec_band_spans_v1']={'width_records_added':2,'publication_sources_added':1,'whole_current_dimensions_added':0}
    return result

def expected_snapshot(name,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=dashboard_document(json.loads(old['snapshot_json']),contract)
    else:
        result['supplemental_widths']+=copy.deepcopy(contract['width_records'])
        for owner in query.OWNERS:result['current_dimension_evidence_scenes'][owner.removeprefix('current:')]=scene(owner_widths(owner,contract),owner,contract)
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            result['sources_json'][path]=dashboard_document(json.loads(old['sources_json'][path]),contract)
    return result

def expected_object(owner,old,contract,logical_sha):
    result=copy.deepcopy(old);result['bundle_sha256']=logical_sha
    result['collections']['sources'].append(copy.deepcopy(contract['new_source']))
    additions=[r for r in contract['width_records'] if query.owns(r,owner)]
    if additions:result['collections']['widths']+=copy.deepcopy(additions)
    if owner in query.OWNERS:result['current_dimension_evidence_scene']=scene(owner_widths(owner,contract),owner,contract)
    return result

def merge_width_scene(old,new):
    if new is None:return old
    scenes=copy.deepcopy(old['scenes']) if old and old.get('kind')=='scoped_width_comparisons' else [copy.deepcopy(old)] if old else []
    position=0
    while position<len(scenes) and scenes[position].get('kind')=='published_current_dimension_evidence':position+=1
    scenes.insert(position,new)
    if len(scenes)==1:return scenes[0]
    return {'kind':'scoped_width_comparisons','scope':'Source comparisons preserve different definitions, integration and sampling support.','scenes':scenes}

def expected_query(request,old,contract,prior_collections):
    result=copy.deepcopy(old);name=request['collection']
    if name=='objects':
        # All historical object filters/sorts use unchanged identity fields. Taxonomy
        # selection is preserved exactly; only the selected object values change.
        if any(f['field']!='id' for f in request.get('filters',[])):raise ValueError('Undeclared mutable object predicate')
        result['rows']=[copy.deepcopy(contract['final_objects'].get(r['id'],r)) for r in old['rows']]
        return result
    if name not in ('sources','widths'):return result
    before=selected_rows(request,prior_collections[name]);offset=request.get('offset',0);limit=request.get('limit',100)
    if old['total']!=len(before) or not same(old['rows'],before[offset:offset+limit]):raise ValueError('Preceding selected rows differ')
    additions=[contract['new_source']] if name=='sources' else contract['width_records']
    after=selected_rows(request,prior_collections[name]+additions)
    result['total']=len(after);result['rows']=copy.deepcopy(after[offset:offset+limit])
    if name=='widths':
        relevant={r['id'] for owner in query.OWNERS for r in owner_widths(owner,contract)}
        selected=[r for r in after if r['id'] in relevant]
        owners={r['current_id'] for r in selected};owner='current:'+next(iter(owners)) if len(owners)==1 else None
        result['chart_scene']=merge_width_scene(old['chart_scene'],scene(selected,owner,contract))
    return result

def verify_extension(parent,child,contract):
    if set(parent['collections'])!=set(child['collections']):raise ValueError('Collection set changed')
    for name,before in parent['collections'].items():
        expected=before+[contract['new_source']] if name=='sources' else before+contract['width_records'] if name=='widths' else [contract['final_objects'].get(r['id'],r) for r in before] if name=='objects' else before
        verify_response(expected,child['collections'][name])
    expected=copy.deepcopy(parent['manifest']);expected['input_sha256'].update(contract['input_sha256']);expected['input_sha256'][query.FILE]=query.digest(contract)
    expected[query.KEY]=query.marker(contract,query.digest(contract));verify_response(expected,child['manifest'])
    verify_response({k:v for k,v in parent.items() if k not in ('collections','manifest')},{k:v for k,v in child.items() if k not in ('collections','manifest')})
    return {'historical_collections_checked':len(parent['collections']),'existing_measurement_rows_changed':0,'width_records_added':2,'sources_added':1,'owner_objects_updated':1}
