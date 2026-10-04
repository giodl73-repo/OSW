"""Old/current snapshot migration, conflict choices and native/WASM parity."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_workspace_browser import ready,inspect_source,edit
from test_rust_query_browser import ROOT,BASE,browser_query

def main():
    original=(ROOT/'almanac/query-data.json').read_bytes();old_hash=hashlib.sha256(original).hexdigest()
    changed=json.loads(original);row=next(r for r in changed['collections']['objects'] if r['id']=='current:kuroshio')
    row['label']='Kuroshio updated source label';row['new_source_field']='Synthetic source-update fixture'
    updated=json.dumps(changed,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    new_hash=hashlib.sha256(updated).hexdigest()
    manifest=json.loads((ROOT/'almanac/query-engine.manifest.json').read_text(encoding='utf-8'));manifest['sha256']['almanac/query-data.json']=new_hash
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        context=browser.new_context(viewport={'width':1200,'height':1000});a=context.new_page();ready(a);inspect_source(a)
        proposed=json.loads(a.locator('.working-json').input_value());proposed['label']='Kuroshio proposed alias'
        a.locator('.working-json').fill(json.dumps(proposed));edit(a,'Kuroshio alias proposal','Synthetic proposal for rebase verification.')
        expect(a.locator('#workspace-status')).to_contain_text('Revision 1')
        a.locator('#workspace-controls').evaluate('(el)=>el.open=true')
        with a.expect_download() as downloaded:a.locator('#workspace-export').click()
        old_journal=json.loads(Path(downloaded.value.path()).read_text(encoding='utf-8'))
        context.route('**/query-data.json',lambda r:r.fulfill(body=updated,content_type='application/json'))
        context.route('**/query-engine.manifest.json',lambda r:r.fulfill(json=manifest))
        b=context.new_page();ready(b);expect(b.locator('#workspace-status')).to_contain_text('Revision 0')
        b.locator('#workspace-archive-controls').evaluate('(el)=>el.open=true');b.locator('#workspace-list').click()
        expect(b.locator('#workspace-snapshots option')).to_have_count(1)
        b.locator('#workspace-snapshots').select_option(old_hash)
        with b.expect_download() as source:b.locator('#workspace-export-source').click()
        assert Path(source.value.path()).read_bytes()==original
        b.locator('#workspace-rebase-preview').click()
        expect(b.locator('#workspace-rebase-plan')).to_contain_text('1 unresolved conflicts',timeout=60000)
        assert b.get_by_role('button',name='Save rebased working records').is_disabled()
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as directory:
            folder=Path(directory);new_path=folder/'new.json';new_path.write_bytes(updated)
            request={'journal':old_journal,'base_revision':0,'transaction_id':'native-rebase','created_at':'2026-10-04T12:00:00Z','resolutions':{}}
            rp=folder/'request.json';rp.write_text(json.dumps(request),encoding='utf-8');exe=str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe')
            plan=json.loads(subprocess.check_output([exe,str(new_path),'--rebase',str(ROOT/'almanac/query-data.json'),str(rp)],text=True,encoding='utf-8'))
            assert plan['unresolved']==1 and not plan['ready']
            conflict=plan['conflicts'][0];assert conflict['path']=='/label'
            select=b.locator('#workspace-rebase-plan select').first
            assert select.get_attribute('data-conflict')==conflict['id']
            select.select_option('proposed');expect(b.locator('#workspace-rebase-plan')).to_contain_text('0 unresolved conflicts')
            b.locator('#workspace-rebase-plan details').first.evaluate('(el)=>el.open=true')
            b.set_viewport_size({'width':320,'height':900})
            assert b.evaluate('document.documentElement.scrollWidth<=innerWidth')
            b.set_viewport_size({'width':1200,'height':1000})
            b.locator('#workspace-rebase-plan').screenshot(path=str(ROOT/'figures/rust-rebase-conflict-review.png'))
            request['resolutions']={conflict['id']:'proposed'};rp.write_text(json.dumps(request),encoding='utf-8')
            native_path=folder/'rebased.json'
            native=json.loads(subprocess.check_output([exe,str(new_path),'--rebase',str(ROOT/'almanac/query-data.json'),str(rp),'--prepare','--output',str(native_path)],text=True,encoding='utf-8'))
            assert native['journal']['schema']=='osw.workspace-journal.v2'
            b.get_by_role('button',name='Save rebased working records').click();expect(b.locator('#workspace-status')).to_contain_text('Revision 1')
            b.wait_for_function('window.oswLastQueryResult.collection==="working_records"')
            record=b.evaluate('window.oswLastQueryResult.rows[0]')
            assert record['proposed_data']['label']=='Kuroshio proposed alias'
            assert record['proposed_data']['new_source_field']=='Synthetic source-update fixture'
            assert record==native['journal']['events'][0]['operations'][0]['record']
            with b.expect_download() as exported:b.locator('#workspace-export').click()
            migrated=json.loads(Path(exported.value.path()).read_text(encoding='utf-8'))
            assert migrated['events'][0]['rebase']==native['journal']['events'][0]['rebase']
            assert migrated['bundle_sha256']==new_hash
        b.reload();b.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert b.evaluate('window.oswLastQueryResult.rows[0].proposed_data.label')=='Kuroshio proposed alias'
        source_query=browser_query(b,{'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:kuroshio'}]})
        assert source_query['rows'][0]['label']=='Kuroshio updated source label'
        with a.expect_download() as unchanged:a.locator('#workspace-export').click()
        assert json.loads(Path(unchanged.value.path()).read_text(encoding='utf-8'))==old_journal
        b.set_viewport_size({'width':320,'height':900});assert b.evaluate('document.documentElement.scrollWidth<=innerWidth')
        browser.close()
    print('PASS: retained baseline, three-way conflict preview/choice, native/WASM rebase parity, v2 replay, old/source preservation and mobile')

if __name__=='__main__':main()
