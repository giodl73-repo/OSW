"""Cloud-only, single-CPU browser verification of the eddy register."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.pytest_cache/eddy-measurement-register-browser-v1'
REQUEST='research/eddy-measurement-register-browser-request-v1.json'
PREFLIGHT='research/eddy-measurement-register-browser-preflight-v1.json'


def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def run():
    assert os.name=='posix' and os.environ.get('GITHUB_ACTIONS')=='true'
    assert os.environ.get('OSW_EDDY_REGISTER_BROWSER_V1')=='1'
    assert os.environ.get('GITHUB_REPOSITORY')=='giodl73-repo/OSW'
    assert os.environ.get('GITHUB_REF')=='refs/heads/codex/current-measurement-gaps'
    assert len(os.sched_getaffinity(0))==1 and os.getpriority(os.PRIO_PROCESS,0)>=15
    request=json.loads((ROOT/REQUEST).read_bytes())
    assert request['execute'] is True and request['preflight_sha256']==sha(PREFLIGHT)
    assert request['max_cloud_jobs']==1 and request['max_heavy_local_jobs']==0
    assert not any(request[k] for k in ['native_build_permitted','wasm_build_permitted','ocean_field_processing_permitted','installation_permitted','main_merge_permitted','local_bulk_sync_permitted'])
    preflight=json.loads((ROOT/PREFLIGHT).read_bytes())
    for path,pin in preflight['input_sha256'].items():assert sha(path)==pin,path
    document=json.loads((ROOT/'research/eddy-measurement-register-v1.json').read_bytes())
    OUT.mkdir(parents=True,exist_ok=True)
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.HTTPServer(('127.0.0.1',0),handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    base=f'http://127.0.0.1:{server.server_port}'
    from playwright.sync_api import sync_playwright
    errors=[];requests=[];assets=set();checks=[];page=None
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,args=['--disable-dev-shm-usage','--renderer-process-limit=1'])
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
            page=context.new_page();page.set_default_timeout(60000)
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:requests.append(request.url))
            page.goto(base+'/almanac/eddies.html')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            assert page.locator('#eddy-rows tr').count()==136
            ids=page.locator('#eddy-rows tr').evaluate_all('(els)=>els.map(e=>e.dataset.eddyId)')
            assert set(ids)=={r['entity_id'] for r in document['records']}
            links=page.locator('#eddy-rows tr td:first-child>a').evaluate_all('(els)=>els.map(e=>e.getAttribute("href"))')
            assert all(parse_qs(urlsplit(link).query)['id']==[owner] for link,owner in zip(links,ids))
            counts=document['counts']
            assert f"{counts['evidence_records']} evidence records across {counts['identities_with_measurements']} entries" in page.locator('#eddy-summary').inner_text()
            page.screenshot(path=str(OUT/'desktop.png'))
            for value,expected in [('individual_eddy',112),('recurrent_eddy_region',20),('eddy_family',4),('all',136)]:
                page.select_option('#eddy-identity',value);assert page.locator('#eddy-rows tr').count()==expected
            for value,expected in [('measured',counts['identities_with_measurements']),('gap',counts['identities_without_measurements']),('linked',counts['linked_primary_context_entries']),('unlinked-gap',2),('size-gap',sum(r['size_gap'] for r in document['records'])),('duration-gap',sum(r['duration_gap'] for r in document['records'])),('all',136)]:
                page.select_option('#eddy-filter',value);assert page.locator('#eddy-rows tr').count()==expected
            for category in ['size','duration','recurrence','travel','structure','kinematics','all']:
                page.select_option('#eddy-category',category)
                expected=sum(category=='all' or category in r['categories'] for r in document['records'])
                assert page.locator('#eddy-rows tr').count()==expected
            checks.append('All136 identities, card href identities and all coverage/category/identity filters')
            page.fill('#eddy-search','Agulhas Ring Eliza');assert page.locator('#eddy-rows tr').count()==1
            page.locator('#eddy-rows summary').click()
            assert 'Unresolved source values' in page.locator('#eddy-rows').inner_text()
            assert '88 km' in page.locator('#eddy-rows').inner_text() and '93 km' in page.locator('#eddy-rows').inner_text()
            assert 'Source year conflict unresolved' in page.locator('#eddy-rows').inner_text()
            assert 'parent-ring' in page.locator('#eddy-rows').inner_text()
            page.fill('#eddy-search','')
            for name in ['thor-2020','ursa-2021']:
                tr=page.locator(f'tr[data-eddy-id="eddy:published:{name}"]');tr.locator('summary').click()
                assert 'Paper window:' in tr.inner_text() and 'measured lifetime' in tr.inner_text()
                assert tr.locator('.eddy-record').count()==1
                assert 'Not an individual lifespan' in tr.inner_text()
            checks.append('Eliza value/year conflicts retained; parent-ring span and paper windows not promoted to individual lifetimes')
            page.select_option('#eddy-identity','eddy_family');page.fill('#eddy-search','Agulhas')
            assert page.locator('#eddy-rows tr').count()==1
            page.locator('#eddy-rows summary').click()
            assert page.locator('#eddy-rows .eddy-record').count()==7
            assert 'Table sample count: 2' in page.locator('#eddy-rows').inner_text()
            assert 'operator discrepancy' in page.locator('#eddy-rows').inner_text()
            assert '40 W' in page.locator('#eddy-rows').inner_text()
            page.select_option('#eddy-identity','all');page.fill('#eddy-search','Lilian')
            page.locator('#eddy-rows summary').click()
            text=page.locator('#eddy-rows').inner_text()
            assert '3.5 years' in text and '> 5,500 km' in text
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            checks.append('Seven population means/SD/cohorts; strict travel bound; approximate year unit; mobile expanded layout')
            page.set_viewport_size({'width':1440,'height':1000})
            for search,needles in [
                ('Kenai Eddy (2007)',['40 km','378 days','Track still present at the final study snapshot','disappearance date unknown']),
                ('Haida-1998',['Haida-1998a','Haida-1998b','no post-merger radius inferred','Approaches 50 km']),
                ('Agulhas Ring Laura',['8.6 km/day','Size reference needed'])]:
                page.fill('#eddy-search',search);assert page.locator('#eddy-rows tr').count()==1
                page.locator('#eddy-rows summary').click()
                for needle in needles:assert needle in page.locator('#eddy-rows').inner_text(),(search,needle)
            page.fill('#eddy-search','Meddy Ulla');page.locator('#eddy-rows summary').click()
            text=page.locator('#eddy-rows').inner_text()
            assert '15 km' in text and '18 months' in text and 'Publisher abstract' in text
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            checks.append('New Kenai/Sitka scope, right-censored Kenai span, distinct Haida components, Laura drift units and abstract-qualified Ulla months/radius')
            page.set_viewport_size({'width':1440,'height':1000})
            for search,needles in [
                ('Danube Eddy',['55 %','Not annual presence days']),
                ('Meddies (Mediterranean Water eddies)',['20–100 km','No representative midpoint inferred']),
                ('Cuba anticyclones',['< 100 km','CA6 model case','One model case']),
                ('Mindanao Eddy',['126 km','Model calculation:','Computed model reference']),
                ('New Guinea Eddy',['300 km','Qualified indexed reference']),
                ('Agulhas Eddy W',['2 weeks','5 degrees latitude','Angular displacement'])]:
                page.fill('#eddy-search',search);assert page.locator('#eddy-rows tr').count()==1,(search,'count')
                page.locator('#eddy-rows summary').click()
                for needle in needles:assert needle in page.locator('#eddy-rows').inner_text(),(search,needle)
            page.fill('#eddy-search','Peddies');page.locator('#eddy-rows summary').click()
            assert '200–300 m' in page.locator('#eddy-rows').inner_text()
            assert 'Not eddy thickness' in page.locator('#eddy-rows').inner_text()
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            checks.append('Third batch: range-only family size, depth band, strict bound, sampled/model cases, qualified indexed reference, native angular displacement and phase intervals')
            page.set_viewport_size({'width':1440,'height':1000})
            for search,needles,name in [
                ('Kathleen',['214–273 days','start 1988-01-01 to 1988-01-31','No midpoint'],'calendar-month.png'),
                ('Rebel',['0–2 days','Chronology-conditioned range','not missing data'],'calendar-zero.png'),
                ('Revelle',['3.9 knots','Registry maximum surface current as reported.'],None),
                ('Yazoo II',['no independent secondary measurement assigned','no values inherited'],'secondary-context.png')]:
                page.fill('#eddy-search',search);assert page.locator('#eddy-rows tr').count()==1
                page.locator('#eddy-rows summary').click()
                for needle in needles:assert needle in page.locator('#eddy-rows').inner_text(),(search,needle)
                if name:page.screenshot(path=str(OUT/name),full_page=True)
            assert page.locator('#eddy-rows .eddy-record').count()==0
            page.get_by_role('link',name='Inspect primary Yazoo',exact=True).click()
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            primary=page.locator('tr[data-eddy-id="eddy:horizon:loop-74-primary"]')
            assert primary.locator('details').evaluate('(e)=>e.open')
            assert primary.locator('.eddy-record').count()==1
            for name in ['Feldman','Edison']:
                page.fill('#eddy-search',name);page.locator('#eddy-rows summary').click()
                assert page.locator('#eddy-rows .eddy-record').count()==0
                assert 'current status and age have not been established' in page.locator('#eddy-rows').inner_text()
                if name=='Feldman':page.screenshot(path=str(OUT/'undated-active-label.png'),full_page=True)
            page.fill('#eddy-search','Kathleen');page.locator('#eddy-rows summary').click()
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(OUT/'mobile-calendar.png'),full_page=True)
            checks.append('Registry: native knots, full-month calendar support, explicit zero chronology condition, secondary noninheritance/primary navigation and undated Active labels without ages')
            page.set_viewport_size({'width':1440,'height':1000})
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-51-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            tr=page.locator('#eddy-rows');assert '7,596 km²' in tr.inner_text()
            for needle in ['0.17 m','2008-03-06','2008-03-10','Dates differ','inter-event spacing','physical identity crosswalk remains unverified']:
                assert needle in tr.inner_text(),needle
            assert page.locator('[data-evidence-id="loop-51-dukhovskoy-2015-separation-area"]').count()==1
            page.screenshot(path=str(OUT/'published-area.png'),full_page=True)
            page.fill('#eddy-search','Millennium');page.locator('#eddy-rows summary').click()
            assert '44,392 km²' in tr.inner_text() and 'Source spelling Millenium' in tr.inner_text()
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(OUT/'mobile-published-area.png'),full_page=True)
            checks.append('27 published named separation areas: native square kilometres, study/registry date discrepancy, explicit spelling alias, unverified physical association and mobile layout')
            page.set_viewport_size({'width':1440,'height':1000})
            for search,needles in [
                ('Batumi Eddy',['100 km','source regional typical diameter']),
                ('Kaliakra Eddy',['60 km','Published model case','summer 1992 model case']),
                ('Peddies (Persian Gulf Water eddies)',['10 km','Published model case','Qualified indexed model reference','other instability cases']),
                ('Sevastopol Eddy',['70 km','15–20 cm/s','Published model case']),
                ('Agulhas Ring Lilian',['1,200 m','400 m','temperature and salinity anomalies','significant radial velocity signal','not form a thickness range'])]:
                page.fill('#eddy-search',search);assert page.locator('#eddy-rows tr').count()==1
                page.locator('#eddy-rows summary').click()
                for needle in needles:assert needle in page.locator('#eddy-rows').inner_text(),(search,needle)
                if search.startswith('Peddies'):page.screenshot(path=str(OUT/'peddy-model-case.png'),full_page=True)
            page.screenshot(path=str(OUT/'lilian-depth-diagnostics.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            assert page.locator('.eddy-scroll').evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(OUT/'mobile-depth-diagnostics.png'),full_page=True)
            checks.append('Regional typical size, explicit simulated cases and indexed model access, native cm/s range and separate Lilian depth diagnostics; mobile layout')
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Triton');page.locator('#eddy-rows summary').click()
            for needle in ['350 km','200 km','40–60 km','< 20 km','150–200 km','drifter orbit is not an outer boundary','southern cleavage fragment']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="triton-biggs-1996-southern-fragment-orbit-diameter"]').screenshot(path=str(OUT/'triton-fragment-orbit.png'))
            page.fill('#eddy-search','Poseidon');page.locator('#eddy-rows summary').click()
            for needle in ['67,000 km²','87,000 km²','300 km','350 km','290 km','310 km','0.7 m absolute','0.6 m absolute','102 days','2–7 cm/s','3–10 cm/s']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="poseidon-meunier-2018-0.6-area"]').screenshot(path=str(OUT/'poseidon-contour-area.png'))
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-66-secondary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            assert page.locator('#eddy-rows .eddy-record').count()==2
            for needle in ['304 days','Independent named source case','no primary values inherited','2017-12-19 to 2018-10-19','physical crosswalk remains unverified']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-independent-secondary.png'),full_page=True)
            checks.append('Triton orbital axes/radii and fragment scope; distinct Poseidon ADT contour areas and phases; Quantum II own sampling evidence without primary inheritance, deep link and mobile layout')
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Nautilus')
            page.locator('tr[data-eddy-id="eddy:horizon:loop-63-primary"] summary').click()
            for needle in ['40–80 km · graph estimate','30–70 km · graph estimate','30–130 km · graph estimate','A1A2 remerged child','5 km allowance','10 km','not pooled','not an area-equivalent']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="nautilus-a1a2-dwde-2020-digitized-mean-radius-range"]').screenshot(path=str(OUT/'nautilus-graph-envelope.png'))
            page.fill('#eddy-search','Revelle');page.locator('#eddy-rows summary').click()
            for needle in ['100–220 km · graph estimate','pre-split','first approximately 1-40 plotted days','day 51']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="revelle-f-pre-split-dwde-2020-digitized-mean-radius-range"]').screenshot(path=str(OUT/'revelle-pre-split-graph.png'))
            page.fill('#eddy-search','Quantum II')
            assert page.locator('#eddy-rows details').evaluate('(e)=>e.open')
            for needle in ['40–100 km · graph estimate','304 days','no primary values inherited','plot ends well before the report sampling endpoint']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-graph-envelope.png'),full_page=True)
            checks.append('Graph estimates labeled separately; native mean contour radius, reading allowance/outward rounding, separate child cases, selected pre-split window and Quantum II plot endpoint without extrapolation')
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Bosphorus');page.locator('#eddy-rows summary').click()
            for needle in ['200 m','0.15–0.35 m/s','Published model case','day 40, 10 June 2000','not lens thickness','not assigned as a measured sampling depth']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="bosphorus-enriquez-2005-model-penetration"]').screenshot(path=str(OUT/'bosphorus-model-depth.png'))
            page.fill('#eddy-search','Caucasus');page.locator('#eddy-rows summary').click()
            for needle in ['100 m','0.1–0.15 m/s','6 days','3 days','17 days','occurrence 1','occurrence 2','occurrence 3','not a measured physical lifespan']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="caucasus-enriquez-2005-model-event-3-duration"]').screenshot(path=str(OUT/'caucasus-model-event.png'))
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-caucasus-model-cases.png'),full_page=True)
            page.fill('#eddy-search','Batumi');page.locator('#eddy-rows summary').click()
            assert 'open return-flow structure rather than a closed anticyclone' in page.locator('#eddy-rows').inner_text()
            checks.append('Black Sea: six approximate model penetration depths and native m/s ranges; source day-40 depth date does not date velocities; separate 6/3/17-day Caucasus model events and open Batumi qualification; mobile layout')
            with page.expect_download() as pending:page.get_by_role('link',name='Download measurement CSV').click()
            assert hashlib.sha256(Path(pending.value.path()).read_bytes()).hexdigest()==sha('research/eddy-measurement-register-v1.csv')
            for path in set(r['source_file'] for r in document['evidence'])|{'plans/eddy-measurement-register-v1.md','research/eddy-measurement-register-v1.json'}:
                response=context.request.get(base+'/'+path);assert response.status==200 and hashlib.sha256(response.body()).hexdigest()==sha(path),path
                assets.add(path)
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Latakia');page.locator('#eddy-rows summary').click()
            for needle in ['50 km','100 km','spring 2010 cyclonic','summer 2010 anticyclonic','2010-05-13','2010-08-04','not a seasonal envelope','HTTP 403']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="latakia-menna-2012-spring-diameter"]').screenshot(path=str(OUT/'latakia-spring-diameter.png'))
            page.locator('[data-evidence-id="latakia-menna-2012-summer-diameter"]').screenshot(path=str(OUT/'latakia-summer-diameter.png'))
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-latakia-cases.png'),full_page=True)
            checks.append('Latakia opposite-rotation regional cases retain separate diameters, map support, qualified source access and no pooled seasonal envelope')
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Jumbo')
            jumbo=page.locator('tr[data-eddy-id="eddy:horizon:loop-59-primary"]');jumbo.locator('summary').click()
            for needle in ['400 km','247 km','Post-separation intact case','August 2012','No value assigned to Jumbo Jr.','not independently verified']:
                assert needle in jumbo.inner_text(),needle
            page.locator('[data-evidence-id="jumbo-post-separation-hamilton-2018-diameter"]').screenshot(path=str(OUT/'jumbo-post-separation-diameter.png'))
            child=page.locator('tr[data-eddy-id="eddy:horizon:loop-59-secondary"]');assert 'Size reference needed' in child.inner_text()
            page.fill('#eddy-search','Icarus');page.locator('#eddy-rows summary').click()
            for needle in ['175 km','diameter sampling date unspecified','Qualified indexed reference','not independently verified']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="icarus-lemus-2024-diameter"]').screenshot(path=str(OUT/'icarus-source-diameter.png'))
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-icarus-diameter.png'),full_page=True)
            checks.append('Jumbo distinct narrative phase diameters without child inheritance or pooled range; Icarus qualified contextual size without invented sampling dates; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Apublished%3Akraken-2013')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            target=page.locator('tr[data-eddy-id="eddy:published:kraken-2013"]')
            assert target.locator('details').evaluate('(e)=>e.open')
            assert 'identity unverified' in target.inner_text()
            assert '200 days' in target.inner_text()
            assert not errors,errors
            assert not any('.wasm' in u or 'query-packet' in u or '/release/' in u for u in requests)
            checks.append('CSV/source bytes, deep link, unverified identity crosswalk, no JS errors or runtime packet load')
            result={'status':'PASS','source_commit':os.environ['GITHUB_SHA'],'counts':document['counts'],'checks':checks,'source_assets_checked':len(assets),'input_sha256':preflight['input_sha256'],'browser_scope':'Lightweight register only; card href identities verified, destinations not executed.','runtime_loaded':False,'full_goal_complete':False}
            (OUT/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
            print(json.dumps(result));browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':run()
