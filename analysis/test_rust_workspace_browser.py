"""Durable browser/native journals, optimistic edits, import and failed saves."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import browser_query,BASE,ROOT


def inspect_source(page):
    browser_query(page,{'collection':'objects','text':'current:kuroshio','record_type':'named_current'})
    page.get_by_role('button',name='Kuroshio Current',exact=True).click()
    expect(page.locator('.working-editor')).to_be_visible()
    page.locator('.working-editor').evaluate('(el)=>el.open=true')


def edit(page,label,summary):
    page.locator('.working-editor input').fill(label)
    page.locator('.working-editor textarea').first.fill(summary)
    page.get_by_role('button',name='Save proposed revision').click()


def ready(page):
    page.goto(BASE)
    page.wait_for_function('window.oswLastQueryResult',timeout=60000)
    page.locator('#workspace-controls').evaluate('(el)=>el.open=true')
    expect(page.locator('#workspace-status')).to_contain_text('Revision')


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER'])
        context=browser.new_context(viewport={'width':1280,'height':1000})
        a=context.new_page();b=context.new_page();ready(a);ready(b)
        inspect_source(a);inspect_source(b)
        edit(a,'Kuroshio working review','Test proposal retains regional measurement scope.')
        a.wait_for_function('window.oswLastQueryResult.collection==="working_records"&&window.oswLastQueryResult.total===1')
        expect(a.locator('#workspace-status')).to_contain_text('Revision 1')
        edit(b,'Conflicting proposal','A stale editor must not overwrite revision one.')
        expect(b.locator('.working-editor [role="status"]')).to_contain_text('revision conflict')
        b.locator('#workspace-refresh').click()
        expect(b.locator('#workspace-status')).to_contain_text('Revision 1')
        b.locator('#workspace-query').click()
        b.wait_for_function('window.oswLastQueryResult.collection==="working_records"')
        b.get_by_role('button',name='Kuroshio working review',exact=True).click()
        b.locator('.working-editor').evaluate('(el)=>el.open=true')
        edit(b,'Kuroshio revised working review','Second revision from a reloaded working copy.')
        expect(b.locator('#workspace-status')).to_contain_text('Revision 2')
        a.reload();a.wait_for_function('window.oswLastQueryResult',timeout=60000)
        expect(a.locator('#workspace-status')).to_contain_text('Revision 2')
        assert a.locator('#query-collection option[value="working_records"]').inner_text().endswith('(1)')
        assert a.evaluate('window.oswLastQueryResult.rows[0].label')=='Kuroshio revised working review'
        a.locator('#workspace-controls').evaluate('(el)=>el.open=true')
        with a.expect_download() as download:a.locator('#workspace-export').click()
        journal=json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
        assert len(journal['events'])==2
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as directory:
            folder=Path(directory);jp=folder/'journal.json';jp.write_text(json.dumps(journal),encoding='utf-8')
            query={'collection':'working_records','limit':50};qp=folder/'query.json';qp.write_text(json.dumps(query),encoding='utf-8')
            exe=str(ROOT/'rust/osw-query/target/debug/osw-query-cli.exe')
            native=json.loads(subprocess.check_output([exe,str(ROOT/'almanac/query-data.json'),'--workspace',str(jp),str(qp)],text=True,encoding='utf-8'))
            assert native==browser_query(a,query)
            tx={'base_revision':2,'transaction_id':'native-revision-3','created_at':'2026-10-04T12:00:00Z','operations':[{'op':'upsert','record':native['rows'][0]}]}
            tx['operations'][0]['record']['summary']='Third revision prepared by native Rust.'
            tp=folder/'transaction.json';tp.write_text(json.dumps(tx),encoding='utf-8')
            prepared=json.loads(subprocess.check_output([exe,str(ROOT/'almanac/query-data.json'),'--workspace',str(jp),'--transaction',str(tp)],text=True,encoding='utf-8'))
            saved_path=folder/'native-revision-3.json'
            subprocess.check_output([exe,str(ROOT/'almanac/query-data.json'),'--workspace',str(jp),'--transaction',str(tp),'--output',str(saved_path)],text=True,encoding='utf-8')
            assert json.loads(saved_path.read_text(encoding='utf-8'))==prepared['journal']
            saved_bytes=saved_path.read_bytes()
            failed_write=subprocess.run([exe,str(ROOT/'almanac/query-data.json'),'--workspace',str(jp),'--transaction',str(tp),'--output',str(saved_path)],capture_output=True,text=True)
            assert failed_write.returncode!=0 and saved_path.read_bytes()==saved_bytes
            imported=prepared['journal'];jp.write_text(json.dumps(imported),encoding='utf-8')
            a.locator('#workspace-import').set_input_files(str(jp))
            expect(a.locator('#workspace-status')).to_contain_text('Revision 3')
            # Snapshot mismatch and history rewriting cannot commit.
            bad=json.loads(json.dumps(imported));bad['bundle_sha256']='0'*64;jp.write_text(json.dumps(bad),encoding='utf-8')
            a.locator('#workspace-import').set_input_files(str(jp));expect(a.locator('#workspace-status')).to_contain_text('another source snapshot')
            bad=json.loads(json.dumps(imported));bad['events'][0]['operations'][0]['record']['summary']='Rewritten historical event';jp.write_text(json.dumps(bad),encoding='utf-8')
            a.locator('#workspace-import').set_input_files(str(jp));expect(a.locator('#workspace-status')).to_contain_text('rewrite existing revision history')
            a.locator('#workspace-refresh').click();expect(a.locator('#workspace-status')).to_contain_text('Revision 3')
        # Archive preserves all prior events, but removes the live working record.
        a.get_by_role('button',name='Kuroshio revised working review',exact=True).click()
        a.locator('.working-editor').evaluate('(el)=>el.open=true')
        a.get_by_role('button',name='Archive working copy').click()
        expect(a.locator('#workspace-status')).to_contain_text('Revision 4')
        a.wait_for_function('window.oswLastQueryResult.total===0')
        a.reload();a.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert a.evaluate('window.oswLastQueryResult.total')==0
        a.locator('#workspace-controls').evaluate('(el)=>el.open=true')
        a.locator('#workspace-archive-controls').evaluate('(el)=>el.open=true')
        # An older-source journal is retained as storage, never applied to this source.
        older=json.loads(json.dumps(imported));older['bundle_sha256']='f'*64
        a.evaluate('''journal=>new Promise((resolve,reject)=>{const request=indexedDB.open('osw-query-workspaces',1);request.onsuccess=()=>{const db=request.result,tx=db.transaction('journals','readwrite');tx.objectStore('journals').put(journal,journal.bundle_sha256);tx.oncomplete=()=>{db.close();resolve();};tx.onerror=()=>reject(tx.error);};})''',older)
        a.locator('#workspace-list').click()
        expect(a.locator('#workspace-snapshots option')).to_have_count(2)
        a.locator('#workspace-snapshots').select_option('f'*64)
        with a.expect_download() as archived:a.locator('#workspace-export-snapshot').click()
        assert json.loads(Path(archived.value.path()).read_text(encoding='utf-8'))==older
        inspect_source(a)
        expect(a.locator('#query-detail')).to_contain_text('218')
        a.locator('.working-editor textarea').first.fill('Uncommitted example for the UI review.')
        a.locator('.working-editor').screenshot(path=str(ROOT/'figures/rust-workspace-editor-review.png'))
        a.set_viewport_size({'width':320,'height':900})
        assert a.evaluate('document.documentElement.scrollWidth<=innerWidth')
        # A storage abort must not install the prepared candidate in Rust memory.
        isolated=browser.new_context()
        script=(ROOT/'almanac/query-worker.js').read_text(encoding='utf-8').replace('store.put(journal,bundleHash);',"reason='Simulated storage failure';tx.abort();")
        isolated.route('**/query-worker.js*',lambda r:r.fulfill(body=script,content_type='application/javascript'))
        failed=isolated.new_page();ready(failed);inspect_source(failed)
        edit(failed,'Failed save','Storage failure must leave the store unchanged.')
        expect(failed.locator('.working-editor [role="status"]')).to_contain_text('Simulated storage failure')
        assert browser_query(failed,{'collection':'working_records'})['total']==0
        failed.reload();failed.wait_for_function('window.oswLastQueryResult',timeout=60000)
        assert failed.evaluate('window.oswLastQueryResult.total')==0
        browser.close()
    print('PASS: durable revisions, cross-tab conflict, native replay/prepare, append-only import, archive, source preservation, mobile and storage abort')


if __name__=='__main__':main()
