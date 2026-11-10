"""Attach the scoped Labrador floor to working queries without editing history."""
import copy
import hashlib
import json
from urllib.parse import quote
from labrador_latitude_gate_bound_v1 import (
    ROOT, REPORT, FIGURE, ENTITY, BASE, SOURCE_ID, METHOD_ID, verify_inputs,
)

OPERATOR = 'analysis/labrador_gate_bound_query.py'


def evidence():
    document, pins = verify_inputs()
    return document, {**pins, OPERATOR: hashlib.sha256((ROOT / OPERATOR).read_bytes()).hexdigest()}


def records(document):
    return [('current_length_bound_admissions', document),
            ('measurements', document['measurement']),
            ('claims', document['claim']),
            ('sources', document['source_record']),
            ('sources', document['method_source'])]


def append(collections, document):
    rows = collections['length_assessments']
    matches = [i for i, row in enumerate(rows) if row['entity_id'] == ENTITY]
    prior = next(row for row in json.loads((ROOT / BASE).read_bytes())['length_assessments'] if row['entity_id'] == ENTITY)
    if len(matches) != 1 or rows[matches[0]] != prior:
        raise ValueError('Renew the declared prior Labrador assessment')
    for name, record in records(document):
        if any(row['id'] == record['id'] for row in collections.get(name, [])):
            raise ValueError('Duplicate Labrador bound record: ' + record['id'])
    rows[matches[0]] = copy.deepcopy(document['length_assessment'])
    for name, record in records(document):
        collections.setdefault(name, []).append(copy.deepcopy(record))


def links(document):
    def query(label, collection, field, value):
        request = {'collection': collection, 'filters': [{'field': field, 'op': 'eq', 'value': value}], 'limit': 1}
        return {'label': label, 'url': 'query.html?q=' + quote(json.dumps(request, separators=(',', ':')), safe='')}
    return [
        {'label': f"Inspect the conditional {document['measurement']['value']:,.0f} km geographic floor", 'url': '../' + FIGURE},
        query('Query the working Labrador length assessment', 'length_assessments', 'entity_id', ENTITY),
        query('Audit all nine Labrador geographic gate scenarios', 'current_length_bound_admissions', 'entity_id', ENTITY),
        query('Read the selected original-source custody', 'sources', 'id', SOURCE_ID),
    ]
