"""Pure scope checks for a matching compiled catalog; no build or data loading."""
import copy
import posixpath
import re
import shlex

CATALOG = 'almanac/index-catalog.json'
WASM = 'almanac/query-engine.wasm'
RECEIPT = 'south_java_compiled_catalog_engine_v1'


def dependencies(text, root, inventory):
    """Check compiler-emitted dependencies, not only a scan of include macros."""
    root = str(root).rstrip('/')
    if not root.startswith('/'):
        raise ValueError('Cloud POSIX workspace required')
    lines = [line for line in text.replace('\\\n', ' ').splitlines() if line and not line.startswith('#')]
    if not lines or ': ' not in lines[0]:
        raise ValueError('Unsupported compiler dependency record')
    values = shlex.split(lines[0].split(': ', 1)[1])
    if not values:
        raise ValueError('Empty compiler dependency record')
    allowed = set(inventory['rust_source_sha256']) | set(inventory['compile_time_data_sha256'])
    excluded = set(inventory['excluded_test_only_data_references'])
    actual = set()
    for value in values:
        path = posixpath.normpath(value if value.startswith('/') else root + '/' + value)
        if not path.startswith(root + '/'):
            raise ValueError('Compile dependency leaves frozen workspace')
        relative = path[len(root) + 1:]
        if relative in excluded:
            raise ValueError('Unpinned test-only fixture reached production compilation: ' + relative)
        if relative not in allowed:
            raise ValueError('Undeclared production compile dependency: ' + relative)
        actual.add(relative)
    required = {CATALOG, 'rust/osw-query/src/index_store.rs'}
    if not required <= actual:
        raise ValueError('Compiled index catalog/guard missing from dependency record')
    return {'production_dependencies': sorted(actual),
            'production_dependency_count': len(actual), 'test_only_fixtures_compiled': 0,
            'compiled_catalog_dependency_verified': True}


def overlay(parent, inventory, scope, *, wasm_sha256, compiler, parent_manifest_sha256, dependency_proof):
    if (parent.get('schema') != 'osw.query-engine-manifest.v1' or parent.get('abi_version') != 1
            or RECEIPT in parent or not re.fullmatch('[0-9a-f]{64}', wasm_sha256)
            or not re.fullmatch('[0-9a-f]{64}', parent_manifest_sha256)
            or not compiler.startswith('rustc 1.95.0 ')
            or dependency_proof.get('compiled_catalog_dependency_verified') is not True):
        raise ValueError('Exact matching-build identity and dependency proof required')
    sources = inventory['rust_source_sha256']
    data = inventory['compile_time_data_sha256']
    declared = {row['path']: row for row in scope['source_pin_differences']}
    actual = {path for path, value in sources.items() if parent['sha256'].get(path) != value}
    if actual != set(declared):
        raise ValueError('Runtime source differences exceed the declared prior local-extent scope')
    for path in actual:
        if (parent['sha256'].get(path) != declared[path]['installed_engine_source_sha256']
                or sources[path] != declared[path]['current_native_source_sha256']):
            raise ValueError('Declared runtime source identity mismatch: ' + path)
    if parent['sha256'].get(CATALOG) != data.get(CATALOG) or data.get(CATALOG) != inventory['saved_candidate_catalog_sha256']:
        raise ValueError('Saved generated catalog identity mismatch')
    for path, value in data.items():
        if path in parent['sha256'] and parent['sha256'][path] != value:
            raise ValueError('Historical compiled scientific/generated input would change: ' + path)
    result = copy.deepcopy(parent)
    result['sha256'].update(sources)
    result['sha256'].update(data)
    result['sha256'][WASM] = wasm_sha256
    result['rustc'] = compiler
    result[RECEIPT] = {'schema': 'osw.south-java-compiled-catalog-engine.v1',
                       'parent_engine_manifest_sha256': parent_manifest_sha256,
                       'previous_binary_sha256': parent['sha256'][WASM],
                       'matching_binary_sha256': wasm_sha256,
                       'saved_candidate_catalog_sha256': data[CATALOG],
                       'saved_candidate_logical_sha256': inventory['saved_candidate_logical_sha256'],
                       'declared_prior_runtime_source_changes': sorted(actual),
                       'compiled_rust_source_count': len(sources),
                       'pinned_compile_time_data_count': len(data),
                       'newly_recorded_compile_input_pins': sorted((set(sources) | set(data)) - set(parent['sha256'])),
                       'dependency_proof': copy.deepcopy(dependency_proof),
                       'catalog_integrity_guard_preserved': True,
                       'scientific_source_processing': False, 'new_physical_dimensions_admitted': 0}
    return result
