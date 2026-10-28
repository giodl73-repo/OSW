"""Exact route/source/owner/null-range filters and one changed inventory total."""
import wicc_winter_reference_query_v1 as query


def adapt(cases):
    result=[];changed=0
    for request,expected in cases:
        if request=={'collection':'reference_routes','limit':1}:
            if expected!=82:raise ValueError('Exact preceding route inventory required')
            expected=83;changed+=1
        result.append((request,expected))
    if changed!=1:raise ValueError('Exactly one route inventory case required')
    return result


def main_cases(collections):
    contract=query.build_contract();route=contract['route']
    def case(collection,field,value,extra=None,**kwargs):
        filters=[{'field':field,'op':'eq','value':value}]+(extra or [])
        rows=[r for r in collections[collection] if all(r.get(f['field'])==f['value'] for f in filters)]
        return {'collection':collection,'filters':filters,'limit':100,**kwargs},rows
    by_id={'field':'id','op':'eq','value':query.ROUTE}
    result=[case('reference_routes','id',query.ROUTE),case('reference_routes','current_id',query.CURRENT),
        case('objects','id',query.OWNER),case('route_decisions','entity_id',query.OWNER)]
    result += [case('sources','id',r['id']) for r in contract['new_sources']]
    result += [case('reference_routes','current_id',query.CURRENT,[{'field':'scenario_range_km','op':'eq','value':None}]),
        case('reference_routes','current_id',query.CURRENT,[{'field':'rank_eligible','op':'eq','value':True}]),
        case('reference_routes','current_id','agulhas',[by_id]),
        case('reference_routes','id',query.ROUTE,offset=1,limit=1),
        case('reference_routes','source_file',query.CANDIDATE)]
    if len(result)!=12:raise ValueError('Twelve exact WICC cases required')
    return result


def verify(request,expected,response):
    selected=sorted(expected,key=lambda r:r['id'])[request.get('offset',0):request.get('offset',0)+request['limit']]
    if response.get('ok') is not True or response['total']!=len(expected) or response['rows']!=selected:
        raise ValueError('WICC route selection/pagination differs')
    if request['collection']=='reference_routes':
        for row in response['rows']:
            if row['scenario_range_km'] is not None or row['annual_length_range_km'] is not None or row['rank_eligible'] is not False:
                raise ValueError('Unsupported dimension/ranking support inferred')
