"""Local hydrographic records must remain selectable without a seasonal movie."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
 root=Path(__file__).resolve().parents[1]
 widths=json.loads((root/'research/ocean-current-width-inventory.json').read_text(encoding='utf-8'))
 records=[r for r in widths['measurements'] if r['current_id']=='persian-gulf-saline-overflow']
 snapshot=json.loads((root/'research/ocean-motion-dashboard.json').read_text(encoding='utf-8'))
 current=next(r for r in snapshot['entries'] if r['id']=='current:persian-gulf-saline-overflow')
 assert current['capabilities']['scoped_width']==6 and current['capabilities']['reference_route']==0
 assert current['latest_observation_date'] is None
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ['OSW_TEST_BROWSER'])
  page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=persian-gulf-saline-overflow',wait_until='networkidle')
  assert page.locator('#season-phase option').count()==6
  for i,row in enumerate(records):
   page.locator('#season-phase').select_option(str(i))
   assert page.locator('#season-title').inner_text()=='Local salinity-core observation'
   value=row['width_range_km'] if row['width_range_km'] else [row['approximate_width_km']]
   assert '–'.join(map(str,value)) in page.locator('#season-value').inner_text()
   assert row['phase_label'] in page.locator('#season-value').inner_text()
   assert row['boundary_rule'] in page.locator('#season-definition').inner_text()
   assert 'not a paired velocity envelope' in page.locator('#season-definition').inner_text()
   assert 'not a seasonal sequence' in page.locator('#season-range').inner_text()
   assert page.locator('#season-play').is_disabled()
   assert page.locator('#season-bar').is_hidden() and page.locator('#season-map').is_hidden()
   assert row['id'] in page.url
  page.reload(wait_until='networkidle')
  assert page.locator('#season-phase').input_value()=='5'
  page.screenshot(path=str(root/'figures/persian-gulf-core-width-season-review.png'),full_page=True)
  page.set_viewport_size({'width':320,'height':800})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('#season-atlas').click()
  page.wait_for_function('document.querySelector("#route-atlas-select").value==="current:persian-gulf-saline-overflow"')
  assert page.locator('.route-atlas-local-dimensions tbody tr').count()==6
  assert page.locator('#width-rows tr').count()==25
  first=page.locator('#width-persian-gulf-gogp99-core-width-1')
  assert 'reported local salinity-core span' in first.inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  browser.close()
 print('OK: six scoped core records, phase links/reload, no seasonal playback/bar/route, atlas return, 25 inventory rows and mobile reflow')

if __name__=='__main__':main()
