"""Prepare the independently gated T24 published width; no width reconstruction."""
import argparse
import copy
import json

from build_ocean_motion_claims import review_fingerprint
import indian_current_evidence_query as context
import indian_current_identity_query as identity

ROOT = identity.ROOT
FILE = 'research/eicc-t24-published-width-admission-v1.json'
ENTITY = 'current:east-india-coastal'
WIDTH_ID = 'east-india-coastal-wijesekera-2015-t24-21m-width'
CLAIM_ID = 'claim:width:' + WIDTH_ID
ADMISSION_ID = 'current_measurement_admission:east-india-coastal:t24-2013'
PROTOCOL = 'plans/published-prose-dimension-admission-protocol-v1.md'


def build_contract():
    prepared, dependencies = context.evidence()
    statement = next(row for row in prepared['additions']['current_reported_width_evidence']
                     if row['id'] == 'width-evidence:eicc:wijesekera-2015:t24')
    if (statement['reported_width_km'], statement['width_depth_level_m'], statement['reported_time_window']) != (100, 21, ['2013-12-23', '2013-12-24']):
        raise ValueError('Changed source-reported T24 width support')
    source = next(row for row in prepared['additions']['sources'] if row['id'] == context.WIJ)
    # Full-text passage support is a separate measurement gate, after naming.
    import pymupdf
    import unicodedata
    with pymupdf.open(ROOT / source['original_file']) as pdf:
        text = lambda n: ' '.join(unicodedata.normalize('NFKC', pdf[n - 1].get_text()).split())
        if any(anchor not in text(7) for anchor in ('The EICC at 21 m depth', 'and was about 100 km wide.')):
            raise ValueError('Full primary width passage missing')
        if '23 and 24 December (T24' not in text(2):
            raise ValueError('Full primary T24 survey support missing')
    scope = ('About100km reported for the inbound T24 ship transect on23-24December2013, '
             'approximately along5.25N south of Sri Lanka, in the source description at21m. '
             'No paired edges, numerical cutoff or error specified. Not a whole-current width or annual range.')
    width = {
        'id': WIDTH_ID, 'current_id': 'east-india-coastal', 'entity_id': ENTITY,
        'name': 'East India Coastal Current', 'status': 'editorial_source_extraction_not_historical_release',
        'measurement_type': 'published_regional_summary', 'width_metric': 'author_reported_21m_transect_width',
        'approximate_width_km': 100, 'width_range_km': None, 'source_precision': 'about',
        'range_interpretation': 'One approximate transect summary; not a variability range or uncertainty interval.',
        'geographic_scope': statement['geographic_scope'], 'vertical_scope': statement['vertical_support'],
        'layer': 'Source-associated21m level; no finite width sampling interval established.',
        'source_reported_depth_level_m': 21, 'fixed_layer_bounds_m': None,
        'boundary_rule': 'Author-reported prose width; current-edge coordinates and numerical cutoff unspecified.',
        'boundary_sides': 'author_reported_width_edges_not_supplied',
        'source_id': context.WIJ, 'method_source_id': context.WIDTH_METHOD,
        'source_url': source['url'], 'source_citation': 'Wijesekera et al.2015, doi:10.1002/2015JC010744.',
        'source_locator': 'Section3.2, retained PDF6-7; section2, PDF2 gives T24 dates.',
        'source_access': 'Full NRL-hosted original retained; selected passages reviewed, not a complete scientific paper review.',
        'original_source_file_sha256': source['original_sha256'],
        'extraction_method': 'Direct factual prose extraction under the published prose protocol; no figure digitization or threshold reconstruction.',
        'source_report_file': context.WIDTH, 'source_statement_id': statement['id'],
        'claim_id': CLAIM_ID, 'width_admission_file': FILE,
        'observation_window': ['2013-12-23', '2013-12-24'],
        'observed_period': '2013-12-23/2013-12-24', 'time_precision': 'survey_window_calendar_days',
        'calendar_months': None, 'phase_label': '23-24December2013 inbound T24',
        'phase_kind': 'published_21m_transect_survey_summary',
        'time_convention': 'Transect calendar-day bounds; not exact edge timestamps, monthly climatology or publication dates.',
        'uncertainty_km': None, 'whole_current_width_km': None, 'annual_width_range_km': None,
        'geographic_current_edges': None, 'whole_current_representative': False,
        'width_rank_eligible': False, 'full_width_inference_eligible': False,
        'annual_extrema_eligible': False, 'seasonal_playback_eligible': False,
        'geographic_width_bar_eligible': False, 'is_confidence_interval': False,
        'is_annual_mean': False, 'is_climatology': False, 'source_statements_count': 1,
        'independent_width_samples_admitted': False, 'physical_current_envelope_admitted': False,
        'historical_release_admitted': False,
        'source_quality_note': scope,
        'figure_file': statement['figure_file'], 'figure_sha256': statement['figure_sha256'],
        'figure_scope_note': 'The linked source diagram also shows200/250km statements with other support. This admission selects only T24.',
        'width_admission_id': ADMISSION_ID,
    }
    claim = {
        'id': CLAIM_ID, 'subject_id': ENTITY, 'object_id': None, 'predicate': 'reported_width',
        'value': 100, 'unit': 'km', 'target_collection': 'widths', 'target_id': WIDTH_ID,
        'source_id': context.WIJ, 'method_source_id': context.WIDTH_METHOD,
        'source_locator': width['source_locator'], 'source_locator_status': 'specific',
        'evidence_class': 'published_regional_summary', 'assertion_status': 'reported_or_derived_measurement',
        'scope': scope, 'observation_time': None, 'observation_window': width['observation_window'].copy(),
        'method': PROTOCOL, 'method_status': 'described', 'source_date': None,
        'source_publication_year': 2015, 'source_snapshot_id': None, 'support_claim_id': None,
        'review_status': 'not_individually_reviewed', 'reviewer': None, 'review_date': None,
        'review_note': 'Internal editorial full-passage and scope checks; no external scientific review claimed.',
    }
    claim['review_fingerprint'] = review_fingerprint(claim)
    admission = {
        'id': ADMISSION_ID, 'schema': 'osw.published-prose-width-admission.v1',
        'entity_id': ENTITY, 'current_id': 'east-india-coastal',
        'status': 'scoped_published_width_admitted_measurement_geometry_separately_gated',
        'width_id': WIDTH_ID, 'claim_id': CLAIM_ID, 'source_id': context.WIJ,
        'method_source_id': context.WIDTH_METHOD, 'protocol_file': PROTOCOL,
        'source_report_file': context.WIDTH, 'source_statement_id': statement['id'],
        'scope': scope, 'source_figures_digitized': False, 'full_paper_scientifically_reviewed': False,
        'physical_edges_admitted': False, 'annual_extrema_admitted': False,
        'independent_observations_added': 0, 'raw_width_samples_added': 0,
        'external_scientific_review_claimed': False,
        'historical_source_stage_status_note': 'Frozen source-stage reports remain unchanged. This is a separate later scoped admission, not a rewrite of their earlier pending status.',
    }
    for path in ('analysis/eicc_t24_width_admission.py', PROTOCOL, 'analysis/build_ocean_motion_claims.py'):
        dependencies[path] = identity.pin(path)
    return {'schema': 'osw.eicc-t24-width.query-contract.v1',
        'status': 'prepared_scoped_width_admission_not_yet_in_live_catalogue',
        'canonical_delivery_verified': False, 'input_sha256': dict(sorted(dependencies.items())),
        'width_record': width, 'claim': claim, 'admission': admission,
        'scoped_published_width_records_added': 1, 'raw_width_samples_added': 0,
        'card_links': [
            {'label': 'Query the scoped T24 published width: about100km', 'url': identity.query_url('widths', WIDTH_ID)},
            {'label': 'Read the scoped width admission and limitations', 'url': identity.query_url('current_measurement_admissions', ADMISSION_ID)},
        ]}


def evidence():
    document = build_contract()
    if identity.encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Stale T24 scoped width admission contract')
    return document, {**document['input_sha256'], FILE: identity.pin(FILE)}


def records(document):
    return [('widths', document['width_record']), ('claims', document['claim']),
            ('current_measurement_admissions', document['admission'])]


def append(collections, document):
    if identity.encoded(document) != (ROOT / FILE).read_bytes():
        raise ValueError('Unverified T24 scoped width admission')
    owners = [r for r in collections.get('objects', []) if r['id'] == ENTITY]
    entities = [r for r in collections.get('entities', []) if r['id'] == ENTITY]
    if len(owners) != 1 or len(entities) != 1:
        raise ValueError('Missing or duplicate EICC identity')
    if not any(r['entity_id'] == ENTITY for r in collections.get('current_identity_admissions', [])):
        raise ValueError('Separately gated EICC identity admission required')
    for name, row in records(document):
        existing = collections.get(name, [])
        if not isinstance(existing, list) or any(old['id'] == row['id'] for old in existing):
            raise ValueError('T24 width admission collision in ' + name)
    registry = [r['id'] for r in collections.get('sources', [])]
    if len(registry) != len(set(registry)) or {context.WIJ, context.WIDTH_METHOD} - set(registry):
        raise ValueError('Unresolved T24 width provenance')
    statements = [r for r in collections.get('current_reported_width_evidence', [])
                  if r['id'] == document['width_record']['source_statement_id']]
    if len(statements) != 1 or statements[0]['entity_id'] != ENTITY or statements[0]['reported_width_km'] != 100:
        raise ValueError('Missing or changed T24 source statement')
    owner = copy.deepcopy(owners[0])
    ids = owner.get('width_ids', [])
    if not isinstance(ids, list) or len(ids) != len(set(ids)) or WIDTH_ID in ids:
        raise ValueError('Invalid or duplicate owner width references')
    owner['width_ids'] = [*ids, WIDTH_ID]
    owner['capabilities']['scoped_width'] = len(owner['width_ids'])
    owner['evidence_links'].extend(copy.deepcopy(document['card_links']))
    indexed = copy.deepcopy(statements[0])
    indexed['source_stage_canonical_width_admitted'] = indexed['canonical_width_admitted']
    indexed.update(canonical_width_admitted=True, width_id=WIDTH_ID, width_admission_id=ADMISSION_ID)
    replacements = {name: [*collections.get(name, []), copy.deepcopy(row)] for name, row in records(document)}
    claims = [r for r in replacements['claims'] if ENTITY in (r.get('subject_id'), r.get('object_id'))]
    owner['recorded_claims'] = len(claims)
    owner['claim_review_counts'] = {}
    for row in claims:
        status = row.get('review_status') or 'unspecified'
        if not isinstance(status, str):
            raise ValueError('Invalid claim review metadata')
        owner['claim_review_counts'][status] = owner['claim_review_counts'].get(status, 0) + 1
    owner['section_fingerprints']['claims'] = identity.fingerprint(claims)
    own_widths = [r for r in replacements['widths'] if r.get('current_id') == 'east-india-coastal']
    own_measures = [r for r in collections.get('measurements', []) if r.get('entity_id') == ENTITY]
    owner['section_fingerprints']['measurements'] = identity.fingerprint([own_measures, own_widths, None])
    owner['fingerprint'] = identity.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})
    # All validation and fingerprint preparation precede every mutation.
    collections.update(replacements)
    collections['objects'] = [owner if row['id'] == ENTITY else row for row in collections['objects']]
    collections['current_reported_width_evidence'] = [indexed if row['id'] == indexed['id'] else row for row in collections['current_reported_width_evidence']]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('build', 'check'))
    action = parser.parse_args().action
    if action == 'build':
        (ROOT / FILE).write_bytes(identity.encoded(build_contract()))
    else:
        evidence()
    print('PASS prepared scoped T24 published width admission ' + action)


if __name__ == '__main__':
    main()
