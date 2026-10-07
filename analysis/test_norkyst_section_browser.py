"""Verify the new sampled-profile playback and mobile data view."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os,json,subprocess,tempfile
from threading import Thread
from playwright.sync_api import sync_playwright,expect
from test_rust_query_browser import CLI
from test_rust_atlas_snapshot_browser import route_atlas_bundle

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args): pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            b=p.chromium.launch(headless=True,executable_path=os.environ.get('OSW_TEST_BROWSER'))
            page=b.new_page()
            page.set_default_timeout(90000)
            errors=[]
            direct=[]
            page.route('**/research/*.json',lambda r:(direct.append(r.request.url),r.fulfill(status=503,body='Direct reads disabled'))[-1])
            page.on('pageerror',lambda error:errors.append(str(error)))
            url=f'http://127.0.0.1:{server.server_port}/almanac/norkyst-section.html'
            page.goto(url+'?date=2024-06-15',wait_until='networkidle')
            expect(page.locator('#section-month option')).to_have_count(12,timeout=90000)
            expect(page.locator('#section-month')).to_have_value('5')
            native=json.loads(subprocess.check_output([str(CLI),str(ROOT/'almanac/query-data.json'),'--atlas'],encoding='utf-8'))
            assert page.evaluate('window.oswCheckedAtlasSnapshot')==native
            assert '12 pinned hourly' in page.locator('#section-status').inner_text()
            assert 'Ingøy' in page.locator('h1').inner_text()
            assert 'Â' not in page.locator('body').inner_text()
            january=page.locator('#section-chart path').first.get_attribute('d')
            for i in range(12):
                page.locator('#section-month').select_option(str(i))
                assert f'2024-{i+1:02d}-15T12:00:00Z' in page.locator('#section-time').inner_text()
                assert page.url.endswith(f'?date=2024-{i+1:02d}-15')
                assert page.locator('#section-chart path').count()==3
                page.wait_for_function("document.getElementById('section-map').dataset.sampleTime === document.getElementById('section-month').selectedOptions[0].textContent + 'T12:00:00Z'")
                assert not page.locator('#section-map').is_hidden()
                assert f'norkyst-ingoy-map-2024-{i+1:02d}-15.svg' in page.locator('#section-map').get_attribute('src')
                assert page.locator('#section-map').evaluate('el => el.complete && el.naturalWidth > 0')
                assert page.locator('#section-rows tr').count()==191
                assert f'2024{i+1:02d}15.nc.ascii' in page.locator('#section-source a').get_attribute('href')
            assert page.locator('#section-chart path').first.get_attribute('d')!=january
            page.locator('#section-month').select_option('0')
            page.locator('#section-play').click()
            page.wait_for_function("document.getElementById('section-month').value === '1'")
            page.locator('#section-play').click()
            page.wait_for_timeout(2350)
            assert page.locator('#section-month').input_value()=='1'
            page.locator('#section-play').click()
            page.locator('#section-month').select_option('5')
            assert page.locator('#section-play').inner_text()=='Play snapshots'
            page.locator('#section-play').click()
            page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'))")
            assert page.locator('#section-play').inner_text()=='Play snapshots'
            page.emulate_media(reduced_motion='reduce')
            page.set_viewport_size({'width':320,'height':900})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.locator('summary').click()
            assert '34.' in page.locator('#section-rows').inner_text()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert page.locator('a[href="https://creativecommons.org/licenses/by/4.0/"]').count()==1
            restored=b.new_page();restored.goto(page.url)
            expect(restored.locator('#section-month')).to_have_value('5',timeout=90000)
            assert '2024-06-15T12:00:00Z' in restored.locator('#section-time').inner_text()
            for kind in ['load_failure','missing_maps']:
                other=b.new_page();other.on('pageerror',lambda e:errors.append(str(e)))
                if kind=='load_failure':other.route('**/query-data.json',lambda r:r.fulfill(status=503,body='Unavailable'))
                else:
                    bundle=json.loads((ROOT/'almanac/query-data.json').read_bytes())
                    del bundle['manifest']['atlas_receipts']['research/norkyst-ingoy-2024-map-frames.json'];route_atlas_bundle(other,bundle)
                    # Model frame/sample collections require this receipt at store load.
                    # Its absence rejects the store before the page's optional-view guard.
                    with tempfile.TemporaryDirectory() as directory:
                        packet=Path(directory)/'missing-maps.json';packet.write_text(json.dumps(bundle),encoding='utf-8')
                        rejected=subprocess.run([str(CLI),str(packet),'-'],input='{}',capture_output=True,text=True)
                        assert rejected.returncode==2 and not rejected.stdout and 'Missing atlas source bytes' in rejected.stderr,rejected.stderr
                other.goto(url)
                expect(other.locator('#section-status')).to_contain_text('HTTP 503' if kind=='load_failure' else 'Missing atlas source bytes',timeout=90000)
                assert other.locator('#section-month').is_disabled() and other.locator('#section-play').is_disabled()
                assert other.locator('#section-map').is_hidden() and other.locator('#section-rows tr').count()==0
            assert not direct and not errors,(direct,errors)
            b.close()
            print('OK: 12 frames, values, playback/pause/manual/hidden controls, source/license and mobile table')
    finally:
        server.shutdown();server.server_close()


if __name__=='__main__':main()
