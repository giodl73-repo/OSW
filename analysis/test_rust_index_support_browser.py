"""Source name decisions, display spans and diagnostic relations stay distinct."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(path): return json.loads((ROOT/path).read_bytes())
    currents = {r['id']:r for r in read('research/ocean-current-almanac.json')['entries']}
    names = read('research/marine-regions-current-crosswalk.json')
    spans = read('research/ocean-current-illustrated-spans.json')
    codes = list(read('research/ocean-motion-state-join.json')['states'])
    timelines = [(year,read(source),source) for year,source in [
        ('2025','research/ocean-current-dated-timeline-2025.json'),
        ('2026','research/ocean-current-dated-timeline.json')]]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as folder:
        packet = Path(folder)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        def native(request):
            run = subprocess.run([str(CLI),'--index',str(packet),'--support','-'],input=json.dumps(request),
                                 text=True,encoding='utf-8',capture_output=True)
            assert run.returncode == 0,run.stderr
            return json.loads(run.stdout)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page(viewport={'width':1440,'height':1000})
            errors = []
            page.on('pageerror',lambda e: errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html?state=GFST')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            def query(request): return page.evaluate('r=>oswIndexSupport(r)',request)
            for facet in ['all','matched','excluded','candidate_needs_review']:
                request = {'section':'reconciliation','filter':facet}
                view = query(request)
                assert view == native(request)
                expected = []
                for index,record in enumerate(names['records']):
                    matched = record['join_status'].startswith('matched')
                    excluded = not matched and record['join_status'] != 'candidate_needs_review'
                    if facet=='matched' and not matched or facet=='excluded' and not excluded or facet=='candidate_needs_review' and record['join_status']!=facet: continue
                    expected.append({'record':record,'current':currents.get(record.get('osw_current_id')),
                                     'status_label':('Exact name match' if record['join_status']=='matched_exact_name' else 'Alias to review') if matched else 'Other type' if excluded else 'Needs review',
                                     'source':'research/marine-regions-current-crosswalk.json','source_pointer':'/records/'+str(index)})
                assert view['rows'] == expected
                page.locator('#source-current-filter').select_option(facet)
                page.wait_for_function('facet=>oswIndexReconciliationView.rows.length===Number(facet)',arg=str(len(expected)))
                assert page.locator('#source-current-rows tr').evaluate_all('(nodes)=>nodes.map(n=>n.id)') == ['mr-current-'+str(r['record']['mrgid']) for r in expected]
            for record in names['records']:
                text = record['name'].upper()
                view = query({'section':'reconciliation','text':text})
                assert [r['record'] for r in view['rows']] == [r for r in names['records'] if text.lower() in ' '.join(str(r.get(k) or '') for k in ['name','source','join_note','review_note']).lower()]
            request = {'section':'illustrated_spans'}
            view = query(request)
            assert view == native(request)
            expected = [{'record':record,'current':currents[record['current_id']],
                         'source':'research/ocean-current-illustrated-spans.json','source_pointer':'/entries/'+str(index)}
                        for index,record in enumerate(spans['entries']) if record.get('illustrated_span_rank') is not None]
            assert view['rows'] == expected and view['counts'] == spans['counts']
            assert view['metric'] == spans['metric'] and view['ranking_rule'] == spans['ranking_rule']
            assert page.locator('#illustrated-span-rows tr').count() == len(expected) == 24
            for code in codes:
                view = query({'section':'diagnostic_samples','state_code':code})
                expected = [{'year':year,'frame':frame,'relation':relation,'source':source,
                             'source_pointer':f'/frames/{index}/state_relations/{ri}',
                             'atlas_url':f"reference-routes.html?atlas-feature=current%3Agulf-stream-system&atlas-series={year}&atlas-date={frame['date']}#route-atlas"}
                            for year,doc,source in timelines for index,frame in enumerate(doc['frames'])
                            for ri,relation in enumerate(frame['state_relations']) if relation['state_code']==code]
                assert view['rows'] == expected
                if code=='GFST': assert view == native({'section':'diagnostic_samples','state_code':code})
                page.locator('#state-select').select_option(code)
                page.wait_for_function('code=>oswIndexStateMembershipView?.state_code===code',arg=code)
                page.wait_for_function('()=>{const p=document.querySelector(".state-dated-samples summary");return p&&!p.textContent.includes("loading")}',timeout=90000)
                assert page.locator('.state-dated-samples li[data-sample-date]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.sampleDate)') == [r['frame']['date'] for r in expected]
            for request in [{'section':'invented'},{'section':'reconciliation','filter':'invented'},
                            {'section':'illustrated_spans','text':''},{'section':'diagnostic_samples','state_code':'invented'},
                            {'section':'diagnostic_samples','state_code':'GFST','filter':'all'},{'section':'reconciliation','extra':True}]:
                assert page.evaluate('r=>oswIndexSupport(r).then(()=>false,()=>true)',request)
            monthly=read('research/indian-sec-monthly-bifurcation-extraction.json')
            for series in monthly['series']:
                for row in series['months']:
                    request={'section':'monthly_bifurcation','filter':series['id'],'month':row['month']}
                    view=query(request)
                    assert view==native(request)
                    assert view['selected']['latitude']==row['approximate_latitude_degrees_north']
                    assert view['rows']==series['months'] and view['layer']==series['layer']
                    assert view['geographic_playback_eligible'] is False
            pacific=read('research/pacific-nec-monthly-bifurcation-extraction.json')
            for row in pacific['series'][0]['months']:
                request={'section':'monthly_bifurcation','current_id':'pacific-north-equatorial','filter':'surface_ssh','month':row['month']}
                view=query(request)
                assert view==native(request)
                assert view['rows']==pacific['series'][0]['months']
                assert view['source_period']==pacific['series'][0]['source_period']
                assert view['selected']['latitude']==row['approximate_latitude_degrees_north']
                assert view['selected']['source_band']==row['approximate_source_standard_deviation_band_degrees_north']
                assert view['selected']['band_endpoint_reading_intervals']==row['band_endpoint_plot_reading_intervals_degrees_north']
                assert view['source_variability_kind']==pacific['source_variability_kind']
                assert view['geographic_playback_eligible'] is False
                assert view['selected']['y']==210-(row['approximate_latitude_degrees_north']-8)*16
            for request in [{'section':'monthly_bifurcation','month':13},{'section':'monthly_bifurcation','filter':'model'},
                            {'section':'monthly_bifurcation','state_code':'GFST'},{'section':'reconciliation','month':1},{'section':'reconciliation','current_id':'pacific-north-equatorial'},
                            {'section':'monthly_bifurcation','current_id':'invented'},
                            {'section':'monthly_bifurcation','current_id':'pacific-north-equatorial','filter':'wod_upper400'}]:
                assert page.evaluate('r=>oswIndexSupport(r).then(()=>false,()=>true)',request)
            page.wait_for_function('window.oswIndexBifurcationView?.month===1')
            assert page.locator('#branch-chart svg polyline').count()==2
            page.locator('#branch-series').select_option('wod_upper400')
            page.wait_for_function('window.oswIndexBifurcationView?.series_id==="wod_upper400"&&document.querySelector("#branch-status").dataset.pending==="false"')
            page.locator('#branch-month').evaluate('(el)=>{el.value="6";el.dispatchEvent(new Event("change",{bubbles:true}));}')
            page.wait_for_function('window.oswIndexBifurcationView?.month===6')
            assert '18.6\u00b0S' in page.locator('#branch-status').inner_text()
            upper_source=next(s for s in monthly['series'] if s['id']=='wod_upper400')
            assert upper_source['period_note'] in page.locator('#branch-scope').inner_text()
            assert page.locator('#branch-rows tr').count()==12
            shared_url=page.locator('#branch-share').get_attribute('href')
            shared=browser.new_page();shared.goto(shared_url)
            shared.wait_for_function('window.oswIndexBifurcationView?.month===6&&oswIndexBifurcationView?.series_id==="wod_upper400"',timeout=90000)
            shared.close()
            page.clock.install()
            page.locator('#branch-play').click()
            for month in range(7,13):
                page.clock.run_for(1300)
                page.wait_for_function('month=>window.oswIndexBifurcationView?.month===month',arg=month)
            assert page.locator('#branch-play').inner_text()=='Play months'
            assert page.locator('#branch-next').is_disabled()
            # Hold the Home request: the focused slider must survive loading and
            # accept the next key. A late older reply must not repaint January.
            page.evaluate("""() => {
                const original=window.oswIndexSupport; let hold=true;
                window.oswIndexSupport=request=>{
                    if(hold){hold=false;return new Promise(resolve=>{
                        window.releaseBranchRequest=()=>original(request).then(resolve);
                    });}
                    return original(request);
                };
                window.restoreBranchSupport=()=>{window.oswIndexSupport=original;};
            }""")
            page.locator('#branch-month').focus();page.keyboard.press('Home')
            page.wait_for_function('document.querySelector("#branch-status").dataset.pending==="true"')
            assert page.locator('#branch-month').is_enabled()
            assert page.locator('#branch-month').evaluate('(el)=>document.activeElement===el')
            assert page.locator('#branch-month').input_value()=='1'
            page.keyboard.press('ArrowRight')
            page.wait_for_function('window.oswIndexBifurcationView?.month===2&&document.querySelector("#branch-status").dataset.pending==="false"')
            page.evaluate('()=>window.releaseBranchRequest()')
            assert page.evaluate('window.oswIndexBifurcationView.month')==2
            assert page.locator('#branch-month').input_value()=='2'
            assert page.locator('#branch-month').evaluate('(el)=>document.activeElement===el')
            page.evaluate('()=>window.restoreBranchSupport()')
            page.locator('#branch-play').click()
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function('document.querySelector("#branch-play").textContent==="Play months"')
            page.clock.run_for(2600)
            assert page.evaluate('window.oswIndexBifurcationView.month')==2
            # Source switching resets unsupported layers and replaces hemisphere, scope and band.
            page.locator('#branch-current').select_option('pacific-north-equatorial')
            page.wait_for_function('window.oswIndexBifurcationView?.current_id==="pacific-north-equatorial"&&document.querySelector("#branch-status").dataset.pending==="false"')
            assert page.locator('#branch-series').input_value()=='surface_ssh'
            assert page.locator('#branch-series option[value="wod_upper400"]').evaluate('(el)=>el.disabled')
            assert page.locator('#branch-chart svg polyline').count()==1
            band=page.locator('#branch-chart svg polygon[data-source-band="standard-deviation"]')
            assert band.count()==1
            source_rows=pacific['series'][0]['months']
            expected_points=[f"{56+i*48},{210-(r['approximate_source_standard_deviation_band_degrees_north'][1]-8)*16}" for i,r in enumerate(source_rows)]
            expected_points += [f"{56+i*48},{210-(r['approximate_source_standard_deviation_band_degrees_north'][0]-8)*16}" for i,r in reversed(list(enumerate(source_rows)))]
            actual_points=[[float(c) for c in point.split(',')] for point in band.get_attribute('points').split()]
            assert len(actual_points)==len(expected_points)==24
            assert all(abs(a-float(e))<1e-9 for actual,expected in zip(actual_points,expected_points) for a,e in zip(actual,expected.split(',')))
            assert '12.0\u00b0N' in page.locator('#branch-status').inner_text()
            assert '1992-10 to 2009-12' in page.locator('#branch-scope').inner_text()
            assert 'denominator and multiplier are not recovered' in page.locator('#branch-legend').inner_text()
            assert 'not a confidence interval' in page.locator('#branch-legend').inner_text()
            assert page.locator('#branch-source').get_attribute('href')==pacific['source_url']
            assert page.locator('#branch-source').inner_text()==pacific['source_locator']
            assert page.locator('#branch-card').get_attribute('href').endswith('#inventory-addition-pacific-north-equatorial')
            for i,row in enumerate(source_rows):
                cells=page.locator('#branch-rows tr').nth(i).locator('td').all_text_contents()
                assert len(cells)==4 and cells[1]==f"{row['approximate_latitude_degrees_north']:.1f}\u00b0N"
                assert 'endpoint reading allowances' in cells[3]
            shared_url=page.locator('#branch-share').get_attribute('href')
            from urllib.parse import urlparse,parse_qs
            assert parse_qs(urlparse(shared_url).query)['state']==[codes[-1]]
            shared=browser.new_page();shared.goto(shared_url)
            shared.wait_for_function('window.oswIndexBifurcationView?.current_id==="pacific-north-equatorial"&&oswIndexBifurcationView?.month===2',timeout=90000)
            assert shared.locator('#branch-chart svg polygon').count()==1
            shared.close()
            page.locator('#branch-play').click()
            for month in range(3,13):
                page.clock.run_for(1300)
                page.wait_for_function('month=>window.oswIndexBifurcationView?.month===month',arg=month)
            assert page.locator('#branch-play').inner_text()=='Play months'
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('#branch-chart svg text').first.evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)')==22
            page.locator('#branch-table').focus();page.keyboard.press('ArrowRight');page.clock.run_for(250)
            page.wait_for_function('document.getElementById("branch-table").scrollLeft>0')
            page.locator('#branching-cycles').screenshot(path=str(ROOT/'.pytest_cache/pacific-branching-mobile.png'))
            page.locator('#branch-play').click()
            page.wait_for_function('window.oswIndexBifurcationView?.month===1&&document.querySelector("#branch-status").dataset.pending==="false"')
            page.locator('#branch-current').select_option('indian-south-equatorial')
            page.wait_for_function('window.oswIndexBifurcationView?.current_id==="indian-south-equatorial"&&document.querySelector("#branch-status").dataset.pending==="false"')
            assert page.locator('#branch-play').inner_text()=='Play months'
            page.clock.run_for(2600)
            assert page.evaluate('window.oswIndexBifurcationView.month')==1
            assert page.locator('#branch-chart svg polygon').count()==0
            assert page.locator('#branch-chart svg polyline').count()==2
            assert not page.locator('#branch-series option[value="wod_upper400"]').evaluate('(el)=>el.disabled')
            assert 'Not extracted' in page.locator('#branch-rows').inner_text()
            assert 'Chen' in page.locator('#branch-source').inner_text()
            assert page.locator('#branch-card').get_attribute('href').endswith('#inventory-addition-indian-south-equatorial')
            page.locator('#current-search').fill('does-not-exist')
            page.wait_for_function('document.querySelector("#current-rows").children.length===0')
            page.locator('#illustrated-span-rows a').first.click()
            page.wait_for_function('document.querySelector("#current-search").value===""&&document.querySelector("#current-rows").children.length===100')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for control in ['#branch-current','#branch-series','#branch-prev','#branch-next','#branch-play','#branch-month']:
                assert page.locator(control).bounding_box()['height']>=44
            page.locator('#branching-cycles').screenshot(path=str(ROOT/'.pytest_cache/monthly-branching-mobile.png'))
            unavailable=browser.new_page()
            unavailable.route('**/index-data.json.gz',lambda route:route.fulfill(status=503,body='Source corpus unavailable'))
            unavailable.goto('http://127.0.0.1:8788/almanac/index.html#branching-title')
            unavailable.wait_for_function('document.querySelector("#branch-status").textContent.includes("unavailable")',timeout=90000)
            assert unavailable.locator('#branch-chart').is_hidden()
            assert unavailable.locator('#branch-rows tr').count()==0
            assert unavailable.locator('#branch-play').is_disabled()
            assert unavailable.locator('#branch-current').is_disabled()
            for link in ['#branch-source','#branch-card','#branch-share']:
                assert unavailable.locator(link).get_attribute('href') is None
            unavailable.close()
            assert not errors,errors
            browser.close()
    print('PASS: source decisions, 24 display spans, 56 state diagnostic joins, 36 branching samples/native-WASM parity, separate source band and endpoint allowances, owner/layer switching, monthly playback/share/keyboard/mobile and unavailable corpus')


if __name__ == '__main__': main()
