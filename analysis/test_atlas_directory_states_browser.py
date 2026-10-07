"""State-filtered atlas identities agree with the saved route and eddy evidence."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788/almanac/reference-routes.html'
def main():
    joins=json.loads((ROOT/'research/ocean-current-reference-route-state-join.json').read_text(encoding='utf-8'))['states']
    rows=json.loads((ROOT/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))['entries']
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(BASE+'#atlas-directory',wait_until='networkidle')
        state=page.locator('#atlas-directory-state');root=page.locator('#atlas-directory')
        visible=root.locator('.atlas-directory-item:not([hidden])');filter=root.locator('select').first
        expect(state.locator('option')).to_have_count(len(joins)+1,timeout=90000)
        for code,record in joins.items():
            expected={'current:'+route['current_id'] for route in record['route_candidates']}
            expected.update(row['id'] for row in rows if any(e['state_code']==code for e in row.get('state_evidence',[])))
            state.select_option(code)
            actual=set(visible.evaluate_all('(items)=>items.map(item=>item.dataset.featureId)'))
            assert actual==expected,(code,actual^expected)
            assert root.locator('[role=status]').inner_text().startswith(f'{len(expected)} of 240 entries')
            assert code in root.locator('.atlas-directory-state-note').inner_text()
        state.select_option('PSAW');filter.select_option('currents')
        assert visible.count()==3
        extension=visible.filter(has_text='Kuroshio Extension')
        assert 'Alternative reference-route crossing only' in extension.inner_text()
        extension.click();assert page.locator('#route-atlas-select').input_value()=='current:kuroshio-extension'
        assert 'atlas-state=PSAW' in page.url
        state.select_option('CAMR')
        assert 'atlas-state=CAMR' in page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        state.select_option('PSAW')
        page.reload(wait_until='networkidle')
        expect(state).to_have_value('PSAW',timeout=90000)
        expect(page.locator('#route-atlas-select')).to_have_value('current:kuroshio-extension',timeout=90000)
        page.locator('#route-atlas-world').click();assert state.input_value()=='PSAW'
        state.select_option('CAMR')
        filter.select_option('eddies')
        gateway=visible.filter(has_text='Shared gateway')
        expected_gateways=sum(any(e['state_code']=='CAMR' for e in row.get('state_evidence',[])) and any(f['role']=='shared_regional_gateway' for f in row['map_features']) for row in rows)
        assert gateway.count()==expected_gateways
        gateway.first.focus();page.keyboard.press('Enter')
        assert 'Shared regional gateway' in page.locator('#route-atlas-preview').inner_text()
        assert 'atlas-state=CAMR' in page.locator('#route-atlas-preview [data-atlas-share]').get_attribute('href')
        dated=next(row for row in rows if row['type']=='operational_eddy_detection' and row.get('state_evidence'))
        evidence=dated['state_evidence'][0];state.select_option(evidence['state_code'])
        item=root.locator(f'[data-feature-id="{dated["id"]}"]')
        assert evidence['observation_date'] in item.inner_text()
        item.click();assert evidence['observation_date'] in page.locator('#route-atlas-preview').inner_text()
        state.select_option('BERS');assert 'No matching entries' in root.locator('[role=status]').inner_text()
        state.select_option('PSAW');filter.select_option('all');root.screenshot(path=str(ROOT/'figures/atlas-state-directory-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.goto(BASE+'?atlas-state=INVALID#atlas-directory',wait_until='networkidle')
        expect(state.locator('option')).to_have_count(len(joins)+1,timeout=90000)
        assert state.input_value()=='' and 'atlas-state=' not in page.url
        from test_rust_atlas_snapshot_browser import without_state_join
        without_state_join(page)
        page.reload(wait_until='networkidle')
        expect(root.locator('.atlas-directory-state-note')).to_contain_text('Current route-state links are unavailable',timeout=90000)
        assert 'Current route-state links are unavailable' in root.locator('.atlas-directory-state-note').inner_text()
        assert not errors,errors
        browser.close()
    print(f'OK: all {len(joins)} OSW state identity sets, alternative/nominal scope, dated eddy labels, shared gateways, saved state/card restore, invalid state, missing join and mobile')
if __name__=='__main__':main()
