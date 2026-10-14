"""Keep the contour-defined core distinct from total flow and dated sections."""
import copy
import json
import pytest
from check_atlantic_seuc_core_width import ROOT, OWNER, ID, load, record, validate_row, validate_inventory


def test_core_definition_preserves_unresolved_description_and_source_history():
    row = record()
    validate_row(row)
    assert row['approximate_width_km'] == 120
    assert row['width_range_km'] is None
    context = row['original_regional_context']
    assert context['core_threshold_cm_s'] == 20
    assert context['abstract_description_width_km'] == 100
    assert context['geostrophic_reference_prose'] == '1000 m'
    assert context['geostrophic_reference_figure_captions'] == '1000 db'
    assert not context['net_flow_boundaries_resolved']
    assert '2008GL035753' in load()['previous_source_review']['evidence'][0]['url']
    assert row['observed_period'] is None and row['fixed_layer_bounds_m'] is None


@pytest.mark.parametrize('key,value', [
    ('approximate_width_km', 110), ('width_range_km', [100, 120]),
    ('uncertainty_km', 10), ('fixed_layer_bounds_m', [150, 200]),
    ('calendar_months', [1, 7]), ('annual_width_range_km', [100, 120]),
    ('observed_period', {'start': '1978-01-01', 'end': '1980-12-31'}),
    ('width_rank_eligible', True), ('seasonal_playback_eligible', True),
    ('current_id', 'south-equatorial-undercurrent'),
    ('section_geometry', {'type': 'LineString', 'coordinates': [[-35, -4], [-35, -2.5]]}),
])
def test_cannot_invent_range_error_depth_season_or_transfer_owner(key, value):
    row = record()
    row[key] = value
    with pytest.raises(ValueError):
        validate_row(row)


def test_missing_duplicate_and_removed_context_cannot_erase_source_rules():
    document = json.loads((ROOT/'research/ocean-current-width-inventory.json').read_bytes())
    validate_inventory(document)
    for mode in ['missing', 'duplicate', 'context']:
        bad = copy.deepcopy(document)
        row = next(r for r in bad['measurements'] if r['id'] == ID)
        if mode == 'missing': bad['measurements'].remove(row)
        if mode == 'duplicate': bad['measurements'].append(copy.deepcopy(row))
        if mode == 'context': row.pop('original_regional_context')
        with pytest.raises(ValueError): validate_inventory(bad)
    assert next(r for r in document['current_decisions'] if r['current_id'] == OWNER)['whole_current_width_km'] is None
