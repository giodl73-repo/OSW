"""Explicit audited publication insertion and direct atlas navigation supplement."""
import argparse
import copy
import json

import pacific_secc_reference_runtime_v1 as runtime
import pacific_secc_reference_query_v1 as query

ROOT = query.ROOT
FILE = 'research/pacific-secc-reference-publication-admission-v1.json'
MODULE = 'analysis/pacific_secc_publication_admission_v1.py'
PROTOCOL = 'plans/pacific-secc-publication-admission-v1.md'
AUDIT = 'research/pacific-secc-parent-audit-result-v1.json'
SELECTED = 'research/pacific-secc-parent-audit-selected-records-v1.json'
SELECTED_SHA = '06f646ecaecdea3a1eb97f915d71fec5be63fadbafb8da7f88a465c88aa55009'
AUDIT_SHA = '6238f7fe553527f7dd5bc7b14bc20ca52787c700c801ea072bda25f1ac0a5c80'
PAPER = 'source:chen-qiu-secc-seasonal-2004'


def read_selected():
    raw = (ROOT / SELECTED).read_bytes()
    if runtime.sha(raw) != SELECTED_SHA:
        raise ValueError('Changed exact installed Pacific parent metadata')
    return json.loads(raw)


def build_contract():
    selected = read_selected()
    raw = (ROOT / AUDIT).read_bytes()
    if runtime.sha(raw) != AUDIT_SHA:
        raise ValueError('Changed installed publication audit receipt')
    audit = json.loads(raw)
    if (audit['logical_sha256'] != runtime.PARENT_LOGICAL or audit['publication_candidate_count'] != 0
            or audit['selected_records_sha256'] != SELECTED_SHA or audit['collection_counts']['sources'] != 208
            or audit['exact_original_planning_source_matches'] is not True
            or selected['owner']['route_url'] is not None):
        raise ValueError('Exact missing-publication and navigation audit required')
    candidate = json.loads((ROOT / query.CANDIDATE).read_bytes())
    query.build_contract()  # Verify all executed candidate/map/source evidence pins.
    paper = {'id': PAPER, 'kind': 'external', 'doi': query.DOI, 'url': query.URL,
             'title': 'Seasonal variability of the South Equatorial Countercurrent',
             'label': 'Chen and Qiu (2004): Pacific SECC mean circulation and seasonal variability',
             'publication_year': 2004, 'source_citation': candidate['source_citation'],
             'access_scope': 'Original author-hosted PDF reviewed; mean-field and anomaly contexts kept separate.',
             'original_asset_sha256': candidate['source_original']['sha256'],
             'original_asset_retained': True, 'provider_asset_redistributed': False,
             'source_curves_digitized': False}
    return {'schema': 'osw.pacific-secc-publication-admission.v1',
            'status': 'SOURCE_SUPPLEMENT_PREPARED_NOT_INSTALLED',
            'owner_id': query.TARGET, 'parent_logical_sha256': runtime.PARENT_LOGICAL,
            'prior_source_count': 208, 'publication_source': paper,
            'audited_prior_owner': selected['owner'], 'audited_prior_decision': selected['planning_decision'],
            'audited_owner_sources': selected['owner_sources'],
            'atlas_route_url': query.build_contract()['atlas_url_after_installation'],
            'audited_selected_records_sha256': SELECTED_SHA,
            'input_sha256': {p: runtime.sha((ROOT / p).read_bytes()) for p in
                              [AUDIT, SELECTED, MODULE, PROTOCOL, runtime.FILE, query.FILE]},
            'new_publication_records': 1, 'new_physical_dimensions': 0,
            'new_independent_observations': 0}


def prepare(collections, manifest, document, *, parent_logical_sha256):
    if query.encoded(document) != query.encoded(build_contract()) or parent_logical_sha256 != runtime.PARENT_LOGICAL:
        raise ValueError('Exact audited publication admission required')
    selected = read_selected()
    for name, key in [('objects', 'owner'), ('entities', 'entity'), ('route_decisions', 'planning_decision')]:
        rows = [r for r in collections.get(name, []) if r.get('id') == selected[key]['id']]
        if rows != [selected[key]]:
            raise ValueError('Actual installed parent differs from audited ' + key)
    sources = collections.get('sources')
    ids = query.checked_ids(sources, 'sources')
    if len(sources) != document['prior_source_count'] or PAPER in ids or query.METHOD in ids:
        raise ValueError('Changed source registry or publication-ID collision')
    # Include title aliases, even when an old source omitted its DOI and author URL.
    for source in sources:
        text = json.dumps(source, ensure_ascii=False).lower()
        if (query.DOI.lower() in text or 'cq04.pdf' in text
                or ('seasonal variability' in text and 'south equatorial countercurrent' in text)):
            raise ValueError('Existing equivalent publication requires explicit reconciliation')
    if [r for r in sources if r['id'] in selected['owner']['source_ids']] != selected['owner_sources']:
        raise ValueError('Audited prior owner source records changed')
    after = dict(collections)
    after['sources'] = [*sources, copy.deepcopy(document['publication_source'])]
    updated_manifest = copy.deepcopy(manifest)
    runtime.prepare(after, updated_manifest, runtime.build_contract(), parent_logical_sha256=parent_logical_sha256)
    owner = next(r for r in after['objects'] if r['id'] == query.TARGET)
    owner['route_url'] = document['atlas_route_url']
    owner['fingerprint'] = query.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    receipt = updated_manifest[runtime.KEY]
    receipt['owner_fingerprint_json'] = runtime.compact({k: v for k, v in owner.items() if k != 'fingerprint'})
    receipt['publication_admission'] = copy.deepcopy(document)
    updated_manifest['input_sha256'].update(document['input_sha256'])
    updated_manifest['input_sha256'][FILE] = runtime.sha(query.encoded(document))
    collections.update(after)
    manifest.update(updated_manifest)
    return {'publication_added': True, 'publication_source_id': PAPER,
            'new_source_records': 2, 'new_reference_routes': 1, 'new_physical_dimensions': 0, 'installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check'])
    args = parser.parse_args()
    raw = query.encoded(build_contract())
    if args.action == 'build':
        (ROOT / FILE).write_bytes(raw)
    elif (ROOT / FILE).read_bytes() != raw:
        raise ValueError('Publication supplement differs')
    print(json.dumps({'status': 'PASS', 'installed': False, 'new_publication_records': 1}))
