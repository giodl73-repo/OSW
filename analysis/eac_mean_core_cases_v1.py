"""Source-defined EAC sections: filtering, sorting, pagination, joins and unknowns."""
import eac_mean_core_query_v1 as query

COUNT=16


def main_cases(collections):
    def case(collection=query.COLLECTION, filters=None, **extra):
        request={'collection':collection,'limit':100,**extra}
        if filters is not None:request['filters']=filters
        rows=[r for r in collections[collection] if all(r.get(f['field'])==f['value'] for f in filters or [])]
        return request,rows
    eq=lambda field,value:[{'field':field,'op':'eq','value':value}]
    first=collections[query.COLLECTION][0]
    result=[case(),case(filters=eq('current_id',query.CURRENT)),
        case(filters=eq('latitude_degrees_north',-32.3)),case(filters=eq('place','Sydney')),
        case(filters=eq('id',first['id'])),case(filters=eq('source_file',query.facts.FACTS)),
        case(filters=eq('geometry',None)),case(filters=eq('annual_width_range_km',None)),
        case(filters=eq('rank_eligible',False)),case(filters=eq('rank_eligible',True)),
        case(filters=eq('current_id','agulhas')),case(limit=1,offset=2),
        case(sort={'field':'maximum_depth_m','direction':'desc'},limit=2,offset=1),
        case('objects',eq('id',query.OWNER)),case('sources',eq('id',query.SOURCE_ID)),
        case(filters=eq('seasonal_playback_eligible',False))]
    if len(result)!=COUNT:raise ValueError('Exact EAC query case inventory required')
    return result


def verify(request,expected,response):
    sort=request.get('sort',{'field':'id','direction':'asc'})
    selected=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
    start=request.get('offset',0);selected=selected[start:start+request['limit']]
    if response.get('ok') is not True or response.get('total')!=len(expected) or response.get('rows')!=selected:
        raise ValueError('EAC exact filtering/sort/pagination differs')
    if request['collection']!=query.COLLECTION:return
    if response.get('map_scene') is not None:raise ValueError('No physical EAC footprint admitted')
    scene=response.get('chart_scene')
    if not expected:
        if scene is not None:raise ValueError('Empty EAC selection must not fabricate a scene')
        return
    if (not isinstance(scene,dict) or scene.get('kind')!='published_mean_core_sections'
        or sorted(scene.get('records',[]),key=lambda r:r['id'])!=sorted(expected,key=lambda r:r['id'])):
        raise ValueError('EAC scene must include all matching records before pagination')
    for row in scene['records']:
        if any(row.get(k) is not None for k in ['geometry','annual_width_range_km','paired_edge_width_km']):
            raise ValueError('Unsupported EAC footprint/width/range inferred')
