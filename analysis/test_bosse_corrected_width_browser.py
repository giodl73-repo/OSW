"""Corrected branch width and raw records: source queries, UI and frozen rejection."""
import copy,gzip,hashlib,json,os,subprocess,tempfile
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI,ROOT

RECORD='research/norwegian-front-bosse-2019-corrected-width-record.json'
def main():
    payload=gzip.decompress((ROOT/'almanac/index-data.json.gz').read_bytes())
    query={'document':RECORD,'pointer':'','limit':10}
    gliders={'document':'research/norwegian-front-glider-source-alignment.json','pointer':'/missions/0/DAC_records','limit':20}
    with tempfile.TemporaryDirectory(dir=ROOT/'.pytest_cache') as temp:
        packet=Path(temp)/'index.json';packet.write_bytes(payload)
        def native(q):return json.loads(subprocess.check_output([str(CLI),'--index',str(packet),'-'],input=json.dumps(q),encoding='utf-8'))
        # The individual record is an object; query its named field values.
        query['pointer']='/sampling_context/seasonal_composite_months'
        expected=native(query);raw=native(gliders);assert raw['total']==673
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ['OSW_TEST_BROWSER']);page=browser.new_page(viewport={'width':320,'height':1000});errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8788/almanac/reference-routes.html#inventory-addition-norwegian-atlantic-front')
            card=page.locator('#inventory-addition-norwegian-atlantic-front')
            expect(card).to_contain_text('38 ± 2 km',timeout=90000);expect(card).to_contain_text('width-specific interpretation awaits')
            assert card.locator('.proposed-width-chart circle').count()==1
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            card.locator('.proposed-width-chart').evaluate('(e)=>e.scrollIntoView({block:"start"})')
            card.locator('figure').screenshot(path=str(ROOT/'figures/bosse-corrected-front-width-review.png'))
            card.get_by_role('link',name='Query retained glider current records').click()
            page.wait_for_function('window.oswSourceQueryResult?.total===673',timeout=90000)
            assert page.evaluate('window.oswSourceQueryResult')==raw
            page.goto('http://127.0.0.1:8788/almanac/query.html?source-q='+quote(json.dumps(query)))
            page.wait_for_function('window.oswSourceQueryResult',timeout=90000)
            assert page.evaluate('window.oswSourceQueryResult')==expected
            assert not errors,errors
            # Rebind a main-store proposal receipt coherently; the compiled scope must reject it.
            bad=json.loads((ROOT/'almanac/query-data.json').read_bytes());source='research/ocean-current-inventory-expansion-candidates.json'
            receipt=bad['manifest']['atlas_receipts'][source];doc=json.loads(receipt['source_json'])
            owner=next(r for r in doc['entries'] if r['proposed_id']=='norwegian-atlantic-front')
            next(r for r in owner['width_evidence'] if r['id']=='norwegian-atlantic-front-bosse-2019-corrected-width')['author_reported_error_km']=20
            receipt['source_json']=json.dumps(doc);receipt['source_sha256']=hashlib.sha256(receipt['source_json'].encode()).hexdigest();bad['manifest']['input_sha256'][source]=receipt['source_sha256']
            badbytes=json.dumps(bad).encode();packet.write_bytes(badbytes)
            run=subprocess.run([str(CLI),str(packet),'--atlas'],capture_output=True,text=True,encoding='utf-8')
            assert run.returncode==2 and 'Corrected Norwegian front' in run.stderr,run.stderr
            page.route('**/bosse-coherent.json',lambda route:route.fulfill(body=badbytes,content_type='application/json'))
            result=page.evaluate('''async()=>{const {instance}=await WebAssembly.instantiate(await (await fetch('query-engine.wasm')).arrayBuffer(),{});const e=instance.exports;const b=new Uint8Array(await(await fetch('bosse-coherent.json')).arrayBuffer());const p=e.osw_alloc(b.length);new Uint8Array(e.memory.buffer,p,b.length).set(b);e.osw_load(p,b.length);let result=JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));if(result.ok){e.osw_atlas();result=JSON.parse(new TextDecoder().decode(new Uint8Array(e.memory.buffer,e.osw_result_ptr(),e.osw_result_len())));}e.osw_dealloc(p,b.length);return result;}''')
            assert result['ok'] is False and 'Corrected Norwegian front' in result['error'],result
            browser.close()
    print('PASS: corrected 38 +/- 2 source scope, branch card/mobile, 673 raw records, native/WASM source queries and coherent uncertainty rewrite rejection')
if __name__=='__main__':main()
