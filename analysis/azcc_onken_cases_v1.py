"""Independent filtering, pagination, scene-scope and inventory semantics."""
import azcc_onken_query_v1 as query
COUNT=12

def adapt_legacy_cases(cases):
    contract=query.build_contract()
    if contract['parent_collection_counts']['widths']!=177 or contract['expected_totals']['widths']!=178 or contract['new_width_records']!=1:
        raise ValueError('Exact one-width addition required')
    result=[];changed=0
    for request,expected in cases:
        if request=={'collection':'widths','limit':1}:
            if type(expected) is not int or expected!=177:raise ValueError('Exact177-width legacy expectation required')
            expected=178;changed+=1
        result.append((request,expected))
    if changed!=1:raise ValueError('Exactly one historical width inventory case required')
    return result

def main_cases(collections):
    eq=lambda field,value:{'field':field,'op':'eq','value':value}
    def case(collection,filters,**extra):
        request={'collection':collection,'filters':filters,'limit':100,**extra}
        return request,[r for r in collections[collection] if all(r.get(f['field'])==f['value'] for f in filters)]
    current=[eq('current_id',query.CURRENT)]
    old=query.build_contract()['prior_records']['widths'][0]['id']
    result=[case('widths',current),case('widths',[eq('id',query.WIDTH_ID)]),case('widths',[eq('id',old)]),
        case('widths',current,limit=1,offset=1),case('widths',current,sort={'field':'approximate_width_km','direction':'desc'},limit=1),
        case('widths',current+[eq('approximate_width_km',200)]),case('widths',current+[eq('width_rank_eligible',True)]),
        case('widths',current+[eq('source_id',query.SOURCE_ID)]),case('objects',[eq('id',query.OWNER)]),
        case('sources',[eq('id',query.SOURCE_ID)]),case('widths',[eq('source_file',query.FACTS)]),case('reference_routes',current)]
    if len(result)!=COUNT:raise ValueError('Exact AzCC query inventory required')
    return result

def verify(request,expected,response):
    sort=request.get('sort',{'field':'id','direction':'asc'})
    ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
    start=request.get('offset',0);selected=ordered[start:start+request['limit']]
    if response.get('ok') is not True or response.get('total')!=len(expected) or response.get('rows')!=selected:
        raise ValueError('AzCC exact filtering/sorting/pagination differs')
    if request['collection']!='widths':return
    chart=response.get('chart_scene')
    if not expected:
        if chart is not None:raise ValueError('Empty selection fabricated a width scene')
        return
    scenes=chart.get('scenes',[]) if isinstance(chart,dict) and chart.get('kind')=='scoped_width_comparisons' else [chart]
    matching=[s for s in scenes if isinstance(s,dict) and s.get('kind')=='published_current_dimension_evidence' and s.get('entity_id')==query.OWNER]
    if len(matching)!=1:raise ValueError('One AzCC comparison scene required')
    scene=matching[0]
    if sorted(scene.get('width_records',[]),key=lambda r:r['id'])!=sorted(expected,key=lambda r:r['id']) or scene.get('event_records')!=[]:
        raise ValueError('Width scene must retain only matching rows before pagination')
    if all(r['id']==query.WIDTH_ID for r in expected) and response.get('map_scene') is not None:
        raise ValueError('Historical regional width gained physical geometry')
