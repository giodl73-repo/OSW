"""Shipped Rust/WASM derived evidence: source parity, UI access and admission guards."""
def main():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from urllib.parse import quote,parse_qs,urlsplit
    import copy,gzip,hashlib,json,subprocess,sys,os
    from playwright.sync_api import sync_playwright,expect
    from test_current_research_evidence_browser import native, CLI
    root=Path(__file__).resolve().parents[1];out=root/'.pytest_cache/asca-component-browser';base='http://127.0.0.1:8788'
    out.mkdir(parents=True,exist_ok=True)
    cli=CLI;report='research/agulhas-asca-100m-dated-component-spans.json'
    figure='figures/agulhas-asca-100m-dated-component-spans.svg';identifier='diagnostic:agulhas-asca100m-component-spans'
    query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':identifier}],'limit':100}
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
     folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((root/'almanac/index-data.json.gz').read_bytes()))
     browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[];row_query=None
     def page():
      p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
      p.on('pageerror',lambda e:errors.append(str(e)))
      p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.mat','.zip')) else None)
      return p
     urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3AAgulhas#route-atlas',
      'seasons':'/almanac/seasons.html?current=agulhas','diagnostic':'/almanac/query.html?q='+quote(json.dumps(query))}
     urls['card']=urls['card'].replace('Agulhas','agulhas')
     for view,url in urls.items():
      p=page();p.goto(base+url);panel=p.locator('.asca-component-spans')
      try:expect(panel).to_be_visible(timeout=90000)
      except AssertionError:
       print(json.dumps({'errors':errors,'url':p.url,'snapshot':p.evaluate('({loaded:!!window.oswAtlasSnapshot,kind:window.oswAtlasSnapshot?.asca_component_span_scene?.kind})'),'body':p.locator('body').inner_text()[:1800]}),flush=True)
       raise
      expect(panel).to_contain_text('330 resolved / 931 dated profiles');expect(panel).to_contain_text('601 unresolved')
      expect(panel).to_contain_text('not flow-normal current widths')
      details=panel.locator('details')
      if details.get_attribute('open') is None:panel.locator('summary').focus();p.keyboard.press('Enter')
      image=panel.locator('img');image.scroll_into_view_if_needed();expect(image).to_have_attribute('src','../'+figure)
      expect(image).to_have_js_property('complete',True);assert image.evaluate('(n)=>n.naturalWidth>0')
      select=panel.get_by_label('Recorded year and month');assert select.locator('option').count()==27
      assert panel.locator('tbody').nth(0).locator('tr').count()==3
      assert panel.locator('tbody').nth(1).locator('tr').count()==15
      expect(panel.locator('tbody').nth(1).locator('tr').first).to_contain_text('blocked by missing data')
      select.focus();p.keyboard.press('End');expect(select).to_have_value('2018-06')
      rows=panel.locator('tbody').nth(1).locator('tr');assert rows.count()==3
      expect(rows.last).to_contain_text('2018-06-03T00:00:00Z');expect(rows.last).to_contain_text('45')
      derived=rows.last.get_by_role('link',name='Inspect derived outcome 930',exact=True)
      derived.focus();expect(derived).to_be_focused();row_query=json.loads(parse_qs(urlsplit(derived.get_attribute('href')).query)['source-q'][0]);assert row_query['pointer']=='/profiles/930'
      if view=='diagnostic':assert p.evaluate('oswLastQueryResult')==native(query)
      if view=='card':panel.locator('figure').screenshot(path=str(out/'figure-desktop.png'))
      p.set_viewport_size({'width':320,'height':900});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
      scroll=panel.locator('[role="region"]').last;scroll.focus();before=scroll.evaluate('(n)=>n.scrollLeft');p.keyboard.press('ArrowRight');p.wait_for_timeout(300);assert scroll.evaluate('(n)=>n.scrollLeft')>before
      if view=='diagnostic':scroll.screenshot(path=str(out/'table-mobile.png'))
      p.close();print('PASS',view,'all27months/complete failures/three thresholds/source links/keyboard320px',flush=True)
     p=page()
     requests=[{'document':report,'pointer':'','limit':100},
      {'document':'research/agulhas-asca-100m-dated-component-spans-figure.json','pointer':'','limit':100},
      row_query,{'document':report,'pointer':'/profiles','limit':100,'filters':[{'field':'record.year','op':'eq','value':2018},{'field':'record.month','op':'eq','value':6}]}]
     for i,request in enumerate(requests):
      if i==0:p.goto(base+'/almanac/query.html?source-q='+quote(json.dumps(request)))
      else:
       p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(request))
       p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
      p.wait_for_function('window.oswSourceQueryResult',timeout=90000)
      value=p.evaluate('oswSourceQueryResult');assert value==native(request,index=index)
      assert value['source_sha256']==hashlib.sha256((root/request['document']).read_bytes()).hexdigest()
      print('PASS exact source query',request['document'],request['pointer'],flush=True)
     all_rows=[]
     for offset in [0,500]:
      request={'document':report,'pointer':'/profiles','limit':500,'offset':offset}
      p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(request))
      p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
      p.wait_for_function('window.oswSourceQueryResult',timeout=90000);value=p.evaluate('oswSourceQueryResult')
      assert value==native(request,index=index) and value['total']==931
      assert len(value['rows'])==(500 if offset==0 else 431)
      all_rows.extend(r['record'] for r in value['rows'])
     assert sorted(r['source_time_index'] for r in all_rows)==list(range(931))
     assert sum(r['cases'][1]['span_km'] is not None for r in all_rows)==330
     print('PASS actual native/WASM pagination: all931outcomes,330resolved/601unresolved',flush=True)
     p.close();packet=json.loads((root/'almanac/query-data.json').read_bytes())
     for kind in ['source_hash','figure_hash','operator_hash','false_physical_width','fake_date','missing_outcome','coherent_rebind','inventory_width']:
      bad=copy.deepcopy(packet);diag=next(r for r in bad['collections']['diagnostics'] if r['id']==identifier)
      if kind.endswith('_hash'):
       path={'source_hash':report,'figure_hash':figure,'operator_hash':'plans/agulhas-asca-100m-component-span-protocol-v1.md'}[kind]
       bad['manifest']['input_sha256'][path]='0'*64
      elif kind=='false_physical_width':diag['document']['width_measurement_admitted']=True
      elif kind=='fake_date':diag['document']['profiles'][0]['observed_at']='2026-10-18T00:00:00Z'
      elif kind=='missing_outcome':diag['document']['profiles'].pop()
      elif kind=='coherent_rebind':
       diag['document']['interpretation']=[];raw=json.dumps(diag['document']);pin=hashlib.sha256(raw.encode()).hexdigest();diag.update(source_json=raw,source_file_sha256=pin);bad['manifest']['input_sha256'][report]=pin
      else:bad['collections']['widths'][0]['source_file']=report
      fixture=folder/'bad.json';fixture.write_bytes(json.dumps(bad).encode());del bad
      result=subprocess.run([str(cli),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert result.returncode==2 and not result.stdout
      p=page();p.route('**/asca-span-guard.html',lambda r:r.fulfill(body='<title>ASCA guard</title>',content_type='text/html'));p.goto(base+'/asca-span-guard.html')
      value=p.evaluate('''async url=>{const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,r=await fetch(url);if(!r.ok)throw new Error('Unserved fixture');const b=new Uint8Array(await r.arrayBuffer()),p=e.osw_alloc(b.length);try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(p,b.length);}}''',base+'/'+fixture.relative_to(root).as_posix())
      assert value['ok'] is False;p.close();print('PASS native/actual WASM rejection',kind,flush=True)
     browser.close();assert not errors and not originals,(errors,originals)
    (out/'browser-result.json').write_text(json.dumps({'status':'PASS','views':list(urls),'profiles':931,'primary_resolved':330,'primary_unresolved':601,'month_options':27,'thresholds':3,'source_queries':4,'native_wasm_parity':True,'native_wasm_corruptions':8,'mobile_width':320,'keyboard_and_horizontal_scroll':True,'reduced_motion':True,'no_automatic_originals':True},indent=2)+'\n')


if __name__ == '__main__': main()
