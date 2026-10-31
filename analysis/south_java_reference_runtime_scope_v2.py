"""Record exact installed-source archives and the bounded South Java extension."""
import argparse
import json

import south_java_reference_runtime_v1 as runtime

ROOT = runtime.ROOT
FILE = 'research/south-java-reference-runtime-scope-v2.json'
MODULE = 'analysis/south_java_reference_runtime_scope_v2.py'
BINDINGS = 'research/south-java-reference-runtime-parent-source-bindings-v2.json'
PARENT = 'research/pacific-secc-installation-saved-engine-manifest-v1.json'
ADAPTER = 'rust/osw-query/src/south_java_reference.rs'
FIXTURE = 'research/south-java-reference-runtime-fixture-v1.json'


def build():
    parent_raw = (ROOT / PARENT).read_bytes()
    if runtime.sha(parent_raw) != 'a36845e583cf89ba49a1c75612da627f6d78bebacdc15fdf02574985d51d00fa':
        raise ValueError('Exact saved installed engine metadata required')
    parent = json.loads(parent_raw)
    bindings = json.loads((ROOT / BINDINGS).read_bytes())['bindings']
    if len(bindings) != 9:
        raise ValueError('Eight Rust revisions and one atlas UI revision required')
    for path, row in bindings.items():
        if (parent['sha256'].get(path) != row['historical_sha256']
                or runtime.sha((ROOT / row['archive_path']).read_bytes()) != row['historical_sha256']
                or runtime.sha((ROOT / path).read_bytes()) != row['candidate_sha256']):
            raise ValueError('Changed exact parent archive or declared child source: ' + path)
    raw = (ROOT / runtime.FILE).read_bytes()
    if raw != runtime.query.encoded(runtime.build_contract()):
        raise ValueError('Frozen runtime contract required')
    lines = (ROOT / ADAPTER).read_bytes().decode().splitlines()
    module_line = next(i for i, line in enumerate(lines, 1) if line.strip() == '#[cfg(test)]')
    references = [i for i, line in enumerate(lines, 1) if FIXTURE in line and 'include_str!' in line]
    if len(references) != 1 or references[0] <= module_line:
        raise ValueError('One test-only fixture include required')
    cohort_path = 'rust/osw-query/src/current_gap_admissions.rs'
    cohort_lines = (ROOT / cohort_path).read_bytes().decode().splitlines()
    cohort_module = next(i for i, line in enumerate(cohort_lines, 1) if line.strip() == '#[cfg(test)]')
    cohort_references = [i for i, line in enumerate(cohort_lines, 1) if FIXTURE in line and 'include_str!' in line]
    if len(cohort_references) != 1 or cohort_references[0] <= cohort_module:
        raise ValueError('One cohort integration test-only fixture include required')
    names = [MODULE, BINDINGS, PARENT, ADAPTER, FIXTURE, runtime.FILE, runtime.MODULE, runtime.PROTOCOL,
        'analysis/south_java_reference_fixture_v1.py', 'analysis/test_south_java_reference_runtime_v1.py',
        runtime.query.MODULE, runtime.query.FILE, runtime.query.PROTOCOL,
        'analysis/test_south_java_reference_query_v1.py', runtime.query.PAGE]
    names += [row['archive_path'] for row in bindings.values()]
    return {'schema': 'osw.south-java-reference-runtime-scope.v2',
        'status': 'SOURCE_AND_FIXTURE_PREPARED_NATIVE_CLOUD_CHECK_PENDING',
        'parent_engine_manifest_file': PARENT, 'parent_engine_manifest_sha256': runtime.sha(parent_raw),
        'parent_logical_sha256': runtime.query.PARENT, 'runtime_source_changes': bindings,
        'added_runtime_source': {ADAPTER: runtime.sha((ROOT / ADAPTER).read_bytes())},
        'additional_compiled_source_contracts': {runtime.FILE: runtime.sha(raw)},
        'additional_test_only_fixtures': [FIXTURE],
        'additional_test_only_data_reference_locations': {FIXTURE: [
            {'source': ADAPTER, 'line': references[0], 'test_module_line': module_line},
            {'source': cohort_path, 'line': cohort_references[0], 'test_module_line': cohort_module}]},
        'input_sha256': {p: runtime.sha((ROOT / p).read_bytes()) for p in names},
        'new_physical_dimensions': 0, 'native_built_locally': False, 'packet_or_index_loaded_locally': False,
        'native_source_cloud_verified': False, 'native_wasm_delivery_verified': False, 'installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = runtime.query.encoded(build())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Changed source scope')
    print(json.dumps({'status': 'PASS', 'native_wasm_delivery_verified': False, 'installed': False}))
