"""Prospective synthetic mutation cases; actual source extraction runs separately."""
import copy
import xml.etree.ElementTree as ET
import pytest
import eacc_regional_connection_v1 as method


def facts():
    return {
        'entity_id': 'current:east-african-coastal',
        'quantity': 'source_reported_approximate_regional_connection_distance',
        'reported_distance_km': 1000, 'approximate': True,
        'reported_latitude_context_degrees': [-11, -3], 'source': {'synthetic': True},
        **{k: None for k in ['longitude_coordinates', 'exact_observation_dates',
                            'fixed_depth_layer_m', 'source_numeric_length_uncertainty_km',
                            'whole_current_length_km', 'annual_length_range_km']},
        **{k: False for k in ['source_gate_coordinates_extracted', 'geodesic_path_computed',
                             'whole_current_rank_eligible', 'seasonal_geometry_eligible',
                             'working_dataset_admitted']},
        'new_physical_geometry_or_state_joins': 0,
    }


@pytest.mark.parametrize('key,value', [
    ('entity_id', 'current:another'), ('quantity', 'whole_current_length'),
    ('reported_distance_km', True), ('reported_distance_km', 0),
    ('reported_distance_km', float('nan')), ('approximate', False),
    ('reported_latitude_context_degrees', [-11, 3]),
    ('longitude_coordinates', [40, 41]), ('exact_observation_dates', ['2020-01-01']),
    ('fixed_depth_layer_m', [0, 50]), ('source_numeric_length_uncertainty_km', 0),
    ('whole_current_length_km', 1000), ('annual_length_range_km', [900, 1100]),
    ('source_gate_coordinates_extracted', True), ('geodesic_path_computed', True),
    ('whole_current_rank_eligible', True), ('seasonal_geometry_eligible', True),
    ('working_dataset_admitted', True), ('new_physical_geometry_or_state_joins', 1),
])
def test_rejects_fabricated_or_reassigned_support(key, value):
    source = facts(); source[key] = value
    with pytest.raises(ValueError): method.project(source)


def test_keeps_scope_and_owns_nested_values():
    source = facts(); before = copy.deepcopy(source)
    output = method.project(source)
    assert output['reported_value_km'] == 1000 and output['approximate'] is True
    assert output['whole_current_length_km'] is None and not output['rank_eligible']
    assert output['observation_window'] is None and output['reported_uncertainty_km'] is None
    assert output['physical_length_lower_bound_km'] is None
    output['latitude_context_degrees_north'][0] = 0
    output['source']['synthetic'] = False
    assert source == before


def test_visual_text_explains_quantity_and_unknowns():
    root = ET.fromstring(method.figure(method.project(facts())))
    text = ' '.join(root.itertext())
    assert root.attrib['aria-labelledby'] == 'title desc'
    for required in ['approximately 1000 km', 'Schematic only', 'annual ranges unknown',
                     'excluded from length ranking', 'not a tracked transit']:
        assert required in text
