"""Old/current snapshot migration, conflict choices and native/WASM parity."""
from query_packet import read_bundle_bytes
from browser_bundle_fixture import install_bundle_fixture
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_workspace_browser import ready,inspect_source,edit
from test_rust_query_browser import CLI,ROOT,BASE,browser_query

def preview(page):
    page.locator('#workspace-rebase-preview').click()
    expect(page.locator('#workspace-rebase-preview')).to_be_enabled(timeout=90000)
    assert page.locator('#workspace-rebase-plan').is_visible(),page.locator('#workspace-status').inner_text()
    expect(page.locator('#workspace-rebase-plan')).to_contain_text('1 unresolved conflicts')

def main():
    (ROOT/'tmp').mkdir(exist_ok=True)
    original=read_bundle_bytes(ROOT/'almanac/query-data.json');old_hash=hashlib.sha256(original).hexdigest()
    changed=json.loads(original);row=next(r for r in changed['collections']['objects'] if r['id']=='current:kuroshio')
    # Keep checked scientific identity and provenance intact. Both editions add
    # a different editorial note, exercising the same three-way field conflict.
    row['new_source_field']='Synthetic source-update fixture'
    row['source_only_addition']='Synthetic source-only addition'
    updated=json.dumps(changed,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    new_hash=hashlib.sha256(updated).hexdigest()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        context=browser.new_context(viewport={'width':1200,'height':1000});a=context.new_page();ready(a);inspect_source(a)
        proposed=json.loads(a.locator('.working-json').input_value());proposed['new_source_field']='Proposed comparison note'
        a.locator('.working-json').fill(json.dumps(proposed));edit(a,'Kuroshio alias proposal','Synthetic proposal for rebase verification.')
        expect(a.locator('#workspace-status')).to_contain_text('Revision 1')
        a.locator('#workspace-controls').evaluate('(el)=>el.open=true')
        with a.expect_download() as downloaded:a.locator('#workspace-export').click()
        old_journal=json.loads(Path(downloaded.value.path()).read_text(encoding='utf-8'))
        b=context.new_page()
        fixture=install_bundle_fixture(b,changed);assert fixture.read_bytes()==updated
        ready(b);expect(b.locator('#workspace-status')).to_contain_text('Revision 0')
        b.locator('#workspace-archive-controls').evaluate('(el)=>el.open=true');b.locator('#workspace-list').click()
        expect(b.locator('#workspace-snapshots option')).to_have_count(1)
        b.locator('#workspace-snapshots').select_option(old_hash)
        with b.expect_download() as source:b.locator('#workspace-export-source').click()
        assert Path(source.value.path()).read_bytes()==original
        preview(b)
        assert b.get_by_role('button',name='Save rebased working records').is_disabled()
        # Exported complete source bytes exceed the old 100 MB upload cap.
        assert len(original)>100000000
        b.locator('#workspace-rebase-source').set_input_files(source.value.path())
        preview(b)
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as directory:
            folder=Path(directory);new_path=folder/'new.json';new_path.write_bytes(updated)
            request={'journal':old_journal,'base_revision':0,'transaction_id':'native-rebase','created_at':'2026-10-04T12:00:00Z','resolutions':{}}
            rp=folder/'request.json';rp.write_text(json.dumps(request),encoding='utf-8');exe=str(CLI)
            plan=json.loads(subprocess.check_output([exe,str(new_path),'--rebase',str(ROOT/'almanac/query-data.json'),str(rp)],text=True,encoding='utf-8'))
            assert plan['unresolved']==1 and not plan['ready']
            conflict=plan['conflicts'][0];assert conflict['path']=='/new_source_field'
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
            assert record['proposed_data']['new_source_field']=='Proposed comparison note'
            assert record['proposed_data']['source_only_addition']=='Synthetic source-only addition'
            assert record==native['journal']['events'][0]['operations'][0]['record']
            with b.expect_download() as exported:b.locator('#workspace-export').click()
            migrated=json.loads(Path(exported.value.path()).read_text(encoding='utf-8'))
            assert migrated['events'][0]['rebase']==native['journal']['events'][0]['rebase']
            assert migrated['bundle_sha256']==new_hash
        b.reload();b.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert b.evaluate('window.oswLastQueryResult.rows[0].proposed_data.new_source_field')=='Proposed comparison note'
        source_query=browser_query(b,{'collection':'objects','filters':[{'field':'id','op':'eq','value':'current:kuroshio'}]})
        assert source_query['rows'][0]['new_source_field']=='Synthetic source-update fixture'
        with a.expect_download() as unchanged:a.locator('#workspace-export').click()
        assert json.loads(Path(unchanged.value.path()).read_text(encoding='utf-8'))==old_journal
        b.set_viewport_size({'width':320,'height':900});assert b.evaluate('document.documentElement.scrollWidth<=innerWidth')
        browser.close()
    print('PASS: retained baseline, three-way conflict preview/choice, native/WASM rebase parity, v2 replay, old/source preservation and mobile')

if __name__=='__main__':main()
