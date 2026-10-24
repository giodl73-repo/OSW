"""Cloud delivery gate: actual native/WASM Baffin evidence, mobile and queries."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote

from playwright.sync_api import expect, sync_playwright

import baffin_bound_admission as a
import baffin_bound_owner_projection as owner

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('OSW_RESEARCH_EVIDENCE_BASE','http://127.0.0.1:8788')


def main():
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise RuntimeError('Run Baffin delivery checks in the cloud; local browsers remain held')
    cli = ROOT / 'rust/osw-query/target/debug/osw-query-cli'
    document = json.loads(a.read(a.FILE))
    assert a.encoded(document) == a.encoded(a.build_contract())
    result = subprocess.run([str(cli),'almanac/query-data.json','--object-view',a.ENTITY],
                            cwd=ROOT,capture_output=True,text=True,check=True)
    native = json.loads(result.stdout)
    assert native['ok'] and native['id'] == a.ENTITY
    data = native['collections']
    assert data['current_length_bound_admissions'] == [document['admission']]
    assert data['current_length_bound_scenarios'] == document['scenario_records']
    assert [r for r in data['measurements'] if r['id'] == a.MEASUREMENT] == [document['measurement']]
    assert sorted(r['id'] for r in data['widths']) == sorted(owner.parent()['owner']['width_ids'])
    ranked = sorted((r for r in data['length_assessments'] if r.get('rank_eligible')),
                    key=lambda row:row['published_rank'])
    assert len(ranked) == 13 and all(r['entity_id'] != a.ENTITY for r in ranked)
    output = ROOT / '.pytest_cache/baffin-bound-browser'
    output.mkdir(parents=True,exist_ok=True)
    errors, originals = [], []
    phase = 'current-card'
    parity_queries = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page = browser.new_page(viewport={'width':1100,'height':900})
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:originals.append(request.url)
                if request.url.split('?')[0].endswith(('.pdf','.zip','.nc','.npz')) else None)
        try:
            page.goto(BASE+'/almanac/object.html?id='+quote(a.ENTITY))
            page.wait_for_function('window.oswObjectView?.id === "current:baffin"',timeout=180000)
            assert page.evaluate('window.oswObjectView') == native
            section = page.locator('#current-geographic-length-bound')
            for text in ['1,000 km','conditional geographic floor','unranked',
                         'Summer near-surface observations in 1978 and 1979',
                         'historical Baffin Current naming north to Lady Ann Strait',
                         'not below every editorial scenario','not observations',
                         'common fixed layer','no current route or physical endpoints']:
                expect(section).to_contain_text(text)
            expect(section.locator('tbody tr')).to_have_count(9)
            for row in document['scenario_records']:
                tr = section.locator(f'tr[data-scenario-index="{row["scenario_index"]}"]')
                values = [str(row['scenario_index']),*[f'{v:.1f}' for v in row['nominal_latitudes_degrees_north']],
                          f'{row["geographic_separation_km"]:.1f}']
                assert tr.locator('th,td').all_text_contents() == values
            image = section.locator('img')
            image.scroll_into_view_if_needed()
            expect(image).to_have_js_property('complete',True)
            assert image.evaluate('image => image.naturalWidth > 0')
            for width in [320,390]:
                phase = 'phone-'+str(width)
                page.set_viewport_size({'width':width,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                section.screenshot(path=str(output/f'card-{width}px.png'))
            image.screenshot(path=str(output/'scalar-phone.png'))
            phase = 'keyboard-scenario-query'
            link = section.get_by_role('link',name='Query all nine editorial scenarios',exact=True)
            link.focus()
            assert link.evaluate('link => document.activeElement === link')
            page.keyboard.press('Enter')
            page.wait_for_function('window.oswLastQueryResult',timeout=180000)
            assert page.evaluate('window.oswLastQueryResult.rows') == document['scenario_records']
            parity_queries += 1
            cases = [
                ('measurements','id',a.MEASUREMENT,[document['measurement']]),
                ('claims','id',document['claim']['id'],[document['claim']]),
                ('length_assessments','entity_id',a.ENTITY,[document['length_assessment']]),
                ('current_length_bound_admissions','id',a.ADMISSION,[document['admission']]),
                *[('sources','id',row['id'],[row]) for row in document['source_records']],
                ('objects','id',a.ENTITY,[owner.expected_owner(document)]),
            ]
            from test_rust_query_browser import browser_query
            for collection,field,value,rows in cases:
                phase = 'query-'+collection
                actual = browser_query(page,{'collection':collection,'filters':[{'field':field,'op':'eq','value':value}],'limit':10})
                assert actual['total'] == len(rows) and actual['rows'] == rows
                assert page.locator('#query-export').is_enabled()
                parity_queries += 1
            phase = 'qualified-length-ranking'
            actual = browser_query(page,{'collection':'length_assessments','filters':[{'field':'rank_eligible','op':'eq','value':True}],
                                         'sort':{'field':'published_rank','direction':'asc'},'limit':100})
            assert actual['total'] == 13 and actual['rows'] == ranked
            parity_queries += 1
            phase = 'scalar-source-integrity'
            response = page.request.get(BASE+'/'+a.FIGURE)
            assert response.ok and hashlib.sha256(response.body()).hexdigest() == a.OUTPUTS[a.FIGURE]
            assert not errors,errors
            assert not originals,originals
        except Exception as error:
            (output/'failure.json').write_text(json.dumps({
                'status':'FAIL','phase':phase,'error':str(error),'url':page.url,
                'bundle_sha256':native['bundle_sha256'],'errors':errors,'original_downloads':originals,
            },indent=2)+'\n',encoding='utf8')
            raise
        finally:
            browser.close()
    (output/'result.json').write_text(json.dumps({
        'status':'PASS','bundle_sha256':native['bundle_sha256'],
        'native_wasm_card_equal':True,'record_parity_queries':parity_queries,
        'complete_nine_scenario_table':True,'scenario_rows_are_editorial_not_observations':True,
        'parent_width_ids_preserved':True,'parent_owner_physical_fields_preserved':True,
        'historical_naming_scope_visible':True,'qualified_length_ranks_preserved':13,
        'phone_viewports_verified':[320,390],'phone_horizontal_overflow':False,
        'keyboard_scenario_query':True,'source_scalar_sha256':a.OUTPUTS[a.FIGURE],
        'errors':errors,'original_downloads':originals,'scientific_release_published':False,
    },indent=2)+'\n',encoding='utf8')


if __name__ == '__main__':
    main()
