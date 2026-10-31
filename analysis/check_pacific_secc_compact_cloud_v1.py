"""Cloud-only presentation overlay on the exact passed data/WASM artifact."""
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import threading
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.pytest_cache/pacific-secc-compact-map-cloud-v1'
REQUEST = 'research/pacific-secc-compact-map-request-v1.json'
PREFLIGHT = 'research/pacific-secc-compact-map-preflight-v1.json'
WORKFLOW = '.github/workflows/pacific-secc-compact-map-cloud-v1.yml'
ARTIFACT = 12750803966
ARTIFACT_BYTES = 96938937
ARTIFACT_SHA = '7fdaea073f3b27c96ca574099e81dd7dbab1fee57a74fb6b98b2186fe37c25cd'
MANIFEST = 'almanac/query-engine.manifest.json'


def read(path): return json.loads((ROOT / path).read_bytes())
def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes((json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode())


def controls():
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Exact cloud working-branch compact presentation push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1': raise ValueError('Single worker required: ' + key)
    request = read(REQUEST)
    if (request.get('schema') != 'osw.pacific-secc-compact-map-request.v1'
            or request.get('workflow') != WORKFLOW or request.get('execute') is not True
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0
            or request.get('cloud_artifact_restore_permitted') is not True or request.get('browser_permitted') is not True):
        raise ValueError('Exact compact presentation request is disabled or invalid')
    for key in ['native_wasm_build_permitted', 'scientific_source_processing_permitted',
                'working_branch_installation_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False: raise ValueError('Forbidden presentation permission: ' + key)
    if digest(ROOT / PREFLIGHT) != request['preflight_sha256']: raise ValueError('Changed compact presentation preflight')
    for path, sha in read(PREFLIGHT)['input_sha256'].items():
        if digest(ROOT / path) != sha: raise ValueError('Changed compact source: ' + path)
    phase = read('research/current-gap-delivery-phase.json')
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global phase must remain disabled')
    if read('research/pacific-secc-full-delivery-request-v1.json').get('execute') is not False:
        raise ValueError('Completed full delivery request must be disabled')
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or remote != head: raise ValueError('Exact current working-branch source required')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean checkout required before restoring cloud candidates')
    return head


def execute():
    head = controls()  # Refuse local execution before opening artifacts or starting servers.
    import pacific_secc_compact_map_v1 as compact
    if OUTPUT.exists(): raise ValueError('Prior compact cloud output exists')
    OUTPUT.mkdir(parents=True)
    passed = read('research/pacific-secc-full-delivery-result-v1.json')
    if (passed['status'] != 'PASS' or passed['browser_verified'] is not True
            or passed['source_commit'] != 'c16a0e71610e0137a94d1f213fe073aca404195a'
            or passed['logical_sha256'] != compact.LOGICAL or passed['wasm_sha256'] != compact.WASM_SHA):
        raise ValueError('Exact passed full delivery receipt required')
    archive_path = OUTPUT / 'candidate.zip'
    with archive_path.open('xb') as stream:
        subprocess.run(['gh', 'api', 'repos/giodl73-repo/OSW/actions/artifacts/' + str(ARTIFACT) + '/zip'],
            cwd=ROOT, stdout=stream, check=True, timeout=180)
    if archive_path.stat().st_size != ARTIFACT_BYTES or digest(archive_path) != ARTIFACT_SHA:
        raise ValueError('Passed full candidate artifact bytes differ')
    expected = passed['generated_sha256']
    with zipfile.ZipFile(archive_path) as archive:
        mapped = {}; prefixes = set()
        for item in archive.infolist():
            matches = [p for p in expected if item.filename == p or item.filename.endswith('/' + p)]
            if len(matches) != 1 or matches[0] in mapped: raise ValueError('Ambiguous or duplicate artifact member')
            path = matches[0]; prefix = item.filename[:-len(path)]
            if prefix.startswith('/') or '..' in Path(prefix).parts or '\\' in prefix:
                raise ValueError('Unsafe artifact packaging prefix')
            mapped[path] = item; prefixes.add(prefix)
        if set(mapped) != set(expected) or len(prefixes) != 1 or sum(r.file_size for r in archive.infolist()) > 350000000:
            raise ValueError('Exact finite reviewed candidate file inventory required')
        for path, item in mapped.items():
            target = (ROOT / path).resolve()
            if not target.is_relative_to(ROOT.resolve()): raise ValueError('Unsafe artifact path')
            raw = archive.read(item)
            if hashlib.sha256(raw).hexdigest() != expected[path]: raise ValueError('Changed reviewed candidate file')
            target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    if digest(ROOT / MANIFEST) != compact.BASE_ENGINE_SHA: raise ValueError('Exact candidate engine manifest required')
    parent = read(MANIFEST)
    updated = compact.overlay(parent, parent_manifest_sha=compact.BASE_ENGINE_SHA, control_commit=head)
    (ROOT / compact.PAGE).write_bytes(compact.support_page())
    (ROOT / compact.UI).write_bytes(compact.atlas_ui())
    (ROOT / compact.FIGURE).write_bytes(compact.compact_svg())
    write(ROOT / MANIFEST, updated)
    unchanged = {p: sha for p, sha in expected.items() if p not in {MANIFEST, compact.PAGE}}
    if any(digest(ROOT / p) != sha for p, sha in unchanged.items()): raise ValueError('Presentation changed reviewed scientific bytes')
    from playwright.sync_api import sync_playwright, expect
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = 'http://127.0.0.1:' + str(server.server_port)
    images, checks, errors = [], [], []
    def capture(locator, name):
        path = OUTPUT / name; locator.screenshot(path=str(path))
        images.append({'path': name, 'sha256': digest(path), 'bytes': path.stat().st_size})
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=['--renderer-process-limit=1'])
            context = browser.new_context(viewport={'width': 320, 'height': 900}, device_scale_factor=2)
            page = context.new_page(); page.set_default_timeout(180000)
            page.on('pageerror', lambda error: errors.append(str(error)))
            for width in [320, 390]:
                page.set_viewport_size({'width': width, 'height': 900})
                page.goto(base + '/' + compact.PAGE)
                page.wait_for_function('Array.from(document.images).every(el=>el.complete&&el.naturalWidth>0)')
                image = page.locator('figure img')
                if not image.evaluate('(el)=>el.currentSrc').endswith('/' + compact.FIGURE): raise ValueError('Phone did not select compact source')
                if page.evaluate('document.documentElement.scrollWidth>innerWidth'): raise ValueError('Phone page overflow')
                capture(page.locator('figure'), 'compact-support-' + str(width) + 'px.png')
                checks.append('support-compact-source-' + str(width) + 'px-dpr2')
                page.get_by_role('link', name='Explore this current in the global atlas').click()
                page.wait_for_function('(id)=>window.oswAtlasSnapshot?.working_reference_routes?.candidates.some(r=>r.id===id)', arg=compact.admission.query.ROUTE)
                expect(page.locator('#route-atlas-select')).to_have_value(compact.admission.query.TARGET)
                card = page.locator('section.route-card[id="' + compact.admission.query.ROUTE + '"]')
                image = card.locator('img.route-map'); image.scroll_into_view_if_needed()
                page.wait_for_function('(id)=>{const e=document.getElementById(id)?.querySelector("img.route-map");return e?.complete&&e.naturalWidth>0}', arg=compact.admission.query.ROUTE)
                if not image.evaluate('(el)=>el.currentSrc').endswith('/' + compact.FIGURE): raise ValueError('Phone atlas card did not select compact source')
                expect(card.get_by_role('link', name='Open route map at full size')).to_have_attribute('href', '../' + compact.SOURCE)
                capture(image, 'compact-atlas-card-' + str(width) + 'px.png')
                checks.append('atlas-card-compact-source-' + str(width) + 'px-dpr2')
            page.set_viewport_size({'width': 1100, 'height': 950})
            page.goto(base + '/' + compact.PAGE)
            page.wait_for_function('document.images[0]?.complete&&document.images[0].naturalWidth>0')
            if not page.locator('figure img').evaluate('(el)=>el.currentSrc').endswith('/' + compact.SOURCE): raise ValueError('Desktop detailed map changed')
            page.get_by_role('link', name='Open the reference record and query map').click()
            page.wait_for_function('(id)=>window.oswLastQueryResult?.rows?.[0]?.id===id', arg=compact.admission.query.ROUTE)
            if page.evaluate('window.oswLastQueryResult.total') != 1: raise ValueError('Compact page query link changed')
            checks.append('desktop-detailed-map-and-exact-query-link')
            if errors: raise ValueError('Browser errors: ' + repr(errors))
            browser.close()
    except Exception as error:
        if 'page' in locals():
            try: page.screenshot(path=str(OUTPUT / 'browser-failure.png'), timeout=15000)
            except Exception: pass
        write(OUTPUT / 'browser-failure.json', {'status': 'FAIL', 'error': str(error)[:2500], 'checks': checks, 'page_errors': errors})
        raise
    finally:
        server.shutdown(); server.server_close()
    if any(digest(ROOT / p) != sha for p, sha in unchanged.items()): raise ValueError('Browser changed reviewed scientific bytes')
    outputs = {p: digest(ROOT / p) for p in [MANIFEST, compact.PAGE, compact.UI, compact.FIGURE]}
    for path in outputs:
        destination = OUTPUT / 'artifact' / path; destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / path).read_bytes())
    write(OUTPUT / 'result.json', {'schema': 'osw.pacific-secc-compact-map-result.v1', 'status': 'PASS',
        'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'parent_candidate_engine_manifest_sha256': compact.BASE_ENGINE_SHA, 'generated_sha256': outputs,
        'logical_sha256': compact.LOGICAL, 'wasm_sha256': compact.WASM_SHA,
        'full_candidate_artifact_id': ARTIFACT, 'full_candidate_artifact_sha256': ARTIFACT_SHA,
        'unchanged_scientific_candidate_paths': unchanged, 'checks': checks, 'screenshots': images,
        'native_wasm_rebuilt': False, 'new_scientific_records': 0, 'visual_review_complete': False,
        'working_branch_installed': False, 'main_merged': False})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    try:
        if args.preflight_only: controls()
        else: execute()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            write(OUTPUT / 'failure.json', {'status': 'FAIL', 'error': str(error)[:4000], 'installed': False})
        raise
