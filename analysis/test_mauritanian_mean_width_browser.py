"""Local seasonal-mean undercurrent span is not a whole-current seasonal footprint."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 root=Path(__file__).resolve().parents[1]
 data=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
 row=next(r for r in data['entries'] if r['id']=='current:mauritanian')
 assert row['capabilities']['scoped_width']==1
 assert row['capabilities']['reference_route']==0
 assert row['latest_observation_date'] is None
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
  page=browser.new_page(viewport={'width':1440,'height':1100});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=mauritanian',wait_until='networkidle')
  page.wait_for_function('document.querySelector("#season-title").textContent.includes("Seasonal mean undercurrent")')
  assert '30–40 km author-reported seasonal mean span' in page.locator('#season-value').inner_text()
  assert 'not the mean of instantaneous widths' in page.locator('#season-definition').inner_text()
  assert '2005–2011' in page.locator('#season-definition').inner_text()
  assert 'January–April' in page.locator('#season-definition').inner_text()
  assert 'not annual variation' in page.locator('#season-range').inner_text()
  assert page.locator('#season-play').is_disabled()
  assert page.locator('#season-bar').is_hidden()
  assert page.locator('#season-map').is_hidden()
  page.screenshot(path=str(root/'figures/mauritanian-seasonal-mean-width-review.png'),full_page=True)
  page.locator('#season-current').select_option('northern-mediterranean')
  assert page.locator('#season-bar').is_visible()
  page.locator('#season-current').select_option('mauritanian')
  assert page.locator('#season-bar').is_hidden()
  page.set_viewport_size({'width':320,'height':800})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3Amauritanian#route-atlas',wait_until='networkidle')
  page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:mauritanian"')
  assert row['scope_notes'][0]['summary'] in page.locator('.route-atlas-scope-reviews').inner_text()
  assert page.locator('#route-atlas-preview .route-map').count()==0
  width=page.locator('#width-rows tr').filter(has_text='Mauritanian Current')
  assert '30–40 km author-reported seasonal mean span; not annual extrema' in width.inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  browser.close()
 print('OK: local 30–40 km seasonal-mean undercurrent span, sampling support, no midpoint/bar/axis/annual inference, switch reset and mobile reflow')

if __name__=='__main__':main()
