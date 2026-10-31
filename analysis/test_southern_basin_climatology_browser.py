"""Three current cards, distinct climatologies, source years and native/WASM guards."""
from query_packet import read_bundle_bytes
import copy
import gzip
import hashlib
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, urljoin
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, CLI, BASE, native, browser_query
from build_query_width_samples import build as project_samples
from check_southern_basin_oscar_climatology import DATA, DOCUMENTS, saved


def corrupt(bundle,mode,index):
    bad=copy.deepcopy(bundle)
    identifier=saved()[index]['diagnostic_id']
    diagnostic=next(d for d in bad['collections']['diagnostics'] if d['id']==identifier)
    doc=diagnostic['document']
    if mode=='zero':
        month=next(m for m in doc['months'] if m['approximate_section_span_km'] is None)
        month['approximate_section_span_km']=0
    if mode=='pooled':doc['climatology_operator']='Pool original records with unequal year weights'
    if mode=='longitude':doc['section_longitude_degrees_east']+=1;doc['section']['fixed_coordinate']+=1
    if mode=='annual':doc['annual_width_range_km']=[10,1000]
    if mode=='uncertainty':doc['months'][0]['measurement_uncertainty_interval_km']=[10,1000]
    if mode in ['zero','pooled','longitude','annual','uncertainty']:
        diagnostic['source_json']=json.dumps(doc,ensure_ascii=False)
        diagnostic['source_file_sha256']=hashlib.sha256(diagnostic['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][diagnostic['source_file']]=diagnostic['source_file_sha256']
        if mode!='annual':bad['collections']['width_samples']=project_samples(bad['collections']['diagnostics'])
    if mode=='missing':
        bad['collections']['diagnostics'].remove(diagnostic)
        bad['collections']['width_samples']=[r for r in bad['collections']['width_samples'] if r['diagnostic_id']!=identifier]
        bad['manifest']['input_sha256'].pop(diagnostic['source_file'])
    if mode=='root_pin':bad['manifest']['input_sha256'][DATA]='0'*64
    if mode in ['year','association']:
        row=next(r for r in bad['collections']['width_samples'] if r['diagnostic_id']==identifier)
        row['year' if mode=='year' else 'current_association_verified']=2013 if mode=='year' else True
    return bad


def main():
    out=ROOT/'.pytest_cache/southern-basin-climatology-review';out.mkdir(parents=True,exist_ok=True)
    bundle=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    docs=saved()
    with TemporaryDirectory(dir=out) as directory, sync_playwright() as p:
        index=Path(directory)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        errors=[]
        for number,doc in enumerate(docs):
            page=browser.new_page(viewport={'width':320,'height':900})
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.emulate_media(reduced_motion='reduce')
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A'+doc['current_id']+'#route-atlas')
            link=page.locator('#route-atlas-preview').get_by_role('link',name=doc['period_label']+' (current width unresolved)',exact=False)
            expect(link).to_be_visible(timeout=90000);link.click()
            page.wait_for_function('window.oswLastQueryResult?.total===12',timeout=90000)
            query={'collection':'width_samples','filters':[{'field':'diagnostic_id','op':'eq','value':doc['diagnostic_id']}],'sort':{'field':'month','direction':'asc'},'limit':100}
            expected=native(query)
            assert page.evaluate('oswLastQueryResult')==expected
            assert all(r['year'] is None and r['current_association_verified'] is False for r in expected['rows'])
            assert sum(r['value_km'] is not None for r in expected['rows'])==doc['summary']['resolved_nominal_months']
            assert expected['map_scene']['mapped_objects']==doc['summary']['resolved_nominal_months']
            assert len(expected['chart_scene']['panels'])==1
            expect(page.locator('#query-chart-panels')).to_contain_text('1995–2016')
            control=page.locator('.chart-playback select');assert control.locator('option').count()==12
            assert page.get_by_role('button',name='Play monthly readings',exact=True).is_disabled()
            for month in [0,3,6,9,11]:
                control.select_option(index=month)
                page.get_by_role('button',name='Inspect selected month',exact=True).click()
                expect(page.locator('#query-detail')).to_contain_text('Climatology period')
                expect(page.locator('#query-detail')).to_contain_text('declared geographic peak-search window')
                expect(page.locator('#query-detail')).to_contain_text('22/22 profiles')
                expect(page.locator('#query-detail')).to_contain_text('neither measurement uncertainty nor annual physical extrema')
                assert 'null-monthly' not in page.locator('#query-detail').inner_html()
            for label in ['View year-by-year monthly spans','Inspect 22 years of monthly profiles']:
                assert page.get_by_role('link',name=label,exact=True).bounding_box()['height']>=44
            assert page.get_by_role('link',name='View all monthly velocity profiles',exact=True).get_attribute('href').endswith(doc['profile_figure'])
            page.locator('#query-detail').screenshot(path=str(out/(doc['current_id']+'-mobile.png')))
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            years=page.get_by_role('link',name='Inspect 22 years of monthly profiles',exact=True).get_attribute('href')
            resolved=next(i for i,m in enumerate(doc['months']) if m['approximate_section_span_km'] is not None)
            control.select_option(index=resolved)
            page.get_by_role('button',name='Inspect selected month',exact=True).click()
            page.get_by_role('link',name='Map this local section span',exact=True).click()
            page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            mapped=page.evaluate('oswLastQueryResult')
            assert mapped['map_scene']['mapped_objects']==1
            assert mapped['map_scene']['features'][0]['climatology_period_years']==[1995,2016]
            page.goto(urljoin(BASE,years));page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            result=page.evaluate('oswSourceQueryResult');assert result['document']==DATA and result['total']==22
            assert all(len(r['record']['months'])==12 for r in result['rows'])
            request={'document':DATA,'pointer':f'/sections/{number}/yearly/2013/months/2/profile','limit':100}
            run=subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(request),capture_output=True,text=True,encoding='utf8')
            assert run.returncode==0,run.stderr
            page.goto(BASE+'?source-q='+quote(json.dumps(request)));page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==json.loads(run.stdout)
            assert page.evaluate('oswSourceQueryResult.total')==doc['counts']['cells_per_time']
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            # The owner query must retain both 2013 and climatology, in distinct panels.
            both={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':doc['current_id']}],'limit':100}
            page.goto(BASE+'?q='+quote(json.dumps(both)));page.wait_for_function('window.oswLastQueryResult?.total===24',timeout=90000)
            actual=page.evaluate('oswLastQueryResult');assert actual==native(both)
            assert len(actual['chart_scene']['panels'])==2
            assert {r['year'] for r in actual['rows']}=={None,2013}
            page.close()
        page=browser.new_page()
        page.route('**/southern-basin-guard.html',lambda r:r.fulfill(body='<title>Source guard</title>',content_type='text/html'))
        page.goto('http://127.0.0.1:8788/southern-basin-guard.html')
        for i,mode in enumerate(['zero','pooled','longitude','annual','uncertainty','missing','root_pin','year','association']):
            number=0 if mode=='zero' else i%3
            path=Path(directory)/'bad.json';path.write_text(json.dumps(corrupt(bundle,mode,number),ensure_ascii=False),encoding='utf8')
            run=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert run.returncode==2 and not run.stdout,(mode,run.stderr)
            result=page.evaluate('''async path=>{
              const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
              try {new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
              }finally{e.osw_dealloc(p,b.length);}
            }''','/'+path.relative_to(ROOT).as_posix())
            assert result['ok'] is False,(mode,result)
        assert not errors,errors
        browser.close()
    print('PASS: three atlas cards; 36 climatological and 36 original monthly samples; playback, source-year and native/WASM parity; mobile; nine coherent rejection cases')


if __name__=='__main__':main()
