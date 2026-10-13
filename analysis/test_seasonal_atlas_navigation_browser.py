"""Atlas/season round trips retain current and recorded-phase identity."""
import json,os
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright

def main():
 root=Path(__file__).resolve().parents[1]
 def read(f):return json.loads((root/f).read_text(encoding='utf-8'))
 frames=read('research/ocean-current-seasonal-route-frames.json')['frames']
 widths=read('research/ocean-current-width-inventory.json')['measurements']
 directions=read('research/new-guinea-coastal-current-seasonal-direction-scope-audit.json')['phases']
 catalog=read('research/ocean-current-reference-path-candidates.json')['candidates']
 linked={ident for f in frames for ident in f['width_measurement_ids']}
 records=frames+[r for r in widths if r['id'] not in linked]+directions
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
  page=browser.new_page(viewport={'width':1440,'height':1100});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#route-atlas',wait_until='networkidle')
  page.wait_for_function('document.querySelectorAll("#route-atlas-select option").length===101')
  for row in read('research/ocean-motion-dashboard.json')['entries']:
   if row['type']!='named_current':continue
   page.locator('#route-atlas-select').select_option(row['id'])
   href=page.locator('#route-atlas-preview').get_by_role('link',name='Widths and seasonal evidence →',exact=True).get_attribute('href')
   assert parse_qs(urlparse(href).query)['current']==[row['id'].split(':',1)[1]]
  for row in catalog:
   href=page.locator('#'+row['id']).get_by_role('link',name='Widths and seasonal evidence',exact=True).get_attribute('href')
   query=parse_qs(urlparse(href).query)
   assert query['current']==[row['current_id']]
   frame=next((f for f in frames if f['route_candidate_file']==row['candidate_file']),None)
   if frame:assert query['phase']==[frame['id']]
  for row in records:
   page.goto('http://127.0.0.1:8788/almanac/seasons.html?current='+row['current_id']+'&phase='+row['id'],wait_until='networkidle')
   page.wait_for_function('(id)=>new URL(location.href).searchParams.get("phase")===id && document.querySelector("#season-phase").options.length>0',arg=row['id'])
   assert page.locator('#season-current').input_value()==row['current_id']
   assert parse_qs(urlparse(page.locator('#season-share').get_attribute('href')).query)['phase']==[row['id']]
   atlas_query=parse_qs(urlparse(page.locator('#season-atlas').get_attribute('href')).query)
   assert atlas_query['atlas-feature']==['current:'+row['current_id']]
   if row in frames:
    route=next(r for r in catalog if r['candidate_file']==row['route_candidate_file'])
    assert atlas_query['atlas-route']==[route['id']]
    page.locator('#season-atlas').click()
    page.wait_for_function('(id)=>document.querySelector("#route-atlas-select").value===id',arg='current:'+row['current_id'])
    href=page.locator('#route-atlas-preview').get_by_role('link',name='Open this recorded seasonal phase →',exact=True).get_attribute('href')
    assert parse_qs(urlparse(href).query)['phase']==[row['id']]
    page.locator('#route-atlas-preview').get_by_role('link',name='Open this recorded seasonal phase →',exact=True).click()
    page.wait_for_function('(id)=>new URL(location.href).searchParams.get("phase")===id',arg=row['id'])
  page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=monsoon&phase=monsoon-winter-sri-lanka',wait_until='networkidle')
  page.wait_for_function('window.oswSeasonSnapshot && document.querySelector("#season-current").options.length===100',timeout=90000)
  assert 'westward' in page.locator('#season-value').inner_text()
  page.locator('#season-phase').select_option(str(page.evaluate('oswSeasonPlan.phases.findIndex(p=>p.frame_id==="monsoon-summer-sri-lanka")')))
  assert parse_qs(urlparse(page.url).query)['phase']==['monsoon-summer-sri-lanka']
  page.locator('#season-current').select_option('mauritanian')
  assert parse_qs(urlparse(page.url).query)['phase']==['mauritanian-upwelling-seasonal-mean-width-range']
  assert page.locator('#season-play').is_disabled()
  page.set_viewport_size({'width':320,'height':800})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.screenshot(path=str(root/'figures/seasonal-atlas-navigation-review.png'),full_page=True)
  page.goto('http://127.0.0.1:8788/almanac/seasons.html?current=west-australian&phase=monsoon-winter-sri-lanka',wait_until='networkidle')
  page.wait_for_function('window.oswSeasonSnapshot && document.querySelector("#season-current").options.length===100',timeout=90000)
  assert parse_qs(urlparse(page.url).query)['current']==['west-australian']
  own=next(r for r in widths if r['current_id']=='west-australian')
  assert parse_qs(urlparse(page.url).query)['phase']==[own['id']]
  assert page.evaluate('oswSeasonPlan.current_id')=='west-australian'
  assert own['phase_label'] in page.locator('#season-phase option:checked').inner_text()
  assert page.locator('#season-play').is_disabled()
  assert not errors,errors
  browser.close()
 print(f'OK: 100 atlas current links, {len(catalog)} route-card links, {len(records)} phase deep links, six seasonal atlas round trips, share/update/reset and mobile reflow')

if __name__=='__main__':main()
