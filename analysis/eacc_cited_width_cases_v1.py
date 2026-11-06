"""Source-bound EACC filters and the one changed inventory expectation."""
import published_eacc_cited_width_constraint_v1 as core


def adapt_legacy_cases(cases):
    result=[];changes=0
    for query,expected in cases:
        if query=={'collection':'widths','limit':1}:
            if type(expected) is not int or expected!=175:
                raise ValueError('Exact preceding 175-width expectation required')
            expected=176;changes+=1
        result.append((query,expected))
    if changes!=1:raise ValueError('Exactly one prior width inventory case required')
    return result


def main_cases(collections):
    row=core.record()
    def widths(filters,rows,**extra):return ({'collection':'widths','filters':filters,'limit':100,**extra},rows)
    by_id=[{'field':'id','op':'eq','value':core.ID}]
    by_source=[{'field':'source_file','op':'eq','value':core.SOURCE}]
    by_owner=[{'field':'current_id','op':'eq','value':'east-african-coastal'}]
    return [widths(by_id,[row]),widths(by_source,[row]),widths(by_owner,[row]),
        widths(by_source,[row],offset=1,limit=1),
        widths(by_owner,[row],sort={'field':'id','direction':'desc'},limit=1),
        widths(by_source+[{'field':'current_id','op':'eq','value':'agulhas'}],[]),
        widths([{'field':'id','op':'eq','value':'missing-eacc-constraint'}],[]),
        ({'collection':'objects','filters':[{'field':'id','op':'eq','value':core.OWNER}],'limit':100},
         [r for r in collections['objects'] if r['id']==core.OWNER]),
        widths(by_source+[{'field':'reported_operator','op':'eq','value':'gt'}],[row]),
        widths(by_source+[{'field':'reported_operator','op':'eq','value':'gte'}],[])]


def verify_response(query,expected,response):
    ordered=sorted(expected,key=lambda r:r['id'],reverse=query.get('sort',{}).get('direction')=='desc')
    offset=query.get('offset',0);selected=ordered[offset:offset+query['limit']]
    if response.get('ok') is not True or response['total']!=len(ordered) or response['rows']!=selected:
        raise ValueError('Review width rows, owner or pagination differ')
    scene=response.get('chart_scene');scenes=scene.get('scenes',[scene]) if isinstance(scene,dict) else []
    found=[s for s in scenes if s.get('kind')=='published_cited_width_constraints']
    wanted=[r for r in ordered if r.get('id')==core.ID] if query['collection']=='widths' else []
    if wanted:
        if len(found)!=1 or found[0]['records']!=wanted:raise ValueError('Review scene differs from filtered matches')
        if response.get('map_scene') is not None:raise ValueError('Unreported review width geometry invented')
    elif found:raise ValueError('Unrelated query contains a review width scene')
