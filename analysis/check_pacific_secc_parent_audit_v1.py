"""Cloud-only read-only parent packet and publication identity audit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REQUEST = 'research/pacific-secc-parent-audit-request-v1.json'
PREFLIGHT = 'research/pacific-secc-parent-audit-preflight-v1.json'
WORKFLOW = '.github/workflows/pacific-secc-parent-audit-cloud-v1.yml'
OUTPUT = ROOT / '.pytest_cache/pacific-secc-parent-audit-v1'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


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
    request = json.loads((ROOT / REQUEST).read_bytes())
    if (request.get('schema') != 'osw.pacific-secc-parent-audit-request.v1'
            or request.get('workflow') != WORKFLOW or request.get('execute') is not True
            or request.get('cloud_parent_packet_read_permitted') is not True
            or request.get('max_cloud_jobs') != 1 or request.get('max_heavy_local_jobs') != 0):
        raise ValueError('Exact parent audit request is disabled or invalid')
    for key in ['index_load_permitted', 'native_wasm_build_permitted', 'browser_permitted',
                'ocean_field_processing_permitted', 'working_branch_installation_permitted',
                'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden audit permission: ' + key)
    phase = json.loads((ROOT / 'research/current-gap-delivery-phase.json').read_bytes())
    if phase.get('phase') != 'source-review-only-v1' or phase.get('heavy_work_permitted') is not False:
        raise ValueError('Global phase must remain source-review-only and disabled')
    if digest((ROOT / PREFLIGHT).read_bytes()) != request.get('preflight_sha256'):
        raise ValueError('Changed frozen audit preflight')
    preflight = json.loads((ROOT / PREFLIGHT).read_bytes())
    for path, sha in preflight['input_sha256'].items():
        if digest((ROOT / path).read_bytes()) != sha:
            raise ValueError('Changed audit input: ' + path)
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    remote = json.loads(subprocess.check_output(['gh', 'api',
        'repos/giodl73-repo/OSW/git/ref/heads/codex/current-measurement-gaps']))['object']['sha']
    if head != os.environ.get('GITHUB_SHA') or remote != head:
        raise ValueError('Exact current working-branch source required')
    if subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'status', '--porcelain'], cwd=ROOT).strip():
        raise ValueError('Clean source checkout required')
    return head


def audit():
    head = controls()  # Refuse locally before any packet or source import.
    import pacific_secc_reference_runtime_v1 as runtime
    import pacific_secc_reference_query_v1 as query
    from query_packet import read_bundle_bytes, descriptors
    engine_raw = (ROOT / 'almanac/query-engine.manifest.json').read_bytes()
    # The full engine hash is retained separately from the logical data identity.
    expected_engine = 'c9ccda691c287f560be53a8bd422a7c364fc9a8e5d2300d6f4868efb9daaf4e9'
    if digest(engine_raw) != expected_engine:
        raise ValueError('Installed parent engine manifest changed')
    engine = json.loads(engine_raw)
    descriptor_raw = (ROOT / 'almanac/query-data.json').read_bytes()
    packet = json.loads(descriptor_raw)
    parts = descriptors(packet)
    if (engine['sha256']['almanac/query-data.json'] != digest(descriptor_raw)
            or packet['logical_sha256'] != runtime.PARENT_LOGICAL
            or packet['logical_byte_length'] != 190404811):
        raise ValueError('Exact installed parent packet required')
    for part in parts:
        if engine['sha256'].get('almanac/' + part['path']) != part['sha256']:
            raise ValueError('Packet part differs from installed engine pin')
    raw = read_bundle_bytes(ROOT / 'almanac/query-data.json')
    bundle = json.loads(raw)
    logical_sha = digest(raw)
    del raw
    collections = bundle['collections']
    query.checked_ids(collections['sources'], 'installed sources')
    owners = [r for r in collections['objects'] if r['id'] == query.TARGET]
    entities = [r for r in collections['entities'] if r['id'] == query.TARGET]
    decisions = [r for r in collections['route_decisions'] if r.get('entity_id') == query.TARGET]
    if len(owners) != 1 or len(entities) != 1 or len(decisions) != 1:
        raise ValueError('Exactly one installed Pacific object, entity and decision required')
    candidates = []
    for source in collections['sources']:
        text = json.dumps(source, ensure_ascii=False).lower()
        if (query.DOI.lower() in text or 'cq04.pdf' in text
                or ('seasonal variability' in text and 'south equatorial countercurrent' in text)):
            candidates.append(source)
    try:
        source_id = query.publication_source(collections['sources'])
        resolution = 'UNIQUE_EXISTING_PUBLICATION'
        error = None
    except ValueError as exception:
        source_id = None
        resolution = 'PUBLICATION_RECONCILIATION_REQUIRED'
        error = str(exception)
    contract = runtime.build_contract()
    selected = {'owner': owners[0], 'entity': entities[0], 'planning_decision': decisions[0],
                'owner_sources': [r for r in collections['sources'] if r['id'] in owners[0]['source_ids']],
                'publication_candidates': candidates}
    selected_raw = query.encoded(selected)
    result = {'schema': 'osw.pacific-secc-installed-parent-audit.v1', 'status': 'AUDIT_COMPLETE_READ_ONLY',
        'source_commit': head, 'run_id': os.environ['GITHUB_RUN_ID'], 'run_attempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'engine_manifest_sha256': expected_engine, 'logical_sha256': logical_sha,
        'logical_byte_length': 190404811, 'packet_parts_verified': len(parts),
        'collection_counts': {name: len(rows) for name, rows in collections.items()},
        'publication_resolution': resolution, 'publication_source_id': source_id,
        'publication_resolver_error': error, 'publication_candidate_count': len(candidates),
        'exact_original_planning_source_matches': decisions[0]['source_decision'] == contract['original_planning_source'],
        'prior_owner_routes_empty': owners[0]['route_ids'] == [],
        'prior_reference_capability_zero': owners[0]['capabilities']['reference_route'] == 0,
        'selected_records_sha256': digest(selected_raw), 'selected_records_bytes': len(selected_raw),
        'packet_loaded_only_in_cloud': True, 'index_loaded': False, 'scientific_data_changed': False,
        'native_wasm_built': False, 'browser_run': False, 'working_branch_installed': False}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'selected-records.json').write_bytes(selected_raw)
    (OUTPUT / 'result.json').write_bytes(query.encoded(result))
    print(json.dumps({k: result[k] for k in ['status', 'publication_resolution', 'publication_candidate_count',
                     'exact_original_planning_source_matches', 'selected_records_bytes']}))


if __name__ == '__main__':
    try:
        audit()
    except Exception as error:
        if os.name == 'posix' and os.environ.get('GITHUB_ACTIONS') == 'true':
            OUTPUT.mkdir(parents=True, exist_ok=True)
            (OUTPUT / 'failure.json').write_bytes((json.dumps({'status': 'FAIL', 'error': str(error),
                'source_commit': os.environ.get('GITHUB_SHA'), 'installed': False}) + '\n').encode())
        raise
