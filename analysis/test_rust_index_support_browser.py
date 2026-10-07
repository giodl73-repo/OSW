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
            page.locator('#current-search').fill('does-not-exist')
            page.wait_for_function('document.querySelector("#current-rows").children.length===0')
            page.locator('#illustrated-span-rows a').first.click()
            page.wait_for_function('document.querySelector("#current-search").value===""&&document.querySelector("#current-rows").children.length===100')
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert not errors,errors
            browser.close()
    print('PASS: 52 source decisions/all filters/names, 24 original display spans, 56 states × both diagnostic sets, native/WASM and DOM parity, invalid selections, current navigation and mobile')


if __name__ == '__main__': main()
