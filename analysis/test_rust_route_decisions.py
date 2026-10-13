"""Complete route worklist, source receipts, strict joins and browser navigation."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import native, browser_query

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_bytes())

def main():
    bundle=read('almanac/query-data.json');collections=bundle['collections']
    source=read('research/ocean-current-reference-path-candidates.json')
    rows=collections['route_decisions'];assert len(rows)==89
    originals={r['current_id']:r for r in source['remaining_current_decisions']}
    owners={r['id']:r for r in collections['objects']}
    sicu=next(r for r in rows if r['current_id']=='solomon-island-coastal-undercurrent')
    assert sicu['candidate_count']==1 and not sicu['rank_eligible']
    reviewed=sicu['scope_reviews'][0]['document']
    assert reviewed['flow_evidence_class']=='modeled_proposal_with_later_regional_observational_interpretation'
    assert reviewed['whole_current_length_km'] is None and reviewed['whole_current_width_km'] is None
    assert reviewed['observed_period'] is None and not reviewed['seasonal_playback_eligible']
    assert len(reviewed['evidence_contexts'])==3
    assert {r['current_id'] for r in rows}==set(originals)
    assert sum(r['candidate_count']==0 for r in rows)==28
    assert sum(r['candidate_count'] for r in rows)==64
    for row in rows:
        assert row['source_decision']==originals[row['current_id']]
        assert sorted(row['route_ids'])==sorted(owners[row['entity_id']]['route_ids'])
        assert owners[row['entity_id']]['route_decision_ids']==[row['id']]
        for review in row['scope_reviews']:assert review['document']==read(review['note']['audit_file'])
    audit=read('research/pacific-secc-argo-seasonal-extent-scope-audit.json')
    assert [p['eastward_longitude_span_degrees'] for p in audit['phases']]==[40,70]
    for phase in audit['phases']:
        west,east=phase['reported_longitude_limits_degrees_east']
        assert (east-west)%360==phase['eastward_longitude_span_degrees']
        assert phase['calendar_months'] is None and phase['axis_coordinates_lon_lat'] is None
    assert not audit['seasonal_route_playback_supported']
    assert all(audit[k] is None for k in ['observed_period','whole_current_length_km','whole_current_width_km','annual_length_range_km','annual_width_range_km'])
    queries=[{'collection':'route_decisions','limit':100},
        {'collection':'route_decisions','filters':[{'field':'candidate_count','op':'eq','value':0}],'sort':{'field':'strategy_label'},'limit':100},
        {'collection':'route_decisions','filters':[{'field':'strategy_id','op':'eq','value':'split_basin_family'}],'limit':100},
        {'collection':'route_decisions','filters':[{'field':'current_id','op':'eq','value':'solomon-island-coastal-undercurrent'}]}]
    assert [native(q)['total'] for q in queries]==[89,28,8,1]
    # Loader rejects forged planner coverage, cross-owner joins and admission.
    with tempfile.TemporaryDirectory() as temporary:
        path=Path(temporary)/'bundle.json'
        for mutation in ['next_action','rank','coverage','missing','receipt','review_owner','owner_link']:
            altered=copy.deepcopy(bundle);decision=altered['collections']['route_decisions'][0]
            if mutation=='next_action':decision['next_action']='Invent a current length'
            elif mutation=='rank':decision['rank_eligible']=True
            elif mutation=='coverage':decision['candidate_count']=999
            elif mutation=='missing':altered['collections']['route_decisions'].pop()
            elif mutation=='receipt':decision['source_catalog_sha256']='0'*64
            elif mutation=='review_owner':
                target=next(r for r in altered['collections']['route_decisions'] if r['scope_reviews'])
                target['scope_reviews'][0]['document']['current_id']='other'
            else:
                owner=next(r for r in altered['collections']['objects'] if r['id']==decision['entity_id'])
                owner['route_decision_ids']=[altered['collections']['route_decisions'][1]['id']]
            path.write_text(json.dumps(altered),encoding='utf-8')
            process=subprocess.run([str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe'),str(path),'-'],input='{}',text=True,capture_output=True)
            assert process.returncode==2 and not process.stdout,(mutation,process.stdout,process.stderr)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1280,'height':1000});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto('http://127.0.0.1:8788/almanac/query.html');page.wait_for_function('window.oswLastQueryResult',timeout=60000)
        for query in queries:assert browser_query(page,query)==native(query)
        page.locator('[data-preset="unbuilt-decisions"]').click()
        expect(page.locator('#query-page')).to_contain_text('28 of 28')
        expect(page.locator('#query-decision-status')).to_have_value('reference_path_not_constructed')
        page.locator('#query-sort').select_option('label')
        page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===28')
        page.locator('#query-decision-strategy').select_option('seasonal_routes')
        page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===5')
        page.locator('#query-decision-status').select_option('')
        page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===14')
        extra={'collection':'route_decisions','filters':[{'field':'candidate_count','op':'eq','value':0},{'field':'strategy_id','op':'eq','value':'seasonal_routes'},{'field':'strategy_id','op':'eq','value':'system_route_graph'}]}
        browser_query(page,extra);expect(page.locator('#query-decision-extra')).to_be_visible()
        page.evaluate('window.oswLastQueryResult=null');page.locator('#query-run').click()
        page.wait_for_function('window.oswLastQueryResult?.total===0')
        actual=json.loads(page.locator('#query-json').input_value())
        assert len(actual['filters'])==3 and all(f in actual['filters'] for f in extra['filters'])
        page.locator('[data-preset="length-decisions"]').click()
        expect(page.locator('#query-page')).to_contain_text('89 of 89')
        query={'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:pacific-south-equatorial-countercurrent'}]}
        browser_query(page,query);page.locator('#query-rows button').first.click()
        expect(page.locator('#query-detail')).to_contain_text('Next evidence needed')
        expect(page.locator('#query-detail')).to_contain_text('Recover compatible numerical total-flow axes')
        expect(page.locator('#query-detail')).to_contain_text('full 2026 methods')
        page.locator('#query-detail a').filter(has_text='Query remaining length decision').click()
        page.wait_for_function('window.oswLastQueryResult?.collection==="route_decisions"',timeout=60000)
        expect(page.locator('#query-decision-current')).to_have_value('current:pacific-south-equatorial-countercurrent')
        page.locator('#query-rows button').first.focus();page.locator('#query-rows button').first.press('Enter')
        expect(page.locator('#query-detail')).to_contain_text('Argo seasonal envelope and dateline scope')
        expect(page.locator('#query-detail')).to_contain_text('Full methods, figures and supplementary file not acquired')
        expect(page.locator('#query-detail')).to_contain_text('WOA01 mean flow and seasonal anomaly separation')
        page.get_by_text('WOA01 mean flow and seasonal anomaly separation',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text('University-hosted full PDF acquired')
        page.locator('#query-detail').screenshot(path=str(ROOT/'figures/rust-query-route-decisions-review.png'))
        page.set_viewport_size({'width':320,'height':900})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert not errors;browser.close()
    print('PASS: all 89 route decisions; 28 unbuilt; eight families; 64 route references; SICU evidence separation; source receipts and scope fidelity; seven loader rejection cases; native/WASM parity and keyboard/card/mobile navigation')

if __name__=='__main__':main()
