"""Protect the Antilles source join, conflicts and dimensional limits."""
import copy
import json
import pytest
import build_antilles_cainzos_section_spans as source


def test_original_tables_reconstruct_three_distinct_cruise_spans():
    actual=source.build()
    assert actual==json.loads((source.ROOT/source.OUTPUT).read_bytes())
    rows=actual['measurements']
    assert [r['approximate_width_km'] for r in rows]==[125,38,39]
    assert [r['hydrographic_section_context']['source_depth_extent_m'] for r in rows]==[[0,736],[0,758],[0,704]]
    assert [r['hydrographic_section_context']['cruise_id'] for r in rows]==['29HE19920714','74DI20040404','29AH20110128']
    assert [c['point_count'] for c in actual['measurement_contexts']]==[101,114,153]


def test_scope_preserves_conflicts_and_does_not_invent_dimensions():
    actual=source.build()
    assert actual['source_conflicts'][0]['source_phrase']=='from Cape Hatteras'
    assert actual['source_conflicts'][1]['table_value_km']==39
    assert actual['source_conflicts'][1]['prose_approximate_value_km']==38
    assert actual['prior_values_viewed_before_protocol'] is True and actual['fully_blinded'] is False
    for r in actual['measurements']:
        assert r['width_range_km'] is None and r['section_geometry'] is None
        assert r['fixed_layer_bounds_m'] is None and r['observed_period'] is None
        for key in ['whole_current_representative','width_rank_eligible','annual_extrema_eligible','seasonal_playback_eligible','full_width_inference_eligible','is_confidence_interval']:
            assert r[key] is False,key
        assert r['hydrographic_section_context']['nominal_latitude_is_endpoint_latitude'] is False
    # Actual western station tracks differ from the nominal section latitude.
    western=[p for p in actual['measurement_contexts'][1]['points'] if -77<p['coordinates'][0]<-76]
    assert western and all(26<p['coordinates'][1]<27 for p in western)


@pytest.mark.parametrize('mutation',['distance','cruise'])
def test_reject_changed_distance_or_wrong_cruise_join(monkeypatch,mutation):
    original=source.read_cells
    def changed(path):
        rows=copy.deepcopy(original(path))
        for r in rows:
            if mutation=='distance' and path.endswith('table-2.xlsx') and r['row']==53:r['cells']['D']=38
            if mutation=='cruise' and path.endswith('table-1.xlsx') and r['row']==18:r['cells']['D']='different-cruise'
        return rows
    monkeypatch.setattr(source,'read_cells',changed)
    with pytest.raises(ValueError,match='publisher cruise join'):source.build()


def test_reject_archive_identity_mismatch(monkeypatch):
    original=source.parse_events
    def changed(*args):
        events=original(*args)
        for e in events:e['archive_section_label']='A09'
        return events
    monkeypatch.setattr(source,'parse_events',changed)
    with pytest.raises(ValueError,match='archive cruise identity'):source.build()


def test_reject_absent_compatible_sampling_context(monkeypatch):
    monkeypatch.setattr(source,'context_points',lambda *args:[])
    with pytest.raises(ValueError,match='dated hydrographic sampling'):source.build()
