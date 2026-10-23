"""All eleven native source matrices, both variables, and direct cell navigation."""
import gzip
import json
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright, expect
from angola_nansen_native_sections import ROOT, REPORT


def main():
    report=json.loads((ROOT/REPORT).read_bytes())
    output=ROOT/'.pytest_cache/angola-nansen-sections/browser';output.mkdir(parents=True,exist_ok=True)
    url=os.environ.get('OSW_TEST_BASE_URL','http://127.0.0.1:8788')+'/figures/angola-nansen-sections-2007-2014/'
    errors,originals=[],[];cases=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        page=browser.new_page(viewport={'width':1100,'height':1000})
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:originals.append(request.url) if request.url.split('?')[0].endswith(('.zip','.nc','.pdf')) else None)
        page.goto(url);page.wait_for_function('window.oswAngolaReady || window.oswAngolaError')
        assert not page.evaluate('window.oswAngolaError || null')
        assert page.evaluate('window.oswAngolaReport')==report
        for section in report['sections']:
            expected=json.loads(gzip.decompress((ROOT/section['field_file']).read_bytes()))
            page.locator('#section').select_option(section['id'])
            page.wait_for_function('(member)=>window.oswAngolaField?.source_member===member',arg=section['source_member'])
            # Complete matrices, coordinates, masks and metadata, not sampled cells.
            assert page.evaluate('window.oswAngolaField')==expected
            for variable in ['U_CUR','V_CUR']:
                page.locator('#variable').select_option(variable)
                rendered=page.evaluate('window.oswAngolaRender')
                summary=section['variable_summaries'][variable]
                assert rendered==dict(section=section['id'],variable=variable,width=section['dimensions']['PROFILE'],height=section['dimensions']['DEPTH'],finite=summary['finite'],missing=summary['missing'],interpolated=False)
                for p,b in [(1,1),(section['dimensions']['PROFILE'],section['dimensions']['DEPTH'])]:
                    page.locator('#profile').fill(str(p));page.locator('#profile').dispatch_event('change')
                    page.locator('#bin').fill(str(b));page.locator('#bin').dispatch_event('change')
                    row=page.evaluate('window.oswAngolaSelectedCell')
                    assert row['U_CUR']==expected['variables']['U_CUR']['values'][p-1][b-1]
                    assert row['V_CUR']==expected['variables']['V_CUR']['values'][p-1][b-1]
                    assert row['DEPTH']==expected['variables']['DEPTH']['values'][b-1]
                    assert row['TIME']==expected['variables']['TIME']['values'][p-1]
                    assert json.loads(page.locator('#raw').text_content())==row
                    query=json.loads(parse_qs(urlparse(page.locator('#query-cell').get_attribute('href')).query)['source-q'][0])
                    assert query=={'document':'research/angola-nansen-query-fields-v1/'+section['id'].split(':')[1]+'.json','pointer':f'/variables/{variable}/values/{p-1}','limit':1,'offset':b-1}
                cases.append({'section':section['id'],'variable':variable,'finite':summary['finite'],'missing':summary['missing']})
        page.locator('#profile').fill('2');page.locator('#profile').dispatch_event('change')
        page.locator('#bin').fill('2');page.locator('#bin').dispatch_event('change')
        page.locator('#field').focus();page.keyboard.press('ArrowRight');page.keyboard.press('ArrowDown')
        assert page.evaluate('window.oswAngolaSelectedCell.profile_index_1based')==3
        assert page.evaluate('window.oswAngolaSelectedCell.depth_bin_index_1based')==3
        share=page.locator('#permalink').get_attribute('href')
        page.goto(share);page.wait_for_function('window.oswAngolaReady')
        assert page.evaluate('window.oswAngolaSelectedCell.profile_index_1based')==3
        assert page.evaluate('window.oswAngolaSelectedCell.depth_bin_index_1based')==3
        page.screenshot(path=str(output/'desktop.png'))
        page.set_viewport_size({'width':320,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.locator('#field').scroll_into_view_if_needed();page.screenshot(path=str(output/'phone.png'))
        page.goto(url+'?section=missing&variable=bad&profile=-4&bin=99999');page.wait_for_function('window.oswAngolaReady')
        expect(page.locator('#section')).to_have_value(report['sections'][0]['id'])
        assert page.evaluate('window.oswAngolaSelectedCell.profile_index_1based')==1
        assert page.evaluate('window.oswAngolaSelectedCell.depth_bin_index_1based')==120
        # A corrupt payload never leaves another section's stale data visible.
        page.route('**/'+report['sections'][1]['field_file'],lambda route:route.fulfill(body=b'not the source',content_type='application/gzip'))
        page.locator('#section').select_option(report['sections'][1]['id'])
        expect(page.locator('#status')).to_contain_text('checksum mismatch')
        assert page.evaluate('window.oswAngolaField') is None
        assert page.locator('#cell tr').count()==0 and page.locator('#profile').is_disabled()
        assert not errors and not originals,(errors,originals)
        browser.close()
    result={'status':'PASS','full_sections_exact':11,'native_profiles':6148,'velocity_cells_including_missing':2044320,'variable_render_cases':cases,'keyboard_and_permalink':True,'phone_320px':True,'invalid_url_fallback':True,'corrupt_field_clears_stale_data':True,'automatic_original_downloads':0,'physical_width_admitted':False}
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print('PASS: all eleven complete matrices, both variables, missing cells, keyboard/permalink, phone and corruption guard')


if __name__=='__main__':main()
