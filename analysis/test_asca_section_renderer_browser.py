"""Exercise the section renderer from a Rust-generated scene (no provider requests)."""
import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main(scene_path):
    scene = json.loads(Path(scene_path).read_bytes())
    output = ROOT / '.pytest_cache/agulhas-act-source-review'
    output.mkdir(exist_ok=True)
    assert scene['kind'] == 'current_sections'
    assert len(scene['frames']) == 27
    assert scene['chronological_frame_interpolation'] is False
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width':1000, 'height':1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<base href="http://127.0.0.1:8788/almanac/"><style>body{font:16px system-ui;margin:12px}button,select{font:inherit}p{line-height:1.5}h4{margin-bottom:8px}</style><main id="charts"></main>')
        page.add_script_tag(path=str(ROOT/'almanac/current-section-charts.js'))
        page.evaluate('''scene => {window.stops=[];window.inspections=[];
            matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',()=>stops.forEach(stop=>stop()));
            window.render=()=>{
            document.querySelector('#charts').replaceChildren();
            oswCurrentSectionCharts.render(scene,(...args)=>inspections.push(args),document.querySelector('#charts'),stop=>stops.push(stop));
        };render();}''', scene)
        months = page.locator('[data-section-month]')
        assert months.locator('option').count() == 27
        expect(page.locator('[data-section-status]')).to_contain_text('partial month')
        assert page.locator('[data-section-field] svg').count() == 4
        assert page.get_by_role('button', name='Previous month').is_disabled()
        page.get_by_role('button', name='Next month').click()
        expect(page.locator('[data-section-status]')).to_contain_text('May 2016')
        expect(page.locator('[data-section-status]')).to_contain_text('37 source records')
        query_link = page.get_by_role('link', name='Inspect original timestamped profiles')
        from urllib.parse import urlparse, parse_qs
        query = json.loads(parse_qs(urlparse(query_link.get_attribute('href')).query)['source-q'][0])
        assert query['filters'] == [{'field':'record.year','op':'eq','value':2016}, {'field':'record.month','op':'eq','value':5}]
        page.get_by_role('button', name='Inspect selected monthly section').click()
        assert page.evaluate('inspections') == [['current_sections', 'section:agulhas:asca100m:2016-05']]
        # Offshore U is absent, so the drawn finite mean must stop before the array end.
        offshore = page.locator('[data-section-field="U"]')
        runs = offshore.locator('polyline').evaluate_all('(lines)=>lines.map(line=>line.getAttribute("points"))')
        assert runs and max(float(point.split(',')[0]) for run in runs for point in run.split()) < 655
        offshore.locator('summary').click()
        offshore.locator('select').select_option('600')
        expect(offshore.locator('details')).to_contain_text('mean unavailable')
        expect(offshore.locator('details')).to_contain_text('n=0 of 37')
        page.set_viewport_size({'width':320,'height':1000})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(output/'monthly-sections-mobile.png'), full_page=True)
        page.set_viewport_size({'width':1000,'height':1000})
        page.screenshot(path=str(output/'monthly-sections-desktop.png'), full_page=True)
        # Playback advances discrete source records and stops at the final frame.
        months.select_option(scene['frames'][-2]['id'])
        page.get_by_role('button', name='Play months').click()
        expect(months).to_have_value(scene['frames'][-1]['id'], timeout=5000)
        expect(page.get_by_role('button', name='Play months')).to_be_visible(timeout=5000)
        assert page.get_by_role('button', name='Next month').is_disabled()
        page.emulate_media(reduced_motion='reduce')
        assert page.get_by_role('button', name='Play months').is_disabled()
        page.get_by_role('button', name='Previous month').click()
        expect(months).to_have_value(scene['frames'][-2]['id'])
        page.evaluate('stops.forEach(stop=>stop())')
        assert not errors, errors
        browser.close()
    print('PASS: Rust scene / 27 frames / four fields / source filters / inspector / unavailable offshore U / mobile / discrete playback / reduced motion')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, required=True)
    main(parser.parse_args().scene)
