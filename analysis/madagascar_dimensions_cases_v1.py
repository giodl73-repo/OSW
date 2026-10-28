"""Exact filtered source joins and unknowns for regional width and dated events."""
import madagascar_dimensions_query_v1 as query
COUNT=18

def main_cases(collections):
    def case(collection=query.COLLECTION,filters=None,**extra):
        request={'collection':collection,'limit':100,**extra}
        if filters is not None:request['filters']=filters
        rows=[r for r in collections[collection] if all(r.get(f['field'])==f['value'] for f in filters or [])]
        return request,rows
    eq=lambda field,value:[{'field':field,'op':'eq','value':value}]
    first=collections[query.COLLECTION][0];width=query.build_contract()['width_record']
    result=[case(),case(filters=eq('current_id',query.CURRENT)),case(filters=eq('date','2011-01-19')),
        case(filters=eq('id',first['id'])),case(filters=eq('width_km',None)),case(filters=eq('seasonal_playback_eligible',True)),
        case(filters=eq('current_id','agulhas')),case(limit=1,offset=2),case(sort={'field':'date','direction':'desc'},limit=2,offset=1),
        case('widths',eq('current_id',query.CURRENT)),case('widths',eq('id',width['id'])),
        case('widths',eq('current_id',query.CURRENT),limit=1,offset=1),
        case('objects',eq('id',query.OWNER)),case('sources',eq('id',query.SOURCE_ID)),
        case(filters=eq('independent_new_observation',False)),case(filters=eq('geometry',None)),
        case(filters=eq('source_file',query.source.FACTS)),case(filters=eq('source_panel','Figure4g'))]
    if len(result)!=COUNT:raise ValueError('Exact query inventory required')
    return result

def verify(request,expected,response):
    sort=request.get('sort',{'field':'id','direction':'asc'})
    ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
    start=request.get('offset',0);selected=ordered[start:start+request['limit']]
    if response.get('ok') is not True or response.get('total')!=len(expected) or response.get('rows')!=selected:
        raise ValueError('Madagascar exact filtering/sorting/pagination differs')
    if request['collection'] not in ['widths',query.COLLECTION]:return
    scene=response.get('chart_scene')
    if not expected:
        if scene is not None:raise ValueError('Empty selection fabricated a scene')
        return
    if not isinstance(scene,dict) or scene.get('kind')!='published_current_dimension_evidence':raise ValueError('Missing dimension evidence scene')
    key='width_records' if request['collection']=='widths' else 'event_records'
    if sorted(scene.get(key,[]),key=lambda r:r['id'])!=sorted(expected,key=lambda r:r['id']):raise ValueError('Scene must retain all matching rows before pagination')
    other='event_records' if key=='width_records' else 'width_records'
    if scene.get(other)!=[]:raise ValueError('Filtered scene leaked unrelated evidence')
    for row in scene.get('event_records',[]):
        if row['width_km'] is not None or row['geometry'] is not None or row['seasonal_playback_eligible'] is not False:
            raise ValueError('Event promoted to physical seasonal dimensions')
