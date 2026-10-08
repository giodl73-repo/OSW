"""Protect cruise identity and prevent unsupported dimensional interpretations."""
import json
import pytest
from build_atlantic_cruise_widths import build, OUTPUT, ROOT
from check_current_width_inventory import validate


def test_extraction_matches_publisher_and_preserves_exclusions():
    document = build()
    assert document == json.loads((ROOT / OUTPUT).read_bytes())
    assert len(document['measurements']) == 32
    assert len({r['current_id'] for r in document['measurements']}) == 9
    assert not {14, 32}.intersection(r['table_2_row'] for r in document['excluded_rows'])
    resolved = [r for r in document['measurements'] if r['hydrographic_section_context']['table_1_row'] == 17]
    assert [(r['current_id'], r['approximate_width_km']) for r in resolved] == [('brazil', 47), ('benguela', 108)]
    for row in resolved:
        context = row['hydrographic_section_context']
        assert context['nominal_section_latitude_degrees_north'] == -24
        assert context['table_1_latitude_label'].startswith('19')
        assert context['nominal_latitude_reconciliation']['archive_section_label'] == 'A09.5_24S'
        assert row['section_geometry'] is None and row['width_rank_eligible'] is False
    malvinas = document['measurements'][0]
    assert malvinas['current_id'] == 'falkland'
    assert malvinas['approximate_width_km'] == 109
    assert malvinas['hydrographic_section_context']['cruise_sampling_window'] == {'start': '1992-12-27', 'end': '1993-01-30'}
    assert [r['approximate_width_km'] for r in document['measurements'] if r['current_id'] == 'canary'] == [310, 215, 289]
    assert [r['approximate_width_km'] for r in document['measurements'] if r['current_id'] == 'irminger'] == [282, 178, 418]


@pytest.mark.parametrize('key,value', [
    ('approximate_width_km', 110), ('width_range_km', [82, 264]),
    ('current_id', 'east-greenland-coastal'), ('fixed_layer_bounds_m', [0, 1206]),
    ('observed_period', {'start': '1992-12-27', 'end': '1993-01-30'}),
    ('calendar_months', [12, 1]), ('section_geometry', {'type': 'LineString', 'coordinates': [[-59.9, -45], [-58.6, -45]]}),
    ('annual_extrema_eligible', True), ('seasonal_playback_eligible', True),
    ('full_width_inference_eligible', True), ('is_confidence_interval', True),
    ('extraction_sha256', 'changed'), ('phase_kind', 'seasonal_summary'),
])
def test_width_inventory_rejects_mutated_identity_values_and_inference(key, value):
    document = json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes())
    ledger = json.loads((ROOT / 'research/ocean-current-almanac.json').read_bytes())
    row = next(r for r in document['measurements'] if r['phase_kind'] == 'inverse_hydrographic_section_span')
    row[key] = value
    with pytest.raises(ValueError): validate(document, ledger)


@pytest.mark.parametrize('key,value', [
    ('cruise_id', '06MT19921227'), ('inverse_model_decade_group', '1992–1993'),
    ('nominal_section_latitude_degrees_north', -30),
    ('source_longitude_limits_degrees_east', [-59.9, -58.5]),
    ('source_depth_extent_m', [0, 650]), ('decade_group_is_time_average', True),
    ('nominal_latitude_is_endpoint_latitude', True),
    ('cruise_sampling_window', {'start': '1992-12-27', 'end': '1992-12-30'}),
    ('source_width_uncertainty_km', 2),
])
def test_width_inventory_rejects_changed_source_context(key, value):
    document = json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes())
    ledger = json.loads((ROOT / 'research/ocean-current-almanac.json').read_bytes())
    row = next(r for r in document['measurements'] if r['phase_kind'] == 'inverse_hydrographic_section_span')
    row['hydrographic_section_context'][key] = value
    with pytest.raises(ValueError): validate(document, ledger)


def test_width_inventory_rejects_unproven_2018_reconciliation():
    document = json.loads((ROOT / 'research/ocean-current-width-inventory.json').read_bytes())
    ledger = json.loads((ROOT / 'research/ocean-current-almanac.json').read_bytes())
    row = next(r for r in document['measurements'] if r['id'] == 'cainzos-2023-t02-row-14-section-span')
    row['hydrographic_section_context']['nominal_latitude_reconciliation']['source_sha256'] = 'invented'
    with pytest.raises(ValueError): validate(document, ledger)
