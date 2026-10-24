"""Extend a hash-verified index without rerunning historical science producers."""
import copy
import json
from current_gap_candidate_metadata import DASHBOARD, digest


def extend(catalog, corpus, registry, additions):
    """Preserve every old source string except the explicit dashboard refresh.

    The caller verifies the original compressed and decompressed corpus hashes
    before parsing. Every original document is checked against its descriptor
    here. New source paths cannot overwrite historical source documents.
    """
    if (catalog.get('schema') != 'osw.almanac-index-catalog.v1'
            or corpus.get('schema') != 'osw.almanac-index-bundle.v1'
            or registry.get('schema') != 'osw.almanac-index-sources.v1'):
        raise ValueError('Unsupported parent index')
    documents = corpus['documents']
    descriptors = catalog['documents']
    paths = [row['path'] for row in descriptors]
    if len(paths) != len(set(paths)) or set(paths) != set(documents):
        raise ValueError('Incomplete or duplicate parent index inventory')
    if catalog['source_count'] != len(paths):
        raise ValueError('Changed parent index count')
    for row in descriptors:
        raw = documents[row['path']].encode('utf-8')
        if digest(raw) != row['source_sha256'] or len(raw) != row['source_bytes']:
            raise ValueError('Changed original index source: ' + row['path'])
    declared = registry['documents']
    if len(declared) != len(set(declared)) or not set(declared) <= set(documents):
        raise ValueError('Changed parent index registry')
    new_documents = dict(documents)
    replacements = set()
    for path, raw in additions.items():
        if (not path.startswith('research/') or not path.endswith('.json') or '\\' in path or ':' in path
                or any(part in ('', '.', '..') for part in path.split('/'))):
            raise ValueError('Unsupported new index source address')
        text = raw.decode('utf-8')
        if not isinstance(json.loads(text), (dict, list)):
            raise ValueError('Unsupported new index source shape')
        if path in documents and documents[path] != text:
            if path != DASHBOARD:
                raise ValueError('Historical source replacement prohibited: ' + path)
            replacements.add(path)
        new_documents[path] = text
    new_registry = copy.deepcopy(registry)
    new_registry['documents'] = sorted(set(declared) | set(additions))
    by_path = {row['path']: row for row in descriptors}
    for path, raw in additions.items():
        document = json.loads(raw)
        by_path[path] = {
            'path': path, 'source_sha256': digest(raw), 'source_bytes': len(raw),
            'root_kind': 'object' if isinstance(document, dict) else 'array',
            'source_schema': document.get('schema') if isinstance(document, dict) else None,
            'optional': by_path.get(path, {}).get('optional', False)}
    next_catalog = copy.deepcopy(catalog)
    next_catalog['documents'] = [by_path[path] for path in sorted(by_path)]
    next_catalog['source_count'] = len(by_path)
    next_catalog['source_bytes'] = sum(row['source_bytes'] for row in by_path.values())
    audit = {
        'original_sources_verified': len(documents),
        'original_source_strings_preserved': len(documents) - len(replacements),
        'replaced_source_paths': sorted(replacements),
        'added_source_paths': sorted(set(additions) - set(documents)),
        'scientific_source_documents_replaced': 0,
    }
    return next_catalog, {'schema': corpus['schema'], 'documents': new_documents}, new_registry, audit
