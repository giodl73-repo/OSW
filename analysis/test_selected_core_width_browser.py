"""Published core width has the same meaning in cards, seasons and WASM queries."""
import copy,gzip,json,os,subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from check_west_spitsbergen_selected_core import record,AUDIT
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('OSW_SELECTED_CORE_BASE','http://127.0.0.1:8788')
CLI=ROOT/'rust/osw-query/target/debug'/('osw-query-cli.exe' if os.name=='nt' else 'osw-query-cli')
def native(q,packet=None,index=None):
 args=[str(CLI)]+(['--index',str(index)] if index else [str(packet or ROOT/'almanac/query-data.json')])+['-']
 p=subprocess.run(args,input=json.dumps(q),capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return json.loads(p.stdout)
def check_sources(page):
 import hashlib
 documents=[AUDIT]+['research/source-data/dundas-fer-wsc-2026/'+name for name in ['acquisition.json','dataset-acquisition.json','dataset-datacite.json','figure.json']]
 page.locator('#source-query-panel details').evaluate('(node)=>node.open=true')
 for document in documents:
  page.locator('#source-query-json').fill(json.dumps({'document':document,'pointer':'','limit':1}))
  page.evaluate('window.oswSourceQueryResult=null');page.locator('#source-query-run-json').click();page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
  actual=page.evaluate('oswSourceQueryResult');raw=(ROOT/document).read_bytes();source=json.loads(raw);key=sorted(source)[0]
  assert actual['document']==document and actual['total']==len(source) and actual['source_sha256']==hashlib.sha256(raw).hexdigest()
  assert actual['rows']==[{'source_key':key,'source_pointer':'/'+key.replace('~','~0').replace('/','~1'),'record':source[key]}]

def sources_only():
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page()
  source={'document':AUDIT,'pointer':'','limit':1};page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(source)));page.wait_for_function('window.oswSourceQueryResult',timeout=90000);check_sources(page);browser.close()
 print('PASS all five new indexed source documents through the shipped WASM source UI')

def main():
 output=ROOT/'.pytest_cache/selected-core-browser';output.mkdir(parents=True,exist_ok=True)
 row=record();query={'collection':'widths','filters':[{'field':'id','op':'eq','value':row['id']}],'limit':100}
 packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
 with TemporaryDirectory(dir=output) as temporary,sync_playwright() as playwright:
  folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
  browser=playwright.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.on('request',lambda r:originals.append(r.url) if r.url.split('?')[0].endswith(('.pdf','.nc','.zip')) else None)
  page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Awest-spitsbergen#route-atlas')
  panel=page.locator('#route-atlas-preview .selected-core-width');expect(panel).to_be_visible(timeout=90000)
  assert panel.locator('dd').all_text_contents()==['28 km','7 km','Unknown','Unknown']
  expect(panel).to_contain_text('not confidence limits');assert panel.locator('tbody tr').count()==3
  assert panel.locator('details').get_attribute('open') is None
  panel.locator('summary').focus();page.keyboard.press('Enter');assert panel.locator('details').get_attribute('open') is not None
  expect(panel.locator('img')).to_have_js_property('complete',True);assert panel.locator('img').evaluate('(img)=>img.naturalWidth>0')
  link=panel.get_by_role('link',name='Open selected-core width query');link.focus();page.keyboard.press('Enter');page.wait_for_function('window.oswLastQueryResult',timeout=90000)
  assert page.evaluate('oswLastQueryResult')==native(query)
  panel=page.locator('#query-chart-panels .selected-core-width');expect(panel).to_be_visible()
  panel.get_by_role('button',name='Inspect selected-core width record').click();expect(page.locator('#query-detail')).to_contain_text(row['id'])
  source={'document':AUDIT,'pointer':'/measurement','limit':100}
  panel.get_by_role('link',name='Inspect published width and method').click();page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
  assert page.evaluate('oswSourceQueryResult')==native(source,index=index)
  check_sources(page)
  page.goto(BASE+'/almanac/seasons.html?current=west-spitsbergen&phase='+row['id']);panel=page.locator('#regional-width-range .selected-core-width');expect(panel).to_be_visible(timeout=90000)
  expect(page.locator('#season-value')).to_contain_text('7 km reported standard deviation');expect(page.locator('#season-play')).to_be_disabled()
  page.set_viewport_size({'width':320,'height':900});page.emulate_media(reduced_motion='reduce');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');panel.screenshot(path=str(output/'wsc-mobile.png'))
  page.locator('#season-current').select_option('portugal');expect(page.locator('.selected-core-width')).to_have_count(0)
  page.set_viewport_size({'width':1280,'height':1000})
  allq={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'west-spitsbergen'}],'limit':100}
  page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(allq)));page.wait_for_function('window.oswLastQueryResult',timeout=90000);assert page.evaluate('oswLastQueryResult')==native(allq)
  assert page.evaluate('oswLastQueryResult.total')==7;expect(page.locator('.selected-core-width')).to_be_visible();expect(page.locator('.nordic-section-width')).to_be_visible();assert page.locator('.nordic-section-width svg circle').count()==3
  for owner in ['norwegian','spitsbergen-atlantic']:assert native({'collection':'widths','filters':[{'field':'current_id','op':'eq','value':owner}]})['total']==0
  page.route('**/selected-core-guard.html',lambda route:route.fulfill(body='<title>Selected core guard</title>',content_type='text/html'));page.goto(BASE+'/selected-core-guard.html')
  cases={'sd':('width_standard_deviation_km',0),'range':('width_range_km',[21,35]),'identity':('current_id','spitsbergen-atlantic'),'annual':('annual_extrema_eligible',True)}
  import sys
  if '--ui-only' in sys.argv:cases={}
  for name,(key,value) in cases.items():
   bad=copy.deepcopy(packet);target=next(r for r in bad['collections']['widths'] if r['id']==row['id']);target[key]=value
   path=folder/'corrupt.json';path.write_bytes(json.dumps(bad).encode())
   p=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True);assert p.returncode==2 and not p.stdout,(name,p.stderr)
   actual=page.evaluate("""async path=>{const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(p,b.length);}}""",'/'+path.relative_to(ROOT).as_posix());assert actual['ok'] is False,(name,actual)
  assert not errors,errors;assert not originals,originals;browser.close()
 print(f'PASS selected-core card/seasons/query/inspector/source/native-WASM parity, five source documents, old six-method comparison, aliases, mobile/reduced motion and {len(cases)} corruption rejections')
if __name__=='__main__':
 import sys
 sources_only() if '--sources-only' in sys.argv else main()
