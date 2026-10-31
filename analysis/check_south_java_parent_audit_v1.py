"""Read-only cloud selection of the exact installed South Java owner and sources."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/south-java-parent-audit-request-v1.json'
PREFLIGHT = 'research/south-java-parent-audit-preflight-v1.json'
WORKFLOW = '.github/workflows/south-java-parent-audit-cloud-v1.yml'
OUTPUT = ROOT / '.pytest_cache/south-java-parent-audit-v1'
TARGET = 'current:south-java'
ENGINE_SHA = 'a36845e583cf89ba49a1c75612da627f6d78bebacdc15fdf02574985d51d00fa'
LOGICAL_SHA = 'f0e046651b75c84da488c4e81204e410b18f37256e102c26a0ab2f70b5f69184'
PAPERS = {
    'iskandar_2006': {'doi': '10.1029/2006jc003486', 'id': 'source:iskandar-south-java-ofes-2006',
        'url': 'https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2006JC003486'},
    'sprintall_2010': {'doi': '10.1016/j.dynatmoce.2010.02.006',
        'id': 'source:sprintall-sjc-2010-ombai-confinement',
        'url': 'https://pordlabs.ucsd.edu/jsprintall/pub_dir/Sprintall_etal_DYNAT2010.pdf'}}


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def normalized_doi(value):
    value = str(value).strip().lower()
    for prefix in ['https://doi.org/', 'http://doi.org/', 'http://dx.doi.org/', 'https://dx.doi.org/', 'doi:']:
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            break
    return value


def canonical_url(value):
    value = urlsplit(str(value).strip())
    return (value.hostname or '').lower(), value.path.rstrip('/')


def checked_ids(rows):
    ids = [r.get('id') for r in rows]
    if any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError('Unique nonempty installed source IDs required')


def publication(sources, key):
    checked_ids(sources)
    expected = PAPERS[key]
    matches = [r for r in sources if normalized_doi(r.get('doi', '')) == expected['doi']
        or normalized_doi(r.get('url', '')) == expected['doi']
        or canonical_url(r.get('url', '')) == canonical_url(expected['url'])]
    if len(matches) != 1:
        raise ValueError('Exactly one existing publication required: ' + key)
    row = matches[0]
    if row.get('doi') and normalized_doi(row['doi']) != expected['doi']:
        raise ValueError('Publication DOI and URL conflict: ' + key)
    if row['id'] != expected['id']:
        raise ValueError('Publication identity needs reconciliation: ' + key)
    return row


def controls():
    if (os.name != 'posix' or os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REPOSITORY') != 'giodl73-repo/OSW'
            or os.environ.get('GITHUB_REF') != 'refs/heads/codex/current-measurement-gaps'
            or os.environ.get('GITHUB_EVENT_NAME') != 'push'):
        raise ValueError('Exact cloud working-branch audit push required')
    if len(os.sched_getaffinity(0)) != 1 or os.getpriority(os.PRIO_PROCESS, 0) < 15:
        raise ValueError('One CPU with nice15 required')
    for key in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
        if os.environ.get(key) != '1':
            raise ValueError('Single worker required: ' + key)
    request = read(REQUEST)
    for key, value in {'schema': 'osw.south-java-parent-audit-request.v1', 'workflow': WORKFLOW,
        'execute': True, 'cloud_parent_packet_read_permitted': True,
        'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}.items():
        if type(request.get(key)) is not type(value) or request[key] != value:
            raise ValueError('Disabled or changed audit request: ' + key)
    for key in ['index_load_permitted', 'native_wasm_build_permitted', 'browser_permitted',
                'ocean_field_processing_permitted', 'working_branch_installation_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden audit permission: ' + key)
    phase = read('research/current-gap-delivery-phase.json')
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global phase must remain source-review-only and disabled')
    if sha((ROOT / PREFLIGHT).read_bytes()) != request['preflight_sha256']:
        raise ValueError('Changed frozen audit preflight')
    for path, pin in read(PREFLIGHT)['input_sha256'].items():
        if sha((ROOT / path).read_bytes()) != pin:
            raise ValueError('Changed frozen audit source: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api',
        'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or remote != head:
        raise ValueError('Stale source audit refused')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean exact audit checkout required')
    return head


def audit():
    head = controls()  # No packet imports/reads before environment and source checks.
    from query_packet import descriptors, read_bundle_bytes
    engine_raw = (ROOT / 'almanac/query-engine.manifest.json').read_bytes()
    if sha(engine_raw) != ENGINE_SHA:
        raise ValueError('Exact installed Pacific-inclusive engine required')
    engine = json.loads(engine_raw)
    descriptor_raw = (ROOT / 'almanac/query-data.json').read_bytes()
    packet = json.loads(descriptor_raw)
    parts = descriptors(packet)
    if (engine['sha256']['almanac/query-data.json'] != sha(descriptor_raw)
            or packet['logical_sha256'] != LOGICAL_SHA or packet['logical_byte_length'] != 190476712):
        raise ValueError('Exact installed logical parent required')
    for row in parts:
        if engine['sha256'].get('almanac/' + row['path']) != row['sha256']:
            raise ValueError('Changed installed packet part pin')
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    if sha(raw) != LOGICAL_SHA:
        raise ValueError('Logical parent bytes changed')
    bundle = json.loads(raw)
    del raw
    collections = bundle['collections']
    sources = collections['sources']
    checked_ids(sources)
    if len(sources) != 210 or len(collections['reference_routes']) != 81:
        raise ValueError('Unexpected installed source/reference inventory')
    selected = {}
    for name, collection, field in [('owner', 'objects', 'id'), ('entity', 'entities', 'id'),
                                    ('planning_decision', 'route_decisions', 'entity_id')]:
        rows = [r for r in collections[collection] if r.get(field) == TARGET]
        if len(rows) != 1:
            raise ValueError('One installed South Java record required: ' + name)
        selected[name] = rows[0]
    selected['owner_sources'] = [r for r in sources if r['id'] in selected['owner']['source_ids']]
    selected['publications'] = {}
    resolutions = {}
    for key in PAPERS:
        try:
            selected['publications'][key] = publication(sources, key)
            resolutions[key] = {'status': 'UNIQUE_EXISTING_PUBLICATION',
                                'source_id': selected['publications'][key]['id']}
        except ValueError as error:
            resolutions[key] = {'status': 'RECONCILIATION_REQUIRED', 'error': str(error)}
    model = read('research/south-java-model-layer-query-contract-v1.json')['collections']['sources']
    context = read('research/indian-coastal-dimension-context-query-contract-v1.json')['additions']['sources']
    expected = {r['id']: r for r in model + context}
    unchanged = {key: row == expected.get(row['id']) for key, row in selected['publications'].items()}
    planning_path = 'research/indian-current-reference-route-planning-v1.json'
    planning_raw = (ROOT / planning_path).read_bytes()
    plans = [r for r in json.loads(planning_raw)['entries'] if r['current_id'] == 'south-java']
    decision = selected['planning_decision']
    encoded = encode(selected)
    if len(encoded) > 120000:
        raise ValueError('Unexpectedly large selected metadata; do not return a packet')
    result = {'schema': 'osw.south-java-installed-parent-audit.v1', 'status': 'AUDIT_COMPLETE_READ_ONLY',
        'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'engine_manifest_sha256': ENGINE_SHA, 'logical_sha256': LOGICAL_SHA, 'logical_byte_length': 190476712,
        'packet_parts_verified': len(parts), 'collection_counts': {k: len(v) for k, v in collections.items()},
        'publication_resolutions': resolutions, 'original_publication_records_unchanged': unchanged,
        'prior_owner_routes_empty': selected['owner']['route_ids'] == [],
        'prior_reference_capability_zero': selected['owner']['capabilities']['reference_route'] == 0,
        'original_planning_source_matches': len(plans) == 1 and decision.get('source_decision') == plans[0],
        'original_planning_receipt_matches': decision.get('source_catalog_file') == planning_path
            and decision.get('source_catalog_sha256') == sha(planning_raw)
            and bundle['manifest']['input_sha256'].get(planning_path) == sha(planning_raw),
        'selected_records_sha256': sha(encoded), 'selected_records_bytes': len(encoded),
        'packet_loaded_only_in_cloud': True, 'index_loaded': False, 'scientific_data_changed': False,
        'native_wasm_built': False, 'browser_run': False, 'working_branch_installed': False}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'selected-records.json').write_bytes(encoded)
    (OUTPUT / 'result.json').write_bytes(encode(result))
    print(json.dumps({k: result[k] for k in ['status', 'publication_resolutions',
        'original_planning_source_matches', 'original_planning_receipt_matches', 'selected_records_bytes']}))


if __name__ == '__main__':
    try:
        audit()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            OUTPUT.mkdir(parents=True, exist_ok=True)
            (OUTPUT / 'failure.json').write_bytes(encode({'status': 'FAIL', 'error': str(error),
                'source_commit': os.environ.get('GITHUB_SHA'), 'installed': False}))
        raise
