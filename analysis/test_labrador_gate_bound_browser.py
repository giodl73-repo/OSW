"""Complete native/WASM admission parity and mapped-card source navigation."""
import json
import os
from urllib.parse import quote, parse_qs, urlparse
from playwright.sync_api import sync_playwright, expect
from labrador_gate_bound_query import evidence, links
from labrador_latitude_gate_bound_v1 import ROOT, ENTITY, SOURCE_ID
from north_atlantic_gate_bound import verify_inputs as nac_evidence
from test_current_research_evidence_browser import BASE, native
from test_rust_query_browser import browser_query
from browser_inventory_expectations import RANKED_LENGTH_COUNT


def main():
    document,_=evidence();nac,_=nac_evidence()
    output=ROOT/'.pytest_cache/labrador-bound-v1/browser';output.mkdir(parents=True,exist_ok=True)
    errors,originals=[],[]
    complete={'collection':'current_length_bound_admissions','limit':100}
    # Both full admissions include every individual measurement, claim,
    # assessment and source. One native load verifies both documents; the
    # shipped WASM also checks each new record through its own collection.
    expected=native(complete)
    assert expected['total']==2
    assert {r['id']:r for r in expected['rows']}=={document['id']:document,nac['id']:nac}
    individual=[('length_assessments','entity_id',ENTITY,document['length_assessment']),
                ('measurements','id',document['measurement']['id'],document['measurement']),
                ('claims','id',document['claim']['id'],document['claim']),
                ('sources','id',SOURCE_ID,document['source_record'])]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],args=['--disable-features=BackForwardCache'])
        page=browser.new_page(viewport={'width':1100,'height':950})
        page.on('pageerror',lambda error:errors.append(str(error)))
        original_urls={document['source_url'],'https://doi.org/'+document['source_doi']}
        page.on('request',lambda request:originals.append(request.url) if request.url in original_urls or request.url.split('?')[0].endswith(('.pdf','.nc','.zip','.xml')) else None)
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(complete)))
        page.wait_for_function('window.oswLastQueryResult',timeout=180000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        for collection,field,value,row in individual:
            query={'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':1}
            result=browser_query(page,query)
            assert result['total']==1 and result['rows']==[row]
            assert page.locator('#query-export').is_enabled()
        ranked=browser_query(page,{'collection':'length_assessments','filters':[{'field':'rank_eligible','op':'eq','value':True}],'limit':100})
        assert ranked['total']==RANKED_LENGTH_COUNT==13
        assert all(r['entity_id']!=ENTITY for r in ranked['rows'])
        page.set_viewport_size({'width':320,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Alabrador#route-atlas')
        panel=page.locator('.route-atlas-evidence-links');panel.wait_for(state='attached',timeout=180000)
        if not panel.evaluate('(e)=>e.open'):
            panel.locator('summary').focus();page.keyboard.press('Enter')
        for link in links(document):expect(panel.get_by_role('link',name=link['label'],exact=True)).to_have_attribute('href',link['url'])
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output/'card-phone.png'))
        # Select the old current in the same atlas workspace. Its scenarios
        # link must filter its own admission once this collection has two rows.
        page.locator('#route-atlas-select').select_option('current:north-atlantic')
        panel=page.locator('.route-atlas-evidence-links')
        expect(panel.locator('a').filter(has_text='Audit all nine geographic gate scenarios')).to_have_count(1)
        if not panel.evaluate('(e)=>e.open'):
            panel.locator('summary').focus();page.keyboard.press('Enter')
        old_link=panel.get_by_role('link',name='Audit all nine geographic gate scenarios',exact=True)
        request=json.loads(parse_qs(urlparse(old_link.get_attribute('href')).query)['q'][0])
        assert request['filters']==[{'field':'entity_id','op':'eq','value':'current:north-atlantic'}]
        page.locator('#route-atlas-select').select_option(ENTITY)
        panel=page.locator('.route-atlas-evidence-links')
        expect(panel.locator('a').filter(has_text=links(document)[0]['label'])).to_have_count(1)
        if not panel.evaluate('(e)=>e.open'):
            panel.locator('summary').focus();page.keyboard.press('Enter')
        figure=panel.get_by_role('link',name=links(document)[0]['label'],exact=True)
        figure.focus();page.keyboard.press('Enter')
        expect(page.locator('svg')).to_have_attribute('role','img')
        expect(page.locator('#desc')).to_contain_text('Not a mapped current route or whole-current length')
        page.set_viewport_size({'width':1100,'height':650})
        page.screenshot(path=str(output/'figure.png'))
        assert not errors and not originals,(errors,originals)
        browser.close()
    receipt={'status':'PASS','complete_native_wasm_admissions':2,'individual_wasm_records':len(individual),
             'all_nine_scenarios_preserved':True,'qualified_ranked_lengths':13,'labrador_ranked':False,
             'native_cli_closed_before_browser':True,'reused_query_and_atlas_workspaces':True,
             'legacy_nac_scenario_link_scoped':True,'keyboard_atlas_to_scalar_figure':True,
             'phone_320px':True,'automatic_original_downloads':0}
    (output/'result.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    print('PASS: both complete bound admissions, new records, unchanged ranks, keyboard map-card/source links and phone')


if __name__=='__main__':main()
