"""Synthetic source/context records only; no parent atlas payload loaded."""
import copy
import pytest
import indian_coastal_dimension_context_v1 as batch


def facts():
    source = {'title': 'Synthetic publication', 'year': 2000, 'author': 'Fixture Author',
              'doi': 'synthetic-fixture-not-an-original', 'url': 'https://example.invalid/source',
              'original_sha256': 'a' * 64, 'original_bytes': 100, 'full_paper_visual_review': False,
              'locator': 'Synthetic page1', 'locators': ['Synthetic page2']}
    reach = {'schema': 'osw.reported-regional-reach-source-facts.v1', 'entity_id': batch.EACC,
             'quantity': 'source_reported_approximate_regional_connection_distance',
             'reported_distance_km': 900, 'approximate': True, 'source': copy.deepcopy(source),
             'regional_context': 'Synthetic regional context', 'interpretation': 'Reported connection only.',
             **{key: None for key in ['whole_current_length_km', 'annual_length_range_km',
               'source_numeric_length_uncertainty_km', 'exact_observation_dates', 'fixed_depth_layer_m', 'longitude_coordinates']},
             **{key: False for key in ['whole_current_rank_eligible', 'seasonal_geometry_eligible',
                'working_dataset_admitted', 'source_gate_coordinates_extracted', 'geodesic_path_computed']}}
    cross = {'schema': 'osw.current-coastal-confinement-source-facts.v1', 'entity_id': batch.SJC,
             'quantity': 'sst_associated_coastal_confinement_scale', 'source': copy.deepcopy(source),
             'reported_approximate_extent_range_km': [8, 12], 'reference_boundary': 'Synthetic northern shore',
             'range_meaning': 'Regional proxy extent, not width or error.', 'region': 'Synthetic strait',
             'season_label': 'Source-defined season', 'velocity_observation_years': [1999, 2000],
             'sst_climatology_period_as_reported': 'Synthetic independent climatology',
             **{key: None for key in ['paired_current_width_km', 'fixed_velocity_layer_m',
                'annual_width_range_km', 'numeric_measurement_uncertainty_km', 'calendar_months_assigned_to_this_number']},
             **{key: False for key in ['full_current_width_inference_eligible', 'whole_current_rank_eligible',
                'seasonal_current_geometry_eligible', 'working_dataset_admitted']}}
    return reach, cross


def contract():
    return {'schema': 'osw.indian-coastal-dimension-context.query-contract.v1', 'version': batch.VERSION,
            'canonical_delivery_verified': False, 'additions': batch.project(*facts())}


def parent():
    ids = [batch.EACC, batch.SJC, 'current:unrelated']
    owners = [{'id': entity, 'type': 'named_current', 'source_ids': ['source:old'], 'linked_source_count': 1,
               'capabilities': {'scoped_width': 0, 'geometry': 0}, 'map_features': [], 'published_length_km': None,
               'width_ids': [], 'measurement_ids': [], 'section_fingerprints': {}, 'fingerprint': 'old'} for entity in ids]
    return {'entities': [{'id': entity} for entity in ids], 'objects': owners,
            'sources': [{'id': 'source:old', 'label': 'Preserve me'}], 'claims': [],
            'measurements': [{'id': 'measurement:old', 'value': 42}], 'widths': [{'id': 'width:old'}],
            'geometries': [{'id': 'geometry:old'}], 'width_samples': [], 'length_ranks': [],
            'source_arrays': [{'id': 'array:old', 'values': [1, 2, 3]}]}


def test_two_distinct_source_quantities_are_copied_without_measurement_promotion():
    rows = batch.project(*facts())
    reach = rows['current_regional_reaches'][0];cross = rows['current_cross_shore_context'][0]
    assert reach['constraint']['reported_value_km'] == 900
    assert cross['reported_range_km'] == [8, 12]
    assert reach['constraint']['whole_current_length_km'] is None and cross['paired_current_width_km'] is None
    assert sum(map(len, rows.values())) == 7
    assert '1999, 2000' in cross['time_support_note']


@pytest.mark.parametrize('change', ['none', 'hash', 'bytes', 'boolean_bytes', 'url', 'doi', 'http_status', 'redistribution', 'missing'])
def test_source_identity_must_match_both_original_acquisition_receipts(change):
    documents = facts()
    receipts = [{'source_url': documents[0]['source']['url'], 'bytes': 100, 'sha256': 'a' * 64,
                 'doi': documents[0]['source']['doi']},
                {'url': documents[1]['source']['url'], 'bytes': 100, 'sha256': 'a' * 64,
                 'http_status': 200, 'original_pdf_committed': False}]
    if change == 'hash':receipts[1]['sha256'] = 'b' * 64
    if change == 'bytes':receipts[0]['bytes'] = 101
    if change == 'boolean_bytes':receipts[0]['bytes'] = True
    if change == 'url':receipts[1]['url'] = 'https://example.invalid/different-original'
    if change == 'doi':receipts[0]['doi'] = 'changed-doi'
    if change == 'http_status':receipts[1]['http_status'] = 403
    if change == 'redistribution':receipts[1]['original_pdf_committed'] = True
    if change == 'missing':receipts.pop()
    if change == 'none':batch.validate_custody(documents, receipts)
    else:
        with pytest.raises(ValueError):batch.validate_custody(documents, receipts)


def test_staging_preserves_parent_and_all_physical_collection_instances():
    original = parent();before = copy.deepcopy(original)
    stage, receipt = batch.prepare(original, contract())
    assert original == before and receipt['new_rows'] == 7
    for name in ['entities', 'measurements', 'widths', 'geometries', 'width_samples', 'length_ranks', 'source_arrays']:
        assert stage[name] is original[name]
    assert stage['objects'][2] is original['objects'][2]
    assert stage['sources'][0] == original['sources'][0]
    assert [o['capabilities']['scoped_width'] for o in stage['objects']] == [0, 0, 0]
    assert stage['objects'][0]['regional_reach_ids'] == [batch.REACH]
    assert stage['objects'][1]['cross_shore_context_ids'] == [batch.CONFINEMENT]
    assert receipt['new_paired_widths'] == receipt['new_ranked_lengths'] == 0


@pytest.mark.parametrize('target,field,value', [('reach', 'whole_current_length_km', 900),
 ('reach', 'whole_current_rank_eligible', True), ('reach', 'source_gate_coordinates_extracted', True),
 ('cross', 'paired_current_width_km', 12), ('cross', 'annual_width_range_km', [8, 12]),
 ('cross', 'calendar_months_assigned_to_this_number', [6, 7, 8]), ('cross', 'fixed_velocity_layer_m', [50, 100]),
 ('cross', 'numeric_measurement_uncertainty_km', 2)])
def test_source_facts_cannot_invent_physical_support(target, field, value):
    reach, cross = facts();(reach if target == 'reach' else cross)[field] = value
    with pytest.raises(ValueError):batch.project(reach, cross)


@pytest.mark.parametrize('change', ['owner', 'width', 'rank', 'claim', 'physical_collection', 'source_duplicate'])
def test_bad_contract_rejects_without_partial_parent_mutation(change):
    c = contract();a = c['additions'];original = parent();before = copy.deepcopy(original)
    if change == 'owner':a['current_cross_shore_context'][0]['entity_id'] = batch.EACC
    if change == 'width':a['current_cross_shore_context'][0]['paired_current_width_km'] = 12
    if change == 'rank':a['current_regional_reaches'][0]['constraint']['rank_eligible'] = True
    if change == 'claim':a['claims'][0]['value']['reported_value_km'] = 901
    if change == 'physical_collection':a['widths'] = [{'id': 'width:invented'}]
    if change == 'source_duplicate':original['sources'].append({'id': batch.METHOD});before = copy.deepcopy(original)
    with pytest.raises(ValueError):batch.prepare(original, c)
    assert original == before


@pytest.mark.parametrize('change', ['owner_missing', 'owner_duplicate', 'source_count', 'unresolved_source', 'context_count'])
def test_changed_parent_registry_or_owner_rejects_atomically(change):
    original = parent()
    if change == 'owner_missing':original['objects'].pop(0)
    if change == 'owner_duplicate':original['objects'].append(copy.deepcopy(original['objects'][0]))
    if change == 'source_count':original['objects'][0]['linked_source_count'] = True
    if change == 'unresolved_source':original['objects'][0]['source_ids'] = ['source:missing']
    if change == 'context_count':original['objects'][0]['capabilities']['reported_regional_reaches'] = 1
    before = copy.deepcopy(original)
    with pytest.raises(ValueError):batch.prepare(original, contract())
    assert original == before


def test_repeated_application_rejects_instead_of_duplicating_context():
    stage, _ = batch.prepare(parent(), contract());before = copy.deepcopy(stage)
    with pytest.raises(ValueError):batch.prepare(stage, contract())
    assert stage == before


def test_context_and_claims_preserve_prior_rows_and_recompute_owner_fingerprints():
    original = parent()
    original['claims'] = [{'id': 'claim:old', 'subject_id': batch.EACC, 'review_status': None}]
    original['current_cross_shore_context'] = [{'id': 'context:old', 'entity_id': batch.SJC}]
    original['objects'][1].update(cross_shore_context_ids=['context:old'])
    original['objects'][1]['capabilities']['cross_shore_context'] = 1
    stage, _ = batch.prepare(original, contract())
    assert stage['current_cross_shore_context'][0] is original['current_cross_shore_context'][0]
    assert stage['objects'][1]['cross_shore_context_ids'] == ['context:old', batch.CONFINEMENT]
    assert stage['objects'][0]['claim_review_counts'] == {'not_individually_reviewed': 1, 'unspecified': 1}
    for owner in stage['objects'][:2]:
        assert owner['fingerprint'] == batch.fingerprint({k: v for k, v in owner.items() if k != 'fingerprint'})


@pytest.mark.parametrize('change', ['extra_dimension', 'review_approval', 'delivery_claim'])
def test_context_cannot_smuggle_physical_values_or_approval(change):
    c = contract();original = parent();before = copy.deepcopy(original)
    if change == 'extra_dimension':c['additions']['current_cross_shore_context'][0]['width_km'] = 12
    if change == 'review_approval':c['additions']['claims'][0]['review_status'] = 'scientifically_approved'
    if change == 'delivery_claim':c['canonical_delivery_verified'] = True
    with pytest.raises(ValueError):batch.prepare(original, c)
    assert original == before
