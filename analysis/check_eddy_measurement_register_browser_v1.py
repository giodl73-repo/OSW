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
            for value,expected in [('measured',counts['identities_with_measurements']),('gap',counts['identities_without_measurements']),('linked',counts['linked_primary_context_entries']),('unlinked-gap',1),('size-gap',sum(r['size_gap'] for r in document['records'])),('duration-gap',sum(r['duration_gap'] for r in document['records'])),('all',136)]:
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
                assert tr.locator('.eddy-record').count()==(3 if name=='ursa-2021' else 2)
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
            assert primary.locator('.eddy-record').count()==3
            for name in ['Feldman','Edison']:
                page.fill('#eddy-search',name);page.locator('#eddy-rows summary').click()
                assert page.locator('#eddy-rows .eddy-record').count()==(0 if name=='Feldman' else 3)
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
            page.set_viewport_size({'width':1440,'height':1000})
            page.fill('#eddy-search','Sukhumi');page.locator('#eddy-rows summary').click()
            for needle in ['100 km','300 m','30–35 cm/s','15–20 cm/s','Published model case','absent from experiment 1','not dated observations']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="sukhumi-dymova-2019-diameter"]').screenshot(path=str(OUT/'sukhumi-model-diameter.png'))
            page.fill('#eddy-search','Kerch');page.locator('#eddy-rows summary').click()
            for needle in ['60 km','400 m','15–20 cm/s','regional-origin case candidate','Cape Sarych','not a size snapshot at Kerch']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.locator('[data-evidence-id="kerch-dymova-2019-diameter"]').screenshot(path=str(OUT/'kerch-origin-model-diameter.png'))
            page.set_viewport_size({'width':390,'height':844})
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-kerch-origin-case.png'),full_page=True)
            checks.append('Sukhumi and Kerch-origin model sizes, vertical reach and distinct velocity phases; bathymetry configuration dependence, source access and migrated size location retained; no dated observation or state containment inferred')
            page.set_viewport_size({'width':1440,'height':1000});page.fill('#eddy-search','')
            page.select_option('#eddy-filter','size-class');assert page.locator('#eddy-rows tr').count()==15
            assert '9 of these still need numeric sizes' in page.locator('#eddy-class-summary').inner_text()
            page.screenshot(path=str(OUT/'source-size-class-filter.png'))
            page.fill('#eddy-search','QE-2')
            qe=page.locator('tr[data-eddy-id="eddy:horizon:loop-40-secondary"]');qe.locator('summary').click()
            for needle in ['Small · source size class','Size reference needed','no numeric class thresholds','no values inherited','Source row: QE-2, 2002','Associated primary registry row: Quick','This supplies no secondary separation date']:
                assert needle in qe.inner_text(),needle
            assert 'Huge · source size class' not in qe.inner_text()
            assert 'Registry context: QE-2, separation' not in qe.inner_text()
            page.locator('[data-classification-id="whoi-2005-03-table2-row-04"]').screenshot(path=str(OUT/'qe2-own-source-class.png'))
            page.select_option('#eddy-filter','measured');assert page.locator('#eddy-rows tr').count()==0
            page.select_option('#eddy-filter','gap');assert page.locator('#eddy-rows tr').count()==1
            page.select_option('#eddy-filter','all');page.fill('#eddy-search','Gyre');page.locator('#eddy-rows summary').click()
            for needle in ['Source row: Gyre, 1999','separation 1998-05-11','not assumed to be separation year']:
                assert needle in page.locator('#eddy-rows').inner_text(),needle
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-gyre-source-class.png'),full_page=True)
            with page.expect_download() as pending:page.get_by_role('link',name='Download size classifications CSV').click()
            assert hashlib.sha256(Path(pending.value.path()).read_bytes()).hexdigest()==sha('research/eddy-size-classifications-v1.csv')
            checks.append('15 qualitative classes with no numeric thresholds; QE-2 own Small label does not inherit Quick Huge or close numeric gaps; Gyre source year and registry context kept distinct; separate classification CSV and mobile layout')
            page.set_viewport_size({'width':1440,'height':1000});page.fill('#eddy-search','Kenai')
            region=page.locator('tr[data-eddy-id="eddy:geography:kenai-eddy-region"]');region.locator('summary').click()
            for needle in ['15,000 km²','10,000 km²','6,000 km²','1.8 km/day','-0.8–5 km/day','1,278–1,338 days','negative eastward','includes post-split main branch','not an exact period mean']:
                assert needle in region.inner_text(),needle
            page.locator('[data-evidence-id="kenai-ueno-2012-early-area"]').screenshot(path=str(OUT/'kenai-source-area-level.png'))
            page.locator('[data-evidence-id="kenai-ueno-2012-signed-westward-component-range"]').screenshot(path=str(OUT/'kenai-signed-westward-component.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-kenai-track-reference.png'),full_page=True)
            checks.append('Kenai source-case Okubo-Weiss area levels retain phases and split continuation; signed westward component keeps negative eastward endpoint; month-supported main-track span remains distinct from physical lifespan; mobile layout')
            page.set_viewport_size({'width':1440,'height':1000});page.fill('#eddy-search','Sverdrup')
            primary=page.locator('tr[data-eddy-id="eddy:horizon:loop-68-primary"]');primary.locator('summary').click()
            for needle in ['300–475 km · map estimate','400–550 km · map estimate','one published snapshot, not eddy diameter','6 pixels at each extent','rounded outward to 25 km','2019-07-06']:
                assert needle in primary.inner_text(),needle
            page.locator('[data-evidence-id="sverdrup-trott-2024-map-north-south-span"]').screenshot(path=str(OUT/'sverdrup-map-span.png'))
            child=page.locator('tr[data-eddy-id="eddy:horizon:loop-68-secondary"]');assert 'Size reference needed' in child.inner_text()
            page.fill('#eddy-search','Thor');primary=page.locator('tr[data-eddy-id="eddy:horizon:loop-69-primary"]');primary.locator('summary').click()
            assert '325–500 km · map estimate' in primary.inner_text()
            published=page.locator('tr[data-eddy-id="eddy:published:thor-2020"]');published.locator('summary').click()
            assert 'Size reference needed' not in published.inner_text() and '550 km' in published.inner_text()
            assert published.locator('[data-evidence-id="thor-thoppil-2025-parent-analysis-zonal-extent"]').count()==1
            assert published.locator('[data-evidence-id^="thor-trott-2024-"]').count()==0
            published.locator('summary').click()
            page.locator('[data-evidence-id="thor-trott-2024-map-east-west-span"]').screenshot(path=str(OUT/'thor-map-span.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-thor-map-span.png'),full_page=True)
            checks.append('Source-pixel map span estimates labeled separately from diameter and source ranges; day snapshots, 6-pixel reading allowance and 25-km outward rounding visible; no secondary or possible published-match inheritance; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ageography%3Acaucasus-eddy-region')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            region=page.locator('tr[data-eddy-id="eddy:geography:caucasus-eddy-region"]')
            assert region.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['30 km','12 days','2.3 km/day','Caucasian AE A11','Published model case','not outer radius or diameter','HTTP 429','no verified calendar date']:
                assert needle in region.inner_text(),needle
            assert 'Size reference needed' not in region.inner_text()
            page.locator('[data-evidence-id="caucasus-korotenko-2022-core-radius"]').screenshot(path=str(OUT/'caucasian-model-core-radius.png'))
            page.locator('[data-evidence-id="caucasus-korotenko-2022-core-rotation-period"]').screenshot(path=str(OUT/'caucasian-model-rotation-period.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-caucasian-model-case.png'),full_page=True)
            checks.append('Named Caucasian model case retains inner-core radius, distinct rotation period and translation speed; model support and qualified source access visible; no diameter, physical lifetime or seasonal range inferred')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ageography%3Acrimea-eddy-region')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            region=page.locator('tr[data-eddy-id="eddy:geography:crimea-eddy-region"]');assert region.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['100 km','1997-10-30','source hypothesis','none of CACE-1','HTTP 403','no fixed contour threshold']:
                assert needle in region.inner_text(),needle
            assert 'Size reference needed' not in region.inner_text()
            page.locator('[data-evidence-id="crimea-ginzburg-2001-1997-10-30-diameter"]').screenshot(path=str(OUT/'crimean-dated-diameter.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-crimean-dated-case.png'),full_page=True)
            checks.append('Crimean named image-case diameter retains one source date, qualified original-PDF text access and unverified merger hypothesis; no neighboring measurements inherited or seasonal range inferred')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Apublished%3Aursa-2021')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:published:ursa-2021"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['300–375 km · map estimate','250–325 km · map estimate','68 axis scenarios','physical ring attribution remains pending','0.65 cm','unresolved unit','2021-03-07','Not eddy diameter','49 days']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            page.locator('[data-evidence-id="ursa-exley-2022-map-east-west-span"]').screenshot(path=str(OUT/'ursa-candidate-east-west-span.png'))
            page.locator('[data-evidence-id="ursa-exley-2022-map-north-south-span"]').screenshot(path=str(OUT/'ursa-candidate-north-south-span.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-ursa-candidate-spans.png'),full_page=True)
            checks.append('Ursa dated editorial contour spans with accepted stroke/threshold and axis sensitivity, literal unresolved SSH unit and pending physical attribution; paper-stage interval stays separate; no registry inheritance or physical boundary admission')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ageography%3Alilian-2006')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:geography:lilian-2006"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['100–225 km · map estimate','75–150 km · map estimate','source legend unit unspecified','plot levels 9, 10, 11','OSW diagnostic choice','2006-07-05','not the authors’ ring-edge definition','3.5 years']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            page.locator('[data-evidence-id="lilian-guerra-2018-colour-level-10-east-west-span"]').screenshot(path=str(OUT/'lilian-colour-patch-east-west-span.png'))
            page.locator('[data-evidence-id="lilian-guerra-2018-colour-level-10-north-south-span"]').screenshot(path=str(OUT/'lilian-colour-patch-north-south-span.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-lilian-colour-patch-spans.png'),full_page=True)
            checks.append('Lilian source colour-level patch spans with explicit OSW diagnostic choice, unknown legend unit and selection/reading sensitivity; no whole-ring dimensions or population-radius inheritance; existing lifetime and depth references retained')
            for name,owner,needles in [('Lazarus','eddy:horizon:loop-61-primary',['125–200 km · map estimate','175–225 km · map estimate']),('Michael','eddy:horizon:loop-62-primary',['375–425 km · map estimate','300–350 km · map estimate'])]:
                page.goto(base+'/almanac/eddies.html?id='+owner)
                page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
                row=page.locator('tr[data-eddy-id="'+owner+'"]');assert row.locator('details').evaluate('(e)=>e.open')
                page.set_viewport_size({'width':1440,'height':1000})
                for needle in needles+['2015-01-22','Visible circulation-arrow extents','Closed-outline extraction rejected','CONFIDENTIAL','excluded from rights-screened release','not an extracted closed contour']:
                    assert needle in row.inner_text(),needle
                assert 'Size reference needed' not in row.inner_text()
                page.locator('[data-evidence-id="'+name.lower()+'-aade-2015-arrow-east-west-span"]').screenshot(path=str(OUT/(name.lower()+'-source-arrow-span.png')))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'mobile-michael-arrow-spans.png'),full_page=True)
            checks.append('Lazarus and Michael visible circulation-arrow spans retain date, manual source readings, rejected closed-outline extraction and explicit confidential/copyright source status; no contour, footprint or release-rights promotion')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-61-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-61-primary"]')
            assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['30 m','20–30 kJ/cm²','> 100 kJ/cm²','Depth averaging: 0–1000 m; averaging axis: depth.','26°C isotherm','context only, not exact sample dates','not whole-eddy depth','full methods not independently reviewed']:
                assert needle in row.inner_text(),needle
            page.locator('[data-evidence-id="lazarus-perry-2015-later-depth-average-speed"]').screenshot(path=str(OUT/'lazarus-glider-depth-average.png'))
            page.locator('[data-evidence-id="lazarus-perry-2015-transition-column-ohc"]').screenshot(path=str(OUT/'lazarus-glider-column-heat.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="lazarus-perry-2015-later-column-ohc"]').screenshot(path=str(OUT/'mobile-lazarus-glider-heat.png'))
            checks.append('Lazarus glider diagnostics retain thermal-column depth, energy-per-area units, strict heat-content bound and depth averaging; later circuit remains context only, no whole-eddy depth or seasonal extrema inferred; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ageography%3Aagulhas-eddy-w-2000')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:geography:agulhas-eddy-w-2000"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['150–225 km · coordinate estimate','190.056 km','Station 06 (sampled center): -29.2°, 8.2°','Station 05 (sampled edge): -28.8°, 6.3°','not whole-eddy radius or diameter','Source accuracy and simultaneity unverified','60 m','2000-02-22','threshold unspecified','Original publisher PDF']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            page.locator('[data-evidence-id="agulhas-w-loncaric-2006-center-edge-station-separation"]').screenshot(path=str(OUT/'eddy-w-station-separation.png'))
            page.locator('[data-evidence-id="agulhas-w-loncaric-2006-center-mixed-layer-depth"]').screenshot(path=str(OUT/'eddy-w-mixed-layer.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="agulhas-w-loncaric-2006-center-edge-station-separation"]').screenshot(path=str(OUT/'mobile-eddy-w-station-separation.png'))
            checks.append('Eddy W sampled station separation retains original center/edge coordinates, assumed coordinate sensitivity and unverified simultaneity; distinct dated mixed-layer depth with unspecified threshold; no full radius, diameter or whole-eddy depth inference; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-77-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-77-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['350–400 km · map estimate','300–350 km · map estimate','Native PDF line span','contour observation date unspecified','1.5-knot frontal-analysis contour','2023-12-21; this does not date the frontal line','3,500 continuous line segments','no reconstructed gaps','6 PDF points','Not whole-eddy radius or diameter']:
                assert needle in row.inner_text(),needle
            assert 'undefined' not in row.inner_text() and 'NaN' not in row.inner_text()
            assert 'Size reference needed' not in row.inner_text()
            child=page.locator('tr[data-eddy-id="eddy:horizon:loop-77-secondary"]');assert 'Size reference needed' in child.inner_text()
            page.locator('[data-evidence-id="berek-bower-2024-native-frontal-east-west-span"]').screenshot(path=str(OUT/'berek-native-frontal-east-west.png'))
            page.locator('[data-evidence-id="berek-bower-2024-native-frontal-north-south-span"]').screenshot(path=str(OUT/'berek-native-frontal-north-south.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="berek-bower-2024-native-frontal-east-west-span"]').screenshot(path=str(OUT/'mobile-berek-native-frontal.png'))
            checks.append('Berek source-native frontal line spans retain exact source path, source threshold, unknown contour observation date separate from dated SSH background and no reconstructed gaps; no secondary inheritance or physical footprint inference; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-03-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-03-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['280 km','4.6 km/day','130 km','40 km','≥ 180 km','≥ 200 km','Published alias: Fast Eddy / Eddy B','early July 1985','1985-05-31','conventions remain unreconciled','does not indicate eddy size','not an outer radius','Different methods and dates do not define growth']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            page.locator('[data-evidence-id="fast-saic-1988-october-deeper-isotherm-radius-lower-bound"]').screenshot(path=str(OUT/'fast-hydrographic-radius-bound.png'))
            page.locator('[data-evidence-id="fast-saic-1988-october-drifter-orbit-radius"]').screenshot(path=str(OUT/'fast-sampled-drifter-radius.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="fast-saic-1988-november-drifter-flow-radius-lower-bound"]').screenshot(path=str(OUT/'mobile-fast-flow-radius-bound.png'))
            checks.append('Fast / Eddy B alias retains unverified registry identity and different separation conventions; orbit radius/diameter stay distinct from hydrographic and flow-radius inclusive bounds, center translation differs from orbit speed; mobile layout')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-31-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-31-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['200 m','Airborne temperature diagnostic','20°C isotherm','1999-08-03','finite sampling','HTTP 403','full methods not independently reviewed']:
                assert needle in row.inner_text(),needle
            assert 'Glider profile diagnostic' not in row.inner_text() and 'Size reference needed' in row.inner_text()
            page.locator('[data-evidence-id="haskell-noaa-1999-20c-isotherm-maximum-depth"]').screenshot(path=str(OUT/'haskell-airborne-isotherm-depth.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            checks.append('Haskell NOAA airborne mission retains sampled maximum depth of the 20°C isotherm, flight date and qualified original-figure access; no other feature values or whole-eddy depth inferred; size gap remains')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-10-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-10-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['175–225 km · graph estimate','0.6–0.7 m · graph estimate','OSW-chosen 0.30 m','sensitivity 0.25 and 0.35 m','Meridional projection, not diameter','not eddy depth','384 sensitivity cases','8 sensitivity cases','AXBT comparison was several days apart']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text() and 'undefined km' not in row.inner_text()
            for component in ['meridional-span','peak-height']:
                page.locator('[data-evidence-id="murphy-calman-1989-'+component+'"]').screenshot(path=str(OUT/('murphy-profile-'+component+'.png')))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="murphy-calman-1989-meridional-span"]').screenshot(path=str(OUT/'mobile-murphy-profile-span.png'))
            checks.append('Murphy selected satellite height-profile crossings and peak retain date, diagnostic threshold sensitivity and original pixel verification; meridional projection is not diameter or oblique track length, dynamic height is not eddy depth; mobile layout')
            for owner,name,needles,record in [('eddy:horizon:loop-08-primary','kathleen',['75 cm/s','source direction: southward','post-coalescence context'],'post-coalescence-spring-1988-100m-site-speed'),('eddy:horizon:loop-10-primary','murphy',['80–90 cm/s','30–40 cm/s','10–20 cm/s','70–80 cm/s','instrument depth: 725 m','source direction: northeastward','source direction: eastward'],'september-1988-725m-site-speed')]:
                page.goto(base+'/almanac/eddies.html?id='+owner)
                page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
                row=page.locator('tr[data-eddy-id="'+owner+'"]');assert row.locator('details').evaluate('(e)=>e.open')
                page.set_viewport_size({'width':1440,'height':1000})
                for needle in needles+['Fixed-mooring current diagnostic','SAIC GG','mean versus maximum is unspecified','not whole-eddy depth','raw time series unavailable']:
                    assert needle in row.inner_text(),needle
                assert 'Glider profile diagnostic' not in row.inner_text()
                if name=='kathleen':assert 'Size reference needed' not in row.inner_text()
                page.locator('[data-evidence-id="'+name+'-nowlin-2001-'+record+'"]').screenshot(path=str(OUT/(name+'-mooring-current.png')))
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.locator('[data-evidence-id="'+name+'-nowlin-2001-'+record+'"]').screenshot(path=str(OUT/('mobile-'+name+'-mooring-current.png')))
            checks.append('Kathleen and Murphy fixed-mooring speeds preserve instrument depths, native units, source directions, coalescence context and imprecise time support; no whole-eddy maximum/thickness, simultaneous depth section or seasonal envelope; desktop and mobile')
            for owner,name,needles,record in [('eddy:horizon:loop-08-primary','kathleen',['50–170 km','Sampled drifter-axis change','not a seasonal size range','Published alias: Kathleen / Eddy E','does not assign each endpoint separately'],'sampled-axes-length-extrema'),('eddy:horizon:loop-10-primary','murphy',['244 km','148 km','180 km','300 km','Sampled ellipse dimension','Baroclinic radius of influence','boundary and observation date unspecified','Published alias: Murphy / Eddy F'],'baroclinic-radius-of-influence')]:
                page.goto(base+'/almanac/eddies.html?id='+owner)
                page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
                row=page.locator('tr[data-eddy-id="'+owner+'"]');assert row.locator('details').evaluate('(e)=>e.open')
                page.set_viewport_size({'width':1440,'height':1000})
                for needle in needles+['Separation conventions remain unreconciled','not digitized graph values']:
                    assert needle in row.inner_text(),needle
                assert 'Size reference needed' not in row.inner_text()
                page.locator('[data-evidence-id="'+name+'-saic-1989-'+record+'"]').screenshot(path=str(OUT/(name+'-year5-size.png')))
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.locator('[data-evidence-id="'+name+'-saic-1989-'+record+'"]').screenshot(path=str(OUT/('mobile-'+name+'-year5-size.png')))
            checks.append('Kathleen sampled-axis extrema and Murphy ellipse dimensions, baroclinic influence radius and definition-unspecified diameter preserve source operators, E/F alias references and unreconciled separation conventions; no seasonal envelope, radius conversion or front inference; desktop/mobile')
            for owner,name,needles,record in [('eddy:horizon:loop-71-primary','verne',['125–225 km','100–200 km','Chart-scale equivalent','not a calibrated geodesic distance','Geographic scale variation at the eddy remains unquantified','2021-11-23','3.5 knots'],'verne-cls-2021-scale-bar-horizontal-span'),('eddy:horizon:loop-72-primary','wilde',['4.25 knots','western front of Wilde','October 2021'],'wilde-cls-2021-local-maximum-current')]:
                page.goto(base+'/almanac/eddies.html?id='+owner)
                page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
                row=page.locator('tr[data-eddy-id="'+owner+'"]');assert row.locator('details').evaluate('(e)=>e.open')
                page.set_viewport_size({'width':1440,'height':1000})
                for needle in needles+['Operational ADCP current diagnostic','Provider-reported local maximum','Sample depth, exact dates and averaging interval unspecified']:
                    assert needle in row.inner_text(),needle
                assert 'undefined km' not in row.inner_text() and 'Glider profile diagnostic' not in row.inner_text()
                assert ('Size reference needed' in row.inner_text())==(name=='wilde')
                page.locator('[data-evidence-id="'+record+'"]').screenshot(path=str(OUT/(name+'-cls-reference.png')))
                if name=='verne':page.locator('[data-evidence-id="verne-cls-2021-local-maximum-current"]').screenshot(path=str(OUT/'verne-cls-local-maximum.png'))
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.locator('[data-evidence-id="'+record+'"]').screenshot(path=str(OUT/('mobile-'+name+'-cls-reference.png')))
            checks.append('Verne source-chart scale-bar equivalents retain unknown projection and contour definition, date and unquantified geographic scale error; Verne/Wilde local operational ADCP maxima retain native knots and unspecified sample depths; Wilde size gap remains; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-66-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-66-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['225–275 km','Visible model-inferred front','eastern side clipped','512 sensitivity cases','no pre-split parent or Quantum II values inferred','Multi-instrument current comparison','0.8 m/s','1.1 m/s','0.6 m/s','1.2 m/s','sample depth: 5 m','no single assigned depth','not an arithmetic average','about an hour']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text() and 'Glider profile diagnostic' not in row.inner_text()
            for record,name in [('quantum-rodriguez-2020-visible-model-front-meridional-span','quantum-visible-model-front'),('quantum-rodriguez-2020-2018-03-26-5m-adcp','quantum-adcp-5m'),('quantum-rodriguez-2020-2018-03-25-remote-shared-speed','quantum-remote-shared-speed')]:
                page.locator('[data-evidence-id="'+record+'"]').screenshot(path=str(OUT/(name+'.png')))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for record,name in [('quantum-rodriguez-2020-visible-model-front-meridional-span','mobile-quantum-visible-model-front'),('quantum-rodriguez-2020-2018-03-25-remote-shared-speed','mobile-quantum-remote-shared-speed')]:
                page.locator('[data-evidence-id="'+record+'"]').screenshot(path=str(OUT/(name+'.png')))
            checks.append('Quantum northern post-split component retains visible model-front meridional extent, eastern clipping and no reconstructed geometry; ADCP 5 m and shared ROCIS/DopplerScatt comparison values retain dates and instrument-dependent support, no arithmetic averaging or simultaneous shear; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-60-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-60-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['60,000–70,000 km²','275–300 km','300–325 km','325–375 km','gridded contour estimate','method sensitivity only','Nine primary-map interior probes','First March detachment','2013-04-08','Registry physical crosswalk unverified','not a minimum width']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            for part in ['area','equivalent-diameter','east-west','north-south']:
                card=page.locator('[data-evidence-id="kraken-2013-03-31-gridded-'+part+'"]')
                assert 'Model calculation:' not in card.inner_text()
            for part in ['area','equivalent-diameter','north-south']:
                page.locator('[data-evidence-id="kraken-2013-03-31-gridded-'+part+'"]').screenshot(path=str(OUT/('kraken-gridded-'+part+'.png')))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for part in ['area','north-south']:
                page.locator('[data-evidence-id="kraken-2013-03-31-gridded-'+part+'"]').screenshot(path=str(OUT/('mobile-kraken-gridded-'+part+'.png')))
            checks.append('Kraken source-case comparison retains original daily gridded area, equivalent diameter and bounding spans as six-scenario method sensitivity, registry/date conflict, later reattachments and no inherited physical identity; desktop/mobile')
            for number,name,values in [(56,'galileo',['100–300 km','100–325 km','2011-06-21']),(57,'hadal',['400–625 km','2011-08-01','caption says shed by 30 July','Hadal II inherits no values'])]:
                page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-'+str(number)+'-primary')
                page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
                row=page.locator('tr[data-eddy-id="eddy:horizon:loop-'+str(number)+'-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
                page.set_viewport_size({'width':1440,'height':1000})
                for needle in values+['operational chart estimate','low-resolution chart','303 × 240 pixels','128 sensitivity cases','no missing ink or closed boundary reconstructed','separate gridded comparison did not qualify']:
                    assert needle in row.inner_text(),needle
                assert 'Size reference needed' not in row.inner_text()
                page.locator('[data-evidence-id="'+name+'-brickley-2012-operational-chart-east-west-span"]').screenshot(path=str(OUT/(name+'-operational-chart-east-west.png')))
                if number==57:page.locator('[data-evidence-id="hadal-brickley-2012-operational-chart-north-south-span"]').screenshot(path=str(OUT/'hadal-operational-chart-north-south.png'))
                page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.locator('[data-evidence-id="'+name+'-brickley-2012-operational-chart-east-west-span"]').screenshot(path=str(OUT/('mobile-'+name+'-operational-chart-east-west.png')))
            checks.append('Galileo and Hadal retain low-resolution operational chart line spans, native map dates and Hadal caption/date discrepancy, pixel/axis sensitivity and no gridded or secondary inheritance; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-80-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-80-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            page.set_viewport_size({'width':1440,'height':1000})
            for needle in ['6 days','1 day','No-Hurricane','No-Helene','No-Milton','Preprint model event-date contrast','not eddy lifetime','Different simulated worlds','not additive','not peer-reviewed','Size reference needed','2024-10-16','2024-10-11']:
                assert needle in row.inner_text(),needle
            for part in ['both-hurricanes-removed','helene-removed','milton-removed']:
                card=page.locator('[data-evidence-id="edison-deng-2026-model-detachment-contrast-'+part+'"]')
                assert 'Published model case' not in card.inner_text()
                card.screenshot(path=str(OUT/('edison-model-'+part+'.png')))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for part in ['both-hurricanes-removed','milton-removed']:
                page.locator('[data-evidence-id="edison-deng-2026-model-detachment-contrast-'+part+'"]').screenshot(path=str(OUT/('mobile-edison-model-'+part+'.png')))
            checks.append('Edison preprint model date contrasts retain three forcing experiments, different simulated worlds, non-additivity, no observed lifespan or physical effect, and an open size gap; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-03-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-03-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            thermal=page.locator('[data-evidence-id^="fast-saic-1988-thermal-area-"]');assert thermal.count()==17
            for needle in ['Thermal-level enclosed area','not sampling depth or eddy thickness','not the full outer boundary','Zero and unclosed','8°C temperature surface','1985-10','1986-04','registry physical crosswalk unverified']:
                assert needle in row.inner_text(),needle
            page.set_viewport_size({'width':1440,'height':1000})
            for month,depth,value in [('1985-10',550,'97000'),('1986-01',650,'17000'),('1986-04',600,'24000')]:
                card=page.locator(f'[data-evidence-id="fast-saic-1988-thermal-area-{month}-{depth}m"]')
                assert value in card.inner_text().replace(',','').replace(' ','')
                card.screenshot(path=str(OUT/f'fast-thermal-area-{month}-{depth}m.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for month,depth in [('1985-10',550),('1986-04',600)]:
                page.locator(f'[data-evidence-id="fast-saic-1988-thermal-area-{month}-{depth}m"]').screenshot(path=str(OUT/f'mobile-fast-thermal-area-{month}-{depth}m.png'))
            checks.append('Fast thermal-level areas: 17 positive source cells, distinct survey and contour levels, unit conversion, no filled zero or unclosed cells, no outer boundary or thickness inference; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-74-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-74-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            for needle in ['150 km','2.5 knots','Approximate high-ADT-patch radius','not diameter','7–17 November 2022','not a daily footprint','No Yazoo II values inherited','1–5 October 2022','physical crosswalk unverified']:
                assert needle in row.inner_text(),needle
            assert row.locator('[data-evidence-id^="yazoo-2022-"]').count()==2
            assert 'Size reference needed' not in row.inner_text()
            page.set_viewport_size({'width':1440,'height':1000})
            for part in ['radius','current']:page.locator(f'[data-evidence-id="yazoo-2022-{part}-primary-reference"]').screenshot(path=str(OUT/f'yazoo-{part}.png'))
            row.locator('summary').screenshot(path=str(OUT/'yazoo-summary.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for part in ['radius','current']:page.locator(f'[data-evidence-id="yazoo-2022-{part}-primary-reference"]').screenshot(path=str(OUT/f'mobile-yazoo-{part}.png'))
            checks.append('Yazoo explicit named primary radius and separately dated local cruise current: temporal-average limits, no diameter or Yazoo II inheritance, primary size gap closed; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-75-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-75-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            for needle in ['350–400 km','450–525 km','325–375 km','250–325 km','Source 17 cm SSH isoline span','not principal width or diameter','not an SST warm-patch size','128 scenarios','year typo','physical crosswalk unverified']:
                assert needle in row.inner_text(),needle
            assert row.locator('[data-evidence-id^="zodiac-lsu-"]').count()==4
            assert 'Size reference needed' not in row.inner_text()
            page.set_viewport_size({'width':1440,'height':1000})
            for date in ['2022-12-29','2023-01-13']:
                for component in ['east_west','north_south']:
                    page.locator(f'[data-evidence-id="zodiac-lsu-{date}-{component}-isoline-span"]').screenshot(path=str(OUT/f'zodiac-{date}-{component}.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="zodiac-lsu-2023-01-13-north_south-isoline-span"]').screenshot(path=str(OUT/'mobile-zodiac-2023-01-13-north_south.png'))
            checks.append('Zodiac original dated 17 cm SSH chart isolines: four bounding spans, reading/axis sensitivity, original map year over prose typo, no SST patch, principal width, physical footprint or seasonal envelope; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Apublished%3Athor-2020')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:published:thor-2020"]');assert row.locator('details').evaluate('(e)=>e.open')
            for needle in ['550 km','56 days','Assimilative model-analysis extent','not directly observed length','24 February 2020','32 members','not a forecast-member result','No values transferred to the March anticyclones or registry Thor']:
                assert needle in row.inner_text(),needle
            assert row.locator('.eddy-record').count()==2 and 'Size reference needed' not in row.inner_text()
            page.set_viewport_size({'width':1440,'height':1000})
            page.locator('[data-evidence-id="thor-thoppil-2025-parent-analysis-zonal-extent"]').screenshot(path=str(OUT/'thor-parent-analysis-extent.png'))
            page.locator('[data-evidence-id="thor-2020-event-stage-interval"]').screenshot(path=str(OUT/'thor-existing-event-interval.png'))
            row.locator('summary').screenshot(path=str(OUT/'thor-published-two-record-summary.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.locator('[data-evidence-id="thor-thoppil-2025-parent-analysis-zonal-extent"]').screenshot(path=str(OUT/'mobile-thor-parent-analysis-extent.png'))
            page.locator('[data-evidence-id="thor-2020-event-stage-interval"]').screenshot(path=str(OUT/'mobile-thor-existing-event-interval.png'))
            checks.append('Published Thor pre-near-split parent extent: source scalar, assimilative verifying analysis, not direct observation/forecast member/diameter, no child or registry inheritance; prior event interval preserved; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-34-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-34-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            for needle in ['50 cm/s','30 cm/s','755 m','Near-surface reached value','exact depth unspecified','First two weeks of November 2000','not the exact current sample time','cross-report event association','remain unverified','not isolated eddy swirl','Size reference needed']:
                assert needle in row.inner_text(),needle
            assert row.locator('[data-evidence-id^="kinetic-mckone-2007-"]').count()==2
            page.set_viewport_size({'width':1440,'height':1000})
            for part in ['near-surface','755m']:page.locator(f'[data-evidence-id="kinetic-mckone-2007-november-{part}-current"]').screenshot(path=str(OUT/f'kinetic-{part}-interaction-current.png'))
            row.locator('summary').screenshot(path=str(OUT/'kinetic-current-reference-summary.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for part in ['near-surface','755m']:page.locator(f'[data-evidence-id="kinetic-mckone-2007-november-{part}-current"]').screenshot(path=str(OUT/f'mobile-kinetic-{part}-interaction-current.png'))
            checks.append('Kinetic qualified interaction-site currents: near-surface reached value and 755 m local maximum, phase rather than invented sample dates, no simultaneous profile/shear/thickness, cross-report association unverified, size gap retained; desktop/mobile')
            page.goto(base+'/almanac/eddies.html?id=eddy%3Ahorizon%3Aloop-14-primary')
            page.wait_for_function('window.oswEddyMeasurementRegister?.records.length===136')
            row=page.locator('tr[data-eddy-id="eddy:horizon:loop-14-primary"]');assert row.locator('details').evaluate('(e)=>e.open')
            for needle in ['400 km','250–300 km','Nearly 400 km','north-oriented major axis','east–west minor axis','12 and 19 August 1990','No separate axis pair','not a strict upper bound','No ellipse area','physical crosswalk unverified']:
                assert needle in row.inner_text(),needle
            assert 'Size reference needed' not in row.inner_text()
            assert row.locator('[data-evidence-id^="quiet-hawkins-1991-"]').count()==2
            page.set_viewport_size({'width':1440,'height':1000})
            for axis in ['major','minor']:page.locator(f'[data-evidence-id="quiet-hawkins-1991-sst-{axis}-axis"]').screenshot(path=str(OUT/f'quiet-sst-{axis}-axis.png'))
            row.locator('summary').screenshot(path=str(OUT/'quiet-sst-reference-summary.png'))
            page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            for axis in ['major','minor']:page.locator(f'[data-evidence-id="quiet-hawkins-1991-sst-{axis}-axis"]').screenshot(path=str(OUT/f'mobile-quiet-sst-{axis}-axis.png'))
            checks.append('Quiet source-reported SST axes: nearly 400 km major and about 250–300 km minor; paired image-date support without daily values or seasonal bounds, no strict upper bound, fitted ellipse/area or geometry; named size gap closed; desktop/mobile')
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
            generated={p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(OUT.glob('*.png'))}
            selected=request.get('review_screenshot_names')
            if selected is not None:
                assert isinstance(selected,list) and selected and len(selected)==len(set(selected))
                assert set(selected)<=set(generated) and all(Path(name).name==name for name in selected)
                result['screenshots_generated']=generated
                result['screenshots_retained']=sorted(selected)
                result['screenshot_retention']='All regression assertions and screenshot captures executed; retain selected current-batch PNGs plus the complete generated-image hash/byte inventory.'
                for p in OUT.glob('*.png'):
                    if p.name not in selected:p.unlink()
            (OUT/'result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
            print(json.dumps(result));browser.close()
    finally:server.shutdown();server.server_close()


if __name__=='__main__':run()
