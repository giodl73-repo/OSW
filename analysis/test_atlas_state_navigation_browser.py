"""State map navigation reuses masked OSW geometry and the inventory filter."""
import os,xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];BASE='http://127.0.0.1:8788/almanac/reference-routes.html'
def main():
    source=ET.parse(ROOT/'figures/ocean-motion-dashboard-ground.svg').getroot()
    shapes={g.attrib['data-code']:[p.attrib['d'] for p in g.findall('{http://www.w3.org/2000/svg}path')] for g in source.iter() if 'data-code' in g.attrib and g.tag.endswith('}g')}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'),headless=True)
        page=browser.new_page(viewport={'width':1200,'height':900});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(BASE+'#route-atlas',wait_until='networkidle')
        expect(page.locator('.atlas-state-region')).to_have_count(56,timeout=90000)
        expect(page.locator('#atlas-directory-state option')).to_have_count(57,timeout=90000)
        region=page.locator('.atlas-state-region');state=page.locator('#atlas-directory-state')
        for code,paths in shapes.items():
            item=page.locator(f'.atlas-state-region[data-state-code="{code}"]')
            assert item.locator('path').evaluate_all('(items)=>items.map(item=>item.getAttribute("d"))')==paths,(code,paths,item.locator('path').evaluate_all('(items)=>items.map(item=>item.getAttribute("d"))'))
            item.focus();page.keyboard.press('Enter');assert state.input_value()==code
            assert item.get_attribute('aria-pressed')=='true'
            assert page.evaluate('document.activeElement.id')=='atlas-directory-state',(code,page.evaluate('document.activeElement.id'))
            assert page.locator('.atlas-state-region[aria-pressed=true]').count()==1
        state.select_option('PSAW');assert page.locator('[data-state-code=PSAW]').get_attribute('aria-pressed')=='true'
        page.locator('#route-atlas-map').scroll_into_view_if_needed()
        land_hits=page.evaluate("""()=>{const svg=document.querySelector('#route-atlas-map'),box=svg.getBoundingClientRect();return [[-100,40],[20,5],[100,45]].map(([lon,lat])=>{const x=box.left+(lon+180)/360*box.width,y=box.top+(90-lat)/180*box.height;return Boolean(document.elementFromPoint(x,y)?.closest('.atlas-state-region'));});}""")
        assert land_hits==[False,False,False],land_hits
        hit=page.evaluate('''()=>{const svg=document.querySelector('#route-atlas-map'),rect=svg.getBoundingClientRect();for(let y=rect.top+10;y<rect.bottom-10;y+=15)for(let x=rect.left+10;x<rect.right-10;x+=15){const button=document.elementFromPoint(x,y)?.closest('.atlas-state-region');if(button&&button.dataset.stateCode!=='PSAW')return {x,y,code:button.dataset.stateCode};}return null;}''')
        assert hit;page.mouse.click(hit['x'],hit['y']);assert state.input_value()==hit['code']
        page.locator('#route-atlas-map').scroll_into_view_if_needed()
        point=page.locator('#route-atlas-map .route-atlas-station').first
        point.focus();page.keyboard.press('Enter');assert page.locator('#route-atlas-select').input_value()
        state.select_option('PSAW');page.locator('#route-atlas-world').click()
        page.locator('#route-atlas-map').screenshot(path=str(ROOT/'figures/atlas-clickable-states-review.png'))
        page.reload(wait_until='networkidle');expect(state).to_have_value('PSAW',timeout=90000)
        assert page.locator('[data-state-code=PSAW]').get_attribute('aria-pressed')=='true'
        page.route('**/ocean-motion-dashboard-ground.svg',lambda route:route.fulfill(status=503,body='unavailable'))
        page.reload(wait_until='networkidle')
        expect(page.locator('#atlas-state-map-note')).to_contain_text('Clickable state shapes are unavailable',timeout=90000)
        expect(page.locator('.atlas-directory-item')).to_have_count(240,timeout=90000)
        page.unroute('**/ocean-motion-dashboard-ground.svg')
        held=[]
        def hold_shape(route):
            if route.request.resource_type=='fetch':held.append(route)
            else:route.continue_()
        page.route('**/ocean-motion-dashboard-ground.svg',hold_shape)
        page.goto(BASE+'#route-atlas',wait_until='domcontentloaded')
        page.wait_for_function('typeof window.restoreReferenceRouteAtlas === "function"')
        expect(page.locator('#route-atlas-select option')).to_have_count(101,timeout=90000)
        assert held
        world=page.locator('#route-atlas-map').get_attribute('viewBox')
        page.locator('#route-atlas-in').click();assert page.locator('#route-atlas-map').get_attribute('viewBox')!=world
        page.locator('#route-atlas-select').select_option('current:agulhas')
        held.pop().fulfill(status=200,content_type='image/svg+xml',body=(ROOT/'figures/ocean-motion-dashboard-ground.svg').read_text(encoding='utf-8'))
        page.wait_for_function('document.querySelectorAll(".atlas-state-region").length===56')
        assert page.locator('#route-atlas-select').input_value()=='current:agulhas'
        page.unroute('**/ocean-motion-dashboard-ground.svg')
        broken=(ROOT/'figures/ocean-motion-dashboard-ground.svg').read_text(encoding='utf-8')
        import re
        broken=re.sub(r'(<g[^>]+data-code="BERS"[^>]*>.*?<path) d="[^"]+"',r'\1 d=""',broken,count=1,flags=re.S)
        page.route('**/ocean-motion-dashboard-ground.svg',lambda route:route.fulfill(status=200,content_type='image/svg+xml',body=broken))
        page.reload(wait_until='networkidle')
        expect(page.locator('#atlas-state-map-note')).to_contain_text('Clickable state shapes are unavailable',timeout=90000)
        expect(page.locator('#route-atlas-select option')).to_have_count(101,timeout=90000)
        assert not errors,errors
        browser.close()
    print('OK: all 56 exact saved shapes, keyboard filters, pointer activation, selected state/reload, current marker navigation and missing geometry fallback')
if __name__=='__main__':main()
