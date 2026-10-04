"""Oblique mean widths retain source axes and naming; no seasonal interpolation."""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'],headless=True)
        page=browser.new_page(viewport={'width':1200,'height':1000});errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        for ident,section,width in [('north-brazil','hs1',520),('north-brazil','hs2',220),('guiana','hs3',440)]:
            record=f'{ident}-{section}-oblique-mean-zero-width'
            page.goto(f'http://127.0.0.1:8788/almanac/seasons.html?current={ident}&phase={record}',wait_until='networkidle')
            assert page.locator('#season-title').inner_text()=='Mean oblique section'
            assert f'about {width} km' in page.locator('#season-value').inner_text()
            assert 'Bar scale:' not in page.locator('#season-definition').inner_text()
            assert 'source rotation 45' in page.locator('#season-definition').inner_text()
            assert 'not seasonal phases' in page.locator('#season-definition').inner_text()
            assert page.locator('#season-play').is_disabled()
            assert page.locator('#season-bar').evaluate('(e)=>e.parentElement.hidden')
            assert page.locator('#season-section-locator').is_hidden()
            if section=='hs2':assert 'Discrepancy unresolved' in page.locator('#season-definition').inner_text()
            if ident=='guiana':assert 'no canonical alias merge' in page.locator('#season-definition').inner_text()
            page.reload(wait_until='networkidle');assert f'about {width} km' in page.locator('#season-value').inner_text()
            page.set_viewport_size({'width':320,'height':800});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#season-atlas').click()
            page.wait_for_function('(ident)=>document.querySelector("#route-atlas-select").value===ident',arg='current:'+ident)
            assert str(width) in page.locator('#width-'+record).inner_text()
            page.set_viewport_size({'width':1200,'height':1000})
        page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=guiana',wait_until='networkidle')
        page.screenshot(path=str(ROOT/'figures/guiana-oblique-mean-width-review.png'))
        assert not errors,errors
        browser.close()
    print('OK: three oblique widths, source rotation and identity convention, table/prose conflict, no inferred edges/playback, reload, atlas/table links and mobile')
if __name__=='__main__':main()
