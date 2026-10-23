"""Prospective synthetic cases only; no actual report is executed here."""
import copy
import xml.etree.ElementTree as ET

import pytest

import published_current_regional_reaches_v2 as method


def fixture():
    return {'entity_id': 'current:synthetic', 'current_id': 'synthetic',
            'reported_value_km': 42, 'quantity': 'reported_initial_regional_reach',
            'relation': 'source_reported_value', 'source_uncertainty_km': None,
            'physical_length_lower_bound_km': None, 'reported_observation_window': None,
            'time_support_kind': 'unspecified_textbook_synthesis_not_publication_or_revision_date',
            'upstream_latitude_context_degrees_north': -10,
            'upstream_latitude_qualifier': 'near', 'upstream_longitude_degrees_east': None,
            'downstream_endpoint_coordinates': None,
            'source_kind': 'textbook_synthesis_not_a_new_observation_campaign',
            'numeric_precision': 'Published round number; exact physical equality unestablished.',
            'vertical_support': 'Unspecified',
            **{key: False for key in method.PROHIBITED}}


def test_reported_value_is_not_promoted_to_a_bound_or_equality():
    facts = fixture(); before = copy.deepcopy(facts)
    result = method.constraint(facts)
    assert result['reported_value_km'] == 42
    assert result['relation'] == 'source_reported_value'
    assert result['display'] == '42 km'
    assert result['study_window'] is None
    assert result['physical_length_lower_bound_km'] is None
    assert result['whole_current_length_km'] is None
    assert result['reported_uncertainty_km'] is None
    assert not result['rank_eligible']
    assert facts == before


@pytest.mark.parametrize('value', [0, -1, True, None, '42', float('nan'), float('inf')])
def test_invalid_numeric_values_reject(value):
    facts = fixture(); facts['reported_value_km'] = value
    with pytest.raises(ValueError): method.constraint(facts)


@pytest.mark.parametrize('field,value', [
    ('quantity', 'whole_current_length'), ('relation', 'eq'), ('relation', 'ge'), ('relation', 'gt'),
    ('source_uncertainty_km', 0), ('physical_length_lower_bound_km', 42),
    ('reported_observation_window', ['1994-01-01', '2002-09-30']),
    ('time_support_kind', 'publication_date'), ('upstream_longitude_degrees_east', 0),
    ('downstream_endpoint_coordinates', [-38, -50]), ('upstream_latitude_qualifier', 'exact'),
    ('upstream_latitude_context_degrees_north', 91), ('upstream_latitude_context_degrees_north', True),
    ('upstream_latitude_context_degrees_north', float('nan')),
    ('entity_id', 'current:another'), ('source_kind', 'dated_observation_campaign')])
def test_invented_support_and_changed_scope_reject(field, value):
    facts = fixture(); facts[field] = value
    with pytest.raises(ValueError): method.constraint(facts)


@pytest.mark.parametrize('field', method.PROHIBITED)
def test_physical_promotions_reject(field):
    facts = fixture(); facts[field] = True
    with pytest.raises(ValueError): method.constraint(facts)


def test_figure_has_explicit_accessible_limits_without_geographic_path_claim():
    output = method.figure({'constraint': method.constraint(fixture())})
    tree = ET.fromstring(output)
    text = ' '.join(tree.itertext())
    assert tree.attrib['aria-labelledby'] == 'title desc'
    assert '42 km' in text and 'observation dates unspecified' in text
    assert 'Downstream coordinates unspecified' in text
    assert 'numerical uncertainty not reported' in text
    assert 'not a geographic axis or a physical length lower bound' in text
    assert 'Neither dates this reach' in text


def test_projection_owns_its_values():
    facts = fixture(); result = method.constraint(facts)
    result['reported_value_km'] = 99
    result['study_window'] = ['2000-01-01', '2001-01-01']
    assert facts == fixture()
