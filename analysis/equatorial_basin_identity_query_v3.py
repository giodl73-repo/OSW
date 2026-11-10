"""Five basin current identities with append-only general taxonomy membership."""
import copy
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import equatorial_basin_identity_query_v2 as previous

ROOT = Path(__file__).resolve().parents[1]
FILE = 'research/equatorial-basin-identity-query-contract-v3.json'
PROTOCOL = 'plans/equatorial-basin-identity-contract-v3.md'
KEY = 'equatorial_basin_identities_v3'
FACTS, AUDIT, RESULT = previous.FACTS, previous.AUDIT, previous.RESULT
PLANNING, FIGURE, SOURCE, PARENT, EXPECTED = previous.PLANNING, previous.FIGURE, previous.SOURCE, previous.PARENT, previous.EXPECTED
encoded, normalized = previous.encoded, previous.normalized
TAXONOMY_SCOPE = ('Existing editorial identity facets and ledger parent assignments; not flow connectivity, physical containment, '
                  'equivalent identities or inherited measurements. Missing members remain unassessed.')


def read(path):
    return json.loads((ROOT / path).read_bytes())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def build_contract():
    base = previous.build_contract()
    if encoded(base) != (ROOT / previous.FILE).read_bytes():
        raise ValueError('Frozen v2 identity history differs')
    c = copy.deepcopy(base)
    if c['prior_collection_counts']['objects'] != 246 or c['prior_collection_counts']['taxonomy_links'] != 20:
        raise ValueError('Exact246-node20-link installed taxonomy required')
    links = []
    for i, member in enumerate(c['additions']['current_basin_memberships']):
        entity = next(e for e in c['additions']['entities'] if e['id'] == member['entity_id'])
        family = c['prior_family_records'][member['family_entity_id']]['entities'][0]
        links.append({'id': 'taxonomy-link:' + member['current_id'], 'child_id': entity['id'], 'parent_id': family['id'],
                      'child_label': entity['label'], 'parent_label': family['label'],
                      'predicate': 'basin_or_subfamily_member_of',
                      'status': 'editorial_basin_identity_admission_not_physical_connection',
                      'source_file': FILE, 'source_pointer': f'/additions/current_basin_memberships/{i}',
                      'evidence_role': 'reviewed_editorial_basin_qualification',
                      'naming_source_url': 'https://www.tidesandcurrents.noaa.gov/glossary.html',
                      'naming_source_is_parent_relation_evidence': False,
                      'physical_connectivity_eligible': False, 'measurement_inheritance_eligible': False,
                      'scope': TAXONOMY_SCOPE})
    c['additions']['taxonomy_links'] = links
    c['after_collection_counts']['taxonomy_links'] = 25
    c['taxonomy_counts'] = {'before': {'node_count': 246, 'link_count': 20}, 'after': {'node_count': 251, 'link_count': 25}}
    c['schema'] = 'osw.equatorial-basin-identity.query-contract.v3'
    paths = set(c['input_sha256']) | {previous.FILE, previous.PROTOCOL, 'analysis/equatorial_basin_identity_query_v2.py',
            'analysis/equatorial_basin_identity_query_v3.py', PROTOCOL,
            'research/equatorial-basin-delivery-execution-review-v1.json',
            'research/equatorial-basin-engine-run-v1/native-failure.json',
            'research/equatorial-basin-taxonomy-repair-original-bindings-v1.json',
            'research/equatorial-basin-runtime-history-v2/rust/osw-query/src/taxonomy.rs.source'}
    c['input_sha256'] = {p: sha(p) for p in sorted(paths)}
    return c


def taxonomy_projection(manifest, c):
    graph = manifest.get('taxonomy')
    if (not isinstance(graph, dict) or graph.get('schema') != 'osw.query-taxonomy.v1'
            or graph.get('scope') != TAXONOMY_SCOPE or graph.get('complete_physical_taxonomy') is not False
            or graph.get('measurement_inheritance_eligible') is not False
            or any(graph.get(k) != v for k, v in c['taxonomy_counts']['before'].items())):
        raise ValueError('Exact preceding taxonomy scope/counts required')
    receipts = graph.get('source_receipts')
    if not isinstance(receipts, list) or len(receipts) != 2:
        raise ValueError('Two historical taxonomy receipts required')
    paths = set()
    for receipt in receipts:
        path, raw = receipt.get('file'), receipt.get('source_json')
        if not isinstance(raw, str) or path in paths:
            raise ValueError('Invalid historical taxonomy receipt')
        paths.add(path)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        if receipt.get('sha256') != digest or manifest.get('input_sha256', {}).get(path) != digest:
            raise ValueError('Changed historical taxonomy source')
    if paths != {'research/ocean-current-almanac.json', 'research/ocean-motion-taxonomy.json'}:
        raise ValueError('Historical taxonomy source inventory differs')
    result = copy.deepcopy(graph)
    result.update(c['taxonomy_counts']['after'])
    return result


def prepare(collections, manifest, c, *, parent_logical_sha256):
    if parent_logical_sha256 != PARENT:
        raise ValueError('Exact installed logical parent required')
    if encoded(c) != (ROOT / FILE).read_bytes() or c != build_contract():
        raise ValueError('Frozen unmodified contract required')
    if KEY in manifest or previous.KEY in manifest or 'current_basin_memberships' in collections:
        raise ValueError('Repeated or conflicting membership extension')
    if {k: len(v) for k, v in collections.items()} != c['prior_collection_counts']:
        raise ValueError('Installed collection inventory differs')
    for name, rows in collections.items():
        ids = [r.get('id') for r in rows]
        if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
            raise ValueError('Unique IDs required: ' + name)
    ids = set(c['expected_entity_ids'])
    labels = {normalized(r['label']) for r in c['additions']['entities']}
    for name in ['entities', 'objects', 'names']:
        if any(r['id'] in ids or r.get('entity_id') in ids or normalized(r.get('label', '')) in labels for r in collections[name]):
            raise ValueError('Existing identity, qualified alias or partial record: ' + name)
    for ident, prior in c['prior_family_records'].items():
        for name in ['entities', 'objects']:
            if [r for r in collections[name] if r['id'] == ident] != prior[name]:
                raise ValueError('Audited family differs: ' + ident)
        if [r for r in collections['names'] if r.get('entity_id') == ident] != prior['names']:
            raise ValueError('Family aliases differ')
    for row in c['prior_glossary_sources']:
        if [r for r in collections['sources'] if r['id'] == row['id']] != [row]:
            raise ValueError('Historical glossary source differs')
    pins = {**c['input_sha256'], FILE: sha(FILE)}
    inputs = manifest.get('input_sha256', {})
    if any(p in inputs and inputs[p] != pin for p, pin in pins.items()):
        raise ValueError('Historical input rebinding refused')
    graph = taxonomy_projection(manifest, c)
    result = {key: list(rows) for key, rows in collections.items()}
    for name, rows in c['additions'].items():
        existing = {r['id'] for r in result.get(name, [])}
        if any(r['id'] in existing for r in rows):
            raise ValueError('Admission row ID collision: ' + name)
        result[name] = result.get(name, []) + copy.deepcopy(rows)
    final = copy.deepcopy(manifest)
    final.setdefault('input_sha256', {}).update(pins)
    final['taxonomy'] = graph
    final[KEY] = {'contract_file': FILE, 'contract_sha256': sha(FILE), 'parent_logical_sha256': PARENT,
                  'new_identity_ids': c['expected_entity_ids'], 'accepted_current_identities': 111,
                  'new_measurements': 0, 'new_publication_sources': 0, 'physical_geometry_added': False}
    collections.clear()
    collections.update(result)
    manifest.clear()
    manifest.update(final)
