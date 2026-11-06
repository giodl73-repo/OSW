"""Bind six exact installed Rust parents to the prepared regional-reference sources."""
import argparse
import json

import pacific_secc_reference_runtime_v1 as runtime

ROOT = runtime.ROOT
FILE = 'research/pacific-secc-reference-runtime-scope-v1.json'
MODULE = 'analysis/pacific_secc_runtime_scope_v1.py'
ARCHIVE = 'research/pacific-secc-reference-runtime-history-v1/archive.json'
PARENT_MANIFEST = 'research/eacc-connection-presentation-saved-engine-manifest-v4.json'
PARENT_MANIFEST_SHA = 'c9ccda691c287f560be53a8bd422a7c364fc9a8e5d2300d6f4868efb9daaf4e9'
NEW_MODULE = 'rust/osw-query/src/pacific_secc_reference.rs'
FIXTURE = 'research/pacific-secc-reference-runtime-fixture-v1.json'
PRESENTATION = 'eacc_regional_connection_presentation_v4'


def build():
    raw = (ROOT / PARENT_MANIFEST).read_bytes()
    if runtime.sha(raw) != PARENT_MANIFEST_SHA:
        raise ValueError('Exact installed EACC parent engine manifest required')
    parent = json.loads(raw)
    presentation = parent.get(PRESENTATION)
    if not isinstance(presentation, dict):
        raise ValueError('Installed EACC presentation namespace missing')
    archive = json.loads((ROOT / ARCHIVE).read_bytes())['sources']
    expected = {'rust/osw-query/src/' + n for n in ['lib.rs', 'planning.rs', 'atlas_data.rs',
                'seasons_data.rs', 'madagascar_coastal_curve.rs', 'nwasc_reference_route.rs']}
    if set(archive) != expected:
        raise ValueError('Exact six-file parent source inventory required')
    changes = {}
    for path, identity in archive.items():
        old = (ROOT / identity['archive_path']).read_bytes()
        new = (ROOT / path).read_bytes()
        if runtime.sha(old) != identity['parent_sha256'] or parent['sha256'].get(path) != identity['parent_sha256']:
            raise ValueError('Archived source differs from installed engine parent: ' + path)
        if new == old:
            raise ValueError('Expected runtime source integration missing: ' + path)
        changes[path] = {**identity, 'candidate_sha256': runtime.sha(new),
                         'parent_bytes': len(old), 'candidate_bytes': len(new)}
    document = runtime.build_contract()
    if (ROOT / runtime.FILE).read_bytes() != runtime.query.encoded(document):
        raise ValueError('Saved runtime contract differs')
    pins = {p: runtime.sha((ROOT / p).read_bytes()) for p in [MODULE, ARCHIVE, PARENT_MANIFEST,
            runtime.FILE, runtime.MODULE, runtime.PROTOCOL, NEW_MODULE, FIXTURE,
            'analysis/test_pacific_secc_reference_runtime_v1.py']}
    return {'schema': 'osw.pacific-secc-reference-runtime-scope.v1',
            'status': 'SOURCE_SCOPE_VERIFIED_COMPILATION_AND_DELIVERY_PENDING',
            'parent_engine_manifest_file': PARENT_MANIFEST,
            'parent_engine_manifest_sha256': PARENT_MANIFEST_SHA,
            'parent_logical_sha256': runtime.PARENT_LOGICAL,
            'runtime_source_changes': changes,
            'added_runtime_source': {NEW_MODULE: pins[NEW_MODULE]},
            'additional_compiled_source_contracts': [runtime.FILE],
            'test_only_source_fixture': FIXTURE,
            'preserve_engine_namespace': PRESENTATION,
            'preserved_engine_namespace_sha256': runtime.sha(runtime.query.encoded(presentation)),
            'input_sha256': pins, 'local_heavy_work_permitted': False,
            'native_wasm_verified': False, 'installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = runtime.query.encoded(build())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Runtime source scope differs')
    print(json.dumps({'status': 'PASS', 'installed_parent_source_archives': 6, 'native_wasm_verified': False}))
