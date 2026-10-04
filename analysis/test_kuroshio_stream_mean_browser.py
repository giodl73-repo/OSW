"""Regional threshold-width means retain spatial and temporal averaging scope."""
import os
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8788/almanac/seasons.html?current=kuroshio&phase='

def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':860,'height':1050})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for part,width in [('winter',218),('summer',207),('period',210)]:
            record=f'kuroshio-ecs-{part}-stream-mean-width'
            page.goto(BASE+record,wait_until='networkidle')
            assert page.locator('#season-title').inner_text()=='Regional surface stream-mean width'
            assert f'about {width} km' in page.locator('#season-value').inner_text()
            assert page.locator('#season-phase option').count()==3
            definition=page.locator('#season-definition').inner_text()
            for text in ['0.1 m/s','not observation depth','not width of a seasonal mean velocity','opposite local seasonal changes','Interpolation to 0.1 degree']:
                assert text in definition,text
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(el)=>el.parentElement.hidden')
            assert page.locator('#season-section-locator').is_hidden()
            assert 'not a third seasonal state' in page.locator('#season-range').inner_text()
            page.reload(wait_until='networkidle');assert f'about {width} km' in page.locator('#season-value').inner_text()
            page.locator('#season-atlas').click()
            page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:kuroshio"')
            row=page.locator(f'.atlas-width-record[data-measurement-id="{record}"]')
            row.locator('summary').click()
            assert f'{width} km' in row.inner_text()
            assert '0.1 m/s' in row.inner_text()
            row.get_by_text('Inspect this width record',exact=True).click()
            assert f'about {width} km' in page.locator('#season-value').inner_text()
        page.screenshot(path='figures/kuroshio-stream-mean-width-review.png',full_page=True)
        page.set_viewport_size({'width':320,'height':850})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors;browser.close()
    print('OK: Kuroshio winter/summer/period means, threshold and averaging, no depth/date/range/playback inference, atlas roundtrip, reload and mobile')

if __name__=='__main__':main()
