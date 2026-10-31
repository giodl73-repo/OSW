"""Freeze complete-card compatibility and the matching-engine delivery scope."""
import argparse
import json

import pacific_secc_reference_runtime_v1 as runtime
import pacific_secc_publication_admission_v1 as admission

ROOT = runtime.ROOT
FILE = 'research/pacific-secc-reference-runtime-scope-v3.json'
MODULE = 'analysis/pacific_secc_runtime_scope_v3.py'
PRIOR = 'research/pacific-secc-reference-runtime-scope-v2.json'
PRIOR_SHA = '8963e66eb3db3547750a4d6aa103492030aa36d8f424b04a432985c0879edc76'
ADAPTER = 'rust/osw-query/src/pacific_secc_reference.rs'
ARCHIVE = 'research/pacific-secc-reference-runtime-history-v3/pacific_secc_reference.rs.source'
PRIOR_ADAPTER_SHA = '4a7cadcba2da37f6152ecff2456c0c81d9a8acee06564494a33ca79957d530a3'


def build():
    raw = (ROOT / PRIOR).read_bytes()
    if runtime.sha(raw) != PRIOR_SHA:
        raise ValueError('Exact v2 preparation scope required')
    prior = json.loads(raw)
    for path, sha in prior['input_sha256'].items():
        actual_path = ARCHIVE if path == ADAPTER else path
        if runtime.sha((ROOT / actual_path).read_bytes()) != sha:
            raise ValueError('Prior prepared source or retained adapter bytes changed: ' + path)
    if runtime.sha((ROOT / ARCHIVE).read_bytes()) != PRIOR_ADAPTER_SHA:
        raise ValueError('Exact prior card adapter archive required')
    for path, row in prior['runtime_source_changes'].items():
        if runtime.sha((ROOT / path).read_bytes()) != row['candidate_sha256']:
            raise ValueError('Other scoped runtime source changed: ' + path)
    names = [MODULE, PRIOR, ARCHIVE, ADAPTER, 'analysis/pacific_secc_reference_delivery_v2.py',
             'analysis/pacific_secc_engine_delivery_v1.py', 'plans/pacific-secc-full-delivery-v1.md',
             'research/pacific-secc-reference-presentation-history-v1/support-prepared.html.source',
             'analysis/test_pacific_secc_engine_delivery_v1.py',
             'analysis/pacific_secc_full_delivery_cases_v1.py', 'analysis/check_pacific_secc_parity_v1.mjs',
             'analysis/check_pacific_secc_browser_v1.py']
    lines = (ROOT / ADAPTER).read_text(encoding='utf-8').splitlines()
    module_line = next(i for i, line in enumerate(lines, 1) if line.strip() == '#[cfg(test)]')
    locations = {}
    for path in prior['additional_test_only_fixtures']:
        matches = [i for i, line in enumerate(lines, 1) if path in line and 'include_str!' in line]
        if len(matches) != 1:
            raise ValueError('One explicit test-only reference required: ' + path)
        locations[path] = [{'source': ADAPTER, 'line': matches[0], 'test_module_line': module_line}]
    output = dict(prior)
    output.update(schema='osw.pacific-secc-reference-runtime-scope.v3',
        status='FULL_CARD_AND_ENGINE_SOURCE_SCOPE_PREPARED_CLOUD_DELIVERY_PENDING',
        prior_scope_file=PRIOR, prior_scope_sha256=PRIOR_SHA,
        added_runtime_source={ADAPTER: runtime.sha((ROOT / ADAPTER).read_bytes())},
        prior_prepared_adapter_archive={'path': ARCHIVE, 'sha256': PRIOR_ADAPTER_SHA},
        compiled_source_contract_sha256={p: runtime.sha((ROOT / p).read_bytes())
                                       for p in prior['additional_compiled_source_contracts']},
        candidate_presentation_paths=[admission.query.PAGE],
        additional_test_only_data_reference_locations=locations,
        input_sha256={p: runtime.sha((ROOT / p).read_bytes()) for p in names},
        native_wasm_supplement_verified=False, installed=False)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = runtime.query.encoded(build())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Complete card/engine scope differs')
    print(json.dumps({'status': 'PASS', 'native_wasm_supplement_verified': False, 'installed': False}))
