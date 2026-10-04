"""Two extracted climatological fitted widths cannot look like an annual movie."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':860,'height':1050});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        for month,width in [(4,132),(9,89)]:
            record=f'leeuwin-a101-monthly-fit-{month:02d}'
            page.goto(f'http://127.0.0.1:8788/almanac/seasons.html?current=leeuwin&phase={record}',wait_until='networkidle')
            assert page.locator('#season-title').inner_text()=='Monthly climatological fitted width'
            assert f'about {width} km' in page.locator('#season-value').inner_text()
            assert page.locator('#season-phase option').count()==2
            definition=page.locator('#season-definition').inner_text()
            for text in ['1.89*L*cos(theta)','not width of the monthly mean','80 m layer is a transport assumption','July/August 2002','not a confidence interval','all twelve graph readings']:
                assert text in definition,text
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#season-section-locator').is_hidden()
            assert 'Only April and September' in page.locator('#season-range').inner_text()
            page.reload(wait_until='networkidle');assert f'about {width} km' in page.locator('#season-value').inner_text()
            page.locator('#season-atlas').click()
            page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:leeuwin"')
            row=page.locator(f'.atlas-width-record[data-measurement-id="{record}"]')
            row.locator('summary').click();assert f'{width} km' in row.inner_text()
            assert 'Calendar-month composite' in row.inner_text()
            row.get_by_text('Inspect this width record',exact=True).click()
            assert f'about {width} km' in page.locator('#season-value').inner_text()
        page.screenshot(path=str(ROOT/'figures/leeuwin-monthly-fit-width-review.png'))
        page.set_viewport_size({'width':320,'height':800})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors,errors;browser.close()
    print('OK: Leeuwin April/September fits, averaging and boundary scope, period discrepancy, no annual/edge/playback inference, reload, atlas roundtrip and mobile')


if __name__=='__main__':main()
