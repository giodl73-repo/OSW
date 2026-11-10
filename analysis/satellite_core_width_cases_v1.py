"""Twelve explicit source/owner/filter/pagination cases for the width append."""
import published_satellite_core_widths_v1 as core


def adapt_legacy_cases(cases):
    """Change only the declared total affected by this exact two-row append."""
    result=[];changes=0
    for query,expected in cases:
        if query=={'collection':'widths','limit':1}:
            if type(expected) is not int or expected!=172:raise ValueError('Exact historical172-width expectation required')
            expected=174;changes+=1
        result.append((query,expected))
    if changes!=1:raise ValueError('Exactly one historical width inventory case required')
    return result


def main_cases(collections):
    new=core.records();all_agulhas=[r for r in collections['widths'] if r['current_id']=='agulhas']
    if len(all_agulhas)!=4:raise ValueError('Four Agulhas scoped widths required')
    by_source=[{'field':'source_file','op':'eq','value':core.SOURCE}]
    def widths(filters,rows,**extra):return ({'collection':'widths','filters':filters,'limit':100,**extra},rows)
    result=[widths(by_source,new)]
    for row in new:result.append(widths([{'field':'id','op':'eq','value':row['id']}],[row]))
    result.append(widths(by_source,new,sort={'field':'id','direction':'desc'},offset=1,limit=1))
    result.append(widths([{'field':'current_id','op':'eq','value':'agulhas'}],all_agulhas))
    result.append(widths([{'field':'current_id','op':'eq','value':'agulhas'}],all_agulhas,offset=3,limit=1))
    result.append(widths(by_source+[{'field':'current_id','op':'eq','value':'other'}],[]))
    result.append(widths([{'field':'id','op':'eq','value':'missing-satellite-width'}],[]))
    result.append(({'collection':'objects','filters':[{'field':'id','op':'eq','value':core.OWNER}],'limit':100},[r for r in collections['objects'] if r['id']==core.OWNER]))
    result.append(widths(by_source,new,offset=1,limit=1))
    result.append(widths(by_source,new,offset=2,limit=1))
    result.append(widths([{'field':'width_metric','op':'eq','value':'satellite_gaussian_core_mean'}],[new[0]]))
    if len(result)!=12:raise ValueError('Twelve explicit width cases required')
    return result


def verify_response(query,expected,response):
    ordered=sorted(expected,key=lambda r:r['id'],reverse=query.get('sort',{}).get('direction')=='desc')
    offset=query.get('offset',0);selected=ordered[offset:offset+query['limit']]
    if response.get('ok') is not True or response['total']!=len(ordered) or response['rows']!=selected:raise ValueError('Satellite case rows, owner or pagination differ')
    scene=response.get('chart_scene');scenes=scene.get('scenes',[scene]) if isinstance(scene,dict) else []
    matches=[s for s in scenes if s.get('kind')=='published_satellite_core_widths']
    wanted=[r for r in ordered if r.get('satellite_core_context') is not None] if query['collection']=='widths' else []
    if wanted:
        if len(matches)!=1 or sorted(matches[0]['records'],key=lambda r:r['id'])!=sorted(wanted,key=lambda r:r['id']):raise ValueError('Satellite scene does not reflect all filtered matches')
        if len(wanted)==len(ordered) and response.get('map_scene') is not None:raise ValueError('Unreported satellite width geometry invented')
    elif matches:raise ValueError('Unexpected satellite scene')
