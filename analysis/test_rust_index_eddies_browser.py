"""Original-source eddy identities/joins, native/WASM parity and filtered navigation."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(name): return json.loads((ROOT/'research'/name).read_bytes())
    sources = {'loop':read('named-loop-current-eddy-identities.json'),
               'geography':read('named-eddy-geography.json'),
               'inventory':read('ocean-eddy-name-inventory.json')}
    loop = {r['id']:r for r in sources['loop']['entries']}
    geography = {r['id']:r for r in sources['geography']['entries']}
    currents = {r['id']:r for r in read('ocean-current-almanac.json')['entries']}
    contexts = {r['id']:r for r in read('named-loop-eddy-nasa-context.json')['entries']}
    geo_joins = read('named-eddy-geography-join.json')['entries']
    def oracle(section, text=''):
        query = text.strip().lower()
        rows = []
        for ordinal,item in enumerate(sources[section]['entries']):
            if section=='loop': fields=[item['name'],item.get('initial_separation'),item['role'],item['source_number']]
            elif section=='geography': fields=[item['name'],item['basin'],item['identity_level'],item.get('event_year')]
            else: fields=[item['name'],item['basin'],item['identity_level'],item.get('source_event_date'),item.get('event_year'),item.get('date_evidence',{}).get('observation_start')]
            if section=='inventory' and not query or query not in ' '.join(str(v) if v is not None else '' for v in fields).lower(): continue
            row={'record':item,'source_pointer':f'/entries/{ordinal}'}
            if section=='loop': row.update(relation=contexts[item['id']],parent=loop.get(item.get('related_primary_id')))
            elif section=='geography': row.update(relation=geo_joins[item['id']],parent=geography.get(item.get('member_of')),related_current=currents.get(item.get('related_current_id')))
            else:
                row['source_label']={'horizon_loop_current':'Loop register','published_loop_current':'Published study'}.get(item['source_collection'],item['basin'])
                row['date_label']=next(v for v in [item.get('date_evidence',{}).get('observation_start'),item.get('source_event_date'),item.get('event_year'),item['identity_level']] if v)
            rows.append(row)
        return rows
    selections=[{'section':'loop'},{'section':'loop','text':'II'},
                {'section':'geography'},{'section':'geography','text':'jeannette'},
                {'section':'inventory','text':'kraken'},{'section':'inventory','text':'2021'}]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet=Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        native_views=[]
        for selection in selections:
            run=subprocess.run([str(CLI),'--index',str(packet),'--eddies','-'],input=json.dumps(selection),
                               text=True,encoding='utf-8',capture_output=True)
            assert run.returncode==0,run.stderr
            view=json.loads(run.stdout)
            assert view['rows']==oracle(selection['section'],selection.get('text','')),selection
            assert view['total']==len(sources[selection['section']]['entries'])
            native_views.append(view)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('oswIndexEddyViews.loop')==native_views[0]
            assert page.evaluate('oswIndexEddyViews.geography')==native_views[2]
            assert page.locator('#eddy-rows tr').count()==96
            assert page.locator('#eddy-geography-rows tr').count()==35
            selectors={'loop':'#eddy-search','geography':'#eddy-geography-search','inventory':'#all-eddy-search'}
            for selection,expected in zip(selections,native_views):
                section=selection['section'];query=selection.get('text','')
                page.evaluate('section=>{oswIndexEddyViews[section]=null}',section)
                page.locator(selectors[section]).fill(query)
                page.locator(selectors[section]).dispatch_event('input')
                page.wait_for_function('section=>oswIndexEddyViews[section]',arg=section,timeout=90000)
                assert page.evaluate('section=>oswIndexEddyViews[section]',section)==expected
            # Every inventory identity can be found without collapsing equal names.
            found=set()
            for item in sources['inventory']['entries']:
                selection={'section':'inventory','text':item['name']}
                actual=page.evaluate('s=>oswIndexEddies(s)',selection)
                assert actual['rows']==oracle('inventory',item['name'])
                found.update(r['record']['id'] for r in actual['rows'])
            assert found=={r['id'] for r in sources['inventory']['entries']}
            for selection in [{'section':'unknown'},{'section':'loop','extra':True},{}]:
                assert page.evaluate('s=>oswIndexEddies(s).then(()=>false,()=>true)',selection)
            # Family links reveal the family even when the child's search hid it.
            member=next(r for r in sources['geography']['entries'] if r.get('member_of'))
            page.locator('#eddy-geography-search').fill(member['name'])
            page.wait_for_function('text=>oswIndexEddyViews.geography.text===text',arg=member['name'])
            page.locator(f'#eddy-geography-{member["id"]} a[href="#eddy-geography-{member["member_of"]}"]').click()
            page.wait_for_function('hash=>location.hash===hash && oswIndexEddyViews.geography.rows.length===35',arg='#eddy-geography-'+member['member_of'])
            page.locator('#eddy-geography-search').fill('jeannette')
            page.wait_for_function("oswIndexEddyViews.geography.text==='jeannette'")
            marker=page.locator('#motion-markers a[data-record="batumi-eddy-region"]')
            marker.focus()
            marker.press('Enter')
            page.wait_for_function("location.hash==='#eddy-geography-batumi-eddy-region' && oswIndexEddyViews.geography.rows.length===35")
            page.locator('#eddy-search').fill('Edison')
            page.wait_for_function("oswIndexEddyViews.loop.text==='Edison'")
            page.locator('#all-eddy-search').fill('Feldman')
            page.wait_for_function("oswIndexEddyViews.inventory.text==='Feldman'")
            page.locator('#all-eddy-results a[href="#eddy-loop-81-primary"]').click()
            page.wait_for_function("location.hash==='#eddy-loop-81-primary' && oswIndexEddyViews.loop.rows.length===96")
            for query in ['jeannette','haida','sitka']:
                page.locator('#eddy-geography-search').fill(query)
            page.wait_for_function("oswIndexEddyViews.geography.text==='sitka'")
            assert page.evaluate('oswIndexEddyViews.geography.rows')==oracle('geography','sitka')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('#eddy-geography-search').fill('Astrid')
            page.wait_for_function("oswIndexEddyViews.geography.text==='Astrid'",timeout=90000)
            chart=page.locator('#eddy-geography-astrid-2000 .eddy-radial-scales svg')
            assert '120 km maximum-speed radius' in chart.locator('text').all_text_contents()
            assert '140 km integration limit' in chart.locator('text').all_text_contents()
            assert 'not a seasonal range' in chart.get_attribute('aria-label')
            assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html?atlas-feature=eddy%3Ageography%3Aastrid-2000#route-atlas',wait_until='networkidle')
            chart=page.locator('#route-atlas-preview .eddy-radial-scales svg');chart.wait_for(state='visible',timeout=90000)
            assert chart.locator('text').evaluate_all('(es)=>es.every(e=>{const b=e.getBoundingClientRect(),s=e.ownerSVGElement.getBoundingClientRect();return b.left>=s.left && b.right<=s.right})')
            assert chart.locator('text').first.evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)*e.getScreenCTM().a>=12')
            assert 'closed footprint' in page.locator('#route-atlas-preview .eddy-radial-scales').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            chart.screenshot(path=str(ROOT/'.pytest_cache/astrid-radial-scales-mobile.png'))
            page.locator('#route-atlas-preview .eddy-radial-scales a').click()
            page.wait_for_function('window.oswSourceQueryResult?.rows.length===2',timeout=90000)
            request={'document':'research/astrid-2000-radial-scale-scope-audit.json','pointer':'/measurements','limit':10}
            expected=json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(request),encoding='utf8'))
            assert page.evaluate('oswSourceQueryResult')==expected
            assert [r['record']['value_km'] for r in expected['rows']]==[120,140]
            assert not errors,errors
            browser.close()
    from test_astrid_radial_scales import check_compiled_loader_rejects_coherent_scope_rewrites
    scratch=ROOT/'.pytest_cache/astrid-native-gate';scratch.mkdir(exist_ok=True)
    check_compiled_loader_rejects_coherent_scope_rewrites(scratch)
    print('PASS: 96 Loop/35 geography source records and joins; all 136 inventory identities, six native/WASM views, family/map/inventory navigation, rapid search and mobile layout')


if __name__=='__main__': main()
