"""Verify the custom atlas exposes every stored route/state crossing."""
import json,os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from test_rust_atlas_snapshot_browser import without_state_join


def main():
    catalog=json.loads(Path('research/ocean-current-reference-path-candidates.json').read_text(encoding='utf-8'))
    join=json.loads(Path('research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))
    grouped={}
    for row in catalog['candidates']:
        grouped.setdefault(row['current_id'],[]).append(row)
    url='http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page();errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(url,wait_until='networkidle')
        total=0
        for current,rows in grouped.items():
            page.locator('#route-atlas-select').select_option('current:'+current)
            for index,row in enumerate(rows):
                if len(rows)>1:page.locator('#route-atlas-preview button').nth(index).click()
                panel=page.locator('.route-atlas-state-links')
                expected={code:r for code,state in join['states'].items() for r in state['route_candidates'] if r['candidate_id']==row['id']}
                actual=panel.locator('li').evaluate_all('(els)=>els.map(el=>({code:el.dataset.stateCode,text:el.textContent,href:el.querySelector("a").getAttribute("href")}))')
                assert len(actual)==len(expected),row['id']
                for item in actual:
                    record=expected[item['code']]
                    assert item['href']==f'index.html?state={quote(item["code"])}#state-title',item
                    assert join['states'][item['code']]['name'] in item['text']
                    assert f'{record["crossing_scenario_count"]}/{record["scenario_count"]} declared scenarios' in item['text']
                    assert ('nominal crossing' if record['nominal_crossing'] else 'scenario-only crossing') in item['text']
                assert 'not observed passage, probabilities or seasonal occupancy' in panel.inner_text()
                total+=len(actual)
        assert total==join['counts']['candidate_state_pairs']
        page.locator('#route-atlas-select').select_option('current:agulhas')
        page.locator('.route-atlas-state-links li[data-state-code="EAFR"] a').click()
        page.wait_for_function('document.querySelector("#state-select").value==="EAFR"')
        page.wait_for_function('window.oswIndexPageReady && window.oswIndexStateContextView?.views[0]?.state_code==="EAFR"',timeout=90000)
        assert page.locator('#state-result li[data-candidate-id="agulhas-reference-path-candidate"]').count()==1
        without_state_join(page)
        page.goto(url,wait_until='networkidle')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert 'State crossing inventory unavailable' in page.locator('.route-atlas-state-links').inner_text()
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors
        browser.close()
    print(f'OK: {total} route/state links, component-specific sensitivity counts, state navigation and optional-data fallback')


if __name__=='__main__':main()
