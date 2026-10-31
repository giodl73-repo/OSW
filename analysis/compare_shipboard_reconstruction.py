"""Allow submicrometre geodesic roundoff; retain every source/operator exactly."""
import math


def matches(saved,calculated):
    schema='osw.shipboard-layer-component-spans.v1'
    if not isinstance(saved,dict) or not isinstance(calculated,dict) or saved.get('schema')!=schema or calculated.get('schema')!=schema:
        return False

    def compare(a,b,path=()):
        if type(a) is not type(b): return False
        if isinstance(a,dict):
            return a.keys()==b.keys() and all(compare(a[k],b[k],path+(k,)) for k in a)
        if isinstance(a,list):
            return len(a)==len(b) and all(compare(x,y,path+(i,)) for i,(x,y) in enumerate(zip(a,b)))
        if isinstance(a,float):
            if not math.isfinite(a) or not math.isfinite(b): return False
            geodesic=(len(path)==5 and path[0]=='rows' and isinstance(path[1],int)
                      and path[2]=='threshold_cases' and isinstance(path[3],int)
                      and path[4]=='survey_span_km')
            if geodesic: return math.isclose(a,b,rel_tol=0,abs_tol=1e-10)
        return a==b

    return compare(saved,calculated)
