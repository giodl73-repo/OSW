"""Actual shipped normal queries, map/card sync, sharing, missingness and source access."""
import hashlib,json,os
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_current_research_evidence_browser import ROOT,BASE,native
from test_motion_dashboard_browser import settle
import kuroshio_axis_normal_query as k


def main():
    out=ROOT/'.pytest_cache/kuroshio-normal-browser';out.mkdir(exist_ok=True)
    _,doc=k.verify_inputs();errors=[]
    q={'collection':'diagnostics','filters':[{'field':'id','op':'eq','value':k.ID}],'limit':1}
    expected=native(q);scene=expected['chart_scene']
    assert scene['default_metric']=='axis_normal'
    assert len(scene['normal']['summaries'])==585
    samples={'collection':k.COLLECTION,'filters':[{'field':'sample_date','op':'eq','value':'2024-02-01'},{'field':'source_level','op':'eq','value':23}],'limit':100}
    selected=native(samples);assert selected['total']==15
    def url(query):return BASE+'/almanac/query.html?q='+quote(json.dumps(query))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page=browser.new_page(viewport={'width':1360,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url(q));page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==expected
        panel=page.locator('.kuroshio-daily');expect(panel.locator('.kuroshio-daily-metric')).to_have_value('axis_normal')
        assert panel.locator('tbody tr').count()==5
        expect(panel.locator('.kuroshio-normal-scope')).to_contain_text('unknown')
        expect(panel.locator('thead')).to_contain_text('Selected month')
        panel.locator('.kuroshio-daily-date').select_option('2024-02-01')
        panel.locator('.kuroshio-daily-depth').select_option('23')
        panel.locator('.kuroshio-daily-tangent').select_option('28')
        frame=next(f for f in scene['frames'] if f['date']=='2024-02-01' and f['source_level']==23)
        rows=[s for s in frame['normal_sections'] if s['tangent_half_window_km']==28]
        assert panel.locator('svg path[data-model-role="axis_normal"]').count()==sum(bool(s['d']) for s in rows)
        panel.locator('tbody tr').first.get_by_role('button',name='Inspect',exact=True).click()
        expect(page.locator('#query-detail')).to_contain_text(rows[0]['sample_id'])
        page.locator('#query-detail').get_by_role('button',name='Close record',exact=True).click()
        share=panel.get_by_role('link',name='Share this dated model view').get_attribute('href')
        for text in ['dimension-date=2024-02-01','dimension-depth=23','dimension-metric=axis_normal','dimension-tangent=28']:assert text in share
        panel.screenshot(path=str(out/'normal-desktop.png'))
        page.goto(url(samples));page.wait_for_function('window.oswLastQueryResult',timeout=120000)
        assert page.evaluate('window.oswLastQueryResult')==selected
        page.goto(BASE+'/almanac/reference-routes.html?atlas-layout=map&atlas-feature=current%3Akuroshio&dimension-metric=axis_normal&dimension-tangent=28&dimension-date=2024-02-01&dimension-depth=23#route-atlas')
        preview=page.locator('#route-atlas-preview .kuroshio-daily');expect(preview).to_be_visible(timeout=120000)
        expect(preview.locator('.kuroshio-daily-metric')).to_have_value('axis_normal')
        assert page.locator('#route-atlas-model-lines path[data-model-role="axis_normal"]').count()==sum(bool(s['d']) for s in rows)
        assert json.loads(page.evaluate('(p)=>window.oswAtlasSnapshot.sources_json[p]',k.source.FILE))==doc
        page.locator('#route-atlas-card-link').focus();page.keyboard.press('Enter')
        card=page.locator('#kuroshio-2024-model-card');expect(card).to_be_focused()
        expect(card.locator('.kuroshio-daily-metric')).to_have_value('axis_normal')
        expect(card.locator('.kuroshio-daily-tangent')).to_have_value('28')
        card.locator('.kuroshio-daily-tangent').select_option('7')
        expect(preview.locator('.kuroshio-daily-tangent')).to_have_value('7')
        card.get_by_role('link',name='Back to Kuroshio on the global map').focus();page.keyboard.press('Enter')
        expect(preview).to_be_visible(timeout=120000)
        expect(preview.locator('.kuroshio-daily-tangent')).to_have_value('7')
        preview.locator('.kuroshio-daily-metric').select_option('regional')
        assert page.locator('#route-atlas-model-lines path').count()==3
        preview.locator('.kuroshio-daily-metric').select_option('axis_normal')
        page.locator('#route-atlas-select').select_option('current:agulhas')
        assert page.locator('#route-atlas-model-lines path').count()==0
        page.set_viewport_size({'width':320,'height':1000});page.emulate_media(reduced_motion='reduce');page.goto(share)
        panel=page.locator('.kuroshio-daily');expect(panel).to_be_visible(timeout=120000)
        expect(panel.locator('.kuroshio-daily-tangent')).to_have_value('28')
        expect(panel.locator('.kuroshio-daily-play')).to_be_disabled()
        panel.locator('.kuroshio-daily-tangent').focus();page.keyboard.press('Home');page.keyboard.press('Enter')
        expect(panel.locator('.kuroshio-daily-tangent')).to_have_value('7')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        panel.screenshot(path=str(out/'normal-mobile.png'))
        source_query={'document':k.source.FILE,'pointer':'/cases','filters':[{'field':'record.id','op':'eq','value':rows[0]['sample_id']}],'limit':1}
        page.goto(BASE+'/almanac/query.html?source-q='+quote(json.dumps(source_query)))
        page.wait_for_function('window.oswSourceQueryResult',timeout=120000)
        result=page.evaluate('window.oswSourceQueryResult');assert result['total']==1
        assert result['rows'][0]['record']==next(r for r in doc['cases'] if r['id']==rows[0]['sample_id'])
        page.goto(BASE+'/almanac/dashboard.html');page.wait_for_function('window.oswDashboardSnapshot',timeout=120000)
        page.locator('#dashboard-metric').select_option('axis_normal_samples');settle(page)
        assert page.locator('.motion-card.lit').count()==1
        expect(page.locator('.motion-card.lit')).to_contain_text('Kuroshio')
        assert not errors,errors
        browser.close()
    receipt={'status':'PASS','typed_attempts':16470,'normal_source_sha256':hashlib.sha256((ROOT/k.source.FILE).read_bytes()).hexdigest(),
        'wasm_sha256':hashlib.sha256((ROOT/'almanac/query-engine.wasm').read_bytes()).hexdigest(),
        'component_sha256':hashlib.sha256((ROOT/'almanac/kuroshio-daily.js').read_bytes()).hexdigest(),
        'native_wasm_exact':True,'source_row_exact':True,'map_card_metric_window_sync':True,'share_restore':True,
        'keyboard':True,'phone_320px':True,'reduced_motion':True,'single_dashboard_owner':True,'page_errors':errors}
    (out/'browser-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
