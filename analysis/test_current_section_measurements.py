"""Typed records retain every source case and explicit local-only scope."""
import json
import pytest
import current_section_measurements as adapter


def test_all_sixty_cases_and_nulls_are_queryable():
    rows,pins=adapter.build()
    assert len(rows)==len({r['id'] for r in rows})==60
    assert sum(r['component_span_km'] is not None for r in rows)==14
    assert sum(r['is_primary_convention'] for r in rows)==4
    assert sum(r['component_span_km'] is not None and r['saline_outflow_screen'] is False for r in rows)==4
    assert [sum(r['campaign']==campaign for r in rows) for campaign in ['RSX1','RSX2']]==[30,30]
    for row in rows:
        source=json.loads((adapter.ROOT/row['source_file']).read_bytes())
        parts=row['source_pointer'].split('/')[1:]
        layer=source[parts[0]][int(parts[1])]
        case=layer['cases'][int(parts[3])]
        assert row['source_case']==case
        assert row['component_span_km']==case['span_km']
        assert row['branch']==case['branch']
        assert [row['height_low_m'],row['height_high_m']]==layer['height_layer_m']
        assert row['source_file_sha256']==pins[row['source_file']]
        assert row['metric']=='local_section_normal_component_span'
        assert row['rank_eligible'] is False and row['current_association_verified'] is False
        assert row['whole_current_width_km'] is None and row['annual_width_range_km'] is None


def test_changed_provider_is_not_silently_adapted(monkeypatch):
    original=adapter.Path.read_bytes
    target=adapter.ROOT/adapter.PROVIDERS[1][0]
    def altered(path):
        raw=original(path)
        return raw+b' ' if path==target else raw
    monkeypatch.setattr(adapter.Path,'read_bytes',altered)
    with pytest.raises(ValueError):adapter.build()
