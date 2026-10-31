"""Pure custody rules for saved Loop data plus a noncompiled page revision."""
import copy
import hashlib
import json
import re

PAGE = 'almanac/loop-published-metrics.html'
ARCHIVED_PAGE = 'almanac/loop-published-metrics-source-v1.html'
ARCHIVED_MANIFEST = 'research/loop-published-metrics-saved-engine-manifest-v2.json'
MANIFEST = 'almanac/query-engine.manifest.json'
WASM = 'almanac/query-engine.wasm'
OVERLAY = 'loop_published_metrics_presentation_revision_v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()


def generated_paths(result):
    paths = result['artifact_paths']
    fixed = {'almanac/query-data.json', WASM, MANIFEST, 'almanac/index-catalog.json',
             'almanac/index-data.json.gz', 'almanac/index-sources.json',
             'research/ocean-motion-dashboard.json'}
    if len(paths) != 19 or len(set(paths)) != 19 or not fixed <= set(paths):
        raise ValueError('Exact nineteen saved paths required')
    parts = set(paths) - fixed
    if len(parts) != 12 or any(re.fullmatch(r'almanac/query-parts/\d{6}-[0-9a-f]{64}\.bin', p) is None for p in parts):
        raise ValueError('Twelve exact addressed packet parts required')
    if set(result['generated_sha256']) != set(paths):
        raise ValueError('Every saved path must have an exact hash')
    return set(paths)


def presentation_manifest(saved_raw, original_page, revised_page, revision, inventory):
    """Leave all saved binary/data/source history intact; declare only page changes."""
    saved = json.loads(saved_raw)
    if (sha(original_page) != revision['original_sha256']
            or sha(revised_page) != revision['candidate_sha256']
            or revision['original_path'] != PAGE):
        raise ValueError('Page revision differs from reviewed byte versions')
    compiled = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    if {PAGE, ARCHIVED_PAGE, ARCHIVED_MANIFEST} & compiled:
        raise ValueError('Presentation overlay may not change compiled inputs')
    pins = saved['sha256']
    if pins.get(PAGE) != revision['original_sha256']:
        raise ValueError('Saved engine must bind the original reviewed page')
    if OVERLAY in saved or ARCHIVED_PAGE in pins or ARCHIVED_MANIFEST in pins:
        raise ValueError('Do not overwrite existing presentation history')
    result = copy.deepcopy(saved)
    result['sha256'][PAGE] = revision['candidate_sha256']
    result['sha256'][ARCHIVED_PAGE] = revision['original_sha256']
    result['sha256'][ARCHIVED_MANIFEST] = sha(saved_raw)
    result[OVERLAY] = {
        'schema': 'osw.loop-published-metrics-presentation-manifest-overlay.v1',
        'saved_engine_manifest_sha256': sha(saved_raw),
        'saved_manifest_archive_path': ARCHIVED_MANIFEST,
        'original_page_sha256': revision['original_sha256'],
        'original_page_archive_path': ARCHIVED_PAGE,
        'original_page_source_commit': revision['reviewed_execution_commit'],
        'revised_page_sha256': revision['candidate_sha256'],
        'changed_existing_paths': [PAGE],
        'compiled_inputs_changed': [],
        'packet_changed': False,
        'binary_changed': False,
        'historical_source_documents_changed': False,
        'scope': 'Presentation-only revision after separate cloud browser and actual screenshot review. Historical query/source preparation hashes describe their executed source versions.'
    }
    assert result['sha256'][WASM] == saved['sha256'][WASM]
    return result
