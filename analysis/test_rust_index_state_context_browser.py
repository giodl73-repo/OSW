"""State routes/local observations/point context/movie joins retain source dates."""
import gzip
import json
import os
from pathlib import Path
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT,CLI


def main():
    def read(path):return json.loads((ROOT/path).read_bytes())
    join=read('research/ocean-motion-state-join.json')
    codes=list(join['states'])
    seasons=read('research/noaa-munster-eddy-seasonal-manifest-2021-2023.json')
    front=read('research/gulf-stream-navo-state-snapshot-20260928.json')
    diagnosed=read('almanac/release/v0.1.0/source-ledgers/gulf-stream-geostrophic-path-20260925.json')
    local=read('almanac/release/v0.1.0/named_current_source_observations.json')
    operational=read('almanac/release/v0.1.0/operational_eddy_state_observations.json')
    currents={r['id']:r for r in read('research/ocean-current-almanac.json')['entries']}
    geography=read('research/named-eddy-geography-join.json')
    names={r['id']:r for r in read('research/named-eddy-geography.json')['entries']}
    loops=read('research/named-loop-eddy-nasa-context.json')
    loop_names={r['id']:r for r in loops['entries']}
    movies=read('research/nasa-perpetual-ocean-state-tile-join.json')
    timeline=read('research/nasa-perpetual-ocean-crop-timeline.json')
    routes=read('research/ocean-current-reference-route-state-join.json')
    def oracle(code,date):
        movie=movies['states'][code]
        matches={r['tile_id']:r for r in movie['matches']}
        return {'state_code':code,'date':date,'reference_routes':routes['states'].get(code),
                'front':front['states'][code],'front_date':front['date'],'front_source_url':front['source_url'],'front_claim_limit':front['claim_limit'],
                'diagnosed_relation':next((r for r in diagnosed['state_relations'] if r['state_code']==code),None),
                'diagnosed_date':diagnosed['observation_date'],'diagnosed_length_km':diagnosed['representative']['segment_length_km'],
                'diagnosed_product_page':diagnosed['product_page'],'diagnosed_physical_limit':diagnosed['physical_limit'],
                'current_observations':[{'record':r,'current':currents[r['entity_id'].removeprefix('current:')]} for r in local if r['state_id']=='state:'+code],
                'operational_eddy_observations':[r for r in operational if r['state_id']=='state:'+code],
                'named_eddy_positions':[{'record':r,'eddy':names[r['eddy_id']]} for r in geography.get('states_with_additional_observed_positions',{}).get(code,[])],
                'loop_region_names':[loop_names[id] for id in loops['states'].get(code,[])],
                'published_loop_positions':[loop_names[id] for id in loops.get('states_with_published_positions',{}).get(code,[])],
                'movie_selection':movie,'recommended_movies':[matches[id] for id in movie['recommended_regional_tiles']],
                'overview_movie':matches[movie['overview_tile']]}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet=Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        run=subprocess.run([str(CLI),'--index',str(packet),'--state-context','-'],input=json.dumps({'state_codes':codes}),
                           text=True,encoding='utf-8',capture_output=True)
        assert run.returncode==0,run.stderr
        expected=json.loads(run.stdout)
        assert expected['views']==[oracle(code,'2023-06-01') for code in codes]
        assert expected['movie_seek']==timeline['dates'].get('2023-06-01')
        assert expected['movie_time_limit']==timeline['limit']
        assert expected['movie_evidence_limit']==movies['evidence_limit']
        assert expected['named_eddy_position_limit']==geography['evidence_limit']
        assert expected['loop_position_limit']==loops['evidence_limit']
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/index.html?state=GFST')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('r=>oswIndexStateContext(r)',{'state_codes':codes})==expected
            for snapshot in seasons['snapshots']:
                date=snapshot['date']
                actual=page.evaluate('r=>oswIndexStateContext(r)',{'state_codes':codes,'date':date})
                assert actual['views']==[oracle(code,date) for code in codes]
                assert actual['movie_seek']==timeline['dates'].get(date)
                assert actual['movie_alignment_status']==timeline['alignment_status']
            for code in codes:
                page.locator('#state-select').select_option(code)
                page.wait_for_function('code=>oswIndexStateContextView?.views[0].state_code===code',arg=code,timeout=90000)
                view=oracle(code,'2023-06-01')
                assert page.evaluate('oswIndexStateContextView.views[0]')==view
                if view['reference_routes']:
                    assert page.locator('.state-reference-routes li[data-candidate-id]').evaluate_all('(nodes)=>nodes.map(n=>n.dataset.candidateId)')==[
                        r['candidate_id'] for r in view['reference_routes']['route_candidates']]
                assert page.locator('.state-source-observation').count()==len(view['current_observations'])
                assert page.locator('.operational-eddy-details li').count()==len(view['operational_eddy_observations'])
                urls=[]
                for movie in [*view['recommended_movies'],view['overview_movie']]:
                    urls.append(movie['url'])
                    if expected['movie_seek']:urls.append(movie['url']+'#t='+str(expected['movie_seek']['estimated_crop_seconds']))
                if view['movie_selection'].get('polar_perspective'):urls.append(view['movie_selection']['polar_perspective']['url'])
                assert page.locator('.state-movie-list a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')==urls
            page.locator('#state-select').select_option('CAMR')
            page.wait_for_function("oswIndexStateContextView.views[0].state_code==='CAMR'")
            for snapshot in seasons['snapshots']:
                date=snapshot['date']
                page.locator('#eddy-date-select').select_option(date)
                page.wait_for_function("!document.querySelector('#eddy-date-select').disabled",timeout=90000)
                assert page.evaluate('oswIndexStateContextView.date')==date
                view=page.evaluate('oswIndexStateContextView.views[0]')
                assert view==oracle('CAMR',date)
                assert view['front_date']=='2026-09-28' and view['diagnosed_date']=='2026-09-25'
                links=page.locator('.state-movie-list a').evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("href"))')
                seek=timeline['dates'].get(date)
                assert sum('#t=' in url for url in links)==(len(view['recommended_movies'])+1 if seek else 0)
            for request in [{'state_code':'invented'},{'state_codes':['GFST','GFST']},{'state_code':'GFST','state_codes':['GFST']},{'state_code':'GFST','date':'2023-06-02'},{'extra':True}]:
                assert page.evaluate('r=>oswIndexStateContext(r).then(()=>false,()=>true)',request)
            page.set_viewport_size({'width':320,'height':800})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert not errors,errors
            browser.close()
    print('PASS: 56-state source context joins across all 12 sample dates, fixed observation dates, movie seek gaps/scopes, native/WASM and DOM parity, invalid requests and mobile layout')


if __name__=='__main__':main()
