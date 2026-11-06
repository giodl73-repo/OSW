"""Prepare qualified source context without manufacturing measured coverage."""
import argparse
import copy
import json

import indian_current_identity_query as identity

ROOT = identity.ROOT
FILE = 'research/indian-current-evidence-query-contract-v1.json'
CALENDAR = 'research/indian-current-reported-direction-calendars-v1.json'
WIDTH = 'research/eicc-wijesekera-2015-width-evidence-v1.json'
OFFSHORE = 'research/eacc-painter-2020-cross-shore-source-facts-v1.json'
REGIME = 'research/wicc-march-1994-regime-source-facts-v1.json'
PINS = {
    CALENDAR: 'ea1399d45121884279686675d0cc8f42200fd59ac14e9203d38f77e40c401374',
    WIDTH: '4a452eeafa4c95a3afafac470bb6858819d748b81b1a4bb43219c8737175479b',
    OFFSHORE: 'd2c780825fc32bef542fd6a17b8bc2e8769e3efff9b39159368781351b62200e',
    REGIME: '0c02420dfe2f68cfce6ce106d8db0aa669d78f3ce2ed54038c0458dcc70bc3d1',
    'figures/indian-current-reported-direction-calendars-v1.svg': 'a9528d58a4af9a34fead12d50d47642c6f31ac6b6a182f17712f2cfa9fa34cac',
    'figures/eicc-wijesekera-2015-width-evidence-v1.svg': '63616a738d10e181afc4b04f33b9b082c9be2f6cdc44bc9d9a16f6298c37055e',
}
SHE = 'source:direction-wicc-shetye-1998'
VIJ = 'source:wicc-march-1994-vijith-2022'
WIJ = 'source:eicc-width-wijesekera-2015'
PAI = 'source:eacc-context-painter-2020'
CAL_METHOD = 'source:reported-current-direction-calendar-v1'
WIDTH_METHOD = 'source:reported-current-width-evidence-v1'
OWNER_FIELDS = {
    'current_direction_calendars': ('direction_calendar_ids', 'direction_calendars'),
    'current_direction_descriptions': ('direction_description_ids', 'direction_descriptions'),
    'current_reported_width_evidence': ('reported_width_evidence_ids', 'reported_width_evidence'),
    'current_cross_shore_context': ('cross_shore_context_ids', 'cross_shore_context'),
    'current_regime_context': ('regime_context_ids', 'regime_context'),
}


def build_contract():
    _, dependencies = identity.evidence()
    for path, expected in PINS.items():
        if identity.pin(path) != expected:
            raise ValueError('Changed reviewed source context: ' + path)
    read = lambda path: json.loads((ROOT / path).read_bytes())
    calendar, width, offshore, regime = [read(path) for path in (CALENDAR, WIDTH, OFFSHORE, REGIME)]
    dependencies.update(PINS)
    for doc in (calendar, width):
        for path, expected in doc['input_sha256'].items():
            if identity.pin(path) != expected:
                raise ValueError('Frozen source dependency differs: ' + path)
            dependencies[path] = expected
    for source in (width['source_facts']['source'], offshore['source']):
        path = source['original_file']
        if identity.pin(path) != source['original_sha256'] or (ROOT / path).stat().st_size != source['original_bytes']:
            raise ValueError('Changed retained source original: ' + path)
        dependencies[path] = source['original_sha256']
        dependencies[source['acquisition_receipt']] = identity.pin(source['acquisition_receipt'])
    dependencies['analysis/indian_current_evidence_query.py'] = identity.pin('analysis/indian_current_evidence_query.py')
    rows = {key: [] for key in (*OWNER_FIELDS, 'sources')}
    wicc_profile = calendar['profiles'][0]
    rows['sources'] = [
        {'id': SHE, 'kind': 'external', 'label': wicc_profile['source_title'], 'title': wicc_profile['source_title'],
         'doi': wicc_profile['source_doi'], 'url': wicc_profile['source_url'],
         'authors': [wicc_profile['source_author']], 'publication_year': wicc_profile['publication_year'],
         'access_scope': wicc_profile['access_scope'], 'source_locator': wicc_profile['source_locator'],
         'original_asset_retained': False, 'provider_asset_redistributed': False,
         'full_original_independently_checked': False, 'rights_note': wicc_profile['rights_note']},
        {'id': VIJ, 'kind': 'external', 'label': regime['source_title'], 'title': regime['source_title'],
         'doi': regime['source_doi'], 'url': regime['source_url'], 'source_locator': regime['source_locator'],
         'authors': copy.deepcopy(regime['source_authors']), 'publication_date': regime['publication_date'],
         'access_scope': regime['access_scope'], 'original_asset_retained': False,
         'provider_asset_redistributed': False, 'full_paper_reviewed': False, 'rights_note': regime['rights_note']},
    ]
    for source_id, source, redistributed in [(WIJ, width['source_facts']['source'], False), (PAI, offshore['source'], True)]:
        rows['sources'].append({
            'id': source_id, 'kind': 'external', 'label': source['title'], 'title': source['title'],
            'doi': source['doi'], 'url': source['publisher_url'], 'original_url': source['original_url'],
            'authors': copy.deepcopy(source['authors']),
            'publication_year': source.get('publication_year'), 'publication_date': source.get('publication_date'),
            'original_file': source['original_file'], 'original_sha256': source['original_sha256'],
            'document_identity_sha256': source['original_sha256'], 'original_bytes': source['original_bytes'],
            'original_pages': source['original_pdf_pages'], 'custody_file': source['acquisition_receipt'],
            'access_scope': 'retained_full_original_selected_passages_reviewed',
            'source_kind': 'published_review_synthesis_not_new_width_observations' if source_id == PAI else 'published_article_source_reported_width_context',
            'license': source.get('license'),
            'provider_asset_redistributed': redistributed, 'full_paper_reviewed': False,
            'selected_reviewed_pdf_pages': source['selected_pdf_pages_visually_reviewed'],
            'rights_note': source.get('rights_note', 'CC-BY-4.0 original; attribution and license link retained in acquisition receipt.'),
            'metadata_note': 'Scoped source statements, not another independent observation campaign.',
        })
    for source_id, protocol in [(CAL_METHOD, calendar['protocol_file']), (WIDTH_METHOD, width['method'])]:
        rows['sources'].append({'id': source_id, 'kind': 'internal', 'label': protocol,
            'title': protocol, 'path': protocol, 'url': '../' + protocol,
            'provider_asset_redistributed': False,
            'metadata_note': 'Source extraction/description method; no invented observations or physical geometry.'})
    for profile in calendar['profiles']:
        source_id = SHE if profile['entity_id'] == 'current:west-india-coastal' else identity.PRIMARY
        refs = sorted({source_id, identity.PRIMARY, CAL_METHOD})
        calendar_id = 'direction-calendar:' + profile['id']
        record = {key: copy.deepcopy(value) for key, value in profile.items() if key != 'months'}
        record.update(id=calendar_id, source_profile_id=profile['id'], source_id=source_id,
            source_ids=refs, method_source_id=CAL_METHOD,
            description_ids=[row['id'] for row in profile['months']],
            source_file=CALENDAR, source_file_sha256=PINS[CALENDAR],
            figure_file='figures/indian-current-reported-direction-calendars-v1.svg',
            figure_sha256=PINS['figures/indian-current-reported-direction-calendars-v1.svg'],
            is_observation=False, calendar_month_highlight_eligible=True,
            geographic_seasonal_playback_eligible=False,
            unknown_month_meaning=calendar['unknown_month_meaning'],
            variability_note=calendar['variability_note'] if source_id == SHE else 'Source annual orientation is not a guarantee of direction at every observed instant.')
        rows['current_direction_calendars'].append(record)
        for month in profile['months']:
            rows['current_direction_descriptions'].append({**copy.deepcopy(month),
                'calendar_id': calendar_id, 'source_id': source_id, 'source_ids': refs.copy(),
                'method_source_id': CAL_METHOD, 'source_file': CALENDAR,
                'source_file_sha256': PINS[CALENDAR], 'source_locator': profile['source_locator'],
                'time_support_kind': profile['time_support_kind'],
                'geographic_seasonal_playback_eligible': False})
    for statement in width['source_facts']['reported_widths']:
        rows['current_reported_width_evidence'].append({**copy.deepcopy(statement),
            'entity_id': width['source_facts']['entity_id'], 'source_id': WIJ, 'method_source_id': WIDTH_METHOD,
            'record_role': 'reported_source_statement_not_canonical_width_sample',
            'source_file': WIDTH, 'source_file_sha256': PINS[WIDTH],
            'figure_file': 'figures/eicc-wijesekera-2015-width-evidence-v1.svg',
            'figure_sha256': PINS['figures/eicc-wijesekera-2015-width-evidence-v1.svg'],
            'annual_width_range_km': None, 'geographic_width_geometry': None,
            'independent_observations_added': 0, 'ranking_eligible': False,
            'physical_seasonal_playback_eligible': False,
            'scope_reconciliation': width['source_facts']['scope_reconciliation']})
    for descriptor in offshore['cross_shore_descriptors']:
        rows['current_cross_shore_context'].append({**copy.deepcopy(descriptor),
            'entity_id': offshore['entity_id'], 'source_id': PAI,
            'source_file': OFFSHORE, 'source_file_sha256': PINS[OFFSHORE],
            'source_locator': offshore['source']['source_locator'],
            'source_kind': offshore['source']['source_kind'],
            'source_dependency': copy.deepcopy(offshore['source_dependency']),
            'canonical_width_admitted': False, 'geographic_width_geometry': None,
            'ranking_eligible': False, 'physical_seasonal_playback_eligible': False})
    rows['current_regime_context'].append({
        'id': regime['id'], 'entity_id': regime['entity_id'], 'source_id': VIJ,
        'record_role': 'dated_qualitative_survey_context_not_monthly_climatology',
        'source_file': REGIME, 'source_file_sha256': PINS[REGIME],
        'source_locator': regime['source_locator'], 'access_scope': regime['access_scope'],
        'reported_hydrographic_survey_window': copy.deepcopy(regime['reported_hydrographic_survey_window']),
        'date_precision': regime['date_precision'], 'window_meaning': regime['window_meaning'],
        'reported_altimeter_archive_year': regime['reported_altimeter_archive_year'],
        'altimeter_sample_window': None, 'source_reported_regime': regime['source_reported_regime'],
        'relation_to_direction_calendar': regime['relation_to_direction_calendar'],
        'zero_current_claimed': False, 'monthly_climatology_inferred': False,
        'named_eddies_admitted': [], 'length_km': None, 'width_km': None, 'velocity_m_s': None,
        'annual_dimension_ranges': None, 'physical_geometry_admitted': False,
        'state_intersections_admitted': False, 'ranking_eligible': False})
    return {'schema': 'osw.indian-current-evidence.query-contract.v1',
        'status': 'prepared_source_context_not_yet_in_canonical_bundle',
        'canonical_delivery_verified': False, 'independent_observations_added': 0,
        'canonical_width_samples_added': 0, 'input_sha256': dict(sorted(dependencies.items())),
        'additions': rows,
        'next_gate': 'Atomic identity/evidence/reach admission, complete source projection, typed native/WASM validation and accessible source-qualified object/card delivery.'}


def evidence():
    document = build_contract()
    if identity.encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Stale prepared Indian evidence query contract')
    return document, {**document['input_sha256'], FILE: identity.pin(FILE)}


def append(collections, document):
    """Source-verified document first; reject every failure before mutation."""
    if identity.encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Unverified Indian source-context query contract')
    rows = document['additions']
    owners = {}
    for entity_id in identity.EXPECTED:
        matches = [r for r in collections.get('objects', []) if r['id'] == entity_id]
        entities = [r for r in collections.get('entities', []) if r['id'] == entity_id]
        if len(matches) != 1 or len(entities) != 1:
            raise ValueError('Missing or duplicate separately admitted current identity')
        owners[entity_id] = matches[0]
    for name, additions in rows.items():
        existing = collections.get(name, [])
        if not isinstance(existing, list):
            raise ValueError('Source-context collection must be a record list')
        ids = [row['id'] for row in existing]
        extra = [row['id'] for row in additions]
        if len(ids) != len(set(ids)) or len(extra) != len(set(extra)) or set(ids) & set(extra):
            raise ValueError('Source-context record collision in ' + name)
    registry = {row['id'] for row in [*collections.get('sources', []), *rows['sources']]}
    updates = {}
    for entity_id, owner in owners.items():
        refs = owner.get('source_ids', [])
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs) or len(refs) != len(set(refs)):
            raise ValueError('Invalid existing owner source references')
        count = owner.get('linked_source_count')
        if type(count) is not int or count != len(refs) or set(refs) - registry:
            raise ValueError('Existing owner source registry/count mismatch')
        result = copy.deepcopy(owner)
        owned_rows = []
        for collection, (field, capability) in OWNER_FIELDS.items():
            additions = [r for r in rows[collection] if r['entity_id'] == entity_id]
            prior = result.get(field, [])
            if not isinstance(prior, list) or len(prior) != len(set(prior)) or set(prior) & {r['id'] for r in additions}:
                raise ValueError('Invalid or duplicate source-context owner references')
            result[field] = prior + [r['id'] for r in additions]
            result['capabilities'][capability] = len(result[field])
            owned_rows.extend(additions)
            if additions:
                result['evidence_links'].append({'label': 'Query qualified ' + capability.replace('_', ' '),
                    'url': identity.query_url(collection, additions[0]['id'])})
        for row in owned_rows:
            refs = set(row.get('source_ids', [])) | {row['source_id']}
            if row.get('method_source_id'):
                refs.add(row['method_source_id'])
            if refs - registry:
                raise ValueError('Unresolved source-context provenance')
            result['source_ids'] = sorted(set(result['source_ids']) | refs)
        result['linked_source_count'] = len(result['source_ids'])
        figures = sorted({r['figure_file'] for r in owned_rows if r.get('figure_file')})
        result['evidence_links'].extend({'label': 'View source-qualified evidence diagram', 'url': '../' + path} for path in figures)
        result['section_fingerprints']['source_context'] = identity.fingerprint(owned_rows)
        result['fingerprint'] = identity.fingerprint({k: v for k, v in result.items() if k != 'fingerprint'})
        updates[entity_id] = result
    for name, additions in rows.items():
        collections.setdefault(name, []).extend(copy.deepcopy(additions))
    collections['objects'] = [updates.get(row['id'], row) for row in collections['objects']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'check'))
    action = parser.parse_args().action
    if action == 'build':
        (ROOT / FILE).write_bytes(identity.encoded(build_contract()))
    else:
        evidence()
    print('PASS prepared Indian source-context query contract ' + action)


if __name__ == '__main__':
    main()
