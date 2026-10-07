"""Original-ledger current join/filter/rank oracle and actual index WASM parity."""
import gzip
import json
import os
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from test_rust_query_browser import ROOT, CLI


def main():
    def read(name):
        return json.loads((ROOT/'research'/name).read_bytes())
    data = read('ocean-current-almanac.json')
    atlas = read('ocean-current-atlas-index.json')
    lengths = read('ocean-current-length-evidence.json')
    nasa = read('ocean-current-nasa-crosswalk.json')
    tiles = read('nasa-perpetual-ocean-tile-join.json')
    by_id = {r['id']:r for r in data['entries']}
    lb = {r['current_id']:r for r in lengths['entries']}
    nb = {r['current_id']:r for r in nasa['entries']}
    ordered = sorted(data['entries'],key=lambda r:(-(r['length_km'] if r.get('length_km') is not None else -1),r['name']))
    rank, previous, measured = 0, None, 0
    ranks = {}
    for item in ordered:
        value = item.get('length_km')
        if value is not None:
            measured += 1
            if previous != value:
                rank = measured
            previous = value
        ranks[item['id']] = rank if value is not None else None

    def named(id):
        return {'id':id,'name':by_id[id]['name']}

    def oracle(selection):
        rows = []
        for item in ordered:
            id = item['id']
            classification = atlas['entries'][id]
            parent = item.get('part_of_system')
            components = item.get('component_current_ids',[])
            related_names = ' '.join(by_id[k]['name'] for k in ([parent] if parent else []) + components)
            haystack = ' '.join([item['name'],item['basin'],item['kind'],related_names,
                                 classification['identity_level'].replace('_',' '),classification['setting'].replace('_',' ')]).lower()
            if selection.get('text','').strip().lower() not in haystack:
                continue
            if any(selection.get(key,'all') != 'all' and selection[key] != value for key,value in [
                ('setting',classification['setting']),('length_status',lb[id]['status']),('nasa_status',nb[id]['status'])]):
                continue
            rows.append({'record':item,'classification':classification,'length_evidence':lb[id],
                         'nasa_relation':nb[id],'rank':ranks[id],
                         'linked_currents':[named(k) for k in ([parent] if parent else components)],
                         'identity_related':named(item['identity_review']['related_current_id']) if item.get('identity_review',{}).get('related_current_id') else None,
                         'related_currents':[named(k) for k in item.get('related_current_ids',[])],
                         'nasa_links':[{'id':k,'upstream_feeder':any(r['nasa_object_id']==k and r['relation']=='independently_named_upstream_feeder'
                                                                 for r in nb[id]['object_relations'])} for k in item.get('related_nasa_object_ids',[])],
                         'scene_url':atlas['nasa_current_scene_urls'].get(id),
                         'crop_url':tiles['current_joins'][id][0]['url']})
        return rows

    selections = [{},{'length_status':'published_estimate'},{'length_status':'derived_lower_bound'},
                  {'nasa_status':'independent_context'},{'text':'agulhas','setting':'western_boundary'}]
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as directory:
        packet = __import__('pathlib').Path(directory)/'index.json'
        packet.write_bytes(gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes()))
        def native(selection):
            run = subprocess.run([str(CLI),'--index',str(packet),'--currents','-'],
                                 input=json.dumps(selection),text=True,encoding='utf-8',capture_output=True)
            assert run.returncode == 0, run.stderr
            return json.loads(run.stdout)
        native_views = [native(s) for s in selections]
        for s,view in zip(selections,native_views):
            assert view['ok'] and view['rows'] == oracle(s), s
        initial = native_views[0]
        assert initial['total'] == 100
        assert initial['sources'] == data['sources']
        assert initial['length_counts'] == lengths['counts']
        assert initial['nasa_counts'] == nasa['counts']
        assert sum(r['rank'] is not None for r in initial['rows']) == 11
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page = browser.new_page()
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto('http://127.0.0.1:8788/almanac/index.html')
            page.wait_for_function('window.oswIndexPageReady',timeout=90000)
            assert page.evaluate('oswIndexCurrentView') == initial
            cases = selections + [{'length_status':key} for key in lengths['status_definitions']]
            cases += [{'nasa_status':key} for key in nasa['status_definitions']]
            cases += [{'setting':key} for key in initial['settings']]
            cases += [{'text':'Gulf Stream System'},{'text':'  aGuLhAs  '},{'text':'nothing matches here'}]
            for selection in cases:
                page.evaluate('''s=>{
                  oswIndexCurrentView=null;
                  document.querySelector('#current-search').value=s.text||'';
                  document.querySelector('#current-setting').value=s.setting||'all';
                  document.querySelector('#current-length-status').value=s.length_status||'all';
                  document.querySelector('#current-nasa-status').value=s.nasa_status||'all';
                  document.querySelector('#current-search').dispatchEvent(new Event('input'));
                }''',selection)
                page.wait_for_function('window.oswIndexCurrentView',timeout=90000)
                actual=page.evaluate('oswIndexCurrentView')
                assert actual['rows'] == oracle(selection), selection
                assert page.locator('#current-rows tr').evaluate_all('(rows)=>rows.map(r=>r.id)') == [
                    'current-'+r['record']['id'] for r in actual['rows']]
                assert page.locator('#current-rows tr td:first-child').all_text_contents() == [
                    str(r['rank']) if r['rank'] is not None else '—' for r in actual['rows']]
                if selection in selections:
                    assert actual == native_views[selections.index(selection)]
            for selection in [{'setting':'invented'},{'length_status':'invented'},{'nasa_status':'invented'},{'extra':True}]:
                assert page.evaluate('s=>oswIndexCurrents(s).then(()=>false,()=>true)',selection)
            # Latest input wins when several worker replies are pending.
            page.locator('#current-search').fill('Gulf')
            page.locator('#current-search').fill('Agulhas')
            page.locator('#current-search').fill('Kuroshio')
            page.wait_for_function("ids=>oswIndexCurrentView.rows.map(r=>r.record.id).join('|')===ids",
                                   arg='|'.join(r['record']['id'] for r in oracle({'text':'Kuroshio'})))
            assert page.evaluate('oswIndexCurrentView.rows') == oracle({'text':'Kuroshio'})
            # Related links must wait for fresh rows and reset all active facets.
            page.evaluate("document.querySelector('#current-search').value='Agulhas'; document.querySelector('#current-length-status').value='derived_lower_bound'; document.querySelector('#current-search').dispatchEvent(new Event('input'))")
            page.wait_for_function("oswIndexCurrentView.rows.some(r=>r.record.id==='agulhas-return') && oswIndexCurrentView.rows.every(r=>r.length_evidence.status==='derived_lower_bound')")
            page.locator('#current-agulhas-return a[href="#current-agulhas"]').first.click()
            page.wait_for_function("location.hash==='#current-agulhas' && oswIndexCurrentView.rows.length===100")
            page.locator('#current-search').fill('Kuroshio')
            page.wait_for_function("ids=>oswIndexCurrentView.rows.map(r=>r.record.id).join('|')===ids",
                                   arg='|'.join(r['record']['id'] for r in oracle({'text':'Kuroshio'})))
            page.locator('#motion-markers a[data-record="florida"]').first.click()
            page.wait_for_function("location.hash==='#current-florida' && oswIndexCurrentView.rows.length===100")
            assert not errors, errors
            browser.close()
    print(f'PASS: exact original-ledger joins and global ranks; five native/WASM views, {len(cases)} filter cases, invalid facets, rapid input and related-current navigation')


if __name__ == '__main__':
    main()
