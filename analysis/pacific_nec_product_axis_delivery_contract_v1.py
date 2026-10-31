"""Independent, additive expectations for complete diagnostic delivery responses."""
import copy
import hashlib
import json
import pacific_nec_product_axis_records_v1 as records
from pacific_nec_product_axis_query_v1 import FILE

OWNER='current:pacific-north-equatorial'

def same(left,right):
    numeric=lambda value:type(value) in (int,float)
    if numeric(left) and numeric(right):return left==right
    if type(left) is not type(right):return False
    if isinstance(left,dict):return left.keys()==right.keys() and all(same(value,right[key]) for key,value in left.items())
    if isinstance(left,list):return len(left)==len(right) and all(same(a,b) for a,b in zip(left,right))
    return left==right

def verify_response(expected,actual):
    if not same(expected,actual):raise ValueError('Complete response changed outside the declared additive projection')

def admission_marker(contract):
    return {'schema':'osw.pacific-nec-product-axis-runtime.v1','contract_file':FILE,
        'contract_sha256':hashlib.sha256(records.encoded(contract)).hexdigest(),
        'parent_logical_sha256':contract['parent_logical_sha256'],'collections_added':contract['counts_added'],
        'sources_added':len(contract['new_sources']),'admission':'experimental_product_operator_only',
        'reported_lengths_added':0,'reference_routes_added':0,'physical_widths_added':0,'physical_state_joins_added':0,
        'annual_physical_ranges_added':0,'independent_observations_added':0}

def full_scene(contract):
    rows=contract['collections_added']
    return {'kind':'surface_product_axis_diagnostics','entity_id':OWNER,'title':'Pacific NEC:2013 surface-product diagnostics',
        'scope':'Experimental window-constrained OSCAR product-operator paths between130E and120W. They do not establish whole-current dimensions, physical axes, annual physical ranges or independent observations.',
        'series':copy.deepcopy(rows['current_axis_series']),'readings':copy.deepcopy(rows['current_axis_readings']),
        'section_spans':copy.deepcopy(rows['current_axis_section_spans']),'scenario_count':1332,'sources':copy.deepcopy(contract['new_sources']),
        'nominal_window_deg_north':[8,18],'default_month':1,'year':2013,
        'playback_scope':'Dated monthly source-product frames only; no temporal interpolation or seasonal climatology.',
        'method_span_scope':'Threshold, direction, search/window and representation choices are separate operators; their spread is not physical uncertainty.'}

def diagnostic_status():
    return {'entity_id':OWNER,'series_count':3,'monthly_path_count':36,'method_scenario_count':1332,'section_span_count':36,
        'withheld_scenario_count':85,'withheld_section_span_count':1,'physical_dimensions_added':0,
        'label':'Pacific NEC: experimental2013 product diagnostics','object_url':'object.html?id=current%3Apacific-north-equatorial','collection':'current_axis_series'}

def dashboard_document(parent):
    if 'surface_product_axis_diagnostics' in parent:raise ValueError('Parent already has diagnostic status')
    result=copy.deepcopy(parent);result['surface_product_axis_diagnostics']=diagnostic_status();return result

def expected_snapshot(name,parent,contract,logical_sha):
    if name not in ('atlas','seasons','dashboard') or parent.get('ok') is not True:raise ValueError('Complete parent snapshot required')
    result=copy.deepcopy(parent);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=dashboard_document(json.loads(parent['snapshot_json']))
    else:
        if 'surface_product_axis_scenes' in parent:raise ValueError('Already projected atlas')
        result['surface_product_axis_scenes']={'pacific-north-equatorial':full_scene(contract)}
        if name=='atlas':
            path='research/ocean-motion-dashboard.json'
            result['sources_json'][path]=dashboard_document(json.loads(parent['sources_json'][path]))
    return result

def normalized_snapshot(name,result):
    result=copy.deepcopy(result)
    if name=='dashboard':result['snapshot_json']=json.loads(result['snapshot_json'])
    elif name=='atlas':
        path='research/ocean-motion-dashboard.json';result['sources_json'][path]=json.loads(result['sources_json'][path])
    return result

def expected_object(owner,parent,contract,logical_sha):
    if parent.get('ok') is not True or parent.get('id')!=owner:raise ValueError('Complete parent object required')
    result=copy.deepcopy(parent);result['bundle_sha256']=logical_sha
    result['collections']['sources']+=copy.deepcopy(contract['new_sources'])
    if owner==OWNER:result['surface_product_axis_scene']=full_scene(contract)
    return result

def expected_query(request,parent,contract,old_sources):
    if parent.get('ok') is not True:raise ValueError('Complete historical query required')
    result=copy.deepcopy(parent)
    if request['collection']!='sources':return result
    if any(f.get('op')!='eq' for f in request.get('filters',[])) or set(request)-{'collection','filters','sort','limit','offset'}:raise ValueError('Unsupported historical source query')
    def matches(row):return all(type(row.get(f['field'])) is type(f['value']) and row.get(f['field'])==f['value'] for f in request.get('filters',[]))
    order=request.get('sort',{'field':'id','direction':'asc'});key=order['field']
    if any(row.get(key) is None for row in old_sources+contract['new_sources']):raise ValueError('Nullable source ordering is not declared')
    sort=lambda rows:sorted(rows,key=lambda row:row[key],reverse=order['direction']=='desc')
    old=sort([r for r in old_sources if matches(r)]);offset=request.get('offset',0);limit=request.get('limit',100)
    if parent['total']!=len(old) or parent['rows']!=old[offset:offset+limit]:raise ValueError('Parent source response differs from exact audited rows')
    rows=sort(old+[r for r in contract['new_sources'] if matches(r)]);result['total']=len(rows);result['rows']=rows[offset:offset+limit]
    return result

def query_scene(name,matches,contract):
    if name not in contract['collections_added']:raise ValueError('Unknown diagnostic collection')
    scene=full_scene(contract)
    ids={r['id'] if name=='current_axis_series' else r['series_id'] for r in matches}
    scene['series']=[r for r in scene['series'] if r['id'] in ids]
    scene['readings']=copy.deepcopy(matches) if name=='current_axis_readings' else [r for r in scene['readings'] if r['series_id'] in ids] if name=='current_axis_series' else []
    scene['section_spans']=copy.deepcopy(matches) if name=='current_axis_section_spans' else []
    scene.update(selected_collection=name,selected_records=copy.deepcopy(matches),selected_count=len(matches))
    return scene

def verify_extension(parent,child,contract):
    before=parent['collections'];after=child['collections'];added=contract['collections_added']
    if set(after)!=set(before)|set(added):raise ValueError('Unexpected collection change')
    for name,rows in before.items():
        wanted=rows+contract['new_sources'] if name=='sources' else rows
        if not same(after[name],wanted):raise ValueError('Historical rows changed: '+name)
    for name,rows in added.items():
        if not same(after[name],rows):raise ValueError('Incomplete diagnostic collection: '+name)
    expected_manifest=copy.deepcopy(parent['manifest'])
    if contract['namespace'] in expected_manifest:raise ValueError('Diagnostic namespace already exists')
    expected_manifest['input_sha256']={**expected_manifest.get('input_sha256',{}),**contract['input_sha256'],FILE:admission_marker(contract)['contract_sha256']}
    expected_manifest[contract['namespace']]=admission_marker(contract)
    if not same(expected_manifest,child['manifest']):raise ValueError('Manifest changed outside declared diagnostic admission')
    if {k:v for k,v in parent.items() if k not in ('collections','manifest')}!={k:v for k,v in child.items() if k not in ('collections','manifest')}:raise ValueError('Unrelated packet metadata changed')
    return {'historical_collections_preserved':len(before),'new_collection_counts':{k:len(v) for k,v in added.items()},'new_sources':len(contract['new_sources']),'canonical_measurement_rows_changed':0}
