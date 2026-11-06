"""Versioned planning correction and exact source-bound runtime receipt."""
import copy
import hashlib
import json
from pathlib import Path

import pacific_secc_reference_query_v1 as query

ROOT = query.ROOT
FILE = 'research/pacific-secc-reference-runtime-contract-v1.json'
MODULE = 'analysis/pacific_secc_reference_runtime_v1.py'
PROTOCOL = 'plans/pacific-secc-reference-runtime-protocol-v1.md'
KEY = 'pacific_secc_reference_delivery_v1'
PLANNING = 'research/ocean-current-reference-path-candidates.json'
PLANNING_SHA = 'b06caed27655c39f8127ddda441cba0a856800f599ec52edcd5b30d2ad37b633'
PARENT_LOGICAL = '93c7c184e547ad0c2801ff2183cc5f88f2e11f6150b69b7583fc2f0db05ab696'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':'))


def build_contract():
    source_raw = (ROOT / PLANNING).read_bytes()
    if sha(source_raw) != PLANNING_SHA:
        raise ValueError('Original Pacific route planning source changed')
    plans = json.loads(source_raw)['remaining_current_decisions']
    selected = [r for r in plans if r['current_id'] == query.CURRENT]
    if len(selected) != 1 or selected[0]['candidate_ids'] != []:
        raise ValueError('Exactly one original empty Pacific planning source required')
    contract = query.build_contract()
    raw = (ROOT / query.FILE).read_bytes()
    if raw != query.encoded(contract):
        raise ValueError('Exact frozen source query contract required')
    return {'schema': 'osw.pacific-secc-reference-runtime-contract.v1',
            'status': 'PREPARED_NOT_COMPILED_OR_INSTALLED', 'owner_id': query.TARGET,
            'parent_logical_sha256': PARENT_LOGICAL,
            'original_planning_file': PLANNING, 'original_planning_sha256': PLANNING_SHA,
            'original_planning_source': selected[0],
            'query_contract_file': query.FILE, 'query_contract_sha256': sha(raw),
            'query_contract': contract, 'atlas_report': query.atlas_report(contract),
            'input_sha256': {**contract['input_sha256'], query.FILE: sha(raw), PLANNING: PLANNING_SHA,
                             MODULE: sha((ROOT / MODULE).read_bytes()),
                             PROTOCOL: sha((ROOT / PROTOCOL).read_bytes())}}


def prepare(collections, manifest, contract, *, parent_logical_sha256):
    """Build the complete patch before replacing either caller-owned container."""
    if query.encoded(contract) != query.encoded(build_contract()):
        raise ValueError('Changed Pacific runtime source contract')
    if (parent_logical_sha256 != PARENT_LOGICAL or KEY in manifest
            or manifest.get('input_sha256', {}).get(PLANNING) != PLANNING_SHA):
        raise ValueError('Original source receipt and unapplied runtime required')
    decisions = [r for r in collections.get('route_decisions', []) if r.get('entity_id') == query.TARGET]
    if (len(decisions) != 1 or decisions[0].get('source_decision') != contract['original_planning_source']
            or decisions[0].get('source_catalog_file') != PLANNING
            or decisions[0].get('source_catalog_sha256') != PLANNING_SHA):
        raise ValueError('Exact original Pacific planning projection required')
    before = copy.deepcopy(collections)
    after = copy.deepcopy(collections)
    admission = query.append(after, contract['query_contract'])
    decision = next(r for r in after['route_decisions'] if r['entity_id'] == query.TARGET)
    # Generic Rust planning validation requires both URL projections to agree.
    decision['source_decision']['name_source_url'] = decision['source_url']
    old_owner = next(r for r in before['objects'] if r['id'] == query.TARGET)
    new_owner = next(r for r in after['objects'] if r['id'] == query.TARGET)
    route = next(r for r in after['reference_routes'] if r['id'] == query.ROUTE)
    paper = next(r for r in before['sources'] if r['id'] == admission['publication_source_id'])
    receipt = {'schema': 'osw.pacific-secc-reference-runtime-receipt.v1',
               'parent_logical_sha256': PARENT_LOGICAL,
               'contract_file': FILE, 'contract_sha256': sha(query.encoded(contract)),
               'prior_owner': old_owner, 'prior_decision': copy.deepcopy(decisions[0]),
               'publication_source': copy.deepcopy(paper),
               'owner_fingerprint_json': compact({k: v for k, v in new_owner.items() if k != 'fingerprint'}),
               'section_fingerprint_json': compact(route),
               'new_physical_dimensions': 0, 'installed': False}
    updated_manifest = copy.deepcopy(manifest)
    updated_manifest[KEY] = receipt
    updated_manifest['input_sha256'].update(contract['input_sha256'])
    updated_manifest['input_sha256'][FILE] = receipt['contract_sha256']
    collections.update(after)
    manifest.update(updated_manifest)
    return admission


def catalog_projection(catalog, collections, contract):
    if query.encoded(contract) != query.encoded(build_contract()):
        raise ValueError('Changed runtime contract')
    plans = [r for r in catalog.get('remaining_current_decisions', []) if r.get('current_id') == query.CURRENT]
    if plans != [contract['original_planning_source']]:
        raise ValueError('Exact original Pacific atlas planning source required')
    return query.catalog_projection(catalog, collections, contract['query_contract'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = query.encoded(build_contract())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Runtime contract differs from exact projection')
    print(json.dumps({'status': 'PASS', 'compiled': False, 'installed': False}))
