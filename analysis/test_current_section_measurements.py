"""Typed records retain every source case and explicit local-only scope."""
import json
import pytest
import current_section_measurements as adapter


def test_all_sixty_cases_and_nulls_are_queryable():
    all_rows,pins=adapter.build()
    rows=[r for r in all_rows if r['current_id']=='red-sea-saline-overflow']
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
        assert row['vertical_reference']=='height_above_bottom'
        assert row['component_frame']=='local_section_right_normal'
        assert row['depth_low_m'] is None and row['depth_high_m'] is None
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


def test_asca_cases_retain_dates_vertical_frame_and_all_failures():
    rows,pins=adapter.build()
    assert len(rows)==len({r['id'] for r in rows})==2853
    rows=[r for r in rows if r['current_id']=='agulhas']
    source=json.loads((adapter.ROOT/adapter.ASCA_PROVIDER[0]).read_bytes())
    assert len(rows)==2793
    assert sum(r['component_span_km'] is not None for r in rows)==1007
    primary=[r for r in rows if r['is_primary_convention']]
    assert len(primary)==931 and sum(r['component_span_km'] is not None for r in primary)==330
    assert len({(r['year'],r['month']) for r in rows})==27
    for row in rows:
        _,_,pi,_,ci=row['source_pointer'].split('/')
        profile=source['profiles'][int(pi)];case=profile['cases'][int(ci)]
        assert row['source_case']==case
        assert row['component_span_km']==case['span_km']
        assert row['boundary_fraction']==case['fraction']
        assert row['is_primary_convention']==case['primary']
        assert row['observation_start_utc']==row['observation_end_utc']==profile['observed_at']
        assert row['source_profile_id']==profile['source_profile_id']
        assert row['vertical_reference']=='depth_below_surface'
        assert row['component_frame']=='source_fixed_array_negative_v'
        assert row['depth_low_m']==row['depth_high_m']==100
        assert row['height_low_m'] is None and row['height_high_m'] is None
        assert row['normal_component_velocity_offset_m_s'] is None
        assert row['branch'] is None and row['saline_outflow_screen'] is None
        assert row['tides_removed'] is None
        assert row['metric']=='fixed_array_southwestward_v_component_span'
        assert row['time_support']=='filtered_mapped_source_timestamp'
        assert row['rank_eligible'] is False and row['current_association_verified'] is False
        assert row['whole_current_width_km'] is None and row['annual_width_range_km'] is None
        assert row['source_file_sha256']==pins[row['source_file']]
        for scalar,field in [('peak_source_index','peak_index'),('peak_distance_m','peak_distance_m'),
            ('peak_v_m_s','peak_v_m_s'),('peak_U_m_s','peak_U_m_s'),('peak_alignment_indicator_deg','peak_alignment_indicator_deg')]:
            assert row[scalar]==profile[field]


def test_changed_asca_provider_rejects(monkeypatch):
    original=adapter.Path.read_bytes;target=adapter.ROOT/adapter.ASCA_PROVIDER[0]
    monkeypatch.setattr(adapter.Path,'read_bytes',lambda path:original(path)+(b' ' if path==target else b''))
    with pytest.raises(ValueError,match='Changed current section provider'):adapter.build()
