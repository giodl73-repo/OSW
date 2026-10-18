"""Shipped Rust/WASM derived evidence: source parity, UI access and admission guards."""
def main():
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from urllib.parse import quote,parse_qs,urlsplit
    import copy,gzip,hashlib,json,subprocess,sys,os
    from playwright.sync_api import sync_playwright,expect
    from test_current_research_evidence_browser import native, CLI
    root=Path(__file__).resolve().parents[1];out=root/'.pytest_cache/kuroshio-filtered-browser';base='http://127.0.0.1:8788'
    out.mkdir(parents=True,exist_ok=True)
    cli=CLI;report='research/kuroshio-ecs-filtered-width-time-series.json'
    figure='figures/kuroshio-ecs-filtered-width-time-series.svg';identifier='diagnostic:kuroshio-filtered-width'
    sample_query={'collection':'width_samples','filters':[{'field':'sample_family','op':'eq','value':'kuroshio_filtered_curve_plot'}],
     'sort':{'field':'plot_year','direction':'asc'},'limit':250}
    diagnostic_query={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':identifier}],'limit':100}
    with TemporaryDirectory(dir=out) as temporary,sync_playwright() as pw:
     folder=Path(temporary);index=folder/'index.json';index.write_bytes(gzip.decompress((root/'almanac/index-data.json.gz').read_bytes()))
     browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'));errors=[];originals=[];source_request=None
     def page():
      p=browser.new_page(viewport={'width':1280,'height':1000});p.emulate_media(reduced_motion='reduce')
      p.on('pageerror',lambda e:errors.append(str(e)))
      p.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.nc','.mat','.zip')) else None)
      return p
     urls={'card':'/almanac/reference-routes.html?atlas-feature=current%3Akuroshio#route-atlas',
      'seasons':'/almanac/seasons.html?current=kuroshio','diagnostic':'/almanac/query.html?q='+quote(json.dumps(diagnostic_query))}
     for view,url in urls.items():
      p=page();p.goto(base+url);panel=p.locator('.kuroshio-filtered-width')
      try:expect(panel).to_be_visible(timeout=90000)
      except AssertionError:
       print(json.dumps({'errors':errors,'url':p.url,'snapshot':p.evaluate('({loaded:!!window.oswAtlasSnapshot,kind:window.oswAtlasSnapshot?.kuroshio_filtered_width_scene?.kind})'),'body':p.locator('body').inner_text()[:1800]}),flush=True)
       raise
      expect(panel).to_contain_text('192 readings');expect(panel).to_contain_text('not independent monthly means or exact observation dates')
      details=panel.locator('details')
      if details.get_attribute('open') is None:panel.locator('summary').focus();p.keyboard.press('Enter')
      img=panel.locator('img');img.scroll_into_view_if_needed();expect(img).to_have_attribute('src','../'+figure)
      expect(img).to_have_js_property('complete',True);assert img.evaluate('(n)=>n.naturalWidth>0')
      select=panel.get_by_label('Year on published plot');assert select.locator('option').count()==16
      select.focus();p.keyboard.press('End');expect(select).to_have_value('2008')
      rows=panel.locator('tbody tr');assert rows.count()==12
      expect(rows.first).to_contain_text('2008-01 (filtered plot sample)')
      all_link=panel.get_by_role('link',name='Query all 192 filtered plot readings',exact=True)
      assert json.loads(parse_qs(urlsplit(all_link.get_attribute('href')).query)['q'][0])==sample_query
      source_link=panel.get_by_role('link',name='Inspect exact filtered-width source data',exact=True)
      source_link.focus();expect(source_link).to_be_focused();source_request=json.loads(parse_qs(urlsplit(source_link.get_attribute('href')).query)['source-q'][0])
      if view=='diagnostic':
       assert p.evaluate('oswLastQueryResult')==native(diagnostic_query)
       rows.first.get_by_role('button').click();expect(p.locator('#query-detail')).to_contain_text('width-sample:kuroshio-filtered-width:samples:180')
      else:
       row_link=rows.first.get_by_role('link');row_link.focus();expect(row_link).to_be_focused()
       request=json.loads(parse_qs(urlsplit(row_link.get_attribute('href')).query)['q'][0]);assert request['filters'][0]['value'].endswith(':180')
      if view=='card':panel.locator('figure').screenshot(path=str(out/'figure-desktop.png'))
      p.set_viewport_size({'width':320,'height':900});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth')
      scroll=panel.locator('[role="region"]');scroll.focus();expect(scroll).to_be_focused();p.keyboard.press('ArrowRight')
      p.wait_for_function('(n)=>n.scrollLeft>0',arg=scroll.element_handle());p.wait_for_timeout(300);scroll.evaluate('(n)=>n.scrollLeft=0')
      if view=='card':scroll.screenshot(path=str(out/'table-mobile.png'))
      p.close();print('PASS',view,'figure/year selection/12rows/source+inspector links/keyboard320px',flush=True)
     p=page();p.goto(base+'/almanac/query.html?q='+quote(json.dumps(sample_query)));p.wait_for_function('window.oswLastQueryResult',timeout=90000)
     result=p.evaluate('oswLastQueryResult');assert result==native(sample_query);assert len(result['rows'])==192
     assert all(r['observation_date'] is None and r['month'] is None and r['year'] is None for r in result['rows'])
     panel=result['chart_scene']['panels'][0];assert panel['x_field']=='plot_year' and panel['x_domain']==[1993,2009]
     assert len(panel['points'])==192 and all(p['observation_date'] is None for p in panel['points'])
     expect(p.locator('#query-chart-panels')).to_contain_text('not raw monthly means or exact observation dates')
     mark=p.locator('.chart-sample').first;mark.focus();p.keyboard.press('Enter');expect(p.locator('#query-detail')).to_contain_text('width-sample:kuroshio-filtered-width:samples:0')
     p.screenshot(path=str(out/'sample-query-desktop.png'));p.set_viewport_size({'width':320,'height':900});assert p.evaluate('document.documentElement.scrollWidth<=innerWidth');p.close()
     print('PASS all192 native/WASM samples, graphical axes, null observation dates and point inspector',flush=True)
     p=page()
     requests=[source_request,{'document':'research/kuroshio-ecs-filtered-width-time-series-figure.json','pointer':'','limit':100},
      {'document':'research/source-data/kuroshio-liu-gan-2012/figure7a-time-extraction.json','pointer':'','limit':100}]
     for i,request in enumerate(requests):
      if i==0:p.goto(base+'/almanac/query.html?source-q='+quote(json.dumps(request)))
      else:
       p.locator('#source-query-panel details').evaluate('(n)=>n.open=true');p.locator('#source-query-json').fill(json.dumps(request))
       p.evaluate('oswSourceQueryResult=null');p.locator('#source-query-run-json').click()
      p.wait_for_function('window.oswSourceQueryResult',timeout=90000)
      value=p.evaluate('oswSourceQueryResult');assert value==native(request,index=index)
      assert value['source_sha256']==hashlib.sha256((root/request['document']).read_bytes()).hexdigest()
      print('PASS exact source',request['document'],flush=True)
     p.close();packet=json.loads((root/'almanac/query-data.json').read_bytes())
     for kind in ['source_hash','figure_hash','operator_hash','raw_means','fake_date','missing_sample','coherent_rebind','inventory_width']:
      bad=copy.deepcopy(packet);diag=next(r for r in bad['collections']['diagnostics'] if r['id']==identifier)
      samples=[r for r in bad['collections']['width_samples'] if r['diagnostic_id']==identifier]
      if kind.endswith('_hash'):
       path={'source_hash':report,'figure_hash':figure,'operator_hash':'plans/kuroshio-filtered-width-time-series-protocol-v1.md'}[kind]
       bad['manifest']['input_sha256'][path]='0'*64
      elif kind=='raw_means':samples[0]['samples_are_raw_monthly_means']=True
      elif kind=='fake_date':samples[0].update(observation_date='1993-01-15',month=1,year=1993)
      elif kind=='missing_sample':
       sample=samples[-1];bad['collections']['width_samples']=[r for r in bad['collections']['width_samples'] if r['id']!=sample['id']]
       owner=next(r for r in bad['collections']['objects'] if r['id']=='current:kuroshio');owner['width_sample_ids'].remove(sample['id']);owner['capabilities']['width_samples']-=1
      elif kind=='coherent_rebind':
       diag['document']['cautions']=[]
       for r in samples:r['source_context']['cautions']=[]
       raw=json.dumps(diag['document']);pin=hashlib.sha256(raw.encode()).hexdigest();diag.update(source_json=raw,source_file_sha256=pin);bad['manifest']['input_sha256'][report]=pin
      else:bad['collections']['widths'][0]['source_file']=report
      fixture=folder/'bad.json';fixture.write_bytes(json.dumps(bad).encode());del bad
      native_result=subprocess.run([str(cli),str(fixture),'-'],input='{}',capture_output=True,text=True,encoding='utf8');assert native_result.returncode==2 and not native_result.stdout
      p=page();p.route('**/filtered-width-guard.html',lambda r:r.fulfill(body='<title>Filtered width guard</title>',content_type='text/html'));p.goto(base+'/filtered-width-guard.html')
      value=p.evaluate('''async url=>{const {instance}=await WebAssembly.instantiate(await (await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports,r=await fetch(url);if(!r.ok)throw new Error('Unserved fixture');const b=new Uint8Array(await r.arrayBuffer()),p=e.osw_alloc(b.length);try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(p,b.length);}}''',base+'/'+fixture.relative_to(root).as_posix())
      assert value['ok'] is False;p.close();print('PASS native/actual WASM rejection',kind,flush=True)
     browser.close();assert not errors and not originals,(errors,originals)
    (out/'browser-result.json').write_text(json.dumps({'status':'PASS','views':[*urls,'all192sample_query'],'new_sample_count':192,
     'native_wasm_parity':True,'source_documents':3,'native_wasm_corruptions':8,'year_options':16,'rows_per_year':12,'all_observation_dates_null':True,
     'mobile_width':320,'keyboard_and_horizontal_scroll':True,'reduced_motion':True,'no_automatic_originals':True},indent=2)+'\n')


if __name__ == '__main__': main()
