"""Synthetic overlay mutations; no installed packet or browser is opened."""
import copy
import pytest
import eacc_connection_presentation_v3 as method


def parent():
    return {'schema':'osw.query-engine-manifest.v1','engine':'rust-osw-query-v1','abi_version':1,
            'sha256':{method.UI:'a'*64,'almanac/query-engine.wasm':'b'*64,
                      'almanac/query-data.json':'c'*64,
                      **{r['manifest_path']:r['historical_sha256'] for r in method.bindings()}},
            'earlier_delivery':{'unchanged':True}}


def test_overlay_preserves_science_prior_metadata_and_archives():
    p=parent();before=copy.deepcopy(p)
    result=method.overlay(p,b'new UI',b'SVG',control_commit='d'*40)
    assert p==before
    assert result['earlier_delivery']==p['earlier_delivery']
    assert result['sha256']['almanac/query-engine.wasm']=='b'*64
    assert result['sha256']['almanac/query-data.json']=='c'*64
    for row in method.bindings():
        if row['role']=='historical_workflow_dependency':
            assert result['sha256'][row['manifest_path']]==row['historical_sha256']
    assert len(result[method.KEY]['historical_source_archives'])==5


@pytest.mark.parametrize('case',['data','wasm','html','archive','binding','scope','extra','prior','rebuild','record'])
def test_corruption_rejects(case):
    p=parent();result=method.overlay(p,b'new UI',b'SVG',control_commit='d'*40)
    if case=='data':result['sha256']['almanac/query-data.json']='0'*64
    elif case=='wasm':result['sha256']['almanac/query-engine.wasm']='0'*64
    elif case=='html':result['sha256']['almanac/query.html']='0'*64
    elif case=='archive':result[method.KEY]['historical_source_archives']={}
    elif case=='binding':result[method.KEY]['historical_source_bindings_sha256']='0'*64
    elif case=='scope':result[method.KEY]['preexisting_navigation_pin_repairs']={}
    elif case=='extra':result['sha256']['extra']='0'*64
    elif case=='prior':result['earlier_delivery']={}
    elif case=='rebuild':result[method.KEY]['wasm_rebuild']=True
    else:result[method.KEY]['new_scientific_records']=1
    with pytest.raises(ValueError):method.validate(p,result)


@pytest.mark.parametrize('cloud,args',[(False,[]),(False,['--site','fixture','--output','fixture']),(True,[])])
def test_no_local_or_implicit_saved_data_access(monkeypatch,cloud,args):
    import sys
    import check_eacc_connection_presentation_v3 as checker
    monkeypatch.setattr(sys,'argv',['check',*args]);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    if cloud:monkeypatch.setenv('GITHUB_ACTIONS','true')
    monkeypatch.setenv('GITHUB_REF','refs/heads/codex/current-measurement-gaps')
    def forbidden(*a,**k):pytest.fail('Data or browser accessed before cloud opt-in')
    monkeypatch.setattr(checker.method,'verify_files',forbidden);monkeypatch.setattr(checker.subprocess,'Popen',forbidden)
    with pytest.raises(SystemExit) as error:checker.main()
    assert error.value.code==2


def test_workflow_and_checker_use_only_the_v2_execution_request():
    import check_eacc_connection_presentation_v3 as checker
    text=(method.ROOT/'.github/workflows/eacc-connection-presentation-v3.yml').read_text()
    assert checker.REQUEST=='research/eacc-connection-presentation-request-v3.json'
    assert checker.REQUEST in text
    assert 'presentation-request-v2.json' not in text
    assert 'group: osw-current-gap-delivery' in text
    assert 'cancel-in-progress: false' in text
