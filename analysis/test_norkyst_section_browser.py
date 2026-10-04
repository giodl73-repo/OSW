"""Verify the new sampled-profile playback and mobile data view."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args): pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
    Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
            page=b.new_page()
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/almanac/norkyst-section.html',wait_until='networkidle')
            assert page.locator('#section-month option').count()==12
            assert '12 pinned hourly' in page.locator('#section-status').inner_text()
            january=page.locator('#section-chart path').first.get_attribute('d')
            for i in range(12):
                page.locator('#section-month').select_option(str(i))
                assert f'2024-{i+1:02d}-15T12:00:00Z' in page.locator('#section-time').inner_text()
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
            assert not errors,errors
            b.close()
            print('OK: 12 frames, values, playback/pause/manual/hidden controls, source/license and mobile table')
    finally:
        server.shutdown();server.server_close()


if __name__=='__main__':main()
