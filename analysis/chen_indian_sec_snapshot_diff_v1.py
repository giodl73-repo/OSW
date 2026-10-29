"""Read-only complete API diagnostics; no acceptance rule is relaxed."""
import hashlib
import json
import chen_indian_sec_delivery_contract_v1 as rules

def expected_snapshot(name,parent,contract,logical_sha):
    result=rules.transform_rows(parent,contract);result['bundle_sha256']=logical_sha
    if name=='dashboard':result['snapshot_json']=rules.dashboard_document(json.loads(parent['snapshot_json']),contract)
    else:
        result['regional_model_length_scenes']={'indian-south-equatorial':rules.full_scene(contract)}
        if name=='atlas':
            p='research/ocean-motion-dashboard.json'
            result['sources_json'][p]=rules.dashboard_document(json.loads(parent['sources_json'][p]),contract)
    return result

def normalized_snapshot(name,value):
    result=dict(value)
    if name=='dashboard':result['snapshot_json']=json.loads(value['snapshot_json'])
    elif name=='atlas':
        result['sources_json']=dict(value['sources_json']);p='research/ocean-motion-dashboard.json'
        result['sources_json'][p]=json.loads(value['sources_json'][p])
    return result

def differences(a,b,path=''):
    pointer=lambda key:path+'/'+str(key).replace('~','~0').replace('/','~1')
    if type(a) is not type(b):return [{'pointer':path,'kind':'type','expected':type(a).__name__,'actual':type(b).__name__}]
    if isinstance(a,dict):
        result=[{'pointer':pointer(k),'kind':'missing_key'} for k in sorted(set(a)-set(b))]
        result += [{'pointer':pointer(k),'kind':'extra_key'} for k in sorted(set(b)-set(a))]
        return result+[d for k in sorted(set(a)&set(b)) for d in differences(a[k],b[k],pointer(k))]
    if isinstance(a,list):
        return ([{'pointer':path,'kind':'length','expected':len(a),'actual':len(b)}] if len(a)!=len(b) else [])+[d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,pointer(i))]
    if a==b:return []
    if isinstance(a,str) and max(len(a),len(b))>300:
        result={'pointer':path,'kind':'text','expected_sha256':hashlib.sha256(a.encode()).hexdigest(),'actual_sha256':hashlib.sha256(b.encode()).hexdigest(),'expected_bytes':len(a.encode()),'actual_bytes':len(b.encode()),'expected_prefix':a[:160],'actual_prefix':b[:160]}
        try:
            x,y=json.loads(a),json.loads(b)
            if isinstance(x,(dict,list)) and isinstance(y,(dict,list)):
                nested=differences(x,y,path+'/[decoded JSON]');result.update(semantic_difference_count=len(nested),first_semantic_differences=nested[:20])
        except (ValueError,TypeError):pass
        return [result]
    return [{'pointer':path,'kind':'value','expected':a,'actual':b}]
