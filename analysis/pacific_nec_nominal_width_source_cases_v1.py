"""Exact original-document queries for cloud verification; no index is loaded here."""
import copy
import hashlib
import json
import pacific_nec_nominal_width_query_v1 as query
import pacific_nec_nominal_width_index_v1 as index

COUNT = 6


def cases():
    documents = {path: json.loads((query.ROOT / path).read_bytes()) for path in index.DOCUMENTS}
    result = [({'document': path, 'pointer': '', 'limit': 500, 'offset': 0}, value)
              for path, value in documents.items()]
    for path, pointer in [(query.nominal.FACTS, '/nominal_surface_width'),
                          (query.FILE, '/width_record'), (query.FILE, '/new_sources')]:
        result.append(({'document': path, 'pointer': pointer, 'limit': 100, 'offset': 0},
                       documents[path][pointer[1:]]))
    if len(result) != COUNT:
        raise ValueError('Exact six new source queries required')
    return copy.deepcopy(result)


def verify(request, expected, response):
    if (request, expected) not in cases():
        raise ValueError('Only frozen original-document requests are supported')
    wanted_hash = hashlib.sha256((query.ROOT / request['document']).read_bytes()).hexdigest()
    rows = response.get('rows', [])
    if (response.get('ok') is not True or response.get('source_sha256') != wanted_hash
            or any(response.get(key) != request[key] for key in ['document', 'pointer', 'offset', 'limit'])
            or response.get('total') != len(expected) or len(rows) != len(expected)):
        raise ValueError('Complete source identity, total and rows required')
    for position, row in enumerate(rows):
        key = str(position) if isinstance(expected, list) else row.get('source_key')
        if not isinstance(key, str):
            raise ValueError('Source row key must be a string')
        escaped = key.replace('~', '~0').replace('/', '~1')
        if row.get('source_key') != key or row.get('source_pointer') != request['pointer'] + '/' + escaped:
            raise ValueError('Source row provenance differs')
    if isinstance(expected, list):
        actual = [row['record'] for row in rows]
    else:
        keys = [row['source_key'] for row in rows]
        if len(set(keys)) != len(keys):
            raise ValueError('Duplicate source keys')
        actual = {row['source_key']: row['record'] for row in rows}
    if actual != expected:
        raise ValueError('Frozen original source content differs')
