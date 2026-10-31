"""One cloud browser review of the exact saved South Java generated candidate."""
import argparse
import functools
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import zipfile

import check_south_java_model_layer_cloud_v1 as native
import south_java_layer_query_v1 as context
import south_java_model_browser_custody_v1 as custody

ROOT = native.ROOT
OUTPUT = ROOT / '.pytest_cache/south-java-model-browser-v1'
REQUEST = 'research/south-java-model-browser-request-v1.json'
PREFLIGHT = 'research/south-java-model-browser-preflight-v1.json'
RESULT = 'research/south-java-model-delivery-result-v1.json'
REVIEW = 'research/south-java-model-delivery-execution-review-v1.json'


def controls(env):
    native.cloud_environment(env)  # Local refusal precedes data and browser imports.
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    if head != env.get('GITHUB_SHA'):
        raise ValueError('Exact cloud source checkout required')
    request = json.loads((ROOT / REQUEST).read_bytes())
    if (request.get('schema') != 'osw.south-java-model-browser-request.v1'
            or request.get('execution_permitted') is not True
            or request.get('browser_automation_permitted') is not True
            or type(request.get('max_cloud_jobs')) is not int or request['max_cloud_jobs'] != 1
            or type(request.get('max_heavy_local_jobs')) is not int or request['max_heavy_local_jobs'] != 0):
        raise ValueError('Single cloud browser stage is disabled')
    for key in ['local_browser_permitted', 'installed_assets_change_permitted',
                'scientific_source_processing_permitted', 'native_build_permitted',
                'wasm_build_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden browser-stage permission: ' + key)
    raw = (ROOT / PREFLIGHT).read_bytes()
    if native.digest(raw) != request['preflight_sha256']:
        raise ValueError('Changed browser preflight')
    for path, expected in json.loads(raw)['input_sha256'].items():
        if custody.digest(ROOT / path) != expected:
            raise ValueError('Changed browser-stage input: ' + path)
    for path, count in [('research/eacc-coastal-reference-extent-preflight-v1.json', 83),
                        ('research/current-local-extent-query-check-preflight-v2.json', 23),
                        ('research/current-local-extent-ui-preflight-v1.json', 20),
                        (native.PREFLIGHT, 26), ('research/south-java-saved-wasm-preflight-v1.json', 12),
                        ('research/south-java-model-delivery-preflight-v1.json', 24)]:
        pins = json.loads((ROOT / path).read_bytes())['input_sha256']
        if len(pins) != count:
            raise ValueError('Changed preserved source inventory')
        for name, expected in pins.items():
            if custody.digest(ROOT / name) != expected:
                raise ValueError('Changed preserved source: ' + name)
    for path in [native.REQUEST, 'research/south-java-saved-wasm-request-v1.json',
                 'research/south-java-model-delivery-request-v1.json']:
        if json.loads((ROOT / path).read_bytes())['execution_permitted'] is not False:
            raise ValueError('Earlier computation/export request must be disabled')
    phase = json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Scientific source-processing hold must remain')


def api(path):
    raw = subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/' + path,
                                   '-H', 'Cache-Control: no-cache'])
    if len(raw) > 1048576:
        raise ValueError('Unexpected workflow metadata size')
    return json.loads(raw)


def restore():
    review = json.loads((ROOT / REVIEW).read_bytes())
    result = json.loads((ROOT / RESULT).read_bytes())
    if (review['run_id'] != 40150485982 or review['run_attempt'] != 2
            or result['status'] != 'PASS' or result['native_wasm_queries_equal'] != 11
            or result['source_commit'] != review['executed_source_commit']):
        raise ValueError('Verified final-candidate receipts required')
    run = api('actions/runs/' + str(review['run_id']))
    if (run['status'] != 'completed' or run['conclusion'] != 'success'
            or run['head_sha'] != review['executed_source_commit'] or run['run_attempt'] != 2):
        raise ValueError('Source export run no longer matches verified identity')
    artifact = review['generated_artifact']
    info = api('actions/artifacts/' + str(artifact['id']))
    if (info['expired'] or info['size_in_bytes'] != artifact['bytes']
            or info['digest'] != 'sha256:' + artifact['sha256']
            or info['workflow_run']['id'] != review['run_id']):
        raise ValueError('Saved generated artifact custody differs')
    if shutil.disk_usage(ROOT).free < 3221225472:
        raise ValueError('At least3GiB free cloud disk required')
    archive = OUTPUT / 'saved-generated.zip'
    with archive.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(artifact['id']) + '/zip'],
                       stdout=stream, check=True, timeout=300)
    if archive.stat().st_size != artifact['bytes'] or custody.digest(archive) != artifact['sha256']:
        raise ValueError('Full saved generated ZIP digest differs')
    with zipfile.ZipFile(archive) as saved:
        files = custody.members(saved.infolist(), result['artifact_paths'])
        for info in files:
            target = ROOT / info.filename
            if target.is_symlink() or not target.resolve().is_relative_to(ROOT):
                raise ValueError('Saved member leaves isolated checkout')
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix('.browser-restore-tmp')
            with saved.open(info) as source, temporary.open('xb') as destination:
                shutil.copyfileobj(source, destination, length=1048576)
            if temporary.stat().st_size != info.file_size:
                raise ValueError('Incomplete restored member')
            temporary.replace(target)
    return {**custody.verify(ROOT, result), 'full_generated_archive_sha256': artifact['sha256'],
            'source_run_id': review['run_id'], 'source_run_attempt': 2,
            'generated_artifact_id': artifact['id']}


def run_browser(proof):
    from playwright.sync_api import sync_playwright, expect
    contract = json.loads((ROOT / context.FILE).read_bytes())
    rows = contract['collections']
    output = {'schema': 'osw.south-java-model-browser-result.v1', 'status': 'RUNNING',
              'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
              'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'], 'custody': proof,
              'cards': [], 'screenshots': [], 'source_documents': [], 'keyboard_checks': [],
              'browser_verified': False, 'visual_review_complete': False,
              'working_branch_installed': False, 'new_physical_dimensions_admitted': 0}
    def save():
        (OUTPUT / 'result.json').write_text(json.dumps(output, indent=2) + '\n')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    phase = 'launch'
    errors, originals = [], []
    save()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
        page = browser.new_page(viewport={'width': 1100, 'height': 950})
        page.set_default_timeout(180000)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda req: originals.append(req.url) if req.url.split('?')[0].endswith(('.pdf', '.zip', '.nc', '.npz')) else None)
        def query(value):
            page.locator('#query-advanced').evaluate('(el)=>el.open=true')
            page.locator('#query-json').fill(json.dumps(value))
            page.evaluate('window.oswLastQueryResult=null')
            page.locator('#query-run-json').click()
            page.wait_for_function('window.oswLastQueryResult', timeout=180000)
            return page.evaluate('window.oswLastQueryResult')
        def screenshot(locator, name):
            path = OUTPUT / name
            locator.screenshot(path=str(path))
            output['screenshots'].append({'path': name, 'sha256': custody.digest(path), 'bytes': path.stat().st_size})
            save()
        try:
            phase = 'dashboard-navigation'
            page.goto(base + '/almanac/dashboard.html')
            page.wait_for_function('window.oswDashboardSelection', timeout=180000)
            page.locator('#dashboard-card-view').click()
            page.locator('#dashboard-search').fill('South Java')
            card = page.locator('article[data-id="current:south-java"]')
            expect(card).to_be_visible()
            card.locator('details').evaluate('(el)=>el.open=true')
            link = card.get_by_role('link').filter(has_text='analysis layers').first
            link.focus(); expect(link).to_be_focused(); link.press('Enter')
            page.wait_for_function('window.oswLastQueryResult?.collection === "current_model_analysis_layers"', timeout=180000)
            output['keyboard_checks'].append('dashboard-to-analysis-layer-query')
            for name, label in [(context.LAYERS, 'Model study analysis-layer definitions'),
                                (context.DEPTHS, 'Model mean-flow depth context')]:
                expect(page.locator('#query-collection option[value="' + name + '"]')).to_contain_text(label)
            ordinary = query({'collection': 'objects', 'record_type': 'named_current', 'limit': 1})
            assert ordinary['total'] == 106
            output['ordinary_current_inventory'] = ordinary['total']
            owner_href = facts_href = None
            for collection in [context.LAYERS, context.DEPTHS]:
                actual = query({'collection': collection, 'filters': [{'field': 'related_current_id', 'op': 'eq', 'value': context.TARGET}],
                                'sort': {'field': 'id'}, 'limit': 100})
                expected = sorted(rows[collection], key=lambda row: row['id'])
                assert context.encoded(actual['rows']) == context.encoded(expected)
                for index, row in enumerate(expected):
                    phase = 'card-' + row['id']
                    page.locator('#query-rows tr').nth(index).get_by_role('button').first.click()
                    detail = page.locator('.model-layer-context-card')
                    expect(detail).to_contain_text(row['source_locator'])
                    expect(detail).to_contain_text('annual ranges and uncertainty remain unknown')
                    expect(detail).to_contain_text('1990–2003')
                    if row['entity_id'] is None:
                        expect(detail).to_contain_text('Separate undercurrent context')
                    if 'depth_cap_m' in row:
                        expect(detail).to_contain_text('exact edge depth is unresolved')
                    image = detail.locator('img')
                    expect(image).to_have_attribute('src', base + '/' + context.FIGURE)
                    image.evaluate('(img)=>img.loading="eager"')
                    page.wait_for_function('document.querySelector(".model-layer-context-card img")?.complete && document.querySelector(".model-layer-context-card img")?.naturalWidth > 0')
                    owner_href = detail.get_by_role('link', name='South Java current record', exact=True).get_attribute('href')
                    facts_href = detail.get_by_role('link', name='Reviewed source facts', exact=True).get_attribute('href')
                    for width in [320, 390]:
                        page.set_viewport_size({'width': width, 'height': 844})
                        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                        assert detail.evaluate('el=>el.scrollWidth <= el.clientWidth + 1')
                        screenshot(detail, row['id'] + '-' + str(width) + 'px.png')
                    page.set_viewport_size({'width': 1100, 'height': 950})
                    output['cards'].append({'id': row['id'], 'collection': collection, 'widths_px': [320, 390],
                                             'entity_id': row['entity_id'], 'diagram_loaded': True})
                    save()
            phase = 'publication-keyboard'
            publication = page.get_by_role('button', name='Publication and source details', exact=True)
            publication.focus(); expect(publication).to_be_focused(); publication.press('Enter')
            paper = next(row for row in rows['sources'] if row['id'] == context.PAPER)
            expect(page.locator('#query-detail')).to_contain_text(paper['title'])
            expect(page.locator('#query-detail a[href="' + paper['url'] + '"]')).to_have_count(1)
            output['keyboard_checks'].append('card-to-publication')
            phase = 'related-owner-navigation'
            page.goto(owner_href)
            page.wait_for_function('window.oswLastQueryResult?.rows?.[0]?.id === "current:south-java"')
            owner = page.evaluate('window.oswLastQueryResult.rows[0]')
            assert owner['capabilities']['model_analysis_layers'] == 1 and owner['capabilities']['model_depth_context'] == 2
            output['related_owner_navigation_verified'] = True
            phase = 'indexed-source-navigation'
            page.goto(facts_href)
            page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
            for path in sorted(__import__('south_java_model_delivery_v1').DOCUMENTS):
                page.locator('#source-query-json').evaluate('(el)=>el.closest("details").open=true')
                page.locator('#source-query-json').fill(json.dumps({'document': path, 'pointer': '', 'limit': 500, 'offset': 0}))
                page.evaluate('window.oswSourceQueryResult=null')
                page.locator('#source-query-run-json').click()
                page.wait_for_function('window.oswSourceQueryResult', timeout=180000)
                source = page.evaluate('window.oswSourceQueryResult')
                raw = (ROOT / path).read_bytes()
                assert source['source_sha256'] == native.digest(raw)
                assert {row['source_key']: row['record'] for row in source['rows']} == json.loads(raw)
                output['source_documents'].append({'path': path, 'sha256': native.digest(raw)})
            phase = 'preserved-model-sample-card'
            query({'collection': 'model_samples', 'limit': 1})
            page.locator('#query-rows tr').first.get_by_role('button').first.click()
            expect(page.locator('.model-section-card')).to_contain_text('Hourly hindcast model section at 10 m')
            output['prior_model_sample_card_verified'] = True
            assert not errors, errors
            assert not originals, originals
            output.update(status='PASS', browser_verified=True, errors=errors, original_downloads=originals)
        except Exception as error:
            output.update(status='FAIL', phase=phase, error=str(error)[:1500], url=page.url, errors=errors, original_downloads=originals)
            page.screenshot(path=str(OUTPUT / 'failure.png'))
            raise
        finally:
            save(); browser.close(); server.shutdown(); server.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-browser', action='store_true')
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    if not args.cloud_browser:
        parser.error('Explicit cloud browser stage required; no artifact or browser opened')
    controls(dict(os.environ))
    if args.preflight_only:
        print('Browser source preflight passed'); return
    OUTPUT.mkdir(parents=True, exist_ok=False)
    try:
        proof = restore()
        (OUTPUT / 'custody.json').write_text(json.dumps(proof, indent=2) + '\n')
        run_browser(proof)
    except Exception as error:
        (OUTPUT / 'failure.json').write_text(json.dumps({'status': 'FAIL',
            'source_commit': os.environ['GITHUB_SHA'], 'run_id': os.environ['GITHUB_RUN_ID'],
            'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
            'error': (type(error).__name__ + ': ' + str(error))[:1500],
            'working_branch_installed': False, 'scientific_source_processing': False}, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
