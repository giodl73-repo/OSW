"""The proposal card reaches typed branch data without canonical transfer."""
import os
from playwright.sync_api import sync_playwright, expect

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#inventory-addition-norwegian-atlantic-slope')
        card=page.locator('#inventory-addition-norwegian-atlantic-slope')
        expect(card).to_contain_text('Additional measurements for this proposed branch',timeout=60000)
        expect(card).to_contain_text('25–30 km')
        expect(card).to_contain_text('no dimensions assigned to Norwegian Current or Norwegian Coastal Current')
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        card.get_by_role('link',name='Compare proposed branch section widths',exact=True).click()
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        result=page.evaluate('window.oswLastQueryResult')
        assert result['collection']=='proposed_widths' and result['total']==5
        assert all(r['proposed_current_id']=='norwegian-atlantic-slope' and 'current_id' not in r for r in result['rows'])
        assert result['map_scene'] is None
        expect(page.locator('.nordic-section-width').first).to_contain_text('Proposed identity only')
        assert not errors,errors
        browser.close()
    print('PASS: proposed slope card, 320 px layout, query navigation, five qualified records and no canonical dimensions')

if __name__=='__main__':main()
