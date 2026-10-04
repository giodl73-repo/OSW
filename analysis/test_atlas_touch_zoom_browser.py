"""Actual browser touch input zooms the atlas without dismissing its card."""
import os
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':860,'height':1100},has_touch=True)
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
        page.wait_for_function('document.querySelectorAll(".atlas-directory-item").length===240')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        atlas=page.locator('#route-atlas-map');atlas.scroll_into_view_if_needed()
        box=atlas.bounding_box();cx=box['x']+box['width']/2;cy=box['y']+box['height']/2
        def view():return list(map(float,atlas.get_attribute('viewBox').split()))
        initial=view();url=page.url
        session=page.context.new_cdp_session(page)
        def touch(kind,points):
            session.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':[{'x':x,'y':y,'id':i+1} for i,(x,y) in enumerate(points)]})
        touch('touchStart',[(cx-40,cy),(cx+40,cy)])
        touch('touchMove',[(cx-80,cy),(cx+80,cy)])
        touch('touchEnd',[])
        zoomed=view()
        assert abs(zoomed[2]-initial[2]/2)<.001,(initial,zoomed)
        assert 'atlas-feature=current%3Aagulhas' in page.url and 'atlas-view=' in page.url
        assert page.locator('#route-atlas-select').input_value()=='current:agulhas'
        assert page.locator('#route-atlas-preview .route-map').is_visible()
        # A second pinch pans its center as well as changing the scale.
        touch('touchStart',[(cx-40,cy),(cx+40,cy)])
        touch('touchMove',[(cx-20,cy+20),(cx+140,cy+20)])
        touch('touchEnd',[])
        shifted=view()
        assert abs(shifted[2]-zoomed[2]/2)<.001
        assert shifted[0]<zoomed[0]+zoomed[2]/4
        assert shifted[1]<zoomed[1]+zoomed[3]/4
        # Cancellation leaves no stale touch pan; keyboard controls still work.
        touch('touchStart',[(cx-40,cy),(cx+40,cy)])
        touch('touchCancel',[])
        atlas.focus();page.keyboard.press('Home')
        assert view()==[60,90,1480,740]
        assert page.locator('#route-atlas-preview').is_hidden()
        page.locator('#route-atlas-select').select_option('current:agulhas')
        atlas.scroll_into_view_if_needed()
        page.locator('.route-atlas-station[data-current-id="current:agulhas"] circle').tap()
        assert page.locator('#route-atlas-select').input_value()=='current:agulhas'
        assert page.locator('#route-atlas-preview').is_visible()
        before=view();atlas.focus();page.keyboard.press('-');assert view()[2]>before[2]
        assert not errors,errors
        browser.close()
    print('OK: real touch pinch zoom, moving center, card retention, cancellation, subsequent tap and keyboard reset/zoom')


if __name__=='__main__':main()
