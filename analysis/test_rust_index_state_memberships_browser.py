"""All 56 state membership inventories: source joins, evidence kinds and UI parity."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(name):return json.loads((ROOT/'research'/name).read_bytes())
    join=read('ocean-motion-state-join.json')
    cartographic=read('cartographic-ocean-current-state-join.json')
    crosswalk=read('nasa-ocean-object-state-crosswalk.json')
    nm=read('nasa-object-state-relation-matrix.json')
    cm=read('ocean-current-state-relation-matrix.json')
    geography=read('named-eddy-geography-join.json')
    currents={r['id']:r for r in read('ocean-current-almanac.json')['entries']}
    nasa={r['id']:r for r in read('nasa-perpetual-ocean-objects.json')['objects']}
    names={r['id']:r for r in read('named-eddy-geography.json')['entries']}
    definitions=[('current','schematic_current_centerline_crossings',join,None),
                 ('current','stable_cartographic_current_crossings',cartographic,'stable'),
                 ('current','width_sensitive_cartographic_contacts',cartographic,'width_sensitive'),
                 ('current','editorial_nasa_current_line_crossings',join,None),
                 ('current','editorial_named_current_line_crossings',join,None),
                 ('nasa','cartographic_current_crossings',crosswalk,'stable'),
                 ('nasa','width_sensitive_cartographic_contacts',crosswalk,'width_sensitive'),
                 ('nasa','schematic_current_crossings',crosswalk,None),
                 ('nasa','schematic_object_crossings',crosswalk,None),
                 ('nasa','editorial_current_line_crossings',crosswalk,None),
                 ('current','current_locator_candidates',join,None),
                 ('nasa','nasa_object_locator_candidates',join,None),
                 ('eddy-geography','locators',geography,None)]
    codes=list(join['states'])
    def member(id,prefix,code,arrow=None):
        ledger={'current':currents,'nasa':nasa,'eddy-geography':names}[prefix]
        ids=(nm['states'][code]['objects'][id] if prefix=='nasa' else cm['states'][code]['currents'][id])['cartographic_source_arrow_ids'][arrow] if arrow else []
        return {'id':id,'name':ledger[id]['name'],'record':ledger[id],'source_arrow_ids':ids}
    def verify(view):
        code=view['state_code']
        assert view['state']==join['states'][code]
        assert view['current_count']==cm['current_count']
        assert view['atlas_linked_current_count']==cm['states'][code]['atlas_linked_current_count']
        assert view['nasa_object_count']==nm['object_count']
        assert view['atlas_linked_object_count']==nm['states'][code]['atlas_linked_object_count']
        assert len(view['groups'])==13
        for group,(prefix,key,source,arrow) in zip(view['groups'],definitions):
            ids=source['states'][code] if key=='locators' else source['states'][code][key]
            assert group['prefix']==prefix and group['kind']==key
            assert group['members']==[member(id,prefix,code,arrow) for id in ids],(code,key)
        relations=nm['states'][code]['objects']
        assert list(relations)==list(nasa), 'Source pair order must follow the original NASA ledger'
        unresolved=[];contexts=[]
        for id,r in relations.items():
            if r['atlas_relation']=='unresolved':unresolved.append({**member(id,'nasa',code),'relation':r})
            if r['contextual_members']:
                contexts.append({'object':member(id,'nasa',code),'relation':r,
                                 'members':[{**member(m['object_id'],'nasa',code),'relation':m} for m in r['contextual_members']]})
        assert view['unresolved_nasa']==unresolved
        assert view['contextual_classes']==contexts
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet=Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        request={'state_codes':codes}
        run=subprocess.run([str(CLI),'--index',str(packet),'--state-memberships','-'],input=json.dumps(request),
                           capture_output=True,text=True,encoding='utf-8')
        assert run.returncode==0,run.stderr
        expected=json.loads(run.stdout)
        assert expected['state_count']==56
        assert expected['current_claim_limit']==cm.get('claim_limit')
        assert expected['nasa_claim_limit']==nm['claim_limit']
        assert len(expected['views'])==56
        for view in expected['views']:verify(view)
        by_code={v['state_code']:v for v in expected['views']}
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html?state=GFST')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('r=>oswIndexStateMemberships(r)',request)==expected
            for code in codes:
                page.locator('#state-select').select_option(code)
                page.wait_for_function('code=>oswIndexStateMembershipView?.state_code===code',arg=code,timeout=90000)
                assert page.evaluate('oswIndexStateMembershipView')==by_code[code]
                groups=page.locator('#state-result .state-groups > div')
                assert groups.count()==13
                for i,group in enumerate(by_code[code]['groups']):
                    dom=groups.nth(i)
                    assert dom.get_attribute('data-membership-kind')==group['prefix']+':'+group['kind']
                    assert dom.locator('h4').text_content()==group['title'], (code, i, dom.locator('h4').text_content(), group['title'])
                    assert dom.locator('h4').inner_text()==group['title'].upper()
                    assert dom.locator('a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[
                        '#'+group['prefix']+'-'+m['id'] for m in group['members']]
                    assert dom.locator('a').all_text_contents()==[m['name'] for m in group['members']]
                    if not group['members']:assert dom.locator('li').inner_text()==group['fallback']
                    for j,m in enumerate(group['members']):
                        if m['source_arrow_ids']:assert 'source arrow '+', '.join(map(str,m['source_arrow_ids'])) in dom.locator('li').nth(j).inner_text()
                unknown=page.locator('#state-result .nasa-unresolved-details')
                assert unknown.locator('a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[
                    '#nasa-'+m['id'] for m in by_code[code]['unresolved_nasa']]
                contexts=by_code[code]['contextual_classes']
                panel=page.locator('#state-result details').filter(has=page.locator('summary').filter(has_text='NASA classes or systems with indexed examples here'))
                assert panel.count()==(1 if contexts else 0)
                if contexts:
                    assert panel.locator('a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==[
                        '#nasa-'+m['id'] for context in contexts for m in [context['object'],*context['members']]]
            for request in [{'state_code':'invented'},{'state_codes':['GFST','GFST']},{'state_code':'GFST','state_codes':['GFST']},{'extra':True}]:
                assert page.evaluate('r=>oswIndexStateMemberships(r).then(()=>false,()=>true)',request)
            page.locator('#state-select').select_option('GFST');page.locator('#state-select').select_option('CAMR');page.locator('#state-select').select_option('KURO')
            page.wait_for_function("oswIndexStateMembershipView?.state_code==='KURO'")
            assert page.evaluate('oswIndexStateMembershipView')==by_code['KURO']
            assert 'state=KURO' in page.url
            page.locator('#state-select').select_option('')
            page.wait_for_function('oswIndexStateMembershipView===null')
            assert 'Choose a state' in page.locator('#state-result').inner_text()
            assert 'state=' not in page.url
            assert page.locator('#state-count').inner_text()=='56 states'
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert not errors,errors
            browser.close()
    print('PASS: all 56 states, 13 distinct evidence groups, source names/arrows, NASA context/unresolved pairs, native/WASM and DOM parity, invalid batches and rapid selection')


if __name__=='__main__':main()
