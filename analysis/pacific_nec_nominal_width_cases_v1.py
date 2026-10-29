"""Independent query semantics for one reviewed nominal regional approximation."""
import equatorial_basin_identity_cases_v2 as basin_cases
import pacific_nec_nominal_width_runtime_v1 as runtime
query=runtime.query
COUNT=20


def adapt_legacy_cases(cases):
    result=[];changed=0
    for request,expected in cases:
        if request=={'collection':'widths','limit':1}:
            if type(expected) is not int or expected!=178:raise ValueError('Exact178-width expectation required')
            expected=179;changed+=1
        result.append((request,expected))
    if changed!=1:raise ValueError('Exactly one prior width inventory case required')
    return result


def main_cases(collections):
    eq=lambda field,value:{'field':field,'op':'eq','value':value}
    def case(name,filters,**extra):
        request={'collection':name,'filters':filters,'limit':100,**extra}
        return request,[r for r in collections[name] if all(r.get(f['field'])==f['value'] for f in filters)]
    current=[eq('current_id',query.CURRENT)];c=query.build_contract();w=c['width_record']
    result=[case('widths',current),case('widths',[eq('id',query.WIDTH_ID)]),case('widths',[eq('source_file',query.nominal.FACTS)]),
        case('widths',current,limit=1,offset=1),case('widths',current+[eq('approximate_width_km',1000)]),
        case('widths',current+[eq('source_id',query.SOURCE_IDS[0])]),case('widths',current+[eq('width_rank_eligible',True)]),
        case('widths',current+[eq('seasonal_playback_eligible',True)]),case('widths',current+[eq('annual_extrema_eligible',True)]),
        case('objects',[eq('id',query.OWNER)]),case('sources',[eq('id',query.SOURCE_IDS[0])]),case('sources',[eq('id',query.SOURCE_IDS[1])]),
        case('widths',[eq('current_id','north-equatorial')]),case('reference_routes',current),case('widths',[eq('current_id','absent')]),
        case('widths',[eq('source_doi',w['source_doi'])]),case('widths',current,sort={'field':'approximate_width_km','direction':'desc'},limit=1),
        case('sources',[eq('year',2015)]),case('sources',[],limit=1,offset=1),
        case('widths',[eq('measurement_type','published_nominal_regional_angular_width')])]
    if len(result)!=COUNT:raise ValueError('Exact20-query nominal-width inventory required')
    return result


def verify(request,expected,response):
    sort=request.get('sort',{'field':'id','direction':'asc'})
    ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc')
    offset=request.get('offset',0)
    if response.get('ok') is not True or response.get('total')!=len(expected) or response.get('rows')!=ordered[offset:offset+request['limit']]:
        raise ValueError('Exact nominal-width filtering/sorting/pagination differs')
    if request['collection']!='widths':return
    chart=response.get('chart_scene')
    if not expected:
        if chart is not None:raise ValueError('Empty selection fabricated a width scene')
    elif chart!=runtime.width_scene(ordered):raise ValueError('Only exact matching widths may appear before pagination')
    if response.get('map_scene') is not None:raise ValueError('Nominal angular width acquired unsupported map geometry')


def verify_basin_case(request,expected,response):
    if request['collection']=='current_basin_memberships':
        sort=request.get('sort',{'field':'id','direction':'asc'})
        ordered=sorted(expected,key=lambda r:r[sort['field']],reverse=sort['direction']=='desc');offset=request.get('offset',0)
        if (response.get('ok') is not True or response.get('total')!=len(expected)
                or response.get('rows')!=ordered[offset:offset+request['limit']]
                or response.get('chart_scene')!=runtime.membership_scene(ordered) or response.get('map_scene') is not None):
            raise ValueError('Exact basin membership scene or pagination differs')
    elif request['collection']=='widths' and expected:verify(request,expected,response)
    else:basin_cases.verify(request,expected,response)
