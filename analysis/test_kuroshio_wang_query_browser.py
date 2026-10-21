"""Actual native/WASM model queries, mapped cards, stepping and source access."""
import json,os
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
from test_motion_dashboard_browser import native_selection,settle
import kuroshio_wang_query as k


def url(q):return BASE+'/almanac/query.html?q='+quote(json.dumps(q))


def main():
    out=ROOT/'.pytest_cache/kuroshio-wang-query-browser';out.mkdir(exist_ok=True)
    contract,doc=k.verify_inputs();errors=[]
    q={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':k.ID}],'limit':1}
    expected=native(q);assert expected['total']==1
    assert expected['chart_scene']['kind']=='kuroshio_daily_dimensions'
    for quantity,total,resolved in [('regional_axis_length',1098,908),('fixed_latitude_boundary_span',5490,4976)]:
        filters=[{'field':'quantity','op':'eq','value':quantity}]
        assert native({'collection':k.COLLECTION,'filters':filters,'limit':1})['total']==total
        assert native({'collection':k.COLLECTION,'filters':filters+[{'field':'status','op':'eq','value':'resolved'}],'limit':1})['total']==resolved
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url(q));page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        panel=page.locator('.kuroshio-daily');expect(panel).to_have_count(1)
        expect(panel.locator('.kuroshio-daily-status')).to_contain_text('2024-01-01')
        assert panel.locator('tbody tr').count()==6
        expect(panel.locator('tbody')).to_contain_text('304 / 366')
        panel.locator('tbody tr').first.get_by_role('button',name='Inspect',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text(expected['chart_scene']['frames'][0]['axis_sample_id'])
        page.locator('#query-detail').get_by_role('button',name='Close record',exact=True).click()
        panel.locator('.kuroshio-daily-depth').select_option('23')
        panel.locator('.kuroshio-daily-date').select_option('2024-02-01')
        expect(panel.locator('.kuroshio-daily-status')).to_contain_text('109.73 m')
        expect(panel.locator('tbody')).to_contain_text('365 / 366')
        share=panel.get_by_role('link',name='Share this dated model view').get_attribute('href')
        assert 'dimension-date=2024-02-01' in share and 'dimension-depth=23' in share
        panel.locator('.kuroshio-daily-date').focus();page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Enter')
        expect(panel.locator('.kuroshio-daily-status')).to_contain_text('2024-02-01')
        panel.locator('.kuroshio-daily-play').click()
        page.wait_for_function('document.querySelector(".kuroshio-daily-date").value!=="2024-02-01"',timeout=10000)
        page.emulate_media(reduced_motion='reduce');expect(panel.locator('.kuroshio-daily-play')).to_be_disabled()
        frozen=panel.locator('.kuroshio-daily-date').input_value();page.wait_for_timeout(1400);assert panel.locator('.kuroshio-daily-date').input_value()==frozen
        panel.locator('.kuroshio-daily-date').select_option('2024-11-01');panel.locator('.kuroshio-daily-depth').select_option('1')
        expect(panel.locator('tbody')).to_contain_text('Unresolved')
        panel.screenshot(path=str(out/'query-desktop.png'))
        samples={'collection':k.COLLECTION,'filters':[{'field':'sample_date','op':'eq','value':'2024-02-01'},{'field':'source_level','op':'eq','value':23}],'limit':100}
        page.goto(url(samples));page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==native(samples);assert page.evaluate('window.oswLastQueryResult.total')==6
        page.goto(BASE+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio#route-atlas')
        preview=page.locator('#route-atlas-preview .kuroshio-daily');expect(preview).to_be_visible(timeout=120000)
        assert page.locator('#route-atlas-model-lines path').count()==3
        old=page.locator('#route-atlas-model-lines path').first.get_attribute('d')
        preview.locator('.kuroshio-daily-date').select_option('2024-02-01')
        preview.locator('.kuroshio-daily-depth').select_option('23')
        assert page.locator('#route-atlas-model-lines path').first.get_attribute('d')!=old
        expect(page.locator('#route-atlas-status')).to_contain_text('2024-02-01')
        assert json.loads(page.evaluate('(f)=>window.oswAtlasSnapshot.sources_json[f]',k.source.FILE))==doc
        page.locator('#route-atlas-card-link').focus();page.keyboard.press('Enter')
        card=page.locator('#kuroshio-2024-model-card');expect(card).to_be_focused()
        expect(card.locator('.kuroshio-daily')).to_be_visible()
        expect(card.locator('.kuroshio-daily-date')).to_have_value('2024-02-01')
        expect(card.locator('.kuroshio-daily-depth')).to_have_value('23')
        card.get_by_role('link',name='Back to Kuroshio on the global map').focus();page.keyboard.press('Enter')
        expect(page.locator('#route-atlas-preview .kuroshio-daily')).to_be_visible(timeout=120000)
        expect(page.locator('#route-atlas-preview .kuroshio-daily-date')).to_have_value('2024-02-01')
        expect(page.locator('#route-atlas-preview .kuroshio-daily-depth')).to_have_value('23')
        page.locator('#route-atlas-select').select_option('current:agulhas');assert page.locator('#route-atlas-model-lines path').count()==0
        page.set_viewport_size({'width':320,'height':1000});page.goto(share)
        panel=page.locator('.kuroshio-daily');expect(panel).to_be_visible(timeout=120000)
        expect(panel.locator('.kuroshio-daily-status')).to_contain_text('2024-02-01')
        expect(panel.locator('.kuroshio-daily-status')).to_contain_text('109.73 m')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        panel.screenshot(path=str(out/'query-mobile.png'))
        page.goto(BASE+'/almanac/seasons.html?current=kuroshio')
        expect(page.locator('.kuroshio-daily')).to_be_visible(timeout=120000)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        source_q={'document':k.source.FILE,'pointer':'/daily','filters':[{'field':'record.date','op':'eq','value':'2024-02-01'},{'field':'record.source_level','op':'eq','value':23}],'limit':10}
        page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(source_q)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
        result=page.evaluate('window.oswSourceQueryResult');assert result['total']==1
        assert result['rows'][0]['record']==next(r for r in doc['daily'] if r['date']=='2024-02-01' and r['source_level']==23)
        page.goto(BASE+'/almanac/dashboard.html')
        page.wait_for_function('window.oswDashboardSnapshot',timeout=120000)
        page.locator('#dashboard-metric').select_option('model_dimension_samples');settle(page)
        assert page.locator('.motion-card.lit').count()==1
        page.locator('#dashboard-covered').check();settle(page)
        assert page.locator('.motion-card').count()==1
        expect(page.locator('.motion-card')).to_contain_text('Kuroshio')
        selection=page.evaluate('window.oswDashboardSelection')
        assert selection['result']==native_selection(selection['request'])
        assert selection['result']['ids']==['current:kuroshio']
        assert not errors,errors;browser.close()
    receipt={'status':'PASS','native_wasm_diagnostic_exact':True,'typed_records':6588,'regional_lengths_resolved':908,'fixed_section_spans_resolved':4976,'dated_frames':36,'map_card_keyboard_return':True,'global_map_paths_update_and_clear':True,'shared_date_depth':True,'reduced_motion_stops_playback':True,'phone_reflow':True,'seasons':True,'exact_source_query':True,'dashboard_metric_single_owner_and_native_parity':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))


if __name__=='__main__':main()
