"""Taxonomy closure, source rejection, scoped measurements and browser navigation."""
import copy,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI,native,browser_query
ROOT=Path(__file__).resolve().parents[1]

def query(root,relation='descendants',include=False):return {'collection':'objects','taxonomy':{'root_id':root,'relation':relation,'include_root':include},'limit':100}
def main():
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes());ledger=json.loads((ROOT/'research/ocean-current-almanac.json').read_bytes())
    parent={"current:"+r['id']:"current:"+r['part_of_system'] for r in ledger['entries'] if r.get('part_of_system')}
    roots=set(parent)|set(parent.values());roots.add('eddy:horizon:loop-81-primary')
    def expected(root,relation):
        if relation=='parents':return {parent[root]} if root in parent else set()
        if relation=='children':return {c for c,p in parent.items() if p==root}
        result=set();frontier=[root]
        while frontier:
            children=expected(frontier.pop(),'children' if relation=='descendants' else 'parents')-result
            result.update(children);frontier.extend(children)
        return result
    for root in sorted(roots):
        for relation in ['children','parents','descendants','ancestors']:
            r=native(query(root,relation));assert r['ok'],r
            assert {x['id'] for x in r['rows']}==expected(root,relation),(root,relation,r)
    family=query('current:equatorial-countercurrent');result=native(family);assert result['total']==7
    assert native(query('current:equatorial-countercurrent',include=True))['total']==8
    byid={r['id']:r for r in bundle['collections']['objects']}
    for r in result['rows']:assert r['width_ids']==byid[r['id']]['width_ids'] and r['published_length_km']==byid[r['id']]['published_length_km']
    assert byid['current:equatorial-countercurrent']['width_ids']==[]
    selected={**family,'filters':[{'field':'identity_level','op':'eq','value':'current'},{'field':'capabilities.scoped_width','op':'gt','value':0}]}
    narrow=native(selected);assert narrow['total']==3
    assert native({**family,'collection':'widths'})['ok'] is False
    assert native(query('current:missing'))['ok'] is False
    assert native(query('current:equatorial-countercurrent','flow_connectivity'))['ok'] is False
    cases=[]
    for key,value in [('parent_id','current:agulhas'),('child_label','wrong'),('measurement_inheritance_eligible',True),('source_pointer','/entries/0/part_of_system')]:
        bad=copy.deepcopy(bundle);bad['collections']['taxonomy_links'][0][key]=value;cases.append(bad)
    bad=copy.deepcopy(bundle);bad['collections']['taxonomy_links'].pop();cases.append(bad)
    bad=copy.deepcopy(bundle);bad['collections']['objects'][0]['identity_level']='family';cases.append(bad)
    bad=copy.deepcopy(bundle);bad['manifest']['taxonomy']['source_receipts'][0]['source_json']+=' ';cases.append(bad)
    bad=copy.deepcopy(bundle);bad['manifest']['taxonomy']['identity_levels']['family']='incorrect scope';cases.append(bad)
    with tempfile.TemporaryDirectory() as directory:
        for i,bad in enumerate(cases):
            path=Path(directory)/'bad.json';path.write_text(json.dumps(bad),encoding='utf-8');run=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True)
            assert run.returncode==2 and not run.stdout,(i,run.stderr)
    browser_navigation(family,result,selected,narrow)
    print('PASS: complete declared graph closures, eight loader rejections, no measurement inheritance, native/WASM and builder/filter/share/parent/card/mobile navigation')
def browser_navigation(family,result,selected,narrow):
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert browser_query(page,family)==result
        expect(page.locator('#query-taxonomy-root')).to_have_value('current:equatorial-countercurrent')
        expect(page.locator('#query-status')).to_contain_text('not flow connectivity')
        assert browser_query(page,selected)==narrow
        page.locator('#query-run').click();page.wait_for_function('!document.querySelector("#query-run").disabled')
        assert page.evaluate('window.oswLastQueryResult.total')==3
        assert len(json.loads(page.locator('#query-json').input_value())['filters'])==2
        share=page.locator('#query-share').get_attribute('href');page.goto(share);page.wait_for_function('window.oswLastQueryResult?.total===3',timeout=60000)
        expect(page.locator('#query-identity-level')).to_have_value('current')
        page.locator('#query-rows button').filter(has_text='Pacific North Equatorial Countercurrent').click()
        expect(page.locator('#query-detail')).to_contain_text('Declared identity memberships (1 parents, 0 children)')
        page.get_by_role('button',name='North Equatorial Countercurrent',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text('Declared identity memberships (1 parents, 2 children)')
        assert 'inspect=current%3Anorth-equatorial-countercurrent' in page.locator('#query-share').get_attribute('href')
        parent_share=page.locator('#query-share').get_attribute('href');page.goto(parent_share);page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=60000)
        expect(page.locator('#query-detail')).to_contain_text('Declared identity memberships (1 parents, 2 children)')
        expect(page.locator('#query-detail')).to_contain_text('Parent families or systems')
        expect(page.locator('#query-detail')).to_contain_text('Declared members or components')
        page.locator('#query-detail').screenshot(path=str(ROOT/'figures/query-taxonomy-membership-review.png'))
        page.get_by_role('button',name='Query all declared descendants',exact=True).click()
        page.wait_for_function('window.oswLastQueryResult?.total===2')
        assert {r['id'] for r in page.evaluate('window.oswLastQueryResult.rows')}=={'current:atlantic-north-equatorial-countercurrent','current:pacific-north-equatorial-countercurrent'}
        membership=browser_query(page,{'collection':'taxonomy_links','filters':[{'field':'child_id','op':'eq','value':'current:pacific-north-equatorial-countercurrent'}]});assert membership['total']==1
        page.locator('#query-rows button').first.focus();page.locator('#query-rows button').first.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('naming reference does not independently establish')
        parent_button=page.get_by_role('button',name='North Equatorial Countercurrent',exact=True);parent_button.focus();parent_button.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Declared identity memberships (1 parents, 2 children)')
        assert 'inspect=current%3Anorth-equatorial-countercurrent' in page.locator('#query-share').get_attribute('href')
        page.locator('[data-preset="countercurrent-family"]').click();page.wait_for_function('window.oswLastQueryResult?.total===7')
        page.locator('#query-taxonomy-include').check();page.locator('#query-run').click();page.wait_for_function('window.oswLastQueryResult?.total===8')
        page.set_viewport_size({'width':320,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert not errors,errors;browser.close()

if __name__=='__main__':main()
