"""Shared Antilles UI and actual native/WASM source-contract rejection."""
import copy,gzip,json,os,subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote,unquote
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('OSW_ANTILLES_CRUISE_BASE','http://127.0.0.1:8788').rstrip('/')
CLI=ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'
SOURCE='research/antilles-cainzos-2023-cruise-section-spans.json'


def native(q,packet=None,index=None):
    args=[str(CLI)]+(['--index',str(index)] if index else [str(packet or ROOT/'almanac/query-data.json')])+['-']
    result=subprocess.run(args,input=json.dumps(q),capture_output=True,text=True,encoding='utf8')
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def bars(panel):
    assert panel.locator('.cruise-span-chart rect').evaluate_all('(nodes)=>nodes.map(n=>Number(n.dataset.valueKm))')==[125,38,39]
    expect(panel).to_contain_text('Cape Hatteras')
    expect(panel).to_contain_text('49.4 km')
    assert panel.locator('.cruise-span-table tbody tr').count()==3
    assert panel.locator('.cruise-span-chart').evaluate('(svg)=>{const r=svg.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth;}')


def main():
    output=ROOT/'.pytest_cache/antilles-cainzos-browser';output.mkdir(parents=True,exist_ok=True)
    q={'collection':'widths','filters':[{'field':'current_id','op':'eq','value':'antilles'}],'limit':100}
    expected=native(q);assert expected['total']==3 and expected['chart_scene']['kind']=='antilles_cruise_section_spans'
    packet=json.loads((ROOT/'almanac/query-data.json').read_bytes())
    with TemporaryDirectory(dir=output) as temporary,sync_playwright() as p:
        index=Path(temporary)/'index.json';index.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];originals=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:originals.append(r.url) if r.url.lower().split('?')[0].endswith(('.pdf','.zip','.mat')) else None)
        page.goto(BASE+'/almanac/query.html?q='+quote(json.dumps(q)))
        page.wait_for_function('window.oswLastQueryResult',timeout=90000)
        assert page.evaluate('oswLastQueryResult')==expected
        panel=page.locator('#query-chart-panels .antilles-cruise-evidence');bars(panel)
        panel.get_by_role('button',name='Inspect 29AH20110128 record').click()
        expect(page.locator('#query-detail')).to_contain_text('cainzos-2023-t02-row-53-section-span')
        link=panel.get_by_role('link',name='Inspect exact Antilles source extraction')
        source_q=json.loads(unquote(link.get_attribute('href').split('source-q=')[1]));link.click()
        page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
        assert page.evaluate('oswSourceQueryResult')==native(source_q,index=index)
        page.goto(BASE+'/almanac/seasons.html?current=antilles')
        panel=page.locator('#cruise-span-panel');expect(panel).to_be_visible(timeout=90000);bars(panel)
        assert page.locator('#season-play').is_disabled()
        details=panel.locator('.cruise-station-context');details.locator('summary').focus();page.keyboard.press('Enter')
        page.wait_for_function('window.oswAtlanticStationContext?.point_count===101',timeout=90000)
        for row,count in [(52,114),(53,153)]:
            details.get_by_label('Cruise sampling map measurement').select_option(f'cainzos-2023-t02-row-{row}-section-span')
            page.wait_for_function('(n)=>window.oswAtlanticStationContext?.point_count===n',arg=count,timeout=90000)
            context=page.evaluate('oswAtlanticStationContext')
            assert context['geometry_role']=='cruise_sampling_context_not_current_boundary'
            assert context['boundary_station_mapping_status']=='unresolved'
        page.set_viewport_size({'width':320,'height':900});page.emulate_media(reduced_motion='reduce')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output/'seasons-mobile.png'))
        page.goto(BASE+'/almanac/reference-routes.html?atlas-feature=current%3Aantilles#route-atlas')
        panel=page.locator('#route-atlas-preview .antilles-cruise-evidence');expect(panel).to_be_visible(timeout=90000)
        panel.locator(':scope > summary').focus();page.keyboard.press('Enter');bars(panel)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        panel.screenshot(path=str(output/'card-mobile.png'))
        assert not errors,errors;assert not originals,originals;page.close()
        cases=['distance','annual','identity','geometry','conflict','missing','duplicate','source_pin','original_pin']
        for case in cases:
            bad=copy.deepcopy(packet);rows=bad['collections']['widths'];target=next(r for r in rows if r['id']=='cainzos-2023-t02-row-53-section-span')
            if case=='distance':target['approximate_width_km']=38
            elif case=='annual':target['width_range_km']=[38,125];target['annual_extrema_eligible']=True
            elif case=='identity':target['current_id']='gulf-stream'
            elif case=='geometry':target['section_geometry']={'type':'LineString','coordinates':[[-77.1,24.5],[-76.7,24.5]]}
            elif case=='conflict':target['hydrographic_section_context']['source_conflicts']=[]
            elif case=='missing':rows.remove(target)
            elif case=='duplicate':rows.append(copy.deepcopy(target))
            elif case=='source_pin':bad['manifest']['input_sha256'][SOURCE]='0'*64
            elif case=='original_pin':bad['manifest']['input_sha256']['research/source-data/cainzos-antilles-2023/journal-article.pdf']='0'*64
            path=Path(temporary)/'corrupt.json'
            with path.open('w',encoding='utf8') as out:json.dump(bad,out)
            del bad
            result=subprocess.run([str(CLI),str(path),'-'],input='{}',capture_output=True,text=True,encoding='utf8')
            assert result.returncode==2 and not result.stdout,(case,result.stderr)
            page=browser.new_page();page.route('**/antilles-guard.html',lambda route:route.fulfill(body='<title>Guard</title>',content_type='text/html'))
            page.goto(BASE+'/antilles-guard.html')
            result=page.evaluate('''async data=>{
              const w=await fetch(data.wasm),r=await fetch(data.fixture);if(!w.ok||!r.ok)throw Error('Unserved fixture');
              const {instance}=await WebAssembly.instantiate(await w.arrayBuffer(),{}),e=instance.exports;
              const b=new Uint8Array(await r.arrayBuffer()),p=e.osw_alloc(b.length);
              try{new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);return JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}finally{e.osw_dealloc(p,b.length);}
            }''',{'wasm':BASE+'/almanac/query-engine.wasm','fixture':BASE+'/'+path.relative_to(ROOT).as_posix()})
            assert result['ok'] is False,(case,result);page.close();print('PASS native/WASM',case,flush=True)
        browser.close()
    print('PASS Antilles cards/seasons/query/source/inspector, three sampling contexts, mobile/keyboard/reduced motion, nine native/WASM corruptions, no automatic originals',flush=True)


if __name__=='__main__':main()
