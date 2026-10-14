"""Monthly climatology, source years, map support and frozen native/WASM joins."""
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
from check_indian_secc_oscar_climatology import OWNER, DATA, DOCUMENTS


def corrupt(bundle,mode):
    bad=copy.deepcopy(bundle)
    diagnostic=next(d for d in bad['collections']['diagnostics'] if d['id']=='diagnostic:basin-indian-secc-80p333e')
    doc=diagnostic['document']
    if mode=='zero':doc['months'][3]['approximate_section_span_km']=0
    if mode=='pooled':doc['climatology_operator']='Pool all five-day samples with unequal year weights'
    if mode=='longitude':doc['section_longitude_degrees_east']=80.5;doc['section']['fixed_coordinate']=80.5
    if mode=='annual':doc['annual_width_range_km']=[60,670]
    if mode=='uncertainty':doc['months'][0]['measurement_uncertainty_interval_km']=[170,440]
    if mode in ['zero','pooled','longitude','annual','uncertainty']:
        diagnostic['source_json']=json.dumps(doc,ensure_ascii=False)
        diagnostic['source_file_sha256']=hashlib.sha256(diagnostic['source_json'].encode()).hexdigest()
        bad['manifest']['input_sha256'][diagnostic['source_file']]=diagnostic['source_file_sha256']
        # Projection rejects a promoted annual range before native loading;
        # preserve its other exact source-bound rows for that malformed case.
        if mode!='annual':bad['collections']['width_samples']=project_samples(bad['collections']['diagnostics'])
    if mode=='missing':
        bad['collections']['diagnostics'].remove(diagnostic)
        bad['collections']['width_samples']=[r for r in bad['collections']['width_samples'] if r['diagnostic_id']!=diagnostic['id']]
        bad['manifest']['input_sha256'].pop(diagnostic['source_file'])
    if mode=='root_pin':bad['manifest']['input_sha256'][DATA]='0'*64
    if mode in ['year','association']:
        row=next(r for r in bad['collections']['width_samples'] if r['diagnostic_id']==diagnostic['id'])
        row['year' if mode=='year' else 'current_association_verified']=2013 if mode=='year' else True
    return bad


def navigation():
    """The new evidence must be reachable from the current's actual atlas card."""
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':320,'height':900})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        for coordinate,suffix in [('80.333','80p333e'),('80.667','80p667e')]:
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=current%3A'+OWNER+'#route-atlas')
            preview=page.locator('#route-atlas-preview')
            link=preview.get_by_role('link',name='1995–2016 calendar-month climatology at '+coordinate+' E (current width unresolved)',exact=False)
            expect(link).to_be_visible(timeout=90000)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            link.click()
            page.wait_for_function('window.oswLastQueryResult?.total===12',timeout=90000)
            actual=page.evaluate('oswLastQueryResult')
            assert all(r['diagnostic_id']=='diagnostic:basin-indian-secc-'+suffix for r in actual['rows'])
            expect(page.locator('#query-chart-panels')).to_contain_text('1995–2016')
            page.get_by_role('button',name='Inspect selected month',exact=True).click()
            expect(page.locator('#query-detail')).to_contain_text('Climatology period')
            expect(page.locator('#query-detail')).not_to_contain_text('Source year')
            for label in ['View year-by-year monthly spans','Inspect 22 years of monthly profiles']:
                assert page.get_by_role('link',name=label,exact=True).bounding_box()['height']>=44
        assert not errors,errors
        browser.close()
    print('PASS: both native columns reachable directly from the current atlas card at320 px')


def main():
    navigation()
    out=ROOT/'.pytest_cache/indian-secc-climatology-review';out.mkdir(parents=True,exist_ok=True)
    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    query={'collection':'width_samples','filters':[{'field':'current_id','op':'eq','value':OWNER}],'sort':{'field':'month'},'limit':100}
    expected=native(query)
    assert expected['ok'] and expected['total']==24
    assert sum(r['value_km'] is None for r in expected['rows'])==16
    assert all(r['year'] is None and r['current_association_verified'] is False for r in expected['rows'])
    assert expected['map_scene']['mapped_objects']==8 and expected['map_scene']['unmapped_objects']==16
    assert len(expected['chart_scene']['panels'])==2
    assert all('1995–2016' in p['title'] and 'null' not in p['title'] for p in expected['chart_scene']['panels'])
    with TemporaryDirectory(dir=out) as directory:
        index=Path(directory)/'index.json'
        index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1400,'height':1100})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.emulate_media(reduced_motion='reduce')
            page.goto(BASE+'?q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswLastQueryResult',timeout=90000)
            assert page.evaluate('oswLastQueryResult')==expected
            selects=page.locator('.chart-playback select')
            assert selects.count()==2 and selects.first.locator('option').count()==12
            assert page.get_by_role('button',name='Play monthly readings',exact=True).first.is_disabled()
            selects.first.select_option(index=3)
            page.get_by_role('button',name='Inspect selected month',exact=True).first.click()
            expect(page.locator('#query-detail h3')).to_contain_text('Apr')
            expect(page.locator('#query-detail')).to_contain_text('Native resolution review: unresolved')
            expect(page.locator('#query-detail')).to_contain_text('1995–2016 calendar-month climatology')
            assert 'null-monthly' not in page.locator('#query-detail').inner_html()
            selects.first.select_option(index=0)
            page.get_by_role('button',name='Inspect selected month',exact=True).first.click()
            expect(page.locator('#query-detail h3')).to_contain_text('Jan')
            expect(page.locator('#query-detail')).to_contain_text('19/22 profiles')
            expect(page.locator('#query-detail')).to_contain_text('classification window: yes')
            expect(page.locator('#query-detail')).to_contain_text('neither measurement uncertainty nor annual physical extrema')
            years=page.get_by_role('link',name='Inspect 22 years of monthly profiles',exact=True).get_attribute('href')
            profile=page.get_by_role('link',name='View all monthly velocity profiles',exact=True).get_attribute('href')
            assert profile.endswith('indian-secc-80p333e-1995-2016-monthly-component-profiles.svg')
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#query-detail').screenshot(path=str(out/'climatology-inspector-mobile.png'))
            page.locator('#query-chart-panels').screenshot(path=str(out/'climatology-charts-mobile.png'))
            page.get_by_role('link',name='Map this local section span',exact=True).click()
            page.wait_for_function('window.oswLastQueryResult?.total===1',timeout=90000)
            mapped=page.evaluate('oswLastQueryResult')
            assert mapped['map_scene']['mapped_objects']==1
            feature=mapped['map_scene']['features'][0]
            assert feature['climatology_period_years']==[1995,2016]
            assert '80.333' in feature['time_support']
            page.goto(urljoin(BASE,years))
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            actual=page.evaluate('oswSourceQueryResult')
            assert actual['document']==DATA and actual['total']==22
            assert all(len(r['record']['months'])==12 for r in actual['rows'])
            request={'document':DATA,'pointer':'/sections/0/yearly/2013/months/2/profile','limit':100}
            run=subprocess.run([str(CLI),'--index',str(index),'-'],input=json.dumps(request),capture_output=True,text=True,encoding='utf8')
            assert run.returncode==0,run.stderr
            page.goto(BASE+'?source-q='+quote(json.dumps(request)))
            page.wait_for_function('window.oswSourceQueryResult?.ok',timeout=90000)
            assert page.evaluate('oswSourceQueryResult')==json.loads(run.stdout)
            assert page.evaluate('oswSourceQueryResult.total')==37
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            # Use a light page for independent bundle-load rejection checks.
            page.route('**/indian-secc-guard.html',lambda r:r.fulfill(body='<title>Climatology source guard</title>',content_type='text/html'))
            page.goto('http://127.0.0.1:8788/indian-secc-guard.html')
            for mode in ['zero','pooled','longitude','annual','uncertainty','missing','root_pin','year','association']:
                path=Path(directory)/'bad.json';path.write_text(json.dumps(corrupt(bundle,mode),ensure_ascii=False),encoding='utf8')
                result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
                assert result.returncode==2 and not result.stdout,(mode,result.stderr)
                actual=page.evaluate('''async path=>{
                  const {instance}=await WebAssembly.instantiate(await(await fetch('/almanac/query-engine.wasm')).arrayBuffer(),{}),e=instance.exports;
                  const b=new Uint8Array(await(await fetch(path)).arrayBuffer()),p=e.osw_alloc(b.length);
                  try {new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);
                    return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));
                  }finally{e.osw_dealloc(p,b.length);}
                }''','/'+path.relative_to(ROOT).as_posix())
                assert actual['ok'] is False,(mode,actual)
            assert not errors,errors
            browser.close()
    print('PASS: two native climatologies, explicit gaps, playback and real inspectors, local maps, 22 yearly records and37-cell source/native parity, mobile and nine coherent rejection cases')


if __name__=='__main__':main()
