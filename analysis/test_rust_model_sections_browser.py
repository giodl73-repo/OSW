"""Hourly model source parity, query maps, frame/sample navigation and failures."""
import copy
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright, expect
from test_rust_query_browser import ROOT, BASE, CLI, native, browser_query
from test_rust_atlas_snapshot_browser import route_atlas_bundle

TIMELINE = 'research/norkyst-ingoy-2024-section-timeline.json'
MAPS = 'research/norkyst-ingoy-2024-map-frames.json'


def main():
    bundle = json.loads((ROOT / 'almanac/query-data.json').read_bytes())
    timeline = json.loads((ROOT / TIMELINE).read_bytes())
    maps = json.loads((ROOT / MAPS).read_bytes())
    frames = bundle['collections']['model_frames']
    samples = bundle['collections']['model_samples']
    assert len(frames) == 12 and len(samples) == 2292
    for index, source in enumerate(timeline['frames']):
        frame = frames[index]
        assert frame['date'] == source['date']
        assert frame['sample_time_utc'] == source['sample_time_utc']
        assert frame['receipt_sha256'] == source['receipt_sha256']
        assert frame['section'] == timeline['section']
        assert frame['map_figure_sha256'] == maps['frames'][index]['figure_sha256']
        assert frame['source_sha256'] == hashlib.sha256((ROOT / TIMELINE).read_bytes()).hexdigest()
        assert frame['current_length_km'] is None and frame['current_width_km'] is None
        receipt = json.loads((ROOT / source['receipt_file']).read_bytes())
        assert frame['field_units'] == {key: receipt['packing'][key]['units']
                                        for key in ['salinity', 'u_eastward', 'v_northward']}
        selected = [row for row in samples if row['model_frame_id'] == frame['id']]
        assert len(selected) == len(source['profile']) == 191
        for sample_index, (row, point) in enumerate(zip(selected, source['profile'])):
            assert {key: row[key] for key in point} == point
            assert row['sample_index'] == sample_index
            assert row['sample_time_utc'] == source['sample_time_utc']
            assert row['source_path'] == f'/frames/{index}/profile/{sample_index}'
            assert row['field_values_available'] == all(point[key] is not None for key in
                                                        ['salinity', 'u_eastward', 'v_northward'])
            assert row['width_rank_eligible'] is False
            assert row['annual_extrema_eligible'] is False
            assert row['state_footprint_join_eligible'] is False
    cases = [
        {'collection': 'model_frames', 'sort': {'field': 'date'}, 'limit': 4},
        {'collection': 'model_samples', 'filters': [{'field': 'month', 'op': 'eq', 'value': 1}],
         'sort': {'field': 'sample_index'}, 'limit': 7},
        {'collection': 'model_samples', 'filters': [{'field': 'u_eastward', 'op': 'lt', 'value': 0}],
         'sort': {'field': 'id'}, 'limit': 7},
        {'collection': 'model_samples', 'sort': {'field': 'id'}, 'offset': 2285, 'limit': 7},
        {'collection': 'model_samples', 'filters': [{'field': 'field_values_available', 'op': 'eq', 'value': False}],
         'limit': 7},
    ]
    expected_results = []
    for query in cases:
        expected = list(bundle['collections'][query['collection']])
        for predicate in query.get('filters', []):
            key, value = predicate['field'], predicate['value']
            expected = [row for row in expected if row[key] == value] if predicate['op'] == 'eq' else [
                row for row in expected if row[key] is not None and row[key] < value]
        expected.sort(key=lambda row: row[query.get('sort', {'field': 'id'})['field']])
        result = native(query)
        assert result['ok'], result
        assert result['total'] == len(expected)
        offset = query.get('offset', 0)
        assert result['rows'] == expected[offset:offset + query['limit']]
        scene = result['map_scene']
        assert scene['mapped_objects'] == len(expected)
        assert {f['entity_id'] for f in scene['features']} == {row['id'] for row in expected}
        assert scene['inspection_collection'] == query['collection']
        assert 'not observations, monthly means' in scene['scope']
        assert all(f['primitive']['kind'] != 'polygon' for f in scene['features'])
        expected_results.append(result)

    mutations = [
        ('field', lambda b: b['collections']['model_samples'][0].update(salinity=999)),
        ('position', lambda b: b['collections']['model_samples'][0].update(coordinates_lon_lat=[24, 72])),
        ('hour', lambda b: b['collections']['model_samples'][0].update(sample_time_utc='2024-01-15T00:00:00Z')),
        ('dimension', lambda b: b['collections']['model_frames'][0].update(current_width_km=30)),
        ('inventory', lambda b: b['collections']['model_samples'].pop()),
        ('parent', lambda b: b['collections']['model_samples'][0].update(model_frame_id=frames[1]['id'])),
        ('receipt', lambda b: b['manifest']['atlas_receipts'].pop(MAPS)),
    ]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'invalid.json'
        for name, mutate in mutations:
            changed = copy.deepcopy(bundle)
            mutate(changed)
            path.write_text(json.dumps(changed, ensure_ascii=False), encoding='utf-8')
            run = subprocess.run([str(CLI), str(path), '-'], input='{}',
                                 capture_output=True, text=True, encoding='utf-8')
            assert run.returncode == 2 and not run.stdout, (name, run.stderr)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('OSW_TEST_BROWSER'))
        page = browser.new_page(viewport={'width': 1280, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.route('**/research/*.json', lambda route: route.abort())
        page.goto(BASE)
        page.wait_for_function('window.oswLastQueryResult', timeout=90000)
        for query, expected in zip(cases, expected_results):
            assert browser_query(page, query) == expected
            assert page.locator('#query-map-features > *').count() == expected['total']
        frame_query = cases[0]
        assert browser_query(page, frame_query) == expected_results[0]
        page.locator('#query-rows button').first.click()
        card = page.locator('.model-section-card')
        expect(card).to_contain_text('Hourly hindcast model section at 10 m')
        expect(card).to_contain_text('2024-01-15T12:00:00Z')
        card.locator('img').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelector(".model-section-card img")?.naturalWidth>0', timeout=30000)
        page.get_by_role('link', name='Query this frame’s 191 section samples').click()
        page.wait_for_function('window.oswLastQueryResult?.collection==="model_samples" && window.oswLastQueryResult?.total===191', timeout=90000)
        mark = page.locator('#query-map-features > *').first
        mark.focus()
        mark.press('Enter')
        expect(card).to_contain_text('Eastward velocity component (m/s)')
        expect(card).to_contain_text('0.024102')
        page.get_by_role('button', name='Inspect source frame, units and map').click()
        expect(card).to_contain_text('191 of 191')
        page.get_by_role('link', name='Query all NorKyst source frames').click()
        page.wait_for_function('window.oswLastQueryResult?.collection==="model_frames" && window.oswLastQueryResult?.total===12', timeout=90000)
        share = page.locator('#query-share').get_attribute('href')
        page.goto(share)
        page.wait_for_function('window.oswLastQueryResult?.collection==="model_frames" && window.oswLastQueryResult?.total===12', timeout=90000)
        assert json.loads(page.locator('#query-json').input_value())['filters'] == [
            {'field': 'current_id', 'op': 'eq', 'value': 'norwegian-coastal'}]
        page.set_viewport_size({'width': 320, 'height': 900})
        page.locator('#query-rows button').first.click()
        expect(card).to_be_visible()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.locator('#query-detail').screenshot(path=str(ROOT / 'figures/rust-model-section-query-review.png'))
        assert not errors, errors
        changed = copy.deepcopy(bundle)
        changed['collections']['model_frames'][0]['current_width_km'] = 30
        failed = browser.new_page()
        route_atlas_bundle(failed, changed)
        failed.goto(BASE)
        expect(failed.locator('#query-status')).to_contain_text('Model query projection disagrees', timeout=90000)
        assert failed.locator('#query-rows tr').count() == 0
        assert failed.evaluate('window.oswLastQueryResult') is None
        missing = browser.new_page()
        missing.route('**/query-data.json', lambda route: route.fulfill(status=503, body='Unavailable'))
        missing.goto(BASE)
        expect(missing.locator('#query-status')).to_have_class('error', timeout=90000)
        assert missing.locator('#query-rows tr').count() == 0
        browser.close()
    print('PASS: 12 hourly model frames and 2292 source samples, seven loader rejections, native/WASM maps and pagination, keyboard frame/sample navigation, saved filters, source scopes, mobile and unavailable data')


if __name__ == '__main__':
    main()
