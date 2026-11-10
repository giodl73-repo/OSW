"""Synthetic archive/current corruption cases; no saved packet is opened."""
import copy
import json
import hashlib
import pytest
import eacc_connection_parent_custody_v3 as method


def fixture(root):
    manifest = {'schema': 'osw.query-engine-manifest.v1', 'engine': 'rust-osw-query-v1',
                'abi_version': 1, 'sha256': {}, 'delivery': {'dependency_proof': {'production_dependencies': []}}}
    bindings = []
    for i,(name,role) in enumerate(method.ALLOWED.items()):
        old = ('old'+str(i)).encode(); current = (json.dumps({'phase':'source-review-only-v1','heavy_work_permitted':False,'max_heavy_local_jobs':0,'max_heavy_cloud_jobs':1}).encode() if role=='historical_delivery_phase_control' else ('current'+str(i)).encode())
        target = method.local_path(root,name); target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(current)
        archive = method.ARCHIVE_ROOT+str(i)+'.source'
        old_path = method.local_path(root,archive);old_path.parent.mkdir(parents=True,exist_ok=True);old_path.write_bytes(old)
        h = lambda raw:hashlib.sha256(raw).hexdigest()
        manifest['sha256'][name] = h(old)
        bindings.append({'manifest_path':name,'role':role,'archive_path':archive,
                         'historical_commit':'0c2f0dc67a9ba25cbf488f634702b05f30401f2f',
                         'historical_sha256':h(old),'installed_path_sha256':h(current),
                         'historical_bytes':len(old),'installed_path_bytes':len(current)})
    for name in ['almanac/query-data.json','almanac/query-engine.wasm']:
        target=method.local_path(root,name);target.write_bytes(b'synthetic unchanged')
        manifest['sha256'][name]=hashlib.sha256(target.read_bytes()).hexdigest()
    return manifest,bindings


def test_all_current_and_historical_pins_verified_without_mutation(tmp_path):
    manifest,bindings=fixture(tmp_path);before=copy.deepcopy((manifest,bindings))
    result=method.verify_parent(tmp_path,tmp_path,manifest,bindings)
    assert result['manifest_paths_verified']==7 and result['current_path_matches']==2
    assert len(result['historical_bindings'])==5 and result['production_dependencies_rebound']==0
    assert (manifest,bindings)==before


@pytest.mark.parametrize('case',['archive','current','archive-size','current-size','missing','escape','role','production','duplicate','new-path'])
def test_source_bindings_cannot_hide_corruption_or_expand_scope(tmp_path,case):
    manifest,bindings=fixture(tmp_path);row=bindings[0]
    if case=='archive':method.local_path(tmp_path,row['archive_path']).write_bytes(b'changed')
    elif case=='current':method.local_path(tmp_path,row['manifest_path']).write_bytes(b'changed')
    elif case=='archive-size':row['historical_bytes']+=1
    elif case=='current-size':row['installed_path_bytes']+=1
    elif case=='missing':method.local_path(tmp_path,row['archive_path']).unlink()
    elif case=='escape':row['archive_path']=method.ARCHIVE_ROOT+'../../outside'
    elif case=='role':row['role']='data'
    elif case=='production':manifest['delivery']['dependency_proof']['production_dependencies']=[row['manifest_path']]
    elif case=='duplicate':bindings.append(copy.deepcopy(row))
    else:row['manifest_path']='almanac/query-engine.wasm'
    with pytest.raises(ValueError):method.verify_parent(tmp_path,tmp_path,manifest,bindings)


def test_collects_all_unrecognized_mismatches_including_data_and_wasm(tmp_path):
    manifest,bindings=fixture(tmp_path)
    for path in ['almanac/query-data.json','almanac/query-engine.wasm']:
        method.local_path(tmp_path,path).write_bytes(b'corrupted')
    with pytest.raises(method.ParentCustodyError) as error:
        method.verify_parent(tmp_path,tmp_path,manifest,bindings)
    assert {f['path'] for f in error.value.failures}=={'almanac/query-data.json','almanac/query-engine.wasm'}


@pytest.mark.parametrize('field,value',[('phase','indian-coastal-context-v1'),('heavy_work_permitted',True),('max_heavy_local_jobs',1),('max_heavy_cloud_jobs',2)])
def test_even_rehashed_live_phase_cannot_authorize_heavy_work(tmp_path,field,value):
    manifest,bindings=fixture(tmp_path)
    row=next(r for r in bindings if r['role']=='historical_delivery_phase_control')
    target=method.local_path(tmp_path,row['manifest_path'])
    phase=json.loads(target.read_bytes());phase[field]=value
    raw=json.dumps(phase).encode();target.write_bytes(raw)
    row['installed_path_sha256']=hashlib.sha256(raw).hexdigest();row['installed_path_bytes']=len(raw)
    with pytest.raises(method.ParentCustodyError,match='remain disabled'):
        method.verify_parent(tmp_path,tmp_path,manifest,bindings)
