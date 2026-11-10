"""Small, strict custody rules for the exact reviewed EICC saved artifacts."""
import hashlib
import re

CASE = (40402558440, 2, 121852515778, 'b7ba3fbbc4718e8391602275460462be931826ac')
PROOF_DIR = 'research/eicc-reference-delivery-evidence-v7/'
WORKFLOW = '.github/workflows/install-eicc-reference-v1.yml'
REQUEST = 'research/eicc-reference-installation-request-v1.json'
PROOF = 'research/eicc-reference-installed-v1.json'
FIXED = {'almanac/query-data.json', 'almanac/query-engine.wasm', 'almanac/query-engine.manifest.json',
         'almanac/index-catalog.json', 'almanac/index-data.json.gz', 'almanac/index-sources.json',
         'research/ocean-motion-dashboard.json'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_request(request):
    expected = {'schema': 'osw.eicc-reference-installation-request.v1', 'execution_permitted': True,
                'working_branch_installation_permitted': True, 'installation_workflow': WORKFLOW,
                'max_cloud_jobs': 1, 'max_heavy_local_jobs': 0}
    for key, value in expected.items():
        if type(request.get(key)) is not type(value) or request[key] != value:
            raise ValueError('Disabled or changed installation request: ' + key)
    for key in ['native_build_permitted', 'wasm_build_permitted', 'browser_automation_permitted',
                'scientific_source_processing_permitted', 'local_bulk_sync_permitted', 'main_merge_permitted']:
        if request.get(key) is not False:
            raise ValueError('Forbidden installation permission: ' + key)


def generated_paths(result):
    paths = result.get('artifact_paths', [])
    hashes = result.get('generated_sha256', {})
    if len(paths) != 19 or len(set(paths)) != 19 or not FIXED <= set(paths) or set(hashes) != set(paths):
        raise ValueError('Exact nineteen saved files and hashes required')
    parts = set(paths) - FIXED
    indices = set()
    for path in parts:
        match = re.fullmatch(r'almanac/query-parts/(\d{6})-([0-9a-f]{64})\.bin', path)
        if not match or hashes[path] != match[2]:
            raise ValueError('Changed addressed packet part')
        indices.add(int(match[1]))
    if indices != set(range(12)) or any(not isinstance(h, str) or not re.fullmatch('[0-9a-f]{64}', h) for h in hashes.values()):
        raise ValueError('Twelve consecutive packet parts and exact byte hashes required')
    return set(paths)


def verify_proofs(review, result, engine, browser, custody, parities, preservation):
    fixed = {'schema': 'osw.eicc-reference-installation-visual-review.v1',
             'status': 'APPROVED_EXACT_WORKING_BRANCH_DATA_INSTALLATION',
             'run_id': CASE[0], 'run_attempt': CASE[1], 'job_id': CASE[2], 'source_commit': CASE[3],
             'actual_screenshots_inspected': 8, 'visual_review_complete': True, 'browser_verified': True,
             'scientific_release_approved': False, 'main_merge_approved': False, 'working_branch_installed': False}
    if any(type(review.get(k)) is not type(v) or review[k] != v for k, v in fixed.items()):
        raise ValueError('Exact completed visual review required')
    expected = {'schema': 'osw.eicc-reference-delivery-result.v7', 'status': 'PASS', 'source_commit': CASE[3],
                'logical_sha256': '93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696',
                'logical_bytes': 190404811, 'candidate_records': 108592, 'named_currents': 106,
                'scoped_width_records': 172, 'new_evidence_records': 15, 'new_source_records': 3,
                'rust_planning_tests_passed': 6, 'rust_route_inventory_tests_passed': 2,
                'main_query_comparisons': 24, 'source_query_comparisons': 25, 'presentation_api_comparisons': 2,
                'new_ranked_lengths': 0, 'new_physical_dimensions_admitted': 0, 'new_named_eddies': 0,
                'new_state_intersections': 0, 'browser_verified': True, 'working_branch_installed': False,
                'visual_review_complete': False, 'scientific_source_processing': False, 'main_merged': False}
    if any(type(result.get(k)) is not type(v) or result[k] != v for k, v in expected.items()):
        raise ValueError('Exact successful saved delivery result required')
    if str(result.get('run_id')) != str(CASE[0]) or str(result.get('run_attempt')) != str(CASE[1]):
        raise ValueError('Changed delivery run/attempt')
    paths = generated_paths(result)
    if (engine.get('status') != 'PASS' or engine.get('stage') != 'engine_verified'
            or engine.get('source_commit') != CASE[3] or engine.get('native_smoke_verified') is not True
            or engine.get('rust_planning_tests_passed') != 6 or engine.get('rust_route_inventory_tests_passed') != 2
            or engine.get('verified_generated_sha256') != result['generated_sha256']
            or set(engine.get('verified_generated_artifact_paths', [])) != paths):
        raise ValueError('Saved matching engine custody differs')
    for key, path in [('wasm_sha256', 'almanac/query-engine.wasm'),
                      ('engine_manifest_sha256', 'almanac/query-engine.manifest.json')]:
        if engine.get(key) != result['generated_sha256'][path] or review.get(key) != engine[key] or custody.get(key) != engine[key]:
            raise ValueError('Binary/manifest identities differ')
    if (custody.get('status') != 'PASS' or custody.get('source_commit') != CASE[3]
            or custody.get('generated_paths_verified') != 19 or custody.get('logical_sha256') != result['logical_sha256']
            or review.get('logical_sha256') != result['logical_sha256'] or review.get('logical_bytes') != result['logical_bytes']):
        raise ValueError('Verified pre-browser artifact custody differs')
    for mode, count in [('main', 24), ('index', 25), ('snapshots', 2)]:
        row = parities.get(mode, {})
        if (row.get('status') != 'PASS' or row.get('wasm_sha256') != engine['wasm_sha256']
                or row.get('initialization_metadata_equal') is not True or len(row.get('checks', [])) != count
                or any(c.get('entire_response_equal') is not True for c in row['checks'])
                or (mode == 'index' and row.get('mismatched_corpus_refused') is not True)
                or engine.get('native_wasm_parity', {}).get(mode) != row):
            raise ValueError('Complete saved native/WASM proof differs: ' + mode)
    for mode in ['atlas', 'seasons']:
        row = preservation.get(mode, {})
        if row.get('status') != 'PASS' or row.get('complete_catalog_matches_source_projection') is not True:
            raise ValueError('Complete parent/candidate presentation preservation required')
    screenshots = browser.get('screenshots', [])
    if (browser.get('browser_verified') is not True or browser.get('page_errors') != []
            or browser.get('original_downloads') != [] or len(browser.get('checks', [])) != 6
            or len(screenshots) != 8 or len({r['path'] for r in screenshots}) != 8
            or screenshots != review.get('screenshots')):
        raise ValueError('Exact successful browser and reviewed screenshots required')
    return paths
