"""Bounded-report support only: never decides delivery acceptance."""
import chen_indian_sec_snapshot_diff_v1 as prior


def differences(a, b, path=''):
    pointer=lambda key:path+'/'+str(key).replace('~','~0').replace('/','~1')
    numeric=lambda value:type(value) in (int,float)
    if numeric(a) and numeric(b):
        return [] if a==b else [{'pointer':path,'kind':'number','expected':a,'actual':b}]
    if type(a) is not type(b):
        return [{'pointer':path,'kind':'type','expected':type(a).__name__,'actual':type(b).__name__}]
    if isinstance(a,dict):
        result=[{'pointer':pointer(k),'kind':'missing_key'} for k in sorted(set(a)-set(b))]
        result += [{'pointer':pointer(k),'kind':'extra_key'} for k in sorted(set(b)-set(a))]
        return result+[d for k in sorted(set(a)&set(b)) for d in differences(a[k],b[k],pointer(k))]
    if isinstance(a,list):
        result=[] if len(a)==len(b) else [{'pointer':path,'kind':'length','expected':len(a),'actual':len(b)}]
        return result+[d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,pointer(i))]
    return prior.differences(a,b,path)
