"""Shared model-scale views preserve source meaning through actual Rust/WASM."""
from query_packet import read_bundle_bytes
import copy,gzip,json,os,subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote,unquote
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('OSW_MODEL_SCALE_BASE','http://127.0.0.1:8788').rstrip('/')
CLI=ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'
OWNER='pacific-north-equatorial-countercurrent'
SOURCE='research/pacific-necc-chen-2016-axis-spread-scale-scope-audit.json'
PREFIX='pacific-necc-chen-2016-model-axis-spread-'


def native(q,packet=None,index=None):
    args=[str(CLI)]+(['--index',str(index)] if index else [str(packet or ROOT/'almanac/query-data.json')])+['-']
    result=subprocess.run(args,input=json.dumps(q),capture_output=True,text=True,encoding='utf8')
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def check_panel(panel):
    assert panel.locator('svg rect').evaluate_all('(nodes)=>nodes.map(n=>Number(n.dataset.valueKm))')==[100,130]
    expect(panel).to_contain_text('latitude degrees')
    expect(panel).to_contain_text('13-month running mean')
    expect(panel).to_contain_text('uncertainty')
    assert panel.locator('tbody tr').count()==2


def main():
    output=ROOT/'.pytest_cache/necc-model-scale-browser';output.mkdir(parents=True,exist_ok=True)
    packet=json.loads(read_bundle_bytes(ROOT/'almanac/query-data.json'))
    q={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':OWNER}],'limit':100}
    expected=native(q);assert expected['total']==2 and expected['chart_scene']['kind']=='published_model_axis_spread'
    with TemporaryDirectory(dir=output) as temp,sync_playwright() as p:
        folder=Path(temp);index=folder/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.zip','.mat')) else None)
        page.route('**/research/**',lambda route:route.fulfill(status=503,body='Direct scientific file reads disabled'))
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(q)))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        panel=page.locator('#query-chart-panels .model-axis-spread');check_panel(panel)
        panel.get_by_role('button',name='Inspect reported to state').click()
        expect(page.locator('#query-detail')).to_contain_text(PREFIX+'to')
        one={'collection':'widths','filters':[{'field':'id','op':'eq','value':PREFIX+'to'}],'limit':1}
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(one)));page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        result=page.evaluate('oswLastQueryResult');assert result==native(one) and result['total']==1
        assert result['chart_scene']['matching_ids']==[PREFIX+'to']
        panel=page.locator('#query-chart-panels .model-axis-spread');check_panel(panel)
        expect(panel).to_contain_text('Source context');expect(panel).to_contain_text('Matches query')
        link=panel.get_by_role('link',name='Inspect exact model-scale source records')
        source_q=json.loads(unquote(link.get_attribute('href').split('source-q=')[1]));link.click()
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('oswSourceQueryResult')==native(source_q,index=index)
        page.goto(BASE+'/almanac/seasons.html?current='+OWNER)
        panel=page.locator('#regional-width-range .model-axis-spread');expect(panel).to_be_visible(timeout=90000);check_panel(panel)
        assert page.locator('#season-play').is_disabled()
        page.locator('#season-phase').select_option('1');expect(page.locator('#season-value')).to_contain_text('130 km')
        page.set_viewport_size({'width':320,'height':900});page.emulate_media(reduced_motion='reduce')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output/'seasons-mobile.png'))
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3A'+OWNER+'#route-atlas')
        panel=page.locator('#route-atlas-preview .model-axis-spread');expect(panel).to_be_visible(timeout=90000)
        panel.locator('summary').focus();page.keyboard.press('Enter');check_panel(panel)
        assert panel.locator('svg').evaluate('(n)=>n.getBoundingClientRect().right<=innerWidth')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output/'card-mobile.png'))
        page.locator('summary').filter(has_text='Width coverage for all 100 names').click()
        coverage=page.locator('#width-decision-'+OWNER)
        expect(coverage).to_contain_text('scoped width evidence present')
        expect(coverage).to_contain_text('Separate derived section-width candidate still requires scientific review.')
        coverage.get_by_role('link',name='Inspect derived section-width candidate').click()
        page.wait_for_function('document.querySelectorAll("#section-rows tr").length===12',timeout=90000)
        expect(page.locator('#section-status')).to_contain_text('12 resolved')
        assert not errors,errors;assert not originals,originals;page.close()
        cases=['double','rms','annual','plot_units','dates','raw_claim','geometry','missing','duplicate','source_pin','original_pin']
        for case in cases:
            bad=copy.deepcopy(packet);rows=bad['collections']['widths'];target=next(r for r in rows if r['id']==PREFIX+'from');context=target['model_axis_spread_context']
            if case=='double':target['approximate_width_km']=200
            elif case=='rms':context['operator']['scale_is_rms_or_standard_deviation']=True
            elif case=='annual':target['width_range_km']=[100,130];target['annual_extrema_eligible']=True
            elif case=='plot_units':context['operator']['source_figure_8_width_axis_unit']='kilometres'
            elif case=='dates':target['observed_period']={'start':'1960-01-01','end':'1960-01-01'}
            elif case=='raw_claim':context['raw_model_fields_acquired']=True
            elif case=='geometry':target['section_geometry']={'type':'LineString','coordinates':[[145,0],[145,10]]}
            elif case=='missing':rows.remove(target)
            elif case=='duplicate':rows.append(copy.deepcopy(target))
            elif case=='source_pin':bad['manifest']['input_sha256'][SOURCE]='0'*64
            else:bad['manifest']['input_sha256']['research/source-data/chen-necc-2016/journal-article.pdf']='0'*64
            path=folder/'corrupt.json'
            with path.open('w',encoding='utf8') as out:json.dump(bad,out)
            del bad
            result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and not result.stdout,(case,result.stderr)
            page=browser.new_page();page.route('**/model-scale-guard.html',lambda route:route.fulfill(body='<title>Guard</title>',content_type='text/html'))
            page.goto(BASE+'/model-scale-guard.html')
            result=page.evaluate('''async data=>{
              const w=await fetch(data.wasm),r=await fetch(data.fixture);if(!w.ok||!r.ok)throw Error('Unserved fixture');
              const {instance}=await WebAssembly.instantiate(await w.arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await r.arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(p,b.length);}
            }''',{'wasm':BASE+'/almanac/query-engine.wasm','fixture':BASE+'/'+path.relative_to(ROOT).as_posix()})
            assert result['ok'] is False,(case,result);page.close();print('PASS native/WASM',case,flush=True)
        browser.close()
    print('PASS model-scale card/seasons/query/source/inspector, filtered comparison context, mobile/keyboard/reduced motion,11 native/WASM corruptions; no direct research reads or automatic originals',flush=True)


if __name__=='__main__':main()
