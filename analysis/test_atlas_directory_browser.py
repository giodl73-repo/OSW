"""Atlas inventory index uses the existing identity, selection and update baseline."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':1200,'height':950});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
        page.wait_for_timeout(150)
        root=page.locator('#atlas-directory');search=root.locator('input');filter=root.locator('select').first
        def visible():return root.locator('.atlas-directory-item:not([hidden])')
        assert visible().count()==240
        filter.select_option('currents');assert visible().count()==100
        assert len(set(visible().evaluate_all('(items)=>items.map(item=>item.dataset.featureId)')))==100
        search.fill('agulhas return');assert visible().count()==1
        visible().click()
        assert page.locator('#route-atlas-select').input_value()=='current:agulhas-return'
        assert visible().get_attribute('aria-pressed')=='true'
        assert 'Agulhas Return' in page.locator('#route-atlas-preview > h3').inner_text()
        assert page.locator('#route-atlas-map').get_attribute('viewBox')!='60 90 1480 740'
        page.locator('#route-atlas-world').click();assert visible().get_attribute('aria-pressed')=='false'
        search.fill('nonesuchxyz');assert visible().count()==0
        assert 'No matching entries' in root.locator('[role=status]').inner_text()
        search.fill('');filter.select_option('eddies');assert visible().count()==140
        search.fill('shared gateway');assert visible().count()==100
        visible().first.focus();page.keyboard.press('Enter')
        assert page.locator('#route-atlas-eddy-select').input_value()
        assert 'Shared regional gateway' in page.locator('#route-atlas-preview').inner_text()
        assert visible().first.get_attribute('aria-pressed')=='true'
        page.evaluate('''()=>{const key='osw-motion-dashboard-seen-v2';const baseline=JSON.parse(localStorage.getItem(key));baseline['current:agulhas'].fingerprint='older-value';localStorage.setItem(key,JSON.stringify(baseline));}''')
        page.reload(wait_until='networkidle');page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240',timeout=90000)
        search.fill('');filter.select_option('updated');assert visible().count()==1
        assert visible().get_attribute('data-feature-id')=='current:agulhas'
        assert 'updated' in visible().get_attribute('class')
        page.locator('#route-atlas-seen').click();assert visible().count()==0
        filter.select_option('all');search.fill('');assert visible().count()==240
        root.screenshot(path=str(ROOT/'figures/atlas-directory-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        search.fill('agulhas');visible().first.click()
        assert page.locator('#route-atlas-preview').is_visible()
        assert not errors,errors
        browser.close()
    print('OK: all 100 currents and 140 eddies/detections indexed; search, map card selection, keyboard, shared gateways, updates, empty results and mobile')
if __name__=='__main__':main()
