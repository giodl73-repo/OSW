"""Bounded cloud-only selection of installed WICC metadata; never builds or installs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/wicc-reference-parent-request-v1.json'
PREFLIGHT = 'research/wicc-reference-parent-preflight-v1.json'
WORKFLOW = '.github/workflows/wicc-reference-parent-cloud-v1.yml'
OUT = ROOT / '.pytest_cache/wicc-reference-parent-v1'
OWNER = 'current:west-india-coastal'
ENGINE = 'bfd24fac7c745b3891136fca77a1f6c1ac8a2a55923abc0f74dd30aaa52870e5'
LOGICAL = 'bb343f71dd42ba40dcc688aa4209c72a884f909f31d046e2158d14ea994bfc24'
FORBIDDEN = ['index_load_permitted', 'native_wasm_build_permitted', 'browser_permitted',
             'ocean_field_processing_permitted', 'working_branch_installation_permitted',
             'local_bulk_sync_permitted', 'main_merge_permitted']
PAPERS = {
    'shetye_1991': ('10.1016/0198-0149(91)90087-v', 'https://www.sciencedirect.com/science/article/pii/019801499190087V'),
    'shetye_2008': ('10.1029/2008jc004874', 'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2008JC004874'),
}


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def doi(value):
    value = str(value).strip().lower()
    for prefix in ['https://doi.org/', 'http://doi.org/', 'https://dx.doi.org/', 'http://dx.doi.org/', 'doi:']:
        if value.startswith(prefix):
            return value[len(prefix):].strip().rstrip('/')
    return value.rstrip('/')


def url(value):
    value = urlsplit(str(value).strip())
    return (value.hostname or '').lower(), value.path.rstrip('/')


def publications(rows):
    ids = [r.get('id') for r in rows]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Unique nonempty installed source IDs required')
    selected, resolutions = {}, {}
    for key, (identifier, primary) in PAPERS.items():
        matches = [r for r in rows if doi(r.get('doi', '')) == identifier
                   or doi(r.get('url', '')) == identifier or url(r.get('url', '')) == url(primary)]
        if any(r.get('doi') and doi(r['doi']) != identifier for r in matches):
            raise ValueError('Conflicting publication DOI/URL: ' + key)
        selected[key] = matches
        resolutions[key] = {'status': 'MISSING' if not matches else 'UNIQUE_EXISTING' if len(matches) == 1 else 'RECONCILIATION_REQUIRED',
                            'matching_source_ids': [r['id'] for r in matches]}
    return selected, resolutions


def controls():
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Exact cloud working-branch audit required before packet access')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU and nice15 required')
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('Single worker required: ' + key)
    request = read(REQUEST)
    expected = {'schema': 'osw.wicc-reference-parent-request.v1', 'workflow': WORKFLOW,
                'execute': True, 'cloud_parent_packet_read_permitted': True,
                'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        if type(request.get(key)) is not type(value) or request[key] != value:
            raise ValueError('Disabled or changed audit request: ' + key)
    if any(request.get(key) is not False for key in FORBIDDEN):
        raise ValueError('Unrelated audit permission enabled')
    phase = read('research/current-gap-delivery-phase.json')
    if phase['phase'] != 'source-review-only-v1' or phase['heavy_work_permitted'] is not False:
        raise ValueError('Global source-review phase must remain disabled')
    if sha((ROOT / PREFLIGHT).read_bytes()) != request['preflight_sha256']:
        raise ValueError('Changed frozen preflight')
    for path, pin in read(PREFLIGHT)['input_sha256'].items():
        if sha((ROOT / path).read_bytes()) != pin:
            raise ValueError('Changed frozen source: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD']).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api', 'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ['GITHUB_SHA'] or remote != head:
        raise ValueError('Stale checkout refused')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain']).strip():
        raise ValueError('Clean audit checkout required')
    return head


def audit():
    head = controls()
    # Import and read installed payloads only after all cloud and source gates.
    from query_packet import descriptors, read_bundle_bytes
    manifest_raw = (ROOT / 'almanac/query-engine.manifest.json').read_bytes()
    if sha(manifest_raw) != ENGINE:
        raise ValueError('Exact installed EACC-inclusive engine required')
    manifest = json.loads(manifest_raw)
    descriptor_raw = (ROOT / 'almanac/query-data.json').read_bytes()
    descriptor = json.loads(descriptor_raw)
    parts = descriptors(descriptor)
    if (manifest['sha256']['almanac/query-data.json'] != sha(descriptor_raw)
            or descriptor['logical_sha256'] != LOGICAL or descriptor['logical_byte_length'] != 190553938):
        raise ValueError('Installed parent descriptor mismatch')
    if any(manifest['sha256'].get('almanac/' + p['path']) != p['sha256'] for p in parts):
        raise ValueError('Installed part receipt mismatch')
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if sha(raw) != LOGICAL:
        raise ValueError('Installed logical packet mismatch')
    bundle = json.loads(raw)
    del raw
    collections = bundle['collections']
    if len(collections['reference_routes']) != 82 or len(collections['widths']) != 176:
        raise ValueError('Installed route or width inventory differs')
    selected = {}
    for key, collection, field in [('owner', 'objects', 'id'), ('entity', 'entities', 'id'),
                                    ('planning_decision', 'route_decisions', 'entity_id')]:
        rows = [r for r in collections[collection] if r.get(field) == OWNER]
        if len(rows) != 1:
            raise ValueError('One installed WICC record required: ' + key)
        selected[key] = rows[0]
    if selected['owner']['route_ids'] != [] or selected['owner']['capabilities']['reference_route'] != 0:
        raise ValueError('Existing WICC route needs reconciliation')
    selected['widths'] = [r for r in collections['widths'] if r.get('current_id') == 'west-india-coastal']
    if len(selected['widths']) != 1 or selected['widths'][0]['id'] != 'wicc-vinayachandran-2021-review-surface-width':
        raise ValueError('Installed WICC review-cited width differs')
    sources = collections['sources']
    selected['publications'], resolutions = publications(sources)
    selected['owner_sources'] = [r for r in sources if r['id'] in selected['owner']['source_ids']]
    receipt = bundle['manifest']['dashboard_receipt']
    dashboard_raw = receipt['source_json'].encode()
    if sha(dashboard_raw) != receipt['source_sha256']:
        raise ValueError('Historical dashboard receipt mismatch')
    selected['historical_dashboard_entry'] = [r for r in json.loads(dashboard_raw)['entries'] if r['id'] == OWNER]
    if len(selected['historical_dashboard_entry']) != 1:
        raise ValueError('Historical WICC dashboard missing')
    selected['manifest_bindings'] = {key: bundle['manifest'][key] for key in
                                     ['published_wicc_review_width_v1', 'published_eacc_cited_width_constraint_v1']}
    data = encoded(selected)
    if len(data) > 120000:
        raise ValueError('Selected metadata exceeds compact artifact budget')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain']).strip():
        raise ValueError('Audit modified tracked data')
    result = {'schema': 'osw.wicc-reference-parent-audit.v1', 'status': 'PASS_READ_ONLY',
              'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
              'engine_manifest_sha256': ENGINE, 'logical_sha256': LOGICAL, 'logical_byte_length': 190553938,
              'packet_parts_verified': len(parts), 'collection_counts': {k: len(v) for k, v in collections.items()},
              'publication_resolutions': resolutions, 'selected_records_sha256': sha(data), 'selected_records_bytes': len(data),
              'packet_loaded_only_in_cloud': True, 'index_loaded': False, 'native_wasm_built': False,
              'scientific_data_changed': False, 'browser_run': False, 'working_branch_installed': False}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'selected-records.json').write_bytes(data)
    (OUT / 'result.json').write_bytes(encoded(result))
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        audit()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / 'failure.json').write_bytes(encoded({'status': 'FAIL', 'error': str(error), 'source_commit': os.environ.get('GITHUB_SHA')}))
        raise
