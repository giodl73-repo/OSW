"""Retain the executed v1 scope and bind the audited publication supplement."""
import argparse
import json

import pacific_secc_reference_runtime_v1 as runtime
import pacific_secc_publication_admission_v1 as admission

ROOT = runtime.ROOT
FILE = 'research/pacific-secc-reference-runtime-scope-v2.json'
MODULE = 'analysis/pacific_secc_runtime_scope_v2.py'
PRIOR = 'research/pacific-secc-reference-runtime-scope-v1.json'
PRIOR_SHA = '2aa1a0a4a3936c2aad4c6cbe24c063202aa20aad79ebe5149ee5c7a931044f91'
ADAPTER = 'rust/osw-query/src/pacific_secc_reference.rs'
ARCHIVE = 'research/pacific-secc-reference-runtime-history-v2/pacific_secc_reference.rs.source'
EXECUTED_ADAPTER_SHA = '1657429dd8fab0e4b09407803d76513ec7da74728dd51ebc6fec21c0a829c691'


def build():
    raw = (ROOT / PRIOR).read_bytes()
    if runtime.sha(raw) != PRIOR_SHA:
        raise ValueError('Exact executed v1 scope required')
    prior = json.loads(raw)
    for path, change in prior['runtime_source_changes'].items():
        if (runtime.sha((ROOT / path).read_bytes()) != change['candidate_sha256']
                or runtime.sha((ROOT / change['archive_path']).read_bytes()) != change['parent_sha256']):
            raise ValueError('Earlier scoped runtime source or installed parent archive changed: ' + path)
    if (runtime.sha((ROOT / ARCHIVE).read_bytes()) != EXECUTED_ADAPTER_SHA
            or prior['added_runtime_source'].get(ADAPTER) != EXECUTED_ADAPTER_SHA):
        raise ValueError('Exact cloud-tested v1 adapter archive required')
    document = admission.build_contract()
    if (ROOT / admission.FILE).read_bytes() != runtime.query.encoded(document):
        raise ValueError('Saved explicit publication supplement differs')
    names = [MODULE, PRIOR, ADAPTER, ARCHIVE, admission.FILE, admission.MODULE, admission.PROTOCOL,
             admission.AUDIT, admission.SELECTED, 'analysis/test_pacific_secc_publication_admission_v1.py',
             'research/pacific-secc-reference-publication-fixture-v1.json',
             'analysis/pacific_secc_reference_delivery_v1.py', 'analysis/test_pacific_secc_reference_delivery_v1.py',
             'plans/pacific-secc-reference-packet-delivery-v1.md']
    return {'schema': 'osw.pacific-secc-reference-runtime-scope.v2',
        'status': 'AUDITED_PUBLICATION_AND_NAVIGATION_SOURCE_PREPARED_FULL_DELIVERY_PENDING',
        'prior_scope_file': PRIOR, 'prior_scope_sha256': PRIOR_SHA,
        'parent_engine_manifest_sha256': prior['parent_engine_manifest_sha256'],
        'parent_logical_sha256': runtime.PARENT_LOGICAL,
        'runtime_source_changes': prior['runtime_source_changes'],
        'added_runtime_source': {ADAPTER: runtime.sha((ROOT / ADAPTER).read_bytes())},
        'executed_v1_adapter_archive': {'path': ARCHIVE, 'sha256': EXECUTED_ADAPTER_SHA},
        'additional_compiled_source_contracts': [runtime.FILE, admission.FILE],
        'additional_test_only_fixtures': [prior['test_only_source_fixture'],
            'research/pacific-secc-reference-publication-fixture-v1.json'],
        'expected_runtime_inventory_count': 99, 'expected_compile_time_data_inventory_count': 146,
        'expected_test_only_reference_count': 8,
        'preserve_engine_namespace': prior['preserve_engine_namespace'],
        'preserved_engine_namespace_sha256': prior['preserved_engine_namespace_sha256'],
        'input_sha256': {p: runtime.sha((ROOT / p).read_bytes()) for p in names},
        'new_publication_records': 1, 'new_physical_dimensions': 0,
        'native_wasm_supplement_verified': False, 'installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = runtime.query.encoded(build())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Supplemented runtime source scope differs')
    print(json.dumps({'status': 'PASS', 'native_wasm_supplement_verified': False, 'installed': False}))
